import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# === Funciones para detectar patrones de velas ===
def detectar_martillo(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    return (mecha_inferior > 2 * cuerpo) and (mecha_superior < cuerpo)

def detectar_estrelladelamanana(df, i):
    if i < 2:
        return False
    c1, c2, c3 = df.iloc[i-2], df.iloc[i-1], df.iloc[i]
    return (
        c1['Close'] < c1['Open'] and
        abs(c2['Close'] - c2['Open']) < (c1['Open'] - c1['Close']) * 0.3 and
        c3['Close'] > c3['Open'] and
        c3['Close'] > ((c1['Open'] + c1['Close']) / 2)
    )

def detectar_envueltaalcista(df, i):
    if i < 1:
        return False
    prev, curr = df.iloc[i-1], df.iloc[i]
    return (
        prev['Close'] < prev['Open'] and
        curr['Open'] < prev['Close'] and
        curr['Close'] > prev['Open']
    )

# === Interfaz Streamlit ===
st.set_page_config(page_title="📊 Sistema de Señales por Velas", layout="centered")
st.title("📊 Sistema de Señales por Velas Japonesas")
st.write("Este sistema detecta patrones clásicos de velas para generar señales de compra o venta.")

ticker = st.text_input("🔎 Escribe el ticker (ej. AMD, AAPL, MSFT)", "AMD")

if ticker:
    try:
        end = datetime.now()
        start = end - timedelta(days=30)
        df = yf.download(ticker, start=start, end=end, interval="1d")

        if df.empty:
            st.warning("No se encontraron datos para ese ticker.")
        else:
            df = df[['Open', 'High', 'Low', 'Close']]
            df.reset_index(inplace=True)
            señales = []

            for i, row in df.iterrows():
                señal = []
                if detectar_martillo(row):
                    señal.append("🟢 Martillo")
                if detectar_estrelladelamanana(df, i):
                    señal.append("🌅 Estrella Mañana")
                if detectar_envueltaalcista(df, i):
                    señal.append("📦 Envolvente Alcista")
                señales.append(", ".join(señal) if señal else "—")

            df['Señales'] = señales
            st.dataframe(df[['Date', 'Open', 'High', 'Low', 'Close', 'Señales']])
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
