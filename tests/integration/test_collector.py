# FILE: tests/integration/test_collector.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Интеграционные тесты для M-COLLECTOR.
#   SCOPE: [Тестирование взаимодействия PacketCollector и DataStore]
#   DEPENDS: [M-COLLECTOR, M-DATASTORE]
#   LINKS: [V-M-COLLECTOR]
# END_MODULE_CONTRACT

import unittest
from src.collector import PacketCollector
from src.datastore import DataStore

# START_CONTRACT: TestPacketCollector
#   PURPOSE: Тестирование PacketCollector.
#   INPUTS: {}
#   OUTPUTS: {}
#   SIDE_EFFECTS: []
#   LINKS: []
# END_CONTRACT: TestPacketCollector
class TestPacketCollector(unittest.TestCase):

    # START_CONTRACT: setUp
    #   PURPOSE: Инициализация тестового окружения.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Создает DataStore и PacketCollector]
    #   LINKS: []
    # END_CONTRACT: setUp
    def setUp(self):
        # START_BLOCK_INIT_TEST
        self.datastore = DataStore()
        self.collector = PacketCollector(self.datastore)
        # END_BLOCK_INIT_TEST

    # START_CONTRACT: test_handle_packet
    #   PURPOSE: Тестирование обработки пакета.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [handle_packet]
    # END_CONTRACT: test_handle_packet
    def test_handle_packet(self):
        # START_BLOCK_ASSERT_HANDLE_PACKET
        packet = {'id': 1, 'data': 'test'}
        self.collector.handle_packet(packet)
        packets = self.datastore.get_packets()
        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0]['id'], 1)
        # END_BLOCK_ASSERT_HANDLE_PACKET

    # START_CONTRACT: test_start_stop
    #   PURPOSE: Тестирование запуска и остановки.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [start, stop, is_running]
    # END_CONTRACT: test_start_stop
    def test_start_stop(self):
        # START_BLOCK_ASSERT_START_STOP
        self.assertFalse(self.collector.is_running())
        self.collector.start()
        self.assertTrue(self.collector.is_running())
        self.collector.stop()
        self.assertFalse(self.collector.is_running())
        # END_BLOCK_ASSERT_START_STOP

    # START_CONTRACT: test_multiple_packets
    #   PURPOSE: Тестирование обработки нескольких пакетов.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [handle_packet]
    # END_CONTRACT: test_multiple_packets
    def test_multiple_packets(self):
        # START_BLOCK_ASSERT_MULTIPLE_PACKETS
        for i in range(5):
            self.collector.handle_packet({'id': i})
        packets = self.datastore.get_packets()
        self.assertEqual(len(packets), 5)
        # END_BLOCK_ASSERT_MULTIPLE_PACKETS

if __name__ == '__main__':
    unittest.main()
