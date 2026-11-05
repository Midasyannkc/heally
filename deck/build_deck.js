// Builds Heally_executive_summary.pptx. Numbers come from data.json, which is exported from the marts.
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/db7351a8-743d-4fd7-a5a7-7f44d2c57f1c_7caad5f8-69d6-478c-8504-8409ab7234b2/pptx/scripts/apply_theme.js");
const D = require("./data.json");

const THEME = {
  name: "Heally", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "1D2A26", lt1: "F6F7F4", dk2: "0F3D3E", lt2: "E3ECE8", accent1: "1F7A5C", accent2: "D98E04", accent3: "2E6F95",
            accent4: "B3402A", accent5: "8A9A94", accent6: "4FC79D", hlink: "1F7A5C", folHlink: "5D6B66" },
};
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Heally: where should care navigators start after a hospital stay?";
pres.author = "Christian Kouadio Kouassi";
const C = pres.SchemeColor;
const k = D.kpi;
const fmt = (n, d = 0) => Number(n).toLocaleString("en-US", { maximumFractionDigits: d });

pres.defineSlideMaster({
  title: "TITLE", background: { color: "0F3D3E" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.25, w: 5.6, h: 1.0, fontSize: 48, bold: true, color: C.background1, fontFace: "Cambria", margin: 0, valign: "top", align: "left" }, text: "" } }],
});
pres.defineSlideMaster({
  title: "CONTENT", background: { color: "F6F7F4" },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.28, w: 9, h: 0.75, fontSize: 24, bold: true, color: C.text2, fontFace: "Cambria", margin: 0, valign: "top", align: "left" }, text: "" } },
    { text: { text: "Heally  |  CMS readmission analytics engineering", options: { x: 0.5, y: 5.2, w: 6, h: 0.25, fontSize: 10, color: C.accent5, margin: 0 } } },
  ],
  slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.25, fontSize: 10, color: C.accent5, align: "right" },
});

const card = (s, x, y, w, h, name) => s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: "DFE4DE", width: 0.75 }, objectName: name });
const T = (s, text, o) => s.addText(text, { isTextBox: true, margin: 0, ...o });
const link = (text, url, o = {}) => ({ text, options: { hyperlink: { url, tooltip: url }, color: "1F7A5C", underline: { style: "sng" }, ...o } });

// ---------- 1. Title ----------
pres.addSection({ title: "Intro" });
let s = pres.addSlide({ masterName: "TITLE", sectionTitle: "Intro" });
s.addText("Heally", { placeholder: "title" });
T(s, "Where should care navigators start after a hospital stay?", { x: 0.6, y: 2.2, w: 5.4, h: 0.9, fontSize: 22, color: C.background2, fontFace: "Cambria", valign: "top", objectName: "Subtitle" });
T(s, "Analytics engineering on real CMS hospital readmission data: tested ELT, dbt models, governed metrics, a self-service dashboard and a CRM worklist.", { x: 0.6, y: 3.2, w: 5.4, h: 0.8, fontSize: 13, color: C.background2, valign: "top", objectName: "Tagline" });
T(s, [link("CMS data: HRRP 9n3s-kdb3", "https://data.cms.gov/provider-data/dataset/9n3s-kdb3", { color: "4FC79D", breakLine: true, fontSize: 12 }),
      link("CMS data: Hospital General Information xubh-q36u", "https://data.cms.gov/provider-data/dataset/xubh-q36u", { color: "4FC79D", breakLine: true, fontSize: 12 }),
      link("Code: github.com/Midasyannkc/heally", "https://github.com/Midasyannkc/heally", { color: "4FC79D", fontSize: 12 })],
  { x: 0.6, y: 4.1, w: 5.6, h: 0.8, valign: "top", objectName: "Links" });
