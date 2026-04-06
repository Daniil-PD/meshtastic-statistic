# FILE: src/main.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Координирует генерацию и отправку отчета.
#   SCOPE: [Планирование задач, координация модулей]
#   DEPENDS: [M-COLLECTOR, M-REPORTER, M-MESHTASTIC, M-CONFIG]
#   LINKS: [M-SCHEDULER]
# END_MODULE_CONTRACT

import logging
import asyncio
from datetime import datetime, time
from typing import Dict, Any, Optional, List, Callable
from src.config import load_config
from src.datastore import DataStore
from src.collector import PacketCollector
from src.stats import StatsCalculator
from src.weather import WeatherService
from src.reporter import ReportGenerator
from src.meshtastic_interface import MeshtasticInterface

logger = logging.getLogger(__name__)

# START_CONTRACT: Scheduler
#   PURPOSE: Планировщик задач для генерации и отправки отчетов.
#   INPUTS: {}
#   OUTPUTS: {}
#   SIDE_EFFECTS: []
#   LINKS: []
# END_CONTRACT: Scheduler
class Scheduler:
    # START_CONTRACT: __init__
    #   PURPOSE: Инициализирует планировщик.
    #   INPUTS: {config: Optional[Dict[str, Any]] - Конфигурация}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Создает и настраивает все модули]
    #   LINKS: []
    # END_CONTRACT: __init__
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # START_BLOCK_INIT_CONFIG
        if config is None:
            config = load_config()
        self._config = config
        # END_BLOCK_INIT_CONFIG
        
        # START_BLOCK_INIT_DATASTORE
        self._datastore = DataStore()
        # END_BLOCK_INIT_DATASTORE
        
        # START_BLOCK_INIT_COLLECTOR
        self._collector = PacketCollector(self._datastore)
        # END_BLOCK_INIT_COLLECTOR
        
        # START_BLOCK_INIT_STATS
        self._stats_calculator = StatsCalculator(self._datastore)
        # END_BLOCK_INIT_STATS
        
        # START_BLOCK_INIT_WEATHER
        self._weather_service = WeatherService(config)
        # END_BLOCK_INIT_WEATHER
        
        # START_BLOCK_INIT_REPORTER
        self._reporter = ReportGenerator(self._stats_calculator, self._weather_service)
        # END_BLOCK_INIT_REPORTER
        
        # START_BLOCK_INIT_INTERFACE
        self._interface = MeshtasticInterface(config)
        # END_BLOCK_INIT_INTERFACE
        
        # START_BLOCK_INIT_SCHEDULE
        self._scheduled_tasks: List[Dict[str, Any]] = []
        self._running = False
        # END_BLOCK_INIT_SCHEDULE
        
        # START_BLOCK_INIT_LOG
        logger.info("[Scheduler][__init__] Scheduler initialized")
        # END_BLOCK_INIT_LOG

    # START_CONTRACT: schedule_daily_report
    #   PURPOSE: Планирует ежедневную генерацию отчета.
    #   INPUTS: {
    #     report_time: time - Время генерации отчета,
    #     location: Optional[Dict[str, float]] - Координаты для погоды
    #   }
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Добавляет задачу в расписание]
    #   LINKS: []
    # END_CONTRACT: schedule_daily_report
    def schedule_daily_report(
        self,
        report_time: time,
        location: Optional[Dict[str, float]] = None
    ) -> None:
        # START_BLOCK_SCHEDULE_TASK
        task = {
            'type': 'daily_report',
            'time': report_time,
            'location': location,
        }
        self._scheduled_tasks.append(task)
        logger.info(f"[Scheduler][schedule_daily_report] Daily report scheduled for {report_time}")
        # END_BLOCK_SCHEDULE_TASK

    # START_CONTRACT: start
    #   PURPOSE: Запускает планировщик.
    #   INPUTS: {}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Запускает сборщик пакетов, устанавливает running=True]
    #   LINKS: [PacketCollector.start]
    # END_CONTRACT: start
    def start(self) -> None:
        # START_BLOCK_START_SCHEDULER
        self._running = True
        self._collector.start()
        logger.info("[Scheduler][start] Scheduler started")
        # END_BLOCK_START_SCHEDULER

    # START_CONTRACT: stop
    #   PURPOSE: Останавливает планировщик.
    #   INPUTS: {}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Останавливает сборщик пакетов, устанавливает running=False]
    #   LINKS: [PacketCollector.stop]
    # END_CONTRACT: stop
    def stop(self) -> None:
        # START_BLOCK_STOP_SCHEDULER
        self._running = False
        self._collector.stop()
        logger.info("[Scheduler][stop] Scheduler stopped")
        # END_BLOCK_STOP_SCHEDULER

    # START_CONTRACT: is_running
    #   PURPOSE: Проверяет, запущен ли планировщик.
    #   INPUTS: {}
    #   OUTPUTS: {bool - True если запущен}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: is_running
    def is_running(self) -> bool:
        # START_BLOCK_CHECK_RUNNING
        return self._running
        # END_BLOCK_CHECK_RUNNING

    # START_CONTRACT: run_daily_report_job
    #   PURPOSE: Выполняет задачу генерации и отправки ежедневного отчета.
    #   INPUTS: {location: Optional[Dict[str, float]] - Координаты для погоды}
    #   OUTPUTS: {bool - True если отчет успешно отправлен}
    #   SIDE_EFFECTS: [Генерирует отчет, отправляет через интерфейс]
    #   LINKS: [ReportGenerator.generate_report, MeshtasticInterface.send_message]
    # END_CONTRACT: run_daily_report_job
    def run_daily_report_job(
        self,
        location: Optional[Dict[str, float]] = None
    ) -> bool:
        # START_BLOCK_LOG_JOB_START
        logger.info("[Scheduler][run_daily_report_job] Daily report job started")
        # END_BLOCK_LOG_JOB_START
        
        # START_BLOCK_GENERATE_REPORT
        report = self._reporter.generate_report(
            date=datetime.now(),
            location=location
        )
        logger.info("[Scheduler][run_daily_report_job] Report generated")
        # END_BLOCK_GENERATE_REPORT
        
        # START_BLOCK_FORMAT_REPORT
        report_text = self._reporter.format_report_text(report)
        # END_BLOCK_FORMAT_REPORT
        
        # START_BLOCK_CONNECT_INTERFACE
        if not self._interface.is_connected():
            if not self._interface.connect():
                logger.error("[Scheduler][run_daily_report_job] Failed to connect to Meshtastic")
                return False
        # END_BLOCK_CONNECT_INTERFACE
        
        # START_BLOCK_SEND_REPORT
        success = self._interface.send_message(report_text)
        # END_BLOCK_SEND_REPORT
        
        if success:
            # START_BLOCK_LOG_SUCCESS
            logger.info("[Scheduler][run_daily_report_job] Report sent successfully")
            # END_BLOCK_LOG_SUCCESS
        else:
            # START_BLOCK_LOG_FAILURE
            logger.error("[Scheduler][run_daily_report_job] Failed to send report")
            # END_BLOCK_LOG_FAILURE
        
        return success

    # START_CONTRACT: get_scheduled_tasks
    #   PURPOSE: Возвращает список запланированных задач.
    #   INPUTS: {}
    #   OUTPUTS: {List[Dict[str, Any]] - Список задач}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: get_scheduled_tasks
    def get_scheduled_tasks(self) -> list:
        # START_BLOCK_RETURN_TASKS
        return self._scheduled_tasks.copy()
        # END_BLOCK_RETURN_TASKS

    # START_CONTRACT: run_async
    #   PURPOSE: Асинхронно запускает планировщик с выполнением задач по расписанию.
    #   INPUTS: {}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Выполняет задачи по расписанию]
    #   LINKS: []
    # END_CONTRACT: run_async
    async def run_async(self) -> None:
        # START_BLOCK_ASYNC_LOOP
        logger.info("[Scheduler][run_async] Starting async scheduler loop")
        while self._running:
            await asyncio.sleep(60)  # Проверка каждую минуту
            await self._check_and_run_tasks()
        # END_BLOCK_ASYNC_LOOP

    # START_CONTRACT: _check_and_run_tasks
    #   PURPOSE: Проверяет и выполняет задачи по расписанию.
    #   INPUTS: {}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Выполняет запланированные задачи]
    #   LINKS: []
    # END_CONTRACT: _check_and_run_tasks
    async def _check_and_run_tasks(self) -> None:
        # START_BLOCK_CHECK_TASKS
        now = datetime.now()
        current_time = now.time()
        
        for task in self._scheduled_tasks:
            if task['type'] == 'daily_report':
                scheduled_time = task['time']
                # Проверяем, совпадает ли время (с допуском в 1 минуту)
                if abs((scheduled_time.hour - current_time.hour) * 60 + 
                       (scheduled_time.minute - current_time.minute)) < 1:
                    logger.info(f"[Scheduler][_check_and_run_tasks] Running task: {task['type']}")
                    self.run_daily_report_job(location=task.get('location'))
        # END_BLOCK_CHECK_TASKS


