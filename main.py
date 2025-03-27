#!/usr/bin/env python3
import argparse
import sys
import logging
from amo_api import AmoApiClient

# Настройка логирования
logger = logging.getLogger(__name__)


def export_contacts(output_file: str):
    """Экспорт контактов в CSV файл"""
    client = AmoApiClient()
    result = client.save_contacts_to_csv(output_file)
    if result:
        logger.info(f"Контакты успешно экспортированы в файл {output_file}")
    else:
        logger.error("Не удалось экспортировать контакты")
        sys.exit(1)


def update_contacts(input_file: str):
    """Обновление контактов из CSV файла"""
    client = AmoApiClient()
    results = client.update_contacts_from_csv(input_file)
    
    logger.info(f"Результаты обновления контактов:")
    logger.info(f"Всего контактов: {results['total']}")
    logger.info(f"Успешно обновлено: {results['success']}")
    logger.info(f"Ошибок обновления: {results['failed']}")
    
    if results['failed'] > 0:
        logger.warning(f"Не удалось обновить контакты с ID: {results['failed_ids']}")
        
    success_rate = (results['success'] / results['total'] * 100) if results['total'] > 0 else 0
    logger.info(f"Процент успешных обновлений: {success_rate:.2f}%")


def main():
    """Основная функция программы"""
    parser = argparse.ArgumentParser(description="Работа с контактами AMO CRM")
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")
    
    # Команда экспорта контактов
    export_parser = subparsers.add_parser("export", help="Экспорт контактов в CSV")
    export_parser.add_argument("-o", "--output", required=True, help="Путь к файлу для сохранения контактов")
    
    # Команда обновления контактов
    update_parser = subparsers.add_parser("update", help="Обновление контактов из CSV")
    update_parser.add_argument("-i", "--input", required=True, help="Путь к CSV файлу с данными для обновления")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "export":
            export_contacts(args.output)
        elif args.command == "update":
            update_contacts(args.input)
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 