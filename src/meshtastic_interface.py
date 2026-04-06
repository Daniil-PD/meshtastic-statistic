# FILE: src/meshtastic_interface.py
# VERSION: 2.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Управляет взаимодействием с Meshtastic через последовательный порт.
#   SCOPE: [Подключение через serial port, отправка сообщений, управление подключением]
#   DEPENDS: [M-CONFIG, meshtastic library]
#   LINKS: [M-MESHTASTIC]
# END_MODULE_CONTRACT

import logging
from typing import Dict, Any, Optional, Callable
from src.config import load_config

try:
    from pubsub import pub
    PUBSUB_AVAILABLE = True
except ImportError:
    PUBSUB_AVAILABLE = False

logger = logging.getLogger(__name__)

# START_CONTRACT: MeshtasticInterface
#   PURPOSE: Интерфейс для взаимодействия с Meshtastic через serial port.
#   INPUTS: {}
#   OUTPUTS: {}
#   SIDE_EFFECTS: []
#   LINKS: []
# END_CONTRACT: MeshtasticInterface
class MeshtasticInterface:
    # START_CONTRACT: __init__
    #   PURPOSE: Инициализирует интерфейс Meshtastic.
    #   INPUTS: {config: Optional[Dict[str, Any]] - Конфигурация}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Загружает конфигурацию]
    #   LINKS: [load_config]
    # END_CONTRACT: __init__
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # START_BLOCK_INIT_CONFIG
        if config is None:
            config = load_config()
        self._telegram_token = config.get('TELEGRAM_TOKEN')
        self._serial_port = config.get('MESHTASTIC_SERIAL_PORT')
        # END_BLOCK_INIT_CONFIG
        
        # START_BLOCK_INIT_STATE
        self._connected = False
        self._sent_messages = []
        self._interface = None
        self._node = None
        self._packet_listener: Optional[Callable] = None
        # END_BLOCK_INIT_STATE
        
        # START_BLOCK_INIT_LOG
        logger.info("[MeshtasticInterface][__init__] Service initialized")
        # END_BLOCK_INIT_LOG

    # START_CONTRACT: set_packet_listener
    #   PURPOSE: Устанавливает обработчик входящих пакетов.
    #   INPUTS: {listener: Callable - Функция обратного вызова для обработки пакетов}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: set_packet_listener
    def set_packet_listener(self, listener: Callable) -> None:
        # START_BLOCK_SET_LISTENER
        self._packet_listener = listener
        logger.info("[MeshtasticInterface][set_packet_listener] Packet listener registered")
        # END_BLOCK_SET_LISTENER

    # START_CONTRACT: connect
    #   PURPOSE: Подключается к сети Meshtastic через serial port.
    #   INPUTS: {}
    #   OUTPUTS: {bool - True если подключение успешно}
    #   SIDE_EFFECTS: [Устанавливает флаг connected=True, создаёт SerialInterface]
    #   LINKS: [meshtastic.serial_interface.SerialInterface]
    # END_CONTRACT: connect
    def connect(self) -> bool:
        # START_BLOCK_VALIDATE_SERIAL_PORT
        if not self._serial_port:
            logger.warning("[MeshtasticInterface][connect] Serial port not configured, trying auto-detect")
        # END_BLOCK_VALIDATE_SERIAL_PORT
        
        # START_BLOCK_CONNECT
        try:
            import meshtastic.serial_interface
            
            if self._serial_port:
                self._interface = meshtastic.serial_interface.SerialInterface(devPath=self._serial_port)
            else:
                self._interface = meshtastic.serial_interface.SerialInterface()
            
            self._node = self._interface.getNode('^local')
            self._connected = True
            
            # START_BLOCK_SUBSCRIBE_RECEIVE
            if PUBSUB_AVAILABLE and self._packet_listener:
                pub.subscribe(self._on_receive, "meshtastic.receive")
                logger.info("[MeshtasticInterface][connect] Subscribed to meshtastic.receive")
            # END_BLOCK_SUBSCRIBE_RECEIVE
            
            logger.info(f"[MeshtasticInterface][connect] Connected via {self._serial_port or 'auto'}")
            return True
        except Exception as e:
            logger.error(f"[MeshtasticInterface][connect] Failed to connect: {e}")
            self._connected = False
            return False
        # END_BLOCK_CONNECT

    # START_CONTRACT: _on_receive
    #   PURPOSE: Обработчик входящих пакетов от Meshtastic.
    #   INPUTS: {packet: Dict - Входящий пакет, interface: Interface - Интерфейс}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Вызывает зарегистрированный listener]
    #   LINKS: []
    # END_CONTRACT: _on_receive
    def _on_receive(self, packet: Dict[str, Any], interface: Any = None) -> None:
        # START_BLOCK_INVOKE_LISTENER
        if self._packet_listener:
            logger.debug(f"[MeshtasticInterface][_on_receive] Received packet: {packet.get('id')}")
            self._packet_listener(packet)
        # END_BLOCK_INVOKE_LISTENER

    # START_CONTRACT: disconnect
    #   PURPOSE: Отключается от сети Meshtastic.
    #   INPUTS: {}
    #   OUTPUTS: {None}
    #   SIDE_EFFECTS: [Устанавливает флаг connected=False, закрывает интерфейс]
    #   LINKS: []
    # END_CONTRACT: disconnect
    def disconnect(self) -> None:
        # START_BLOCK_DISCONNECT
        if self._interface:
            self._interface.close()
            self._interface = None
        self._connected = False
        self._node = None
        logger.info("[MeshtasticInterface][disconnect] Disconnected")
        # END_BLOCK_DISCONNECT

    # START_CONTRACT: send_message
    #   PURPOSE: Отправляет сообщение в сеть Meshtastic.
    #   INPUTS: {message: str - Текст сообщения, destination: Optional[str] - Адресат}
    #   OUTPUTS: {bool - True если отправка успешна}
    #   SIDE_EFFECTS: [Отправляет сообщение через serial interface]
    #   LINKS: []
    # END_CONTRACT: send_message
    def send_message(self, message: str, destination: Optional[str] = None) -> bool:
        # START_BLOCK_VALIDATE_CONNECTION
        if not self._connected:
            logger.error("[MeshtasticInterface][send_message] Not connected")
            return False
        # END_BLOCK_VALIDATE_CONNECTION
        
        # START_BLOCK_VALIDATE_MESSAGE
        if not message:
            logger.error("[MeshtasticInterface][send_message] Empty message")
            return False
        # END_BLOCK_VALIDATE_MESSAGE
        
        # START_BLOCK_LOG_SEND
        dest = destination or 'broadcast'
        logger.info(f"[MeshtasticInterface][send_message] Sending to {dest}: {message[:50]}...")
        # END_BLOCK_LOG_SEND
        
        # START_BLOCK_SEND_MESSAGE
        try:
            if self._interface:
                self._interface.sendText(message, destinationId=destination)
                success = True
            else:
                success = False
        except Exception as e:
            logger.error(f"[MeshtasticInterface][send_message] Send failed: {e}")
            success = False
        # END_BLOCK_SEND_MESSAGE
        
        if success:
            # START_BLOCK_LOG_SENT
            self._sent_messages.append({'message': message, 'destination': destination})
            logger.info("[MeshtasticInterface][send_message] Message sent successfully")
            # END_BLOCK_LOG_SENT
        else:
            # START_BLOCK_LOG_SEND_ERROR
            logger.error("[MeshtasticInterface][send_message] Failed to send message")
            # END_BLOCK_LOG_SEND_ERROR
        
        return success

    # START_CONTRACT: is_connected
    #   PURPOSE: Проверяет, подключен ли интерфейс.
    #   INPUTS: {}
    #   OUTPUTS: {bool - True если подключен}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: is_connected
    def is_connected(self) -> bool:
        # START_BLOCK_CHECK_CONNECTED
        return self._connected
        # END_BLOCK_CHECK_CONNECTED

    # START_CONTRACT: get_sent_messages
    #   PURPOSE: Возвращает список отправленных сообщений.
    #   INPUTS: {}
    #   OUTPUTS: {List[Dict[str, Any]] - Список отправленных сообщений}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: get_sent_messages
    def get_sent_messages(self) -> list:
        # START_BLOCK_RETURN_SENT
        return self._sent_messages.copy()
        # END_BLOCK_RETURN_SENT

    # START_CONTRACT: get_node_info
    #   PURPOSE: Возвращает информацию о локальном узле.
    #   INPUTS: {}
    #   OUTPUTS: {Optional[Dict] - Информация об узле или None}
    #   SIDE_EFFECTS: [none]
    #   LINKS: []
    # END_CONTRACT: get_node_info
    def get_node_info(self) -> Optional[Dict[str, Any]]:
        # START_BLOCK_GET_NODE_INFO
        if self._node and self._node.localConfig:
            return {
                'node_id': self._node_id,
                'local_config': str(self._node.localConfig),
            }
        return None
        # END_BLOCK_GET_NODE_INFO

# START_MODULE_MAP
#   MeshtasticInterface - Интерфейс для взаимодействия с Meshtastic через serial port.
#   __init__ - Инициализирует интерфейс Meshtastic.
#   connect - Подключается к сети Meshtastic через serial port.
#   disconnect - Отключается от сети Meshtastic.
#   send_message - Отправляет сообщение в сеть Meshtastic.
#   is_connected - Проверяет, подключен ли интерфейс.
#   get_sent_messages - Возвращает список отправленных сообщений.
#   get_node_info - Возвращает информацию о локальном узле.
#   set_packet_listener - Устанавливает обработчик входящих пакетов.
#   _on_receive - Обработчик входящих пакетов от Meshtastic.
# END_MODULE_MAP

# START_CHANGE_SUMMARY
#   LAST_CHANGE: v2.0.2 - Добавлена поддержка получения входящих пакетов через pubsub (set_packet_listener, _on_receive)
# END_CHANGE_SUMMARY
