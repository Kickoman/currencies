import argparse
import database
import datetime
import nbrb
import os


def get_database_connection():
    return database.StorageDatabase(
            host=os.environ.get('CURR_DB_HOST'),
            port=int(os.environ.get('CURR_DB_PORT')),
            user=os.environ.get('CURR_DB_USER'),
            password=os.environ.get('CURR_DB_PASSWD'),
            database=os.environ.get('CURR_DB_NAME')
    )


def pure_update():
    import time

    print('Making pure update of databases')
    api_client = nbrb.Client()
    with get_database_connection() as db_client:
        time_start = time.time()

        def measure_time(prompt: str):
            nonlocal time_start
            print(f'{prompt} in {time.time() - time_start} seconds')
            time_start = time.time()

        db_client.connect()
        measure_time('Connected')

        currencies = list(api_client.available_currencies().values())
        measure_time('Updated local currencies')

        db_client.update_currencies(currencies)
        measure_time('Updated db currencies')

        rates = api_client.all_rates()
        measure_time('Updated local rates')

        # Log dates (and times)
        dates = [rate.date for rate in rates]
        min_date, max_date = min(dates), max(dates)
        print(f'Dates of rates from {min_date} to {max_date}')

        db_client.update_rates(rates)
        measure_time('Updated db rates')


def print_rate(usd_abbreviation: str, on_date: datetime.date | None = None):
    on_date = on_date if on_date else datetime.date.today()
    api_client = nbrb.Client()

    def get_currency(abbreviation: str):
        if cur := db_client.get_currency_by_abbreviation(abbreviation):
            return cur
        return api_client.available_currencies().get(abbreviation, None)

    def get_rate(currency: nbrb.Currency, on_date: datetime.date):
        if rt := db_client.get_rate(currency, on_date):
            return rt
        return api_client.rate(currency, on_date)

    with get_database_connection() as db_client:
        db_client.connect()
        # Try to get currency from database
        if (currency := get_currency(usd_abbreviation)) is None:
            print(f'Cannot find such a currency {usd_abbreviation}')
            return

        if (rate := get_rate(currency, on_date)) is None:
            print(f'Cannot fetch rate for {usd_abbreviation} on date {on_date.strftime("%Y-%m-%d")}')
            return

        print(f'{usd_abbreviation} ({currency.name_blr}) on {on_date.strftime("%Y-%m-%d")} was {rate.rate} BYN')


def main():
    parser = argparse.ArgumentParser(description='Currencies processing')
    parser.add_argument(
        '--pure-update',
        action='store_true',
        help='if presented, only database update is performed'
    )
    parser.add_argument(
        '--currency-rate',
        type=str,
        help='if presented, the rate for currency code is printed'
    )
    parser.add_argument(
        '--date',
        type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'),
        help='date for the currency. if no date, today assumed'
    )

    args = parser.parse_args()

    if args.pure_update:
        pure_update()

    if args.currency_rate:
        print_rate(args.currency_rate, args.date)


if __name__ == '__main__':
    main()
