{# CMS publishes HRRP and General Information on different refresh cycles, so some HRRP hospitals have no General Information row.
   Keep them, flagged, instead of dropping their readmissions. #}
with info as (
    select *, true as in_general_info from {{ ref('stg_hospital_info') }}
),
hrrp_only as (
    select distinct facility_id, facility_name, state from {{ ref('stg_hrrp') }}
    where facility_id not in (select facility_id from info)
)
select facility_id, facility_name, address, city, state, zip_code, county, hospital_type, ownership,
       has_emergency_services, is_birthing_friendly, overall_star_rating, readm_measures_worse, in_general_info
from info
union all
select facility_id, facility_name, null, null, state, null, null, 'Unknown (not in Hospital General Information)', null,
       null, null, null, null, false
from hrrp_only
