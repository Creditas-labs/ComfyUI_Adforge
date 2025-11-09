"""
Utility functions for AdForge nodes.
"""

import datetime
import io
import os
import time
from typing import Any, Dict, List, Tuple

from PIL import Image as PILImage
import folder_paths
from google import genai
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


def bytify_video(video_path: str) -> bytes:
    """
    Read a video file and return its bytes.

    Args:
        video_path: The path to the video file.

    Returns:
        The video as bytes.
    """
    if not video_path or not os.path.exists(video_path):
        return None
    with open(video_path, "rb") as f:
        return f.read()
