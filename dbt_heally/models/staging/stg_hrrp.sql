select
    lpad(facility_id, 6, '0')                                          as facility_id,
    facility_name,
    state,
    replace(replace(measure_name, 'READM-30-', ''), '-HRRP', '')      as measure_code,
    try_cast(number_of_discharges as integer)                              as discharges,
    try_cast(number_of_readmissions as integer)                            as readmissions,
    try_cast(excess_readmission_ratio as double)                           as excess_readmission_ratio,
    try_cast(predicted_readmission_rate as double)                         as predicted_readmission_rate,
    try_cast(expected_readmission_rate as double)                          as expected_readmission_rate,
    nullif(footnote, '')                                               as footnote_code,
    {{ parse_us_date('start_date') }}                                  as performance_start_date,
    {{ parse_us_date('end_date') }}                                    as performance_end_date,
    _synced_at
from {{ source('raw', 'hrrp') }}
