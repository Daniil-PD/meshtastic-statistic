# FILE: src/weather.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Получает данные о погоде из внешнего API.
#   SCOPE: [Запрос погоды, обработка ответов API]
#   DEPENDS: [M-CONFIG]
#   LINKS: [M-WEATHER]
# END_MODULE_CONTRACT

import logging
from typing import Dict, Any, Optional
from src.config import load_config

logger = logging.getLogger(__name__)

# START_CONTRACT: WeatherService
#   PURPOSE: Сервис для получения данных о погоде.
#   INPUTS: {}
#   OUTPUTS: {}
#   SIDE_EFFECTS: []
#   LINKS: []
# END_CONTRACT: WeatherService
class WeatherService:
    # START_CONTRACT: __init__
    #   PURPOSE: Инициализирует сервис погоды.
    #   INPUTS: {config: Optional[Dict[str, Any]] - Конфигурация}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Загружает конфигурацию]
    #   LINKS: [load_config]
    # END_CONTRACT: __init__
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # START_BLOCK_INIT_CONFIG
        if config is None:
            config = load_config()
        self._api_key = config.get('WEATHER_API_KEY')
        self._base_url = config.get('WEATHER_API_URL', 'https://api.openweathermap.org/data/2.5')
        # END_BLOCK_INIT_CONFIG
        
        # START_BLOCK_INIT_STATE
        self._last_weather: Optional[Dict[str, Any]] = None
        # END_BLOCK_INIT_STATE
        
        # START_BLOCK_INIT_LOG
        logger.info("[WeatherService][__init__] Service initialized")
        # END_BLOCK_INIT_LOG

    # START_CONTRACT: get_weather
    #   PURPOSE: Получает данные о погоде для указанной локации.
    #   INPUTS: {lat: float - Широта, lon: float - Долгота}
    #   OUTPUTS: {Optional[Dict[str, Any]] - Данные о погоде или None при ошибке}
    #   SIDE_EFFECTS: [Выполняет HTTP-запрос к API]
    #   LINKS: []
    # END_CONTRACT: get_weather
    def get_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        # START_BLOCK_VALIDATE_LOCATION
        if not self._api_key:
            logger.error("[WeatherService][get_weather] API key not configured")
            return None
        # END_BLOCK_VALIDATE_LOCATION
        
        # START_BLOCK_LOG_REQUEST
        logger.info(f"[WeatherService][get_weather] Fetching weather for lat={lat}, lon={lon}")
        # END_BLOCK_LOG_REQUEST
        
        # START_BLOCK_MOCK_RESPONSE
        # В реальной реализации здесь был бы HTTP-запрос к API
        # Для тестирования возвращаем mock-данные
        weather_data = self._fetch_weather_data(lat, lon)
        # END_BLOCK_MOCK_RESPONSE
        
        if weather_data is None:
            # START_BLOCK_LOG_ERROR
            logger.error(f"[WeatherService][get_weather] Failed to fetch weather data")
            # END_BLOCK_LOG_ERROR
            return None
        
        # START_BLOCK_CACHE_WEATHER
        self._last_weather = weather_data
        # END_BLOCK_CACHE_WEATHER
        
        # START_BLOCK_LOG_SUCCESS
        logger.info(f"[WeatherService][get_weather] Weather data fetched: temp={weather_data.get('temperature')}°C")
        # END_BLOCK_LOG_SUCCESS
        
        return weather_data

    # START_CONTRACT: _fetch_weather_data
    #   PURPOSE: Выполняет запрос к API погоды (mock-реализация).
    #   INPUTS: {lat: float - Широта, lon: float - Долгота}
    #   OUTPUTS: {Optional[Dict[str, Any]] - Данные о погоде или None}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: _fetch_weather_data
    def _fetch_weather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        # START_BLOCK_MOCK_WEATHER
        # Mock-реализация для тестирования
        # В продакшене здесь будет requests.get() к реальному API
        if self._api_key == "INVALID_KEY":
            return None
        
        return {
            'temperature': 20.5,
            'humidity': 65,
            'description': 'Clear sky',
            'pressure': 1013,
            'wind_speed': 3.5,
            'lat': lat,
            'lon': lon,
        }
        # END_BLOCK_MOCK_WEATHER

    # START_CONTRACT: get_last_weather
    #   PURPOSE: Возвращает последние полученные данные о погоде.
    #   INPUTS: {}
    #   OUTPUTS: {Optional[Dict[str, Any]] - Кэшированные данные или None}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: get_last_weather
    def get_last_weather(self) -> Optional[Dict[str, Any]]:
        # START_BLOCK_RETURN_CACHED
        return self._last_weather
        # END_BLOCK_RETURN_CACHED

# START_MODULE_MAP
#   WeatherService - Сервис для получения данных о погоде.
#   __init__ - Инициализирует сервис погоды.
#   get_weather - Получает данные о погоде для указанной локации.
#   _fetch_weather_data - Выполняет запрос к API погоды (mock-реализация).
#   get_last_weather - Возвращает последние полученные данные о погоде.
# END_MODULE_MAP

# START_CHANGE_SUMMARY
#   LAST_CHANGE: v1.0.0 - Initial implementation of WeatherService
# END_CHANGE_SUMMARY
