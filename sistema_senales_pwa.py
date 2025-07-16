
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema de Señales", layout="wide")

st.title("📊 Sistema de Señales por Velas")
st.markdown("Este sistema muestra recomendaciones de compra y venta basadas en patrones de velas japonesas.")

# Simulación de datos (puede ser reemplazado por una llamada a tu backend o CSV real)
data = [
    {"Hora": "08:30", "Apertura": 150.12, "Cierre": 151.10, "Máximo": 151.40, "Mínimo": 149.90, "Volumen": 3200, "Alerta Técnica": "🟢 Compra sugerida"},
    {"Hora": "08:45", "Apertura": 151.10, "Cierre": 150.60, "Máximo": 151.60, "Mínimo": 150.30, "Volumen": 2800, "Alerta Técnica": "🔴 Venta sugerida"},
    {"Hora": "09:00", "Apertura": 150.60, "Cierre": 150.65, "Máximo": 151.20, "Mínimo": 150.10, "Volumen": 2400, "Alerta Técnica": "⚠️ Zona de congestión"},
]

df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)

st.markdown("---")
st.info("🔔 El sistema se actualizará cada 15 minutos con nuevas señales.")
