"""
Load Video from GCS Node for ComfyUI

Downloads videos from Google Cloud Storage and provides local path for VideoHelperSuite.
"""

import os
from typing import Any, Dict

from google.cloud import storage

from comfyui_adforge.documentation import get_documentation
from comfyui_adforge.settings import credentials


class LoadVideoGCS:
    """
    Load a video from Google Cloud Storage and provide local path for processing.

    This node downloads a video from GCS to a temporary local location and returns
    the path in a format compatible with VideoHelperSuite's LoadVideoPath node.

    Authentication is handled automatically by Google Cloud client library using:
    - GOOGLE_APPLICATION_CREDENTIALS environment variable
    - gcloud auth application-default login
    - Service account when running on GCP
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input parameters for the node."""
        return {
            "required": {
                "video_uri": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "gs://your-bucket/video.mp4",
                        "tooltip": "GCS URI of the video (gs://bucket/path/to/video.mp4)",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_path",)
    FUNCTION = "load_video"
    CATEGORY = "Creditas' AdForge/Video Generation"
    DESCRIPTION = get_documentation("LoadVideoGCS")

    def load_video(self, video_uri: str) -> tuple[str]:
        """
        Download video from GCS and return local file path with text preview.

        Args:
            video_uri (str): GCS URI (gs://bucket/path/to/video.mp4)

        Returns:
            A tuple containing the local file path to the downloaded video.
        """
        # Parse GCS URI
        if not video_uri.startswith("gs://"):
            raise ValueError("video_uri must be a valid GCS URI starting with gs://")

        # Extract bucket and path from URI
        uri_parts = video_uri[5:].split("/", 1)
        bucket_name = uri_parts[0]
        blob_path = uri_parts[1] if len(uri_parts) > 1 else ""

        if not bucket_name:
            raise ValueError("GCS bucket name must be provided in the URI")

        if not blob_path:
            raise ValueError("Video path in GCS bucket is required")

        # Initialize GCS client - authentication handled automatically by Google Cloud
        client = storage.Client(
            project=credentials.GOOGLE_CLOUD_PROJECT,
        )

        # Get the bucket and blob
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)

        # Get the ComfyUI output directory and create a subfolder for GCS downloads
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "ComfyUI", "output")
        download_dir = os.path.join(output_dir, "gcs_downloads")
        os.makedirs(download_dir, exist_ok=True)

        # Generate local filename from blob path
        filename = os.path.basename(blob_path)
        local_path = os.path.join(download_dir, filename)

        # Download the video
        blob.download_to_filename(local_path)

        return (local_path,)

    @classmethod
    def IS_CHANGED(cls, video_uri: str) -> str:
        """Return video URI as hash to detect changes."""
        return video_uri