T(s, "Christian Kouadio Kouassi", { x: 0.6, y: 5.0, w: 5, h: 0.3, fontSize: 12, bold: true, color: C.background1, objectName: "Author" });
// visual motif: the worklist tiers
[["A", "457 pairs, half of the excess", "4FC79D", 3.2], ["B", "935 pairs", "D98E04", 2.4], ["C", "2,924 pairs", "8A9A94", 1.6]].forEach(([t, lab, col, w], i) => {
  s.addShape(pres.ShapeType.roundRect, { x: 6.5, y: 1.35 + i * 1.15, w, h: 0.95, rectRadius: 0.1, fill: { color: col }, line: { color: col }, objectName: `Tier ${t}` });
  T(s, "Tier " + t, { x: 6.7, y: 1.45 + i * 1.15, w: w - 0.3, h: 0.35, fontSize: 16, bold: true, color: "0F3D3E", fontFace: "Cambria" });
  T(s, lab, { x: 6.7, y: 1.82 + i * 1.15, w: w - 0.3, h: 0.35, fontSize: 11, color: "0F3D3E" });
});
s.addNotes("Heally is a portfolio project built for an Analytics Engineer role at a care navigation company. Real CMS data, a tested pipeline end to end, and five documented incidents. The tier bars on the right are the output: a ranked worklist for care navigators.");

// ---------- 2. Executive summary ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Intro" });
s.addText("Half of the excess readmissions sit in about 11% of hospital-condition pairs", { placeholder: "title" });
const blocks = [["The problem", "Care navigators have limited hours. A hospital stay is the costliest moment in a family's care journey, and Medicare penalizes hospitals that readmit patients more often than expected."],
  ["What was built", "A tested ELT pipeline on two real CMS datasets: load, dbt models, governed metrics, observability monitors, a dashboard and a reverse ETL worklist. It fails closed, and five incidents are fixed in the git history."],
  ["What it shows", `Working the largest pairs first, ${fmt(k.tier_a_pairs)} of ${fmt(k.worklist_pairs)} pairs reach half of the estimated excess readmissions. Savings are scenarios with visible assumptions, not findings.`]];
blocks.forEach(([h, b], i) => {
  T(s, h, { x: 0.5, y: 1.25 + i * 1.28, w: 5.2, h: 0.3, fontSize: 14, bold: true, color: C.accent1, fontFace: "Cambria", objectName: `Heading ${i + 1}` });
  T(s, b, { x: 0.5, y: 1.56 + i * 1.28, w: 5.2, h: 0.9, fontSize: 13, color: C.text1, valign: "top", objectName: `Body ${i + 1}` });
});
[[fmt(k.tier_a_pairs), `tier A pairs, ${fmt(k.tier_a_share_of_pairs * 100, 1)}% of the worklist, hold ${fmt(k.tier_a_share_of_excess * 100)}% of the excess`],
 [`${fmt(k.tier_a_excess_per_1000_discharges)} vs ${fmt(k.all_pairs_excess_per_1000_discharges)}`, "excess readmissions per 1,000 discharges, tier A against all pairs"],
 ["5", "pipeline incidents, each with a failing test and then a fix"]].forEach(([v, l], i) => {
  card(s, 6.1, 1.25 + i * 1.25, 3.4, 1.1, `Stat card ${i + 1}`);
  T(s, v, { x: 6.3, y: 1.32 + i * 1.25, w: 3.0, h: 0.5, fontSize: 28, bold: true, color: C.accent1, fontFace: "Cambria", objectName: `Stat ${i + 1}` });
  T(s, l, { x: 6.3, y: 1.82 + i * 1.25, w: 3.0, h: 0.5, fontSize: 11, color: C.text1, valign: "top", objectName: `Stat label ${i + 1}` });
});
s.addNotes("Lead with the finding, then how it was built. Be explicit that the savings are scenarios: the cost per readmission and the share navigators can avert are assumptions, shown as a grid in the repo.");

