"""
CoinGecko API Client
Cliente para interactuar con la API de CoinGecko
"""

import time
import requests
from typing import Optional, Dict, List, Any


class CoinGeckoClient:
    """Cliente para la API de CoinGecko"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, rate_limit: int = 10):
        """
        Inicializa el cliente
        
        Args:
            rate_limit: Llamadas por minuto permitidas (default 10)
        """
        self.rate_limit = rate_limit
        self.last_call = 0
        self.calls_this_minute = 0
        self.minute_start = time.time()
    
    def _rate_limit_wait(self):
        """Implementa el control de rate limiting"""
        current_time = time.time()
        
        # Resetear contador cada minuto
        if current_time - self.minute_start >= 60:
            self.calls_this_minute = 0
            self.minute_start = current_time
        
        # Esperar si alcanzamos el límite
        if self.calls_this_minute >= self.rate_limit:
            wait_time = 60 - (current_time - self.minute_start)
            if wait_time > 0:
                time.sleep(wait_time)
            self.calls_this_minute = 0
            self.minute_start = time.time()
        
        # Pequeño delay entre llamadas
        if self.last_call > 0:
            time.sleep(1.2)  #~50 calls/min max con este delay
        
        self.last_call = time.time()
        self.calls_this_minute += 1
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Método interno para hacer requests"""
        self._rate_limit_wait()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en request: {e}")
            return None
    
    # ====================
    # MÉTODOS DE MARKET
    # ====================
    
    def get_price(self, ids: List[str], currencies: List[str] = ["usd"]) -> Optional[Dict]:
        """
        Obtiene precios de criptomonedas
        
        Args:
            ids: Lista de IDs de coins (e.g., ['bitcoin', 'ethereum'])
            currencies: Monedas objetivo (default: ['usd'])
        """
        params = {
            "ids": ",".join(ids),
            "vs_currencies": ",".join(currencies),
            "include_24hr_change": True,
            "include_24hr_vol": True,
            "include_market_cap": True
        }
        return self._get("/simple/price", params)
    
    def get_markets(self, currency: str = "usd", per_page: int = 100, 
                   page: int = 1, order: str = "market_cap_desc") -> Optional[List[Dict]]:
        """
        Obtiene lista de mercados
        
        Args:
            currency: Moneda (default: usd)
            per_page: Resultados por página (max 250)
            page: Página
            order: Ordenamiento
        """
        params = {
            "vs_currency": currency,
            "per_page": per_page,
            "page": page,
            "order": order,
            "sparkline": True,
            "price_change_percentage": "1h,24h,7d,30d,1y"
        }
        return self._get("/coins/markets", params)
    
    def get_coin_detail(self, coin_id: str) -> Optional[Dict]:
        """
        Obtiene detalles de una criptomoneda
        """
        params = {
            "localization": False,
            "tickers": False,
            "market_data": True,
            "community_data": True,
            "developer_data": True,
            "sparkline": True
        }
        return self._get(f"/coins/{coin_id}", params)
    
    def get_global_data(self) -> Optional[Dict]:
        """Obtiene datos globales del mercado"""
        return self._get("/global")
    
    def get_trending(self) -> Optional[Dict]:
        """Obtiene monedas en tendencia"""
        return self._get("/search/trending")
    
    # ====================
    # MÉTODOS ON-CHAIN
    # ====================
    
    def get_history(self, coin_id: str, days: int = 7) -> Optional[Dict]:
        """
        Obtiene historial de precios
        
        Args:
            coin_id: ID de la moneda
            days: Días de historial
        """
        params = {
            "days": days,
            "interval": "daily"
        }
        return self._get(f"/coins/{coin_id}/market_chart", params)
    
    # ====================
    # MÉTODOS DE NEWS
    # ====================
    
    def get_news(self) -> Optional[List[Dict]]:
        """Obtiene últimas noticias (a través de CoinGecko trending)"""
        trending = self.get_trending()
        if trending:
            return trending.get("coins", [])[:10]
        return None
    
    # ====================
    # MÉTODOS DE SEARCH
    # ====================
    
    def search(self, query: str) -> Optional[Dict]:
        """Busca monedas por nombre/símbolo"""
        params = {"query": query}
        return self._get("/search", params)
    
    def get_coins_list(self) -> Optional[List[Dict]]:
        """Obtiene lista completa de monedas disponibles"""
        return self._get("/coins/list")
