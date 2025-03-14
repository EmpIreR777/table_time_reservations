# Проект: Система управления заявками и задолженностями для магазина "Мир Антенн"

Этот проект представляет собой веб-приложение и Telegram-бота для управления заявками через вебхук, задолженностями и услугами магазина "Мир Антенн". Приложение позволяет пользователям создавать заявки на услуги, администраторам — управлять заявками и задолженностями, а также отправлять уведомления через Telegram.

# Основные функции

## Для пользователей:

- Создание заявок на услуги (установка, ремонт, диагностика антенн и т.д.).
- Просмотр статуса своих заявок.
- Получение уведомлений о статусе заявок через Telegram.

---

## Для администраторов:

- Управление заявками (изменение статусов, назначение мастеров).
- Управление задолженностями (добавление, обновление, удаление товаров в долг).
- Просмотр статистики по заявкам и пользователям.
- Отправка сообщений всем пользователям или работникам через Telegram (текст, фото, видео, аудио).
---

## Для работников:

- Просмотр списка задолженностей.
- Управление своими задолженностями.

---

## Технологии

- **Backend**: FastAPI, SQLAlchemy,.
- **База данных**: PostgreSQL или Sqlite
- **Frontend**:  HTML, Jinja2, CSS, JS
- **Telegram Bot**: Aiogram-3
- **Дополнительные инструменты**: Docker, Docker Compose, Yandex Geocoder API.

---

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone git@github.com:EmpIreR777/world_of_antennas.git
   ```
2. Создайте виртуальное окружение:
    ```bash
    python3.12 -m venv venv
    source venv/bin/activate  # Для Linux/MacOS
    venv\Scripts\activate     # Для Windows
    ```
3. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

---

## Настройка окружения
1. Создайте файл .env в корневой директории проекта с следующими переменными:
    ```bash
    BOT_TOKEN=
    ADMIN_IDS=
    BASE_SITE=
    YANDEX_API_KEY=
    DATABASE_URL=
    ```

---

## Создайте файл .env в корне проекта и заполните его по примеру .env.example:

    ```env
    SECRET_KEY=gV64m9aIzFG4qpgVphvQbPQrtAO0nM-7YwwOvu0XPt5KJOjAy4AfgLkqJXYEt
    ALGORITHM=HS256
    POSTGRES_USER=postgre_user
    POSTGRES_PASSWORD=postgre_password
    POSTGRES_DB=postgres_db
    POSTGRES_HOST=db
    POSTGRES_PORT=5432
    ```

---

## Запуск приложения
1. Локальный запуск
    ```bash
    uvicorn app.main:app --reload
    ```
2. Запуск через Docker-compose

    1.Соберите и запустите контейнеры:
    ```bash
        docker-compose up -d --build
    ```
    - **Рекомендую использовать makefile для удобства**
    2.Приложение будет доступно по адресу: 
    ```bash
        http://localhost:5000.
    ```

---

## API документация
1. После запуска приложения документация Swagger доступна по адресу:
    ```bash
        http://localhost:5000/docs — интерактивная документация.
        http://localhost:5000/redoc — альтернативная документация.
    ```

---

## API документация
1. После запуска приложения документация Swagger доступна по адресу:
    ```bash
        http://localhost:5000/docs — интерактивная документация.
        http://localhost:5000/redoc — альтернативная документация.
    ```

---

## Администрирование

Для управления данными используется административная панель, доступная по адресу /admin. Для входа в панель администратора необходимо использовать учетные данные, указанные в базе данных.
    ```
    http://127.0.0.1:5000/admin/
    ```

---

## Примеры данных

- Пользователи (администраторы, мастера, операторы, клиенты).
- Магазины и услуги.
- Заявки и задолженности.
---