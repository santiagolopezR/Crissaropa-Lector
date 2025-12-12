import streamlit as st
from PIL import Image
import cv2
import numpy as np
import requests

st.title("📸 Lector de Código de Barras (Básico)")

# Función para leer códigos con ZXing
def leer_codigo(img_bgr):
    _, buffer = cv2.imencode('.jpg', img_bgr)
    resp = requests.post(
        "https://zxing.org/w/decode",
        files={"file": ("imagen.jpg", buffer.tobytes(), "image/jpeg")}
    )
    text = resp.text

    # Extraer contenido del <pre>
    if "<pre>" in text:
        code = text.split("<pre>")[1].split("</pre>")[0].strip()
        if code:
            return code
    return None

# Capturar imagen
camara = st.camera_input("Tomar foto del código")

if camara:
    # Convertir a formato OpenCV
    imagen = Image.open(camara)
    st.image(imagen, caption="Foto capturada")

    img_cv = cv2.cvtColor(np.array(imagen), cv2.COLOR_RGB2BGR)

    # Leer código
    codigo = leer_codigo(img_cv)

    if codigo:
        st.success(f"📦 Código detectado: {codigo}")
    else:
        st.error("❌ No se detectó ningún código")