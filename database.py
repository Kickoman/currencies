import mysql.connector
import os
import nbrb


class StorageDatabase:
    def __init__(
            self,
            user: str,
            password: str,
            database: str,
            host: str = 'localhost',
            port: int = 3306,
    ):
        self._connection: mysql.connector.connection = None
        self.user: str = user
        self.password: str = password
        self.database: str = database
        self.host: str = host
        self.port: int = port

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            self._connection.close()

    @staticmethod
    def mysql_transform(obj) -> dict | list:
        from dataclasses import fields, is_dataclass
        from datetime import datetime, date

        def mysql_type_prepare(value):
            if isinstance(value, datetime):
                return value.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(value, date):
                return value.strftime('%Y-%m-%d')
            return value

        def transform(value):
            if not is_dataclass(value):
                raise ValueError(f'The object {value.__class__.__name__} is not a dataclass')

            return {
                field.name: mysql_type_prepare(getattr(value, field.name))
                for field in fields(value)
            }

        if isinstance(obj, list):
            return [transform(val) for val in obj]
        return transform(obj)

    def _execute_write_query(self, query: str, parameters: dict | list[dict] | None = None):
        cursor = self._connection.cursor(prepared=True)
        if isinstance(parameters, dict):
            cursor.execute(query, parameters)
        else:
            cursor.executemany(query, parameters)
        self._connection.commit()
        cursor.close()

    def connect(self):
        self._connection = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def update_currencies(self, currency: nbrb.Currency | list[nbrb.Currency]):
        if self._connection is None:
            raise ConnectionError(f'Connection to db {self.host} is closed')
        query = (
            "INSERT IGNORE INTO currency ( "
            "    internal_id,       "
            "    internal_code,     "
            "    abbreviation,      "
            "    name,              "
            "    name_blr,          "
            "    scale,             "
            "    periodicity,       "
            "    date_start,        "
            "    date_end           "
            ") VALUES ("
            "    %(internal_id)s, "
            "    %(internal_code)s, "
            "    %(abbreviation)s, "
            "    %(name)s, "
            "    %(name_blr)s, "
            "    %(scale)s, "
            "    %(periodicity)s, "
            "    %(date_start)s, "
            "    %(date_end)s"
            ")"
        )
        currency = StorageDatabase.mysql_transform(currency)
        self._execute_write_query(query, currency)

    def update_rates(self, rate: nbrb.Rate | list[nbrb.Rate]):
        if self._connection is None:
            raise ConnectionError(f'Connection to db {self.host} is closed')
        query = (
            "INSERT IGNORE INTO rate ("
            "    date,"
            "    currency_id,"
            "    rate"
            ") VALUES ("
            "    %(date)s, "
            "    %(internal_id)s, "
            "    %(rate)s"
            ")"
        )
        rate = StorageDatabase.mysql_transform(rate)
        self._execute_write_query(query, rate)
