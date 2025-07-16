import streamlit as st
import pandas as pd

# ========================
# Datos simulados de ejemplo
# ========================
datos = {
    "Fecha": ["2025-07-15", "2025-07-16", "2025-07-17"],
    "Open": [150.0, 152.0, 151.0],
    "High": [155.0, 153.0, 156.0],
    "Low": [148.0, 150.0, 149.5],
    "Close": [154.5, 150.5, 155.5]
}
df = pd.DataFrame(datos)
df.set_index("Fecha", inplace=True)

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
# Análisis de patrones
# ========================

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

st.title("📊 Sistema de Señales por Velas Japonesas (Versión Local)")
st.markdown("Este sistema usa un ejemplo simulado para detectar patrones clásicos de velas.")

st.dataframe(df)

resultado = analizar_df(df)

if resultado.empty:
    st.info("No se detectaron señales.")
else:
    st.success("Señales detectadas:")
    st.dataframe(resultado)
