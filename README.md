![workflow](https://github.com/petrushque/mailbot/actions/workflows/mailbot_workflow.yml/badge.svg)
## mailbot
Простой телеграм-бот отправляющий уведомления в телеграм о новых полученных письмах.
Не умеет работать с вложениями, равно как и с multipart письмами.

# Используемые модули и технологии
- [Python 3.10.2](https://www.python.org/)
- [BeautifulSoup4](https://beautiful-soup-4.readthedocs.io/en/latest/)
- [Python Telegram Bot](https://docs.python-telegram-bot.org/en/stable/index.html)
- [Docker](https://www.docker.com/)

# Установка и запуск

### Клонировать репозиторий и перейти в него в командной строке:
```sh
git clone git@github.com:PETRUSHQUE/mailbot.git
```
```sh
cd mailbot
```
### Наполнить env файл
```sh
TELEGRAM_TOKEN=<...> # токен телеграм бота
TELEGRAM_CHAT_ID=<...> # чат айди, куда бот будет отправлять сообщения
EMAIL_IMAP_SERVER=<...> # адрес сервера IMAP
EMAIL_LOGIN=<...> # адрес почты
EMAIL_PASSWORD=<...> # пароль от почты
```
### Запустить проект:
Cобрать контейнеры и запустить их:
```sh
cd ../infra
docker-compose up -d --build
```