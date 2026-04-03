# FILE: src/collector.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Прослушивает и сохраняет пакеты Meshtastic.
#   SCOPE: [Сбор и сохранение пакетов в DataStore]
#   DEPENDS: [M-DATASTORE, M-MESHTASTIC]
#   LINKS: [M-COLLECTOR]
# END_MODULE_CONTRACT

import logging
from typing import Dict, Any, Optional
from src.datastore import DataStore

logger = logging.getLogger(__name__)

# START_CONTRACT: PacketCollector
#   PURPOSE: Прослушивает и сохраняет пакеты Meshtastic.
#   INPUTS: {}
#   OUTPUTS: {}
#   SIDE_EFFECTS: []
#   LINKS: []
# END_CONTRACT: PacketCollector
class PacketCollector:
    # START_CONTRACT: __init__
    #   PURPOSE: Инициализирует сборщик пакетов.
    #   INPUTS: {datastore: DataStore - Хранилище для пакетов}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: __init__
    def __init__(self, datastore: DataStore):
        # START_BLOCK_INIT_COLLECTOR
        self._datastore = datastore
        self._running = False
        # END_BLOCK_INIT_COLLECTOR

    # START_CONTRACT: handle_packet
    #   PURPOSE: Обрабатывает входящий пакет.
    #   INPUTS: {packet: Dict[str, Any] - Входящий пакет}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Сохраняет пакет в DataStore]
    #   LINKS: [DataStore.add_packet]
    # END_CONTRACT: handle_packet
    def handle_packet(self, packet: Dict[str, Any]) -> None:
        # START_BLOCK_LOG_PACKET
        logger.debug(f"[PacketCollector][handle_packet] Received packet: {packet.get('id')}")
        # END_BLOCK_LOG_PACKET
        
        # START_BLOCK_SAVE_PACKET
        self._datastore.add_packet(packet)
        # END_BLOCK_SAVE_PACKET
        
        # START_BLOCK_LOG_SAVED
        logger.info(f"[PacketCollector][handle_packet] Packet saved: {packet.get('id')}")
        # END_BLOCK_LOG_SAVED

    # START_CONTRACT: start
    #   PURPOSE: Запускает сборщик пакетов.
    #   INPUTS: {}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Устанавливает флаг running=True]
    #   LINKS: []
    # END_CONTRACT: start
    def start(self) -> None:
        # START_BLOCK_START_COLLECTOR
        self._running = True
        logger.info("[PacketCollector][start] Collector started")
        # END_BLOCK_START_COLLECTOR

    # START_CONTRACT: stop
    #   PURPOSE: Останавливает сборщик пакетов.
    #   INPUTS: {}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Устанавливает флаг running=False]
    #   LINKS: []
    # END_CONTRACT: stop
    def stop(self) -> None:
        # START_BLOCK_STOP_COLLECTOR
        self._running = False
        logger.info("[PacketCollector][stop] Collector stopped")
        # END_BLOCK_STOP_COLLECTOR

    # START_CONTRACT: is_running
    #   PURPOSE: Проверяет, запущен ли сборщик.
    #   INPUTS: {}
    #   OUTPUTS: {bool - True если запущен}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: is_running
    def is_running(self) -> bool:
        # START_BLOCK_CHECK_RUNNING
        return self._running
        # END_BLOCK_CHECK_RUNNING

# START_MODULE_MAP
#   PacketCollector - Прослушивает и сохраняет пакеты Meshtastic.
#   handle_packet - Обрабатывает входящий пакет.
#   start - Запускает сборщик пакетов.
#   stop - Останавливает сборщик пакетов.
#   is_running - Проверяет, запущен ли сборщик.
# END_MODULE_MAP
