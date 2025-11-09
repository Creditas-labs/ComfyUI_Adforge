"""
Documentation infrastructure for AdForge nodes.
"""


def format_dict_as_text(dictionary, depth=0):
    """Format a dictionary as a text string."""
    text = ""
    for key, value in dictionary.items():
        indent = "  " * depth
        if isinstance(value, dict):
            text += f"{indent}{key}:\n{format_dict_as_text(value, depth + 1)}"
        elif isinstance(value, list):
            text += f"{indent}{key}:\n" + "\n".join(f"{indent}  - {item}" for item in value) + "\n"
        else:
            text += f"{indent}{key}: {value}\n"
    return text


def create_documentation(title, short_description, sections):
    """
    Create formatted documentation for a node.

    Args:
        title: Node title
        short_description: Brief description
        sections: Dict of inputs and outputs documentation sections.

    Returns:
        Formatted documentation string
    """
    text = f"{title}\n{short_description}\n\n"
    text += format_dict_as_text(sections)
    return text


COMMON_IO_TOOLTIPS = {
    "prompt": "The text prompt used to guide video generation.",
    "negative_prompt": (
        "Optional. A text string that describes anything you want to discourage " "the model from generating."
    ),
    "aspect_ratio": "Optional. Specifies the aspect ratio of generated videos.",
    "compression_quality": "Optional. Specifies the compression quality of the generated videos.",
    "duration_seconds": "Required. The length in seconds of video files that you want to generate.",
    "enhance_prompt": "Optional. Use Gemini to enhance your prompts.",
    "generate_audio": "Generate audio for the video.",
    "person_generation": (
        "Optional. The safety setting that controls whether people or face " "generation is allowed."
    ),
    "resolution": "Optional. Veo 3 models only. The resolution of the generated video.",
    "sample_count": "Optional. The number of output videos requested",
    "seed": (
        "Optional. A number to request to make generated videos deterministic. Adding a seed "
        "number with your request without changing other parameters will cause the model to "
        "produce the same videos."
    ),
    "output_gcs_uri_list": ("A list of GCS URIs of the generated videos " "(when output_format=gcs_uri)."),
    "output_video_path_list": ("A list of local paths to the generated videos " "(when output_format=local_file)"),
    "output_format": (
        "Some videos are too large to be returned directly. Try reducing compression quality to optimized first. "
        "Choose whether to get "
        "a GCS URI or save locally, when you choose one the other output will be None."
    ),
    "output_gcs_uri": (
        "GCS URI where the generated videos will be stored, in the format " "'gs://BUCKET_NAME/SUBDIRECTORY'."
    ),
    "model": "The Veo model to use for video generation.",
    "fps": "Optional. Frames per second for the generated video.",
    "number_of_videos": "Optional. Number of video variations to generate.",
    # "resizeMode": (
    #     "Optional. Veo 3 models only, used with image for image-to-video. The resize "
    #     "mode that the model uses to resize the video. Accepted values are "pad" "
    #     "(default) or "crop"."
    # ),
}

TOOLTIPS = {
    **COMMON_IO_TOOLTIPS,
    "input_image": "Input image to animate (IMAGE type).",
    "input_image_gcs_uri": ("GCS URI of the input image in the format 'gs://BUCKET_NAME/SUBDIRECTORY.'."),
    "mask": "The mask to use for generating videos.",
    "reference_images": (
        "The images to use as the references to generate the videos. If this "
        "field is provided, the text prompt field must also be provided. The image, "
        "video, or last_frame field are not supported. Each image must be associated "
        "with a type. Veo 2 supports up to 3 asset images *or* 1 style image."
    ),
    "last_frame": (
        "Image to use as the last frame of generated videos. Only supported for image " "to video use cases."
    ),
    "image_mime_type": "Mime type of the input image, e.g., 'image/png' or 'image/jpeg'.",
    "first_frame": (
        "Image to use as the first frame of generated videos. Only supported for image " "to video use cases."
    ),
}

# Documentation for all AdForge nodes
DOCUMENTATION = {
    "VertexVeoImageToVideoNode": create_documentation(
        "Image to Video",
        "Animate static images with motion prompts using Google's Veo",
        {
            "Inputs": {
                "TBA": "TBA",
            },
            "Outputs": {
                "TBA": "TBA",
            },
            "Configuration": {
                "TBA": "TBA",
            },
        },
    ),
}


def get_tooltip(io: str):
    """Get the tooltip"""
    return TOOLTIPS.get(io, "No documentation available")


def get_documentation(node_class_name):
    """Get documentation for a node class."""
    return DOCUMENTATION.get(node_class_name, "No documentation available")
