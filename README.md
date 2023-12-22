# EdGame_bot

Телеграм бот для геймификации образовательного процесса для детей 13-18 лет в
лагере.

### Установка на сервер

1. На сервере создайте `.env` файл и заполните по образцу `.env.example`.
   ```bash
   touch .env
   ```
2. Скопируйте `docker-compose.deploy_stage.yaml` и запустите его:

   ```bash
   docker compose --f docker-compose.deploy_stage.yaml up -d
   ```

На сервере должен быть установлен `docker compose`

---
### Использование

При регистрации пользователя, на этапе когда просят ввести пароль:

- `student` для получения роли студента
- `counsellor` для получения роли вожатого
- `methodist` для получения роли методиста
- `imaking` для получения роли админа

#### Роль суперпользователя

- Поменять в .env `BOSS_ID` на свой
- Перезапустить бота
- Появится возможность менять мастер-пароль и пароли для вожатого и методиста
---
### Разработка

1. Клонировать репозиторий.
   ```bash
   git clone https://github.com/Studio-Yandex-Practicum/EdGame_bot.git
   cd EdGame_bot
   ```
2. Создать и активировать виртуальное окружение.
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Установите зависимости
   ```bash
   pip install -r requirements.txt
   ```
4. Создайте `.env` файл и заполните по образцу `.env.example`.
5. Запустить базу данных:
   ```bash
   docker compose --f docker-compose.dev.yml up -d
   ```
6. Применяем миграции
    ```bash
    alembic upgrade head
    ```
7. Включить `pre-commit`
   ```bash
   pre-commit install
   ```
8. Заполняем тестовыми данными
    ```bash
    python create_test_data.py
    ```

#### Документация

- Перейти в папку docs
- Запустите:

```bash
sphinx-apidoc -o ./source ..
```

- Запустите

```bash
make html
```

- Документация находиться в папке docs/build/html  
