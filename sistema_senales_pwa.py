# sistema_senales.py

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ========== Funciones de patrones ==========

def detectar_martillo(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    return mecha_inferior > 2 * cuerpo and mecha_superior < cuerpo

def detectar_estrellas(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_inferior = min(row['High'] - row['Open'], row['High'] - row['Close'])
    mecha_superior = min(row['Open'] - row['Low'], row['Close'] - row['Low'])
    return mecha_superior > 2 * cuerpo and mecha_inferior < cuerpo

def detectar_envolvente(df):
    envolvente = (df['Close'].shift(1) < df['Open'].shift(1)) & \
                 (df['Close'] > df['Open']) & \
                 (df['Close'] > df['Open'].shift(1)) & \
                 (df['Open'] < df['Close'].shift(1))
    return envolvente

def detectar_doji(row):
    cuerpo = abs(row['Close'] - row['Open'])
    rango_total = row['High'] - row['Low']
    return cuerpo < 0.1 * rango_total

# ========== Análisis de DataFrame ==========

def analizar_df(df):
    señales = []

    for i, row in df.iterrows():
        if detectar_martillo(row):
            señales.append((i, 'Martillo'))
        if detectar_estrellas(row):
            señales.append((i, 'Estrella'))
        if detectar_doji(row):
            señales.append((i, 'Doji'))

    df['Envolvente'] = detectar_envolvente(df)
    for i in df[df['Envolvente']].index:
        señales.append((i, 'Envolvente Alcista'))

    return pd.DataFrame(señales, columns=['Fecha', 'Patrón'])

# ========== Interfaz de Streamlit ==========

st.title("📊 Sistema de Señales por Velas Japonesas")
st.write("Este sistema detecta patrones clásicos de velas para generar señales de compra o venta.")

ticker = st.text_input("🔍 Escribe el ticker (ej. AMD, AAPL, MSFT)", value="AMD")

if ticker:
    try:
        df = yf.download(ticker, period="1mo", interval="1d")
        df = df[['Open', 'High', 'Low', 'Close']]
        st.subheader("📉 Datos recientes")
        st.dataframe(df.tail(10))

        señales = analizar_df(df)

        if not señales.empty:
            st.subheader("📌 Señales detectadas")
            st.dataframe(señales)

            # ========== Gráfico ==========
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Velas'
            )])

            for _, row in señales.iterrows():
                fig.add_trace(go.Scatter(
                    x=[row['Fecha']],
                    y=[df.loc[row['Fecha'], 'Close']],
                    mode="markers+text",
                    text=[row['Patrón']],
                    textposition="top center",
                    marker=dict(size=10, color='red'),
                    name=row['Patrón']
                ))

            st.plotly_chart(fig)

        else:
            st.info("No se detectaron señales en los últimos 30 días.")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
