"""Account identities for private loopback pilots; never publication authority."""
from __future__ import annotations

import uuid


def private_local_pilot_id(
    legacy_id: uuid.UUID | str,
    owner_id: uuid.UUID | str,
    legacy_owner_id: uuid.UUID | str | None = None,
) -> uuid.UUID:
    """Retain an owner's installed legacy ID, otherwise derive a private ID.

    Only the database row identity varies by account. Source/object paths,
    hashes, review gates and private-row conflict checks remain unchanged.
    """
    legacy_id = uuid.UUID(str(legacy_id))
    owner_id = uuid.UUID(str(owner_id))
    if legacy_owner_id is not None and uuid.UUID(str(legacy_owner_id)) == owner_id:
        return legacy_id
    return uuid.uuid5(legacy_id, f'private-local-owner:{owner_id}')
