import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de la app
st.set_page_config(layout="wide")
st.title("📈 Analizador de Velas Japonesas – Estrategia Tortuga 🐢")

# Tickers disponibles
tickers = ["AMD", "AAPL", "MSFT", "GOOGL", "META", "PFE", "LLY"]
ticker = st.selectbox("Selecciona una acción:", tickers)

# Intervalos y rangos de tiempo
interval = st.selectbox("Intervalo de tiempo:", ["1m", "5m", "15m", "1h", "4h", "1d"])
period = st.selectbox("Rango de datos:", ["1d", "5d", "7d", "1mo"])

# Descargar datos
data = yf.download(ticker, interval=interval, period=period)
data.dropna(inplace=True)

# Detectar patrones
def detectar_martillo(df):
    cuerpo = abs(df["Close"] - df["Open"])
    mecha_inferior = df["Open"] - df["Low"]
    mecha_superior = df["High"] - df["Close"]
    return (mecha_inferior > cuerpo * 2) & (mecha_superior < cuerpo)

def detectar_estrella_fugaz(df):
    cuerpo = abs(df["Close"] - df["Open"])
    mecha_superior = df["High"] - df[["Close", "Open"]].max(axis=1)
    mecha_inferior = df[["Close", "Open"]].min(axis=1) - df["Low"]
    return (mecha_superior > cuerpo * 2) & (mecha_inferior < cuerpo)

def detectar_doji(df):
    return abs(df["Close"] - df["Open"]) <= ((df["High"] - df["Low"]) * 0.1)

# Agregar señales
data["Martillo"] = detectar_martillo(data)
data["Estrella"] = detectar_estrella_fugaz(data)
data["Doji"] = detectar_doji(data)

# Detección de tendencia
if data["Close"].iloc[-1] > data["Close"].iloc[0]:
    tendencia = "📈 Tendencia Alcista"
else:
    tendencia = "📉 Tendencia Bajista"

# Mostrar gráfica
fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name='Velas'
)])

# Agregar patrones a la gráfica
for i in range(len(data)):
    if data["Martillo"].iloc[i]:
        fig.add_trace(go.Scatter(x=[data.index[i]], y=[data["Low"].iloc[i]],
                                 mode="markers", marker=dict(color="green", size=10),
                                 name="Martillo"))
    if data["Estrella"].iloc[i]:
        fig.add_trace(go.Scatter(x=[data.index[i]], y=[data["High"].iloc[i]],
                                 mode="markers", marker=dict(color="red", size=10),
                                 name="Estrella Fugaz"))
    if data["Doji"].iloc[i]:
        fig.add_trace(go.Scatter(x=[data.index[i]], y=[(data["High"].iloc[i] + data["Low"].iloc[i]) / 2],
                                 mode="markers", marker=dict(color="orange", size=10),
                                 name="Doji"))

# Layout
fig.update_layout(title=f"Gráfico de Velas para {ticker} ({interval})",
                  xaxis_title="Fecha",
                  yaxis_title="Precio")

st.plotly_chart(fig, use_container_width=True)

# Mostrar notificación de señales
ultima_fila = data.iloc[-1]
mensaje = ""

if ultima_fila["Martillo"]:
    mensaje = "✅ Opción de Compra (Martillo)"
elif ultima_fila["Estrella"]:
    mensaje = "⚠️ Riesgo de Caída (Estrella Fugaz)"
elif ultima_fila["Doji"]:
    mensaje = "⚠️ Indecisión (Doji)"

if mensaje:
    st.markdown(f"### 🔔 {mensaje}")

# Mostrar tendencia
st.markdown(f"**Tendencia actual:** {tendencia}")

# Mostrar estrategia
with st.expander("📘 Estrategia Tortuga (Versión 2.0)"):
    st.markdown("""
- ✅ **Entrada**: Solo en velas con cuerpo sólido luego de periodo estable.
- ⚠️ **No operar**: En zonas de congestión, cuerpos cortos, o velas sin dirección clara.
- 🔄 **Evaluación por velas**: 1m, 5m, 15m, 1h, 4h.
- 🧠 **Salidas**: Señales de agotamiento, mechas largas o velas de indecisión.
- 💰 **Objetivo de ganancia**: Entre +1.5% y +2.5% por operación táctica.
- 💼 **Gestión de capital**: Operaciones de $10, $15 o $20.
- 🧪 **Validación**: Antes de entrar o salir, validar con análisis multivelas.
""")