// ---------- 3. Data source ----------
pres.addSection({ title: "Project" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Project" });
s.addText("Real data: two CMS Provider Data files", { placeholder: "title" });
const ds = [["Hospital Readmissions Reduction Program, FY 2026", "https://data.cms.gov/provider-data/dataset/9n3s-kdb3", "data.cms.gov/provider-data/dataset/9n3s-kdb3", "18,330 rows: 3,055 hospitals x 6 conditions", "Excess readmission ratio, predicted and expected rates, discharges. Discharges Jul 2021 to Jun 2024."],
  ["Hospital General Information", "https://data.cms.gov/provider-data/dataset/xubh-q36u", "data.cms.gov/provider-data/dataset/xubh-q36u", "5,419 hospitals", "Type, ownership, county, CMS overall star rating, emergency services."]];
ds.forEach(([name, url, shown, rows, what], i) => {
  const x = 0.5 + i * 4.6;
  card(s, x, 1.2, 4.4, 2.35, `Dataset card ${i + 1}`);
  T(s, name, { x: x + 0.2, y: 1.3, w: 4.0, h: 0.55, fontSize: 15, bold: true, color: C.text2, fontFace: "Cambria", valign: "top" });
  T(s, [link(shown, url, { fontSize: 12 })], { x: x + 0.2, y: 1.88, w: 4.0, h: 0.3 });
  T(s, rows, { x: x + 0.2, y: 2.25, w: 4.0, h: 0.3, fontSize: 13, bold: true, color: C.accent1 });
  T(s, what, { x: x + 0.2, y: 2.6, w: 4.0, h: 0.85, fontSize: 12, color: C.text1, valign: "top" });
});
T(s, "How the files were obtained", { x: 0.5, y: 3.75, w: 4.4, h: 0.3, fontSize: 13, bold: true, color: C.accent1, fontFace: "Cambria" });
T(s, "The CMS site was not reachable from the build environment, so the CSVs came from a public GitHub repository that publishes them unchanged. Row counts and the star-rating pattern match that analysis. Not compared with CMS directly.", { x: 0.5, y: 4.05, w: 4.4, h: 1.0, fontSize: 11, color: C.text1, valign: "top" });
T(s, "Limits of the data", { x: 5.1, y: 3.75, w: 4.4, h: 0.3, fontSize: 13, bold: true, color: C.accent1, fontFace: "Cambria" });
T(s, "Medicare fee-for-service patients only. CMS replaces small cells with text, so 8,037 of 18,330 rows allow an excess readmission estimate. 20 hospitals appear in one file and not the other.", { x: 5.1, y: 4.05, w: 4.4, h: 1.0, fontSize: 11, color: C.text1, valign: "top" });
s.addNotes("Both links go to the CMS Provider Data Catalog. The files and the processed marts (CSV and parquet) are in the repository. Be upfront about how the files were obtained.");

// ---------- 4. Pipeline ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Project" });
s.addText("The project: ELT pipeline end to end, and where each incident hit", { placeholder: "title" });
const st = [["CMS files", "CSV from the two datasets", "Source", []],
  ["Load", "Idempotent, text-typed, lineage columns, schema drift blocked", "Fivetran pattern", ["INC-1"]],
  ["Staging", "Typed, suppression text becomes null", "dbt", ["INC-2"]],
  ["Marts", "Dimensions, fact, worklist, state exposure, business case", "dbt", ["INC-3", "INC-4"]],
  ["Gates", "30 data tests, 3 unit tests, 4 monitors", "dbt + Metaplane pattern", []],
  ["Outputs", "CRM worklist, dashboard, governed metrics", "Hightouch + Omni pattern", ["INC-5"]]];
st.forEach(([h, d, tool, incs], i) => {
  const x = 0.35 + i * 1.57;
  s.addShape(pres.ShapeType.roundRect, { x, y: 1.25, w: 1.4, h: 1.75, rectRadius: 0.08, fill: { color: i === 0 ? "E3ECE8" : "FFFFFF" }, line: { color: "1F7A5C", width: 1.25 }, objectName: `Stage ${i + 1}` });
  T(s, h, { x: x + 0.08, y: 1.32, w: 1.24, h: 0.3, fontSize: 13, bold: true, color: C.text2, fontFace: "Cambria", align: "center" });
  T(s, d, { x: x + 0.08, y: 1.65, w: 1.24, h: 0.85, fontSize: 10.5, color: C.text1, align: "center", valign: "top" });
  T(s, tool, { x: x + 0.08, y: 2.55, w: 1.24, h: 0.4, fontSize: 10, italic: true, color: C.accent1, align: "center", valign: "top" });
  if (i < st.length - 1) s.addShape(pres.ShapeType.line, { x: x + 1.4, y: 2.12, w: 0.17, h: 0, line: { color: "1F7A5C", width: 1.75, endArrowType: "triangle" }, objectName: `Arrow ${i + 1}` });
  incs.forEach((n, j) => {
    s.addShape(pres.ShapeType.roundRect, { x: x + 0.12, y: 3.12 + j * 0.34, w: 1.16, h: 0.28, rectRadius: 0.06, fill: { color: "B3402A" }, line: { color: "B3402A" }, objectName: `Chip ${n}` });
    T(s, n, { x: x + 0.12, y: 3.12 + j * 0.34, w: 1.16, h: 0.28, fontSize: 10.5, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  });
});
[["Fails closed", "A failed step stops everything after it. Bad data never reaches the CRM."], ["Idempotent", "Second run: 0 rows loaded, 0 inserted, 0 updated, 4,316 unchanged."], ["Automated", "One command, CI on every push, S3 upload triggers the same load through a Lambda."]].forEach(([h, b], i) => {
  const x = 0.5 + i * 3.05;
  T(s, h, { x, y: 4.1, w: 2.85, h: 0.3, fontSize: 13, bold: true, color: C.accent1, fontFace: "Cambria" });
  T(s, b, { x, y: 4.4, w: 2.85, h: 0.75, fontSize: 11, color: C.text1, valign: "top" });
});
s.addNotes("Walk left to right. The red chips show where each incident hit the pipeline. Fivetran, Hightouch, Metaplane and Omni are represented by the patterns built in code, not by the products.");

// ---------- 5. What it demonstrates ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Project" });
s.addText("What this project demonstrates, mapped to the role", { placeholder: "title" });
const tiles = [["dbt and self-service", "Layered models, governed metrics, filterable dashboard"], ["Engineering practices", "TDD, CI, one-command fail-closed pipeline"], ["Requirements", "Stakeholder question to model, metric and test"],
  ["Quality and governance", "Contracts, reconciliations, docs site, roles"], ["Tests", "30 data, 3 unit, 37 pytest; 5 singular reconciliations"], ["Tool evaluation", "Warehouse, metrics layer, observability: build or buy"],
  ["Documentation", "README, ADRs, runbook, data dictionary in dbt docs"], ["Troubleshooting", "5 incidents, runbook with escalation triggers"], ["Working with seniors", "Open design questions listed for review"]];
tiles.forEach(([h, b], i) => {
  const x = 0.5 + (i % 3) * 3.05, y = 1.2 + Math.floor(i / 3) * 1.3;
  card(s, x, y, 2.9, 1.15, `Tile ${i + 1}`);
  s.addShape(pres.ShapeType.ellipse, { x: x + 0.15, y: y + 0.15, w: 0.34, h: 0.34, fill: { color: "1F7A5C" }, line: { color: "1F7A5C" }, objectName: `Tile marker ${i + 1}` });
  T(s, String(i + 1), { x: x + 0.15, y: y + 0.15, w: 0.34, h: 0.34, fontSize: 11, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  T(s, h, { x: x + 0.6, y: y + 0.12, w: 2.2, h: 0.4, fontSize: 13, bold: true, color: C.text2, fontFace: "Cambria", valign: "middle" });
  T(s, b, { x: x + 0.15, y: y + 0.6, w: 2.65, h: 0.5, fontSize: 11, color: C.text1, valign: "top" });
});
T(s, "Stack tools Fivetran, Hightouch, Metaplane, Omni and DeepNote appear as built patterns, not products. Snowplow is not covered. Snowflake is written, not run.", { x: 0.5, y: 5.0, w: 8.9, h: 0.22, fontSize: 10, italic: true, color: C.accent4 });
s.addNotes("Each tile maps to one responsibility in the job posting. The repo has docs/coverage.md with a path to evidence for every row, checked by a test.");

// ---------- 6. Incidents ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Project" });
s.addText("Pipeline-breaking events and the commits that fixed them", { placeholder: "title" });
const kind = { 1: ["Real data", "1F7A5C"], 2: ["Real data", "1F7A5C"], 3: ["Real data", "1F7A5C"], 4: ["Simulated refresh", "D98E04"], 5: ["Latent, found in review", "D98E04"] };
const short = { 1: "Loader registry described 14 of 38 hospital columns; every first load reported 24 phantom added columns",
  2: "CMS puts N/A, Too Few to Report and Not Available inside numeric columns; typed staging crashed",
  3: "20 hospitals in HRRP missing from General Information; the fact join silently dropped their rows",
  4: "A new CMS condition code vanished from the worklist through an inner join to the label seed",
  5: "Governed metric ignored the 25-discharge rule the marts use, so self-service and dashboard disagreed" };
const hdr = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: "0F3D3E" }, fontSize: 11, fontFace: "Calibri" } });
const rows = [[hdr("#"), hdr("What broke"), hdr("Origin"), hdr("Reproduce, then fix")]];
D.inc.forEach((r, i) => {
  const n = i + 1, h1 = r[3].replace(/`/g, ""), h2 = r[4].replace(/`/g, "");
  rows.push([{ text: r[0], options: { bold: true, fontSize: 11 } }, { text: short[n], options: { fontSize: 10.5 } },
    { text: kind[n][0], options: { fontSize: 10.5, bold: true, color: kind[n][1] } }, { text: `${h1}  >  ${h2}`, options: { fontSize: 10.5, fontFace: "Courier New" } }]);
});
s.addTable(rows, { x: 0.5, y: 1.15, w: 9.0, colW: [0.65, 4.2, 1.55, 2.6], border: { type: "solid", pt: 0.5, color: "DFE4DE" }, fill: { color: "FFFFFF" }, color: "1D2A26", valign: "middle", margin: [0.05, 0.08, 0.05, 0.08], rowH: [0.32, 0.62, 0.62, 0.62, 0.62, 0.62], autoPage: false });
T(s, "Each incident has a reproduce commit holding a failing test, then a fix commit that makes it pass. scripts/verify_incidents.py replays every pair in a clean checkout.", { x: 0.5, y: 4.85, w: 9.0, h: 0.35, fontSize: 11, color: C.text1, valign: "top" });
s.addNotes("Say which incidents happened on the real data (1 to 3) and which are a simulated refresh or a latent mismatch found in review (4 and 5). Honesty here is a strength. The incident replay script checks out each commit pair and confirms the reproduce commit fails and the fix commit passes.");

// ---------- 7. Trust ----------
pres.addSection({ title: "Wrap-up" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Wrap-up" });
s.addText("Trust: tests, monitors and governance", { placeholder: "title" });
[["30", "dbt data tests"], ["3", "dbt unit tests"], ["37", "pytest tests"], ["4", "monitors, results stored"]].forEach(([v, l], i) => {
  const x = 0.5 + i * 2.27;
  card(s, x, 1.15, 2.1, 1.1, `Count card ${i + 1}`);
  T(s, v, { x: x + 0.15, y: 1.2, w: 1.8, h: 0.6, fontSize: 32, bold: true, color: C.accent1, fontFace: "Cambria" });
  T(s, l, { x: x + 0.15, y: 1.8, w: 1.8, h: 0.35, fontSize: 12, color: C.text1 });
});
const col = [["Data quality in the pipeline", ["Source contract: a renamed column blocks the load and is logged", "Reconciliations: worklist, state mart and metric each tie to the fact table", "Monitors: volume, freshness, null rate, schema drift", "Reverse ETL refuses to wipe the destination"]],
  ["Governance and access", ["Every model described; dashboard declared as a dbt exposure", "Static dbt docs site with lineage", "Assumptions are variables, shown as a sensitivity grid", "Snowflake roles written: transformer writes, analyst reads marts"]]];
col.forEach(([h, items], i) => {
  const x = 0.5 + i * 4.6;
  T(s, h, { x, y: 2.5, w: 4.4, h: 0.3, fontSize: 14, bold: true, color: C.accent1, fontFace: "Cambria" });
  T(s, items.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < items.length - 1, paraSpaceAfter: 6 } })), { x, y: 2.85, w: 4.4, h: 2.2, fontSize: 12, color: C.text1, valign: "top" });
});
s.addNotes("The posting asks for well-tested code and data quality. The point of this slide is that tests, monitors and reconciliations are layered, and each layer has caught something or has a test that would.");

