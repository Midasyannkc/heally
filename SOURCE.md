# Data source

Two real datasets from the CMS Provider Data Catalog (Centers for Medicare and Medicaid Services), the data Wellthy's health plan and employer partners care about: what happens to patients after a hospital stay.

| Dataset | CMS page (click) | File in this repo | Rows |
| --- | --- | --- | --- |
| Hospital Readmissions Reduction Program, FY 2026 | https://data.cms.gov/provider-data/dataset/9n3s-kdb3 | `data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv` | 18,330 (3,055 hospitals x 6 conditions) |
| Hospital General Information | https://data.cms.gov/provider-data/dataset/xubh-q36u | `data/raw/Hospital_General_Information.csv` | 5,419 hospitals |

Performance period of the HRRP file: discharges 07/01/2021 to 06/30/2024. Conditions: heart attack, heart failure, pneumonia, COPD, coronary artery bypass graft surgery, hip or knee replacement.

Processed data, ready to open: `data/marts/*.csv` and `data/marts/*.parquet` (the dbt marts).

## How the files were obtained (read this)

The CMS website was not reachable from the environment where this project was built. The two CSV files were downloaded from a public GitHub repository that publishes them unchanged next to its own analysis: https://github.com/Kaveenk/hospital-readmissions-analysis (folder `data/`). They match that repository's published row counts (18,330 and 5,419), and average excess ratio by star rating computed here (1.045, 1.023, 1.006, 0.986, 0.964) matches the figures that repository publishes. They could not be compared with CMS directly.

To refresh from CMS, which also changes the rows because CMS updates these datasets, download from the two CMS pages above (use "Download full dataset (CSV)") into `data/raw/` and run `make run`. A renamed column will be stopped by the schema drift check.

Both datasets are published by a U.S. federal agency. Check CMS terms before redistributing outside a portfolio.

## Limits of the data

- HRRP covers Medicare fee-for-service patients, mostly age 65 and over.
- CMS suppresses small cells with text (N/A, Too Few to Report). Only 8,037 of 18,330 rows allow an excess readmission estimate.
- 20 hospitals in HRRP are absent from General Information (INC-3).
