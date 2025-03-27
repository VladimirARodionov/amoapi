from pathlib import Path

import requests
import csv
import logging.config
from typing import List, Dict, Any, Optional
import time

from config import AMO_DOMAIN, AMO_API_KEY, CLIENT_ID, REDIRECT_URI
from models import ContactResponse, ContactsResponse, ContactUpdate, ContactUpdateRequest

# Настройка логирования
logging.config.fileConfig(fname=Path(__file__).resolve().parent / 'logging.ini',
                          disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class AmoApiClient:
    """Клиент для работы с API AMO CRM"""
    
    def __init__(self):
        self.domain = AMO_DOMAIN
        self.client_id = CLIENT_ID
        self.api_key = AMO_API_KEY
        self.base_url = f"https://{self.domain}"
        self.redirect_uri = REDIRECT_URI
        self.session = requests.Session()
        self.auth_header = None
    
    def authenticate(self) -> bool:
        """Аутентификация в AMO CRM используя упрощенную авторизацию"""
        try:
            auth_url = f"{self.base_url}/oauth2/access_token"
            auth_data = {
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
                "code": self.api_key,
                "client_secret": self.api_key,
            }
            
            response = self.session.post(auth_url, data=auth_data)
            response.raise_for_status()
            
            auth_result = response.json()
            if auth_result.get("response", {}).get("auth", False):
                logger.info("Авторизация в AMO CRM успешна")
                self.auth_header = {
                    "Cookie": response.headers.get("Set-Cookie", "")
                }
                return True
            else:
                logger.error(f"Ошибка авторизации: {auth_result}")
                return False
        except requests.exceptions.RequestException as e:
            logger.exception(f"Ошибка при авторизации: {e}")
            return False
    
    def get_contacts(self, limit: int = 50, page: int = 1) -> Optional[ContactsResponse]:
        """Получение списка контактов из AMO CRM"""
        try:
            if not self.auth_header:
                if not self.authenticate():
                    return None
            
            url = f"{self.base_url}/api/v4/contacts"
            params = {
                "page": page,
                "limit": limit
            }
            
            response = self.session.get(url, params=params, headers=self.auth_header)
            response.raise_for_status()
            
            contacts_data = response.json()
            contacts = ContactsResponse.model_validate(contacts_data)
            logger.info(f"Получено {len(contacts._embedded['contacts'])} контактов")
            return contacts
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении контактов: {e}")
            return None
        except Exception as e:
            logger.error(f"Непредвиденная ошибка: {e}")
            return None
    
    def get_all_contacts(self) -> List[ContactResponse]:
        """Получение всех контактов из AMO CRM"""
        all_contacts = []
        page = 1
        
        while True:
            contacts_page = self.get_contacts(page=page)
            if not contacts_page or not contacts_page._embedded['contacts']:
                break
            
            all_contacts.extend(contacts_page._embedded['contacts'])
            
            # Проверяем, есть ли следующая страница
            if not contacts_page._links.get('next'):
                break
            
            page += 1
            # Добавляем задержку, чтобы не превысить лимиты API
            time.sleep(0.5)
        
        return all_contacts
    
    def save_contacts_to_csv(self, filename: str) -> bool:
        """Сохранение списка контактов в CSV файл"""
        try:
            contacts = self.get_all_contacts()
            if not contacts:
                logger.warning("Нет контактов для сохранения")
                return False
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(['contact_id', 'name', 'first_name', 'last_name'])
                
                for contact in contacts:
                    writer.writerow([
                        contact.id,
                        contact.name,
                        contact.first_name or '',
                        contact.last_name or ''
                    ])
            
            logger.info(f"Контакты сохранены в файл {filename}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении контактов в CSV: {e}")
            return False
    
    def load_contacts_from_csv(self, filename: str) -> List[ContactUpdate]:
        """Загрузка списка контактов для обновления из CSV файла"""
        try:
            contacts_to_update = []
            
            with open(filename, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                # Пропускаем заголовок
                header = next(reader)
                
                for row in reader:
                    if len(row) >= 2:
                        try:
                            contact_id = int(row[0])
                            new_name = row[1]
                            contacts_to_update.append(ContactUpdate(
                                contact_id=contact_id,
                                new_name=new_name
                            ))
                        except ValueError as e:
                            logger.warning(f"Пропуск строки с некорректными данными: {row}, ошибка: {e}")
            
            logger.info(f"Загружено {len(contacts_to_update)} контактов для обновления")
            return contacts_to_update
        except Exception as e:
            logger.error(f"Ошибка при загрузке контактов из CSV: {e}")
            return []
    
    def update_contact(self, contact_id: int, new_name: str) -> bool:
        """Обновление имени контакта в AMO CRM"""
        try:
            if not self.auth_header:
                if not self.authenticate():
                    return False
            
            # Разделяем полное имя на имя и фамилию (если возможно)
            name_parts = new_name.strip().split(' ', 1)
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            update_data = ContactUpdateRequest(
                id=contact_id,
                name=new_name,
                first_name=first_name,
                last_name=last_name
            )
            
            url = f"{self.base_url}/api/v4/contacts/{contact_id}"
            response = self.session.patch(
                url, 
                json=update_data.model_dump(exclude_none=True),
                headers=self.auth_header
            )
            response.raise_for_status()
            
            logger.info(f"Контакт {contact_id} успешно обновлен")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при обновлении контакта {contact_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при обновлении контакта {contact_id}: {e}")
            return False
    
    def update_contacts_from_csv(self, filename: str) -> Dict[str, Any]:
        """Обновление контактов из CSV файла"""
        contacts_to_update = self.load_contacts_from_csv(filename)
        results = {
            "total": len(contacts_to_update),
            "success": 0,
            "failed": 0,
            "failed_ids": []
        }
        
        for contact in contacts_to_update:
            try:
                success = self.update_contact(contact.contact_id, contact.new_name)
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    results["failed_ids"].append(contact.contact_id)
                # Добавляем задержку, чтобы не превысить лимиты API
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Ошибка при обработке контакта {contact.contact_id}: {e}")
                results["failed"] += 1
                results["failed_ids"].append(contact.contact_id)
        
        return results 