# ADR 2: The pipeline fails closed

Status: accepted. Sync, dbt build, monitors and reverse ETL run in order, and nothing downstream of a failed step runs. A schema drift stops before dbt; a failed test stops before the CRM sync; reverse ETL refuses to retire most of the destination. Trade-off: a noisy check can block a run, so every check has a runbook entry.
