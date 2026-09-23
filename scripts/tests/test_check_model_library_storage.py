from unittest.mock import Mock

from botocore.exceptions import ClientError
import pytest

from scripts.check_model_library_storage import check_urls, storage_key


def test_storage_key_accepts_only_server_owned_references():
    assert storage_key("/api/v1/files/library/a.glb?v=123", "studio") == "library/a.glb"
    assert storage_key("http://minio:9000/studio/library/b.glb", "studio") == "library/b.glb"
    assert storage_key("https://example.com/external.glb", "studio") is None


def test_missing_object_is_reported_without_masking_storage_failures():
    client = Mock()
    client.head_object.side_effect = [
        {"ContentLength": 1234},
        ClientError({"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject"),
    ]
    missing, uncheckable = check_urls(
        [("Ready", "/api/v1/files/library/a.glb"), ("Missing", "/api/v1/files/library/b.glb")],
        "studio",
        client,
    )
    assert missing == ["Missing: library/b.glb"]
    assert uncheckable == []


def test_storage_permission_error_is_not_reported_as_a_missing_asset():
    client = Mock()
    client.head_object.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Denied"}}, "HeadObject"
    )
    with pytest.raises(ClientError):
        check_urls([("Private", "/api/v1/files/library/a.glb")], "studio", client)
