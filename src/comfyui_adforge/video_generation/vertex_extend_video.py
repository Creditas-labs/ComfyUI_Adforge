"""
Video to Video Node for ComfyUI

Extend existing videos using text prompts with Google GenAI SDK.
"""

from typing import Optional

from comfy_api.latest import IO, VideoInput, ui
from google.genai.types import GenerateVideosConfig, GenerateVideosSource, Video

from comfyui_adforge import settings, utils
from comfyui_adforge.documentation import get_documentation, get_tooltip


class VertexVeoExtendVideoNode(IO.ComfyNode):
    """
    Extend an existing video using a text prompt with Google Veo 2 model.
    This node is ideal for extending the duration of a video.
    """

    @classmethod
    def define_schema(cls):
        """Define input parameters for the node."""
        return IO.Schema(
            node_id="VertexVeoExtendVideoNode",
            display_name="Vertex Veo Extend Video",
            category="AdForge/Video Generation",
            description=get_documentation("VertexVeoExtendVideoNode"),
            inputs=[
                IO.String.Input(
                    "prompt",
                    tooltip=get_tooltip("prompt"),
                    force_input=True,
                ),
                IO.Video.Input(
                    "video",
                    tooltip=get_tooltip("video"),
                    optional=True,
                ),
                IO.String.Input(
                    "input_video_path",
                    placeholder="/path/to/video.mp4",
                    tooltip=get_tooltip("input_video_path"),
                    optional=True,
                ),
                # --- Optional ---
                IO.String.Input(
                    "negative_prompt",
                    tooltip=get_tooltip("negative_prompt"),
                    optional=True,
                    force_input=True,
                ),
                IO.String.Input(
                    "output_gcs_uri",
                    default=settings.get_default_gcs_uri("video-to-video"),
                    tooltip=get_tooltip("output_gcs_uri"),
                    optional=True,
                ),
                IO.Combo.Input(
                    "model",
                    options=settings.VeoModel.options(),
                    default=settings.VeoModel.V2_0,
                    tooltip=get_tooltip("model"),
                    optional=True,
                ),
                IO.Combo.Input(
                    "aspect_ratio",
                    options=settings.AspectRatio.options(),
                    default=settings.AspectRatio.default(),
                    tooltip=get_tooltip("aspect_ratio"),
                    optional=True,
                ),
                IO.Combo.Input(
                    "video_mime_type",
                    options=settings.VideoMimeType.options(),
                    default=settings.VideoMimeType.default(),
                    tooltip=get_tooltip("mime_type"),
                    optional=True,
                ),
                IO.Int.Input(
                    "duration_seconds",
                    default=settings.DEFAULT_DURATION_SECONDS,
                    min=2,
                    max=8,
                    step=1,
                    display_mode=IO.NumberDisplay.number,
                    tooltip=get_tooltip("duration_seconds"),
                    optional=True,
                ),
                IO.Combo.Input(
                    "resolution",
                    options=settings.Resolution.options(),
                    default=settings.Resolution.default(),
                    tooltip=get_tooltip("resolution"),
                    optional=True,
                ),
                IO.Int.Input(
                    "fps",
                    default=24,
                    min=1,
                    max=60,
                    step=1,
                    display_mode=IO.NumberDisplay.number,
                    tooltip=get_tooltip("fps"),
                    optional=True,
                ),
                IO.Int.Input(
                    "number_of_videos",
                    default=1,
                    min=1,
                    max=4,
                    step=1,
                    display_mode=IO.NumberDisplay.number,
                    tooltip=get_tooltip("number_of_videos"),
                    optional=True,
                ),
                IO.Boolean.Input(
                    "enhance_prompt",
                    default=True,
                    tooltip=get_tooltip("enhance_prompt"),
                    optional=True,
                ),
                IO.Boolean.Input(
                    "generate_audio",
                    default=False,
                    tooltip=get_tooltip("generate_audio"),
                    optional=True,
                ),
                IO.Combo.Input(
                    "person_generation",
                    options=settings.PersonGeneration.options(),
                    default=settings.PersonGeneration.default(),
                    tooltip=get_tooltip("person_generation"),
                    optional=True,
                ),
                IO.Int.Input(
                    "seed",
                    default=0,
                    min=0,
                    max=2147483647,
                    step=1,
                    display_mode=IO.NumberDisplay.number,
                    control_after_generate=True,
                    tooltip=get_tooltip("seed"),
                    optional=True,
                ),
            ],
            outputs=[
                IO.Video.Output(
                    id="output_videos",
                    display_name="videos",
                    tooltip=get_tooltip("output_videos"),
                    is_output_list=True,
                ),
                IO.String.Output(
                    id="output_video_path_list",
                    display_name="video_path_list",
                    tooltip=get_tooltip("output_video_path_list"),
                    is_output_list=True,
                ),
            ],
            is_output_node=True,
        )

    @classmethod
    def execute(
        cls,
        prompt: str,
        input_video_path: Optional[str],
        negative_prompt: Optional[str],
        output_gcs_uri: Optional[str],
        model: settings.VeoModel,
        aspect_ratio: Optional[settings.AspectRatio],
        video_mime_type: settings.VideoMimeType,
        duration_seconds: int,
        resolution: Optional[settings.Resolution],
        fps: int,
        seed: int,
        number_of_videos: int,
        enhance_prompt: Optional[bool],
        generate_audio: bool,
        person_generation: settings.PersonGeneration,
        video: Optional[VideoInput] = None,
    ) -> IO.NodeOutput:
        """Extend video using a text prompt."""

        client = utils.get_genai_client()

        if not output_gcs_uri:
            output_gcs_uri = settings.get_default_gcs_uri("video-to-video")
        config_params = {
            "aspect_ratio": aspect_ratio,
            "duration_seconds": duration_seconds,
            "resolution": resolution,
            "fps": fps,
            "enhance_prompt": enhance_prompt,
            "generate_audio": generate_audio,
            "number_of_videos": number_of_videos,
            "person_generation": person_generation,
            "compression_quality": "LOSSLESS",
            "output_gcs_uri": output_gcs_uri,
        }
        if negative_prompt:
            config_params["negative_prompt"] = negative_prompt
        if seed >= 0:
            config_params["seed"] = seed

        try:
            # if video
            video_bytes = utils.bytify_video(video or input_video_path)
            if video_bytes:
                if video:
                    video_mime_type = "video/mp4"
                source_video = Video(video_bytes=video_bytes, mime_type=video_mime_type)
            else:
                raise ValueError("Either an input video path or an input video GCS URI must be provided.")

            operation = client.models.generate_videos(
                model=model,
                source=GenerateVideosSource(prompt=prompt, video=source_video),
                config=GenerateVideosConfig(**config_params),
            )

            result = utils.poll_operation(client, operation)

            filename_prefix = "vertex-extend"
            videos, video_paths, previews = utils.process_genai_results(result, filename_prefix)

            return IO.NodeOutput(videos, video_paths, ui=ui.PreviewVideo(previews))

        except Exception as e:
            raise RuntimeError(f"Video generation failed: {str(e)}")
