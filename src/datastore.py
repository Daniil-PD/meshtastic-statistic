# FILE: src/datastore.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Хранит пакеты Meshtastic в памяти.
#   SCOPE: [Добавление, получение и очистка пакетов]
#   DEPENDS: []
#   LINKS: [M-DATASTORE]
# END_MODULE_CONTRACT

from datetime import datetime
from typing import List, Dict, Any, Optional

# START_CONTRACT: DataStore
#   PURPOSE: Хранит пакеты Meshtastic в памяти.
#   INPUTS: {}
#   OUTPUTS: {}
#   SIDE_EFFECTS: []
#   LINKS: []
# END_CONTRACT: DataStore
class DataStore:
    # START_CONTRACT: __init__
    #   PURPOSE: Инициализирует хранилище данных.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Создает пустой список пакетов]
    #   LINKS: []
    # END_CONTRACT: __init__
    def __init__(self):
        # START_BLOCK_INIT_STORAGE
        self._packets: List[Dict[str, Any]] = []
        # END_BLOCK_INIT_STORAGE

    # START_CONTRACT: add_packet
    #   PURPOSE: Добавляет пакет в хранилище.
    #   INPUTS: {packet: Dict[str, Any] - Пакет для добавления}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Добавляет пакет во внутренний список]
    #   LINKS: []
    # END_CONTRACT: add_packet
    def add_packet(self, packet: Dict[str, Any]) -> None:
        # START_BLOCK_ADD_PACKET
        self._packets.append(packet)
        # END_BLOCK_ADD_PACKET

    # START_CONTRACT: get_packets
    #   PURPOSE: Возвращает все пакеты за период.
    #   INPUTS: {
    #     start_time: Optional[datetime] - Начало периода,
    #     end_time: Optional[datetime] - Конец периода
    #   }
    #   OUTPUTS: {List[Dict[str, Any]] - Список пакетов}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: get_packets
    def get_packets(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        # START_BLOCK_FILTER_PACKETS
        if start_time is None and end_time is None:
            return self._packets.copy()
        
        result = []
        for packet in self._packets:
            packet_time = packet.get('rx_time')
            if packet_time is None:
                continue
            
            if start_time and packet_time < start_time:
                continue
            if end_time and packet_time > end_time:
                continue
            
            result.append(packet)
        
        return result
        # END_BLOCK_FILTER_PACKETS

    # START_CONTRACT: clear
    #   PURPOSE: Очищает хранилище.
    #   INPUTS: {}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Очищает внутренний список пакетов]
    #   LINKS: []
    # END_CONTRACT: clear
    def clear(self) -> None:
        # START_BLOCK_CLEAR_STORAGE
        self._packets.clear()
        # END_BLOCK_CLEAR_STORAGE

# START_MODULE_MAP
#   DataStore - Хранит пакеты Meshtastic в памяти.
#   add_packet - Добавляет пакет в хранилище.
#   get_packets - Возвращает все пакеты за период.
#   clear - Очищает хранилище.
# END_MODULE_MAP
