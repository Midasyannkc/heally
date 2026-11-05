# ADR 1: Reconcile every published number to the fact table

Status: accepted. Singular dbt tests compare the worklist, the state mart and the semantic metric with the fact table. The cost is a few extra queries per build. The benefit is that a join or definition change cannot quietly move a number a stakeholder uses (INC-3, INC-4, INC-5).
