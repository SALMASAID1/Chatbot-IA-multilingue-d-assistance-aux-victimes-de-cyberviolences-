#!/usr/bin/env python3
"""Acquire supportive imagery for the EMC Helpline frontend, safely and reproducibly.

The script searches Google Images through a *structured search API* (SerpAPI by
default, Google Custom Search as an optional adapter), downloads the candidates
locally, normalises them to optimized WebP with metadata stripped, and records
everything it knows in a manifest.

Deliberate policy, encoded in code rather than left to the operator:

* Appearing in Google Images is **never** treated as permission. Every freshly
  fetched asset is recorded as ``review_required`` and the application is only
  allowed to use assets a human has explicitly flipped to ``approved``.
* An asset already marked ``approved`` is never silently replaced.
* Raw Google HTML is never scraped; only documented JSON APIs are called.
* Downloads are bounded (timeout, retries, byte cap, content-type allow-list,
  minimum dimensions) so a hostile or broken URL cannot hang or fill the disk.
* EXIF (including GPS) is stripped before anything is written to the repo.

Usage
-----
    export SERPAPI_KEY=...            # or GOOGLE_CSE_API_KEY + GOOGLE_CSE_CX
    python scripts/fetch_google_images.py --dry-run
    python scripts/fetch_google_images.py --count 3
    python scripts/fetch_google_images.py --provider google_cse --queries scripts/image_queries.json

Dependencies: ``pip install -r scripts/requirements-images.txt``
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import logging
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import urlparse

logger = logging.getLogger("fetch_images")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUERIES = PROJECT_ROOT / "scripts" / "image_queries.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "frontend" / "public" / "images"
MANIFEST_NAME = "assets-manifest.json"
ATTRIBUTIONS_NAME = "ATTRIBUTIONS.md"

SERPAPI_ENDPOINT = "https://serpapi.com/search"
GOOGLE_CSE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/pjpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}

MAX_DOWNLOAD_BYTES = 12 * 1024 * 1024  # 12 MB
REQUEST_TIMEOUT_SECONDS = 20
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 1.5
WEBP_QUALITY = 82
MAX_STORED_WIDTH = 1800

APPROVAL_REVIEW = "review_required"
APPROVAL_APPROVED = "approved"
APPROVAL_REJECTED = "rejected"

# Hosts whose reuse terms are documented and machine-checkable enough to be
# worth surfacing to the reviewer. Even these are NOT auto-approved.
KNOWN_LICENCE_HOSTS: dict[str, str] = {
    "upload.wikimedia.org": "Wikimedia Commons — per-file licence, verify on the file page",
    "commons.wikimedia.org": "Wikimedia Commons — per-file licence, verify on the file page",
    "images.unsplash.com": "Unsplash Licence — verify on the photo page",
    "unsplash.com": "Unsplash Licence — verify on the photo page",
    "cdn.pixabay.com": "Pixabay Content Licence — verify on the media page",
    "pixabay.com": "Pixabay Content Licence — verify on the media page",
    "images.pexels.com": "Pexels Licence — verify on the photo page",
    "pexels.com": "Pexels Licence — verify on the photo page",
    "openclipart.org": "OpenClipart — Public Domain (CC0), verify on the file page",
    "undraw.co": "unDraw Licence — verify on the site",
}

PREFERRED_HOSTS = tuple(KNOWN_LICENCE_HOSTS)


class SetupError(RuntimeError):
    """Raised when credentials or dependencies are missing."""


class FetchError(RuntimeError):
    """Raised when a single candidate cannot be retrieved or processed."""


# ──────────────────────────────────────────────────────────────────────────
# Data model
# ──────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ImageCandidate:
    """One search result, before anything has been downloaded."""

    query_id: str
    query: str
    title: str
    source_page: str
    image_url: str
    provider: str
    reported_width: int | None = None
    reported_height: int | None = None
    licence_hint: str | None = None


@dataclass
class ManifestEntry:
    """What we persist about an asset we actually stored."""

    file_name: str
    query_id: str
    query: str
    title: str
    source_page: str
    original_image_url: str
    provider: str
    width: int
    height: int
    mime_type: str
    original_mime_type: str
    sha256: str
    bytes: int
    acquired_at: str
    licence: str
    attribution: str
    approval_status: str = APPROVAL_REVIEW
    review_notes: str = ""
    policy_flags: list[str] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────
# Providers (structured APIs only — never HTML scraping)
# ──────────────────────────────────────────────────────────────────────────


class SearchProvider:
    name = "abstract"

    def search(self, query: str, count: int, defaults: dict[str, Any]) -> list[ImageCandidate]:
        raise NotImplementedError


class SerpApiProvider(SearchProvider):
    """Google Images via SerpAPI's documented JSON endpoint."""

    name = "serpapi"

    def __init__(self, api_key: str, session: Any) -> None:
        self._api_key = api_key
        self._session = session

    def search(self, query: str, count: int, defaults: dict[str, Any]) -> list[ImageCandidate]:
        params = {
            "engine": "google_images",
            "q": query,
            "api_key": self._api_key,
            "safe": "active" if defaults.get("safe_search", True) else "off",
            # Morocco / French localisation where the API supports it.
            "gl": defaults.get("country", "ma"),
            "hl": defaults.get("language", "fr"),
            "num": max(count * 4, 20),
        }
        payload = _request_json(self._session, SERPAPI_ENDPOINT, params)
        results = payload.get("images_results") or []
        candidates: list[ImageCandidate] = []
        for item in results:
            image_url = item.get("original") or item.get("thumbnail")
            source_page = item.get("link") or item.get("source") or ""
            if not image_url:
                continue
            candidates.append(
                ImageCandidate(
                    query_id="",
                    query=query,
                    title=str(item.get("title") or "").strip(),
                    source_page=str(source_page),
                    image_url=str(image_url),
                    provider=self.name,
                    reported_width=_as_int(item.get("original_width")),
                    reported_height=_as_int(item.get("original_height")),
                )
            )
        return candidates


