# Сервис Gateway

## Зоны ответственности
- Принимает и обрабатывает входящие запросы от пользователей через веб-приложение (UI).
- Направляет запросы к соответствующим сервисам, таким как сервис пользователей, постов и статистики.
- Обеспечивает базовую маршрутизацию и агрегацию данных от различных микросервисов.

## Границы сервиса
- Не занимается хранением данных или сложной бизнес-логикой, связанной с самими данными.
- В основном выполняет функции маршрутизации запросов и взаимодействует с другими сервисами через API.
- Не взаимодействует напрямую с базами данных.
