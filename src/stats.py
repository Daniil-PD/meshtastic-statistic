# FILE: src/stats.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Вычисляет статистику сети.
#   SCOPE: [Расчет статистики по пакетам из DataStore]
#   DEPENDS: [M-DATASTORE]
#   LINKS: [M-STATS]
# END_MODULE_CONTRACT

import logging
from collections import Counter
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.datastore import DataStore

logger = logging.getLogger(__name__)

# START_CONTRACT: StatsCalculator
#   PURPOSE: Вычисляет статистику сети.
#   INPUTS: {}
#   OUTPUTS: {}
#   SIDE_EFFECTS: []
#   LINKS: []
# END_CONTRACT: StatsCalculator
class StatsCalculator:
    # START_CONTRACT: __init__
    #   PURPOSE: Инициализирует калькулятор статистики.
    #   INPUTS: {datastore: DataStore - Хранилище данных}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: __init__
    def __init__(self, datastore: DataStore):
        # START_BLOCK_INIT_CALCULATOR
        self._datastore = datastore
        # END_BLOCK_INIT_CALCULATOR

    # START_CONTRACT: get_total_messages
    #   PURPOSE: Подсчитывает общее количество сообщений.
    #   INPUTS: {}
    #   OUTPUTS: {int - Общее количество сообщений}
    #   SIDE_EFFECTS: [none]
    #   LINKS: [DataStore.get_packets]
    # END_CONTRACT: get_total_messages
    def get_total_messages(self) -> int:
        # START_BLOCK_COUNT_MESSAGES
        packets = self._datastore.get_packets()
        total = len(packets)
        logger.info(f"[StatsCalculator][get_total_messages] Total messages: {total}")
        return total
        # END_BLOCK_COUNT_MESSAGES

    # START_CONTRACT: get_top_senders
    #   PURPOSE: Определяет N самых активных участников.
    #   INPUTS: {n: int - Количество участников для возврата}
    #   OUTPUTS: {List[Dict[str, Any]] - Список участников с количеством сообщений}
    #   SIDE_EFFECTS: [none]
    #   LINKS: [DataStore.get_packets]
    # END_CONTRACT: get_top_senders
    def get_top_senders(self, n: int = 10) -> List[Dict[str, Any]]:
        # START_BLOCK_COUNT_SENDERS
        packets = self._datastore.get_packets()
        sender_counts = Counter(p.get('from_id') for p in packets if 'from_id' in p)
        # END_BLOCK_COUNT_SENDERS
        
        # START_BLOCK_RETURN_TOP_SENDERS
        result = [
            {'sender_id': sender, 'count': count}
            for sender, count in sender_counts.most_common(n)
        ]
        logger.info(f"[StatsCalculator][get_top_senders] Top {n} senders calculated")
        return result
        # END_BLOCK_RETURN_TOP_SENDERS

    # START_CONTRACT: get_top_heard_nodes
    #   PURPOSE: Определяет N самых "слышимых" узлов.
    #   INPUTS: {n: int - Количество узлов для возврата}
    #   OUTPUTS: {List[Dict[str, Any]] - Список узлов с количеством полученных пакетов}
    #   SIDE_EFFECTS: [none]
    #   LINKS: [DataStore.get_packets]
    # END_CONTRACT: get_top_heard_nodes
    def get_top_heard_nodes(self, n: int = 10) -> List[Dict[str, Any]]:
        # START_BLOCK_COUNT_HEARD_NODES
        packets = self._datastore.get_packets()
        node_counts = Counter(p.get('to_id') for p in packets if 'to_id' in p)
        # END_BLOCK_COUNT_HEARD_NODES
        
        # START_BLOCK_RETURN_TOP_HEARD
        result = [
            {'node_id': node, 'count': count}
            for node, count in node_counts.most_common(n)
        ]
        logger.info(f"[StatsCalculator][get_top_heard_nodes] Top {n} heard nodes calculated")
        return result
        # END_BLOCK_RETURN_TOP_HEARD

    # START_CONTRACT: get_portnum_distribution
    #   PURPOSE: Рассчитывает процентное соотношение типов сообщений (PortNum).
    #   INPUTS: {}
    #   OUTPUTS: {Dict[str, float] - Распределение PortNum в процентах}
    #   SIDE_EFFECTS: [none]
    #   LINKS: [DataStore.get_packets]
    # END_CONTRACT: get_portnum_distribution
    def get_portnum_distribution(self) -> Dict[str, float]:
        # START_BLOCK_COUNT_PORTNUM
        packets = self._datastore.get_packets()
        portnum_counts = Counter(p.get('portnum') for p in packets if 'portnum' in p)
        total = sum(portnum_counts.values())
        # END_BLOCK_COUNT_PORTNUM
        
        # START_BLOCK_CALCULATE_DISTRIBUTION
        if total == 0:
            return {}
        
        distribution = {
            str(portnum): (count / total) * 100
            for portnum, count in portnum_counts.items()
        }
        logger.info(f"[StatsCalculator][get_portnum_distribution] PortNum distribution calculated")
        return distribution
        # END_BLOCK_CALCULATE_DISTRIBUTION

    # START_CONTRACT: get_all_stats
    #   PURPOSE: Возвращает всю статистику в одном отчете.
    #   INPUTS: {top_n: int - Количество топ элементов}
    #   OUTPUTS: {Dict[str, Any] - Полный отчет статистики}
    #   SIDE_EFFECTS: [none]
    #   LINKS: [get_total_messages, get_top_senders, get_top_heard_nodes, get_portnum_distribution]
    # END_CONTRACT: get_all_stats
    def get_all_stats(self, top_n: int = 10) -> Dict[str, Any]:
        # START_BLOCK_COLLECT_ALL_STATS
        logger.info("[StatsCalculator][get_all_stats] Calculating all statistics")
        result = {
            'total_messages': self.get_total_messages(),
            'top_senders': self.get_top_senders(top_n),
            'top_heard_nodes': self.get_top_heard_nodes(top_n),
            'portnum_distribution': self.get_portnum_distribution(),
        }
        logger.info("[StatsCalculator][get_all_stats] Statistics calculated")
        return result
        # END_BLOCK_COLLECT_ALL_STATS

# START_MODULE_MAP
#   StatsCalculator - Вычисляет статистику сети.
#   get_total_messages - Подсчитывает общее количество сообщений.
#   get_top_senders - Определяет N самых активных участников.
#   get_top_heard_nodes - Определяет N самых "слышимых" узлов.
#   get_portnum_distribution - Рассчитывает распределение типов сообщений.
#   get_all_stats - Возвращает всю статистику в одном отчете.
# END_MODULE_MAP