# START_CONTRACT: main
#   PURPOSE: Точка входа приложения.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [Запускает планировщик]
#   LINKS: []
# END_CONTRACT: main
def main():
    # START_BLOCK_MAIN_INIT
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s'
    )
    
    config = load_config()
    scheduler = Scheduler(config)
    # END_BLOCK_MAIN_INIT
    
    # START_BLOCK_MAIN_SCHEDULE
    # Планируем ежедневный отчет на 23:59
    scheduler.schedule_daily_report(
        time(23, 59),
        location={'lat': 55.75, 'lon': 37.62}  # Москва (пример)
    )
    # END_BLOCK_MAIN_SCHEDULE
    
    # START_BLOCK_MAIN_START
    scheduler.start()
    logger.info("[main] Scheduler is running. Press Ctrl+C to stop.")
    # END_BLOCK_MAIN_START
    
    # START_BLOCK_MAIN_LOOP
    try:
        asyncio.run(scheduler.run_async())
    except KeyboardInterrupt:
        logger.info("[main] Shutdown requested")
    finally:
        scheduler.stop()
    # END_BLOCK_MAIN_LOOP


if __name__ == '__main__':
    main()

# START_MODULE_MAP
#   Scheduler - Планировщик задач для генерации и отправки отчетов.
#   __init__ - Инициализирует планировщик.
#   schedule_daily_report - Планирует ежедневную генерацию отчета.
#   start - Запускает планировщик.
#   stop - Останавливает планировщик.
#   is_running - Проверяет, запущен ли планировщик.
#   run_daily_report_job - Выполняет задачу генерации и отправки ежедневного отчета.
#   get_scheduled_tasks - Возвращает список запланированных задач.
#   run_async - Асинхронно запускает планировщик с выполнением задач по расписанию.
#   _check_and_run_tasks - Проверяет и выполняет задачи по расписанию.
#   main - Точка входа приложения.
# END_MODULE_MAP

# START_CHANGE_SUMMARY
#   LAST_CHANGE: v1.0.0 - Initial implementation of Scheduler
# END_CHANGE_SUMMARY
