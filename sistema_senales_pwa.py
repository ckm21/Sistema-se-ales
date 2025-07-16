import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# ========================
# Funciones para detectar patrones
# ========================

def detectar_martillo(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    return mecha_inferior > 2 * cuerpo and mecha_superior < cuerpo

def detectar_estrellas(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    return mecha_superior > 2 * cuerpo and mecha_inferior < cuerpo

def detectar_envuelta(df):
    return (
        (df['Close'].shift(1) < df['Open'].shift(1)) &
        (df['Close'] > df['Open']) &
        (df['Open'] < df['Close'].shift(1)) &
        (df['Close'] > df['Open'].shift(1))
    )

# ========================
# Función principal de análisis
# ========================

def analizar_df(df):
    señales = []

    for i, row in df.iterrows():
        if detectar_martillo(row):
            señales.append((i, 'Martillo'))
        elif detectar_estrellas(row):
            señales.append((i, 'Estrella'))

    envolvente_series = detectar_envuelta(df).fillna(False)

    for i, val in envolvente_series.items():
        if val:  # 👈 aquí sí evaluamos cada valor booleano individualmente
            señales.append((i, 'Envolvente Alcista'))

    return pd.DataFrame(señales, columns=['Fecha', 'Patrón'])

# ========================
# Interfaz Streamlit
# ========================

st.title("📊 Sistema de Señales por Velas Japonesas")
st.write("Este sistema detecta patrones clásicos de velas para generar señales de compra o venta.")

ticker = st.text_input("🔍 Escribe el ticker (ej. AMD, AAPL, MSFT)", value="AMD")

if ticker:
    try:
        fin = datetime.today()
        inicio = fin - timedelta(days=30)

        data = yf.download(ticker, start=inicio, end=fin)

        if data.empty:
            st.warning("No se pudieron obtener datos para este ticker.")
        else:
            st.subheader("📈 Datos recientes")
            st.dataframe(data.tail(10))

            señales_df = analizar_df(data)

            if not señales_df.empty:
                st.subheader("🔔 Señales detectadas")
                st.dataframe(señales_df)
            else:
                st.info("No se detectaron patrones en los últimos días.")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
