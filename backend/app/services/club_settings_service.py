import base64
import binascii
from io import BytesIO

from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.engines.documents.branding import ClubBrandingDTO
from app.models.club_settings import ClubSettingsORM


DEFAULT_CLUB_NAME = "TourHub"
MAX_LOGO_BYTES = 1_000_000
MAX_LOGO_PIXELS = 16_000_000
ALLOWED_LOGO_MIME_TYPES = {"image/png", "image/jpeg"}
EXPECTED_IMAGE_FORMATS = {"image/png": "PNG", "image/jpeg": "JPEG"}


class ClubSettingsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self) -> ClubSettingsORM:
        settings = self.session.get(ClubSettingsORM, 1)
        if settings is not None:
            return settings

        settings = ClubSettingsORM(id=1, club_name=DEFAULT_CLUB_NAME)
        self.session.add(settings)
        self.session.commit()
        self.session.refresh(settings)
        return settings

    def update(
        self,
        *,
        club_name: str,
        logo_data_url: str | None,
        remove_logo: bool,
    ) -> ClubSettingsORM:
        normalized_name = club_name.strip()
        if not normalized_name:
            raise ValueError("Club name cannot be empty")
        if logo_data_url is not None and remove_logo:
            raise ValueError("Logo upload and removal cannot be requested together")

        settings = self.get()
        settings.club_name = normalized_name

        if remove_logo:
            settings.logo_mime_type = None
            settings.logo_bytes = None
        elif logo_data_url is not None:
            mime_type, logo_bytes = self._decode_logo(logo_data_url)
            settings.logo_mime_type = mime_type
            settings.logo_bytes = logo_bytes

        self.session.commit()
        self.session.refresh(settings)
        return settings

    def to_branding(self) -> ClubBrandingDTO:
        settings = self.get()
        return ClubBrandingDTO(
            club_name=settings.club_name,
            logo_bytes=settings.logo_bytes,
            logo_mime_type=settings.logo_mime_type,
        )

    @staticmethod
    def logo_data_url(settings: ClubSettingsORM) -> str | None:
        if settings.logo_bytes is None or settings.logo_mime_type is None:
            return None
        encoded = base64.b64encode(settings.logo_bytes).decode("ascii")
        return f"data:{settings.logo_mime_type};base64,{encoded}"

    @staticmethod
    def _decode_logo(data_url: str) -> tuple[str, bytes]:
        header, separator, payload = data_url.partition(",")
        if not separator or not header.startswith("data:") or not header.endswith(";base64"):
            raise ValueError("Logo must be a base64 data URL")

        mime_type = header[5:-7]
        if mime_type not in ALLOWED_LOGO_MIME_TYPES:
            raise ValueError("Logo must be PNG or JPEG")

        try:
            logo_bytes = base64.b64decode(payload, validate=True)
        except (ValueError, binascii.Error) as error:
            raise ValueError("Logo contains invalid base64 data") from error

        if not logo_bytes:
            raise ValueError("Logo cannot be empty")
        if len(logo_bytes) > MAX_LOGO_BYTES:
            raise ValueError("Logo must not exceed 1 MB")

        try:
            with Image.open(BytesIO(logo_bytes)) as image:
                width, height = image.size
                image_format = image.format
                if width * height > MAX_LOGO_PIXELS:
                    raise ValueError("Logo dimensions are too large")
                image.verify()
        except ValueError:
            raise
        except (
            UnidentifiedImageError,
            Image.DecompressionBombError,
            OSError,
            SyntaxError,
        ) as error:
            raise ValueError("Logo is not a valid image") from error

        if image_format != EXPECTED_IMAGE_FORMATS[mime_type]:
            raise ValueError("Logo content does not match its MIME type")

        return mime_type, logo_bytes
