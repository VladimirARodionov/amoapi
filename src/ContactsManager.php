<?php

//namespace AmoCRM\ApiExample;

use AmoCRM\Client\AmoCRMApiClient;
use AmoCRM\Collections\ContactsCollection;
use AmoCRM\Exceptions\AmoCRMApiException;
use AmoCRM\Exceptions\AmoCRMApiNoContentException;
use AmoCRM\Filters\ContactsFilter;
use AmoCRM\Models\ContactModel;

class ContactsManager
{
    private AmoCRMApiClient $apiClient;
    private string $csvPath;

    public function __construct(AmoCRMApiClient $apiClient)
    {
        $this->apiClient = $apiClient;
        $this->csvPath = __DIR__ . '/../data/contacts.csv';
    }

    /**
     * Получение списка контактов и сохранение в CSV
     * @return bool
     */
    public function exportContactsToCsv(): bool
    {
        try {
            $contactsService = $this->apiClient->contacts();
            $page = 1;
            $limit = 250;
            
            echo "Начинаем экспорт контактов..." . PHP_EOL;
            
            // Создаем файл и записываем заголовок
            $file = fopen($this->csvPath, 'w');
            fputcsv($file, ['contact_id', 'name', 'last_name', 'first_name'], ';', '"', '\\');
            fclose($file);
            
            // Создаем фильтр для пагинации
            $filter = new ContactsFilter();
            $filter->setPage($page);
            $filter->setLimit($limit);
            
            echo "Настроен фильтр: страница {$page}, лимит {$limit}" . PHP_EOL;
            
            do {
                try {
                    echo "Запрашиваем страницу {$page}..." . PHP_EOL;
                    
                    $contactsCollection = $contactsService->get($filter);
                    $count = $contactsCollection->count();
                    
                    echo "Получено контактов: {$count}" . PHP_EOL;
                    
                    if ($count === 0) {
                        echo "Получена пустая коллекция, завершаем..." . PHP_EOL;
                        break;
                    }
                    
                    // Открываем файл для добавления данных
                    $file = fopen($this->csvPath, 'a');
                    $processed = 0;
                    
                    /** @var ContactModel $contact */
                    foreach ($contactsCollection as $contact) {
                        $data = [
                            'contact_id' => $contact->getId(),
                            'name' => $contact->getName() ?? '',
                            'last_name' => $contact->getLastName() ?? '',
                            'first_name' => $contact->getFirstName() ?? '',
                        ];
                        fputcsv($file, $data, ';', '"', '\\');
                        $processed++;
                    }
                    
                    fclose($file);
                    
                    echo "Записано в файл контактов: {$processed}" . PHP_EOL;
                    echo "Обработано контактов на странице {$page}: {$count}" . PHP_EOL;
                    
                    // Если получили меньше контактов, чем запрашивали - это последняя страница
                    if ($count < $limit) {
                        echo "Достигнут конец списка контактов (получено меньше, чем запрошено)" . PHP_EOL;
                        break;
                    }
                    
                    // Увеличиваем номер страницы в фильтре
                    $page++;
                    $filter->setPage($page);
                    echo "Переходим к следующей странице: {$page}" . PHP_EOL;
                    
                } catch (AmoCRMApiNoContentException $e) {
                    echo "Получено исключение AmoCRMApiNoContentException: " . $e->getMessage() . PHP_EOL;
                    break;
                }
            } while (true);
            
            echo "Экспорт завершен. Файл сохранен: " . $this->csvPath . PHP_EOL;
            return true;
            
        } catch (AmoCRMApiException $e) {
            echo 'Ошибка экспорта контактов: ' . $e->getMessage() . PHP_EOL;
            return false;
        }
    }

