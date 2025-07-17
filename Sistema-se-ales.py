
import streamlit as st

st.set_page_config(page_title="Velas Kame", layout="wide")

# Sidebar
st.sidebar.title("📊 Velas Kame")
menu = st.sidebar.radio("Selecciona una opción:", ["Inicio", "Favoritas"])

# Estado inicial en sesión
if "favoritas" not in st.session_state:
    st.session_state.favoritas = []

# Simulación de acciones disponibles
acciones_disponibles = ["AAPL", "NVDA", "WOLF", "AMD"]

if menu == "Inicio":
    st.title("🔥 Simulador básico de Velas Kame")
    for accion in acciones_disponibles:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**Acción:** {accion}")
        with col2:
            if accion not in st.session_state.favoritas:
                if st.button(f"⭐ Agregar {accion}", key=f"add_{accion}"):
                    st.session_state.favoritas.append(accion)
            else:
                if st.button(f"❌ Quitar {accion}", key=f"remove_{accion}"):
                    st.session_state.favoritas.remove(accion)

elif menu == "Favoritas":
    st.title("⭐ Tus acciones favoritas")
    if st.session_state.favoritas:
        for fav in st.session_state.favoritas:
            st.write(f"- {fav}")
    else:
        st.info("No has seleccionado acciones favoritas aún.")
