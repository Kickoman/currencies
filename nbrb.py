from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


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
        return result.json()

    @staticmethod
    def _currency_from_dict(raw: dict) -> Currency:
        return Currency(
            internal_id=raw['Cur_ID'],
            internal_code=raw['Cur_Code'],
            abbreviation=raw['Cur_Abbreviation'],
            name=raw['Cur_Name_Eng'],
            name_blr=raw['Cur_Name_Bel'],
            scale=raw['Cur_Scale'],
            periodicity=raw['Cur_Periodicity'],
            date_start=datetime.fromisoformat(raw['Cur_DateStart']),
            date_end=datetime.fromisoformat(raw['Cur_DateEnd']),
        )

    @staticmethod
    def _rate_from_dict(raw):
        return Rate(
            internal_id=raw['Cur_ID'],
            date=datetime.fromisoformat(raw['Date']),
            abbreviation=raw['Cur_Abbreviation'],
            rate=Decimal(str(raw['Cur_OfficialRate']))
        )

    def available_currencies(self) -> dict:
        if self._available_currencies is None:
            response = Client._make_api_call(Client.API_CURRENCIES)
            self._available_currencies = {
                row['Cur_Abbreviation']: Client._currency_from_dict(row) for row in response
            }
        return self._available_currencies

    def rate(self, currency: str | Currency) -> Rate:
        if not isinstance(currency, Currency):
            currency = self.available_currencies()[currency]
        currency_code = currency.internal_id
        row = Client._make_api_call(Client.API_RATES + f'/{currency_code}')
        return Client._rate_from_dict(row)

    def all_rates(self) -> list[Rate]:
        res = self._make_api_call(Client.API_RATES)
        return [Client._rate_from_dict(row) for row in res]
