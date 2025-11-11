"""
Utility functions for AdForge nodes.
"""

import datetime
import io  # This is Python's built-in I/O library, dont confuse with the ComfyUI's io/IO
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from PIL import Image as PILImage
from comfy_api.latest import (
    IO,
    VideoCodec,
    VideoContainer,
    VideoFromFile,
    VideoInput,
    ui,
)
import folder_paths
from google import genai
from google.cloud import storage
import numpy as np
import torch

from . import settings


def poll_operation(client: genai.Client, operation: Any) -> Any:
    """
    Poll a Google GenAI operation until it's complete.

    Args:
        client: The GenAI client.
        operation: The operation to poll.

    Returns:
        The completed operation result.

    Raises:
        RuntimeError: If the operation fails.
    """
    while not operation.done:
        time.sleep(settings.POLL_DELAY_SECONDS)
        operation = client.operations.get(operation)

    if operation.error:
        raise RuntimeError(f"Operation failed: {operation.error}")

    return operation.result


def process_genai_results(result, prefix: str) -> Tuple[List[VideoFromFile], List[str], List[ui.SavedResult]]:
    """
    Process generated videos from Google GenAI SDK  by downloading them from GCS and save them locally.
    """
    videos = []
    video_paths = []
    previews = []

    full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
        prefix, folder_paths.get_output_directory()
    )
    for i, video_data in enumerate(result.generated_videos):
        file = f"{filename}_{counter:05}_{i}.mp4"
        video_path = os.path.join(full_output_folder, file)
        download_from_gcs(video_data.video.uri, video_path)
        video_paths.append(video_path)
        videos.append(VideoFromFile(video_path))
        previews.append(ui.SavedResult(file, subfolder, IO.FolderType.output))

    return videos, video_paths, previews


def save_video_locally(video_bytes: bytes, seed: int) -> str:
    """
    Save video bytes to a local file in the ComfyUI output directory.

    Args:
        video_bytes: The video content.
        seed: The seed used for generation, for filename uniqueness.

    Returns:
        The absolute path to the saved video file.
    """
    output_dir = os.path.join(folder_paths.get_output_directory(), "vertex")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"video_{timestamp}_{seed if seed >= 0 else 'rand'}.mp4"
    video_path = os.path.join(output_dir, filename)

    with open(video_path, "wb") as f:
        f.write(video_bytes)

    return video_path


def get_genai_client() -> genai.Client:
    """
    Get a configured Google GenAI client.

    Returns:
        A genai.Client instance.
    """
    return genai.Client(
        vertexai=True,
        project=settings.credentials.GOOGLE_CLOUD_PROJECT,
        location=settings.credentials.GOOGLE_CLOUD_LOCATION,
    )


def get_gcs_client() -> storage.Client:
    """
    Get a configured Google Cloud Storage client.

    Returns:
        A storage.Client instance.
    """
    return storage.Client(
        project=settings.credentials.GOOGLE_CLOUD_PROJECT,
    )


def extract_keys_and_default(d: Dict[str, Any]) -> Tuple[List[str], str]:
    """
    Extract keys and the key marked as 'default' from a dictionary.

    Args:
        d: The dictionary to process.

    Returns:
        A tuple containing the list of keys and the default key.
    """
    keys = list(d.keys())
    default_key = next((k for k, v in d.items() if v == "default"), keys[0] if keys else "")
    return keys, default_key


def download_from_gcs(gcs_uri: str, output_path_or_seed: Union[str, int] = -1) -> str:
    """Download a file from Google Cloud Storage to a local path."""
    client = get_gcs_client()
    match = re.match(r"gs://([^/]+)/(.+)", gcs_uri)
    if not match:
        raise ValueError(f"Invalid GCS URI: {gcs_uri}")

    if isinstance(output_path_or_seed, str) and os.path.isabs(output_path_or_seed):
        # If an absolute path is provided, use it directly.
        file_path = output_path_or_seed
    else:
        # Otherwise, generate a filename from the seed.
        seed = output_path_or_seed
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        temp_dir = folder_paths.get_temp_directory()
        os.makedirs(temp_dir, exist_ok=True)
        filename = f"video_{timestamp}_{seed if seed >= 0 else 'rand'}.mp4"
        file_path = os.path.join(temp_dir, filename)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    bucket_name, blob_name = match.groups()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(file_path)
    return file_path


def bytify_image(image: "torch.Tensor") -> bytes:
    """
    Convert a torch.Tensor image to bytes.

    Args:
        image: The image tensor.

    Returns:
        The image as bytes.
    """
    if image is None:
        return None

    # Convert tensor to numpy array
    np_image = image.squeeze(0).cpu().numpy()

    # Convert from CHW to HWC format if needed
    if np_image.ndim == 3 and np_image.shape[0] in [1, 3, 4]:
        np_image = np.transpose(np_image, (1, 2, 0))

    # Normalize and convert to uint8
    np_image = (np_image * 255).astype(np.uint8)

    # Create PIL image
    pil_image = PILImage.fromarray(np_image)

    # Save to a byte stream
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()


def bytify_video(video_path: str | VideoInput) -> Optional[bytes]:
    """
    Read a video file and return its bytes.

    Args:
        video_path: The path to the video file.

    Returns:
        The video as bytes.
    """
    if not video_path:
        return None

    if isinstance(video_path, str) and os.path.exists(video_path):
        with open(video_path, "rb") as f:
            return f.read()
    elif isinstance(video_path, VideoInput):
        buffer = io.BytesIO()
        video_path.save_to(buffer, format=VideoContainer.AUTO, codec=VideoCodec.AUTO)
        buffer.seek(0)
        return buffer.read()
    return None
