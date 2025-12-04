import os

class AudioPreview:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio_filepath": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "show_audio"
    CATEGORY = "Audio Generation/Chirp"
    OUTPUT_NODE = True

    def show_audio(self, audio_filepath):

        relative_path = audio_filepath.replace("\\", "/")
        if relative_path.startswith("output/"):
            relative_path = relative_path[len("output/"):]

        html = f"""
        <div style="
            padding: 10px; 
            background: #1e1e1e; 
            border-radius: 8px; 
            color: white;
            font-family: Arial;
        ">
            <p style='margin: 0 0 8px 0; font-size: 14px;'>
                <b>Waveform Preview</b>
            </p>

            <div id="waveform" style="
                width: 100%;
                height: 100px;
                border-radius: 4px;
                overflow: hidden;
                margin-bottom: 10px;
            "></div>

            <button id="playBtn" style="
                background: #4c8bf5;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
                color: white;
                font-weight: bold;
            ">
                ▶ Play
            </button>

            <script src="https://unpkg.com/wavesurfer.js"></script>

            <script>
                const wavesurfer = WaveSurfer.create({{
                    container: '#waveform',
                    waveColor: '#8ec7ff',
                    progressColor: '#4c8bf5',
                    height: 100,
                    barWidth: 2,
                    barGap: 1,
                    responsive: true,
                }});

                wavesurfer.load("view_output/{relative_path}");

                const playBtn = document.getElementById("playBtn");

                playBtn.onclick = () => {{
                    wavesurfer.playPause();
                    playBtn.innerText = wavesurfer.isPlaying() ? "⏸ Pause" : "▶ Play";
                }};
            </script>
        </div>
        """

        return {"ui": {"html": html}}
