import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# ========================
# Funciones de patrones
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

def analizar_df(df):
    señales = []

    for i, row in df.iterrows():
        if detectar_martillo(row):
            señales.append((i, 'Martillo'))
        elif detectar_estrellas(row):
            señales.append((i, 'Estrella'))

    df['Envolvente'] = detectar_envuelta(df)

    for i in df[df['Envolvente']].index:
        señales.append((i, 'Envolvente Alcista'))

    return pd.DataFrame(señales, columns=['Fecha', 'Patrón'])

# ========================
# Interfaz Streamlit
# ========================

st.title("📊 Sistema de Señales por Velas Japonesas")

ticker = st.text_input("🔍 Escribe el ticker (ej. AMD, AAPL, MSFT)", "AMD")

if ticker:
    try:
        fin = datetime.today()
        inicio = fin - timedelta(days=30)

        df = yf.download(ticker, start=inicio, end=fin, interval='1d')

        if df.empty:
            st.error("No se encontraron datos. Revisa el ticker.")
        else:
            df = df[['Open', 'High', 'Low', 'Close']]
            st.subheader("📈 Datos recientes")
            st.dataframe(df.tail(10))

            resultado = analizar_df(df)

            if resultado.empty:
                st.info("No se detectaron señales.")
            else:
                st.success("Señales detectadas:")
                st.dataframe(resultado)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
