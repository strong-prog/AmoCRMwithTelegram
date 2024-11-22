import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

AMOCRM_TOKEN = os.getenv("AMOCRM_TOKEN")
AMOCRM_BASE_URL = os.getenv("AMOCRM_BASE_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Проверка на обязательные переменные
required_vars = [TELEGRAM_TOKEN, AMOCRM_TOKEN, AMOCRM_BASE_URL, TELEGRAM_CHAT_ID]
if not all(required_vars):
    raise ValueError("Не удалось загрузить все обязательные переменные из .env")
