-- Every reportable hospital and condition pair with positive excess readmissions must reach the worklist. A join that drops pairs would understate the work.
select * from (
    select (select count(*) from {{ ref('mart_navigator_worklist') }}) as worklist_pairs,
           (select count(*) from {{ ref('fct_hospital_readmissions') }} where is_reportable_volume and excess_readmissions > 0) as fact_pairs
) where worklist_pairs <> fact_pairs
