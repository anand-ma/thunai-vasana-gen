# To install and run in local
# clear && python3.11 -m pip install -qU -r requirements.txt && streamlit run thunai_vasana_gen.py

# To run in local
# clear && streamlit run thunai_vasana_gen.py

# to use virtual env for python run below command
# source "./.venv/bin/activate"

import streamlit as st
from PIL import Image
from tempfile import NamedTemporaryFile
import whisper
import os

# Main app

# Hide footer and main menu
hide_default_format = """
    <style>
    footer, header {
        visibility: hidden;
        position: relative;
    }
    </style>
"""
# Loading Image using PIL
im = Image.open('./content/App_Icon.png')
# Adding Image to web app
st.set_page_config(page_title="Subtitle Generator", page_icon=im, menu_items=None)

st.markdown(hide_default_format, unsafe_allow_html=True)

st.title("🗞 Subtitle Generator")
st.write("Generate a .srt file from an Audio file (mp3) using AI")

st.subheader("Upload Audio File extract from Video / Audio / Podcast file", divider="rainbow")

if "srt_content" not in st.session_state:
    st.session_state.srt_content = ''
if "filename" not in st.session_state:
    st.session_state.filename = ''
if "audio_filename" not in st.session_state:
    st.session_state.audio_filename = ''

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

# Generate SRT file
def generate_srt(transcription):
    srt_content = ""

    for i, segment in enumerate(transcription["segments"], start=1):
        start_time = format_timestamp(segment["start"])
        end_time = format_timestamp(segment["end"])
        text = segment["text"]
        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"

    return srt_content

# displays srt file in code block and provides download button
def display_srt(srt_content, filename):
    st.download_button(
        label="Download as .srt file",
        data=srt_content,
        file_name=filename,
        mime="application/x-subrip",
        icon=":material/download:"
    )
    st.write(filename)
    st.code(srt_content, language="toml", height=10*50) #toml is closest match to highlight syntax


audio_file = st.file_uploader(
    "Upload an audio file",
    type=["mp3"],
    label_visibility="hidden"
)

# Show a Audio Player to play the file
if audio_file:
    st.audio(audio_file)

if audio_file and st.session_state.audio_filename != audio_file.name: # if new file uploaded
    st.session_state.audio_filename = audio_file.name
    st.session_state.srt_content = None
    st.session_state.filename = None

if audio_file and not st.session_state.srt_content:
    with st.spinner("Generating your Subtitle...", show_time=True):
        with NamedTemporaryFile(suffix="mp3") as temp:
            temp.write(audio_file.getvalue())
            temp.seek(0)

            # Load the Whisper model
            model = whisper.load_model("tiny.en")

            # Transcribe the audio file
            result = model.transcribe(temp.name)

            # Get file name with .srt from .mp3
            filename = f"{os.path.splitext(audio_file.name)[0]}.srt"
            
            # Save SRT file
            srt_content = generate_srt(result)
            st.session_state.srt_content = srt_content
            st.session_state.filename = filename


if st.session_state.srt_content:
    display_srt(st.session_state.srt_content, st.session_state.filename)
    print("SRT file generated successfully!")
