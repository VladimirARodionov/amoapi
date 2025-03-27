import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Конфигурационные параметры
AMO_DOMAIN = os.getenv("AMO_DOMAIN")
AMO_LOGIN = os.getenv("AMO_LOGIN")
AMO_API_KEY = os.getenv("AMO_API_KEY")

# Проверка наличия всех необходимых параметров
if not all([AMO_DOMAIN, AMO_LOGIN, AMO_API_KEY]):
    raise ValueError("Не все необходимые параметры указаны в .env файле") 