import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# Configuración de la app
st.set_page_config(page_title="Sistema de Señales por Velas", layout="wide")
st.title("📈 Sistema de Señales por Velas Japonesas")

# Inputs
ticker = st.text_input("🔍 Escribe un ticker (simulado):", value="AMD")
dias = st.slider("Cantidad de días de datos:", min_value=10, max_value=100, value=20)

# Descargar datos reales desde Yahoo Finance
df = yf.download(ticker, period=f"{dias}d", interval="1d")

# Asegurarse de que el índice sea una columna
df.reset_index(inplace=True)

# Detectores de patrones
def detectar_martillo(row):
    cuerpo = abs(row['Open'] - row['Close'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    return cuerpo < mecha_inferior and mecha_superior < cuerpo

def detectar_estrella_fugaz(row):
    cuerpo = abs(row['Open'] - row['Close'])
    mecha_superior = row['High'] - max(row['Open'], row['Close'])
    mecha_inferior = min(row['Open'], row['Close']) - row['Low']
    return cuerpo < mecha_superior and mecha_inferior < cuerpo

def detectar_doji(row):
    return abs(row['Open'] - row['Close']) < 0.1 * (row['High'] - row['Low'])

# Aplicar los patrones
def analizar_df(df):
    df['Martillo'] = df.apply(detectar_martillo, axis=1)
    df['EstrellaFugaz'] = df.apply(detectar_estrella_fugaz, axis=1)
    df['Doji'] = df.apply(detectar_doji, axis=1)
    df['Compra'] = df['Martillo']
    df['Venta'] = df['EstrellaFugaz']
    return df

df_signals = analizar_df(df)

# Mostrar notificaciones claras en recuadro superior
ultima_fila = df_signals.iloc[-1]
if ultima_fila['Compra'] == True:
    st.success("🟢 Opción de compra detectada (martillo)")
elif ultima_fila['Venta'] == True:
    st.error("🔴 Riesgo de pérdida detectado (estrella fugaz)")

# Mostrar tabla de datos
st.subheader("📋 Datos recientes")
st.dataframe(df_signals[['Date', 'Open', 'High', 'Low', 'Close']].tail(10), use_container_width=True)

# Gráfico de velas
fig = go.Figure(data=[go.Candlestick(
    x=df_signals['Date'],
    open=df_signals['Open'],
    high=df_signals['High'],
    low=df_signals['Low'],
    close=df_signals['Close'],
    increasing_line_color='green',
    decreasing_line_color='red'
)])
fig.update_layout(title=f'Gráfico de velas: {ticker}', xaxis_title='Fecha', yaxis_title='Precio')
st.plotly_chart(fig, use_container_width=True)