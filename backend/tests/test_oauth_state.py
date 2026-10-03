import asyncio
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlparse

import pytest
import redis.asyncio as redis
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.api.v1 import oauth
from app.services import oauth_state


def request(provider, binding):
    cookie = f'{oauth_state.cookie_name(provider)}={binding}'
    return Request({'type': 'http', 'headers': [(b'cookie', cookie.encode())]})


@pytest.mark.asyncio
@pytest.mark.parametrize('provider', ['google', 'microsoft'])
async def test_missing_browser_binding_rejects_before_provider_or_database(client, mock_db, provider):
    response = await client.get(f'/api/v1/auth/oauth/{provider}/callback?state=forged&code=attacker-code')
    assert response.status_code == 400
    mock_db.execute.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize('provider', ['google', 'microsoft'])
async def test_top_level_start_preserves_origin_and_binds_cookie(client, monkeypatch, provider):
    settings = SimpleNamespace(frontend_url='https://class.example', cors_origins=['https://class.example'],
                               is_production=True, google_client_id='test', microsoft_client_id='test',
                               google_redirect_uri='https://api.example/api/v1/auth/oauth/google/callback',
                               microsoft_redirect_uri='https://api.example/api/v1/auth/oauth/microsoft/callback')
    monkeypatch.setattr(oauth, 'settings', settings)
    monkeypatch.setattr(oauth_state, 'get_settings', lambda: settings)
    issue = AsyncMock(return_value=('opaque-state', 'browser-secret'))
    monkeypatch.setattr(oauth, 'issue_state', issue)
    first = await client.get(f'/api/v1/auth/oauth/{provider}?frontend_origin=https://evil.example')
    start = first.json()['authorization_url']
    assert urlparse(start).hostname == 'api.example'
    assert parse_qs(urlparse(start).query)['frontend_origin'] == ['https://class.example']
    assert 'set-cookie' not in first.headers  # Issued only by top-level navigation.
    response = await client.get(f'/api/v1/auth/oauth/{provider}/start?frontend_origin=https://class.example')
    assert response.status_code == 302
    assert parse_qs(urlparse(response.headers['location']).query)['state'] == ['opaque-state']
    cookie = response.headers['set-cookie']
    assert '__Host-' in cookie and 'HttpOnly' in cookie and 'Secure' in cookie and 'SameSite=lax' in cookie
    issue.assert_awaited_once_with(provider, 'https://class.example')


@pytest.mark.asyncio
async def test_store_outage_fails_closed(monkeypatch):
    client = AsyncMock()
    client.__aenter__.return_value = client
    client.eval.side_effect = ConnectionError('offline')
    client.set.side_effect = ConnectionError('offline')
    monkeypatch.setattr(oauth_state, '_client', lambda: client)
    with pytest.raises(HTTPException) as issued:
        await oauth_state.issue_state('google', 'https://class.example')
    assert issued.value.status_code == 503
    with pytest.raises(HTTPException) as consumed:
        await oauth_state.consume_state(request('google', 'binding'), 'google', 'state')
    assert consumed.value.status_code == 503


@pytest.mark.asyncio
async def test_actual_redis_state_expiry_provider_binding_and_atomic_replay(monkeypatch):
    url = os.getenv('CITYPROMPT_TEST_REDIS_URL')
    if not url:
        pytest.skip('Set CITYPROMPT_TEST_REDIS_URL for isolated-key Redis integration')
    monkeypatch.setattr(oauth_state, '_client', lambda: redis.from_url(url, decode_responses=True))
    state, binding = await oauth_state.issue_state('google', 'https://class.example')
    key = oauth_state._key('google', state)
    async with redis.from_url(url, decode_responses=True) as store:
        try:
            assert 0 < await store.ttl(key) <= 600
            for provider, cookie in [('google', 'wrong-browser'), ('microsoft', binding)]:
                with pytest.raises(HTTPException) as rejected:
                    await oauth_state.consume_state(request(provider, cookie), provider, state)
                assert rejected.value.status_code == 400
            # The wrong browser did not consume the real browser's state.
            outcomes = await asyncio.gather(*[
                oauth_state.consume_state(request('google', binding), 'google', state) for _ in range(12)
            ], return_exceptions=True)
            assert outcomes.count('https://class.example') == 1
            assert sum(isinstance(item, HTTPException) and item.status_code == 400 for item in outcomes) == 11
            expired, secret = await oauth_state.issue_state('google', 'https://class.example')
            expired_key = oauth_state._key('google', expired)
            await store.expire(expired_key, 0)
            with pytest.raises(HTTPException) as rejected:
                await oauth_state.consume_state(request('google', secret), 'google', expired)
            assert rejected.value.status_code == 400
        finally:
            await store.delete(key)
