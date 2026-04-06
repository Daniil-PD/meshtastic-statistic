# FILE: tests/integration/test_collector.py
# VERSION: 2.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Интеграционные тесты для M-COLLECTOR.
#   SCOPE: [Тестирование взаимодействия PacketCollector и DataStore]
#   DEPENDS: [M-COLLECTOR, M-DATASTORE]
#   LINKS: [V-M-COLLECTOR]
# END_MODULE_CONTRACT

import unittest
import os
import tempfile
from datetime import datetime
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
    #   SIDE_EFFECTS: [Создает DataStore и PacketCollector с временной БД]
    #   LINKS: []
    # END_CONTRACT: setUp
    def setUp(self):
        # START_BLOCK_INIT_TEST
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.datastore = DataStore(db_path=self.test_db.name)
        self.collector = PacketCollector(self.datastore)
        # END_BLOCK_INIT_TEST

    # START_CONTRACT: tearDown
    #   PURPOSE: Очистка после теста.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Закрывает подключение и удаляет файл БД]
    #   LINKS: []
    # END_CONTRACT: tearDown
    def tearDown(self):
        # START_BLOCK_CLEANUP_TEST
        self.datastore.close()
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        # END_BLOCK_CLEANUP_TEST

    # START_CONTRACT: test_handle_packet
    #   PURPOSE: Тестирование обработки пакета.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [handle_packet]
    # END_CONTRACT: test_handle_packet
    def test_handle_packet(self):
        # START_BLOCK_ASSERT_HANDLE_PACKET
        now = datetime.now()
        packet = {'id': 'pkt-1', 'data': 'test', 'rx_time': now}
        self.collector.handle_packet(packet)
        packets = self.datastore.get_packets()
        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0]['id'], 'pkt-1')
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
        now = datetime.now()
        for i in range(5):
            self.collector.handle_packet({'id': f'pkt-{i}', 'rx_time': now})
        packets = self.datastore.get_packets()
        self.assertEqual(len(packets), 5)
        # END_BLOCK_ASSERT_MULTIPLE_PACKETS

if __name__ == '__main__':
    unittest.main()
