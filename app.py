import streamlit as st
import cv2
import av
import numpy as np
import base64
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

st.title("📱 Lector de Códigos de Barras")
camara=st.camera_input("foto")
if camara:
    imagen= Imagen.open(camara)
    st.image(camara)
    img_cv= cv2.cvtColor(imagen,cv2.COLOR_RGB2BGR)
    
    

