<?php

require_once __DIR__ . '/vendor/autoload.php';

include  'src/AmoClient.php';
include  'src/ContactsManager.php';
use AmoCRM\Exceptions\AmoCRMApiException;

try {
    // Проверка наличия аргумента с путем к файлу
    $id = null;
    if (isset($argv[1])) {
        $id = $argv[1];
        echo "Получаем контакт: {$id}" . PHP_EOL;
    } else {
        echo "Ошибка: не указан ID контакта" . PHP_EOL;
        return;
    }

    // Инициализация клиента и авторизация
    $amoClient = new AmoClient();
    $apiClient = $amoClient->authorize();
    
    // Инициализация менеджера контактов
    $contactsManager = new ContactsManager($apiClient);
    
    // Получаем контакт
    $contactsManager->getContactById($id);
} catch (AmoCRMApiException $e) {
    echo 'Ошибка при работе с API: ' . $e->getMessage() . PHP_EOL;
    throw $e;
} catch (Exception $e) {
    echo 'Ошибка: ' . $e->getMessage() . PHP_EOL;
    throw $e;
} 