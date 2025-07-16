import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# =============================
# 🔍 Funciones para detectar patrones
# =============================

def detectar_martillo(row):
    if row.isnull().any():
        return False
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    return mecha_inferior > 2 * cuerpo and mecha_superior < cuerpo

def detectar_envolvente(row, anterior):
    if row.isnull().any() or anterior.isnull().any():
        return False
    return row['Open'] < row['Close'] and \
           anterior['Open'] > anterior['Close'] and \
           row['Open'] < anterior['Close'] and \
           row['Close'] > anterior['Open']

def detectar_estrella_fugaz(row):
    if row.isnull().any():
        return False
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    return mecha_superior > 2 * cuerpo and mecha_inferior < cuerpo

# =============================
# 🧠 Análisis de señales
# =============================

def analizar_senales(df):
    senales = []
    for i in range(1, len(df)):
        row = df.iloc[i]
        anterior = df.iloc[i - 1]
        if detectar_martillo(row):
            senales.append((df.index[i], "📈 Martillo"))
        elif detectar_envolvente(row, anterior):
            senales.append((df.index[i], "🔁 Envolvente Alcista"))
        elif detectar_estrella_fugaz(row):
            senales.append((df.index[i], "📉 Estrella Fugaz"))
    return senales

# =============================
# 🚀 INTERFAZ STREAMLIT
# =============================

st.set_page_config(page_title="📊 Sistema de Señales por Velas", layout="centered")
st.title("📊 Sistema de Señales por Velas Japonesas")
st.markdown("Este sistema detecta patrones clásicos de velas para generar señales de compra o venta.")

ticker = st.text_input("🔎 Escribe el ticker (ej. AMD, AAPL, MSFT)", "AMD")

if ticker:
    try:
        fin = datetime.today()
        inicio = fin - timedelta(days=3)
        df = yf.download(ticker, start=inicio, end=fin, interval="15m")

        if df.empty:
            st.warning("No se pudo obtener información del ticker.")
        else:
            df = df[['Open', 'High', 'Low', 'Close']]  # Limpiar columnas
            senales = analizar_senales(df)

            st.subheader(f"📅 Datos recientes de {ticker.upper()}")
            st.dataframe(df.tail(5))

            st.subheader("📍 Señales detectadas")
            if senales:
                for fecha, señal in senales[-5:]:
                    st.write(f"{fecha} - {señal}")
            else:
                st.info("No se detectaron señales en los últimos datos.")

            st.caption("⏱ Actualización cada 15 minutos.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
