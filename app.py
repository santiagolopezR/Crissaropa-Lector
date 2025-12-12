import streamlit as st
import av
import cv2
from pyzbar.pyzbar import decode
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

st.title("📱 Lector de Códigos de Barras en Tiempo Real (OpenCV + Streamlit)")

RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})


def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")

    # Procesar código de barras con pyzbar
    barcodes = decode(img)
    for barcode in barcodes:
        x, y, w, h = barcode.rect
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type

        cv2.putText(img, f"{barcode_data} ({barcode_type})",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 0, 0),
                    2)

        st.session_state["last_code"] = barcode_data

    return av.VideoFrame.from_ndarray(img, format="bgr24")


webrtc_streamer(
    key="barcode-reader",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    video_frame_callback=video_frame_callback,
)

# Mostrar el código detectado
if "last_code" in st.session_state:
    st.success(f"📦 Código detectado: **{st.session_state['last_code']}**")