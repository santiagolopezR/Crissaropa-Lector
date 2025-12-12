import streamlit as st
from PIL import Image
import numpy as np
import zbarlight

st.title("📸 Lector de Código de Barras (Funcional en Cloud)")

camara = st.camera_input("Tomar foto del código")

if camara:
    imagen = Image.open(camara)
    st.image(imagen, caption="Foto capturada")

    # Convertir a blanco y negro para ZBarlight
    img_gray = imagen.convert('L')
    img_np = np.array(img_gray)

    # ZBarlight requiere un array 2D puro
    codes = zbarlight.scan_codes(['ean13', 'code128', 'code39', 'ean8'], img_np)

    if codes:
        st.success(f"📦 Código detectado: {codes[0].decode()}")
    else:
        st.error("❌ No se detectó ningún código")