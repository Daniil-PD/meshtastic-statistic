# FILE: src/config.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Управляет конфигурацией приложения.
#   SCOPE: [Загрузка конфигурации из переменных окружения]
#   DEPENDS: []
#   LINKS: [M-CONFIG]
# END_MODULE_CONTRACT

import os

# START_CONTRACT: load_config
#   PURPOSE: Загружает конфигурацию из переменных окружения.
#   INPUTS: {}
#   OUTPUTS: {dict: Конфигурация приложения}
#   SIDE_EFFECTS: [Читает переменные окружения]
#   LINKS: []
# END_CONTRACT: load_config
def load_config():
    # START_BLOCK_VALIDATE_INPUT
    config = {}
    # END_BLOCK_VALIDATE_INPUT

    # START_BLOCK_LOAD_ENV_VARS
    config['TELEGRAM_TOKEN'] = os.getenv('TELEGRAM_TOKEN')
    config['WEATHER_API_KEY'] = os.getenv('WEATHER_API_KEY')
    # END_BLOCK_LOAD_ENV_VARS

    return config

# START_MODULE_MAP
#   load_config - Загружает конфигурацию из переменных окружения.
# END_MODULE_MAP
