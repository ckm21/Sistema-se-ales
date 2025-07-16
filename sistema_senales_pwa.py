import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# ========================
# Funciones de patrones
# ========================

def detectar_martillo(row):
    if row.isnull().any():
        return False
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    return mecha_inferior > 2 * cuerpo and mecha_superior < cuerpo

def detectar_estrella_fugaz(row):
    if row.isnull().any():
        return False
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    return mecha_superior > 2 * cuerpo and mecha_inferior < cuerpo

def detectar_envolvente(row, anterior):
    if row.isnull().any() or anterior.isnull().any():
        return False
    return (
        row['Open'] < row['Close'] and
        anterior['Open'] > anterior['Close'] and
        row['Open'] < anterior['Close'] and
        row['Close'] > anterior['Open']
    )

# ========================
# Interfaz Streamlit
# ========================

st.title("📊 Sistema de Señales por Velas Japonesas")
st.write("Este sistema detecta patrones clásicos de velas para generar señales de compra o venta.")

ticker = st.text_input("🔍 Escribe el ticker (ej. AMD, AAPL, MSFT)", "AMD")

if ticker:
    try:
        # Descarga los últimos 15 días por hora
        datos = yf.download(ticker, period="15d", interval="1h")

        if datos.empty:
            st.warning("No se pudo obtener datos para el ticker proporcionado.")
        else:
            datos.reset_index(inplace=True)
            senales = []

            for i in range(1, len(datos)):
                row = datos.iloc[i]
                anterior = datos.iloc[i - 1]

                if detectar_martillo(row):
                    senales.append((row['Datetime'], "🔨 Martillo"))

                if detectar_estrella_fugaz(row):
                    senales.append((row['Datetime'], "🌠 Estrella Fugaz"))

                if detectar_envolvente(row, anterior):
                    senales.append((row['Datetime'], "📦 Envolvente Alcista"))

            if senales:
                st.success("📈 Señales detectadas:")
                for tiempo, tipo in senales:
                    st.write(f"- {tiempo.strftime('%Y-%m-%d %H:%M')} — {tipo}")
            else:
                st.info("No se detectaron señales en el periodo analizado.")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
