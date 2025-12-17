import streamlit as st
import requests
import streamlit as st
import requests

API_URL = "http://192.168.1.11:8000/last"

def run():
    st.title("📷 Escáner")

    if st.button("Leer último código"):
        data = requests.get(API_URL).json()
        st.success(f"Código: {data['code']}")
API_URL = "http://192.168.1.11:8000/last"

st.set_page_config(page_title="Escáner", layout="centered")

st.title("📷 Escáner en tiempo real")

if st.button("🔄 Leer último código"):
    try:
        data = requests.get(API_URL, timeout=5).json()
        st.success(f"📦 Código: **{data['code']}**")
        st.caption(f"🕒 {data.get('timestamp','')}")
    except Exception as e:
        st.error("No se pudo conectar al escáner")

st.info("Escanea desde el celular y luego presiona el botón.")
