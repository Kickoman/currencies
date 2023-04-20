import argparse
import nbrb
import database
import os


def update_currencies_list(client: nbrb.Client, db_connection: database.StorageDatabase):
    # One by one update example
    for currency in client.available_currencies().values():
        print(f'Trying to insert {currency}')
        db_connection.update_currencies(currency)


def update_rates(client: nbrb.Client, db_connection: database.StorageDatabase):
    # Batch update example
    rates = client.all_rates()
    db_connection.update_rates(rates)


def pure_update():
    import time

    print('Making pure update of databases')
    api_client = nbrb.Client()
    with database.StorageDatabase(
            host=os.environ.get('CURR_DB_HOST'),
            port=int(os.environ.get('CURR_DB_PORT')),
            user=os.environ.get('CURR_DB_USER'),
            password=os.environ.get('CURR_DB_PASSWD'),
            database=os.environ.get('CURR_DB_NAME')
    ) as db_client:
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

        db_client.update_rates(rates)
        measure_time('Updated db rates')


def main():
    parser = argparse.ArgumentParser(description='Currencies processing')
    parser.add_argument(
        '--pure-update',
        action='store_true',
        help='if presented, only database update is performed'
    )

    args = parser.parse_args()

    if args.pure_update:
        pure_update()


if __name__ == '__main__':
    main()
