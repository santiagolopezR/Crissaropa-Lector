import streamlit as st
import requests

API_URL = "http://192.168.1.11:8000/last"

st.set_page_config(page_title="Escánerssss", layout="centered")

st.title("📷 Escáner en tiempo real")

if st.button("🔄 Leer último código"):
    try:
        data = requests.get(API_URL, timeout=5).json()
        st.success(f"📦 Código: **{data['code']}**")
        st.caption(f"🕒 {data.get('timestamp','')}")
    except Exception as e:
        st.error("No se pudo conectar al escáner")

st.info("Escanea desde el celular y luego presiona el botón.")
