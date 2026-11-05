{# Ranks hospital and condition pairs by excess readmissions and tiers them by cumulative share, so care navigators start where the volume is.
   Tier A holds the pairs that together reach tier_a_cumulative_share of all excess readmissions. #}
with base as (
    select f.facility_id, f.measure_code, m.condition_label, d.facility_name, d.state, d.county, d.city, d.ownership, d.overall_star_rating,
           f.discharges, f.excess_readmission_ratio, f.excess_readmissions
    from {{ ref('fct_hospital_readmissions') }} f
    join {{ ref('dim_hospital') }} d using (facility_id)
    join {{ ref('dim_measure') }} m using (measure_code)
    where f.is_reportable_volume and f.excess_readmissions > 0
),
ranked as (
    select *,
        row_number() over (order by excess_readmissions desc, facility_id, measure_code)                                        as outreach_rank,
        sum(excess_readmissions) over (order by excess_readmissions desc, facility_id, measure_code rows unbounded preceding)  as cumulative_excess,
        sum(excess_readmissions) over ()                                                                                       as total_excess
    from base
)
select
    facility_id, measure_code, condition_label, facility_name, state, county, city, ownership, overall_star_rating,
    discharges, excess_readmission_ratio,
    round(excess_readmissions, 2)                                  as excess_readmissions,
    outreach_rank,
    round(cumulative_excess / total_excess, 4)                     as cumulative_share,
    case when (cumulative_excess - excess_readmissions) / total_excess < {{ var('tier_a_cumulative_share') }} then 'A'
         when (cumulative_excess - excess_readmissions) / total_excess < {{ var('tier_b_cumulative_share') }} then 'B'
         else 'C' end                                              as priority_tier
from ranked
