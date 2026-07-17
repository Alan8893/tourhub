from dataclasses import dataclass


@dataclass(frozen=True)
class ClubBrandingDTO:
    club_name: str
    logo_bytes: bytes | None = None
    logo_mime_type: str | None = None
