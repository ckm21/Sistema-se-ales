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
        (df['Close'].shift(1) < df['Open'].shift(1)) &  # Día 1 bajista
        (df['Close'] > df['Open']) &  # Día 2 alcista
        (df['Open'] < df['Close'].shift(1)) &  # Día 2 abre por debajo del cierre anterior
        (df['Close'] > df['Open'].shift(1))  # Día 2 cierra por encima de la apertura anterior
    )

# ========================
# Función principal
# ========================

def analizar_patrones(ticker):
    try:
        hoy = datetime.today()
        inicio = hoy - timedelta(days=30)

        df = yf.download(ticker, start=inicio, end=hoy, interval="1d")

        if df.empty:
            return "No se encontraron datos", pd.DataFrame()

        df = df[['Open
