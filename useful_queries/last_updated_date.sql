-- Last updated date per currency

select
    any_value(c.name_blr) as name,
    any_value(c.abbreviation) as abbreviation,
    max(r.date) as last_updated_date
from rate as r
         left join currency c on r.currency_id = c.internal_id
group by r.currency_id
order by name;
