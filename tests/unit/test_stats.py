# FILE: tests/unit/test_stats.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Модульные тесты для M-STATS.
#   SCOPE: [Тестирование функций расчета статистики]
#   DEPENDS: [M-STATS, M-DATASTORE]
#   LINKS: [V-M-STATS]
# END_MODULE_CONTRACT

import unittest
from src.stats import StatsCalculator
from src.datastore import DataStore

# START_CONTRACT: TestStatsCalculator
#   PURPOSE: Тестирование StatsCalculator.
#   INPUTS: {}
#   OUTPUTS: {}
#   SIDE_EFFECTS: []
#   LINKS: []
# END_CONTRACT: TestStatsCalculator
class TestStatsCalculator(unittest.TestCase):

    # START_CONTRACT: setUp
    #   PURPOSE: Инициализация тестового окружения.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Создает DataStore и StatsCalculator]
    #   LINKS: []
    # END_CONTRACT: setUp
    def setUp(self):
        # START_BLOCK_INIT_TEST
        self.datastore = DataStore()
        self.stats = StatsCalculator(self.datastore)
        # END_BLOCK_INIT_TEST

    # START_CONTRACT: test_get_total_messages
    #   PURPOSE: Тестирование подсчета сообщений.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [get_total_messages]
    # END_CONTRACT: test_get_total_messages
    def test_get_total_messages(self):
        # START_BLOCK_ASSERT_TOTAL_MESSAGES
        self.datastore.add_packet({'id': 1})
        self.datastore.add_packet({'id': 2})
        total = self.stats.get_total_messages()
        self.assertEqual(total, 2)
        # END_BLOCK_ASSERT_TOTAL_MESSAGES

    # START_CONTRACT: test_get_top_senders
    #   PURPOSE: Тестирование определения топ отправителей.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [get_top_senders]
    # END_CONTRACT: test_get_top_senders
    def test_get_top_senders(self):
        # START_BLOCK_ASSERT_TOP_SENDERS
        self.datastore.add_packet({'id': 1, 'from_id': 'A'})
        self.datastore.add_packet({'id': 2, 'from_id': 'A'})
        self.datastore.add_packet({'id': 3, 'from_id': 'B'})
        top = self.stats.get_top_senders(2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0]['sender_id'], 'A')
        self.assertEqual(top[0]['count'], 2)
        # END_BLOCK_ASSERT_TOP_SENDERS

    # START_CONTRACT: test_get_top_heard_nodes
    #   PURPOSE: Тестирование определения топ слышимых узлов.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [get_top_heard_nodes]
    # END_CONTRACT: test_get_top_heard_nodes
    def test_get_top_heard_nodes(self):
        # START_BLOCK_ASSERT_TOP_HEARD
        self.datastore.add_packet({'id': 1, 'to_id': 'X'})
        self.datastore.add_packet({'id': 2, 'to_id': 'X'})
        self.datastore.add_packet({'id': 3, 'to_id': 'Y'})
        top = self.stats.get_top_heard_nodes(2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0]['node_id'], 'X')
        self.assertEqual(top[0]['count'], 2)
        # END_BLOCK_ASSERT_TOP_HEARD

    # START_CONTRACT: test_get_portnum_distribution
    #   PURPOSE: Тестирование распределения PortNum.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [get_portnum_distribution]
    # END_CONTRACT: test_get_portnum_distribution
    def test_get_portnum_distribution(self):
        # START_BLOCK_ASSERT_PORTNUM
        self.datastore.add_packet({'id': 1, 'portnum': 'TEXT'})
        self.datastore.add_packet({'id': 2, 'portnum': 'TEXT'})
        self.datastore.add_packet({'id': 3, 'portnum': 'POSITION'})
        dist = self.stats.get_portnum_distribution()
        self.assertAlmostEqual(dist['TEXT'], 66.67, places=1)
        self.assertAlmostEqual(dist['POSITION'], 33.33, places=1)
        # END_BLOCK_ASSERT_PORTNUM

    # START_CONTRACT: test_get_all_stats
    #   PURPOSE: Тестирование получения всей статистики.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [get_all_stats]
    # END_CONTRACT: test_get_all_stats
    def test_get_all_stats(self):
        # START_BLOCK_ASSERT_ALL_STATS
        self.datastore.add_packet({'id': 1, 'from_id': 'A', 'to_id': 'X', 'portnum': 'TEXT'})
        self.datastore.add_packet({'id': 2, 'from_id': 'A', 'to_id': 'Y', 'portnum': 'TEXT'})
        stats = self.stats.get_all_stats(2)
        self.assertEqual(stats['total_messages'], 2)
        self.assertEqual(len(stats['top_senders']), 1)
        self.assertEqual(len(stats['top_heard_nodes']), 2)
        self.assertEqual(len(stats['portnum_distribution']), 1)
        # END_BLOCK_ASSERT_ALL_STATS

    # START_CONTRACT: test_empty_datastore
    #   PURPOSE: Тестирование с пустым хранилищем.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [get_all_stats]
    # END_CONTRACT: test_empty_datastore
    def test_empty_datastore(self):
        # START_BLOCK_ASSERT_EMPTY
        stats = self.stats.get_all_stats()
        self.assertEqual(stats['total_messages'], 0)
        self.assertEqual(stats['top_senders'], [])
        self.assertEqual(stats['top_heard_nodes'], [])
        self.assertEqual(stats['portnum_distribution'], {})
        # END_BLOCK_ASSERT_EMPTY

if __name__ == '__main__':
    unittest.main()
