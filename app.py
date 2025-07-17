import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from funciones import detectar_senales, detectar_tendencia

st.set_page_config(page_title="📈 Señales Japonesas", layout="wide")

st.title("📊 Velas Japonesas")
st.caption("Versión 2.0 – Monitoreo de señales de entrada y salida según velas japonesas y tendencias.")

ticker = st.text_input("📈 Ingresa el ticker:", "AAPL").upper()
intervalo = st.selectbox("🕒 Intervalo de tiempo", ["15m", "30m", "1h", "4h", "1d"])
periodo = st.selectbox("📆 Periodo de análisis", ["1d", "5d", "7d", "1mo", "3mo"])

if ticker and intervalo and periodo:
    try:
        data = yf.download(ticker, period=periodo, interval=intervalo)
        data.dropna(inplace=True)
        data.columns = [col.lower() for col in data.columns]

        df = data.copy()
        df = detectar_senales(df)
        df = detectar_tendencia(df)

        ult_fila = df.iloc[-1]
        tendencia = ult_fila['Tendencia']
        señales = [col for col in ["Martillo", "Estrella Fugaz", "Doji", "Envolvente Alcista", "Envolvente Bajista"]
                   if ult_fila.get(col)]

        if señales:
            if "Estrella Fugaz" in señales or "Envolvente Bajista" in señales:
                st.warning("⚠️ Riesgo de pérdida: posible señal de salida / venta")
            elif "Martillo" in señales or "Envolvente Alcista" in señales:
                st.success("✅ Opción de compra detectada")
        elif tendencia == "Bajista":
            st.warning("📉 Tendencia bajista continua. Evita entrar sin confirmación.")
        else:
            st.info("ℹ️ No hay señales claras por ahora.")

        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Velas'
        )])
        fig.update_layout(title=f'Gráfico de {ticker}', xaxis_title='Fecha', yaxis_title='Precio')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Últimas señales detectadas")
        st.dataframe(df.tail(10).iloc[::-1])

    except Exception as e:
        st.error(f"Ocurrió un error al analizar los datos: {e}")
