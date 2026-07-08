"""Meshy client pure-logic tests — prompt capping and 4xx classification.

These guard the fix for the 2026-07-08 outage: every "real" building failed
because compose_zone_prompt output (~2,300 chars) exceeded Meshy's 800-char
prompt limit, and the failures were being retried instead of failing fast.
"""

import httpx
import pytest

from app.generation.meshy_client import (
    MESHY_PROMPT_MAX,
    MeshyClient,
    MeshyClientError,
    _cap_prompt,
)


def test_cap_prompt_leaves_short_text_untouched():
    text = "A modern 6-storey mixed-use residential building."
    assert _cap_prompt(text) == text


def test_cap_prompt_trims_over_limit_to_word_boundary():
    text = "word " * 400  # 2000 chars
    capped = _cap_prompt(text)
    assert len(capped) <= MESHY_PROMPT_MAX
    assert not capped.endswith("wor")  # cut at a space, not mid-word


def test_cap_prompt_handles_empty():
    assert _cap_prompt("") == ""
    assert _cap_prompt(None) == ""


def test_cap_prompt_hard_cut_when_no_space():
    text = "x" * 2000  # no spaces
    assert len(_cap_prompt(text)) == MESHY_PROMPT_MAX


def _resp(status: int, body: str = "err") -> httpx.Response:
    return httpx.Response(status_code=status, text=body, request=httpx.Request("POST", "http://x"))


def test_check_raises_permanent_error_on_400():
    with pytest.raises(MeshyClientError):
        MeshyClient._check(_resp(400, '{"message":"Prompt must be a maximum of 800 characters"}'), "preview")


def test_check_retryable_on_429_and_5xx():
    # 429 rate-limit and 5xx are transient — plain RuntimeError, NOT MeshyClientError.
    for status in (429, 500, 503):
        with pytest.raises(RuntimeError) as exc:
            MeshyClient._check(_resp(status), "preview")
        assert not isinstance(exc.value, MeshyClientError)


def test_check_passes_on_2xx():
    MeshyClient._check(_resp(200), "preview")
    MeshyClient._check(_resp(202), "preview")
