import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Конфигурационные параметры для упрощенной авторизации OAuth
AMO_DOMAIN = os.getenv("AMO_DOMAIN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTH_CODE = os.getenv("AUTH_CODE")
REDIRECT_URI = os.getenv("REDIRECT_URI")
ACCESS_TOKEN_FILE = os.getenv("ACCESS_TOKEN_FILE", "access_token.json")

# Проверка наличия всех необходимых параметров
if not all([AMO_DOMAIN, CLIENT_ID, CLIENT_SECRET, AUTH_CODE, REDIRECT_URI]):
    raise ValueError("Не все необходимые параметры указаны в .env файле") 