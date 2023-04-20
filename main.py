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


def get_single_rate(client: nbrb.Client, currency_name: str):
    currency = client.available_currencies().get(currency_name, None)
    if currency is None:
        raise ValueError(f'Unknown currency {currency_name}')

    rate = client.rate(currency)
    print(f'{currency.scale} {currency_name} = {rate.rate} BYN')


def main():
    parser = argparse.ArgumentParser(description='Currencies processing')
    parser.add_argument(
        '--currency',
        type=str,
        help='if presented, the currency'
    )

    args = parser.parse_args()

    api_client = nbrb.Client()
    with database.StorageDatabase(
        host=os.environ.get('CURR_DB_HOST'),
        port=int(os.environ.get('CURR_DB_PORT')),
        user=os.environ.get('CURR_DB_USER'),
        password=os.environ.get('CURR_DB_PASSWD'),
        database=os.environ.get('CURR_DB_NAME')
    ) as db_client:
        db_client.connect()
        update_currencies_list(api_client, db_client)
        update_rates(api_client, db_client)

    if args.currency is not None:
        get_single_rate(api_client, args.currency)


if __name__ == '__main__':
    main()
