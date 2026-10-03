import hashlib
import json
from datetime import datetime, timezone
from io import BytesIO

import pytest
from botocore.exceptions import ClientError

from scripts.classroom_storage_backup import snapshot, verify, restore_new


class Storage:
    def __init__(self):
        self.buckets = {"live": {"projects/one/image.png": (b"saved pixels", {"ContentType": "image/png", "Metadata": {"test": "yes"}}),
                                 "../unsafe/name": (b"safe local path", {"ContentType": "text/plain"})}}
        self.created = []

    def get_paginator(self, operation):
        return self

    def paginate(self, Bucket):
        yield {"Contents": [{"Key": key, "Size": len(value[0]), "ETag": hashlib.sha256(value[0]).hexdigest(),
                             "LastModified": datetime(2026, 9, 23, tzinfo=timezone.utc)} for key, value in self.buckets[Bucket].items()]}

    def get_object(self, Bucket, Key, **kwargs):
        data, attributes = self.buckets[Bucket][Key]
        return {"Body": BytesIO(data), **attributes}

    def head_bucket(self, Bucket):
        if Bucket not in self.buckets:
            raise ClientError({"Error": {"Code": "404"}}, "HeadBucket")

    def create_bucket(self, Bucket, **kwargs):
        assert Bucket not in self.buckets
        self.buckets[Bucket] = {}
        self.created.append(Bucket)

    def put_object(self, Bucket, Key, Body, IfNoneMatch, **attributes):
        assert Key not in self.buckets[Bucket] and IfNoneMatch == "*"
        self.buckets[Bucket][Key] = (Body.read(), attributes)


def test_roundtrip_preserves_private_bytes_metadata_and_unsafe_keys(tmp_path):
    storage = Storage()
    source = tmp_path / "snapshot"
    manifest = snapshot(storage, "live", source)
    assert len(manifest["objects"]) == 2
    assert all("/" not in row["file"] for row in manifest["objects"])
    restore_new(storage, source, "cityprompt-restore-test", "live")
    assert storage.buckets["cityprompt-restore-test"] == storage.buckets["live"]
    with pytest.raises(ValueError, match="already exists"):
        restore_new(storage, source, "cityprompt-restore-test", "live")
    with pytest.raises(ValueError, match="never overwritten"):
        snapshot(storage, "live", source)


def test_corruption_stops_restore_before_bucket_creation(tmp_path):
    storage = Storage()
    source = tmp_path / "snapshot"
    manifest = snapshot(storage, "live", source)
    (source / "objects" / manifest["objects"][0]["file"]).write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="byte/hash"):
        restore_new(storage, source, "cityprompt-restore-test", "live")
    assert storage.created == []


@pytest.mark.parametrize("target", ["live", "production-assets", "cityprompt-restore-../live"])
def test_existing_or_unsafe_targets_are_never_written(tmp_path, target):
    storage = Storage()
    source = tmp_path / "snapshot"
    snapshot(storage, "live", source)
    with pytest.raises(ValueError, match="new cityprompt-restore"):
        restore_new(storage, source, target, "live")
    assert storage.created == []


def test_changed_inventory_leaves_incomplete_backup_unusable(tmp_path):
    storage = Storage()
    original = storage.paginate
    count = 0
    def paginate(**kwargs):
        nonlocal count
        count += 1
        if count == 2:
            storage.buckets["live"]["new-key"] = (b"new", {})
        return original(**kwargs)
    storage.paginate = paginate
    source = tmp_path / "snapshot"
    with pytest.raises(ValueError, match="inventory changed"):
        snapshot(storage, "live", source)
    assert not (source / "manifest.json").exists()


def test_manifest_path_traversal_cannot_read_outside_backup(tmp_path):
    storage = Storage()
    source = tmp_path / "snapshot"
    manifest = snapshot(storage, "live", source)
    manifest["objects"][0]["file"] = "../../private"
    (source / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="snapshot key"):
        verify(source)
