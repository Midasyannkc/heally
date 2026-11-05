{{ config(materialized='table') }}
-- Daily calendar MetricFlow needs for time-based metrics. DuckDB syntax; the Snowflake target would use a generator table function.
select cast(d as date) as date_day from generate_series(date '2018-01-01', date '2030-12-31', interval 1 day) t(d)
