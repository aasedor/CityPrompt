"""Real PostgreSQL migration/locking checks; only disposable, unique schemas."""

import asyncio
import importlib.util
import os
from pathlib import Path
import uuid

from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import HTTPException
import pytest
from sqlalchemy import MetaData, inspect, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.v1 import auth
from app.core import security
from app.models.models import User
from app.schemas.schemas import LoginRequest, RefreshRequest, ResetPasswordRequest
from tests.test_auth_sessions import auth_request, reset_link, provider_login


@pytest.fixture
async def auth_database():
    url = os.getenv("CITYPROMPT_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CITYPROMPT_TEST_DATABASE_URL for isolated-schema auth concurrency tests")
    schema = "test_auth_" + uuid.uuid4().hex
    admin = create_async_engine(url, poolclass=NullPool)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_async_engine(
        url,
        pool_size=8,
        max_overflow=0,
        connect_args={"server_settings": {"search_path": f"{schema},public"}},
    )
    legacy_id = uuid.uuid4()
    try:
        metadata = MetaData()
        table = User.__table__.to_metadata(metadata)
        table.constraints.remove(next(c for c in table.constraints if c.name == "uq_users_oauth_identity"))
        for name in ("oauth_subject", "session_version", "reset_nonce_hash"):
            table._columns.remove(table.c[name])
        async with engine.begin() as connection:
            assert await connection.scalar(text("SELECT current_schema()")) == schema
            # checkfirst=True can discover a public.users table through search_path.
            # Always create this schema's own table before running any mutation.
            await connection.run_sync(lambda conn: metadata.create_all(conn, checkfirst=False))
            namespace = await connection.scalar(
                text(
                    "SELECT n.nspname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.oid='users'::regclass"
                )
            )
            assert namespace == schema
            await connection.execute(
                table.insert().values(
                    id=legacy_id,
                    email="legacy@example.com",
                    hashed_password="preserve-old-hash",
                    role="editor",
                    render_credits=47,
                    is_active=True,
                )
            )

            def migrate(conn):
                path = Path(__file__).parents[1] / "migrations/versions/032_auth_sessions.py"
                spec = importlib.util.spec_from_file_location("auth_migration", path)
                migration = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(migration)
                with Operations.context(MigrationContext.configure(conn)):
                    migration.upgrade()

            await connection.run_sync(migrate)
        yield async_sessionmaker(engine, expire_on_commit=False), legacy_id, engine
    finally:
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()


@pytest.mark.asyncio
async def test_auth_migration_preserves_legacy_user_and_adds_constraints(auth_database):
    sessions, legacy_id, engine = auth_database
    async with sessions() as db:
        user = await db.get(User, legacy_id)
        assert user.email == "legacy@example.com"
        assert user.hashed_password == "preserve-old-hash"
        assert user.render_credits == 47
        assert user.session_version == 0
        assert user.reset_nonce_hash is None and user.oauth_subject is None
    async with engine.connect() as connection:
        info = await connection.run_sync(lambda conn: inspect(conn).get_unique_constraints("users"))
        assert any(set(c["column_names"]) == {"oauth_provider", "oauth_subject"} for c in info)
        indexes = await connection.run_sync(lambda conn: inspect(conn).get_indexes("user_refresh_sessions"))
        assert any(i["column_names"] == ["user_id"] for i in indexes)


async def create_student(sessions):
    async with sessions.begin() as db:
        user = User(
            email="student@gmail.com",
            hashed_password=security.hash_password("old-password"),
        )
        db.add(user)
        await db.flush()
        return user.id


@pytest.mark.asyncio
async def test_only_one_concurrent_refresh_can_consume_a_token(auth_database):
    sessions, _, _ = auth_database
    await create_student(sessions)
    async with sessions.begin() as db:
        tokens = await auth.login(
            LoginRequest(email="student@gmail.com", password="old-password"),
            db,
            request=auth_request(),
        )

    async def rotate():
        try:
            async with sessions.begin() as db:
                return await auth.refresh_token(
                    RefreshRequest(refresh_token=tokens.refresh_token),
                    db,
                    request=auth_request(),
                )
        except HTTPException as exc:
            return exc.status_code

    results = await asyncio.gather(*(rotate() for _ in range(8)))
    assert results.count(401) == 7
    successful = [r for r in results if not isinstance(r, int)]
    assert len(successful) == 1
    async with sessions.begin() as db:
        rotated = await auth.refresh_token(
            RefreshRequest(refresh_token=successful[0].refresh_token),
            db,
            request=auth_request(),
        )
        assert (await security.get_current_user(rotated.access_token, db)).email == "student@gmail.com"


