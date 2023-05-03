import av
import cv2
import glob
import logging
import pandas as pd
import numpy as np
import streamlit as st
from streamlit_ace import st_ace
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from pychuck import _Chuck

st.set_page_config(layout="wide")


# load data
@st.cache_data
def load_data():
    example_names = ['SinOsc', 'Gain', 'ADSR', 'JCRev', 'Impulse', 'BiQuad', 'Sndbuf', 'Mandolin']
    examples = {}
    for name in example_names:
        examples[name] = open(f"examples/{name}.py").read()
    return example_names, examples


example_names, examples = load_data()

# init chuck
if 'chuck' not in st.session_state:
    st_webrtc_logger = logging.getLogger("streamlit_webrtc")
    st_webrtc_logger.setLevel(logging.WARNING)
    aioice_logger = logging.getLogger("aioice")
    aioice_logger.setLevel(logging.WARNING)
    st.session_state.chuck = _Chuck(sample_rate=48000, buffer_size=960, in_channels=2)
    st.session_state.chuck._canvas = np.zeros((480, 640, 3), dtype=np.uint8)

chuck = st.session_state.chuck

if 'shreds' not in st.session_state:
    st.session_state.shreds = pd.DataFrame({"name": ["empty"], "time": ["0:00"], "remove": [False]})


def process_audio(frame: av.AudioFrame) -> av.AudioFrame:
    indata = frame.to_ndarray().astype(np.float32).reshape(-1, 2) / (2 ** 15 - 1)
    outdata = chuck._forward(indata)
    new_samples = (outdata * (2 ** 15 - 1)).astype(np.int16).reshape(1, -1)
    new_frame = av.AudioFrame.from_ndarray(new_samples, layout=frame.layout.name)
    new_frame.sample_rate = frame.sample_rate
    return new_frame


def generate_image() -> av.VideoFrame:
    return av.VideoFrame.from_ndarray(chuck._canvas, format="bgr24")


# title
st.sidebar.write(
    """
    WebChucK &nbsp; [![GitHub][github_badge]][github_link] [![PyPI][pypi_badge]][pypi_link]
    =====================
    [github_badge]: https://badgen.net/badge/icon/GitHub?icon=github&color=black&label
    [github_link]: https://github.com/ccrma/chuck
    [pypi_badge]: https://badgen.net/badge/doc/1.4.2.0/black?
    [pypi_link]: http://18.144.88.181/CKDoc.html
    """
)

with st.sidebar:
    # webchuck
    webrtc_streamer(
        key="webchuck",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": False, "audio": True},
        audio_frame_callback=process_audio,
        async_processing=True,
    )

    add_shred = st.button("ADD SHRED", type="primary")
    replace_shred = st.button("REPLACE SHRED", type="secondary")
    remove_last_shred = st.button("REMOVE LAST SHRED", type="secondary")

    st.experimental_data_editor(st.session_state.shreds, use_container_width=True, key="shreds")

    use_vim = st.checkbox("Enable Vim", value=False)

maincols = st.columns(2)

with maincols[0]:
    example = st.selectbox("Example", example_names, key="example", index=0)
    example_code = examples[example]
    code = st_ace(
        value=example_code,
        language="python",
        theme="gruvbox",
        keybinding="vim" if use_vim else "vscode",
        min_lines=25,
        key=f"editor{example}"
    )
    st.text_area("Console", value="", height=150, key="console", disabled=True)

if add_shred:
    chuck._add_shred(code)
elif replace_shred:
    chuck._remove_last_shred()
    chuck._add_shred(code)
elif remove_last_shred:
    chuck._remove_last_shred()
