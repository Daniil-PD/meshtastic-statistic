# FILE: tests/unit/test_weather.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Модульные тесты для WeatherService.
#   SCOPE: [Тестирование инициализации, получения погоды, обработки ошибок]
#   DEPENDS: [M-WEATHER, M-CONFIG]
#   LINKS: [V-M-WEATHER]
# END_MODULE_CONTRACT

import pytest
from unittest.mock import patch, MagicMock
from src.weather import WeatherService

# START_CONTRACT: test_weather_service_init
#   PURPOSE: Проверяет инициализацию сервиса погоды.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [WeatherService.__init__]
# END_CONTRACT: test_weather_service_init
def test_weather_service_init():
    # START_BLOCK_TEST_INIT_WITH_CONFIG
    config = {'WEATHER_API_KEY': 'test_key', 'WEATHER_API_URL': 'https://test.api'}
    service = WeatherService(config)
    assert service._api_key == 'test_key'
    assert service._base_url == 'https://test.api'
    # END_BLOCK_TEST_INIT_WITH_CONFIG
    
    # START_BLOCK_TEST_INIT_DEFAULT_CONFIG
    with patch('src.weather.load_config') as mock_load:
        mock_load.return_value = {'WEATHER_API_KEY': 'default_key'}
        service2 = WeatherService()
        assert service2._api_key == 'default_key'
    # END_BLOCK_TEST_INIT_DEFAULT_CONFIG

# START_CONTRACT: test_get_weather_success
#   PURPOSE: Проверяет успешное получение данных о погоде.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [WeatherService.get_weather]
# END_CONTRACT: test_get_weather_success
def test_get_weather_success():
    # START_BLOCK_TEST_SUCCESSFUL_FETCH
    service = WeatherService({'WEATHER_API_KEY': 'valid_key'})
    weather = service.get_weather(lat=55.75, lon=37.62)
    
    assert weather is not None
    assert 'temperature' in weather
    assert 'humidity' in weather
    assert 'description' in weather
    assert weather['temperature'] == 20.5
    assert weather['humidity'] == 65
    # END_BLOCK_TEST_SUCCESSFUL_FETCH
    
    # START_BLOCK_TEST_CACHED_WEATHER
    last_weather = service.get_last_weather()
    assert last_weather == weather
    # END_BLOCK_TEST_CACHED_WEATHER

# START_CONTRACT: test_get_weather_no_api_key
#   PURPOSE: Проверяет обработку отсутствия API ключа.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [WeatherService.get_weather]
# END_CONTRACT: test_get_weather_no_api_key
def test_get_weather_no_api_key():
    # START_BLOCK_TEST_MISSING_API_KEY
    service = WeatherService({'WEATHER_API_KEY': None})
    weather = service.get_weather(lat=55.75, lon=37.62)
    
    assert weather is None
    # END_BLOCK_TEST_MISSING_API_KEY

# START_CONTRACT: test_get_weather_invalid_key
#   PURPOSE: Проверяет обработку невалидного API ключа.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [WeatherService.get_weather, WeatherService._fetch_weather_data]
# END_CONTRACT: test_get_weather_invalid_key
def test_get_weather_invalid_key():
    # START_BLOCK_TEST_INVALID_API_KEY
    service = WeatherService({'WEATHER_API_KEY': 'INVALID_KEY'})
    weather = service.get_weather(lat=55.75, lon=37.62)
    
    assert weather is None
    # END_BLOCK_TEST_INVALID_API_KEY

# START_CONTRACT: test_get_last_weather_empty
#   PURPOSE: Проверяет получение кэшированной погоды до первого запроса.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [WeatherService.get_last_weather]
# END_CONTRACT: test_get_last_weather_empty
def test_get_last_weather_empty():
    # START_BLOCK_TEST_EMPTY_CACHE
    service = WeatherService({'WEATHER_API_KEY': 'test_key'})
    assert service.get_last_weather() is None
    # END_BLOCK_TEST_EMPTY_CACHE

# START_CONTRACT: test_fetch_weather_data_mock
#   PURPOSE: Проверяет mock-реализацию запроса к API.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [WeatherService._fetch_weather_data]
# END_CONTRACT: test_fetch_weather_data_mock
def test_fetch_weather_data_mock():
    # START_BLOCK_TEST_MOCK_DATA_STRUCTURE
    service = WeatherService({'WEATHER_API_KEY': 'test_key'})
    weather = service._fetch_weather_data(lat=55.75, lon=37.62)
    
    assert weather is not None
    assert weather['lat'] == 55.75
    assert weather['lon'] == 37.62
    assert 'pressure' in weather
    assert 'wind_speed' in weather
    # END_BLOCK_TEST_MOCK_DATA_STRUCTURE
    
    # START_BLOCK_TEST_MOCK_INVALID_KEY
    service_invalid = WeatherService({'WEATHER_API_KEY': 'INVALID_KEY'})
    assert service_invalid._fetch_weather_data(lat=0, lon=0) is None
    # END_BLOCK_TEST_MOCK_INVALID_KEY

# START_MODULE_MAP
#   test_weather_service_init - Проверяет инициализацию сервиса погоды.
#   test_get_weather_success - Проверяет успешное получение данных о погоде.
#   test_get_weather_no_api_key - Проверяет обработку отсутствия API ключа.
#   test_get_weather_invalid_key - Проверяет обработку невалидного API ключа.
#   test_get_last_weather_empty - Проверяет получение кэшированной погоды до первого запроса.
#   test_fetch_weather_data_mock - Проверяет mock-реализацию запроса к API.
# END_MODULE_MAP

# START_CHANGE_SUMMARY
#   LAST_CHANGE: v1.0.0 - Initial tests for WeatherService
# END_CHANGE_SUMMARY
