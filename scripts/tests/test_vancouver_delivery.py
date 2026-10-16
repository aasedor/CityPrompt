from types import SimpleNamespace
import pytest
from scripts import vancouver_tower_storeys as delivery

def settings(database='postgresql://user:password@db.example/app', storage='https://assets.example'):
    return SimpleNamespace(database_url=database,s3_endpoint_url=storage)

def test_hosted_verification_requires_both_explicit_target_locks():
    with pytest.raises(ValueError,match='explicit'):
        delivery.validate_program_target(settings(),hosted=True)

def test_hosted_target_refuses_an_unexpected_database_or_storage():
    for database,storage in [('other.example','https://assets.example'),('db.example','https://other.example')]:
        with pytest.raises(ValueError,match='match'):
            delivery.validate_program_target(settings(),hosted=True,expected_database_host=database,expected_storage_endpoint=storage)

def test_hosted_target_accepts_only_the_exact_declared_destinations():
    delivery.validate_program_target(settings(),hosted=True,expected_database_host='db.example',expected_storage_endpoint='https://assets.example')

def test_default_installation_remains_loopback_only():
    with pytest.raises(ValueError,match='loopback'):
        delivery.validate_program_target(settings())
