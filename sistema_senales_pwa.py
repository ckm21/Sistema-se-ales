import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta

# Configuración inicial
st.set_page_config(page_title="Señales por Velas", layout="wide")
st.title("📈 Sistema de Señales por Velas Japonesas")

# Entradas
ticker = st.text_input("Ticker de la acción:", value="AAPL")
interval = st.selectbox("Intervalo de tiempo", ["1m", "5m", "15m", "30m", "1h", "1d", "1wk"], index=2)
period = st.selectbox("Periodo de análisis", ["1d", "5d", "7d", "1mo"], index=1)

# Obtener datos
data = yf.download(ticker, period=period, interval=interval)
if data.empty:
    st.warning("No se pudieron obtener datos.")
    st.stop()

data.reset_index(inplace=True)
data.columns = [col.lower() for col in data.columns]

# Detectar tendencia simple
def detectar_tendencia(df):
    if df['close'].iloc[-1] > df['close'].iloc[-5]:
        return "📈 Alcista"
    elif df['close'].iloc[-1] < df['close'].iloc[-5]:
        return "📉 Bajista"
    else:
        return "⏸️ Lateral"

# Detectar patrones de velas
def detectar_patrones(df):
    señales = []

    for i in range(1, len(df)):
        o = df['open'].iloc[i]
        c = df['close'].iloc[i]
        h = df['high'].iloc[i]
        l = df['low'].iloc[i]
        prev_o = df['open'].iloc[i-1]
        prev_c = df['close'].iloc[i-1]

        cuerpo = abs(c - o)
        mecha_superior = h - max(c, o)
        mecha_inferior = min(c, o) - l

        # Martillo
        if cuerpo < (mecha_inferior * 0.5) and mecha_inferior > cuerpo * 2:
            señales.append(("📌 Martillo", df['datetime'].iloc[i]))

        # Envolvente alcista
        elif c > o and prev_c < prev_o and c > prev_o and o < prev_c:
            señales.append(("🟢 Envolvente Alcista", df['datetime'].iloc[i]))

        # Doji
        elif cuerpo <= (h - l) * 0.1:
            señales.append(("⚠️ Doji", df['datetime'].iloc[i]))

    return señales

# Visualización
fig = go.Figure(data=[go.Candlestick(
    x=data['datetime'],
    open=data['open'],
    high=data['high'],
    low=data['low'],
    close=data['close'],
    increasing_line_color='green',
    decreasing_line_color='red'
)])

fig.update_layout(title=f"{ticker} - Velas ({interval})", xaxis_rangeslider_visible=False)

# Mostrar gráfico
st.plotly_chart(fig, use_container_width=True)

# Mostrar tendencia
tendencia = detectar_tendencia(data)
st.subheader(f"Tendencia: {tendencia}")

# Detectar señales
señales = detectar_patrones(data)
ultima_senal = señales[-1][0] if señales else None

# Mostrar notificación destacada
if ultima_senal == "🟢 Envolvente Alcista" or ultima_senal == "📌 Martillo":
    st.success("✅ Señal clara de *compra* detectada.")
elif ultima_senal == "⚠️ Doji":
    st.warning("⚠️ Incertidumbre en el mercado. Evaluar riesgo.")
else:
    st.info("🔎 Sin señal clara de entrada o salida.")

# Mostrar tabla de señales detectadas
if señales:
    df_señales = pd.DataFrame(señales, columns=["Patrón", "Fecha"])
    st.dataframe(df_señales.tail(5), use_container_width=True)
