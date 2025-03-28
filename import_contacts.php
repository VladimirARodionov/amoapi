<?php

require_once __DIR__ . '/vendor/autoload.php';

include  'src/AmoClient.php';
include  'src/ContactsManager.php';
use AmoCRM\Exceptions\AmoCRMApiException;

try {
    // Проверка наличия аргумента с путем к файлу
    $filePath = null;
    if (isset($argv[1]) && file_exists($argv[1])) {
        $filePath = $argv[1];
        echo "Будет использован файл: {$filePath}" . PHP_EOL;
    } else {
        echo "Ошибка: не указан файл или нет такого файла" . PHP_EOL;
        return;
    }

    // Инициализация клиента и авторизация
    $amoClient = new AmoClient();
    $apiClient = $amoClient->authorize();
    
    // Инициализация менеджера контактов
    $contactsManager = new ContactsManager($apiClient);
    
    // Импорт и обновление контактов
    if ($contactsManager->importContactsFromCsv($filePath)) {
        echo 'Контакты успешно импортированы и обновлены' . PHP_EOL;
    } else {
        echo 'Ошибка при импорте контактов' . PHP_EOL;
    }
} catch (AmoCRMApiException $e) {
    echo 'Ошибка при работе с API: ' . $e->getMessage() . PHP_EOL;
    throw $e;
} catch (Exception $e) {
    echo 'Ошибка: ' . $e->getMessage() . PHP_EOL;
    throw $e;
} 