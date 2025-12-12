import streamlit as st
import cv2
import av
import numpy as np
import base64
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

st.title("📱 Lector de Códigos de Barras")
st.camara_input()