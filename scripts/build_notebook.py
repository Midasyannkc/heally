"""Build and execute the exploration notebook (the analyst's view of the marts, DeepNote-style)."""
import os

import nbformat as nbf
from nbclient import NotebookClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md("# Where should care navigators start? Exploring CMS hospital readmissions\n\nEvery number comes from the dbt marts in `out/heally.duckdb`, built from two CMS Provider Data files "
       "([HRRP 9n3s-kdb3](https://data.cms.gov/provider-data/dataset/9n3s-kdb3), [Hospital General Information xubh-q36u](https://data.cms.gov/provider-data/dataset/xubh-q36u)). "
       "Run `make run` first."),
    code("import duckdb, pandas as pd\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n"
         "con = duckdb.connect('out/heally.duckdb', read_only=True)\nq = lambda s: con.execute(s).fetchdf()\npd.set_option('display.width', 160)"),
    md("## 1. The headline numbers\nHRRP covers a three-year window, so the business case is annualized. Cost per readmission and the avertable share are **assumptions** set in `dbt_project.yml`."),
    code("q('select * from marts.mart_business_case').T"),
    md("## 2. How concentrated is the problem?\nIf outreach followed the ranking, how much of the excess is covered by the first N hospital-condition pairs?"),
    code("w = q('select outreach_rank, cumulative_share from marts.mart_navigator_worklist order by 1')\n"
         "fig, ax = plt.subplots(figsize=(6, 3.4))\nax.plot(w.outreach_rank / len(w) * 100, w.cumulative_share * 100)\n"
         "ax.axhline(50, ls='--', c='grey'); ax.set_xlabel('% of hospital-condition pairs worked (largest first)'); ax.set_ylabel('% of excess readmissions covered')\n"
         "ax.set_title('Half of the excess sits in about 11% of pairs'); plt.tight_layout(); plt.savefig('docs/img/concentration.png', dpi=160); plt.show()"),
    md("## 3. Which conditions drive it?"),
    code("q(\"\"\"select condition_label, count(*) pairs, round(sum(excess_readmissions)) excess, round(1000*sum(excess_readmissions)/sum(discharges),1) per_1000_discharges\n"
         "from marts.mart_navigator_worklist group by 1 order by excess desc\"\"\")"),
    md("## 4. Does the CMS star rating line up with readmission performance?\nA useful sanity check on the data: worse-rated hospitals should readmit more than expected."),
    code("s = q('select overall_star_rating, count(*) hospitals, round(avg(avg_excess_readmission_ratio),4) avg_ratio, round(sum(excess_readmissions)) excess from marts.mart_hospital_scorecard group by 1 order by 1')\ns"),
    code("t = s.dropna(); fig, ax = plt.subplots(figsize=(5, 3)); ax.bar(t.overall_star_rating.astype(int).astype(str), t.avg_ratio - 1)\n"
         "ax.axhline(0, c='k', lw=.6); ax.set_xlabel('CMS overall star rating'); ax.set_ylabel('avg excess ratio minus 1'); plt.tight_layout(); plt.savefig('docs/img/stars.png', dpi=160); plt.show()"),
    md("## 5. Where are partners most exposed? (state view for health plan and employer reporting)"),
    code("q('select state, hospitals, excess_readmissions, excess_readmissions_per_1000_discharges per_1000, share_pairs_above_expected from marts.mart_state_exposure order by excess_readmissions desc limit 10')"),
    md("## 6. What the data cannot tell us\n- HRRP covers **Medicare fee-for-service** patients, mostly 65 and over, not every Wellthy member.\n"
       "- Excess readmissions are **estimated** from published rates: discharges x (predicted - expected) / 100. CMS suppresses small cells, so only 8,037 of 18,330 hospital-condition rows are computable.\n"
       "- 20 hospitals appear in HRRP but not in Hospital General Information (kept and flagged, see INC-3)."),
    code("q('''select count(*) filter (where excess_readmissions is not null) computable, count(*) total, count(*) filter (where not exists (select 1 from marts.dim_hospital d where d.facility_id=f.facility_id and d.in_general_info)) from_unknown_hospitals\nfrom marts.fct_hospital_readmissions f''')"),
]
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
os.chdir(ROOT)
NotebookClient(nb, timeout=120, kernel_name="python3", resources={"metadata": {"path": ROOT}}).execute()
nbf.write(nb, os.path.join(ROOT, "notebooks", "explore_readmissions.ipynb"))
print("notebook executed")
