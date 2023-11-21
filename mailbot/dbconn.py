"""Модуль подключения к локальной БД Sqlite3."""
import logging
import logging.config
import sqlite3

from dataclasses import dataclass

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

DB_FILENAME: str = 'mailbot-db.sqlite3'
DB_CREATETABLE: str = '''CREATE TABLE IF NOT EXISTS mails
                      (uid INT PRIMARY KEY,
                      thread TEXT,
                      date TEXT,
                      sender TEXT,
                      text TEXT NOT NULL,
                      is_read INT NOT NULL);'''
DB_SEARCH_ALL: str = 'SELECT uid, thread, date, sender, text FROM mails;'
DB_SEARCH_UNREAD: str = '''SELECT uid, thread, date, sender, text
                        FROM mails WHERE is_read=0;'''
DB_INSERT: str = '''INSERT INTO mails
                 (uid, thread, date, sender, text, is_read) VALUES
                 (?, ?, ?, ?, ?, ?);'''
DB_UPDATE_READ: str = 'UPDATE mails SET is_read=1 WHERE uid={uid};'


DB_ERROR: str = 'Проблема локальной БД: {error} при вызове метода {method}'
DB_INSERTED: str = 'В БД успешно вставлено {amount} новых писем.'
DB_READ: str = 'Сообщение UID={uid} прочитано.'
DB_FETCHED: str = 'ИЗ БД успешно получено {amount} писем.'


@dataclass
class DB:
    """Класс базы данных."""

    conn: sqlite3.Connection = None
    cursor: sqlite3.Cursor = None

    def _db_create(self) -> None:
        """Создание таблиц в базе данных при запуске бота."""
        self.cursor.execute(DB_CREATETABLE)
        self.conn.commit()

    def db_connect(self) -> bool:
        """Подключение к локальной БД SQLite3."""
        try:
            self.conn = sqlite3.connect(DB_FILENAME)
            self.cursor = self.conn.cursor()
            self._db_create()
        except sqlite3.Error as error:
            logger.error(DB_ERROR.format(error=error,
                         method=self.db_connect.__name__))
        return self.conn

    def _db_fetchmany(self, all: bool) -> list | None:
        """Поиск записей в БД: при True всех, при False непрочитанных."""
        result = None
        try:
            self.cursor.execute(DB_SEARCH_ALL if all else DB_SEARCH_UNREAD)
            result = self.cursor.fetchall()
            logger.info(DB_FETCHED.format(amount=len(result)))
        except sqlite3.Error as error:
            logger.error(DB_ERROR.format(error=error,
                         method=self._db_fetchmany.__name__))
        return result

    def _db_insertmany(self, mails: dict) -> None:
        """Добавление множественных записей в БД."""
        try:
            data = []
            for uid, msg in mails.items():
                data.append((int(uid), *msg, 0))
            self.cursor.executemany(DB_INSERT, data)
            self.conn.commit()
            logger.info(DB_INSERTED.format(amount=len(data)))
        except sqlite3.Error as error:
            logger.error(DB_ERROR.format(error=error,
                         method=self._db_insertmany.__name__))

    def db_commitmails(self, mails: dict) -> None:
        """Проверка и добавление писем в БД."""
        existing_mails = self._db_fetchmany(True)
        mails_to_commit = {}
        for uid, msg in mails.items():
            if (int(uid), *msg) not in existing_mails:
                mails_to_commit[uid] = msg
        if mails_to_commit:
            self._db_insertmany(mails_to_commit)

    def db_setreadone(self, uid: int) -> None:
        """Установка метки о том, что сообщение прочитано."""
        try:
            self.cursor.execute(DB_UPDATE_READ.format(uid=uid))
            self.conn.commit()
            logger.info(DB_READ.format(uid=uid))
        except sqlite3.Error as error:
            logger.error(DB_ERROR.format(error=error,
                         method=self.db_setreadone.__name__))

    def _db_exit(self) -> bool:
        """Отключение от локальной БД SQLite3."""
        try:
            self.conn.close()
        except sqlite3.Error as error:
            logger.error(DB_ERROR.format(error=error,
                         method=self._db_exit.__name__))
