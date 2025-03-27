import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Конфигурационные параметры
AMO_DOMAIN = os.getenv("AMO_DOMAIN")
CLIENT_ID = os.getenv("CLIENT_ID")
AMO_API_KEY = os.getenv("AMO_API_KEY")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Проверка наличия всех необходимых параметров
if not all([AMO_DOMAIN, AMO_API_KEY]):
    raise ValueError("Не все необходимые параметры указаны в .env файле") 