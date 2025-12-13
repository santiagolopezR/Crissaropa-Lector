import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(page_title="Inventario Florida", layout="wide")

EMAIL = st.secrets["EMAIL"]
TOKEN = st.secrets["TOKEN"]

DATA_PATH = "inventario.parquet"

# =====================================================
# 1. Cargar items desde Alegra (SOLO cuando se actualiza)
# =====================================================
def cargar_items_desde_alegra():
    url = "https://api.alegra.com/api/v1/items/"
    data_all = []
    start = 0

    with st.spinner("⏳ Conectando a Alegra..."):
        while True:
            params = {"start": start, "limit": 30}
            response = requests.get(url, auth=(EMAIL, TOKEN), params=params, timeout=30)

            if response.status_code != 200:
                st.error(f"❌ Error Alegra: {response.status_code}")
                st.stop()

            data = response.json()
            if not isinstance(data, list) or not data:
                break

            data_all.extend(data)
            start += 30

    df = pd.DataFrame(data_all)

    df["unit_price"] = df["price"].apply(
        lambda x: x[0]["price"] if isinstance(x, list) and len(x) > 0 else None
    )

    return df


# =====================================================
# 2. Crear SOLO la tabla final de inventario (liviana)
# =====================================================
def crear_tabla_inventario(df):
    warehouse_data = []

    for _, row in df.iterrows():
        inv = row.get("inventory")

        category = None
        if isinstance(row.get("itemCategory"), dict):
            category = row["itemCategory"].get("name")

        if isinstance(inv, dict):
            for wh in inv.get("warehouses", []):
                warehouse_data.append(
                    {
                        "item_name": row.get("name"),
                        "reference": row.get("reference"),
                        "unit_price": row.get("unit_price"),
                        "warehouse_name": wh.get("name"),
                        "warehouse_available_qty": wh.get("availableQuantity"),
                        "category": category,
                    }
                )

    return pd.DataFrame(warehouse_data)
        
    

# =====================================================
# 3. BOTÓN: ACTUALIZAR DESDE ALEGRA
# =====================================================
st.title("📦 Inventario Florida Alegra")

if st.button("🔄 Actualizar datos desde Alegra"):
    df_items = cargar_items_desde_alegra()
    df_inventory = crear_tabla_inventario(df_items)

    df_inventory.to_parquet(DATA_PATH, index=False)
    st.success("✅ Inventario actualizado correctamente")


# =====================================================
# 4. CARGA NORMAL (ARCHIVO LOCAL)
# =====================================================
if not os.path.exists(DATA_PATH):
    st.warning("No hay datos locales. Presiona **Actualizar datos desde Alegra**.")
    st.stop()

df_inventory = pd.read_parquet(DATA_PATH)


# =====================================================
# 5. FILTRAR SOLO BODEGA FLORIDA
# =====================================================
florida = df_inventory[df_inventory["warehouse_name"].str.strip() == "Florida"]

floridahay = florida[
    florida["warehouse_available_qty"].notnull()
][["item_name", "warehouse_available_qty", "unit_price", "category"]]

st.subheader("📋 Productos disponibles en Florida")
st.dataframe(floridahay, use_container_width=True)

total_articulos = floridahay["warehouse_available_qty"].sum()
st.success(f"📦 En Florida hay **{int(total_articulos)} artículos**")

inventario_por_categoria = florida.groupby("category", as_index=False)[
    "warehouse_available_qty"
].sum()

st.subheader("📊 Inventario por Categoría (Florida)")
st.dataframe(inventario_por_categoria, use_container_width=True)


# =====================================================
# 6. BUSCADOR LOCAL (INSTANTÁNEO)
# =====================================================
st.subheader("🔍 Buscar producto en Florida")

buscar = st.text_input("Escribe parte del nombre o referencia:")

if buscar:
    resultados = floridahay[
        floridahay["item_name"].str.contains(buscar, case=False, na=False)
    ]
    st.dataframe(resultados, use_container_width=True)
    st.info(f"🔎 Resultados encontrados: {len(resultados)}")