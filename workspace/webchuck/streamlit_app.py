import av
import cv2
import numpy as np
import streamlit as st
from streamlit_ace import st_ace
from streamlit_webrtc import WebRtcMode, webrtc_streamer

import pychuck
from pychuck.core import _Chuck

st.set_page_config(layout="wide")


@st.cache_resource
def init():
    pychuck.canvas = np.zeros((480, 640, 3), dtype=np.uint8)
    return _Chuck(sample_rate=48000, buffer_size=960, in_channels=2)


chuck = init()


def process_audio(frame: av.AudioFrame) -> av.AudioFrame:
    indata = frame.to_ndarray().astype(np.float32).reshape(-1, 2) / (2 ** 15 - 1)
    outdata = chuck._forward(indata)
    new_samples = (outdata * (2 ** 15 - 1)).astype(np.int16).reshape(1, -1)
    new_frame = av.AudioFrame.from_ndarray(new_samples, layout=frame.layout.name)
    new_frame.sample_rate = frame.sample_rate
    return new_frame


def generate_image(frame: av.VideoFrame) -> av.VideoFrame:
    return av.VideoFrame.from_ndarray(pychuck.canvas, format="bgr24")


st.title("WebChucK")

cols = st.columns(3)

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

s = SinOsc()
s >= dac

while True:
    canvas.fill(0)
    cv2.circle(canvas, (int(s.last * 200 + 320), 240), 30, (255, 255, 255), -1)
    now += 1600 * samp
 """)

    subcols = st.columns(6)
    with subcols[0]:
        if st.button("ADD SHRED", type="primary"):
            chuck._add_shred(content)
    with subcols[1]:
        if st.button("REMOVE", type="secondary"):
            chuck._remove_last_shred()
