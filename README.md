## mailbot
Простой телеграм-бот отправляющий уведомления в телеграм о новых полученных письмах. Не умеет работать с вложениями, равно как и с multipart письмами.

# Используемые модули
- [Python 3.10.2](https://www.python.org/)
- [BeautifulSoup4](https://beautiful-soup-4.readthedocs.io/en/latest/)
- [Python Telegram Bot](https://docs.python-telegram-bot.org/en/stable/index.html)

# Установка и запуск
```sh
cd mailbot
py -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
py mailbot.py
```
