# Tool evaluations

Three evaluations made while building. For each: what was actually tried, what was only read, and the decision.

## 1. Warehouse for development and CI: DuckDB or Snowflake
Tried: DuckDB with dbt-duckdb for all runs. Not tried: a Snowflake account. Decision: DuckDB for local development and CI (no cost, whole run in about 20 seconds, 47 dbt nodes), Snowflake as the production target through the `snowflake` output in `dbt_heally/profiles.yml`. Cross-warehouse differences are isolated in one macro (`parse_us_date`).
Risk: SQL that works on DuckDB may need changes on Snowflake (the time spine and `values` clauses). Run the Snowflake target in a staging account before trusting it.

## 2. Metric definitions: dbt semantic layer or plain marts
Tried: semantic models and metrics parse and generate `semantic_manifest.json`. The MetricFlow command line could not load that manifest because of a version mismatch with dbt-core 1.12 (not resolved). Decision: keep the definitions in YAML as the governed source and enforce agreement with the marts by test, which found INC-5. Revisit when the MetricFlow and dbt-core versions line up.

## 3. Observability: build or buy
Tried: four monitors (volume, freshness, null rate, schema drift) in about 90 lines, persisted to `ops.monitor_results`. Not tried: a vendor product. A vendor adds learned anomaly baselines, column-level lineage, a UI and alert routing. Decision: the in-repo monitors are enough for two source files; evaluate a vendor when the source count and the number of alert recipients grow.

## Scorecard used

| Criterion | Weight |
| --- | --- |
| Works in CI without credentials | high |
| Failure is visible to non-engineers | high |
| Cost at current scale | medium |
| Lock-in | medium |
| Time to first useful result | medium |
