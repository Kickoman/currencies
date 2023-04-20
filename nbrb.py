from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import json


@dataclass
class Currency:
    internal_id: int | None
    internal_code: str | None
    abbreviation: str
    name: str
    name_blr: str
    scale: Decimal
    periodicity: int  # Todo: what does it mean?
    date_start: datetime
    date_end: datetime


@dataclass
class Rate:
    internal_id: int | None
    date: datetime
    abbreviation: str
    rate: Decimal


class Client:
    API_BASE_URL = 'https://www.nbrb.by/api/exrates/'
    API_CURRENCIES = 'currencies/'
    API_RATES = 'rates/'
    API_USD_CODE = 431

    def __init__(self):
        self._available_currencies: dict[str, Currency] | None = None

    @staticmethod
    def _make_api_call(method, parameters: dict | None = None) -> dict | list:
        import requests
        url = f'{Client.API_BASE_URL}{method}'
        result = requests.get(url, parameters)
        result.raise_for_status()
        return json.loads(result.text)

    def available_currencies(self) -> dict:
        if self._available_currencies is None:
            response = Client._make_api_call(Client.API_CURRENCIES)
            self._available_currencies = {
                row['Cur_Abbreviation']: Currency(
                    internal_id=row['Cur_ID'],
                    internal_code=row['Cur_Code'],
                    abbreviation=row['Cur_Abbreviation'],
                    name=row['Cur_Name_Eng'],
                    name_blr=row['Cur_Name_Bel'],
                    scale=row['Cur_Scale'],
                    periodicity=row['Cur_Periodicity'],
                    date_start=datetime.fromisoformat(row['Cur_DateStart']),
                    date_end=datetime.fromisoformat(row['Cur_DateEnd']),
                ) for row in response
            }
        return self._available_currencies

    def rate(self, currency: str | Currency) -> Rate:
        if not isinstance(currency, Currency):
            currency = self.available_currencies()[currency]
        currency_code = currency.internal_id
        row = Client._make_api_call(Client.API_RATES + f'/{currency_code}')
        return Rate(
            internal_id=row['Cur_ID'],
            date=datetime.fromisoformat(row['Date']),
            abbreviation=row['Cur_Abbreviation'],
            rate=Decimal(str(row['Cur_OfficialRate']))
        )
