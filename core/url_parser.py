"""BBB URL parser and inspection service.

Parses BigBlueButton playback URLs, extracts meeting identifiers,
and checks for the existence of specific session assets on the remote server.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse
import requests


@dataclass
class BBBMetadata:
    url: str
    meeting_id: str
    base_url: str
    has_audio: bool = False
    has_deskshare: bool = False
    has_webcam: bool = False
    has_shapes: bool = False


class BBBUrlParser:
    """Parses and inspects BigBlueButton playback URLs."""

    MEETING_ID_PATTERN = re.compile(r"([0-9a-f]{40,}-\d+)")

    @classmethod
    def extract_meeting_id(cls, url: str) -> str | None:
        """Extracts the meetingId from query params or URL path."""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        if "meetingId" in params and params["meetingId"]:
            return params["meetingId"][0]

        match = cls.MEETING_ID_PATTERN.search(url)
        if match:
            return match.group(1)

        # Fallback to last path segment if formatted like an ID
        path_segments = [seg for seg in parsed.path.split("/") if seg]
        if path_segments and "-" in path_segments[-1]:
            return path_segments[-1]

        return None

    @classmethod
    def get_session_base_url(cls, url: str, meeting_id: str) -> str:
        """Constructs the base URL for the session raw assets."""
        parsed = urlparse(url)
        scheme = parsed.scheme or "https"
        netloc = parsed.netloc

        # Standard BigBlueButton presentation path
        if "/playback/presentation/" in parsed.path:
            version_match = re.search(r"/playback/presentation/([^/]+)/", parsed.path)
            version = version_match.group(1) if version_match else "2.3"
            return f"{scheme}://{netloc}/presentation/{meeting_id}"

        return f"{scheme}://{netloc}/presentation/{meeting_id}"

    @classmethod
    def inspect_session(cls, url: str) -> BBBMetadata:
        """Inspects remote availability of streams and slides for a meeting."""
        meeting_id = cls.extract_meeting_id(url)
        if not meeting_id:
            raise ValueError(
                f"No se pudo extraer el 'meetingId' de la URL: {url}. "
                "Asegúrate de que sea un enlace válido de grabación de BigBlueButton."
            )

        base_url = cls.get_session_base_url(url, meeting_id)
        meta = BBBMetadata(url=url, meeting_id=meeting_id, base_url=base_url)

        # Check endpoints with quick HEAD or GET range requests
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

        def probe(endpoint: str) -> bool:
            try:
                res = session.head(f"{base_url}/{endpoint}", timeout=4, allow_redirects=True)
                return res.status_code == 200
            except Exception:
                return False

        has_webcams = (
            probe("video/webcams.webm")
            or probe("video/webcams.mp4")
            or probe("video/webcam.webm")
            or probe("video/webcam.mp4")
        )
        has_direct_audio = (
            probe("audio/audio.webm")
            or probe("audio/audio.ogg")
            or probe("audio/audio.mp4")
        )
        meta.has_audio = has_direct_audio or has_webcams
        meta.has_deskshare = probe("deskshare/deskshare.webm") or probe("deskshare/deskshare.mp4")
        meta.has_webcam = has_webcams
        meta.has_shapes = probe("shapes.svg")

        return meta
