import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(layout="wide")

EMAIL = st.secrets["EMAIL"]
TOKEN = st.secrets["TOKEN"]

DATA_PATH = "inventario.parquet"

# =============================
# Cargar datos desde Alegra
# =============================
def cargar_items_desde_alegra():
    url = "https://api.alegra.com/api/v1/items/"
    data_all = []
    start = 0

    with st.spinner("⏳ Conectando a Alegra..."):
        while True:
            params = {"start": start, "limit": 30}
            r = requests.get(url, auth=(EMAIL, TOKEN), params=params)

            if r.status_code != 200:
                st.error("Error conectando a Alegra")
                st.stop()

            data = r.json()
            if not data:
                break

            data_all.extend(data)
            start += 30

    df = pd.DataFrame(data_all)
    df["unit_price"] = df["price"].apply(
        lambda x: x[0]["price"] if isinstance(x, list) and x else None
    )
    return df

# =============================
# Tabla liviana inventario
# =============================
def crear_tabla_inventario(df):
    rows = []

    for _, row in df.iterrows():
        inv = row.get("inventory")

        categoria = (
            row["itemCategory"]["name"]
            if isinstance(row.get("itemCategory"), dict)
            else None
        )

        if isinstance(inv, dict):
            for wh in inv.get("warehouses", []):
                rows.append({
                    "item_name": row.get("name"),
                    "reference": row.get("reference"),
                    "unit_price": row.get("unit_price"),
                    "warehouse_name": wh.get("name"),
                    "warehouse_available_qty": wh.get("availableQuantity"),
                    "category": categoria,
                })

    return pd.DataFrame(rows)

# =============================
# UI
# =============================
st.title("📦 Inventario Florida")

if st.button("🔄 Actualizar desde Alegra"):
    df_items = cargar_items_desde_alegra()
    df_inventory = crear_tabla_inventario(df_items)
    df_inventory.to_parquet(DATA_PATH, index=False)
    st.success("Inventario actualizado")

if not os.path.exists(DATA_PATH):
    st.warning("No hay datos. Presiona actualizar.")
    st.stop()

df_inventory = pd.read_parquet(DATA_PATH)

florida = df_inventory[df_inventory["warehouse_name"].str.strip() == "Florida"]

st.subheader("Productos disponibles")
st.dataframe(florida, use_container_width=True)

st.success(f"📦 Total artículos: {int(florida['warehouse_available_qty'].sum())}")

buscar = st.text_input("🔍 Buscar producto")

if buscar:
    st.dataframe(
        florida[florida["item_name"].str.contains(buscar, case=False, na=False)],
        use_container_width=True
    )