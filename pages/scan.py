import requests
import streamlit as st

API_URL = "http://192.168.1.11:8000/last"

st.subheader("📲 Último código escaneado")

try:
    r = requests.get(API_URL, timeout=2)
    data = r.json()
    codigo = data.get("code")

    if codigo:
        st.success(f"📦 Código escaneado: {codigo}")

        resultado = floridahay[
            floridahay["reference"].astype(str).str.contains(
                codigo, case=False, na=False
            )
        ]

        st.dataframe(resultado, use_container_width=True)

    else:
        st.info("Esperando escaneo...")

except Exception as e:
    st.error("No se puede conectar a la API de escaneo")

