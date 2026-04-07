"""
Crypto Analyzer - Panel de Análisis de Criptomonedas
=====================================================
Aplicación Streamlit para analizar criptomonedas con datos de mercado,
métricas on-chain, noticias y fundamentales.

Autor: Crypto Analyzer
Fecha: 2026
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import sys
import os
import pandas as pd

# Añadir path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos
from api.coingecko import CoinGeckoClient
from modules.market import render_market_dashboard
from modules.onchain import render_onchain_dashboard
from modules.news import render_news_dashboard
from modules.fundamentals import render_fundamentals_dashboard

# ====================
# CONFIGURACIÓN
# ====================

st.set_page_config(
    page_title="Crypto Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": """
        ## Crypto Analyzer Pro
        
        Panel de análisis completo de criptomonedas.
        
        Datos proporcionados por CoinGecko API.
        """,
        "Get Help": "https://www.coingecko.com/api",
    }
)

# ====================
# INICIALIZAR API
# ====================

@st.cache_resource
def get_api_client():
    """Inicializa el cliente de API"""
    return CoinGeckoClient(rate_limit=50)

api_client = get_api_client()

# ====================
# TÍTULO PRINCIPAL
# ====================

st.title("📊 Crypto Analyzer Pro")
st.markdown("### Análisis completo de criptomonedas")

# Auto-refresh cada 60 segundos
st_autorefresh(interval=60000, limit=None, key="main_refresh")

# ====================
# BARRA LATERAL
# ====================

with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Auto-refresh toggle
    auto_refresh = st.toggle("Auto-refresh (1 min)", value=True)
    
    st.divider()
    
    # Información del proyecto
    st.header("ℹ️ Información")
    
    st.markdown("""
    **Fuentes de datos:**
    - CoinGecko API
    
    **Datos disponibles:**
    - 📊 Mercado
    - ⛓️ On-chain
    - 📰 Noticias
    - 💰 Fundamentales
    """)
    
    st.divider()
    
    # Estado de la API
    try:
        test = api_client.get_price(["bitcoin"])
        if test and len(test) > 0:
            st.success("✅ API Conectada")
        else:
            st.warning("⚠️ API no responde")
    except Exception as e:
        st.error(f"❌ Error: {str(e)[:50]}")
    
    st.divider()
    
    st.caption("© 2026 Crypto Analyzer Pro")

# ====================
# PÁGINAS DEL DASHBOARD
# ====================

# Crear tabs para navegación
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Mercado",
    "⛓️ On-Chain", 
    "📰 Noticias",
    "💰 Fundamentales"
])

with tab1:
    render_market_dashboard(api_client)

with tab2:
    render_onchain_dashboard(api_client)

with tab3:
    render_news_dashboard(api_client)

with tab4:
    render_fundamentals_dashboard(api_client)

# ====================
# FOOTER
# ====================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("💡 *Este análisis es informativo y no constituye advice financiero.")

with col2:
    st.caption(f"🕐 Actualizado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col3:
    st.caption("📈 Datos: CoinGecko API")
