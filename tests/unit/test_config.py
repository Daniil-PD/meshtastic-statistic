# FILE: tests/unit/test_config.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Модульные тесты для M-CONFIG.
#   SCOPE: [Тестирование функции load_config]
#   DEPENDS: [M-CONFIG]
#   LINKS: [V-M-CONFIG]
# END_MODULE_CONTRACT

import os
import unittest
from unittest.mock import patch
from src.config import load_config

# START_CONTRACT: TestConfigManager
#   PURPOSE: Тестирование ConfigManager.
#   INPUTS: {}
#   OUTPUTS: {}
#   SIDE_EFFECTS: []
#   LINKS: []
# END_CONTRACT: TestConfigManager
class TestConfigManager(unittest.TestCase):

    # START_CONTRACT: test_load_config
    #   PURPOSE: Тестирование загрузки конфигурации.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Модифицирует переменные окружения для теста]
    #   LINKS: [load_config]
    # END_CONTRACT: test_load_config
    @patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'WEATHER_API_KEY': 'test_api_key'
    })
    def test_load_config(self):
        # START_BLOCK_ASSERT_CONFIG
        config = load_config()
        self.assertEqual(config['TELEGRAM_TOKEN'], 'test_token')
        self.assertEqual(config['WEATHER_API_KEY'], 'test_api_key')
        # END_BLOCK_ASSERT_CONFIG

    # START_CONTRACT: test_load_config_missing_values
    #   PURPOSE: Тестирование с отсутствующими переменными окружения.
    #   INPUTS: {}
    #   OUTPUTS: {}
    #   SIDE_EFFECTS: [Модифицирует переменные окружения для теста]
    #   LINKS: [load_config]
    # END_CONTRACT: test_load_config_missing_values
    @patch.dict(os.environ, {})
    def test_load_config_missing_values(self):
        # START_BLOCK_ASSERT_MISSING_CONFIG
        config = load_config()
        self.assertIsNone(config.get('TELEGRAM_TOKEN'))
        self.assertIsNone(config.get('WEATHER_API_KEY'))
        # END_BLOCK_ASSERT_MISSING_CONFIG

if __name__ == '__main__':
    unittest.main()