select * from (
    select (select sum(excess_readmissions) from {{ ref('mart_state_exposure') }}) as state_total,
           (select sum(greatest(excess_readmissions, 0)) from {{ ref('fct_hospital_readmissions') }} where is_reportable_volume) as fact_total
) where abs(state_total - fact_total) > 1
