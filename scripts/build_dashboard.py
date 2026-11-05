"""Build the self-service dashboard: one HTML file with the marts embedded, filterable by state and tier (the Omni-style surface for Care, Client Success and Marketing)."""
import json
import os

import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con = duckdb.connect(os.path.join(ROOT, "out", "heally.duckdb"), read_only=True)
rows = lambda sql: [dict(zip([d[0] for d in con.description], r)) for r in con.execute(sql).fetchall()]
data = {
    "kpi": rows("select * from marts.mart_business_case")[0],
    "states": rows("select * from marts.mart_state_exposure order by excess_readmissions desc"),
    "worklist": rows("select facility_id, facility_name, state, county, condition_label, overall_star_rating, discharges, excess_readmission_ratio, excess_readmissions, outreach_rank, cumulative_share, priority_tier from marts.mart_navigator_worklist order by outreach_rank"),
    "stars": rows("select overall_star_rating as stars, count(*) hospitals, round(avg(avg_excess_readmission_ratio),4) avg_ratio from marts.mart_hospital_scorecard where overall_star_rating is not null group by 1 order by 1"),
    "sens": rows("select * from marts.mart_savings_sensitivity order by 1,2"),
}
tpl = open(os.path.join(ROOT, "dashboard", "template.html")).read()
open(os.path.join(ROOT, "dashboard", "index.html"), "w").write(tpl.replace("__DATA__", json.dumps(data, default=str)))
print("dashboard built", len(data["worklist"]), "worklist rows")
