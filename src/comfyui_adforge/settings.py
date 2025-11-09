"""
Shared settings and configuration for AdForge nodes.
"""

import datetime
from enum import Enum
from typing import List, Optional

from dotenv import find_dotenv
from google.genai.types import VideoCompressionQuality
from pydantic_settings import BaseSettings, SettingsConfigDict


class DefaultMixin:
    """
    An Enum class that can specify a default member.

    The default is designated by assigning it to `_default`.
    """

    _default = None

    @classmethod
    def options(cls) -> List[str]:
        """Return a list of all member values."""
        return [member.value for member in cls]

    @classmethod
    def default(cls):
        """Return the value of the default member."""
        if cls._default is None:
            raise NotImplementedError(f"No `_default` member defined for {cls.__name__}")
        return cls._default.value


# --- Enums for Dropdown Choices ---


class AspectRatio(DefaultMixin, Enum):
    SIXTEEN_BY_NINE = "16:9"
    NINE_BY_SIXTEEN = "9:16"
    ONE_BY_ONE = "1:1"
    _default = SIXTEEN_BY_NINE


class Resolution(DefaultMixin, Enum):
    FHD_1080P = "1080p"
    HD_720P = "720p"
    _default = FHD_1080P


class PersonGeneration(DefaultMixin, Enum):
    ALLOW_ADULT = "allow_adult"
    DONT_ALLOW = "dont_allow"
    _default = ALLOW_ADULT


class OutputFormat(DefaultMixin, Enum):
    LOCAL_FILE = "local_file"
    GCS_URI = "gcs_uri"
    _default = LOCAL_FILE


class ImageMimeType(DefaultMixin, Enum):
    PNG = "image/png"
    JPEG = "image/jpeg"
    _default = PNG


class VideoMimeType(DefaultMixin, Enum):
    MP4 = "video/mp4"
    _default = MP4


class ReferenceType(DefaultMixin, Enum):
    ASSET = "ASSET"
    STYLE = "STYLE"
    _default = ASSET


class CompressionQuality(DefaultMixin, Enum):
    LOSSLESS = VideoCompressionQuality.LOSSLESS
    OPTIMIZED = VideoCompressionQuality.OPTIMIZED
    _default = LOSSLESS


class VeoModel(DefaultMixin, Enum):
    V3_1_PREVIEW = "veo-3.1-generate-preview"
    V3_1_FAST_PREVIEW = "veo-3.1-fast-generate-preview"
    V3_0 = "veo-3.0-generate-001"
    V3_0_FAST = "veo-3.0-fast-generate-001"
    V2_0 = "veo-2.0-generate-001"
    V2_0_EXP = "veo-2.0-generate-exp"
    V2_0_PREVIEW = "veo-2.0-generate-preview"
    _default = V3_1_PREVIEW


class MaskModel(DefaultMixin, Enum):
    V2_0_PREVIEW = "veo-2.0-generate-preview"
    V2_0 = "veo-2.0-generate-001"
    _default = V2_0_PREVIEW


POLL_DELAY_SECONDS: int = 5
DEFAULT_DURATION_SECONDS: int = 8


class Credentials(BaseSettings):
    """Manages all credentials"""

    # GCP Authentication
    GOOGLE_CLOUD_STORAGE_BUCKET: Optional[str] = None
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_LOCATION: Optional[str] = "global"
    API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        extra="ignore",
    )


# --- Global Settings Instance ---
credentials = Credentials()


def get_default_gcs_uri(filename_prefix: str) -> str:
    """
    Generate a default GCS URI for video output.
    Args:
        filename_prefix: Prefix for the filename (e.g., "text-to-video")
    Returns:
        A GCS URI string.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{credentials.GOOGLE_CLOUD_STORAGE_BUCKET}/videos/{filename_prefix}-{timestamp}.mp4"
