select facility_id, count(distinct state) as states from {{ ref('stg_hrrp') }} group by 1 having count(distinct state) > 1
