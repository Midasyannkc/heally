select
    e.facility_id, e.measure_code, e.state,
    e.discharges, e.readmissions, e.excess_readmission_ratio, e.predicted_readmission_rate, e.expected_readmission_rate,
    e.excess_readmissions, e.is_reportable_volume, e.is_above_expected, e.footnote_code,
    e.performance_start_date, e.performance_end_date
from {{ ref('int_hospital_measure_excess') }} e
join {{ ref('dim_hospital') }} d using (facility_id)