@pytest.mark.asyncio
async def test_only_one_concurrent_password_reset_can_consume_a_link(auth_database, monkeypatch):
    sessions, _, _ = auth_database
    user_id = await create_student(sessions)
    async with sessions.begin() as db:
        user = await db.get(User, user_id)
        token = await reset_link(db, user, monkeypatch)

    async def reset():
        try:
            async with sessions.begin() as db:
                await auth.reset_password(
                    ResetPasswordRequest(token=token, new_password="recovered-password"),
                    db,
                    request=auth_request(),
                )
                return 200
        except HTTPException as exc:
            return exc.status_code

    results = await asyncio.gather(*(reset() for _ in range(8)))
    assert results.count(200) == 1
    assert sum(result in (400, 401) for result in results) == 7
    async with sessions() as db:
        user = await db.get(User, user_id)
        assert user.session_version == 1 and user.reset_nonce_hash is None
        assert security.verify_password("recovered-password", user.hashed_password)


@pytest.mark.asyncio
async def test_only_one_concurrent_oauth_exchange_creates_a_refresh_session(auth_database, monkeypatch):
    import redis.asyncio as redis
    from fastapi import Response
    from app.api.v1 import oauth
    from app.core.config import get_settings
    from app.models.models import UserRefreshSession
    from app.services import oauth_exchange as broker
    from tests.test_oauth_exchange import CHALLENGE, VERIFIER, ORIGIN, exchange_request

    redis_url = os.getenv("CITYPROMPT_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Set CITYPROMPT_TEST_REDIS_URL for end-to-end OAuth concurrency")
    monkeypatch.setattr(broker, "_client", lambda: redis.from_url(redis_url, decode_responses=True))
    monkeypatch.setattr(
        oauth,
        "settings",
        get_settings().model_copy(update={"frontend_url": ORIGIN, "cors_origins": [ORIGIN]}),
    )
    sessions, _, _ = auth_database
    user_id = await create_student(sessions)
    async with sessions() as db:
        code = await broker.issue_exchange(await db.get(User, user_id), ORIGIN, CHALLENGE)

    async def redeem():
        try:
            async with sessions.begin() as db:
                return await oauth.exchange_code(
                    oauth.OAuthExchangeRequest(code=code, code_verifier=VERIFIER),
                    exchange_request(),
                    Response(),
                    db,
                )
        except HTTPException as exc:
            return exc.status_code

    try:
        outcomes = await asyncio.gather(*(redeem() for _ in range(8)))
        assert outcomes.count(400) == 7
        assert sum(not isinstance(outcome, int) for outcome in outcomes) == 1
        async with sessions() as db:
            rows = (
                (await db.execute(select(UserRefreshSession).where(UserRefreshSession.user_id == user_id)))
                .scalars()
                .all()
            )
            assert len(rows) == 1
    finally:
        async with redis.from_url(redis_url, decode_responses=True) as store:
            await store.delete(broker._key(code))


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["google", "microsoft"])
async def test_first_oauth_user_is_visible_to_another_transaction_before_code_publication(
    auth_database, monkeypatch, provider
):
    sessions, _, _ = auth_database

    async def publish(user, _origin, _challenge):
        async with sessions() as reader:
            visible = await reader.get(User, user.id)
            assert visible is not None, "Redirect code raced ahead of the new account commit"
            assert visible.oauth_provider == provider
            assert visible.oauth_subject == "fresh-provider-subject"
        return "x" * 43

    async with sessions() as writer:
        response = await provider_login(
            writer,
            monkeypatch,
            provider,
            {"sub": "fresh-provider-subject", "email": "first-oauth@gmail.com", "email_verified": True},
            publish=publish,
        )
        assert response.status_code == 302


@pytest.mark.asyncio
async def test_oauth_exchange_persists_refresh_session_before_returning_tokens(auth_database, monkeypatch):
    from fastapi import Response
    from unittest.mock import AsyncMock
    from app.api.v1 import oauth
    from app.core.config import get_settings
    from app.models.models import UserRefreshSession
    from tests.test_oauth_exchange import ORIGIN, VERIFIER, exchange_request

    sessions, _, _ = auth_database
    user_id = await create_student(sessions)
    monkeypatch.setattr(
        oauth, "settings", get_settings().model_copy(update={"frontend_url": ORIGIN, "cors_origins": [ORIGIN]})
    )
    monkeypatch.setattr(oauth, "consume_exchange", AsyncMock(return_value={"user_id": str(user_id), "ver": 0}))
    async with sessions() as writer:
        tokens = await oauth.exchange_code(
            oauth.OAuthExchangeRequest(code="x" * 43, code_verifier=VERIFIER),
            exchange_request(),
            Response(),
            writer,
        )
        session_id = security.decode_token(tokens.refresh_token)["sid"]
        async with sessions() as reader:
            persisted = await reader.get(UserRefreshSession, uuid.UUID(session_id))
            assert persisted is not None, "Refresh token escaped before its session commit"
