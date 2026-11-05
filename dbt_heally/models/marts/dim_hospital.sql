select
    facility_id, facility_name, address, city, state, zip_code, county, hospital_type, ownership,
    has_emergency_services, is_birthing_friendly, overall_star_rating, readm_measures_worse
from {{ ref('stg_hospital_info') }}
