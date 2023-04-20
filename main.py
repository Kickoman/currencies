import argparse
import nbrb
import mysql.connector
import os


def connect_to_database():
    return mysql.connector.connect(
        host=os.environ.get('CURR_DB_HOST'),
        port=os.environ.get('CURR_DB_PORT'),
        user=os.environ.get('CURR_DB_USER'),
        password=os.environ.get('CURR_DB_PASSWD'),
        database=os.environ.get('CURR_DB_NAME')
    )


def update_currencies_list(client: nbrb.Client, db_connection: mysql.connector.connection):
    query = (
        "INSERT INTO currency ( "
        "    internal_id,       " 
        "    internal_code,     "
        "    abbreviation,      "
        "    name,              "
        "    name_blr,          "
        "    scale,             "
        "    periodicity,       "
        "    date_start,        "
        "    date_end           "
        ") VALUES (%s, %s, %s, %s, %s, %s, %s, ?, ?)"
    )
    cursor = db_connection.cursor(prepared=True)
    for currency in client.available_currencies().values():
        cursor.execute(query, (
            currency.internal_id,
            currency.internal_code,
            currency.abbreviation,
            currency.name,
            currency.name_blr,
            currency.scale,
            currency.periodicity,
            currency.date_start.strftime('%Y-%m-%d %H:%M:%S'),
            currency.date_end.strftime('%Y-%m-%d %H:%M:%S'),
        ))
        db_connection.commit()


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

    client = nbrb.Client()
    update_currencies_list(client, connect_to_database())
    if args.currency is not None:
        get_single_rate(client, args.currency)


if __name__ == '__main__':
    main()
