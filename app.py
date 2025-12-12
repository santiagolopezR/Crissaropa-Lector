import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Inventario Florida", layout="wide")

EMAIL = st.secrets["EMAIL"]
TOKEN = st.secrets["TOKEN"]

# =====================================================
# Función para cargar items desde Alegra (API)
# =====================================================
def cargar_items():
    url = "https://api.alegra.com/api/v1/items/"
    data_all = []
    start = 0

    while True:
        params = {"start": start, "limit": 30}
        response = requests.get(url, auth=(EMAIL, TOKEN), params=params)

        if response.status_code != 200:
            st.error(f"❌ Error: {response.status_code} - {response.text}")
            return None

        data = response.json()

        if not isinstance(data, list) or not data:
            break

        data_all.extend(data)
        start += 30

    df = pd.DataFrame(data_all)

    if df.empty:
        return None

    df["unit_price"] = df["price"].apply(
        lambda x: x[0]["price"] if isinstance(x, list) and len(x) > 0 else None
    )

    return df


# =====================================================
# Procesar inventario
# =====================================================
def cargar_inventario(df_items):
    warehouse_data = []

    for _, row in df_items.iterrows():
        inv = row.get("inventory")
        category_name = None

        if isinstance(row.get("itemCategory"), dict):
            category_name = row["itemCategory"].get("name")

        if isinstance(inv, dict) and "warehouses" in inv:
            for wh in inv["warehouses"]:
                warehouse_data.append(
                    {
                        "item_id": row.get("id"),
                        "item_name": row.get("name"),
                        "reference": row.get("reference"),
                        "unit_price": row.get("unit_price"),
                        "warehouse_name": wh.get("name"),
                        "warehouse_available_qty": wh.get("availableQuantity"),
                        "category": category_name,
                    }
                )

    return pd.DataFrame(warehouse_data)


# =====================================================
# Cargar datos una sola vez (session_state)
# =====================================================
def cargar_datos_completos():
    df_items = cargar_items()
    df_inv = cargar_inventario(df_items)
    return df_items, df_inv


# =====================================================
# BOTÓN PARA ACTUALIZAR LA API
# =====================================================
if st.button("🔄 Actualizar datos desde API"):
    df_items, df_inv = cargar_datos_completos()
    st.session_state["items"] = df_items
    st.session_state["inv"] = df_inv
    st.success("Datos actualizados desde la API")


# =====================================================
# SI NO EXISTEN DATOS EN SESSION, CARGAR UNA VEZ
# =====================================================
if "items" not in st.session_state:
    df_items, df_inv = cargar_datos_completos()
    st.session_state["items"] = df_items
    st.session_state["inv"] = df_inv

df_items = st.session_state["items"]
df_inventory = st.session_state["inv"]

# =====================================================
# MOSTRAR INVENTARIO
# =====================================================
st.title("📦 Inventario Florida Alegra")

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

st.subheader("📊 Inventario por Categoría")
st.dataframe(inventario_por_categoria, use_container_width=True)

# =====================================================
# BUSCADOR LOCAL (NO API)
# =====================================================
st.subheader("🔍 Buscar producto")

buscar = st.text_input("Escribe parte del nombre o referencia:")

if buscar:
    resultados = floridahay[
        floridahay["item_name"].str.contains(buscar, case=False, na=False)
    ]
    st.dataframe(resultados, use_container_width=True)
    st.info(f"🔎 Resultados encontrados: {len(resultados)}")