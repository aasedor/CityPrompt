from unittest.mock import Mock
from io import BytesIO
import hashlib
import struct

from botocore.exceptions import ClientError
import pytest

from scripts.check_model_library_storage import check_catalogue, check_urls, storage_key


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


def test_empty_database_cannot_pass_expected_catalogue_check():
    client = Mock()
    result = check_catalogue([], [{'variant_id':'station', 'sha256':'a'*64}], 'studio', client)
    assert result[0]['status'] == 'failed'
    assert 'absent' in result[0]['error']
    client.get_object.assert_not_called()


def test_different_variant_or_hash_cannot_substitute_for_expected_model():
    row = {'metadata':{'rlasm':{'variant_id':'station','model_sha256':'b'*64}},'is_public':True}
    assert check_catalogue([row],[{'variant_id':'station','sha256':'a'*64}],'studio',Mock())[0]['status'] == 'failed'


@pytest.mark.parametrize('corrupt', [False, True])
def test_catalogue_reads_actual_object_bytes_instead_of_trusting_database_hash(corrupt):
    body = b'glTF' + struct.pack('<II', 2, 20) + b'12345678'
    digest = hashlib.sha256(body).hexdigest()
    row = {'metadata': {'rlasm': {'variant_id': 'station', 'model_sha256': digest}},
           'is_public': True, 'model_url': '/api/v1/files/library/station.glb'}
    client = Mock()
    stream = BytesIO(body if not corrupt else body[:-1] + b'x')
    client.get_object.return_value = {'Body': stream}
    result = check_catalogue([row], [{'variant_id': 'station', 'sha256': digest}], 'studio', client)
    assert result[0]['status'] == ('failed' if corrupt else 'verified')
    if corrupt:
        assert 'SHA-256 differs' in result[0]['error']
    assert stream.closed
