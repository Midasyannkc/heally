{# The business case depends on two assumptions. Show the grid so nobody has to trust a single number. Annualized. #}
select s.avertable_share, c.cost_per_readmission_usd,
       round(t.excess_per_year * s.avertable_share, 0)                                  as avoided_readmissions_per_year,
       round(t.excess_per_year * s.avertable_share * c.cost_per_readmission_usd, 0)     as savings_usd_per_year
from (select excess_readmissions_per_year as excess_per_year from {{ ref('mart_business_case') }}) t
cross join (values (0.05), (0.10), (0.15), (0.20)) s(avertable_share)
cross join (values (10000), (15000), (20000)) c(cost_per_readmission_usd)
