select measure_code, condition_label, condition_group from {{ ref('measure_labels') }}
