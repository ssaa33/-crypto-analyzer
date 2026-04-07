"""
Módulo de Datos de Mercado
Recopila y procesa datos de mercado de criptomonedas
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime


class MarketData:
    """Clase para gestionar datos de mercado"""
    
    def __init__(self, api_client):
        self.api = api_client
        self.popular_coins = [
            "bitcoin", "ethereum", "binancecoin", "solana", "cardano",
            "ripple", "polkadot", "dogecoin", "avalanche-2", "chainlink",
            "polygon", "litecoin", "uniswap", "cosmos", "stellar"
        ]
    
    def get_top_coins(self, limit: int = 50) -> pd.DataFrame:
        """Obtiene las principales monedas por market cap"""
        markets = self.api.get_markets(per_page=limit)
        
        if not markets:
            return pd.DataFrame()
        
        df = pd.DataFrame(markets)
        
        # Seleccionar columnas relevantes
        cols = [
            'name', 'symbol', 'current_price', 'market_cap', 'market_cap_rank',
            'total_volume', 'price_change_percentage_24h', 
            'price_change_percentage_7d_in_currency',
            'price_change_percentage_30d_in_currency',
            'circulating_supply', 'total_supply', 'max_supply',
            'ath', 'ath_change_percentage', 'atl', 'atl_change_percentage',
            'sparkline_in_7d'
        ]
        
        # Filtrar solo columnas existentes
        existing_cols = [c for c in cols if c in df.columns]
        df = df[existing_cols]
        
        # Formatear
        if 'symbol' in df.columns:
            df['symbol'] = df['symbol'].str.upper()
        
        if 'name' in df.columns:
            df['name'] = df['name'].str[:20]  # Acortar nombres largos
        
        return df
    
    def get_coin_price(self, coin_id: str) -> Optional[Dict]:
        """Obtiene precio actual de una moneda"""
        data = self.api.get_price([coin_id])
        
        if data and coin_id in data:
            return data[coin_id]
        return None
    
    def get_market_summary(self) -> Dict:
        """Obtiene resumen del mercado global"""
        global_data = self.api.get_global_data()
        
        if not global_data:
            return {}
        
        data = global_data.get("data", {})
        
        return {
            "total_market_cap": data.get("total_market_cap", 0),
            "total_volume": data.get("total_volume", 0),
            "btc_dominance": data.get("market_cap_percentage", {}).get("btc", 0),
            "eth_dominance": data.get("market_cap_percentage", {}).get("eth", 0),
            "active_cryptocurrencies": data.get("active_cryptocurrencies", 0),
            "markets": data.get("markets", 0)
        }
    
    def calculate_cycles(self, coin_id: str, days: int = 365) -> Dict:
        """Calcula ciclos históricos de una moneda"""
        history = self.api.get_history(coin_id, days)
        
        if not history or "prices" not in history:
            return {}
        
        prices = history["prices"]
        
        if not prices:
            return {}
        
        # Calcular estadísticas
        price_values = [p[1] for p in prices]
        
        current_price = price_values[-1]
        max_price = max(price_values)
        min_price = min(price_values)
        avg_price = sum(price_values) / len(price_values)
        
        # Días desde ATH
        ath_price = max_price
        
        return {
            "current_price": current_price,
            "max_price": max_price,
            "min_price": min_price,
            "avg_price": avg_price,
            "ath_price": ath_price,
            "distance_from_ath": ((current_price - ath_price) / ath_price) * 100,
            "volatility": ((max_price - min_price) / avg_price) * 100,
            "days_analyzed": len(prices)
        }
    
    def format_market_cap(self, value: float) -> str:
        """Formatea market cap de forma legible"""
        if value >= 1e12:
            return f"${value/1e12:.2f}T"
        elif value >= 1e9:
            return f"${value/1e9:.2f}B"
        elif value >= 1e6:
            return f"${value/1e6:.2f}M"
        elif value >= 1e3:
            return f"${value/1e3:.2f}K"
        else:
            return f"${value:.2f}"
    
    def format_percentage(self, value: float) -> str:
        """Formatea porcentaje con color"""
        if value > 0:
            return f"+{value:.2f}%"
        elif value < 0:
            return f"{value:.2f}%"
        else:
            return "0.00%"
    
    def get_trending_coins(self) -> List[Dict]:
        """Obtiene monedas en tendencia"""
        trending = self.api.get_trending()
        
        if not trending:
            return []
        
        return trending.get("coins", [])[:15]


def render_market_dashboard(api_client):
    """Renderiza el dashboard de mercado"""
    st.header("📊 Datos de Mercado")
    
    market = MarketData(api_client)
    
    # Resumen global
    st.subheader("🌍 Resumen Global del Mercado")
    summary = market.get_market_summary()
    
    if summary:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Market Cap Total",
                market.format_market_cap(summary.get("total_market_cap", 0))
            )
        
        with col2:
            st.metric(
                "Volumen 24h",
                market.format_market_cap(summary.get("total_volume", 0))
            )
        
        with col3:
            st.metric(
                "Dominancia BTC",
                f"{summary.get('btc_dominance', 0):.1f}%"
            )
        
        with col4:
            st.metric(
                "Criptomonedas",
                f"{summary.get('active_cryptocurrencies', 0):,}"
            )
    
    st.divider()
    
    # Top monedas
    st.subheader("🏆 Top 50 Criptomonedas")
    
    df = market.get_top_coins(50)
    
    if not df.empty:
        # Columnas para filtrar
        col1, col2 = st.columns([1, 3])
        
        with col1:
            sort_by = st.selectbox(
                "Ordenar por",
                ["market_cap", "current_price", "price_change_percentage_24h"],
                format_func=lambda x: {
                    "market_cap": "Market Cap",
                    "current_price": "Precio",
                    "price_change_percentage_24h": "Cambio 24h"
                }.get(x, x)
            )
        
        # Ordenar
        if sort_by in df.columns:
            df = df.sort_values(sort_by, ascending=False)
        
        # Mostrar dataframe
        st.dataframe(
            df,
            column_config={
                "current_price": st.column_config.NumberColumn(
                    "Precio ($)",
                    format="$%.2f"
                ),
                "market_cap": st.column_config.NumberColumn(
                    "Market Cap",
                    format=market.format_market_cap
                ),
                "price_change_percentage_24h": st.column_config.NumberColumn(
                    "24h %",
                    format=market.format_percentage
                ),
                "price_change_percentage_7d_in_currency": st.column_config.NumberColumn(
                    "7d %",
                    format=market.format_percentage
                ),
                "price_change_percentage_30d_in_currency": st.column_config.NumberColumn(
                    "30d %",
                    format=market.format_percentage
                ),
            },
            hide_index=True,
            use_container_width=True,
            height=400
        )
    
    st.divider()
    
    # Tendencias
    st.subheader("🔥 Monedas en Tendencia")
    
    trending = market.get_trending_coins()
    
    if trending:
        cols = st.columns(5)
        
        for i, coin in enumerate(trending[:10]):
            with cols[i % 5]:
                item = coin.get("item", {})
                st.image(
                    item.get("small", ""),
                    width=30
                )
                st.caption(
                    f"**{item.get('name', '')}**\n"
                    f"{item.get('symbol', '').upper()}"
                )
