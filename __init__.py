import os
import torch
import numpy as np
from google.cloud import texttospeech

from .audio_preview import AudioPreview

class Chirp_TTS_Node:

    @classmethod
    def INPUT_TYPES(s):
        VOICE_OPTIONS = [
            "pt-BR-Wavenet-A",
            "en-US-Standard-C",
            "en-US-Studio-O"
        ]

        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "voice_name": (VOICE_OPTIONS, {"default": VOICE_OPTIONS[0]}),
                "credentials_path": ("STRING", {
                    "default": "C:/Users/leticia.rosa_santodi/Documents/service-account-key.json"
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "AUDIO")
    RETURN_NAMES = ("audio_filepath", "filename_str", "audio_preview")
    FUNCTION = "generate_audio"
    CATEGORY = "Audio Generation/Chirp"

    def generate_audio(self, prompt, voice_name, credentials_path):

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=prompt)

        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_name[:5],
            name=voice_name
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        if len(response.audio_content) == 0:
            raise Exception("API retornou áudio vazio.")

        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        existing_files = [
            f for f in os.listdir(output_dir)
            if f.startswith("chirp_output_") and f.endswith(".mp3")
        ]

        numbers = []
        for f in existing_files:
            try:
                num = int(f.replace("chirp_output_", "").replace(".mp3", ""))
                numbers.append(num)
            except:
                pass

        next_number = max(numbers) + 1 if numbers else 1

        output_filename = f"chirp_output_{next_number}.mp3"
        output_filepath = os.path.join(output_dir, output_filename)


        with open(output_filepath, "wb") as out:
            out.write(response.audio_content)

        return (output_filepath, output_filename, response.audio_content)


NODE_CLASS_MAPPINGS = {
    "Chirp_TTS_Node": Chirp_TTS_Node,
    "Audio_Preview": AudioPreview
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Chirp_TTS_Node": "🔊 Chirp TTS (Google Cloud)",
    "Audio_Preview": "🎶 Visualizador de Áudio"
}