class GoogleCseProvider(SearchProvider):
    """Optional adapter for legacy Google Custom Search credentials."""

    name = "google_cse"

    def __init__(self, api_key: str, cx: str, session: Any) -> None:
        self._api_key = api_key
        self._cx = cx
        self._session = session

    def search(self, query: str, count: int, defaults: dict[str, Any]) -> list[ImageCandidate]:
        params = {
            "key": self._api_key,
            "cx": self._cx,
            "q": query,
            "searchType": "image",
            "safe": "active" if defaults.get("safe_search", True) else "off",
            "gl": defaults.get("country", "ma"),
            "hl": defaults.get("language", "fr"),
            "num": min(max(count, 1) * 2, 10),
            # Restrict to results Google reports as reusable.
            "rights": "cc_publicdomain|cc_attribute|cc_sharealike",
        }
        payload = _request_json(self._session, GOOGLE_CSE_ENDPOINT, params)
        candidates: list[ImageCandidate] = []
        for item in payload.get("items") or []:
            image = item.get("image") or {}
            link = item.get("link")
            if not link:
                continue
            candidates.append(
                ImageCandidate(
                    query_id="",
                    query=query,
                    title=str(item.get("title") or "").strip(),
                    source_page=str(image.get("contextLink") or ""),
                    image_url=str(link),
                    provider=self.name,
                    reported_width=_as_int(image.get("width")),
                    reported_height=_as_int(image.get("height")),
                    licence_hint="google_cse rights filter: cc_publicdomain|cc_attribute|cc_sharealike",
                )
            )
        return candidates


def build_provider(preference: str, session: Any) -> SearchProvider:
    """Pick a provider from the environment, or explain exactly what is missing."""
    serp_key = os.getenv("SERPAPI_KEY", "").strip()
    cse_key = os.getenv("GOOGLE_CSE_API_KEY", "").strip()
    cse_cx = os.getenv("GOOGLE_CSE_CX", "").strip()

    if preference in ("auto", "serpapi") and serp_key:
        return SerpApiProvider(serp_key, session)
    if preference in ("auto", "google_cse") and cse_key and cse_cx:
        return GoogleCseProvider(cse_key, cse_cx, session)

    if preference == "serpapi":
        raise SetupError(_setup_message("SERPAPI_KEY is not set."))
    if preference == "google_cse":
        raise SetupError(_setup_message("GOOGLE_CSE_API_KEY and/or GOOGLE_CSE_CX are not set."))
    raise SetupError(_setup_message("No image-search credentials were found."))


