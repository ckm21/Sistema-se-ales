import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ================================
# Funciones para detectar patrones
# ================================

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

def detectar_envolvente(df):
    return (
        (df['Close'].shift(1) < df['Open'].shift(1)) & 
        (df['Close'] > df['Open']) & 
        (df['Open'] < df['Close'].shift(1)) & 
        (df['Close'] > df['Open'].shift(1))
    )

# ======================================
# Función principal de análisis de velas
# ======================================

def analizar_df(df):
    señales = []
    for i, row in df.iterrows():
        if detectar_martillo(row):
            señales.append((row.name, 'Martillo'))
        elif detectar_estrellas(row):
            señales.append((row.name, 'Estrella'))

    df['Envolvente'] = detectar_envolvente(df)

    for i in df[df['Envolvente']].index:
        señales.append((i, 'Envolvente Alcista'))

    return pd.DataFrame(señales, columns=['Fecha', 'Patrón'])

# ====================
# Función para graficar
# ====================

def graficar(df):
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Precio'
        )
    ])
    fig.update_layout(title='Gráfico de Velas Japonesas', xaxis_title='Fecha', yaxis_title='Precio')
    return fig

# ============
# Interfaz App
# ============

st.title("📈 Sistema de Señales por Velas Japonesas")

ticker = st.text_input("🔎 Escribe un ticker (simulado):", value="AMD")
dias = st.slider("Cantidad de días de datos simulados:", 10, 100, 20)

if ticker:
    df = yf.download(ticker, period=f"{dias}d", interval='1d')
    df.dropna(inplace=True)

    st.subheader("📋 Datos recientes")
    st.dataframe(df)

    df_signals = analizar_df(df)

    # =====================
    # 🔔 Notificaciones top
    # =====================
    ultima_fila = df.iloc[-1]
    cuerpo_rojo = ultima_fila['Close'] < ultima_fila['Open']
    caida_fuerte = (ultima_fila['Open'] - ultima_fila['Close']) > (ultima_fila['Open'] * 0.015)

    hay_compra = not df_signals.empty
    hay_venta = cuerpo_rojo and caida_fuerte

    if hay_compra:
        st.success("✅ Opción de compra detectada según velas japonesas.")

    if hay_venta:
        st.warning("⚠️ Riesgo de pérdida detectado: vela bajista fuerte, considera vender.")

    # ================
    # Señales halladas
    # ================
    st.subheader("📍 Señales detectadas")
    st.dataframe(df_signals)

    # ============
    # Gráfico velas
    # ============
    st.subheader("🕯️ Gráfico de Velas")
    fig = graficar(df)
    st.plotly_chart(fig, use_container_width=True)