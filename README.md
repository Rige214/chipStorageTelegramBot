# chipStorageTelegramBot
Простой бот для мессенджера Telegram. Позволяющий ввести количество фишек, чтобы не запоминать их самому.

**Начало**
Для использования необходимо запустить - mainBot.py, предварительно в configuration.py указав токен и название Вашей базы данных.

Схема БД
![image](https://github.com/Rige214/chipStorageTelegramBot/assets/40599394/b762c6ab-fa1a-43f0-91c9-10be5f6505d0)



# UPD 29.01.24
Добавлена возможность вывести топ-3 игроков при помощи модуля - heapq
![image](https://github.com/Rige214/chipStorageTelegramBot/assets/40599394/d3d33c99-2659-4f40-aa58-8753d41acb9f)

# UPD 05.02.24
Добавлена возможность вывести собственную статистику по последним играм
![image](https://github.com/Rige214/chipStorageTelegramBot/assets/40599394/3c62def3-0f98-4c6d-9b2e-1d1fb9a365a6)

# UPD 23.02.24
Исправлен баг команды /stats. Оптимизация кода. Добавлен файл table_create.txt , для использования команд при создании БД.