def _setup_message(reason: str) -> str:
    return (
        f"{reason}\n\n"
        "This script only talks to structured search APIs, so it needs one of:\n"
        "  1. SerpAPI (default)\n"
        "       export SERPAPI_KEY=your_key            # https://serpapi.com/manage-api-key\n"
        "  2. Google Custom Search (optional adapter)\n"
        "       export GOOGLE_CSE_API_KEY=your_key\n"
        "       export GOOGLE_CSE_CX=your_search_engine_id\n\n"
        "Then re-run, for example:\n"
        "  python scripts/fetch_google_images.py --dry-run\n\n"
        "Nothing was downloaded and no file was modified."
    )


# ──────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ──────────────────────────────────────────────────────────────────────────


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _request_json(session: Any, url: str, params: dict[str, Any]) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = session.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            if response.status_code == 429:
                raise FetchError("Search API rate limit reached (HTTP 429)")
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise FetchError("Unexpected search API payload (not a JSON object)")
            return payload
        except Exception as exc:  # noqa: BLE001 - retried and re-raised below
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
    raise FetchError(f"Search request failed: {last_error}")


def download_image(session: Any, url: str, max_bytes: int = MAX_DOWNLOAD_BYTES) -> tuple[bytes, str]:
    """Download one image with a byte cap and a content-type allow-list."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise FetchError(f"Refusing non-HTTP(S) image URL: {parsed.scheme or 'relative'}")

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS, stream=True)
            response.raise_for_status()

            content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            if content_type not in ALLOWED_CONTENT_TYPES:
                raise FetchError(f"Unsupported content type: {content_type or 'unknown'}")

            declared = _as_int(response.headers.get("Content-Length"))
            if declared is not None and declared > max_bytes:
                raise FetchError(f"Image is too large: {declared} bytes > {max_bytes}")

            buffer = bytearray()
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                buffer.extend(chunk)
                if len(buffer) > max_bytes:
                    raise FetchError(f"Image exceeded {max_bytes} bytes while downloading")
            if not buffer:
                raise FetchError("Empty response body")
            return bytes(buffer), content_type
        except FetchError:
            raise
        except Exception as exc:  # noqa: BLE001 - retried and re-raised below
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
    raise FetchError(f"Download failed: {last_error}")


# ──────────────────────────────────────────────────────────────────────────
# Image processing
# ──────────────────────────────────────────────────────────────────────────


def slugify(value: str, max_length: int = 48) -> str:
    normalised = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (normalised[:max_length].rstrip("-")) or "image"


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def deterministic_file_name(query_id: str, digest: str) -> str:
    """Same query + same bytes always produce the same file name."""
    return f"{slugify(query_id)}-{digest[:12]}.webp"


def to_optimized_webp(
    data: bytes,
    *,
    min_width: int,
    min_height: int,
    max_width: int = MAX_STORED_WIDTH,
) -> tuple[bytes, int, int]:
    """Validate dimensions, strip metadata, and re-encode as WebP.

    Re-encoding through a fresh Image object is what removes EXIF/GPS: nothing
    from the original container is carried over.
    """
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SetupError(
            "Pillow is required to process images.\n"
            "  pip install -r scripts/requirements-images.txt"
        ) from exc

    try:
        with Image.open(io.BytesIO(data)) as source:
            source.load()
            width, height = source.size
            if width < min_width or height < min_height:
                raise FetchError(
                    f"Image is too small: {width}x{height} (minimum {min_width}x{min_height})"
                )

            converted = source.convert("RGBA" if source.mode in ("RGBA", "LA", "P") else "RGB")

            if converted.width > max_width:
                ratio = max_width / converted.width
                converted = converted.resize(
                    (max_width, max(1, round(converted.height * ratio))),
                    Image.Resampling.LANCZOS,
                )

            # Rebuilt from raw pixels only: no EXIF (incl. GPS), no ICC, no XMP
            # survives the round-trip.
            stripped = Image.frombytes(converted.mode, converted.size, converted.tobytes())

            output = io.BytesIO()
            stripped.save(output, format="WEBP", quality=WEBP_QUALITY, method=6)
            return output.getvalue(), stripped.width, stripped.height
    except FetchError:
        raise
    except SetupError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise FetchError(f"Could not decode or re-encode the image: {exc}") from exc


# ──────────────────────────────────────────────────────────────────────────
# Licensing and policy
# ──────────────────────────────────────────────────────────────────────────


def classify_licence(candidate: ImageCandidate) -> tuple[str, str, str]:
    """Return ``(licence, attribution, review_note)``.

    Nothing here ever returns "approved": presence in an image search says
    nothing about reuse rights, so a human has to make that call.
    """
    host = (urlparse(candidate.source_page or candidate.image_url).hostname or "").lower()
    host = host[4:] if host.startswith("www.") else host

    known = KNOWN_LICENCE_HOSTS.get(host)
    if known:
        note = (
            "Host publishes machine-readable reuse terms. Open the source page, "
            "confirm the exact licence and required credit, then set "
            f'"approval_status": "{APPROVAL_APPROVED}".'
        )
        attribution = f"{candidate.title or 'Untitled'} — {host}"
        return known, attribution, note

    hint = candidate.licence_hint or "unknown"
    note = (
        "Reuse terms could not be determined from search metadata. Appearing in "
        "Google Images is not a licence: verify rights on the source page (or "
        "discard this candidate) before approving it."
    )
    attribution = f"{candidate.title or 'Untitled'} — {host or 'unknown source'}"
    return hint, attribution, note


def policy_flags(candidate: ImageCandidate) -> list[str]:
    """Surface subject-matter risks for the human reviewer."""
    flags: list[str] = []
    haystack = f"{candidate.title} {candidate.query}".lower()

    people_terms = ("teenager", "child", "kid", "girl", "boy", "woman", "man", "parent", "student")
    if any(term in haystack for term in people_terms):
        flags.append(
            "may_depict_people: approve only with a licence covering identifiable "
            "persons; never approve identifiable minors"
        )

    distress_terms = ("crying", "victim", "abuse", "scared", "depressed", "sad")
    if any(term in haystack for term in distress_terms):
        flags.append("may_depict_distress: avoid imagery that could deepen a user's distress")

    host = (urlparse(candidate.source_page or candidate.image_url).hostname or "").lower()
    if not any(preferred in host for preferred in PREFERRED_HOSTS):
        flags.append("unverified_source: prefer Wikimedia Commons or a reputable free-stock host")

    return flags


def rank_candidates(candidates: Sequence[ImageCandidate]) -> list[ImageCandidate]:
    """Prefer hosts with documented reuse terms, then larger images."""

    def sort_key(candidate: ImageCandidate) -> tuple[int, int]:
        host = (urlparse(candidate.source_page or candidate.image_url).hostname or "").lower()
        preferred = 0 if any(known in host for known in PREFERRED_HOSTS) else 1
        area = (candidate.reported_width or 0) * (candidate.reported_height or 0)
        return (preferred, -area)

    return sorted(candidates, key=sort_key)


# ──────────────────────────────────────────────────────────────────────────
# Manifest and attributions
# ──────────────────────────────────────────────────────────────────────────


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "generated_at": None, "assets": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SetupError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
        raise SetupError(f"{path} does not look like an assets manifest")
    return data


def merge_manifest(existing: dict[str, Any], new_entries: Iterable[ManifestEntry]) -> dict[str, Any]:
    """Merge by sha256. An approved asset is never silently replaced."""
    by_digest: dict[str, dict[str, Any]] = {
        str(asset.get("sha256")): asset for asset in existing.get("assets", [])
    }

    for entry in new_entries:
        current = by_digest.get(entry.sha256)
        if current and current.get("approval_status") == APPROVAL_APPROVED:
            logger.info(
                "Keeping approved asset %s untouched (same sha256)", current.get("file_name")
            )
            continue
        if current and current.get("approval_status") == APPROVAL_REJECTED:
            logger.info("Skipping previously rejected asset %s", current.get("file_name"))
            continue
        by_digest[entry.sha256] = asdict(entry)

    merged = dict(existing)
    merged["version"] = 1
    merged["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    merged["policy"] = {
        "approval_required": True,
        "usable_status": APPROVAL_APPROVED,
        "note": (
            "The application may only reference assets whose approval_status is "
            f'"{APPROVAL_APPROVED}". Appearance in an image search is not a licence.'
        ),
    }
    merged["assets"] = sorted(by_digest.values(), key=lambda asset: str(asset.get("file_name")))
    return merged


def write_attributions(manifest: dict[str, Any], path: Path) -> None:
    assets = manifest.get("assets", [])
    approved = [a for a in assets if a.get("approval_status") == APPROVAL_APPROVED]
    pending = [a for a in assets if a.get("approval_status") == APPROVAL_REVIEW]

    lines: list[str] = [
        "# Image attributions",
        "",
        "Generated by `scripts/fetch_google_images.py`. Do not edit by hand —",
        "edit `assets-manifest.json` and re-run the script.",
        "",
        "**Only assets listed as approved may be referenced by the application.**",
        "Appearing in an image search is not a licence.",
        "",
        f"_Last generated: {manifest.get('generated_at') or 'never'}_",
        "",
        "## Approved for use",
        "",
    ]

    if approved:
        lines += ["| File | Title | Source | Licence | Attribution |", "|---|---|---|---|---|"]
        for asset in approved:
            lines.append(
                f"| `{asset.get('file_name')}` | {asset.get('title') or '—'} "
                f"| {asset.get('source_page') or '—'} | {asset.get('licence') or '—'} "
                f"| {asset.get('attribution') or '—'} |"
            )
    else:
        lines.append("_No asset has been approved yet, so the interface uses its built-in "
                     "illustration instead._")

    lines += ["", "## Awaiting licence review", ""]
    if pending:
        for asset in pending:
            lines.append(f"- `{asset.get('file_name')}` — {asset.get('source_page') or 'unknown source'}")
            if asset.get("review_notes"):
                lines.append(f"  - {asset['review_notes']}")
            for flag in asset.get("policy_flags", []):
                lines.append(f"  - ⚠ {flag}")
    else:
        lines.append("_Nothing pending._")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────
# Orchestration
# ──────────────────────────────────────────────────────────────────────────


def load_queries(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not path.exists():
        raise SetupError(f"Query file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    queries = data.get("queries") or []
    if not queries:
        raise SetupError(f"No queries defined in {path}")
    return queries, data.get("defaults", {})


def process_candidate(
    session: Any,
    candidate: ImageCandidate,
    *,
    min_width: int,
    min_height: int,
    max_bytes: int,
    output_dir: Path,
    seen_digests: set[str],
) -> ManifestEntry:
    raw, content_type = download_image(session, candidate.image_url, max_bytes=max_bytes)
    webp, width, height = to_optimized_webp(raw, min_width=min_width, min_height=min_height)

    digest = sha256_of(webp)
    if digest in seen_digests:
        raise FetchError("Duplicate image (identical sha256 already stored)")
    seen_digests.add(digest)

    file_name = deterministic_file_name(candidate.query_id or candidate.query, digest)
    licence, attribution, review_note = classify_licence(candidate)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / file_name).write_bytes(webp)

    return ManifestEntry(
        file_name=file_name,
        query_id=candidate.query_id,
        query=candidate.query,
        title=candidate.title,
        source_page=candidate.source_page,
        original_image_url=candidate.image_url,
        provider=candidate.provider,
        width=width,
        height=height,
        mime_type="image/webp",
        original_mime_type=content_type,
        sha256=digest,
        bytes=len(webp),
        acquired_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        licence=licence,
        attribution=attribution,
        approval_status=APPROVAL_REVIEW,
        review_notes=review_note,
        policy_flags=policy_flags(candidate),
    )


def run(args: argparse.Namespace) -> int:
    queries, defaults = load_queries(Path(args.queries))
    min_width = args.min_width or int(defaults.get("min_width", 900))
    min_height = args.min_height or int(defaults.get("min_height", 500))
    output_dir = Path(args.output)
    manifest_path = output_dir / MANIFEST_NAME

    try:
        import requests
    except ImportError as exc:
        raise SetupError(
            "The 'requests' package is required.\n"
            "  pip install -r scripts/requirements-images.txt"
        ) from exc

    session = requests.Session()
    session.headers.update({"User-Agent": "EMC-Helpline-image-fetch/1.0 (+internal tooling)"})

    provider = build_provider(args.provider, session)
    logger.info("Using search provider: %s", provider.name)

    existing = load_manifest(manifest_path)
    seen_digests = {str(asset.get("sha256")) for asset in existing.get("assets", [])}
    new_entries: list[ManifestEntry] = []

    for query_spec in queries:
        query_id = str(query_spec.get("id") or slugify(str(query_spec.get("query", ""))))
        query = str(query_spec.get("query", "")).strip()
        if not query:
            continue

        logger.info("Searching: %s", query)
        try:
            found = provider.search(query, args.count, defaults)
        except FetchError as exc:
            logger.error("Search failed for %r: %s", query, exc)
            continue

        candidates = [
            ImageCandidate(**{**asdict(candidate), "query_id": query_id})
            for candidate in rank_candidates(found)
        ]

        if args.dry_run:
            logger.info("  [dry-run] %d candidate(s); nothing downloaded", len(candidates))
            for candidate in candidates[: args.count]:
                licence, _, _ = classify_licence(candidate)
                logger.info(
                    "  [dry-run] %s | %s | licence: %s | flags: %s",
                    candidate.image_url[:80],
                    candidate.source_page[:60] or "unknown source",
                    licence,
                    ", ".join(policy_flags(candidate)) or "none",
                )
            continue

        stored = 0
        for candidate in candidates:
            if stored >= args.count:
                break
            try:
                entry = process_candidate(
                    session,
                    candidate,
                    min_width=min_width,
                    min_height=min_height,
                    max_bytes=args.max_bytes,
                    output_dir=output_dir,
                    seen_digests=seen_digests,
                )
            except FetchError as exc:
                logger.warning("  skipped %s: %s", candidate.image_url[:70], exc)
                continue
            new_entries.append(entry)
            stored += 1
            logger.info("  stored %s (%dx%d, %s)", entry.file_name, entry.width, entry.height, entry.licence)

    if args.dry_run:
        logger.info("Dry run complete. No file was written.")
        return 0

    merged = merge_manifest(existing, new_entries)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_attributions(merged, output_dir / ATTRIBUTIONS_NAME)

    approved = sum(1 for a in merged["assets"] if a.get("approval_status") == APPROVAL_APPROVED)
    logger.info(
        "Wrote %s (%d asset(s), %d approved, %d awaiting review).",
        manifest_path,
        len(merged["assets"]),
        approved,
        len(merged["assets"]) - approved,
    )
    if new_entries:
        logger.warning(
            "New assets are recorded as '%s'. Verify each licence on its source page and "
            "flip approval_status to '%s' before the interface may use it.",
            APPROVAL_REVIEW,
            APPROVAL_APPROVED,
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch, normalise and document supportive imagery for the EMC Helpline frontend.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--queries", default=str(DEFAULT_QUERIES), help="Path to the query JSON file.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Directory to write images into.")
    parser.add_argument("--count", type=int, default=2, help="Images to keep per query (default: 2).")
    parser.add_argument(
        "--provider",
        choices=("auto", "serpapi", "google_cse"),
        default="auto",
        help="Search provider (default: auto — SerpAPI first, then Google CSE).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Search only; download and write nothing.")
    parser.add_argument("--min-width", type=int, default=None, help="Minimum accepted width in pixels.")
    parser.add_argument("--min-height", type=int, default=None, help="Minimum accepted height in pixels.")
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=MAX_DOWNLOAD_BYTES,
        help=f"Maximum download size in bytes (default: {MAX_DOWNLOAD_BYTES}).",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)-8s %(message)s",
    )
    try:
        return run(args)
    except SetupError as exc:
        logger.error("Setup required\n\n%s", exc)
        return 2
    except KeyboardInterrupt:
        logger.warning("Interrupted; nothing further was written.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
