from pathlib import Path

import requests
import csv
import logging.config
import json
import os
from typing import List, Dict, Any, Optional
import time
from datetime import datetime

from config import AMO_DOMAIN, CLIENT_ID, CLIENT_SECRET, AUTH_CODE, ACCESS_TOKEN_FILE, REDIRECT_URI
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
        self.client_secret = CLIENT_SECRET
        self.auth_code = AUTH_CODE
        self.redirect_uri = REDIRECT_URI
        self.base_url = f"https://{self.domain}"
        self.access_token_file = ACCESS_TOKEN_FILE
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        
        # Загружаем токены, если они уже существуют
        self.load_tokens()
    
    def load_tokens(self) -> bool:
        """Загрузка токенов из файла"""
        if os.path.exists(self.access_token_file):
            try:
                with open(self.access_token_file, 'r') as file:
                    token_data = json.load(file)
                    self.access_token = token_data.get('access_token')
                    self.refresh_token = token_data.get('refresh_token')
                    self.expires_at = token_data.get('expires_at')
                    
                    # Проверяем, не истекли ли токены
                    if self.expires_at and datetime.now().timestamp() < self.expires_at:
                        logger.info("Токены успешно загружены из файла")
                        return True
                    else:
                        logger.info("Токены истекли, необходимо обновление")
                        return self.refresh_tokens()
            except Exception as e:
                logger.error(f"Ошибка при загрузке токенов: {e}")
        
        return False
    
    def save_tokens(self, token_data: Dict[str, Any]) -> None:
        """Сохранение токенов в файл"""
        try:
            with open(self.access_token_file, 'w') as file:
                json.dump(token_data, file)
            logger.info("Токены успешно сохранены в файл")
        except Exception as e:
            logger.error(f"Ошибка при сохранении токенов: {e}")
    
    def authenticate(self) -> bool:
        """Аутентификация в AMO CRM используя упрощенную OAuth авторизацию"""
        # Если токены уже есть и они валидны, используем их
        if self.access_token and self.expires_at and datetime.now().timestamp() < self.expires_at:
            return True
        
        # Если есть refresh_token, пробуем обновить токены
        if self.refresh_token:
            return self.refresh_tokens()
        
        # Если нет токенов или они невалидны, запрашиваем новые с кодом авторизации
        try:
            if not self.auth_code:
                logger.error("Не предоставлен код авторизации")
                return False
            
            auth_url = f"{self.base_url}/oauth2/access_token"
            auth_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "authorization_code",
                "code": self.auth_code,
                "redirect_uri": self.redirect_uri
            }
            
            logger.info(f"Отправляем запрос на авторизацию: {auth_data}")
            response = self.session.post(auth_url, data=auth_data)
            logger.info(f"Ответ сервера: {response.text}")
            response.raise_for_status()
            
            token_data = response.json()
            
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 0)
            self.expires_at = datetime.now().timestamp() + expires_in
            
            # Сохраняем данные токенов с временем истечения
            token_data['expires_at'] = self.expires_at
            self.save_tokens(token_data)
            
            logger.info("Авторизация в AMO CRM успешна")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при авторизации: {e}")
            if response := getattr(e, 'response', None):
                logger.error(f"Ответ сервера: {response.text}")
            return False
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при авторизации: {e}")
            return False
    
    def refresh_tokens(self) -> bool:
        """Обновление токенов с использованием refresh_token"""
        try:
            if not self.refresh_token:
                logger.error("Нет refresh_token для обновления токенов")
                return False
            
            auth_url = f"{self.base_url}/oauth2/access_token"
            auth_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "redirect_uri": self.redirect_uri
            }
            
            response = self.session.post(auth_url, json=auth_data)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 0)
            self.expires_at = datetime.now().timestamp() + expires_in
            
            # Сохраняем данные токенов с временем истечения
            token_data['expires_at'] = self.expires_at
            self.save_tokens(token_data)
            
            logger.info("Токены успешно обновлены")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при обновлении токенов: {e}")
            if response := getattr(e, 'response', None):
                logger.error(f"Ответ сервера: {response.text}")
            return False
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при обновлении токенов: {e}")
            return False
    
    def get_contacts(self, limit: int = 50, page: int = 1) -> Optional[ContactsResponse]:
        """Получение списка контактов из AMO CRM"""
        try:
            if not self.access_token and not self.authenticate():
                return None
            
            url = f"{self.base_url}/api/v4/contacts"
            params = {
                "page": page,
                "limit": limit
            }
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = self.session.get(url, params=params, headers=headers)
            
            # Если токен истек, пробуем обновить и повторить запрос
            if response.status_code == 401 and self.refresh_tokens():
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = self.session.get(url, params=params, headers=headers)
            
            response.raise_for_status()
            
            contacts_data = response.json()
            contacts = ContactsResponse.model_validate(contacts_data)
            logger.info(f"Получено {len(contacts._embedded['contacts'])} контактов")
            return contacts
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении контактов: {e}")
            if response := getattr(e, 'response', None):
                logger.error(f"Ответ сервера: {response.text}")
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
            if not self.access_token and not self.authenticate():
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
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = self.session.patch(
                url, 
                json=update_data.model_dump(exclude_none=True),
                headers=headers
            )
            
            # Если токен истек, пробуем обновить и повторить запрос
            if response.status_code == 401 and self.refresh_tokens():
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = self.session.patch(
                    url, 
                    json=update_data.model_dump(exclude_none=True),
                    headers=headers
                )
            
            response.raise_for_status()
            
            logger.info(f"Контакт {contact_id} успешно обновлен")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при обновлении контакта {contact_id}: {e}")
            if response := getattr(e, 'response', None):
                logger.error(f"Ответ сервера: {response.text}")
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