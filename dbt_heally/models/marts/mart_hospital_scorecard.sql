{# One row per hospital: the table an analyst opens first when exploring. #}
select
    d.facility_id, d.facility_name, d.state, d.county, d.city, d.ownership, d.hospital_type, d.overall_star_rating, d.in_general_info,
    count(*)                                                    as measures_reported_rows,
    count(f.excess_readmission_ratio)                           as measures_with_ratio,
    sum(case when f.is_above_expected then 1 else 0 end)        as measures_above_expected,
    sum(f.discharges)                                           as discharges,
    round(sum(greatest(f.excess_readmissions, 0)), 2)           as excess_readmissions,
    round(avg(f.excess_readmission_ratio), 4)                   as avg_excess_readmission_ratio
from {{ ref('fct_hospital_readmissions') }} f
join {{ ref('dim_hospital') }} d using (facility_id)
group by all
