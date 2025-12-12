import streamlit as st
import pandas as pd
from allegra_api import get_items, get_inventory_detail

st.set_page_config(page_title="Inventario Florida", layout="wide")

st.title("📦 Inventario Florida - Tiempo Real")

EMAIL = st.secrets["EMAIL"]
TOKEN = st.secrets["TOKEN"]

# botón actualizar
if st.button("🔄 Actualizar Inventario"):
    st.cache_data.clear()

@st.cache_data(ttl=60)  # refresca cada 60 segundos
def load_data():
    df_items, df_raw = get_items(EMAIL, TOKEN)
    df_inventory = get_inventory_detail(df_raw)
    return df_items, df_inventory

with st.spinner("Cargando datos de Allegra..."):
    df_items, df_inventory = load_data()

st.subheader("📌 Inventario resumido por producto")
st.dataframe(df_items, use_container_width=True)

st.subheader("🏷️ Inventario detallado por bodega")
st.dataframe(df_inventory, use_container_width=True)

# Filtro por búsqueda
st.subheader("🔍 Buscar producto")
search = st.text_input("Escriba referencia o nombre")

if search:
    filtrado = df_inventory[df_inventory["item_name"].str.contains(search, case=False)]
    st.dataframe(filtrado, use_container_width=True)