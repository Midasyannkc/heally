{# The business case depends on two assumptions. Show the grid so nobody has to trust a single number. #}
select s.avertable_share, c.cost_per_readmission_usd,
       round(t.excess * s.avertable_share, 0)                                  as avoided_readmissions,
       round(t.excess * s.avertable_share * c.cost_per_readmission_usd, 0)     as savings_usd
from (select sum(excess_readmissions) as excess from {{ ref('mart_navigator_worklist') }}) t
cross join (values (0.05), (0.10), (0.15), (0.20)) s(avertable_share)
cross join (values (10000), (15000), (20000)) c(cost_per_readmission_usd)
