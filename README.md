## mailbot
Простой телеграм-бот отправляющий уведомления в телеграм о новых полученных письмах. Не умеет работать с вложениями, равно как и с multipart письмами.

# Используемые модули
- [Python 3.10.2](https://www.python.org/)
- [BeautifulSoup4](https://beautiful-soup-4.readthedocs.io/en/latest/)
- [Python Telegram Bot](https://docs.python-telegram-bot.org/en/stable/index.html)

# Установка и запуск
1. Cоздать и активировать виртуальное окружение:
```sh
python -m venv venv
```
```sh
. venv/Scripts/activate
```
2. Установить зависимости из файла requirements.txt:
```sh
python -m pip install --upgrade pip
```
```sh
pip install -r requirements.txt
```
3. Наполнить .env файл
```
TELEGRAM_TOKEN=<...> # токен телеграм бота
TELEGRAM_CHAT_ID=<...> # чат айди, куда бот будет отправлять сообщения
EMAIL_IMAP_SERVER=<...> # адрес сервера IMAP
EMAIL_LOGIN=<...> # адрес почты
EMAIL_PASSWORD=<...> # пароль от почты
```
4. Запустить
```sh
python mailbot.py
```
