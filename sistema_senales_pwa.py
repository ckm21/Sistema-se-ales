import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Señales de Velas", layout="wide")

# --- LOGO O IMAGEN DE INICIO ---
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Green_Sea_Turtle_2.jpg/320px-Green_Sea_Turtle_2.jpg", width=100)

# --- TÍTULO PRINCIPAL ---
st.title("🐢 Estrategia de Velas Japonesas")
st.markdown("Versión 2.0 – Monitoreo de señales de entrada y salida según velas japonesas y tendencias.")

# --- ENTRADA DE TICKER Y DATOS ---
ticker = st.text_input("📈 Ingresa el ticker:", value="AMD").upper()
interval = st.selectbox("⏱️ Intervalo de tiempo", options=["1m", "5m", "15m", "1h", "4h", "1d"], index=4)

end_date = datetime.now()
start_date = end_date - timedelta(days=10)

if ticker:
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        df.dropna(inplace=True)
    except Exception as e:
        st.error(f"Error al descargar los datos: {e}")
        st.stop()

    # --- DETECCIÓN DE TENDENCIA ---
    def detectar_tendencia(data):
        ultimos_cierres = data['Close'].tail(5)
        if ultimos_cierres.is_monotonic_increasing:
            return "📈 Alcista"
        elif ultimos_cierres.is_monotonic_decreasing:
            return "📉 Bajista"
        else:
            return "🔄 Lateral"

    # --- DETECCIÓN DE SEÑALES ---
    def detectar_senales(data):
        señales = []
        for i in range(1, len(data)):
            open_ = data['Open'].iloc[i]
            close = data['Close'].iloc[i]
            prev_close = data['Close'].iloc[i-1]
            high = data['High'].iloc[i]
            low = data['Low'].iloc[i]

            cuerpo = abs(close - open_)
            mecha = high - low

            if cuerpo < mecha * 0.2:
                señales.append(("⚠️ Doji", i))
            elif close > open_ and cuerpo > mecha * 0.6 and close > prev_close:
                señales.append(("🟢 Señal de Compra", i))
            elif open_ > close and cuerpo > mecha * 0.6 and close < prev_close:
                señales.append(("🔴 Señal de Venta", i))
        return señales

    señales = detectar_senales(df)
    tendencia = detectar_tendencia(df)

    # --- GRAFICAR CON PLOTLY ---
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='green',
        decreasing_line_color='red'
    )])

    # --- MOSTRAR NOTIFICACIONES ---
    ultima_senal = señales[-1][0] if señales else "Sin señal clara"
    if "Compra" in ultima_senal:
        st.success(f"✅ Opción de compra detectada: {ultima_senal}")
    elif "Venta" in ultima_senal:
        st.warning(f"⚠️ Riesgo de pérdida: {ultima_senal}")
    elif "Doji" in ultima_senal:
        st.info(f"📍 Indecisión del mercado: {ultima_senal}")
    else:
        st.info("Sin señales relevantes en la última vela.")

    # --- MOSTRAR GRÁFICO ---
    st.plotly_chart(fig, use_container_width=True)

    # --- TABLA DE DATOS Y SEÑALES ---
    st.subheader("📊 Señales detectadas")
    if señales:
        df_señales = pd.DataFrame(señales, columns=["Señal", "Index"])
        df_señales["Fecha"] = df.index[df_señales["Index"]].values
        st.dataframe(df_señales[["Fecha", "Señal"]])
    else:
        st.write("No se detectaron señales claras.")

    # --- DETALLE DE TENDENCIA ---
    st.markdown(f"### Tendencia detectada: **{tendencia}**")

    # --- ESTRATEGIA ---
    with st.expander("📘 Estrategia aplicada"):
        st.markdown("""
        **Compra:**
        - Velas con cuerpo fuerte y cierre mayor al anterior.
        - Contexto de tendencia alcista o inicio de impulso tras consolidación.

        **Venta:**
        - Cuerpos bajistas consecutivos o con cierre por debajo del anterior.
        - Mechas largas en velas verdes (señal de agotamiento).
        - Presión vendedora tras subida rápida.

        **Doji:**
        - Señal de pausa o indecisión. Evitar operar en esa zona.

        **Tendencia:**
        - Si es alcista se pueden mantener posiciones.
        - Si es bajista, solo operar con rebotes tácticos bien definidos.
        """)
