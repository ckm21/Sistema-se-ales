import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# ---------------------------
# Funciones de patrones
# ---------------------------

def detectar_martillo(row):
    if not all(k in row for k in ['Open', 'Close', 'High', 'Low']):
        return False
    cuerpo = abs(row['Open'] - row['Close'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    return mecha_inferior > 2 * cuerpo and mecha_superior < cuerpo

def detectar_estrella_fugaz(row):
    if not all(k in row for k in ['Open', 'Close', 'High', 'Low']):
        return False
    cuerpo = abs(row['Open'] - row['Close'])
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    return mecha_superior > 2 * cuerpo and mecha_inferior < cuerpo

def detectar_envuelta_alcista(df, i):
    if i == 0:
        return False
    anterior = df.iloc[i - 1]
    actual = df.iloc[i]
    return anterior['Close'] < anterior['Open'] and actual['Close'] > actual['Open'] and actual['Close'] > anterior['Open'] and actual['Open'] < anterior['Close']

# ---------------------------
# Interfaz
# ---------------------------

st.title("📊 Sistema de Señales por Velas")
st.write("Este sistema muestra recomendaciones de compra y venta basadas en patrones de velas japonesas.")

ticker = st.text_input("🔍 Escribe el ticker (ej. AMD, AAPL, MSFT)", value="AMD")

if ticker:
    try:
        df = yf.download(ticker, interval="15m", period="1d")
        df = df.rename(columns={'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close'})

        if not df.empty:
            df.reset_index(inplace=True)
            df['Hora'] = df['Datetime'].dt.strftime('%H:%M')
            df['Señal'] = ""

            for i in range(len(df)):
                row = df.iloc[i]
                señales = []

                if detectar_martillo(row):
                    señales.append('Martillo')
                if detectar_estrella_fugaz(row):
                    señales.append('Estrella Fugaz')
                if detectar_envuelta_alcista(df, i):
                    señales.append('Envuelta Alcista')

                df.at[i, 'Señal'] = ", ".join(señales)

            st.dataframe(df[['Hora', 'Open', 'Close', 'High', 'Low', 'Volume', 'Señal']])
            st.info("🔔 El sistema se actualizará cada 15 minutos con nuevas señales.")
        else:
            st.warning("⚠️ No se encontraron datos para este ticker.")
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
