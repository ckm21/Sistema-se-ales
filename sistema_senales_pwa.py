import streamlit as st
import pandas as pd

# Simulación de datos (puedes reemplazar esto con datos reales luego)
data = {
    'Hora': ['08:30', '08:45', '09:00', '09:15'],
    'Apertura': [150.12, 151.1, 150.6, 150.4],
    'Cierre':   [151.1, 150.6, 150.65, 150.8],
    'Máximo':   [151.4, 151.6, 151.2, 151.0],
    'Mínimo':   [149.9, 150.3, 150.1, 150.3]
}
df = pd.DataFrame(data)

# ------------------- Funciones de detección de patrones -------------------

def detectar_martillo(row):
    cuerpo = abs(row['Cierre'] - row['Apertura'])
    mecha_inferior = min(row['Apertura'], row['Cierre']) - row['Mínimo']
    mecha_superior = row['Máximo'] - max(row['Apertura'], row['Cierre'])
    return mecha_inferior > cuerpo * 2 and mecha_superior < cuerpo

def detectar_estrella_fugaz(row):
    cuerpo = abs(row['Cierre'] - row['Apertura'])
    mecha_superior = row['Máximo'] - max(row['Apertura'], row['Cierre'])
    mecha_inferior = min(row['Apertura'], row['Cierre']) - row['Mínimo']
    return mecha_superior > cuerpo * 2 and mecha_inferior < cuerpo

def detectar_envolvente_bajista(df, i):
    if i == 0:
        return False
    prev = df.iloc[i - 1]
    curr = df.iloc[i]
    return (
        prev['Cierre'] > prev['Apertura'] and
        curr['Cierre'] < curr['Apertura'] and
        curr['Apertura'] > prev['Cierre'] and
        curr['Cierre'] < prev['Apertura']
    )

# ------------------- Generar señales -------------------

senales = []
for i, row in df.iterrows():
    s = []
    if detectar_martillo(row): s.append("🟢 Martillo")
    if detectar_estrella_fugaz(row): s.append("🔻 Estrella fugaz")
    if detectar_envolvente_bajista(df, i): s.append("⚠️ Envolvente bajista")
    senales.append(", ".join(s) if s else "—")

df['Señal'] = senales

# ------------------- Interfaz en Streamlit -------------------

st.set_page_config(page_title="Sistema de Señales", layout="centered")
st.title("📊 Sistema de Señales por Velas")
st.write("Este sistema muestra recomendaciones de compra y venta basadas en patrones de velas japonesas.")

st.dataframe(df, use_container_width=True)

st.info("🔔 El sistema se actualizará cada 15 minutos con nuevas señales (modo simulado).")
