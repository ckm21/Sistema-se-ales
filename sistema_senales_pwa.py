import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# Funciones de análisis de velas
def detectar_martillo(row):
    cuerpo = abs(row['close'] - row['open'])
    mecha_inferior = row['open'] - row['low'] if row['close'] > row['open'] else row['close'] - row['low']
    mecha_superior = row['high'] - row['close'] if row['close'] > row['open'] else row['high'] - row['open']
    return mecha_inferior > 2 * cuerpo and mecha_superior < cuerpo

def detectar_env_bajista(row_anterior, row_actual):
    return row_anterior['close'] > row_anterior['open'] and row_actual['close'] < row_actual['open'] and row_actual['open'] > row_anterior['close'] and row_actual['close'] < row_anterior['open']

def detectar_env_alcista(row_anterior, row_actual):
    return row_anterior['close'] < row_anterior['open'] and row_actual['close'] > row_actual['open'] and row_actual['open'] < row_anterior['close'] and row_actual['close'] > row_anterior['open']

# Detectar tendencia simple
def detectar_tendencia(df):
    if len(df) < 5:
        return "📉 Muy pocos datos"
    ventana = df['close'].rolling(window=5)
    if df['close'].iloc[-1] > ventana.mean().iloc[-1]:
        return "📈 Tendencia alcista"
    else:
        return "📉 Tendencia bajista"

# Analizar el DataFrame y añadir columnas de señales
def analizar_df(df):
    df['Martillo'] = df.apply(detectar_martillo, axis=1)
    df['EnvBajista'] = False
    df['EnvAlcista'] = False

    for i in range(1, len(df)):
        df.loc[i, 'EnvBajista'] = detectar_env_bajista(df.iloc[i-1], df.iloc[i])
        df.loc[i, 'EnvAlcista'] = detectar_env_alcista(df.iloc[i-1], df.iloc[i])
    
    return df

# Gráfico
def graficar(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Velas'
    )])

    señales_compra = df[df['Martillo'] | df['EnvAlcista']]
    señales_venta = df[df['EnvBajista']]

    fig.add_trace(go.Scatter(
        x=señales_compra.index,
        y=señales_compra['close'],
        mode='markers',
        marker=dict(symbol='arrow-up', color='green', size=10),
        name='Compra'
    ))

    fig.add_trace(go.Scatter(
        x=señales_venta.index,
        y=señales_venta['close'],
        mode='markers',
        marker=dict(symbol='arrow-down', color='red', size=10),
        name='Venta'
    ))

    return fig

# INTERFAZ STREAMLIT
st.title("📉 Sistema de Señales por Velas Japonesas")

ticker = st.text_input("Ticker de la acción:", "AAPL")
intervalo = st.selectbox("Intervalo de tiempo", ["15m", "30m", "1h", "1d"])
periodo = st.selectbox("Periodo de análisis", ["1d", "5d", "7d", "1mo"])

if ticker:
    data = yf.download(tickers=ticker, period=periodo, interval=intervalo)

    if data.empty:
        st.error("No se pudo obtener datos para ese ticker.")
    else:
        # Validar columnas
        if any(col is None for col in data.columns):
            st.error("Algunas columnas son inválidas.")
        else:
            data.columns = [col.lower() for col in data.columns]
            df = data.copy()
            df_signals = analizar_df(df)
            tendencia = detectar_tendencia(df)

            # Recuadro superior con señal clara
            if df_signals['Martillo'].iloc[-1] or df_signals['EnvAlcista'].iloc[-1]:
                st.success("🟢 Opción de compra detectada (señal alcista)")
            elif df_signals['EnvBajista'].iloc[-1]:
                st.error("🔴 Riesgo de pérdida detectado (señal bajista)")
            else:
                st.warning("⚠️ Sin señales claras")

            st.subheader("📊 Tendencia actual:")
            st.write(tendencia)

            st.plotly_chart(graficar(df_signals), use_container_width=True)
            st.dataframe(df_signals.tail(20))
