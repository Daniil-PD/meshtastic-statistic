# FILE: src/datastore.py
# VERSION: 2.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Хранит пакеты Meshtastic в SQLite базе данных с политикой хранения 6 месяцев.
#   SCOPE: [Добавление, получение, очистка пакетов и автоматическое удаление устаревших данных]
#   DEPENDS: [sqlite3, datetime]
#   LINKS: [M-DATASTORE]
# END_MODULE_CONTRACT

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# START_CONTRACT: DataStore
#   PURPOSE: Хранит пакеты Meshtastic в SQLite базе данных.
#   INPUTS: {db_path: str - Путь к файлу базы данных, retention_months: int - Срок хранения данных в месяцах}
#   OUTPUTS: {}
#   SIDE_EFFECTS: [Создает файл базы данных, создает таблицу packets]
#   LINKS: []
# END_CONTRACT: DataStore
class DataStore:
    # START_BLOCK_CONSTANTS
    # Константы
    DEFAULT_DB_PATH = "data/meshtastic.db"
    DEFAULT_RETENTION_MONTHS = 6
    # END_BLOCK_CONSTANTS

    # START_CONTRACT: __init__
    #   PURPOSE: Инициализирует хранилище данных с SQLite базой.
    #   INPUTS: {db_path: Optional[str] - Путь к файлу БД, retention_months: int - Срок хранения в месяцах}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Создает подключение к БД, создает таблицу если не существует]
    #   LINKS: []
    # END_CONTRACT: __init__
    def __init__(self, db_path: Optional[str] = None, retention_months: int = DEFAULT_RETENTION_MONTHS):
        # START_BLOCK_INIT_DB_PATH
        if db_path is None:
            db_path = self.DEFAULT_DB_PATH
        
        self._db_path = db_path
        self._retention_months = retention_months
        self._conn: Optional[sqlite3.Connection] = None
        # END_BLOCK_INIT_DB_PATH
        
        # START_BLOCK_INIT_CONNECTION
        self._connect()
        self._create_table()
        # END_BLOCK_INIT_CONNECTION

    # START_CONTRACT: _connect
    #   PURPOSE: Устанавливает подключение к базе данных.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Создает подключение к SQLite]
    #   LINKS: []
    # END_CONTRACT: _connect
    def _connect(self) -> None:
        # START_BLOCK_CREATE_CONNECTION
        db_dir = Path(self._db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        logger.info(f"[DataStore][_connect] Connected to database: {self._db_path}")
        # END_BLOCK_CREATE_CONNECTION

    # START_CONTRACT: _create_table
    #   PURPOSE: Создает таблицу для хранения пакетов.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Создает таблицу packets если не существует]
    #   LINKS: []
    # END_CONTRACT: _create_table
    def _create_table(self) -> None:
        # START_BLOCK_CREATE_TABLE_STATEMENT
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS packets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            packet_id TEXT UNIQUE NOT NULL,
            from_id TEXT,
            to_id TEXT,
            portnum INTEGER,
            rx_time TIMESTAMP NOT NULL,
            rx_snr REAL,
            rx_rssi REAL,
            channel INTEGER,
            decoded_data TEXT,
            raw_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        # END_BLOCK_CREATE_TABLE_STATEMENT
        
        # START_BLOCK_EXECUTE_CREATE_TABLE
        self._conn.execute(create_table_sql)
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_rx_time ON packets(rx_time)")
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_from_id ON packets(from_id)")
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_to_id ON packets(to_id)")
        self._conn.commit()
        logger.info("[DataStore][_create_table] Table created and indexes added")
        # END_BLOCK_EXECUTE_CREATE_TABLE

    # START_CONTRACT: _cleanup_old_data
    #   PURPOSE: Удаляет данные старше срока хранения.
    #   INPUTS: {}
    #   OUTPUTS: {int - Количество удаленных записей}
    #   SIDE_EFFECTS: [Удаляет старые записи из базы данных]
    #   LINKS: []
    # END_CONTRACT: _cleanup_old_data
    def _cleanup_old_data(self) -> int:
        # START_BLOCK_CALCULATE_CUTOFF_DATE
        cutoff_date = datetime.now() - timedelta(days=self._retention_months * 30)
        # END_BLOCK_CALCULATE_CUTOFF_DATE
        
        # START_BLOCK_DELETE_OLD_RECORDS
        delete_sql = "DELETE FROM packets WHERE rx_time < ?"
        cursor = self._conn.execute(delete_sql, (cutoff_date,))
        deleted_count = cursor.rowcount
        self._conn.commit()
        
        if deleted_count > 0:
            logger.info(f"[DataStore][_cleanup_old_data] Deleted {deleted_count} records older than {cutoff_date}")
        # END_BLOCK_DELETE_OLD_RECORDS
        
        return deleted_count

    # START_CONTRACT: add_packet
    #   PURPOSE: Добавляет пакет в хранилище.
    #   INPUTS: {packet: Dict[str, Any] - Пакет для добавления}
    #   OUTPUTS: {bool - True если пакет добавлен}
    #   SIDE_EFFECTS: [Добавляет пакет в базу данных, запускает очистку старых данных]
    #   LINKS: []
    # END_CONTRACT: add_packet
    def add_packet(self, packet: Dict[str, Any]) -> bool:
        # START_BLOCK_CHECK_CONNECTION
        if self._conn is None:
            logger.warning("[DataStore][add_packet] Database connection is closed")
            return False
        # END_BLOCK_CHECK_CONNECTION
        
        # START_BLOCK_EXTRACT_PACKET_DATA
        packet_id = packet.get('id')
        if packet_id is None:
            logger.warning("[DataStore][add_packet] Packet has no ID, skipping")
            return False
        
        rx_time = packet.get('rx_time')
        if rx_time is None:
            rx_time = datetime.now()
        # END_BLOCK_EXTRACT_PACKET_DATA
        
        # START_BLOCK_SERIALIZE_PACKET
        raw_data = json.dumps(packet, default=str)
        decoded_data = json.dumps(packet.get('decoded', {}), default=str) if 'decoded' in packet else None
        # END_BLOCK_SERIALIZE_PACKET
        
        # START_BLOCK_INSERT_PACKET
        insert_sql = """
        INSERT OR REPLACE INTO packets 
        (packet_id, from_id, to_id, portnum, rx_time, rx_snr, rx_rssi, channel, decoded_data, raw_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            self._conn.execute(insert_sql, (
                packet_id,
                packet.get('from_id'),
                packet.get('to_id'),
                packet.get('portnum'),
                rx_time,
                packet.get('rx_snr'),
                packet.get('rx_rssi'),
                packet.get('channel'),
                decoded_data,
                raw_data
            ))
            self._conn.commit()
            logger.debug(f"[DataStore][add_packet] Packet saved: {packet_id}")
        except sqlite3.Error as e:
            logger.error(f"[DataStore][add_packet] Error saving packet {packet_id}: {e}")
            return False
        # END_BLOCK_INSERT_PACKET
        
        # START_BLOCK_RUN_CLEANUP
        self._cleanup_old_data()
        # END_BLOCK_RUN_CLEANUP
        
        return True

    # START_CONTRACT: get_packets
    #   PURPOSE: Возвращает все пакеты за период.
    #   INPUTS: {start_time: Optional[datetime] - Начало периода, end_time: Optional[datetime] - Конец периода}
    #   OUTPUTS: {List[Dict[str, Any]] - Список пакетов}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: get_packets
    def get_packets(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        # START_BLOCK_BUILD_QUERY
        query = "SELECT * FROM packets WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND rx_time >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND rx_time <= ?"
            params.append(end_time)
        
        query += " ORDER BY rx_time DESC"
        # END_BLOCK_BUILD_QUERY
        
        # START_BLOCK_EXECUTE_QUERY
        cursor = self._conn.execute(query, params)
        rows = cursor.fetchall()
        # END_BLOCK_EXECUTE_QUERY
        
        # START_BLOCK_DESERIALIZE_PACKETS
        result = []
        for row in rows:
            packet = json.loads(row['raw_data'])
            result.append(packet)
        
        logger.debug(f"[DataStore][get_packets] Retrieved {len(result)} packets")
        # END_BLOCK_DESERIALIZE_PACKETS
        
        return result

    # START_CONTRACT: get_packet_count
    #   PURPOSE: Возвращает количество пакетов за период.
    #   INPUTS: {start_time: Optional[datetime] - Начало периода, end_time: Optional[datetime] - Конец периода}
    #   OUTPUTS: {int - Количество пакетов}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: get_packet_count
    def get_packet_count(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        # START_BLOCK_BUILD_COUNT_QUERY
        query = "SELECT COUNT(*) FROM packets WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND rx_time >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND rx_time <= ?"
            params.append(end_time)
        # END_BLOCK_BUILD_COUNT_QUERY
        
        # START_BLOCK_EXECUTE_COUNT_QUERY
        cursor = self._conn.execute(query, params)
        count = cursor.fetchone()[0]
        # END_BLOCK_EXECUTE_COUNT_QUERY
        
        return count

    # START_CONTRACT: get_unique_senders
    #   PURPOSE: Возвращает список уникальных отправителей за период.
    #   INPUTS: {start_time: Optional[datetime] - Начало периода, end_time: Optional[datetime] - Конец периода}
    #   OUTPUTS: {List[str] - Список уникальных отправителей}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: get_unique_senders
    def get_unique_senders(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[str]:
        # START_BLOCK_BUILD_SENDERS_QUERY
        query = "SELECT DISTINCT from_id FROM packets WHERE from_id IS NOT NULL AND 1=1"
        params = []
        
        if start_time:
            query += " AND rx_time >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND rx_time <= ?"
            params.append(end_time)
        # END_BLOCK_BUILD_SENDERS_QUERY
        
        # START_BLOCK_EXECUTE_SENDERS_QUERY
        cursor = self._conn.execute(query, params)
        senders = [row['from_id'] for row in cursor.fetchall()]
        # END_BLOCK_EXECUTE_SENDERS_QUERY
        
        return senders

    # START_CONTRACT: clear
    #   PURPOSE: Очищает хранилище.
    #   INPUTS: {}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Удаляет все пакеты из базы данных]
    #   LINKS: []
    # END_CONTRACT: clear
    def clear(self) -> None:
        # START_BLOCK_CLEAR_STORAGE
        self._conn.execute("DELETE FROM packets")
        self._conn.commit()
        logger.info("[DataStore][clear] Storage cleared")
        # END_BLOCK_CLEAR_STORAGE

    # START_CONTRACT: close
    #   PURPOSE: Закрывает подключение к базе данных.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Закрывает подключение к SQLite]
    #   LINKS: []
    # END_CONTRACT: close
    def close(self) -> None:
        # START_BLOCK_CLOSE_CONNECTION
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("[DataStore][close] Database connection closed")
        # END_BLOCK_CLOSE_CONNECTION

    # START_CONTRACT: get_storage_stats
    #   PURPOSE: Возвращает статистику хранилища.
    #   INPUTS: {}
    #   OUTPUTS: {Dict[str, Any] - Статистика хранилища}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: get_storage_stats
    def get_storage_stats(self) -> Dict[str, Any]:
        # START_BLOCK_GET_TOTAL_COUNT
        total_packets = self.get_packet_count()
        # END_BLOCK_GET_TOTAL_COUNT
        
        # START_BLOCK_GET_DATE_RANGE
        cursor = self._conn.execute("SELECT MIN(rx_time), MAX(rx_time) FROM packets")
        row = cursor.fetchone()
        oldest_packet = row[0]
        newest_packet = row[1]
        # END_BLOCK_GET_DATE_RANGE
        
        # START_BLOCK_GET_UNIQUE_SENDERS_COUNT
        unique_senders = len(self.get_unique_senders())
        # END_BLOCK_GET_UNIQUE_SENDERS_COUNT
        
        # START_BLOCK_BUILD_STATS
        stats = {
            'total_packets': total_packets,
            'unique_senders': unique_senders,
            'oldest_packet': oldest_packet,
            'newest_packet': newest_packet,
            'retention_months': self._retention_months,
        }
        logger.info(f"[DataStore][get_storage_stats] Storage stats: {stats}")
        # END_BLOCK_BUILD_STATS
        
        return stats

# START_MODULE_MAP
#   DataStore - Хранит пакеты Meshtastic в SQLite базе данных.
#   add_packet - Добавляет пакет в хранилище.
#   get_packets - Возвращает все пакеты за период.
#   get_packet_count - Возвращает количество пакетов за период.
#   get_unique_senders - Возвращает список уникальных отправителей за период.
#   clear - Очищает хранилище.
#   close - Закрывает подключение к базе данных.
#   get_storage_stats - Возвращает статистику хранилища.
# END_MODULE_MAP
