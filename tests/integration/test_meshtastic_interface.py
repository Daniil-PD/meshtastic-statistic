# FILE: tests/integration/test_meshtastic_interface.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Интеграционные тесты для MeshtasticInterface.
#   SCOPE: [Тестирование подключения, отправки сообщений, обработки ошибок]
#   DEPENDS: [M-MESHTASTIC, M-CONFIG]
#   LINKS: [V-M-MESHTASTIC]
# END_MODULE_CONTRACT

import pytest
from unittest.mock import patch, MagicMock
from src.meshtastic_interface import MeshtasticInterface

# START_CONTRACT: test_interface_init
#   PURPOSE: Проверяет инициализацию интерфейса.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [MeshtasticInterface.__init__]
# END_CONTRACT: test_interface_init
def test_interface_init():
    # START_BLOCK_TEST_INIT_WITH_CONFIG
    config = {'TELEGRAM_TOKEN': 'test_token', 'MESHTASTIC_NODE_ID': '!12345678'}
    interface = MeshtasticInterface(config)
    assert interface._telegram_token == 'test_token'
    assert interface._node_id == '!12345678'
    assert interface._connected == False
    # END_BLOCK_TEST_INIT_WITH_CONFIG
    
    # START_BLOCK_TEST_INIT_DEFAULT_CONFIG
    with patch('src.meshtastic_interface.load_config') as mock_load:
        mock_load.return_value = {'TELEGRAM_TOKEN': 'default_token', 'MESHTASTIC_NODE_ID': '!87654321'}
        interface2 = MeshtasticInterface()
        assert interface2._telegram_token == 'default_token'
        assert interface2._node_id == '!87654321'
    # END_BLOCK_TEST_INIT_DEFAULT_CONFIG

# START_CONTRACT: test_connect_success
#   PURPOSE: Проверяет успешное подключение.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [MeshtasticInterface.connect]
# END_CONTRACT: test_connect_success
def test_connect_success():
    # START_BLOCK_TEST_CONNECT
    interface = MeshtasticInterface({'MESHTASTIC_NODE_ID': '!12345678'})
    result = interface.connect()
    
    assert result == True
    assert interface.is_connected() == True
    # END_BLOCK_TEST_CONNECT

# START_CONTRACT: test_connect_no_node_id
#   PURPOSE: Проверяет ошибку подключения без Node ID.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [MeshtasticInterface.connect]
# END_CONTRACT: test_connect_no_node_id
def test_connect_no_node_id():
    # START_BLOCK_TEST_CONNECT_MISSING_NODE
    interface = MeshtasticInterface({'MESHTASTIC_NODE_ID': None})
    result = interface.connect()
    
    assert result == False
    assert interface.is_connected() == False
    # END_BLOCK_TEST_CONNECT_MISSING_NODE

# START_CONTRACT: test_disconnect
#   PURPOSE: Проверяет отключение от сети.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [MeshtasticInterface.disconnect]
# END_CONTRACT: test_disconnect
def test_disconnect():
    # START_BLOCK_TEST_DISCONNECT_FLOW
    interface = MeshtasticInterface({'MESHTASTIC_NODE_ID': '!12345678'})
    interface.connect()
    assert interface.is_connected() == True
    
    interface.disconnect()
    assert interface.is_connected() == False
    # END_BLOCK_TEST_DISCONNECT_FLOW

# START_CONTRACT: test_send_message_success
#   PURPOSE: Проверяет успешную отправку сообщения.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [MeshtasticInterface.send_message]
# END_CONTRACT: test_send_message_success
def test_send_message_success():
    # START_BLOCK_TEST_SEND_SUCCESS
    interface = MeshtasticInterface({'TELEGRAM_TOKEN': 'valid_token', 'MESHTASTIC_NODE_ID': '!12345678'})
    interface.connect()
    
    result = interface.send_message("Hello, Meshtastic!", "!87654321")
    
    assert result == True
    assert len(interface.get_sent_messages()) == 1
    assert interface.get_sent_messages()[0]['message'] == "Hello, Meshtastic!"
    # END_BLOCK_TEST_SEND_SUCCESS

