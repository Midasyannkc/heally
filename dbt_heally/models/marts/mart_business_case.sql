{# Headline numbers for the business case. Costs and the avertable share are assumptions set in dbt_project.yml, not CMS data. #}
with w as (select * from {{ ref('mart_navigator_worklist') }}),
tot as (select count(*) as pairs, sum(excess_readmissions) as excess from w),
a as (select count(*) as pairs, sum(excess_readmissions) as excess from w where priority_tier = 'A')
select
    tot.pairs                                                         as worklist_pairs,
    a.pairs                                                           as tier_a_pairs,
    round(a.pairs * 1.0 / tot.pairs, 4)                               as tier_a_share_of_pairs,
    round(tot.excess, 1)                                              as excess_readmissions,
    round(a.excess / tot.excess, 4)                                   as tier_a_share_of_excess,
    {{ var('avertable_share') }}                                      as assumed_avertable_share,
    {{ var('avg_readmission_cost_usd') }}                             as assumed_cost_per_readmission_usd,
    round(tot.excess * {{ var('avertable_share') }}, 0)               as avoided_readmissions_all_tiers,
    round(a.excess * {{ var('avertable_share') }}, 0)                 as avoided_readmissions_tier_a,
    round(tot.excess * {{ var('avertable_share') }} * {{ var('avg_readmission_cost_usd') }}, 0) as savings_usd_all_tiers,
    round(a.excess * {{ var('avertable_share') }} * {{ var('avg_readmission_cost_usd') }}, 0)   as savings_usd_tier_a
from tot, a
