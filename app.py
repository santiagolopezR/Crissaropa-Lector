import streamlit as st
import cv2
import av
import numpy as np
import base64
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

st.title("📱 Lector de Códigos de Barras (Tiempo Real + Python + ZXing)")

RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

# ZXing embebido (sin pyzxing)
def zx_decode(image_bgr):
    # Convertir a JPG base64 (ZXing lo necesita así)
    _, buffer = cv2.imencode('.jpg', image_bgr)
    jpg_as_text = base64.b64encode(buffer).decode()

    import requests
    url = "https://zxing.org/w/decode"
    files = {"file": ("image.jpg", base64.b64decode(jpg_as_text), "image/jpeg")}
    resp = requests.post(url, files=files)

    text = resp.text
    if "<pre>" in text:
        code = text.split("<pre>")[1].split("</pre>")[0].strip()
        if code != "":
            return code

    return None


def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")

    code = zx_decode(img)

    if code:
        st.session_state["last_code"] = code
        cv2.putText(img, f"Detectado: {code}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 3)

    return av.VideoFrame.from_ndarray(img, format="bgr24")


webrtc_streamer(
    key="barcode-reader",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    video_frame_callback=video_frame_callback
)

if "last_code" in st.session_state:
    st.success(f"📦 Código detectado: {st.session_state['last_code']}")