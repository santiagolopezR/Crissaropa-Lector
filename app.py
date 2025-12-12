import streamlit as st
import cv2
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from pyzxing import BarCodeReader

st.title("📱 Lector de Códigos de Barras (Tiempo real + Python)")

reader = BarCodeReader()

RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")

    # Guardar frame temporalmente
    cv2.imwrite("frame.jpg", img)

    # Leer códigos con ZXing
    result = reader.decode("frame.jpg")

    if result:
        code = result[0]["raw"]
        st.session_state["last_code"] = code

        # Dibujar un mensaje en pantalla
        cv2.putText(img, f"Detectado: {code}", (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

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