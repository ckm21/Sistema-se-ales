import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from io import BytesIO

# =========================
# Funciones de patrones
# =========================

def detectar_martillo(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_inferior = row['Open'] - row['Low'] if row['Open'] < row['Close'] else row['Close'] - row['Low']
    mecha_superior = row['High'] - row['Close'] if row['Open'] < row['Close'] else row['High'] - row['Open']
    return mecha_inferior > 2 * cuerpo and mecha_superior < cuerpo

def detectar_estrellas(row):
    cuerpo = abs(row['Close'] - row['Open'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    return mecha_inferior > 2 * cuerpo and mecha_inferior < cuerpo * 4

def detectar_envuelta(df):
    envolvente = (
        (df['Close'].shift(1) < df['Open'].shift(1)) &
        (df['Open'] < df['Close']) &
        (df['Open'] < df['Close'].shift(1)) &
        (df['Close'] > df['Open'].shift(1))
    )
    return envolvente

# =========================
# Análisis del DataFrame
# =========================

def analizar_df(df):
    señales = []

    for i, row in df.iterrows():
        if detectar_martillo(row):
            señales.append((i, 'Martillo'))
        elif detectar_estrellas(row):
            señales.append((i, 'Estrella'))

    envolvente_series = detectar_envuelta(df).fillna(False)
    for i, val in envolvente_series.items():
        if val:
            señales.append((i, 'Envolvente Alcista'))

    return pd.DataFrame(señales, columns=['Fecha', 'Patrón'])

# =========================
# Visualización con Plotly
# =========================

def mostrar_grafico(df, señales):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Velas'
    )])

    colores = {
        'Martillo': 'blue',
        'Estrella': 'orange',
        'Envolvente Alcista': 'green'
    }

    for _, fila in señales.iterrows():
        fecha = fila['Fecha']
        patrón = fila['Patrón']
        precio = df.loc[fecha]['Close']
        fig.add_trace(go.Scatter(
            x=[fecha],
            y=[precio],
            mode='markers+text',
            name=patrón,
            text=[patrón],
            textposition="top center",
            marker=dict(size=12, color=colores.get(patrón, 'black'), symbol='triangle-up')
        ))

    fig.update_layout(title="Gráfico de Velas Japonesas con Señales Detectadas", xaxis_title="Fecha", yaxis_title="Precio")
    return fig

# =========================
# Interfaz Streamlit
# =========================

st.title("📊 Sistema de Señales por Velas Japonesas")
st.markdown("Este sistema detecta patrones clásicos de velas para generar señales de compra o venta.")

ticker = st.text_input("🔍 Escribe el ticker (ej. AMD, AAPL, MSFT)", "AMD")

if ticker:
    try:
        fin = datetime.today()
        inicio = fin - timedelta(days=20)
        df = yf.download(ticker, start=inicio, end=fin, interval="1d")
        df = df[['Open', 'High', 'Low', 'Close']]
        st.subheader("📈 Datos recientes")
        st.dataframe(df.tail(10))

        señales = analizar_df(df)
        st.subheader("🔔 Señales detectadas")
        st.dataframe(señales)

        if not señales.empty:
            fig = mostrar_grafico(df, señales)
            st.plotly_chart(fig, use_container_width=True)

            # Descarga como CSV
            csv = señales.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar señales en CSV",
                data=csv,
                file_name=f'senales_{ticker}.csv',
                mime='text/csv'
            )
        else:
            st.info("No se detectaron señales en los últimos días.")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
