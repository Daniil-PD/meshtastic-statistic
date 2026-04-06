# FILE: tests/unit/test_datastore.py
# VERSION: 2.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Модульные тесты для M-DATASTORE с SQLite хранением.
#   SCOPE: [Тестирование add_packet, get_packets, get_packet_count, get_unique_senders, clear, close, get_storage_stats, cleanup_old_data]
#   DEPENDS: [M-DATASTORE]
#   LINKS: [V-M-DATASTORE]
# END_MODULE_CONTRACT

import unittest
import os
import tempfile
from datetime import datetime, timedelta
from src.datastore import DataStore

# START_CONTRACT: TestDataStore
#   PURPOSE: Тестирование DataStore с SQLite базой данных.
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
    #   SIDE_EFFECTS: [Создает временную базу данных]
    #   LINKS: []
    # END_CONTRACT: setUp
    def setUp(self):
        # START_BLOCK_INIT_TEST_DB
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.store = DataStore(db_path=self.test_db.name, retention_months=6)
        # END_BLOCK_INIT_TEST_DB

    # START_CONTRACT: tearDown
    #   PURPOSE: Очистка после теста.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Закрывает подключение и удаляет файл БД]
    #   LINKS: []
    # END_CONTRACT: tearDown
    def tearDown(self):
        # START_BLOCK_CLEANUP_TEST
        self.store.close()
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        # END_BLOCK_CLEANUP_TEST

    # START_CONTRACT: test_add_packet
    #   PURPOSE: Тестирование добавления пакета.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [add_packet]
    # END_CONTRACT: test_add_packet
    def test_add_packet(self):
        # START_BLOCK_ASSERT_ADD_PACKET
        packet = {'id': 'test-1', 'data': 'test', 'rx_time': datetime.now()}
        result = self.store.add_packet(packet)
        self.assertTrue(result)
        packets = self.store.get_packets()
        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0]['id'], 'test-1')
        # END_BLOCK_ASSERT_ADD_PACKET

    # START_CONTRACT: test_add_packet_without_id
    #   PURPOSE: Тестирование добавления пакета без ID.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [add_packet]
    # END_CONTRACT: test_add_packet_without_id
    def test_add_packet_without_id(self):
        # START_BLOCK_ASSERT_ADD_PACKET_NO_ID
        packet = {'data': 'test'}
        result = self.store.add_packet(packet)
        self.assertFalse(result)
        packets = self.store.get_packets()
        self.assertEqual(len(packets), 0)
        # END_BLOCK_ASSERT_ADD_PACKET_NO_ID

    # START_CONTRACT: test_get_packets_all
    #   PURPOSE: Тестирование получения всех пакетов.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [get_packets]
    # END_CONTRACT: test_get_packets_all
    def test_get_packets_all(self):
        # START_BLOCK_ASSERT_GET_PACKETS_ALL
        now = datetime.now()
        self.store.add_packet({'id': '1', 'rx_time': now})
        self.store.add_packet({'id': '2', 'rx_time': now})
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
        self.store.add_packet({'id': '1', 'rx_time': now - timedelta(hours=2)})
        self.store.add_packet({'id': '2', 'rx_time': now - timedelta(hours=1)})
        self.store.add_packet({'id': '3', 'rx_time': now})
        
        start = now - timedelta(hours=1, minutes=30)
        packets = self.store.get_packets(start_time=start)
        self.assertEqual(len(packets), 2)
        # END_BLOCK_ASSERT_GET_PACKETS_PERIOD

    # START_CONTRACT: test_get_packet_count
    #   PURPOSE: Тестирование подсчета количества пакетов.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [get_packet_count]
    # END_CONTRACT: test_get_packet_count
    def test_get_packet_count(self):
        # START_BLOCK_ASSERT_GET_PACKET_COUNT
        now = datetime.now()
        self.store.add_packet({'id': '1', 'rx_time': now})
        self.store.add_packet({'id': '2', 'rx_time': now})
        self.store.add_packet({'id': '3', 'rx_time': now})
        
        count = self.store.get_packet_count()
        self.assertEqual(count, 3)
        # END_BLOCK_ASSERT_GET_PACKET_COUNT

    # START_CONTRACT: test_get_unique_senders
    #   PURPOSE: Тестирование получения уникальных отправителей.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [get_unique_senders]
    # END_CONTRACT: test_get_unique_senders
    def test_get_unique_senders(self):
        # START_BLOCK_ASSERT_GET_UNIQUE_SENDERS
        now = datetime.now()
        self.store.add_packet({'id': '1', 'from_id': 'user1', 'rx_time': now})
        self.store.add_packet({'id': '2', 'from_id': 'user2', 'rx_time': now})
        self.store.add_packet({'id': '3', 'from_id': 'user1', 'rx_time': now})
        
        senders = self.store.get_unique_senders()
        self.assertEqual(len(senders), 2)
        self.assertIn('user1', senders)
        self.assertIn('user2', senders)
        # END_BLOCK_ASSERT_GET_UNIQUE_SENDERS

    # START_CONTRACT: test_clear
    #   PURPOSE: Тестирование очистки хранилища.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [clear]
    # END_CONTRACT: test_clear
    def test_clear(self):
        # START_BLOCK_ASSERT_CLEAR
        now = datetime.now()
        self.store.add_packet({'id': '1', 'rx_time': now})
        self.store.clear()
        packets = self.store.get_packets()
        self.assertEqual(len(packets), 0)
        # END_BLOCK_ASSERT_CLEAR

    # START_CONTRACT: test_get_storage_stats
    #   PURPOSE: Тестирование получения статистики хранилища.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [get_storage_stats]
    # END_CONTRACT: test_get_storage_stats
    def test_get_storage_stats(self):
        # START_BLOCK_ASSERT_GET_STORAGE_STATS
        now = datetime.now()
        self.store.add_packet({'id': '1', 'from_id': 'user1', 'rx_time': now})
        self.store.add_packet({'id': '2', 'from_id': 'user2', 'rx_time': now})
        
        stats = self.store.get_storage_stats()
        self.assertEqual(stats['total_packets'], 2)
        self.assertEqual(stats['unique_senders'], 2)
        self.assertEqual(stats['retention_months'], 6)
        # END_BLOCK_ASSERT_GET_STORAGE_STATS

    # START_CONTRACT: test_close
    #   PURPOSE: Тестирование закрытия подключения.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [close]
    # END_CONTRACT: test_close
    def test_close(self):
        # START_BLOCK_ASSERT_CLOSE
        self.store.close()
        # После закрытия попытка добавить пакет должна вернуть False
        result = self.store.add_packet({'id': 'test', 'rx_time': datetime.now()})
        self.assertFalse(result)
        # END_BLOCK_ASSERT_CLOSE

    # START_CONTRACT: test_cleanup_old_data
    #   PURPOSE: Тестирование очистки старых данных.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: []
    #   LINKS: [_cleanup_old_data]
    # END_CONTRACT: test_cleanup_old_data
    def test_cleanup_old_data(self):
        # START_BLOCK_ASSERT_CLEANUP_OLD_DATA
        now = datetime.now()
        old_time = now - timedelta(days=200)  # Старше 6 месяцев
        
        # Добавляем старый пакет
        self.store.add_packet({'id': 'old-1', 'rx_time': old_time})
        # Добавляем новый пакет
        self.store.add_packet({'id': 'new-1', 'rx_time': now})
        
        # Принудительно вызываем очистку
        deleted = self.store._cleanup_old_data()
        
        # Старый пакет должен быть удален
        packets = self.store.get_packets()
        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0]['id'], 'new-1')
        # END_BLOCK_ASSERT_CLEANUP_OLD_DATA

if __name__ == '__main__':
    unittest.main()
