import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from funciones import detectar_senales, detectar_tendencia

st.set_page_config(page_title="📈 Sistema de Velas", layout="centered")

st.title("📊 Velas Japonesas")
st.caption("Versión 2.0 – Monitoreo de señales de entrada y salida según velas japonesas y tendencias.")

ticker = st.text_input("📝 Ingresa el ticker:", value="AMD")
intervalo = st.selectbox("⏰ Intervalo de tiempo", ["15m", "1h", "4h", "1d"])
periodo = st.selectbox("📅 Periodo de análisis", ["5d", "10d", "1mo", "3mo", "6mo", "1y"])

if ticker and intervalo and periodo:
    try:
        data = yf.download(ticker, period=periodo, interval=intervalo)
        data.dropna(inplace=True)
        data.columns = [col.lower() for col in data.columns]

        df = data.copy()
        df = detectar_senales(df)
        df = detectar_tendencia(df)

        ult_fila = df.iloc[-1]
        tendencia = ult_fila["Tendencia"]
        señales = [col for col in ["Martillo", "Estrella Fugaz", "Doji", "Envolvente Alcista", "Envolvente Bajista"] if ult_fila.get(col)]

        if señales:
            st.warning(f"⚠️ Señales detectadas: {', '.join(señales)}")

        if tendencia == "Alcista":
            st.success("📈 Tendencia actual: Alcista")
        elif tendencia == "Bajista":
            st.error("📉 Tendencia actual: Bajista")
        else:
            st.info("➖ Tendencia actual: Lateral")

        # Mostrar gráfico
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Velas"
        ))
        st.plotly_chart(fig, use_container_width=True)

        # Mostrar tabla de señales si hay
        st.subheader("📋 Datos recientes")
        st.dataframe(df.tail(10))

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")