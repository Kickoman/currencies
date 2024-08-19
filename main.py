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

    import spectator

    with get_database_connection() as db_client:
        spec = spectator.Spectator(nbrb.Client(), db_client)

        if args.pure_update:
            spec.update_database()
        if args.currency_rate:
            currency = spec.currency_by_abbreviation(args.currency_rate)
            rate = spec.rate_by_date(currency, args.date)
            print(rate.rate)

        main_currencies = ['EUR', 'USD', 'RUB', 'CNY']
        for currency_abbreviation in main_currencies:
            currency = spec.currency_by_abbreviation(currency_abbreviation)
            passed_string = 'passed' if spec.check_limit_passed(currency) else 'has not passed'
            print(f'{currency.name} {passed_string} the limit!}')


if __name__ == '__main__':
    main()
