select * from (
    select sum(excess_readmissions) filter (where priority_tier = 'A') / sum(excess_readmissions) as tier_a_share
    from {{ ref('mart_navigator_worklist') }}
) where tier_a_share < {{ var('tier_a_cumulative_share') }}
