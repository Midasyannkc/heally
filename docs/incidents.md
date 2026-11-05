# Incident log

Every incident has two commits. The first adds a test that fails for the right reason; a later one fixes the code and the same test passes. Hashes below come from `git log`.

| # | Incident | Found by | Reproduce | Fix |
| --- | --- | --- | --- | --- |
| INC-1 | Source registry listed 14 of 38 hospital columns | first load of the real Hospital General Information file (real data) | `39e13ab` | `0e3dbec` |
| INC-2 | CMS suppression text crashed typed staging | profiling the real files, then the first dbt run (real data) | `f0326e6` | `6c68745` |
| INC-3 | 20 hospitals in HRRP are missing from General Information | profiling the real files (real data) | `12b18f5` | `7932789` |
| INC-4 | A new CMS condition code was silently dropped from the worklist | SIMULATED CMS refresh while reviewing joins; the current real files are not affected | `4f65aa4` | `e4abafa` |
| INC-5 | Governed metric disagreed with the marts | review of metric and mart definitions; LATENT, the current real files do not trigger it | `8fff0a5` | `0cd64f1` |

### INC-1: Source registry listed 14 of 38 hospital columns

The loader's contract for the hospital file listed 14 columns, but the real CMS file has 38. Every first load therefore reported 24 added columns, which would bury a genuine drift alert in noise. The registry now lists all 38 columns, so only a real change is reported.

Reproduce `39e13ab`, fix `0e3dbec`. Found by: first load of the real Hospital General Information file (real data).

### INC-2: CMS suppression text crashed typed staging

CMS puts text inside numeric columns: N/A for 10,088 discharge counts, Too Few to Report for 3,683 readmission counts, and Not Available for 2,245 star ratings. A plain cast stopped the build. Staging now uses try_cast, so suppressed cells become null and the footnote code keeps the reason.

Reproduce `f0326e6`, fix `6c68745`. Found by: profiling the real files, then the first dbt run (real data).

### INC-3: 20 hospitals in HRRP are missing from General Information

The fact table inner-joined the hospital dimension, so readmission rows for 20 hospitals would have disappeared with no error. dim_hospital now keeps those hospitals, flagged in_general_info = false, and a relationships test guards the join.

Reproduce `12b18f5`, fix `7932789`. Found by: profiling the real files (real data).

### INC-4: A new CMS condition code was silently dropped from the worklist

The worklist inner-joined a label seed, so a condition CMS adds in a later refresh would vanish from the work queue. The join is now a left join with an Unlabeled measure fallback, and a singular test reconciles the worklist to the fact table.

Reproduce `4f65aa4`, fix `e4abafa`. Found by: SIMULATED CMS refresh while reviewing joins; the current real files are not affected.

### INC-5: Governed metric disagreed with the marts

The semantic layer measure summed excess readmissions for every pair, while the marts count only pairs with reportable volume (25 or more discharges). With a small hospital that has a published ratio, a self-service user would see a different number than the dashboard. The measure now applies the same rule and a test compares the two.

Reproduce `8fff0a5`, fix `0cd64f1`. Found by: review of metric and mart definitions; LATENT, the current real files do not trigger it.
