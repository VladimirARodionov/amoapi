#!/usr/bin/env python3
"""
Вспомогательный скрипт для получения кода авторизации OAuth 2.0 для AMO CRM
"""
import os
import sys
import argparse
import webbrowser
from dotenv import load_dotenv

def main():
    """Основная функция для запуска процесса получения кода авторизации"""
    parser = argparse.ArgumentParser(description="Помощник для получения кода авторизации AMO CRM")
    parser.add_argument("--client_id", help="Client ID интеграции")
    parser.add_argument("--domain", help="Домен AMO CRM (например, mycompany.amocrm.ru)")
    args = parser.parse_args()
    
    # Загружаем переменные из .env файла, если они существуют
    load_dotenv()
    
    client_id = args.client_id or os.getenv("CLIENT_ID")
    domain = args.domain or os.getenv("AMO_DOMAIN")
    
    if not client_id:
        print("Ошибка: не указан CLIENT_ID. Используйте --client_id или укажите в .env файле")
        sys.exit(1)
    
    if not domain:
        print("Ошибка: не указан домен AMO CRM. Используйте --domain или укажите AMO_DOMAIN в .env файле")
        sys.exit(1)
    
    # Формируем URL для авторизации
    auth_url = f"https://{domain}/oauth?client_id={client_id}&mode=post_message"
    
    print("\n" + "="*80)
    print("Инструкция по получению кода авторизации AMO CRM:")
    print("="*80)
    print(f"1. Сейчас будет открыт браузер с URL для авторизации: {auth_url}")
    print("2. Авторизуйтесь в AMO CRM, если потребуется")
    print("3. После авторизации вы увидите код в URL")
    print("4. Скопируйте этот код и добавьте его в .env файл в параметр CODE")
    print("="*80)
    
    input("Нажмите Enter для открытия браузера...")
    
    # Открываем браузер с URL авторизации
    webbrowser.open(auth_url)
    
    print("\nПосле получения кода, добавьте его в .env файл:")
    print("CODE=полученный_код")

if __name__ == "__main__":
    main() 