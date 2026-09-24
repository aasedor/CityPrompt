"""Private immutable evidence; never put image/control payloads in Redis messages."""

import asyncio
import json

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import get_settings
from app.services.render_provenance import canonical_json


def evidence_key(attempt, name: str) -> str:
    if name not in {"request", "source", "provider-result", "response", "provider-error"}:
        raise ValueError("Unknown image evidence part")
    return f"projects/{attempt.project_id}/render-attempts/{attempt.id}/{name}.json"


def _client():
    settings = get_settings()
    return boto3.client(
        "s3", endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key, aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4", connect_timeout=10, read_timeout=30, retries={"max_attempts": 2}),
    ), settings.s3_bucket_name


def _read(key):
    s3, bucket = _client()
    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"]
    except ClientError as exc:
        if exc.response["Error"]["Code"] in {"NoSuchKey", "404"}:
            return None
        raise
    try:
        return json.loads(body.read())
    finally:
        body.close()


async def read_evidence(attempt, name):
    return await asyncio.to_thread(_read, evidence_key(attempt, name))


def _write(key, value):
    body = canonical_json(value).encode("utf-8")
    s3, bucket = _client()
    try:
        s3.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json", IfNoneMatch="*")
    except ClientError as exc:
        if exc.response["Error"]["Code"] not in {"PreconditionFailed", "412"}:
            raise
        if canonical_json(_read(key)).encode("utf-8") != body:
            raise ValueError("Immutable render evidence already exists with different bytes") from exc


async def write_evidence(attempt, name, value):
    await asyncio.to_thread(_write, evidence_key(attempt, name), value)
