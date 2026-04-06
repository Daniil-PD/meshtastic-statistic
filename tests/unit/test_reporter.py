# FILE: tests/unit/test_reporter.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Модульные тесты для ReportGenerator.
#   SCOPE: [Тестирование генерации и форматирования отчетов]
#   DEPENDS: [M-REPORTER, M-STATS, M-WEATHER]
#   LINKS: [V-M-REPORTER]
# END_MODULE_CONTRACT

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.reporter import ReportGenerator
from src.stats import StatsCalculator
from src.weather import WeatherService

# START_CONTRACT: create_mock_dependencies
#   PURPOSE: Создает mock-объекты для зависимостей.
#   INPUTS: {}
#   OUTPUTS: {tuple - (mock_stats, mock_weather)}
#   SIDE_EFFECTS: [none]
#   LINKS: []
# END_CONTRACT: create_mock_dependencies
def create_mock_dependencies():
    # START_BLOCK_CREATE_MOCKS
    mock_stats = MagicMock(spec=StatsCalculator)
    mock_stats.get_all_stats.return_value = {
        'total_messages': 100,
        'top_senders': [
            {'sender_id': '!user1', 'count': 50},
            {'sender_id': '!user2', 'count': 30},
        ],
        'top_heard_nodes': [
            {'node_id': '!node1', 'count': 80},
            {'node_id': '!node2', 'count': 60},
        ],
        'portnum_distribution': {
            'TEXT_MESSAGE_APP': 70.0,
            'NODEINFO_APP': 20.0,
            'POSITION_APP': 10.0,
        },
    }
    
    mock_weather = MagicMock(spec=WeatherService)
    mock_weather.get_weather.return_value = {
        'temperature': 22.5,
        'humidity': 55,
        'description': 'Partly cloudy',
        'pressure': 1015,
        'wind_speed': 4.2,
    }
    
    return mock_stats, mock_weather
    # END_BLOCK_CREATE_MOCKS

# START_CONTRACT: test_report_generator_init
#   PURPOSE: Проверяет инициализацию генератора отчетов.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [ReportGenerator.__init__]
# END_CONTRACT: test_report_generator_init
def test_report_generator_init():
    # START_BLOCK_TEST_INIT
    mock_stats, mock_weather = create_mock_dependencies()
    generator = ReportGenerator(mock_stats, mock_weather)
    
    assert generator._stats_calculator == mock_stats
    assert generator._weather_service == mock_weather
    # END_BLOCK_TEST_INIT

# START_CONTRACT: test_generate_report_basic
#   PURPOSE: Проверяет базовую генерацию отчета.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [ReportGenerator.generate_report]
# END_CONTRACT: test_generate_report_basic
def test_generate_report_basic():
    # START_BLOCK_TEST_BASIC_REPORT
    mock_stats, mock_weather = create_mock_dependencies()
    generator = ReportGenerator(mock_stats, mock_weather)
    
    report = generator.generate_report()
    
    assert 'generated_at' in report
    assert 'statistics' in report
    assert 'weather' in report
    assert 'summary' in report
    assert report['statistics']['total_messages'] == 100
    # END_BLOCK_TEST_BASIC_REPORT
    
    # START_BLOCK_VERIFY_STATS_CALL
    mock_stats.get_all_stats.assert_called_once()
    # END_BLOCK_VERIFY_STATS_CALL

# START_CONTRACT: test_generate_report_with_location
#   PURPOSE: Проверяет генерацию отчета с координатами.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [ReportGenerator.generate_report]
# END_CONTRACT: test_generate_report_with_location
def test_generate_report_with_location():
    # START_BLOCK_TEST_WITH_WEATHER
    mock_stats, mock_weather = create_mock_dependencies()
    generator = ReportGenerator(mock_stats, mock_weather)
    
    report = generator.generate_report(
        location={'lat': 55.75, 'lon': 37.62}
    )
    
    assert report['weather'] is not None
    assert report['weather']['temperature'] == 22.5
    # END_BLOCK_TEST_WITH_WEATHER
    
    # START_BLOCK_VERIFY_WEATHER_CALL
    mock_weather.get_weather.assert_called_once_with(lat=55.75, lon=37.62)
    # END_BLOCK_VERIFY_WEATHER_CALL

# START_CONTRACT: test_generate_report_no_weather
#   PURPOSE: Проверяет генерацию отчета без погоды.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [ReportGenerator.generate_report]
# END_CONTRACT: test_generate_report_no_weather
def test_generate_report_no_weather():
    # START_BLOCK_TEST_NO_WEATHER
    mock_stats, mock_weather = create_mock_dependencies()
    mock_weather.get_weather.return_value = None
    generator = ReportGenerator(mock_stats, mock_weather)
    
    report = generator.generate_report(location={'lat': 0, 'lon': 0})
    
    assert report['weather'] is None
    # END_BLOCK_TEST_NO_WEATHER

# START_CONTRACT: test_generate_report_custom_date
#   PURPOSE: Проверяет генерацию отчета с указанной датой.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [ReportGenerator.generate_report]
# END_CONTRACT: test_generate_report_custom_date
def test_generate_report_custom_date():
    # START_BLOCK_TEST_CUSTOM_DATE
    mock_stats, mock_weather = create_mock_dependencies()
    generator = ReportGenerator(mock_stats, mock_weather)
    
    custom_date = datetime(2024, 1, 15, 10, 30, 0)
    report = generator.generate_report(date=custom_date)
    
    assert report['generated_at'] == '2024-01-15T10:30:00'
    # END_BLOCK_TEST_CUSTOM_DATE

