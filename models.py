from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ContactName(BaseModel):
    """Модель для имени контакта"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class ContactCustomField(BaseModel):
    """Модель для пользовательского поля контакта"""
    field_id: int
    values: List[Dict[str, Any]]


class ContactRequest(BaseModel):
    """Модель для запроса на создание/обновление контакта"""
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    custom_fields_values: Optional[List[ContactCustomField]] = None


class ContactResponse(BaseModel):
    """Модель для ответа API с данными контакта"""
    id: int
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    custom_fields_values: Optional[List[Dict[str, Any]]] = None


class ContactsResponse(BaseModel):
    """Модель для ответа API со списком контактов"""
    _page: Optional[int] = None
    _links: Optional[Dict[str, Any]] = None
    _embedded: Dict[str, List[ContactResponse]]


class ContactUpdate(BaseModel):
    """Модель для обновления контакта из CSV файла"""
    contact_id: int
    new_name: str


class ContactUpdateRequest(BaseModel):
    """Модель для запроса на обновление контакта"""
    id: int
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None 