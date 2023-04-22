-- Get the latest available rate for each currency

select name, abbreviation, date, rate
from (select c.name_blr          as name,
             c.abbreviation      as abbreviation,
             r.date              as date,
             r.rate              as rate,
             row_number() over w as date_age
      from rate as r
        left join currency c on r.currency_id = c.internal_id
      window w as (partition by currency_id order by date desc)) as res
where date_age = 1;
