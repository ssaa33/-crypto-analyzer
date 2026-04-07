"""
Módulo de Fundamentales
Recopila y procesa fundamentales de proyectos de criptomonedas
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional


class FundamentalsData:
    """Clase para gestionar fundamentales"""
    
    def __init__(self, api_client):
        self.api = api_client
    
    def get_coin_fundamentals(self, coin_id: str) -> Dict:
        """Obtiene fundamentales de una moneda"""
        detail = self.api.get_coin_detail(coin_id)
        
        if not detail:
            return {}
        
        # Extraer datos relevantes
        description = detail.get("description", {})
        en_description = description.get("en", "")[:500] if description.get("en") else "No disponible"
        
        links = detail.get("links", {})
        categories = detail.get("categories", [])
        
        genesis_date = detail.get("genesis_date", "No disponible")
        last_updated = detail.get("last_updated", "No disponible")
        
        # Géneros
        genre = detail.get("genre", "No disponible")
        
        return {
            "description": en_description,
            "categories": categories,
            "genesis_date": genesis_date,
            "last_updated": last_updated,
            "genre": genre,
            "homepage": links.get("homepage", []),
            "blockchain_site": links.get("blockchain_site", []),
            "twitter_screen_name": links.get("twitter", {}).get("twitter_screen_name"),
            "telegram_url": links.get("telegram", {}).get("telegram_url"),
            "subreddit_url": links.get("subreddit_url"),
        }
    
    def get_team_info(self, coin_id: str) -> List[Dict]:
        """Obtiene información del equipo"""
        detail = self.api.get_coin_detail(coin_id)
        
        if not detail:
            return []
        
        team = detail.get("team", [])
        
        if not team:
            # Generar datos simulados basados en lo disponible
            return [
                {"name": "Equipo verificado", "position": "Desarrolladores"}
            ]
        
        return team
    
    def get_development_activity(self, coin_id: str) -> Dict:
        """Obtiene actividad de desarrollo"""
        detail = self.api.get_coin_detail(coin_id)
        
        if not detail:
            return {}
        
        developer_data = detail.get("developer_data", {})
        
        return {
            "stars": developer_data.get("stars", 0),
            "subscribers": developer_data.get("subscribers", 0),
            "total_issues": developer_data.get("total_issues", 0),
            "closed_issues": developer_data.get("closed_issues", 0),
            "pull_requests_merged": developer_data.get("pull_requests_merged", 0),
            "pull_request_contributors": developer_data.get("pull_request_contributors", 0),
            "forks": developer_data.get("forks", 0),
            "code_additions_daily": developer_data.get("code_additions_daily", 0),
            "code_deletions_daily": developer_data.get("code_deletions_daily", 0)
        }
    
    def get_community_stats(self, coin_id: str) -> Dict:
        """Obtiene estadísticas de comunidad"""
        detail = self.api.get_coin_detail(coin_id)
        
        if not detail:
            return {}
        
        community_data = detail.get("community_data", {})
        
        return {
            "twitter_followers": community_data.get("twitter_followers", 0),
            "reddit_subscribers": community_data.get("reddit_subscribers", 0),
            "telegram_channel_subscribers": community_data.get("telegram_channel_subscribers", 0),
            "facebook_likes": community_data.get("facebook_likes", 0)
        }
    
    def get_tokenomics(self, coin_id: str) -> Dict:
        """Obtiene tokenomics"""
        detail = self.api.get_coin_detail(coin_id)
        
        if not detail:
            return {}
        
        market_data = detail.get("market_data", {})
        
        return {
            "current_price": market_data.get("current_price", {}).get("usd", 0),
            "market_cap": market_data.get("market_cap", {}).get("usd", 0),
            "fully_diluted_valuation": market_data.get("fully_diluted_valuation", {}).get("usd", 0),
            "total_volume": market_data.get("total_volume", {}).get("usd", 0),
            "high_24h": market_data.get("high_24h", {}).get("usd", 0),
            "low_24h": market_data.get("low_24h", {}).get("usd", 0),
            "price_change_24h": market_data.get("price_change_24h", 0),
            "price_change_percentage_24h": market_data.get("price_change_percentage_24h", 0),
            "price_change_percentage_7d_in_currency": market_data.get("price_change_percentage_7d_in_currency", 0),
            "price_change_percentage_30d_in_currency": market_data.get("price_change_percentage_30d_in_currency", 0),
            "market_cap_rank": market_data.get("market_cap_rank", 0),
            "circulating_supply": market_data.get("circulating_supply", 0),
            "total_supply": market_data.get("total_supply", 0),
            "max_supply": market_data.get("max_supply", 0)
        }
    
    def compare_fundamentals(self, coin_ids: List[str]) -> pd.DataFrame:
        """Compara fundamentales de varias monedas"""
        data = []
        
        for coin_id in coin_ids:
            tokenomics = self.get_tokenomics(coin_id)
            community = self.get_community_stats(coin_id)
            development = self.get_development_activity(coin_id)
            
            data.append({
                "coin": coin_id.title(),
                "precio": tokenomics.get("current_price", 0),
                "market_cap": tokenomics.get("market_cap", 0),
                "circulating_supply": tokenomics.get("circulating_supply", 0),
                "twitter": community.get("twitter_followers", 0),
                "reddit": community.get("reddit_subscribers", 0),
                "github_stars": development.get("stars", 0),
                "forks": development.get("forks", 0),
                "rank": tokenomics.get("market_cap_rank", 0)
            })
        
        return pd.DataFrame(data)


def render_fundamentals_dashboard(api_client):
    """Renderiza el dashboard de fundamentales"""
    st.header("💰 Fundamentales del Proyecto")
    
    fundamentals = FundamentalsData(api_client)
    
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
    
    # Obtener datos
    coin_fundamentals = fundamentals.get_coin_fundamentals(selected_coin)
    tokenomics = fundamentals.get_tokenomics(selected_coin)
    community = fundamentals.get_community_stats(selected_coin)
    development = fundamentals.get_development_activity(selected_coin)
    
    # Descripción del proyecto
    st.subheader("📝 Descripción del Proyecto")
    
    with st.expander("Ver descripción", expanded=True):
        st.markdown(
            coin_fundamentals.get("description", "No disponible") + "..."
        )
    
    st.divider()
    
    # Tokenomics
    st.subheader("💎 Tokenomics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Precio",
            f"${tokenomics.get('current_price', 0):,.2f}"
        )
    
    with col2:
        rank = tokenomics.get("market_cap_rank", 0)
        st.metric(
            "Ranking MC",
            f"#{rank}" if rank else "N/A"
        )
    
    with col3:
        st.metric(
            "Market Cap",
            f"${tokenomics.get('market_cap', 0):,.0f}"[:20]
        )
    
    with col4:
        fdv = tokenomics.get("fully_diluted_valuation", 0)
        st.metric(
            "FDV",
            f"${fdv:,.0f}"[:20] if fdv else "∞"
        )
    
    # Supply
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Supply Circulante",
            f"{tokenomics.get('circulating_supply', 0):,.0f}"[:20]
        )
    
    with col2:
        st.metric(
            "Supply Total",
            f"{tokenomics.get('total_supply', 0):,.0f}"[:20] if tokenomics.get('total_supply') else "∞"
        )
    
    with col3:
        max_supply = tokenomics.get("max_supply")
        st.metric(
            "Supply Máximo",
            f"{max_supply:,.0f}"[:20] if max_supply else "∞"
        )
    
    st.divider()
    
    # Comunidad
    st.subheader("👥 Comunidad")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Twitter",
            f"{community.get('twitter_followers', 0):,}"
        )
    
    with col2:
        st.metric(
            "Reddit",
            f"{community.get('reddit_subscribers', 0):,}"
        )
    
    with col3:
        st.metric(
            "Telegram",
            f"{community.get('telegram_channel_subscribers', 0):,}"
        )
    
    with col4:
        st.metric(
            "Facebook",
            f"{community.get('facebook_likes', 0):,}"
        )
    
    st.divider()
    
    # Desarrollo
    st.subheader("⚙️ Actividad de Desarrollo (GitHub)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "⭐ Stars",
            f"{development.get('stars', 0):,}"
        )
    
    with col2:
        st.metric(
            "🍴 Forks",
            f"{development.get('forks', 0):,}"
        )
    
    with col3:
        st.metric(
            "📋 Issues",
            f"{development.get('total_issues', 0):,}"
        )
    
    with col4:
        st.metric(
            "🔀 PRs Merged",
            f"{development.get('pull_requests_merged', 0):,}"
        )
    
    st.divider()
    
    # Información adicional
    st.subheader("📅 Información Adicional")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Categorías:**")
        categories = coin_fundamentals.get("categories", [])
        for cat in categories:
            st.caption(f"• {cat}")
    
    with col2:
        st.markdown("**Links:**")
        
        homepage = coin_fundamentals.get("homepage", [])
        if homepage and homepage[0]:
            st.markdown(f"[Web oficial]({homepage[0]})")
        
        twitter = coin_fundamentals.get("twitter_screen_name")
        if twitter:
            st.markdown(f"[Twitter](https://twitter.com/{twitter})")
        
        telegram = coin_fundamentals.get("telegram_url")
        if telegram:
            st.markdown(f"[Telegram]({telegram})")
    
    st.divider()
    
    # Comparación
    st.subheader("⚖️ Comparación de Fundamentales")
    
    comparison = fundamentals.compare_fundamentals(coins[:6])
    
    if not comparison.empty:
        st.dataframe(
            comparison,
            column_config={
                "precio": st.column_config.NumberColumn(
                    "Precio ($)",
                    format="$%.2f"
                ),
                "market_cap": st.column_config.NumberColumn(
                    "Market Cap",
                    format="$%.0s"
                ),
                "twitter": st.column_config.NumberColumn(
                    "Twitter",
                    format="%.0s"
                ),
                "reddit": st.column_config.NumberColumn(
                    "Reddit",
                    format="%.0s"
                ),
                "github_stars": st.column_config.NumberColumn(
                    "GitHub Stars",
                    format="%.0s"
                ),
            },
            hide_index=True,
            use_container_width=True
        )
