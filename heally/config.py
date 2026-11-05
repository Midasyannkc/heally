import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.environ.get("HEALLY_DB", os.path.join(ROOT, "out", "heally.duckdb"))
RAW_DIR = os.path.join(ROOT, "data", "raw")

# Source registry: what each CMS file must look like. A header that drops or renames one of these is schema drift.
SOURCES = {
    "hrrp": {
        "file_pattern": "Hospital_Readmissions_Reduction_Program",
        "dataset": "https://data.cms.gov/provider-data/dataset/9n3s-kdb3",
        "key_columns": ["facility_id", "measure_name"],
        "columns": ["Facility Name", "Facility ID", "State", "Measure Name", "Number of Discharges", "Footnote",
                    "Excess Readmission Ratio", "Predicted Readmission Rate", "Expected Readmission Rate",
                    "Number of Readmissions", "Start Date", "End Date"],
    },
    "hospital_info": {
        "file_pattern": "Hospital_General_Information",
        "dataset": "https://data.cms.gov/provider-data/dataset/xubh-q36u",
        "key_columns": ["facility_id"],
        "columns": [
                    "Facility ID",
                    "Facility Name",
                    "Address",
                    "City/Town",
                    "State",
                    "ZIP Code",
                    "County/Parish",
                    "Telephone Number",
                    "Hospital Type",
                    "Hospital Ownership",
                    "Emergency Services",
                    "Meets criteria for birthing friendly designation",
                    "Hospital overall rating",
                    "Hospital overall rating footnote",
                    "MORT Group Measure Count",
                    "Count of Facility MORT Measures",
                    "Count of MORT Measures Better",
                    "Count of MORT Measures No Different",
                    "Count of MORT Measures Worse",
                    "MORT Group Footnote",
                    "Safety Group Measure Count",
                    "Count of Facility Safety Measures",
                    "Count of Safety Measures Better",
                    "Count of Safety Measures No Different",
                    "Count of Safety Measures Worse",
                    "Safety Group Footnote",
                    "READM Group Measure Count",
                    "Count of Facility READM Measures",
                    "Count of READM Measures Better",
                    "Count of READM Measures No Different",
                    "Count of READM Measures Worse",
                    "READM Group Footnote",
                    "Pt Exp Group Measure Count",
                    "Count of Facility Pt Exp Measures",
                    "Pt Exp Group Footnote",
                    "TE Group Measure Count",
                    "Count of Facility TE Measures",
                    "TE Group Footnote",
                ],
    },
}


def source_for_filename(name):
    for key, s in SOURCES.items():
        if s["file_pattern"].lower() in name.lower():
            return key
    return None
