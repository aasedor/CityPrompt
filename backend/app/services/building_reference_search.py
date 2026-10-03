"""Bounded Commons discovery. Only server-issued image identities can be imported."""

import hashlib
import hmac
import html
import json
import re
from urllib.parse import urlsplit

import httpx

from app.services.photo_building import prepare_photo
from app.core.config import get_settings

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "CityPrompt/1.0 (https://github.com/aasedor/CityPrompt; architectural reference search)"}
VIEW_TERMS = {"all": "", "exterior": "exterior", "aerial": "aerial", "rear": "rear", "side": "side"}
MAX_DOWNLOAD = 8 * 1024 * 1024


def sign_candidate(candidate: dict, building_id: str) -> dict:
    """Bind metadata to its building even when generic specifications are edited."""
    content = {key: value for key, value in candidate.items() if key != "_signature"}
    payload = building_id + ":" + json.dumps(content, sort_keys=True, separators=(",", ":"))
    signature = hmac.new(get_settings().jwt_secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return {**content, "_signature": signature}


def verified_candidate(candidate: dict, building_id: str) -> bool:
    signature = candidate.get("_signature")
    return isinstance(signature, str) and hmac.compare_digest(signature, sign_candidate(candidate, building_id)["_signature"])


def plain(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]*>", "", str(value)))[:1200]


def trusted_image_url(url: str) -> bool:
    try:
        parts = urlsplit(url)
        return (parts.scheme == "https" and parts.hostname in {"upload.wikimedia.org", "thumb.wikimedia.org"}
                and parts.port in (None, 443) and not parts.username and not parts.password
                and parts.path.startswith("/wikipedia/commons/"))
    except ValueError:
        return False


def commons_candidate(page: dict) -> dict | None:
    info = (page.get("imageinfo") or [{}])[0]
    if info.get("mime") not in {"image/jpeg", "image/png", "image/tiff"}:
        return None
    metadata = info.get("extmetadata") or {}
    get = lambda key: plain(metadata.get(key, {}).get("value", ""))
    license_name = get("LicenseShortName")
    # Use known reusable licences; incomplete metadata is not an importable result.
    if not (license_name in {"Public domain", "CC0"} or license_name.startswith(("CC BY ", "CC BY-SA "))):
        return None
    image_url = info.get("thumburl") or info.get("url", "")
    if not trusted_image_url(image_url):
        return None
    source_url = info.get("descriptionurl", "")
    if not source_url.startswith("https://commons.wikimedia.org/wiki/File:"):
        return None
    if min(info.get("width", 0), info.get("height", 0)) < 240:
        return None
    identity = f"{page['pageid']}:{info.get('sha1', '')}"
    return {
        "id": hashlib.sha256(identity.encode()).hexdigest()[:24],
        "title": plain(page.get("title", "")).removeprefix("File:"),
        "image_url": image_url, "source_url": source_url,
        "license": license_name, "license_url": get("LicenseUrl"),
        "author": get("Artist"), "description": get("ImageDescription"),
        "source_sha1": info.get("sha1"), "provider": "wikimedia_commons",
    }


async def search_building_views(query: str, view: str) -> list[dict]:
    # Quote the landmark so search operators in student input cannot broaden it.
    query = " ".join(query.replace('"', ' ').split())
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f'intitle:"{query}" {VIEW_TERMS[view]} filetype:bitmap',
        "gsrnamespace": 6, "gsrlimit": 20, "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata|sha1", "iiurlwidth": 1280,
        "iiextmetadatafilter": "LicenseShortName|LicenseUrl|Artist|ImageDescription",
    }
    async with httpx.AsyncClient(timeout=25, headers=HEADERS, follow_redirects=False) as client:
        response = await client.get(COMMONS_API, params=params)
        response.raise_for_status()
        payload = response.json()
    if "error" in payload:
        raise ValueError("The image search service could not complete this search.")
    pages = payload.get("query", {}).get("pages", {}).values()
    results, seen = [], set()
    for page in sorted(pages, key=lambda item: item.get("index", 999)):
        candidate = commons_candidate(page)
        if candidate and candidate["source_sha1"] not in seen:
            seen.add(candidate["source_sha1"])
            results.append(candidate)
    return results[:12]


async def download_building_view(candidate: dict) -> tuple[bytes, str]:
    url = candidate["image_url"]
    if not trusted_image_url(url):
        raise ValueError("This reference source is not supported. Search again.")
    async with httpx.AsyncClient(timeout=30, headers=HEADERS, follow_redirects=False) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            if response.headers.get("content-type", "").split(";")[0] not in {"image/jpeg", "image/png"}:
                raise ValueError("This source did not return a usable photo.")
            data = bytearray()
            async for chunk in response.aiter_bytes():
                data.extend(chunk)
                if len(data) > MAX_DOWNLOAD:
                    raise ValueError("This reference photo is too large. Choose another view.")
    return prepare_photo(bytes(data), max_bytes=MAX_DOWNLOAD)
