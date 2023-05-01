import av
import cv2
import numpy as np
import streamlit as st
from streamlit_ace import st_ace
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from pychuck.core import _Chuck

st.set_page_config(layout="wide")

if 'chuck' not in st.session_state:
    st.session_state.chuck = _Chuck(sample_rate=48000, buffer_size=960, in_channels=2)
    st.session_state.chuck._canvas = np.zeros((480, 640, 3), dtype=np.uint8)

chuck = st.session_state.chuck


def process_audio(frame: av.AudioFrame) -> av.AudioFrame:
    indata = frame.to_ndarray().astype(np.float32).reshape(-1, 2) / (2 ** 15 - 1)
    outdata = chuck._forward(indata)
    new_samples = (outdata * (2 ** 15 - 1)).astype(np.int16).reshape(1, -1)
    new_frame = av.AudioFrame.from_ndarray(new_samples, layout=frame.layout.name)
    new_frame.sample_rate = frame.sample_rate
    return new_frame


def generate_image(frame: av.VideoFrame) -> av.VideoFrame:
    return av.VideoFrame.from_ndarray(chuck._canvas, format="bgr24")


st.write(
    """
    WebChucK &nbsp; [![GitHub][github_badge]][github_link] [![PyPI][pypi_badge]][pypi_link]
    =====================
    [github_badge]: https://badgen.net/badge/icon/GitHub?icon=github&color=black&label
    [github_link]: https://github.com/ccrma/chuck
    [pypi_badge]: https://badgen.net/badge/doc/1.4.2.0/black?
    [pypi_link]: http://18.144.88.181/CKDoc.html
    """
)

cols = st.columns([1, 2, 1])

with cols[0]:
    webrtc_streamer(
        key="audio-filter",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        audio_frame_callback=process_audio,
        video_frame_callback=generate_image,
        async_processing=True,
    )

with cols[1]:
    content = st_ace(language="python", theme="gruvbox", auto_update=True, height=600,
                     value="""from pychuck import *
import cv2

s = SinOsc(freq=440, gain=0.5)
s >= dac

radius, color, thickness = 15, (255, 255, 255), -1
while True:
    x = int(now) // 100 % 640
    y = int(s.last * 240 + 240)
    canvas.fill(0)
    cv2.circle(canvas, (x, y), radius, color, thickness)
    now += 1000 * samp
 """)

    subcols = st.columns(6)
    with subcols[0]:
        if st.button("ADD SHRED", type="primary"):
            chuck._add_shred(content)
    with subcols[1]:
        if st.button("REMOVE", type="secondary"):
            chuck._remove_last_shred()
