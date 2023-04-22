from datetime import datetime, date
import nbrb
import mysql.connector


class QueryResult:
    def __init__(self, cursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._cursor:
            self._cursor.close()

    def fetch_one(self):
        return self._cursor.fetchone()

    def fetch_all(self):
        return self._cursor.fetchall()


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

    def _raise_on_no_connection(self):
        if self._connection is None:
            raise ConnectionError(f'Connection to {self.user}@{self.host}:{self.port}/{self.database} is closed.')

    def _execute_query(self, query: str, parameters: dict | list[dict] | None = None):
        cursor = self._connection.cursor(prepared=True)
        if isinstance(parameters, dict):
            cursor.execute(query, parameters)
        else:
            cursor.executemany(query, parameters)
        return cursor

    def _execute_write_query(self, query: str, parameters: dict | list[dict] | None = None):
        cursor = self._execute_query(query, parameters)
        self._connection.commit()
        cursor.close()

    def _execute_read_query(self, query: str, parameters: dict | list[dict] | None = None):
        cursor = self._execute_query(query, parameters)
        return QueryResult(cursor)

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
        currency = mysql_transform(currency)
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
        rate = mysql_transform(rate)
        self._execute_write_query(query, rate)

    def get_rate(self, currency: nbrb.Currency, on_date: date = date.today()) -> nbrb.Rate | None:
        self._raise_on_no_connection()
        query = "SELECT * FROM rate WHERE date = %(date)s and currency_id = %(currency_id)s"
        with self._execute_read_query(query, {
            "date": mysql_type_prepare(on_date),
            "currency_id": currency.internal_id
        }) as result:
            row = result.fetch_one()
            return nbrb.Rate(*row) if row else None

    def get_currency_by_abbreviation(self, abbreviation: str) -> nbrb.Currency | None:
        self._raise_on_no_connection()
        query = "SELECT * FROM currency WHERE abbreviation = %(abbreviation)s"
        with self._execute_read_query(query, {"abbreviation": abbreviation}) as result:
            row = result.fetch_one()
            return nbrb.Currency(*row) if row else None


def mysql_type_prepare(value):
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(value, date):
        return value.strftime('%Y-%m-%d')
    return value


def mysql_transform(obj) -> dict | list:
    from dataclasses import fields, is_dataclass

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