# START_CONTRACT: test_build_summary_basic
#   PURPOSE: Проверяет создание базового резюме.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [ReportGenerator._build_summary]
# END_CONTRACT: test_build_summary_basic
def test_build_summary_basic():
    # START_BLOCK_TEST_SUMMARY_BASIC
    mock_stats, mock_weather = create_mock_dependencies()
    generator = ReportGenerator(mock_stats, mock_weather)
    
    stats = {'total_messages': 50, 'top_senders': [{'sender_id': '!user1', 'count': 25}]}
    weather = {'description': 'Clear', 'temperature': 20}
    
    summary = generator._build_summary(stats, weather)
    
    assert 'Total messages: 50' in summary
    assert 'Top sender: !user1' in summary
    assert 'Weather: Clear' in summary
    # END_BLOCK_TEST_SUMMARY_BASIC

# START_CONTRACT: test_build_summary_no_weather
#   PURPOSE: Проверяет создание резюме без погоды.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [ReportGenerator._build_summary]
# END_CONTRACT: test_build_summary_no_weather
def test_build_summary_no_weather():
    # START_BLOCK_TEST_SUMMARY_NO_WEATHER
    mock_stats, mock_weather = create_mock_dependencies()
    generator = ReportGenerator(mock_stats, mock_weather)
    
    stats = {'total_messages': 50, 'top_senders': []}
    
    summary = generator._build_summary(stats, None)
    
    assert 'Total messages: 50' in summary
    assert 'Weather' not in summary
    # END_BLOCK_TEST_SUMMARY_NO_WEATHER

# START_CONTRACT: test_format_report_text_structure
#   PURPOSE: Проверяет структуру форматированного отчета.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [ReportGenerator.format_report_text]
# END_CONTRACT: test_format_report_text_structure
def test_format_report_text_structure():
    # START_BLOCK_TEST_FORMAT_STRUCTURE
    mock_stats, mock_weather = create_mock_dependencies()
    generator = ReportGenerator(mock_stats, mock_weather)
    
    report = {
        'generated_at': '2024-01-15T10:00:00',
        'statistics': mock_stats.get_all_stats.return_value,
        'weather': mock_weather.get_weather.return_value,
        'summary': 'Test summary',
    }
    
    formatted = generator.format_report_text(report)
    
    assert 'MESHTASTIC DAILY REPORT' in formatted
    assert 'Generated: 2024-01-15T10:00:00' in formatted
    assert 'STATISTICS:' in formatted
    assert 'WEATHER:' in formatted
    assert 'SUMMARY:' in formatted
    assert '=' * 50 in formatted
    # END_BLOCK_TEST_FORMAT_STRUCTURE

# START_CONTRACT: test_format_report_text_top_senders
#   PURPOSE: Проверяет форматирование топ отправителей.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [ReportGenerator.format_report_text]
# END_CONTRACT: test_format_report_text_top_senders
def test_format_report_text_top_senders():
    # START_BLOCK_TEST_FORMAT_SENDERS
    mock_stats, mock_weather = create_mock_dependencies()
    generator = ReportGenerator(mock_stats, mock_weather)
    
    report = {
        'generated_at': '2024-01-15T10:00:00',
        'statistics': mock_stats.get_all_stats.return_value,
        'weather': None,
        'summary': 'Test',
    }
    
    formatted = generator.format_report_text(report)
    
    assert 'Top senders:' in formatted
    assert '!user1: 50 messages' in formatted
    assert '!user2: 30 messages' in formatted
    # END_BLOCK_TEST_FORMAT_SENDERS

# START_CONTRACT: test_format_report_text_portnum
#   PURPOSE: Проверяет форматирование распределения PortNum.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [ReportGenerator.format_report_text]
# END_CONTRACT: test_format_report_text_portnum
def test_format_report_text_portnum():
    # START_BLOCK_TEST_FORMAT_PORTNUM
    mock_stats, mock_weather = create_mock_dependencies()
    generator = ReportGenerator(mock_stats, mock_weather)
    
    report = {
        'generated_at': '2024-01-15T10:00:00',
        'statistics': mock_stats.get_all_stats.return_value,
        'weather': None,
        'summary': 'Test',
    }
    
    formatted = generator.format_report_text(report)
    
    assert 'PortNum distribution:' in formatted
    assert 'TEXT_MESSAGE_APP:' in formatted
    # END_BLOCK_TEST_FORMAT_PORTNUM

# START_MODULE_MAP
#   create_mock_dependencies - Создает mock-объекты для зависимостей.
#   test_report_generator_init - Проверяет инициализацию генератора отчетов.
#   test_generate_report_basic - Проверяет базовую генерацию отчета.
#   test_generate_report_with_location - Проверяет генерацию отчета с координатами.
#   test_generate_report_no_weather - Проверяет генерацию отчета без погоды.
#   test_generate_report_custom_date - Проверяет генерацию отчета с указанной датой.
#   test_build_summary_basic - Проверяет создание базового резюме.
#   test_build_summary_no_weather - Проверяет создание резюме без погоды.
#   test_format_report_text_structure - Проверяет структуру форматированного отчета.
#   test_format_report_text_top_senders - Проверяет форматирование топ отправителей.
#   test_format_report_text_portnum - Проверяет форматирование распределения PortNum.
# END_MODULE_MAP

# START_CHANGE_SUMMARY
#   LAST_CHANGE: v1.0.0 - Initial tests for ReportGenerator
# END_CHANGE_SUMMARY
