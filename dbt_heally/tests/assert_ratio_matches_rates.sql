-- CMS defines the excess readmission ratio as predicted rate divided by expected rate. A published ratio that disagrees means a bad load or a bad parse.
select facility_id, measure_code, excess_readmission_ratio, predicted_readmission_rate / expected_readmission_rate as recomputed
from {{ ref('stg_hrrp') }}
where excess_readmission_ratio is not null and predicted_readmission_rate is not null and expected_readmission_rate > 0
  and abs(excess_readmission_ratio - predicted_readmission_rate / expected_readmission_rate) > 0.001
