"""
Módulo de Noticias y Sentimiento
Recopila y procesa noticias de criptomonedas
"""

import streamlit as st
import pandas as pd
from typing import List, Dict


class NewsData:
    """Clase para gestionar noticias"""
    
    def __init__(self, api_client):
        self.api = api_client
    
    def get_breaking_news(self) -> List[Dict]:
        """Obtiene noticias de última hora"""
        trending = self.api.get_trending()
        
        if not trending:
            return []
        
        # Noticias basadas en tendencias
        news = []
        for coin in trending.get("coins", [])[:20]:
            item = coin.get("item", {})
            
            # Simular datos de noticia basados en el coin
            news.append({
                "title": f"{item.get('name', '')} está en tendencia",
                "source": "CoinGecko Trends",
                "coin": item.get("name", ""),
                "symbol": item.get("symbol", ""),
                "price_btc": item.get("price_btc", 0),
                "market_cap_rank": item.get("market_cap_rank", 0),
                "type": "trending"
            })
        
        return news
    
    def get_coin_news(self, coin_name: str) -> List[Dict]:
        """Obtiene noticias específicas de una moneda"""
        # Buscar coins relacionados
        search = self.api.search(coin_name)
        
        if not search:
            return []
        
        coins = search.get("coins", [])
        
        news = []
        for coin in coins[:10]:
            news.append({
                "name": coin.get("name", ""),
                "symbol": coin.get("symbol", ""),
                "market_cap_rank": coin.get("market_cap_rank", 0),
                "thumb": coin.get("thumb", ""),
                "large": coin.get("large", "")
            })
        
        return news
    
    def analyze_sentiment(self, coin_id: str) -> Dict:
        """Analiza el sentimiento basándose en datos disponibles"""
        detail = self.api.get_coin_detail(coin_id)
        
        if not detail:
            return {"sentiment": "neutral", "score": 0}
        
        # Analizar basándose en cambios de precio
        market_data = detail.get("market_data", {})
        
        change_24h = market_data.get("price_change_percentage_24h", 0)
        change_7d = market_data.get("price_change_percentage_7d", 0)
        
        # Calcular score de sentimiento
        sentiment_score = (change_24h * 0.4 + change_7d * 0.6) / 2
        
        if sentiment_score > 5:
            sentiment = "bullish"
        elif sentiment_score < -5:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": sentiment_score,
            "change_24h": change_24h,
            "change_7d": change_7d,
            "community_score": detail.get("community_score", 0),
            "developer_score": detail.get("developer_score", 0)
        }


def render_news_dashboard(api_client):
    """Renderiza el dashboard de noticias"""
    st.header("📰 Noticias y Sentimiento")
    
    news = NewsData(api_client)
    
    # Tendencias
    st.subheader("🔥 Tendencias Actuales")
    
    trending_news = news.get_breaking_news()
    
    if trending_news:
        for i, item in enumerate(trending_news[:10]):
            with st.expander(f"#{i+1} {item['coin']} - {item['symbol'].upper()}"):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.image(
                        item.get("large", ""),
                        width=50
                    )
                
                with col2:
                    st.markdown(f"**{item['title']}**")
                    st.caption(f"Ranking Market Cap: #{item['market_cap_rank']}")
                    st.caption(f"Fuente: {item['source']}")
    
    st.divider()
    
    # Análisis de sentimiento
    st.subheader("🎭 Análisis de Sentimiento")
    
    coins = [
        "bitcoin", "ethereum", "solana", "cardano", "binancecoin",
        "ripple", "polkadot", "dogecoin", "avalanche-2", "chainlink"
    ]
    
    selected_coin = st.selectbox(
        "Seleccionar Criptomoneda",
        coins,
        format_func=lambda x: x.title()
    )
    
    sentiment = news.analyze_sentiment(selected_coin)
    
    if sentiment:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sentiment_emoji = "🐂" if sentiment["sentiment"] == "bullish" else "🐻" if sentiment["sentiment"] == "bearish" else "😐"
            st.metric(
                "Sentimiento",
                f"{sentiment_emoji} {sentiment['sentiment'].upper()}"
            )
        
        with col2:
            st.metric(
                "Cambio 24h",
                f"{sentiment.get('change_24h', 0):.2f}%"
            )
        
        with col3:
            st.metric(
                "Cambio 7d",
                f"{sentiment.get('change_7d', 0):.2f}%"
            )
        
        st.progress(
            min(max((sentiment.get("score", 0) + 50) / 100, 0), 1),
            text=f"Score de Sentimiento: {sentiment.get('score', 0):.1f}"
        )
    
    st.divider()
    
    # Buscador de monedas
    st.subheader("🔍 Buscar Criptomoneda")
    
    search_query = st.text_input("Buscar por nombre o símbolo", "")
    
    if search_query:
        results = news.get_coin_news(search_query)
        
        if results:
            for coin in results:
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    st.image(coin.get("thumb", ""), width=30)
                
                with col2:
                    st.markdown(f"**{coin.get('name', '')}**")
                    st.caption(coin.get("symbol", "").upper())
                
                with col3:
                    st.caption(f"#{coin.get('market_cap_rank', 0)}")
        else:
            st.info("No se encontraron resultados")
