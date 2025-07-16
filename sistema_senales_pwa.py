import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# =====================================
# 📊 Funciones para detectar patrones
# =====================================

def detectar_martillo(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    return (mecha_inferior > 2 * cuerpo) and (mecha_superior < cuerpo)

def detectar_estrella_fugaz(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    return (mecha_superior > 2 * cuerpo) and (mecha_inferior < cuerpo)

def detectar_envolvente(df):
    return ((df['Close'].shift(1) < df['Open'].shift(1)) &
            (df['Open'] < df['Close']) &
            (df['Close'] > df['Open'].shift(1)) &
            (df['Open'] < df['Close'].shift(1)))

# =====================================
# 🧠 Análisis del DataFrame
# =====================================

def analizar_df(df):
    señales = []

    df['Envolvente'] = detectar_envolvente(df)
    for i in df[df['Envolvente']].index:
        señales.append((i, 'Envolvente Alcista'))

    for i, row in df.iterrows():
        if detectar_martillo(row):
            señales.append((i, 'Martillo'))
        elif detectar_estrella_fugaz(row):
            señales.append((i, 'Estrella Fugaz'))

    return pd.DataFrame(señales, columns=['Fecha', 'Patrón'])

# =====================================
# 🎛️ Interfaz de Streamlit
# =====================================

st.set_page_config(page_title="Sistema de Velas", layout="centered")
st.title("📈 Sistema de Señales por Velas Japonesas")

# Entrada de usuario (ticker ficticio)
ticker = st.text_input("🔍 Escribe un ticker (simulado):", value="AMD")
dias = st.slider("Cantidad de días de datos simulados:", 10, 100, 30)

# Simulación de datos OHLC
np.random.seed(42)
base = 100
precio = base + np.random.randn(dias).cumsum()
high = precio + np.random.rand(dias)*2
low = precio - np.random.rand(dias)*2
open_ = precio + (np.random.rand(dias)-0.5)
close = precio + (np.random.rand(dias)-0.5)
fechas = pd.date_range(end=datetime.today(), periods=dias)

df = pd.DataFrame({
    'Date': fechas,
    'Open': open_,
    'High': high,
    'Low': low,
    'Close': close
}).set_index('Date')

# Mostrar datos
st.subheader("📋 Datos recientes")
st.dataframe(df)

# Detectar patrones
try:
    resultados = analizar_df(df)

    st.subheader("💡 Señales detectadas")
    if resultados.empty:
        st.info("No se detectaron patrones.")
    else:
        st.dataframe(resultados)
except Exception as e:
    st.error(f"❌ Error durante el análisis: {e}")