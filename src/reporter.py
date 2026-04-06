# FILE: src/reporter.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Формирует итоговый отчет.
#   SCOPE: [Генерация отчета из статистики и данных о погоде]
#   DEPENDS: [M-STATS, M-WEATHER]
#   LINKS: [M-REPORTER]
# END_MODULE_CONTRACT

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from src.stats import StatsCalculator
from src.weather import WeatherService

logger = logging.getLogger(__name__)

# START_CONTRACT: ReportGenerator
#   PURPOSE: Генератор отчетов.
#   INPUTS: {}
#   OUTPUTS: {}
#   SIDE_EFFECTS: []
#   LINKS: []
# END_CONTRACT: ReportGenerator
class ReportGenerator:
    # START_CONTRACT: __init__
    #   PURPOSE: Инициализирует генератор отчетов.
    #   INPUTS: {stats_calculator: StatsCalculator, weather_service: WeatherService}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: __init__
    def __init__(self, stats_calculator: StatsCalculator, weather_service: WeatherService):
        # START_BLOCK_INIT_DEPENDENCIES
        self._stats_calculator = stats_calculator
        self._weather_service = weather_service
        # END_BLOCK_INIT_DEPENDENCIES
        
        # START_BLOCK_INIT_LOG
        logger.info("[ReportGenerator][__init__] Service initialized")
        # END_BLOCK_INIT_LOG

    # START_CONTRACT: generate_report
    #   PURPOSE: Генерирует отчет за период.
    #   INPUTS: {
    #     date: Optional[datetime] - Дата отчета (по умолчанию сегодня),
    #     location: Optional[Dict[str, float]] - Координаты для погоды {lat, lon}
    #   }
    #   OUTPUTS: {Dict[str, Any] - Сформированный отчет}
    #   SIDE_EFFECTS: [Запрашивает статистику и погоду]
    #   LINKS: [StatsCalculator.get_all_stats, WeatherService.get_weather]
    # END_CONTRACT: generate_report
    def generate_report(
        self,
        date: Optional[datetime] = None,
        location: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        # START_BLOCK_INIT_REPORT
        if date is None:
            date = datetime.now()
        # END_BLOCK_INIT_REPORT
        
        # START_BLOCK_LOG_GENERATION
        logger.info(f"[ReportGenerator][generate_report] Generating report for {date}")
        # END_BLOCK_LOG_GENERATION
        
        # START_BLOCK_FETCH_STATS
        stats = self._stats_calculator.get_all_stats()
        logger.info("[ReportGenerator][generate_report] Statistics collected")
        # END_BLOCK_FETCH_STATS
        
        # START_BLOCK_FETCH_WEATHER
        weather = None
        if location:
            weather = self._weather_service.get_weather(
                lat=location.get('lat', 0.0),
                lon=location.get('lon', 0.0)
            )
            if weather:
                logger.info("[ReportGenerator][generate_report] Weather data collected")
            else:
                logger.warning("[ReportGenerator][generate_report] Weather data not available")
        # END_BLOCK_FETCH_WEATHER
        
        # START_BLOCK_BUILD_REPORT
        report = {
            'generated_at': date.isoformat(),
            'statistics': stats,
            'weather': weather,
            'summary': self._build_summary(stats, weather),
        }
        # END_BLOCK_BUILD_REPORT
        
        # START_BLOCK_LOG_COMPLETE
        logger.info("[ReportGenerator][generate_report] Report generated successfully")
        # END_BLOCK_LOG_COMPLETE
        
        return report

    # START_CONTRACT: _build_summary
    #   PURPOSE: Создает текстовое резюме отчета.
    #   INPUTS: {stats: Dict[str, Any], weather: Optional[Dict[str, Any]]}
    #   OUTPUTS: {str - Текстовое резюме}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: _build_summary
    def _build_summary(self, stats: Dict[str, Any], weather: Optional[Dict[str, Any]]) -> str:
        # START_BLOCK_BUILD_TEXT_SUMMARY
        lines = []
        lines.append(f"Total messages: {stats.get('total_messages', 0)}")
        
        top_senders = stats.get('top_senders', [])
        if top_senders:
            lines.append(f"Top sender: {top_senders[0].get('sender_id', 'N/A')} ({top_senders[0].get('count', 0)} messages)")
        
        if weather:
            lines.append(f"Weather: {weather.get('description', 'N/A')}, {weather.get('temperature', 0)}°C")
        
        return " | ".join(lines)
        # END_BLOCK_BUILD_TEXT_SUMMARY

    # START_CONTRACT: format_report_text
    #   PURPOSE: Форматирует отчет в текстовом виде.
    #   INPUTS: {report: Dict[str, Any] - Отчет для форматирования}
    #   OUTPUTS: {str - Отформатированный текст отчета}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: format_report_text
    def format_report_text(self, report: Dict[str, Any]) -> str:
        # START_BLOCK_FORMAT_HEADER
        lines = []
        lines.append("=" * 50)
        lines.append("MESHTASTIC DAILY REPORT")
        lines.append(f"Generated: {report.get('generated_at', 'N/A')}")
        lines.append("=" * 50)
        # END_BLOCK_FORMAT_HEADER
        
        # START_BLOCK_FORMAT_STATS
        lines.append("")
        lines.append("STATISTICS:")
        stats = report.get('statistics', {})
        lines.append(f"  Total messages: {stats.get('total_messages', 0)}")
        # END_BLOCK_FORMAT_STATS
        
        # START_BLOCK_FORMAT_TOP_SENDERS
        top_senders = stats.get('top_senders', [])
        if top_senders:
            lines.append("  Top senders:")
            for sender in top_senders[:5]:
                lines.append(f"    - {sender.get('sender_id', 'N/A')}: {sender.get('count', 0)} messages")
        # END_BLOCK_FORMAT_TOP_SENDERS
        
        # START_BLOCK_FORMAT_TOP_HEARD
        top_heard = stats.get('top_heard_nodes', [])
        if top_heard:
            lines.append("  Top heard nodes:")
            for node in top_heard[:5]:
                lines.append(f"    - {node.get('node_id', 'N/A')}: {node.get('count', 0)} packets")
        # END_BLOCK_FORMAT_TOP_HEARD
        
        # START_BLOCK_FORMAT_PORTNUM
        portnum_dist = stats.get('portnum_distribution', {})
        if portnum_dist:
            lines.append("  PortNum distribution:")
            for portnum, percentage in portnum_dist.items():
                lines.append(f"    - {portnum}: {percentage:.1f}%")
        # END_BLOCK_FORMAT_PORTNUM
        
        # START_BLOCK_FORMAT_WEATHER
        weather = report.get('weather')
        if weather:
            lines.append("")
            lines.append("WEATHER:")
            lines.append(f"  Temperature: {weather.get('temperature', 0)}°C")
            lines.append(f"  Humidity: {weather.get('humidity', 0)}%")
            lines.append(f"  Description: {weather.get('description', 'N/A')}")
            lines.append(f"  Pressure: {weather.get('pressure', 0)} hPa")
            lines.append(f"  Wind speed: {weather.get('wind_speed', 0)} m/s")
        # END_BLOCK_FORMAT_WEATHER
        
        # START_BLOCK_FORMAT_SUMMARY
        lines.append("")
        lines.append("SUMMARY:")
        lines.append(f"  {report.get('summary', 'N/A')}")
        lines.append("")
        lines.append("=" * 50)
        # END_BLOCK_FORMAT_SUMMARY
        
        # START_BLOCK_RETURN_FORMATTED
        result = "\n".join(lines)
        logger.info("[ReportGenerator][format_report_text] Report formatted")
        return result
        # END_BLOCK_RETURN_FORMATTED

# START_MODULE_MAP
#   ReportGenerator - Генератор отчетов.
#   __init__ - Инициализирует генератор отчетов.
#   generate_report - Генерирует отчет за период.
#   _build_summary - Создает текстовое резюме отчета.
#   format_report_text - Форматирует отчет в текстовом виде.
# END_MODULE_MAP

# START_CHANGE_SUMMARY
#   LAST_CHANGE: v1.0.0 - Initial implementation of ReportGenerator
# END_CHANGE_SUMMARY
