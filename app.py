import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Inventario Florida", layout="wide")

EMAIL = st.secrets["EMAIL"]
TOKEN = st.secrets["TOKEN"]

# =====================================================
# Función para cargar items desde Alegra
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
            return None, None

        data = response.json()

        if not isinstance(data, list) or not data:
            break

        data_all.extend(data)
        start += 30

    df = pd.DataFrame(data_all)

    if df.empty:
        return None, None

    df["item_id"] = df.get("id")
    df["name"] = df.get("name")
    df["description"] = df.get("description")
    df["reference"] = df.get("reference")
    df["type"] = df.get("type")
    df["itemcategory"] = df.get("itemCategory")

    df["unit_price"] = df["price"].apply(
        lambda x: x[0]["price"] if isinstance(x, list) and len(x) > 0 else None
    )

    return df, df  # df_items no lo necesitas realmente

# =====================================================
# Cargar inventario por bodegas
# =====================================================
def cargar_inventario(df):
    warehouse_data = []

    for idx, row in df.iterrows():
        inv = row["inventory"]

        category_id, category_name = None, None
        if isinstance(row.get("itemCategory"), dict):
            category_id = row["itemCategory"].get("id")
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
# BOTÓN DE ACTUALIZAR
# =====================================================

if st.button("🔄 Actualizar datos"):
    st.cache_data.clear()

# =====================================================
# CACHE: SOLO CARGA API SI ES NECESARIO
# =====================================================
@st.cache_data(ttl=60)
def cargar_data_cache():
    return cargar_items()

df_items, df_raw = cargar_data_cache()

# =====================================================
# MOSTRAR INVENTARIO
# =====================================================
if df_items is None:
    st.warning("No se pudo cargar el inventario.")
else:

    df_inventory = cargar_inventario(df_raw)

    st.title("📦 Inventario Florida Alegra")

    # Filtrar Florida
    florida = df_inventory[df_inventory["warehouse_name"].str.strip() == "Florida"]

    floridahay = florida[
        florida["warehouse_available_qty"].notnull()
    ][["item_name", "warehouse_available_qty", "unit_price", "category"]]

    st.subheader("📋 Productos disponibles en Florida")
    st.dataframe(floridahay, use_container_width=True)

    # Total artículos
    total_articulos = floridahay["warehouse_available_qty"].sum()
    st.success(f"📦 En Florida hay **{int(total_articulos)} artículos**")

    # Por categoría
    inventario_por_categoria = florida.groupby("category", as_index=False)[
        "warehouse_available_qty"
    ].sum()

    st.subheader("📊 Inventario por Categoría (Florida)")
    st.dataframe(inventario_por_categoria, use_container_width=True)

    # =====================================================
    # BUSCADOR LOCAL (NO API)
    # =====================================================
    st.subheader("🔍 Buscar producto en Florida")

    buscar = st.text_input("Escribe parte del nombre o referencia:")

    if buscar:
        resultados = floridahay[
            floridahay["item_name"].str.contains(buscar, case=False, na=False)
        ]
        st.dataframe(resultados, use_container_width=True)
        st.info(f"🔎 Resultados encontrados: {len(resultados)}")