    /**
     * Импорт и обновление контактов из CSV-файла
     * @param string|null $filePath Путь к файлу (если не указан, используется стандартный)
     * @return bool
     */
    public function importContactsFromCsv(?string $filePath = null): bool
    {
        try {
            $filePath = $filePath ?? $this->csvPath;
            
            if (!file_exists($filePath)) {
                throw new \Exception('Файл не найден: ' . $filePath);
            }
            
            $file = fopen($filePath, 'r');
            
            // Пропускаем заголовок
            fgetcsv($file, 0, ';', '"', '\\');
            
            $contactsToUpdate = [];
            $contactsService = $this->apiClient->contacts();
            
            // Читаем контакты из CSV
            while (($data = fgetcsv($file, 0, ';', '"', '\\')) !== false) {
                if (count($data) < 2) {
                    continue;
                }
                
                $contactId = (int)$data[0];
                $name = $data[1] or '';
                //echo $name . PHP_EOL;
                //$name = preg_replace('/\s+/', ' ', $name);
                
                $contactsToUpdate[] = [
                    'id' => $contactId,
                    'name' => $name,
                ];
            }
            
            fclose($file);
            
            // Обновляем контакты
            if (!empty($contactsToUpdate)) {
                $contactsCollection = new ContactsCollection();
                $contactsErrors[] = [];
                $errors_count = 0;
                
                foreach ($contactsToUpdate as $contactData) {
                    try {
                        // Получаем существующий контакт
                        $contact = $contactsService->getOne($contactData['id']);
                        echo $contact->getName() . PHP_EOL;
                        $firstName = $contact->getFirstName();
                        $lastName = $contact->getLastName();
                        echo $firstName . PHP_EOL;
                        echo $lastName . PHP_EOL;
                        $contact->setName($contactData['name']);
                        $contact->setFirstName($firstName);
                        $contact->setLastName($lastName);
                        
                        // Создаем новую коллекцию для обновления
                        $updateCollection = new ContactsCollection();
                        $updateCollection->add($contact);
                        
                        // Обновляем контакт
                        $contactsService->update($updateCollection);

                        // Добавляем в общую коллекцию для подсчета
                        $contactsCollection->add($contact);
                        
                        echo "Успешно обновлен контакт #{$contactData['id']}" . PHP_EOL;
                        
                        // Небольшая задержка между запросами
                        usleep(200000); // 0.2 секунды
                        
                    } catch (AmoCRMApiException $e) {
                        echo 'Ошибка обновления контакта #' . $contactData['id'] . ': ' . $e->getMessage() . PHP_EOL;
                        $errors_count++;
                        $contactsErrors[] = [
                        'id' => $contactData['id'],
                        'name' => $contactData['name'],
                        ];
                    }
                }
                
                echo 'Всего успешно обновлено контактов: ' . $contactsCollection->count() . PHP_EOL;
                echo 'Всего ошибок: ' . $errors_count . PHP_EOL;
                $err_file = fopen('errors.csv', 'w');
                foreach ($contactsErrors as $contact_err) {
                    fputcsv($err_file, $contact_err, ';', '"', '\\');
                }
                fclose($err_file);
            }
            
            return true;
        } catch (\Exception $e) {
            echo 'Ошибка импорта контактов: ' . $e->getMessage() . PHP_EOL;
            return false;
        }
    }

    /**
     * получение контакта
     * @param string|null $id ID контакта
     * @return bool
     */
    public function getContactById(?string $id = null): bool
    {
            $contactId = (int)$id;
            $contactsService = $this->apiClient->contacts();
            $contact = $contactsService->getOne($contactId);
            $data=[
                'id' => $contact->getId(),
                'name' => $contact->getName(),
                'first_name' => $contact->getFirstName(),
                'last_name' => $contact->getLastName(), 
                'created_at' => date('r', $contact->getCreatedAt()),
                'updated_at' => date('r', $contact->getUpdatedAt()),
            ];
            echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . PHP_EOL;
            return true;
    }

    /**
     * Установка пути к файлу CSV
     * @param string $path
     * @return void
     */
    public function setCsvPath(string $path): void
    {
        $this->csvPath = $path;
    }
} 