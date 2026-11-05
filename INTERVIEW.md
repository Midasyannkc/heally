# Interview guide: presenting Heally

## The two-minute version

"Care navigators have limited hours and a hospital stay is the costliest moment in a family's care journey. I took two real CMS datasets on hospital readmissions and built the pipeline an analytics engineer would own: a tested ELT load, a dbt model layer, governed metrics, a dashboard people can use without asking me, and a worklist pushed to the CRM. The model shows that 457 hospital and condition pairs, 10.6% of the total, hold half of the estimated excess readmissions, so outreach can start there. The savings figures are scenarios with visible assumptions, not findings. Along the way five things broke, and each has a failing test and then a fix in the git history."

## Posting responsibility to proof

| The posting says | Say this | Show this |
| --- | --- | --- |
| dbt transformations and self-service | Layered staging, intermediate, marts; metrics defined once; a dashboard filterable by state and tier | `dbt_heally/models/`, `dashboard/index.html` |
| Efficient, well-tested code, ELT automation | One command runs the whole flow and fails closed; a second run changes nothing | `heally/pipeline.py`, `tests/test_pipeline.py` |
| Translate stakeholder needs | Question, decision, then model, metric and test | `docs/requirements.md` (hypothetical stakeholders, say so) |
| Quality, accessibility, governance | Contracts, reconciliations, docs site, access roles | `docs/governance.md`, `docs/dbt_docs.html` |
| Tests | 29 data tests, 3 unit tests, 4 singular reconciliations, plus pytest around the pipeline | `dbt_heally/tests/`, `tests/` |
| Evaluate tools | Three evaluations with what was tried and what was only read | `docs/tool_evaluation.md` |
| Troubleshoot and communicate | Runbook with escalation triggers; incident log | `docs/runbook.md`, `docs/incidents.md` |
| Work with seniors | Open questions listed for review, not silently decided | `docs/design_review.md` |

## Questions to expect

**Why does the worklist use positive excess only?** Outreach is about where readmissions exceed expectation. Netting a good hospital against a bad one hides work. A net view is a separate question (see the design review file).

**How do you know the CMS files are right?** Row counts and the star-rating pattern match an independent public analysis, the ratio equals predicted over expected within 0.001 on every row (a singular test), and every number reconciles to the fact table. They were not compared with CMS directly because that site was unreachable from the build environment.

**What broke?** Three on the real data (a registry that described 14 of 38 columns, text inside numeric columns, 20 hospitals missing from one file) and two I found by review (a new condition code dropped by a join, a metric that disagreed with the marts). Say which are which.

**Have you used Fivetran, Hightouch, Metaplane, Omni, Snowplow?** Be direct: the patterns are built (incremental sync with drift handling, diff-based reverse ETL, observability monitors, governed metrics with a self-service surface), not the products. Snowplow is not covered. Snowflake is written, not run.

**What would you do next?** Run the Snowflake target in a staging account, add incremental merge on the row hash, add event data for the dashboard so adoption can be measured, and agree the excess readmission definition with the clinical team.

## Do not claim

- That the savings are real. They are scenarios.
- That the data covers all Wellthy members. It covers Medicare fee-for-service.
- Experience with the named vendor products.