// ---------- 8. Assumptions and limits ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Wrap-up" });
s.addText("Assumptions and limits, stated up front", { placeholder: "title" });
card(s, 0.5, 1.2, 4.4, 3.4, "Assumptions card"); card(s, 5.1, 1.2, 4.4, 3.4, "Limits card");
T(s, "Assumptions (not CMS data)", { x: 0.7, y: 1.3, w: 4.0, h: 0.3, fontSize: 14, bold: true, color: C.accent2, fontFace: "Cambria" });
T(s, [["Cost per readmission: $15,000", "grid of $10,000 to $20,000"], ["Share navigators avert: 10%", "grid of 5% to 20%"], ["Reportable volume: 25 discharges or more", "dbt variable"], ["Tier A: pairs reaching 50% of the excess", "tier B at 80%"], ["Annualized: window divided by 3 years", "no seasonality"]]
  .flatMap(([a, b], j, arr) => [{ text: a, options: { bold: true, breakLine: true } }, { text: b, options: { color: "5D6B66", breakLine: j < arr.length - 1, paraSpaceAfter: 6 } }]),
  { x: 0.7, y: 1.7, w: 4.0, h: 3.1, fontSize: 12, color: C.text1, valign: "top" });
T(s, "Limits", { x: 5.3, y: 1.3, w: 4.0, h: 0.3, fontSize: 14, bold: true, color: C.accent4, fontFace: "Cambria" });
T(s, ["Savings are scenarios, not findings", "Medicare fee-for-service patients only, not every care program member", "Excess readmissions estimated from published rates; 8,037 of 18,330 rows computable", "DuckDB runs everything; Snowflake, Snowpipe and Lambda deployment are written, not run", "Vendor tools are patterns, not products; Snowplow not covered", "Metric CLI could not load the manifest; metrics tested against marts instead"]
  .map((t, j, a) => ({ text: t, options: { bullet: true, breakLine: j < a.length - 1, paraSpaceAfter: 5 } })), { x: 5.3, y: 1.7, w: 4.0, h: 3.1, fontSize: 12, color: C.text1, valign: "top" });
