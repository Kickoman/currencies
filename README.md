# NBRB Fetcher

---

**Warning!** FYI: [NBRB API](https://www.nbrb.by/api/exrates/) may not be accessible outside of Belarus.

---

1. Create tables according to `schema.sql` file.
2. Set your database credentials as environment variables:
   1. `CURR_DB_HOST`: database host;
   2. `CURR_DB_PORT`: database port;
   3. `CURR_DB_USER`: database user;
   4. `CURR_DB_PASSWD`: database password;
   5. `CURR_DB_NAME`: database name.
3. Run `python3 main.py --pure-update`
4. ???
5. Profit
