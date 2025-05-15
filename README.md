# Slovobot

**Slovobot** — мультиплатформенный бот для автоматизации поддержки, способный работать как в Telegram, так и во ВКонтакте, с использованием DialogFlow для "умных" ответов на вопросы пользователей.

---

##  Структура проекта

- **bot.py** — основной скрипт Telegram-бота.
- **vk_bot.py** — основной скрипт VK-бота (работает с личными сообщениями группы).
- **dialogflow_utils.py** — функции для интеграции с DialogFlow (используются обоими ботами).
- **create_intents_from_file.py** — отдельный скрипт для массовой загрузки вопросов/ответов в DialogFlow из `questions.json`.
- **questions.json** — список типовых вопросов и ответов для обучения DialogFlow.
- **requirements.txt** — зависимости проекта.
- **logs/** — директория для лог-файлов ботов (создаётся автоматически).
- **logging_utils.py** — общий модуль для настройки логирования.

---

## Описание файлов

| Файл                          | Описание                                                                                 |
|-------------------------------|-----------------------------------------------------------------------------------------|
| `bot.py`                      | Запуск Telegram-бота, интеграция с DialogFlow, логирование                             |
| `vk_bot.py`                   | Запуск VK-бота (через longpoll), интеграция с DialogFlow, логирование                  |
| `dialogflow_utils.py`         | Универсальные функции работы с DialogFlow                                              |
| `create_intents_from_file.py` | Скрипт для массовой загрузки интентов (вопросов/ответов) в DialogFlow                  |
| `questions.json`              | JSON с типовыми вопросами и ответами для загрузки в DialogFlow                         |
| `requirements.txt`            | Список зависимостей Python                                                             |
| `logs/`                       | Папка для логов (создаётся автоматически при запуске любого бота)                      |
| `logging_utils.py`            | Единая функция настройки логирования для всех скриптов                                 |

---

## Требования

- Python 3.8+ (рекомендовано 3.10)
- Аккаунт Telegram, зарегистрированный бот у BotFather
- Группа ВКонтакте с включёнными сообщениями и полученным токеном доступа
- Аккаунт Google Cloud, созданный проект и сервисный аккаунт для DialogFlow
- Созданные intents в DialogFlow (можно массово загрузить через `create_intents_from_file.py`)

---

## Пример `.env.example`

```env
TELEGRAM_TOKEN=your-telegram-bot-token
VK_GROUP_TOKEN=your-vk-group-token
DIALOGFLOW_PROJECT_ID=your-dialogflow-project-id
GOOGLE_APPLICATION_CREDENTIALS=your-service-account.json
````

* **TELEGRAM\_TOKEN** — токен Telegram-бота от BotFather
* **VK\_GROUP\_TOKEN** — токен доступа для вашей группы ВК
* **DIALOGFLOW\_PROJECT\_ID** — идентификатор проекта DialogFlow (см. настройки агента)
* **GOOGLE\_APPLICATION\_CREDENTIALS** — путь до JSON-файла с ключом сервис-аккаунта Google

---

## Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## Запуск Telegram-бота

```bash
python bot.py
```

* После запуска бот будет отвечать в Telegram всем, кто ему напишет.

---

## Запуск VK-бота

```bash
python vk_bot.py
```

* После запуска бот будет слушать личные сообщения сообщества ВК.
* Если не понял вопрос (fallback), бот просто **молчит** (ничего не отправляет).

---

## Массовое обучение DialogFlow (добавление intents)

```bash
python create_intents_from_file.py
```

* Добавляет в DialogFlow интенты из файла `questions.json`.
* Требует корректно настроенный сервисный аккаунт Google и переменные окружения.

---

## Пример запуска обоих ботов

Открой два терминала и запусти:

```bash
python bot.py
```

и отдельно

```bash
python vk_bot.py
```