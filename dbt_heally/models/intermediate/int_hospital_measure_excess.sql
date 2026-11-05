{# Excess readmissions = discharges x (predicted - expected rate) / 100. Only computable when CMS reports discharges and both rates. #}
select
    h.*,
    h.discharges >= {{ var('min_reportable_discharges') }}                       as is_reportable_volume,
    h.excess_readmission_ratio > 1                                                as is_above_expected,
    case when h.discharges is not null and h.predicted_readmission_rate is not null and h.expected_readmission_rate is not null
         then h.discharges * (h.predicted_readmission_rate - h.expected_readmission_rate) / 100.0 end as excess_readmissions
from {{ ref('stg_hrrp') }} h
