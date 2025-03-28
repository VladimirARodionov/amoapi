<?php

require_once __DIR__ . '/vendor/autoload.php';

include  'src/AmoClient.php';
include  'src/ContactsManager.php';
use AmoCRM\Exceptions\AmoCRMApiException;

try {
    // Инициализация клиента и авторизация
    $amoClient = new AmoClient();
    $apiClient = $amoClient->authorize();
    
    // Инициализация менеджера контактов
    $contactsManager = new ContactsManager($apiClient);
    
    // Экспорт контактов
    if ($contactsManager->exportContactsToCsv()) {
        echo 'Контакты успешно экспортированы в файл: ' . __DIR__ . '/data/contacts.csv' . PHP_EOL;
    } else {
        echo 'Ошибка при экспорте контактов' . PHP_EOL;
    }
} catch (AmoCRMApiException $e) {
    echo 'Ошибка при работе с API: ' . $e->getMessage() . PHP_EOL;
} catch (Exception $e) {
    echo 'Ошибка: ' . $e->getMessage() . PHP_EOL;
} 