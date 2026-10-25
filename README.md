# Equipment Helpdesk

API для учёта неисправностей оборудования компьютерного класса. Позволяет
зарегистрировать заявку, найти её по номеру, отфильтровать список и записать
результат ремонта. Данные хранятся в SQLite.

## Установка и запуск

Проект проверен на Python 3.12; эта же версия используется в CI.
Команды ниже — для macOS/Linux.

```bash
git clone https://github.com/f1xgun/equipment-helpdesk.git
cd equipment-helpdesk
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
python -m uvicorn app_final:app --host 127.0.0.1 --port 8000
```

Для разработки можно добавить `--reload`.

Документация и отправка запросов через браузер: <http://127.0.0.1:8000/docs>.

### Через make

Если установлен `make`, активация окружения не нужна:

| Команда | Действие |
| --- | --- |
| `make install` | Создать `.venv`, установить зависимости и создать `.env`, если его нет |
| `make run` | Запустить без перезагрузки |
| `make dev` | Запустить с `--reload` |
| `make test` | Выполнить тесты |
| `make check` | Проверить `/health` и `/version` уже запущенного сервера |

Для другого порта: `make run PORT=8001` и `make check PORT=8001`.

## Настройки и БД

`DATABASE_URL` — путь к SQLite. Значение по умолчанию есть в `.env.example`:

```dotenv
DATABASE_URL=sqlite:///./helpdesk.db
```

Приложение читает `.env` из корня проекта; переменная окружения имеет приоритет.

Запуск с другой БД без изменения `.env`:

```bash
DATABASE_URL=sqlite:///./demo.db python -m uvicorn app_final:app
```

Путь к SQLite отсчитывается от каталога запуска. БД создаётся автоматически,
данные сохраняются после перезапуска. `.env` и файлы БД исключены из Git.

## API

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/health` | Проверка соединения с БД |
| `GET` | `/version` | Версия приложения |
| `POST` | `/tickets` | Создание заявки |
| `GET` | `/tickets/{ticket_id}` | Заявка по номеру |
| `GET` | `/tickets` | Список; фильтры `status` и `room` |
| `PATCH` | `/tickets/{ticket_id}/status` | Изменение статуса |

Приоритеты: `low`, `normal`, `high`. По умолчанию — `normal`.
Статусы: `open → in_progress → closed`. Для закрытия нужен непустой `resolution`;
время закрытия заполняется автоматически.

Фильтры можно комбинировать: `/tickets?status=open&room=305`.

## Тесты и CI

```bash
python -m pytest -v
```

Тесты работают с временной БД. GitHub Actions запускает их при `push` и
`pull_request`, после успеха создаёт artifact `equipment-helpdesk` с исходниками
и `requirements.txt`. Запуски и архивы — во вкладке
[Actions](https://github.com/f1xgun/equipment-helpdesk/actions).

## Проверка и диагностика

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/version
```

При запущенном сервере оба маршрута возвращают `200`: `/health` — `{"status":"ok"}`,
`/version` — JSON с полем `version`. При недоступности БД `/health` отвечает `503`.

Логи видны в терминале с Uvicorn: запуск и остановка, создание заявок, смена
статусов и ошибки проверки БД. Описания заявок, результаты ремонта и настройки
подключения в них не записываются.

| Проблема | Что проверить |
| --- | --- |
| `ModuleNotFoundError` | Активировано ли `.venv`, установлены ли зависимости |
| `Address already in use` | Выбрать другой порт: `--port 8001` |
| `unable to open database file` | Путь к БД, наличие родительского каталога и права записи |
| `/health` вернул `503` | Сообщение `Database health check failed` в терминале, путь и доступность БД |
| API вернул `422` | Поле `detail` в ответе и схема запроса в `/docs` |

Если БД недоступна при старте, приложение не запустится; причина будет в терминале.
