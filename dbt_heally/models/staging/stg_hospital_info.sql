select
    lpad(facility_id, 6, '0')                         as facility_id,
    facility_name,
    address,
    city_town                                         as city,
    state,
    lpad(zip_code, 5, '0')                            as zip_code,
    county_parish                                     as county,
    hospital_type,
    hospital_ownership                                as ownership,
    emergency_services = 'Yes'                        as has_emergency_services,
    meets_criteria_for_birthing_friendly_designation = 'Y' as is_birthing_friendly,
    try_cast(hospital_overall_rating as integer)          as overall_star_rating,
    try_cast(count_of_readm_measures_worse as integer)    as readm_measures_worse
from {{ source('raw', 'hospital_info') }}