# START_CONTRACT: test_send_message_not_connected
#   PURPOSE: Проверяет ошибку отправки без подключения.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [MeshtasticInterface.send_message]
# END_CONTRACT: test_send_message_not_connected
def test_send_message_not_connected():
    # START_BLOCK_TEST_SEND_NOT_CONNECTED
    interface = MeshtasticInterface({'TELEGRAM_TOKEN': 'test_token', 'MESHTASTIC_NODE_ID': '!12345678'})
    # Не подключаемся
    
    result = interface.send_message("Hello")
    
    assert result == False
    # END_BLOCK_TEST_SEND_NOT_CONNECTED

# START_CONTRACT: test_send_message_empty
#   PURPOSE: Проверяет ошибку отправки пустого сообщения.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [MeshtasticInterface.send_message]
# END_CONTRACT: test_send_message_empty
def test_send_message_empty():
    # START_BLOCK_TEST_SEND_EMPTY
    interface = MeshtasticInterface({'TELEGRAM_TOKEN': 'test_token', 'MESHTASTIC_NODE_ID': '!12345678'})
    interface.connect()
    
    result = interface.send_message("")
    
    assert result == False
    # END_BLOCK_TEST_SEND_EMPTY

# START_CONTRACT: test_send_message_invalid_token
#   PURPOSE: Проверяет ошибку отправки с невалидным токеном.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [MeshtasticInterface.send_message, MeshtasticInterface._send_mock_message]
# END_CONTRACT: test_send_message_invalid_token
def test_send_message_invalid_token():
    # START_BLOCK_TEST_SEND_INVALID_TOKEN
    interface = MeshtasticInterface({'TELEGRAM_TOKEN': 'INVALID_TOKEN', 'MESHTASTIC_NODE_ID': '!12345678'})
    interface.connect()
    
    result = interface.send_message("Hello")
    
    assert result == False
    # END_BLOCK_TEST_SEND_INVALID_TOKEN

# START_CONTRACT: test_send_message_broadcast
#   PURPOSE: Проверяет отправку broadcast сообщения.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [MeshtasticInterface.send_message]
# END_CONTRACT: test_send_message_broadcast
def test_send_message_broadcast():
    # START_BLOCK_TEST_BROADCAST
    interface = MeshtasticInterface({'TELEGRAM_TOKEN': 'test_token', 'MESHTASTIC_NODE_ID': '!12345678'})
    interface.connect()
    
    result = interface.send_message("Broadcast message")
    
    assert result == True
    assert interface.get_sent_messages()[0]['destination'] is None
    # END_BLOCK_TEST_BROADCAST

# START_CONTRACT: test_get_sent_messages_empty
#   PURPOSE: Проверяет получение пустого списка сообщений.
#   INPUTS: {}
#   OUTPUTS: {None}
#   SIDE_EFFECTS: [none]
#   LINKS: [MeshtasticInterface.get_sent_messages]
# END_CONTRACT: test_get_sent_messages_empty
def test_get_sent_messages_empty():
    # START_BLOCK_TEST_EMPTY_SENT
    interface = MeshtasticInterface({'TELEGRAM_TOKEN': 'test_token', 'MESHTASTIC_NODE_ID': '!12345678'})
    assert interface.get_sent_messages() == []
    # END_BLOCK_TEST_EMPTY_SENT

# START_MODULE_MAP
#   test_interface_init - Проверяет инициализацию интерфейса.
#   test_connect_success - Проверяет успешное подключение.
#   test_connect_no_node_id - Проверяет ошибку подключения без Node ID.
#   test_disconnect - Проверяет отключение от сети.
#   test_send_message_success - Проверяет успешную отправку сообщения.
#   test_send_message_not_connected - Проверяет ошибку отправки без подключения.
#   test_send_message_empty - Проверяет ошибку отправки пустого сообщения.
#   test_send_message_invalid_token - Проверяет ошибку отправки с невалидным токеном.
#   test_send_message_broadcast - Проверяет отправку broadcast сообщения.
#   test_get_sent_messages_empty - Проверяет получение пустого списка сообщений.
# END_MODULE_MAP

# START_CHANGE_SUMMARY
#   LAST_CHANGE: v1.0.0 - Initial tests for MeshtasticInterface
# END_CHANGE_SUMMARY
