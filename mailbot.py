"""Телеграм бот, отправляющий новый письма с почты."""
import datetime
import email
import imaplib
import logging
import logging.config
import os
import time
from email.header import decode_header

import telegram
from bs4 import BeautifulSoup
from dotenv import load_dotenv


LOGFILENAME: str = __file__.replace('\\', '\\\\') + '.log'

logging.config.fileConfig('logging.conf',
                          disable_existing_loggers=False,
                          defaults={'logfilename': LOGFILENAME})
logger = logging.getLogger(__name__)

load_dotenv()

EMAIL_IMAP_SERVER: str = os.getenv('EMAIL_IMAP_SERVER')
EMAIL_LOGIN: str = os.getenv('EMAIL_LOGIN')
EMAIL_PASS: str = os.getenv('EMAIL_PASSWORD')
TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID')
TOKENS: tuple = ('TELEGRAM_CHAT_ID', 'TELEGRAM_TOKEN', )

RETRY_TIME: int = 60  # в секундах
MESSAGE_TYPE: str = 'UNSEEN'  # UNSEEN/ALL
CALLBACK_THREAD: str = 'Форма обратной связи'
OK_STATUS: str = 'OK'
INBOX: str = 'INBOX'

TOKEN_ERROR: str = ('Отсутствует обязательная переменная окружения: {var}. '
                    'Программа принудительно завершена.')
TELEGRAM_ERROR: str = ('Ошибка в работе программы: Не доставлено сообщение '
                       '"{message}". Недоступен API Telegram. {error}')
TIMEOUT_ERROR: str = ('Ошибка таймаута. {error}')
CONNECTION_ERROR: str = ('Ошибка соединения. {error}')
IMAP_ERROR: str = 'Ошибка IMAP. {error}'
IMAP_DEBUG: str = '{status} {result}'
SSL_ERROR: str = 'Ошибка SSL. {error}'
TOTAL_EMAILS: str = 'Количество сообщений в почтовом ящике: {amount}'
UNREAD_EMAILS: str = ('Количество непрочитанных сообщений в '
                      'почтовом ящике: {amount}')
MESSAGE_SENT: str = 'Бот отправил сообщение "{message}".'
EMAIL_MESSAGE: str = ('Тема: {thread}\n\nОт: {from_}\nДата: {date}\n'
                      'Текст сообщения:\n{message}')
ERROR: str = 'Сбой в работе программы: {error}'


def send_message(bot: telegram.Bot, text: str) -> None:
    """Отправка сообщения."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text)
        logger.info(MESSAGE_SENT.format(message=text))
    except telegram.error.TelegramError as error:
        logger.exception(TELEGRAM_ERROR.format(message=text, error=error))


def retrieve_emails() -> list | None:
    """Получение новых писем."""
    try:
        imap = imaplib.IMAP4_SSL(EMAIL_IMAP_SERVER)
    except ValueError as error:
        logger.exception(SSL_ERROR.format(error=error))
    except TimeoutError as error:
        logger.exception(TIMEOUT_ERROR.format(error=error))
    except ConnectionError as error:
        logger.exception(CONNECTION_ERROR.format(error=error))
    try:
        status, _result = imap.login(EMAIL_LOGIN, EMAIL_PASS)
        _result = _result[-1].decode()
        logger.debug(IMAP_DEBUG.format(status=status, result=_result))
    except imaplib.IMAP4_SSL.error as error:
        logger.exception(IMAP_ERROR.format(error=error))
    if status != OK_STATUS:
        raise imaplib.IMAP4_SSL.error(
            IMAP_ERROR.format(error=_result))
    status, messages = imap.select(INBOX)
    logger.info(TOTAL_EMAILS.format(amount=messages[-1].decode()))
    if status != OK_STATUS:
        raise imaplib.IMAP4_SSL.error
    status, result = imap.uid('search', MESSAGE_TYPE, 'ALL')
    if status != OK_STATUS:
        raise imaplib.IMAP4_SSL.error
    result = result[-1].decode()
    logger.info(UNREAD_EMAILS.format(amount=len(result)))
    if not result:
        status, result = imap.close()
        if isinstance(result[-1], bytes):
            result = result[-1].decode()
        logger.debug(IMAP_DEBUG.format(status=status, result=result))
        status, result = imap.logout()
        if isinstance(result[-1], bytes):
            result = result[-1].decode()
        logger.debug(IMAP_DEBUG.format(status=status, result=result))
        return None
    else:
        logger.info(UNREAD_EMAILS.format(amount=len(result.split(' '))))
        result = result.split(' ')
        msgs = []
        for num in result:
            try:
                status, msg = imap.uid('fetch', num.encode(), '(RFC822)')
            except imaplib.IMAP4_SSL.error as error:
                logger.exception(IMAP_ERROR.format(error=error))
            if status != OK_STATUS:
                raise imaplib.IMAP4_SSL.error
            msgs.append(msg)
        status, result = imap.close()
        if isinstance(result[-1], bytes):
            result = result[-1].decode()
        logger.debug(IMAP_DEBUG.format(status=status, result=result))
        status, result = imap.logout()
        if isinstance(result[-1], bytes):
            result = result[-1].decode()
        logger.debug(IMAP_DEBUG.format(status=status, result=result))
        return msgs


def convert_email(msg: bytes) -> str:
    """Преобразовывание сообщений к читабельному виду."""
    msg = email.message_from_bytes(msg[0][1])
    thread = decode_header(msg['Subject'])[0][0]
    date = datetime.datetime(*email.utils.parsedate_tz(msg['Date'])[:5])
    from_ = msg['Return-path']
    if isinstance(thread, bytes):
        thread = thread.decode()
    payload = msg.get_payload(decode=True).decode()
    if thread == CALLBACK_THREAD:
        soup = BeautifulSoup(payload, features='html.parser')

        div = soup.find('div').get_text()
        body = div.split('\n')
        body = [b for b in body if b.strip()]

        data = body[0] + '\n'
        for index in range(len(body)):
            if index % 2 == 1:
                data = data + body[index] + body[index+1] + '\n'
    else:
        data = payload
    return EMAIL_MESSAGE.format(
        thread=thread, from_=from_, date=date, message=data)


def check_tokens() -> bool:
    """Проверка обязательных переменных окружения."""
    tokens = [var for var in TOKENS if globals()[var] is None]
    if tokens:
        logger.critical(TOKEN_ERROR.format(var=tokens))
    return not tokens


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        return
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    while True:
        try:
            emails = retrieve_emails()
            if emails:
                for _email in emails:
                    send_message(bot, convert_email(_email))
        except Exception as error:
            message = ERROR.format(error=error)
            logger.exception(message)
            send_message(bot, message)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
