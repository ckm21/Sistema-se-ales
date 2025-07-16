import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Funciones de patrones
def detectar_martillo(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    return mecha_inferior > cuerpo * 2 and mecha_superior < cuerpo

def detectar_estrella_fugaz(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    return mecha_superior > cuerpo * 2 and mecha_inferior < cuerpo

def detectar_envolvente_bajista(df, i):
    if i == 0:
        return False
    prev = df.iloc[i - 1]
    curr = df.iloc[i]
    return (
        prev['Close'] > prev['Open'] and
        curr['Close'] < curr['Open'] and
        curr['Open'] > prev['Close'] and
        curr['Close'] < prev['Open']
    )

# Configuración de la app
st.set_page_config(page_title="Sistema de Señales Reales", layout="centered")
st.title("📈 Sistema de Señales con Velas Reales")

ticker = st.text_input("🔍 Escribe el ticker (ej. AMD, AAPL, MSFT)", value="AMD")

if ticker:
    # Descargar datos reales
    datos = yf.download(ticker, period="1d", interval="15m")
    if datos.empty:
        st.warning("No se encontraron datos para ese ticker.")
    else:
        datos = datos.reset_index()

        # Detectar señales
        senales = []
        for i, row in datos.iterrows():
            s = []
            if detectar_martillo(row): s.append("🟢 Martillo")
            if detectar_estrella_fugaz(row): s.appen
