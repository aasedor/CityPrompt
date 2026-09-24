import copy
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import uuid

import pytest
from sqlalchemy import MetaData, create_engine, select, text
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).parents[2]))
from scripts import classroom_model_library as seed
from app.models.models import User, Project, Building, ModelLibraryEntry
from app.services.lego_assembly import descriptor_from_library_entry


def test_exact_model_bindings_are_accepted_by_real_runtime_descriptor():
    _, rows = seed.load_bindings()
    for row in rows:
        entry = SimpleNamespace(id=uuid.UUID(row["id"]), name=row["name"], model_url=row["model_url"], metadata_=row["metadata"])
        module = descriptor_from_library_entry(entry)
        assert module is not None
        assert module.source_variant_id == row["variantId"]
        assert seed.binding_matches(SimpleNamespace(**vars(entry), is_public=True), row)


@pytest.mark.parametrize("review", ["pending", "partial"])
def test_release_seed_cannot_turn_partial_runtime_review_into_approval(review):
    roster, _ = seed.load_bindings()
    roster = copy.deepcopy(roster)
    for entry in roster["entries"]:
        entry["review"]["runtime"] = "passed"
    roster["entries"][0]["review"]["runtime"] = review
    settings = SimpleNamespace(database_url="postgresql://localhost/test", s3_endpoint_url="http://127.0.0.1:9000")
    with pytest.raises(ValueError, match="reviews remain open"):
        seed.validate_target(settings, roster, local_trial=False)
    seed.validate_target(settings, roster, local_trial=True)
    settings.s3_endpoint_url = "https://classroom.example.invalid"
    with pytest.raises(ValueError, match="loopback"):
        seed.validate_target(settings, roster, local_trial=True)


def test_installs_exact_starters_into_isolated_database_and_bucket_without_overwrite():
    url = os.getenv("CITYPROMPT_TEST_DATABASE_URL")
    if not url or os.getenv("CITYPROMPT_TEST_S3") != "1":
        pytest.skip("Set CITYPROMPT_TEST_DATABASE_URL and CITYPROMPT_TEST_S3=1 for disposable DB/S3 seed verification")
    from app.services.render_attempt_storage import _client
    client, live_bucket = _client()
    suffix = uuid.uuid4().hex
    schema, bucket = "test_classroom_seed_" + suffix, "cityprompt-restore-" + suffix
    assert bucket != live_bucket
    admin = create_engine(url.replace("+asyncpg", ""))
    engine = create_engine(url.replace("+asyncpg", ""), connect_args={"options": f"-csearch_path={schema},public"})
    with admin.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    client.create_bucket(Bucket=bucket)
    try:
        metadata = MetaData()
        for model in (User, Project, Building, ModelLibraryEntry):
            model.__table__.to_metadata(metadata)
        metadata.create_all(engine, checkfirst=False)
        roster, rows = seed.load_bindings()
        with Session(engine) as db:
            owner = User(id=uuid.uuid4(), email=f"{suffix}@test.invalid", full_name="Disposable seed owner", role="editor", is_active=True)
            db.add(owner)
            db.commit()
            initial = seed.synchronize(db, client, bucket, roster, rows)
            assert all(row["binding"] == row["object"] == "missing" for row in initial)
            installed = seed.synchronize(db, client, bucket, roster, rows, apply=True, owner_id=owner.id)
            assert all(row["binding"] == row["object"] == "verified" for row in installed)
            assert seed.synchronize(db, client, bucket, roster, rows, apply=True, owner_id=owner.id) == installed
            actual = list(db.scalars(select(ModelLibraryEntry)))
            assert len(actual) == 3
            assert all(descriptor_from_library_entry(entry) is not None for entry in actual)
            # Do not silently replace a future user's changed binding.
            changed = db.get(ModelLibraryEntry, uuid.UUID(rows[0]["id"]))
            changed.model_url = "/api/v1/files/library/user-alternative.glb"
            db.commit()
            with pytest.raises(ValueError, match="existing starter row differs"):
                seed.synchronize(db, client, bucket, roster, rows, apply=True, owner_id=owner.id)
            assert changed.model_url.endswith("user-alternative.glb")
    finally:
        engine.dispose()
        assert schema == "test_classroom_seed_" + suffix
        with admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()
        for page in client.get_paginator("list_objects_v2").paginate(Bucket=bucket):
            objects = [{"Key": item["Key"]} for item in page.get("Contents", [])]
            if objects:
                client.delete_objects(Bucket=bucket, Delete={"Objects": objects})
        client.delete_bucket(Bucket=bucket)
