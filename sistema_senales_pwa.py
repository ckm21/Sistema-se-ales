import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------- Funciones para detectar velas ----------------------

def detectar_martillo(row):
    cuerpo = abs(row['Open'] - row['Close'])
    mecha_inferior = np.minimum(row['Open'], row['Close']) - row['Low']
    mecha_superior = row['High'] - np.maximum(row['Open'], row['Close'])
    return cuerpo < mecha_inferior and mecha_superior < cuerpo

def detectar_estrella_fugaz(row):
    cuerpo = abs(row['Open'] - row['Close'])
    mecha_superior = row['High'] - np.maximum(row['Open'], row['Close'])
    mecha_inferior = np.minimum(row['Open'], row['Close']) - row['Low']
    return cuerpo < mecha_superior and mecha_inferior < cuerpo

def detectar_doji(row):
    return abs(row['Open'] - row['Close']) <= 0.05 * (row['High'] - row['Low'])

# ---------------------- Análisis del DataFrame ----------------------

def analizar_df(df):
    df['Martillo'] = df.apply(detectar_martillo, axis=1)
    df['Estrella_Fugaz'] = df.apply(detectar_estrella_fugaz, axis=1)
    df['Doji'] = df.apply(detectar_doji, axis=1)
    return df

# ---------------------- Detección de tendencia ----------------------

def detectar_tendencia(df):
    tendencia = "Lateral"
    if df['Close'].iloc[-1] > df['Close'].iloc[0] * 1.02:
        tendencia = "📈 Tendencia Alcista"
    elif df['Close'].iloc[-1] < df['Close'].iloc[0] * 0.98:
        tendencia = "📉 Tendencia Bajista"
    return tendencia

# ---------------------- Visualización con Plotly ----------------------

def crear_grafico_velas(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    fig.update_layout(title='Gráfico de Velas Japonesas', xaxis_title='Fecha', yaxis_title='Precio')
    return fig

# ---------------------- Interfaz de Streamlit ----------------------

st.title("📈 Sistema de Señales por Velas Japonesas")

ticker = st.text_input("🔍 Escribe un ticker (simulado o real):", value="AMD")
dias = st.slider("Cantidad de días de datos:", min_value=10, max_value=100, value=20)

# Obtener datos desde Yahoo Finance
try:
    df = yf.download(ticker, period=f"{dias}d", interval="1d")
    df = df[['Open', 'High', 'Low', 'Close']]
    df = df.dropna()
    df = analizar_df(df)
    
    # Notificación superior
    ultima_fila = df.iloc[-1]
    mensaje = ""
    if ultima_fila['Martillo']:
        mensaje = "🟢 Opción de Compra (Martillo detectado)"
    elif ultima_fila['Estrella_Fugaz']:
        mensaje = "🔴 Riesgo de Pérdida (Estrella Fugaz detectada)"
    elif ultima_fila['Doji']:
        mensaje = "⚠️ Indecisión del mercado (Doji detectado)"

    tendencia_actual = detectar_tendencia(df)

    # Cuadro superior de alerta
    if mensaje:
        st.info(f"📢 {mensaje} | {tendencia_actual}")
    else:
        st.info(f"📊 Sin señales claras | {tendencia_actual}")

    # Mostrar tabla y gráfico
    st.subheader("📋 Datos recientes")
    st.dataframe(df.tail(10))

    st.subheader("📊 Gráfico de Velas")
    st.plotly_chart(crear_grafico_velas(df), use_container_width=True)

except Exception as e:
    st.error(f"Ocurrió un error al obtener o analizar los datos: {e}")