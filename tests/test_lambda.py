import os

import boto3
import duckdb
from moto import mock_aws

from tests.conftest import HRRP


@mock_aws
def test_s3_upload_event_loads_the_file_and_ignores_other_keys(tmp_path, monkeypatch):
    db = str(tmp_path / "l.duckdb")
    monkeypatch.setenv("HEALLY_DB", db)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="heally-landing")
    key = "cms/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"
    s3.upload_file(HRRP, "heally-landing", key)
    s3.put_object(Bucket="heally-landing", Key="cms/notes.txt", Body=b"x")
    from heally import lambda_handler
    event = {"Records": [{"s3": {"bucket": {"name": "heally-landing"}, "object": {"key": key}}},
                         {"s3": {"bucket": {"name": "heally-landing"}, "object": {"key": "cms/notes.txt"}}}]}
    out = lambda_handler.handler(event, None)
    assert out["loaded"] == 1 and out["ignored"] == 1
    con = duckdb.connect(db, read_only=True)
    assert con.execute("select count(*) from raw.hrrp").fetchone()[0] == 18330
