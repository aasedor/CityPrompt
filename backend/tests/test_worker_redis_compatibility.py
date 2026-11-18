"""Characterize the Redis client compatibility needed during worker startup."""

from kombu import Connection


def test_worker_redis_transport_can_construct_its_client_without_connecting():
    # A fresh install previously selected Kombu 5.7 with redis-py 5.2.1.
    # Importing the worker succeeded, but its broker client factory then raised
    # VersionMismatch before it could connect. Exercise that exact boundary.
    connection = Connection("redis://localhost:6379/0")
    channel = object.__new__(connection.transport.Channel)
    channel.global_keyprefix = ""

    client_class = channel._get_client()
    client = client_class.from_url("redis://localhost:6379/0")

    assert client.connection_pool.connection_kwargs["host"] == "localhost"
    assert client.connection_pool.connection_kwargs["port"] == 6379
