{# Where a health plan or employer partner's members are most exposed to avoidable readmissions. #}
select
    state,
    count(distinct facility_id)                                                       as hospitals,
    count(*) filter (where is_above_expected is not null)                             as hospital_measure_pairs_with_ratio,
    round(avg(case when is_above_expected then 1.0 else 0.0 end) filter (where is_above_expected is not null), 4) as share_pairs_above_expected,
    sum(discharges)                                                                   as discharges,
    round(sum(greatest(excess_readmissions, 0)), 2)                                   as excess_readmissions,
    round(1000.0 * sum(greatest(excess_readmissions, 0)) / nullif(sum(discharges), 0), 2) as excess_readmissions_per_1000_discharges,
    round(sum(greatest(excess_readmissions, 0)) * {{ var('avertable_share') }} * {{ var('avg_readmission_cost_usd') }}, 0) as scenario_savings_usd_period
from {{ ref('fct_hospital_readmissions') }}
where is_reportable_volume
group by state
