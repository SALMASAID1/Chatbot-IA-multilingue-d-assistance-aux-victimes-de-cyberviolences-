"""Tests for scripts/fetch_google_images.py.

The search API and the image host are both mocked, so the suite is offline,
deterministic, and spends no API credits.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest
from PIL import Image

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import fetch_google_images as fgi  # noqa: E402


# ── helpers ────────────────────────────────────────────────────────────────


def make_jpeg(width: int = 1200, height: int = 800, *, with_exif: bool = False) -> bytes:
    image = Image.new("RGB", (width, height), (200, 220, 215))
    buffer = io.BytesIO()
    if with_exif:
        exif = Image.Exif()
        exif[271] = "ACME Camera"          # Make
        exif[272] = "Model X"              # Model
        exif[306] = "2026:08:24 10:00:00"  # DateTime
        image.save(buffer, format="JPEG", exif=exif)
    else:
        image.save(buffer, format="JPEG")
    return buffer.getvalue()


class FakeResponse:
    def __init__(self, *, payload=None, content=b"", headers=None, status_code=200):
        self._payload = payload
        self._content = content
        self.headers = headers or {}
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload

    def iter_content(self, chunk_size=65536):
        for start in range(0, len(self._content), chunk_size):
            yield self._content[start : start + chunk_size]


class FakeSession:
    """Returns a queued response per URL prefix."""

    def __init__(self, routes: dict[str, FakeResponse]):
        self.routes = routes
        self.calls: list[tuple[str, dict]] = []
        self.headers: dict[str, str] = {}

    def get(self, url, params=None, timeout=None, stream=False):
        self.calls.append((url, params or {}))
        for prefix, response in self.routes.items():
            if url.startswith(prefix):
                return response
        raise AssertionError(f"Unexpected request to {url}")


def candidate(**overrides) -> fgi.ImageCandidate:
    base = dict(
        query_id="calm-confidential-online-help",
        query="calm confidential online help illustration",
        title="Calm supportive illustration",
        source_page="https://commons.wikimedia.org/wiki/File:Example.svg",
        image_url="https://upload.wikimedia.org/example.jpg",
        provider="serpapi",
        reported_width=1200,
        reported_height=800,
    )
    base.update(overrides)
    return fgi.ImageCandidate(**base)


# ── naming and hashing ─────────────────────────────────────────────────────


def test_file_names_are_deterministic_and_descriptive():
    digest = fgi.sha256_of(b"same-bytes")
    first = fgi.deterministic_file_name("calm confidential online help", digest)
    second = fgi.deterministic_file_name("calm confidential online help", digest)
    assert first == second
    assert first.startswith("calm-confidential-online-help-")
    assert first.endswith(".webp")


def test_slugify_strips_unsafe_characters():
    assert fgi.slugify("Aide  — Confidentielle !!") == "aide-confidentielle"


# ── licensing policy ───────────────────────────────────────────────────────


def test_search_results_are_never_auto_approved():
    licence, attribution, note = fgi.classify_licence(candidate())
    assert "Wikimedia" in licence
    assert attribution
    assert "not a licence" in note or "confirm the exact licence" in note


def test_unknown_hosts_are_marked_for_review():
    licence, _, note = fgi.classify_licence(
        candidate(source_page="https://random-blog.example/post", image_url="https://random-blog.example/a.jpg")
    )
    assert licence == "unknown"
    assert "not a licence" in note


def test_policy_flags_warn_about_people_and_unverified_sources():
    flags = fgi.policy_flags(
        candidate(
            title="Parent helping teenager online",
            query="parent helping teenager online safety illustration",
            source_page="https://random-blog.example/post",
            image_url="https://random-blog.example/a.jpg",
        )
    )
    assert any("may_depict_people" in flag for flag in flags)
    assert any("unverified_source" in flag for flag in flags)


def test_preferred_hosts_rank_first():
    ranked = fgi.rank_candidates(
        [
            candidate(source_page="https://random-blog.example/x", image_url="https://random-blog.example/a.jpg"),
            candidate(),
        ]
    )
    assert "wikimedia" in ranked[0].source_page


# ── download guards ────────────────────────────────────────────────────────


def test_rejects_non_image_content_types():
    session = FakeSession(
        {"https://host": FakeResponse(content=b"<html>", headers={"Content-Type": "text/html"})}
    )
    with pytest.raises(fgi.FetchError, match="Unsupported content type"):
        fgi.download_image(session, "https://host/a.html")


def test_rejects_oversized_downloads():
    payload = make_jpeg()
    session = FakeSession(
        {
            "https://host": FakeResponse(
                content=payload,
                headers={"Content-Type": "image/jpeg", "Content-Length": str(len(payload))},
            )
        }
    )
    with pytest.raises(fgi.FetchError, match="too large"):
        fgi.download_image(session, "https://host/a.jpg", max_bytes=10)


def test_rejects_non_http_urls():
    session = FakeSession({})
    with pytest.raises(fgi.FetchError, match="non-HTTP"):
        fgi.download_image(session, "file:///etc/passwd")


# ── image processing ───────────────────────────────────────────────────────


def test_rejects_images_below_minimum_dimensions():
    with pytest.raises(fgi.FetchError, match="too small"):
        fgi.to_optimized_webp(make_jpeg(200, 100), min_width=900, min_height=500)


def test_converts_to_webp_and_strips_exif():
    original = make_jpeg(1200, 800, with_exif=True)
    assert Image.open(io.BytesIO(original)).getexif()

    webp, width, height = fgi.to_optimized_webp(original, min_width=900, min_height=500)

    with Image.open(io.BytesIO(webp)) as result:
        assert result.format == "WEBP"
        assert (width, height) == result.size
        assert dict(result.getexif()) == {}
    assert len(webp) < len(original)


def test_downscales_very_large_images():
    _, width, _ = fgi.to_optimized_webp(make_jpeg(3000, 2000), min_width=900, min_height=500)
    assert width == fgi.MAX_STORED_WIDTH


# ── manifest behaviour ─────────────────────────────────────────────────────


def entry(**overrides) -> fgi.ManifestEntry:
    base = dict(
        file_name="calm-abc123456789.webp",
        query_id="calm",
        query="calm",
        title="t",
        source_page="https://commons.wikimedia.org/x",
        original_image_url="https://upload.wikimedia.org/x.jpg",
        provider="serpapi",
        width=1200,
        height=800,
        mime_type="image/webp",
        original_mime_type="image/jpeg",
        sha256="digest-1",
        bytes=1234,
        acquired_at="2026-08-24T10:00:00+00:00",
        licence="CC BY-SA",
        attribution="Someone",
    )
    base.update(overrides)
    return fgi.ManifestEntry(**base)


def test_new_assets_require_review():
    assert entry().approval_status == fgi.APPROVAL_REVIEW


def test_approved_assets_are_never_silently_replaced():
    existing = {
        "version": 1,
        "assets": [
            {
                "file_name": "approved.webp",
                "sha256": "digest-1",
                "approval_status": fgi.APPROVAL_APPROVED,
                "licence": "CC0",
                "attribution": "Reviewed by hand",
            }
        ],
    }
    merged = fgi.merge_manifest(existing, [entry(file_name="new.webp", licence="unknown")])
    stored = [a for a in merged["assets"] if a["sha256"] == "digest-1"]
    assert len(stored) == 1
    assert stored[0]["file_name"] == "approved.webp"
    assert stored[0]["approval_status"] == fgi.APPROVAL_APPROVED


def test_rejected_assets_are_not_reintroduced():
    existing = {
        "version": 1,
        "assets": [{"file_name": "bad.webp", "sha256": "digest-1", "approval_status": "rejected"}],
    }
    merged = fgi.merge_manifest(existing, [entry()])
    assert merged["assets"][0]["approval_status"] == "rejected"


def test_manifest_records_the_full_provenance(tmp_path: Path):
    merged = fgi.merge_manifest({"version": 1, "assets": []}, [entry()])
    asset = merged["assets"][0]
    for field in (
        "query",
        "title",
        "source_page",
        "original_image_url",
        "width",
        "height",
        "mime_type",
        "sha256",
        "acquired_at",
        "licence",
        "attribution",
        "approval_status",
    ):
        assert field in asset, f"manifest must record {field}"
    assert merged["policy"]["usable_status"] == fgi.APPROVAL_APPROVED

    path = tmp_path / "assets-manifest.json"
    path.write_text(json.dumps(merged), encoding="utf-8")
    assert fgi.load_manifest(path)["assets"][0]["sha256"] == "digest-1"


def test_attributions_file_separates_approved_from_pending(tmp_path: Path):
    merged = fgi.merge_manifest(
        {"version": 1, "assets": []},
        [entry(sha256="d1", file_name="pending.webp")],
    )
    merged["assets"].append(
        {
            "file_name": "ok.webp",
            "title": "Approved art",
            "source_page": "https://commons.wikimedia.org/ok",
            "licence": "CC0",
            "attribution": "Artist",
            "approval_status": fgi.APPROVAL_APPROVED,
            "sha256": "d2",
        }
    )
    out = tmp_path / "ATTRIBUTIONS.md"
    fgi.write_attributions(merged, out)
    text = out.read_text(encoding="utf-8")

    assert "## Approved for use" in text
    assert "ok.webp" in text
    assert "## Awaiting licence review" in text
    assert "pending.webp" in text
    assert "not a licence" in text


# ── provider selection ─────────────────────────────────────────────────────


def test_missing_credentials_raise_a_setup_error(monkeypatch):
    for name in ("SERPAPI_KEY", "GOOGLE_CSE_API_KEY", "GOOGLE_CSE_CX"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(fgi.SetupError) as excinfo:
        fgi.build_provider("auto", FakeSession({}))
    assert "SERPAPI_KEY" in str(excinfo.value)
    assert "Nothing was downloaded" in str(excinfo.value)


def test_serpapi_is_preferred_and_enables_safe_search(monkeypatch):
    monkeypatch.setenv("SERPAPI_KEY", "test-key")
    session = FakeSession(
        {
            fgi.SERPAPI_ENDPOINT: FakeResponse(
                payload={
                    "images_results": [
                        {
                            "original": "https://upload.wikimedia.org/a.jpg",
                            "link": "https://commons.wikimedia.org/wiki/File:A",
                            "title": "A calm illustration",
                            "original_width": 1200,
                            "original_height": 800,
                        }
                    ]
                }
            )
        }
    )
    provider = fgi.build_provider("auto", session)
    assert isinstance(provider, fgi.SerpApiProvider)

    results = provider.search("calm help", 2, {"safe_search": True, "country": "ma", "language": "fr"})
    _, params = session.calls[0]
    assert params["engine"] == "google_images"
    assert params["safe"] == "active"
    assert params["gl"] == "ma" and params["hl"] == "fr"
    assert results[0].image_url == "https://upload.wikimedia.org/a.jpg"


def test_google_cse_adapter_filters_on_reuse_rights(monkeypatch):
    monkeypatch.delenv("SERPAPI_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_CSE_API_KEY", "k")
    monkeypatch.setenv("GOOGLE_CSE_CX", "cx")
    session = FakeSession({fgi.GOOGLE_CSE_ENDPOINT: FakeResponse(payload={"items": []})})

    provider = fgi.build_provider("auto", session)
    assert isinstance(provider, fgi.GoogleCseProvider)

    provider.search("calm help", 2, {})
    _, params = session.calls[0]
    assert params["searchType"] == "image"
    assert params["safe"] == "active"
    assert "cc_publicdomain" in params["rights"]


# ── end-to-end with mocked network ─────────────────────────────────────────


def test_full_run_downloads_normalises_and_documents(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SERPAPI_KEY", "test-key")
    queries = tmp_path / "queries.json"
    queries.write_text(
        json.dumps(
            {
                "defaults": {"safe_search": True, "min_width": 900, "min_height": 500},
                "queries": [{"id": "calm-help", "query": "calm confidential online help illustration"}],
            }
        ),
        encoding="utf-8",
    )

    jpeg = make_jpeg(1200, 800, with_exif=True)
    session = FakeSession(
        {
            fgi.SERPAPI_ENDPOINT: FakeResponse(
                payload={
                    "images_results": [
                        {
                            "original": "https://upload.wikimedia.org/a.jpg",
                            "link": "https://commons.wikimedia.org/wiki/File:A",
                            "title": "Calm illustration",
                            "original_width": 1200,
                            "original_height": 800,
                        }
                    ]
                }
            ),
            "https://upload.wikimedia.org": FakeResponse(
                content=jpeg, headers={"Content-Type": "image/jpeg"}
            ),
        }
    )
    monkeypatch.setattr(fgi, "_request_json", lambda s, url, params: s.get(url, params=params).json())

    class FakeRequests:
        @staticmethod
        def Session():  # noqa: N802 - mirrors requests' API
            return session

    monkeypatch.setitem(sys.modules, "requests", FakeRequests)

    out = tmp_path / "images"
    args = fgi.build_parser().parse_args(
        ["--queries", str(queries), "--output", str(out), "--count", "1"]
    )
    assert fgi.run(args) == 0

    written = list(out.glob("*.webp"))
    assert len(written) == 1
    assert written[0].name.startswith("calm-help-")

    manifest = json.loads((out / "assets-manifest.json").read_text(encoding="utf-8"))
    asset = manifest["assets"][0]
    assert asset["approval_status"] == fgi.APPROVAL_REVIEW
    assert asset["mime_type"] == "image/webp"
    assert asset["original_mime_type"] == "image/jpeg"
    assert len(asset["sha256"]) == 64
    with Image.open(written[0]) as stored:
        assert dict(stored.getexif()) == {}

    attributions = (out / "ATTRIBUTIONS.md").read_text(encoding="utf-8")
    assert "Awaiting licence review" in attributions
    assert "No asset has been approved yet" in attributions


def test_dry_run_writes_nothing(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SERPAPI_KEY", "test-key")
    queries = tmp_path / "queries.json"
    queries.write_text(
        json.dumps({"defaults": {}, "queries": [{"id": "calm", "query": "calm help"}]}),
        encoding="utf-8",
    )
    session = FakeSession(
        {
            fgi.SERPAPI_ENDPOINT: FakeResponse(
                payload={
                    "images_results": [
                        {
                            "original": "https://upload.wikimedia.org/a.jpg",
                            "link": "https://commons.wikimedia.org/wiki/File:A",
                            "title": "Calm",
                        }
                    ]
                }
            )
        }
    )

    class FakeRequests:
        @staticmethod
        def Session():  # noqa: N802
            return session

    monkeypatch.setitem(sys.modules, "requests", FakeRequests)

    out = tmp_path / "images"
    args = fgi.build_parser().parse_args(
        ["--queries", str(queries), "--output", str(out), "--dry-run"]
    )
    assert fgi.run(args) == 0
    assert not out.exists()
