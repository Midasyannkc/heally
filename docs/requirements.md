# Requirements: from stakeholder question to model

**Status of this document:** the stakeholders below are hypothetical. No Wellthy employee was interviewed. The questions are the ones an analytics engineer would ask first, and each answer shows how it becomes a model, a metric and a test.

## Who needs what

| Stakeholder | Business question | Decision it supports |
| --- | --- | --- |
| Care Team lead | Which hospital discharges should navigators watch first? | Where to point outreach hours |
| Client Success | How exposed is each health plan or employer partner, by state? | What goes in partner reviews |
| Marketing | Which states and conditions make the strongest story for a new health plan pitch? | New revenue conversations |
| VP Data, Product and Engineering Ops | Can every team read the same number without a data request? | Self-service and trust |

## Questions asked before building

1. What action follows the number? (A ranked worklist, not a report.)
2. How fresh does it need to be? (CMS refreshes periodically, so weekly sync with a 7 day freshness error.)
3. What would make you stop trusting it? (A metric that differs between the dashboard and the worklist, see INC-5.)
4. Which population is it about? (Medicare fee-for-service only, stated on every page.)
5. What is the unit of work? (A hospital and condition pair.)

## Traceability

| Requirement | Model or metric | Test that protects it |
| --- | --- | --- |
| Rank pairs by avoidable volume | `mart_navigator_worklist` | `assert_worklist_reconciles_to_fact`, unit test on tiering |
| Partner exposure by state | `mart_state_exposure` | `assert_state_totals_reconcile_to_fact` |
| One definition of excess readmissions | semantic metric `excess_readmissions` | `tests/test_inc5_metric_matches_mart.py` |
| Business case with visible assumptions | `mart_business_case`, `mart_savings_sensitivity` | dbt vars in one place, grid of scenarios |
| Do not lose hospitals | `dim_hospital` | `tests/test_inc3_hospitals_missing_from_general_info.py` |
| Worklist available where navigators work | reverse ETL to the CRM | `tests/test_reverse_etl.py` |

## Where Snowplow would plug in

Product event data (which dashboard filters Care Team members use, which worklist rows get actioned) would land as Snowplow events, be sessionized in a dbt model, and measure whether the worklist changes behavior. This project has no event data, so that layer is not built.
