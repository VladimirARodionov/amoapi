# AMO CRM API Example

Пример работы с API AMO CRM для экспорта и импорта контактов

## Требования

- PHP 7.4 или выше (Windows: https://metanit.com/php/tutorial/1.3.php)
- Composer для установки зависимостей (Windows: https://getcomposer.org/download/)

## Установка

1. Клонировать репозиторий
2. Выполнить команду `composer install`
3. Заполнить данные для авторизации в файле `config/credentials.php` по примеру credentials.php.example

## Настройка

Для работы с API AMO CRM необходимо:

1. Создать интеграцию в AMO CRM (раздел "Настройки" -> "Интеграции" -> "Разработчикам")
2. Получить `client_id`, `client_secret` и `redirect_uri`
3. Получить код авторизации
4. Заполнить файл `config/credentials.php` этими данными

## Использование

### Экспорт контактов

Для экспорта контактов из AMO CRM в CSV-файл выполните:

```
php export_contacts.php
```

Контакты будут сохранены в файл `data/contacts.csv`

### Импорт и обновление контактов

Для импорта контактов из CSV-файла и обновления их в AMO CRM выполните:

```
php import_contacts.php [путь_к_файлу]
```

Где `[путь_к_файлу]` - путь к CSV файлу обязательно в формате UTF-8. Например: `data/new_contacts.csv`.

Пример содержимого CSV файла:

```
contact_id;new_name
1234;Иванов Иван
```
### Структура CSV-файла

Файл должен содержать следующие колонки:
- `contact_id` - ID контакта в AMO CRM
- `new_name` - Новое имя контакта

Разделитель в файле - точка с запятой (`;`)

### Получение контакта

Для получения контакта выполните:

```
php get_contact.php [id]
```


Curl uses a single file with all of the CA's in it. To add a new CA to Curl/PHP, you need to get a complete bundle, add your cert to the bundle, then tell PHP to use the custom bundle.
Download the latest bundle from CURL and save it to /etc/ssl/certs/cacert.pem:
https://curl.haxx.se/ca/cacert.pem
Edit the /etc/ssl/certs/cacert.pem file, and add your new CA public key to the bottom.
Edit php.ini and add the line openssl.cafile=/etc/ssl/certs/cacert.pem to the top (or bottom).