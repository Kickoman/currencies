import database
import datetime
import math
import nbrb


class Spectator:
    def __init__(self, api_client: nbrb.Client, db_client: database.StorageDatabase):
        self.api_client = api_client
        self.db_client = db_client

        # Ensure DB client is connected
        self.db_client.connect()

    def currency_by_abbreviation(self, abbreviation: str) -> nbrb.Currency | None:
        if cur := self.db_client.get_currency_by_abbreviation(abbreviation):
            return cur
        return self.api_client.available_currencies().get(abbreviation, None)

    def rate_by_date(self, currency: nbrb.Currency, on_date: datetime.date | None = None) -> nbrb.Rate | None:
        on_date = on_date if on_date else datetime.date.today()
        if rt := self.db_client.get_rate(currency, on_date):
            return rt
        return self.api_client.rate(currency, on_date)

    def update_database(self):
        import time

        print('Making pure update of databases')

        time_start = time.time()

        def measure_time(prompt: str):
            nonlocal time_start
            print(f'{prompt} in {time.time() - time_start} seconds')
            time_start = time.time()

        self.db_client.connect()
        measure_time('Connected')

        currencies = list(self.api_client.available_currencies().values())
        measure_time('Updated local currencies')

        self.db_client.update_currencies(currencies)
        measure_time('Updated db currencies')

        rates = self.api_client.all_rates()
        measure_time('Updated local rates')

        # Log dates (and times)
        dates = [rate.date for rate in rates]
        min_date, max_date = min(dates), max(dates)
        print(f'Dates of rates from {min_date} to {max_date}')

        self.db_client.update_rates(rates)
        measure_time('Updated db rates')

    def check_limit_passed(self, currency: nbrb.Currency) -> bool | None:
        rate_for_today = self.rate_by_date(currency, datetime.date.today())
        rate_for_yesterday = self.rate_by_date(currency, datetime.date.today() - datetime.timedelta(days=1))

        if rate_for_today is None or rate_for_yesterday is None:
            return None

        rate_for_today = math.floor(rate_for_today.rate * 10) / 10
        rate_for_yesterday = math.floor(rate_for_yesterday.rate * 10) / 10
        return rate_for_today != rate_for_yesterday
