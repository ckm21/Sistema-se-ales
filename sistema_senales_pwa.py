import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- Funciones de análisis de velas ---
def detectar_martillo(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    return mecha_inferior > 2 * cuerpo and mecha_superior < cuerpo

def detectar_estrellas_fugaces(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    return mecha_superior > 2 * cuerpo and mecha_inferior < cuerpo

def analizar_df(df):
    df['Martillo'] = df.apply(detectar_martillo, axis=1)
    df['EstrellaFugaz'] = df.apply(detectar_estrellas_fugaces, axis=1)
    df['Compra'] = df['Martillo']
    df['Venta'] = df['EstrellaFugaz']
    return df

# --- Interfaz principal ---
st.set_page_config(layout="centered")
st.title("📈 Sistema de Señales por Velas Japonesas")

ticker = st.text_input("🔍 Escribe un ticker (simulado):", value="AMD")
dias = st.slider("Cantidad de días de datos:", 10, 100, 20)

try:
    df = yf.download(ticker, period=f"{dias}d", interval="1d")
    df = df[['Open', 'High', 'Low', 'Close']]
    df.reset_index(inplace=True)
    df = analizar_df(df)

    # --- Notificaciones principales ---
    ultima_fila = df.iloc[-1]
    if ultima_fila['Compra']:
        st.success("🟢 Opción de compra detectada (martillo)")
    elif ultima_fila['Venta']:
        st.error("🔴 Riesgo de pérdida detectado (estrella fugaz)")

    # --- Mostrar tabla de datos ---
    st.subheader("📋 Datos recientes")
    st.dataframe(df.tail(10), use_container_width=True)

    # --- Gráfico ---
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        increasing_line_color='green', decreasing_line_color='red'
    )])
    fig.update_layout(title=f"Velas japonesas de {ticker}", xaxis_title="Fecha", yaxis_title="Precio")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Ocurrió un error: {e}")
