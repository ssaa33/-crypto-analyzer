"""
Módulo de Métricas On-Chain
Recopila y procesa métricas on-chain de criptomonedas
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional


class OnChainData:
    """Clase para gestionar métricas on-chain"""
    
    def __init__(self, api_client):
        self.api = api_client
    
    def get_coin_onchain(self, coin_id: str) -> Dict:
        """Obtiene datos on-chain básicos de una moneda"""
        detail = self.api.get_coin_detail(coin_id)
        
        if not detail:
            return {}
        
        market_data = detail.get("market_data", {})
        
        return {
            "current_price": market_data.get("current_price", {}).get("usd", 0),
            "market_cap": market_data.get("market_cap", {}).get("usd", 0),
            "total_volume": market_data.get("total_volume", {}).get("usd", 0),
            "high_24h": market_data.get("high_24h", {}).get("usd", 0),
            "low_24h": market_data.get("low_24h", {}).get("usd", 0),
            "price_change_24h": market_data.get("price_change_24h", 0),
            "price_change_percentage_24h": market_data.get("price_change_percentage_24h", 0),
            "price_change_percentage_7d": market_data.get("price_change_percentage_7d", 0),
            "price_change_percentage_30d": market_data.get("price_change_percentage_30d", 0),
            "circulating_supply": market_data.get("circulating_supply", 0),
            "total_supply": market_data.get("total_supply", 0),
            "max_supply": market_data.get("max_supply", 0),
            "ath": market_data.get("ath", {}).get("usd", 0),
            "ath_change_percentage": market_data.get("ath_change_percentage", {}).get("usd", 0),
            "atl": market_data.get("atl", {}).get("usd", 0),
            "atl_change_percentage": market_data.get("atl_change_percentage", {}).get("usd", 0),
            "last_updated": market_data.get("last_updated", "")
        }
    
    def get_historical_volatility(self, coin_id: str, days: int = 30) -> Dict:
        """Calcula volatilidad histórica"""
        history = self.api.get_history(coin_id, days)
        
        if not history or "prices" not in history:
            return {}
        
        prices = [p[1] for p in history["prices"]]
        
        if len(prices) < 2:
            return {}
        
        # Calcular retornos diarios
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        
        # Calcular volatilidad (desviación estándar anualizada)
        import statistics
        if returns:
            volatility = statistics.stdev(returns) * (365 ** 0.5) * 100
            
            return {
                "volatility_30d": volatility,
                "avg_daily_return": statistics.mean(returns) * 100,
                "max_daily_loss": min(returns) * 100,
                "max_daily_gain": max(returns) * 100,
                "days_analyzed": len(returns)
            }
        
        return {}
    
    def get_supply_analysis(self, coin_id: str) -> Dict:
        """Analiza oferta de la moneda"""
        data = self.get_coin_onchain(coin_id)
        
        circulating = data.get("circulating_supply", 0)
        total = data.get("total_supply", 0)
        max_supply = data.get("max_supply", 0)
        
        return {
            "circulating_supply": circulating,
            "total_supply": total,
            "max_supply": max_supply,
            "supply_ratio": (circulating / total * 100) if total > 0 else 0,
            "max_supply_ratio": (circulating / max_supply * 100) if max_supply and max_supply > 0 else 0,
            "unreleased_supply": (total - circulating) if total > 0 else 0
        }
    
    def analyze_price_action(self, coin_id: str, days: int = 90) -> Dict:
        """Analiza acción del precio"""
        history = self.api.get_history(coin_id, days)
        
        if not history or "prices" not in history:
            return {}
        
        prices = [p[1] for p in history["prices"]]
        
        if len(prices) < 2:
            return {}
        
        first_price = prices[0]
        last_price = prices[-1]
        max_price = max(prices)
        min_price = min(prices)
        
        total_return = ((last_price - first_price) / first_price) * 100
        
        # Análisis de tendencias
        up_days = sum(1 for i in range(1, len(prices)) if prices[i] > prices[i-1])
        down_days = sum(1 for i in range(1, len(prices)) if prices[i] < prices[i-1])
        
        return {
            "total_return": total_return,
            "first_price": first_price,
            "last_price": last_price,
            "max_price": max_price,
            "min_price": min_price,
            "up_days": up_days,
            "down_days": down_days,
            "neutral_days": len(prices) - up_days - down_days,
            "trend_strength": ((up_days - down_days) / len(prices)) * 100 if len(prices) > 0 else 0
        }


def render_onchain_dashboard(api_client):
    """Renderiza el dashboard on-chain"""
    st.header("⛓️ Métricas On-Chain")
    
    onchain = OnChainData(api_client)
    
    # Selector de moneda
    coins = [
        "bitcoin", "ethereum", "binancecoin", "solana", "cardano",
        "ripple", "polkadot", "dogecoin", "avalanche-2", "chainlink"
    ]
    
    selected_coin = st.selectbox(
        "Seleccionar Criptomoneda",
        coins,
        format_func=lambda x: x.title()
    )
    
    # Datos on-chain
    st.subheader(f"📈 Análisis de {selected_coin.title()}")
    
    data = onchain.get_coin_onchain(selected_coin)
    
    if data:
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Precio Actual",
                f"${data.get('current_price', 0):,.2f}",
                f"{data.get('price_change_percentage_24h', 0):.2f}%"
            )
        
        with col2:
            st.metric(
                "Market Cap",
                f"${data.get('market_cap', 0):,.0f}"[:20]
            )
        
        with col3:
            st.metric(
                "Volumen 24h",
                f"${data.get('total_volume', 0):,.0f}"[:20]
            )
        
        with col4:
            st.metric(
                "Dominancia",
                f"{data.get('price_change_percentage_7d', 0):.2f}%"
            )
        
        st.divider()
        
        # Análisis de ciclo
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Ciclo de Precios")
            cycles = onchain.analyze_price_action(selected_coin, 90)
            
            if cycles:
                st.metric(
                    "Retorno Total (90d)",
                    f"{cycles.get('total_return', 0):.2f}%"
                )
                st.metric(
                    "Precio Máximo",
                    f"${cycles.get('max_price', 0):,.2f}"
                )
                st.metric(
                    "Precio Mínimo",
                    f"${cycles.get('min_price', 0):,.2f}"
                )
                st.metric(
                    "Fuerza de Tendencia",
                    f"{cycles.get('trend_strength', 0):.1f}%"
                )
        
        with col2:
            st.subheader("💰 Análisis de Supply")
            supply = onchain.get_supply_analysis(selected_coin)
            
            if supply:
                st.metric(
                    "Supply Circulante",
                    f"{supply.get('circulating_supply', 0):,.0f}"
                )
                st.metric(
                    "Supply Total",
                    f"{supply.get('total_supply', 0):,.0f}"[:20]
                )
                st.metric(
                    "Supply Máximo",
                    f"{supply.get('max_supply', 0):,.0f}"[:20] if supply.get('max_supply') else "∞"
                )
                st.metric(
                    "% Circulando",
                    f"{supply.get('supply_ratio', 0):.1f}%"
                )
        
        st.divider()
        
        # Histórico
        st.subheader("📉 Histórico de Precios")
        
        history = onchain.get_historical_volatility(selected_coin, 30)
        
        if history:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Volatilidad Anualizada",
                    f"{history.get('volatility_30d', 0):.1f}%"
                )
            
            with col2:
                st.metric(
                    "Retorno Diario Promedio",
                    f"{history.get('avg_daily_return', 0):.2f}%"
                )
            
            with col3:
                st.metric(
                    "Mejor Día",
                    f"+{history.get('max_daily_gain', 0):.2f}%"
                )
    
    st.divider()
    
    # Comparación entre monedas
    st.subheader("⚖️ Comparación de Principales Criptomonedas")
    
    comparison_data = []
    
    progress_bar = st.progress(0)
    
    for i, coin in enumerate(coins[:6]):
        progress_bar.progress((i + 1) / 6)
        
        coin_data = onchain.get_coin_onchain(coin)
        
        if coin_data:
            comparison_data.append({
                "Moneda": coin.title(),
                "Precio": coin_data.get("current_price", 0),
                "Cambio 24h": coin_data.get("price_change_percentage_24h", 0),
                "Cambio 7d": coin_data.get("price_change_percentage_7d", 0),
                "Cambio 30d": coin_data.get("price_change_percentage_30d", 0),
                "Market Cap": coin_data.get("market_cap", 0)
            })
    
    progress_bar.empty()
    
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        
        st.dataframe(
            df,
            column_config={
                "Precio": st.column_config.NumberColumn(
                    "Precio ($)",
                    format="$%.2f"
                ),
                "Cambio 24h": st.column_config.NumberColumn(
                    "24h %",
                    format="+%.2f%"
                ),
                "Cambio 7d": st.column_config.NumberColumn(
                    "7d %",
                    format="+%.2f%"
                ),
                "Cambio 30d": st.column_config.NumberColumn(
                    "30d %",
                    format="+%.2f%"
                ),
            },
            hide_index=True,
            use_container_width=True
        )
