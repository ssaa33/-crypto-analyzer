# Crypto Analyzer Pro 📊

Analizador completo de criptomonedas con datos de mercado, métricas on-chain, noticias y fundamentales.

## 🚀 Despliegue Online

### Opción 1: Streamlit Community Cloud (Gratis)

1. Sube este proyecto a **GitHub**
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio de GitHub
4. Selecciona `main.py` como archivo principal
5. ¡Listo! Obtendrás un enlace público

### Opción 2: Ejecutar Localmente

```bash
# Clonar el proyecto
git clone <tu-repositorio>

# Instalar dependencias
cd crypto-analyzer
pip install -r requirements.txt

# Ejecutar
streamlit run main.py
```

## 📊 Características del Panel

| Sección | Descripción |
|---------|-------------|
| **📊 Mercado** | Top 50 criptos, market cap, volumen, tendencias, resúmenes globales |
| **⛓️ On-Chain** | Análisis de ciclos, supply, volatilidad, comparación entre monedas |
| **📰 Noticias** | Tendencias, sentimiento de mercado, búsqueda de monedas |
| **💰 Fundamentales** | Tokenomics, comunidad, desarrollo (GitHub), comparación |

## 🛠️ Tecnologías

- **Python** - Lenguaje principal
- **Streamlit** - Framework de dashboard
- **CoinGecko API** - Datos en tiempo real
- **Pandas** - Procesamiento de datos
- **Plotly** - Visualizaciones

## 📁 Estructura

```
crypto-analyzer/
├── main.py                    # Aplicación principal
├── requirements.txt           # Dependencias
├── .streamlit/
│   └── config.toml           # Configuración Streamlit
├── api/
│   └── coingecko.py          # Cliente API
└── modules/
    ├── market.py            # Datos de mercado
    ├── onchain.py           # Métricas on-chain
    ├── news.py              # Noticias
    └── fundamentals.py      # Fundamentales
```

## ⚠️ Disclaimer

Este proyecto es solo para fines informativos.
No constituye advice financiero.
Haz tu propia investigación antes de invertir.

---

*Desarrollado con ❤️*
