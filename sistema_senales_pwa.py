import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from PIL import Image

# Cargar imagen (logo)
st.set_page_config(page_title="Sistema de Señales", page_icon="🐢")
logo = Image.open("tortuga.png")
st.image(logo, width=80)

# Título
st.title("📉 Sistema de Señales por Velas Japonesas")
st.markdown("**Versión 2.0 – Monitoreo de señales de entrada y salida según velas japonesas y tendencias.**")

# Inputs
ticker = st.text_input("📌 Ingresa el ticker:", value="AMD")
intervalo = st.selectbox("🕒 Intervalo de tiempo", ["15m", "30m", "1h", "4h", "1d"])
periodo = st.selectbox("📅 Periodo de análisis", ["1d", "5d", "7d", "1mo", "3mo"])

# Obtener datos
@st.cache_data
def obtener_datos(ticker, intervalo, periodo):
    data = yf.download(ticker, interval=intervalo, period=periodo)
    data.columns = [col.lower() for col in data.columns]
    return data

# Detección de señales
def detectar_senales(df):
    df = df.copy()
    df["señal_compra"] = False
    df["señal_venta"] = False
    df["tendencia"] = "Indefinida"

    for i in range(1, len(df)):
        open_, close, high, low = df.iloc[i][["open", "close", "high", "low"]]
        cuerpo = abs(close - open_)
        mecha = high - low

        try:
            if cuerpo < mecha * 0.2:
                if close > open_ and df.iloc[i - 1]["close"] < df.iloc[i - 1]["open"]:
                    df.at[df.index[i], "señal_compra"] = True
                elif close < open_ and df.iloc[i - 1]["close"] > df.iloc[i - 1]["open"]:
                    df.at[df.index[i], "señal_venta"] = True
        except:
            continue

        if i >= 3:
            if df["close"].iloc[i] > df["close"].iloc[i - 1] > df["close"].iloc[i - 2]:
                df.at[df.index[i], "tendencia"] = "Alcista"
            elif df["close"].iloc[i] < df["close"].iloc[i - 1] < df["close"].iloc[i - 2]:
                df.at[df.index[i], "tendencia"] = "Bajista"
            else:
                df.at[df.index[i], "tendencia"] = "Lateral"

    return df

# Mostrar resultados
if ticker:
    try:
        datos = obtener_datos(ticker, intervalo, periodo)
        if datos.empty:
            st.warning("No se encontraron datos. Verifica el ticker o el periodo.")
        else:
            df_resultado = detectar_senales(datos)
            st.subheader("📊 Gráfico de velas")
            fig, ax = plt.subplots(figsize=(10, 5))

            for i in range(len(df_resultado)):
                o = df_resultado["open"].iloc[i]
                c = df_resultado["close"].iloc[i]
                h = df_resultado["high"].iloc[i]
                l = df_resultado["low"].iloc[i]
                color = "green" if c > o else "red"
                ax.plot([i, i], [l, h], color="black")
                ax.plot([i, i], [o, c], color=color, linewidth=5)

            ax.set_xticks(range(0, len(df_resultado), max(1, len(df_resultado)//10)))
            ax.set_xticklabels(df_resultado.index.strftime('%m-%d %H:%M')[::max(1, len(df_resultado)//10)], rotation=45)
            st.pyplot(fig)

            st.subheader("📌 Últimas señales detectadas")
            ultimas = df_resultado[df_resultado["señal_compra"] | df_resultado["señal_venta"]].tail(5)
            st.dataframe(ultimas[["open", "close", "señal_compra", "señal_venta", "tendencia"]])
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")