# FILE: tests/unit/test_datastore.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Модульные тесты для M-DATASTORE.
#   SCOPE: [Тестирование функций add_packet, get_packets, clear]
#   DEPENDS: [M-DATASTORE]
#   LINKS: [V-M-DATASTORE]
# END_MODULE_CONTRACT

import unittest
from datetime import datetime, timedelta
from src.datastore import DataStore

# START_CONTRACT: TestDataStore
#   PURPOSE: Тестирование DataStore.
#   INPUTS: {}
#   OUTPUTS: {}
#   SIDE_EFFECTS: []
#   LINKS: []
# END_CONTRACT: TestDataStore
class TestDataStore(unittest.TestCase):

    # START_CONTRACT: setUp
    #   PURPOSE: Инициализация тестового окружения.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Создает новый экземпляр DataStore]
    #   LINKS: []
    # END_CONTRACT: setUp
    def setUp(self):
        # START_BLOCK_INIT_TEST
        self.store = DataStore()
        # END_BLOCK_INIT_TEST

    # START_CONTRACT: test_add_packet
    #   PURPOSE: Тестирование добавления пакета.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [add_packet]
    # END_CONTRACT: test_add_packet
    def test_add_packet(self):
        # START_BLOCK_ASSERT_ADD_PACKET
        packet = {'id': 1, 'data': 'test'}
        self.store.add_packet(packet)
        packets = self.store.get_packets()
        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0]['id'], 1)
        # END_BLOCK_ASSERT_ADD_PACKET

    # START_CONTRACT: test_get_packets_all
    #   PURPOSE: Тестирование получения всех пакетов.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [get_packets]
    # END_CONTRACT: test_get_packets_all
    def test_get_packets_all(self):
        # START_BLOCK_ASSERT_GET_PACKETS_ALL
        self.store.add_packet({'id': 1})
        self.store.add_packet({'id': 2})
        packets = self.store.get_packets()
        self.assertEqual(len(packets), 2)
        # END_BLOCK_ASSERT_GET_PACKETS_ALL

    # START_CONTRACT: test_get_packets_by_period
    #   PURPOSE: Тестирование получения пакетов за период.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [get_packets]
    # END_CONTRACT: test_get_packets_by_period
    def test_get_packets_by_period(self):
        # START_BLOCK_ASSERT_GET_PACKETS_PERIOD
        now = datetime.now()
        self.store.add_packet({'id': 1, 'rx_time': now - timedelta(hours=2)})
        self.store.add_packet({'id': 2, 'rx_time': now - timedelta(hours=1)})
        self.store.add_packet({'id': 3, 'rx_time': now})
        
        start = now - timedelta(hours=1, minutes=30)
        packets = self.store.get_packets(start_time=start)
        self.assertEqual(len(packets), 2)
        # END_BLOCK_ASSERT_GET_PACKETS_PERIOD

    # START_CONTRACT: test_clear
    #   PURPOSE: Тестирование очистки хранилища.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [clear]
    # END_CONTRACT: test_clear
    def test_clear(self):
        # START_BLOCK_ASSERT_CLEAR
        self.store.add_packet({'id': 1})
        self.store.clear()
        packets = self.store.get_packets()
        self.assertEqual(len(packets), 0)
        # END_BLOCK_ASSERT_CLEAR

if __name__ == '__main__':
    unittest.main()