s.addNotes("Offer the limits before the interviewer finds them. Each one has a next step in docs/design_review.md.");

// ---------- 9. Conclusion ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Wrap-up" });
s.addText("Result: 457 pairs cover half of the excess", { placeholder: "title" });
[[fmt(k.tier_a_pairs), `pairs in tier A, ${fmt(k.tier_a_share_of_pairs * 100, 1)}% of ${fmt(k.worklist_pairs)}`], [`${fmt(k.tier_a_share_of_excess * 100)}%`, "of estimated excess readmissions covered"], [`${fmt(k.tier_a_excess_per_1000_discharges)} vs ${fmt(k.all_pairs_excess_per_1000_discharges)}`, "excess per 1,000 discharges, tier A vs all"], [`$${fmt(k.savings_usd_per_year_tier_a / 1e6, 1)}M`, "per year, scenario: 10% averted at $15,000 each"]].forEach(([v, l], i) => {
  const x = 0.5 + i * 2.27;
  card(s, x, 1.1, 2.1, 1.15, `KPI card ${i + 1}`);
  T(s, v, { x: x + 0.12, y: 1.15, w: 1.9, h: 0.55, fontSize: 24, bold: true, color: i === 3 ? "D98E04" : "1F7A5C", fontFace: "Cambria" });
  T(s, l, { x: x + 0.12, y: 1.7, w: 1.9, h: 0.5, fontSize: 10.5, color: "1D2A26", valign: "top" });
});
const axisCommon = { catAxisLabelColor: "5D6B66", valAxisLabelColor: "5D6B66", catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", catAxisLabelFontSize: 10, valAxisLabelFontSize: 10, valGridLine: { color: "DFE4DE", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false, titleFontFace: "+mj-lt", titleColor: "0F3D3E", titleFontSize: 12, showTitle: true };
s.addChart(pres.charts.LINE, [{ name: "Share of excess covered", labels: D.curve.map((p) => p[0] + "%"), values: D.curve.map((p) => p[1]) }],
  { x: 0.5, y: 2.4, w: 4.5, h: 2.7, ...axisCommon, title: "Share of excess readmissions covered by share of pairs worked", chartColors: ["1F7A5C"], lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 6, valAxisMaxVal: 100, valAxisMinVal: 0, showValue: false, objectName: "Concentration chart" });
s.addChart(pres.charts.BAR, [{ name: "Excess readmissions", labels: D.states.map((r) => r[0]), values: D.states.map((r) => Math.round(r[1])) }],
  { x: 5.1, y: 2.4, w: 4.4, h: 2.7, ...axisCommon, barDir: "bar", title: "Top 8 states by excess readmissions (3-year window)", chartColors: ["1F7A5C"], catAxisOrientation: "maxMin", showValue: true, dataLabelFontSize: 10, dataLabelColor: "1D2A26", dataLabelPosition: "outEnd", barGapWidthPct: 40, valAxisHidden: true, valGridLine: { style: "none" }, objectName: "State chart" });
s.addNotes("Conclusion. Tier A is the first thing a navigator team would work. The dollar figure is a scenario using stated assumptions. Next steps: run the Snowflake target in a staging account, add event data to measure dashboard adoption, and agree the excess readmission definition with the clinical team.");

pres.writeFile({ fileName: "Heally_executive_summary.pptx" }).then(() => applyTheme("Heally_executive_summary.pptx", THEME)).then(() => console.log("deck written"));
