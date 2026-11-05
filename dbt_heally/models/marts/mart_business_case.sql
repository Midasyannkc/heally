{# Headline numbers for the business case. HRRP covers a multi-year performance window, so counts are annualized.
   Cost per readmission and the avertable share are assumptions set in dbt_project.yml, not CMS data. #}
with w as (select * from {{ ref('mart_navigator_worklist') }}),
period as (
    select greatest(1.0, round((max(performance_end_date) - min(performance_start_date)) / 365.25, 1)) as years
    from {{ ref('fct_hospital_readmissions') }}
),
tot as (select count(*) as pairs, sum(excess_readmissions) as excess, sum(discharges) as discharges from w),
a as (select count(*) as pairs, sum(excess_readmissions) as excess, sum(discharges) as discharges from w where priority_tier = 'A')
select
    period.years                                                      as performance_period_years,
    tot.pairs                                                         as worklist_pairs,
    a.pairs                                                           as tier_a_pairs,
    round(a.pairs * 1.0 / tot.pairs, 4)                               as tier_a_share_of_pairs,
    round(tot.excess, 1)                                              as excess_readmissions_period,
    round(tot.excess / period.years, 1)                               as excess_readmissions_per_year,
    round(a.excess / tot.excess, 4)                                   as tier_a_share_of_excess,
    round(1000.0 * a.excess / a.discharges, 1)                        as tier_a_excess_per_1000_discharges,
    round(1000.0 * tot.excess / tot.discharges, 1)                    as all_pairs_excess_per_1000_discharges,
    {{ var('avertable_share') }}                                      as assumed_avertable_share,
    {{ var('avg_readmission_cost_usd') }}                             as assumed_cost_per_readmission_usd,
    round(tot.excess / period.years * {{ var('avertable_share') }}, 0) as avoided_readmissions_per_year_all_tiers,
    round(a.excess / period.years * {{ var('avertable_share') }}, 0)   as avoided_readmissions_per_year_tier_a,
    round(tot.excess / period.years * {{ var('avertable_share') }} * {{ var('avg_readmission_cost_usd') }}, 0) as savings_usd_per_year_all_tiers,
    round(a.excess / period.years * {{ var('avertable_share') }} * {{ var('avg_readmission_cost_usd') }}, 0)   as savings_usd_per_year_tier_a
from tot, a, period
