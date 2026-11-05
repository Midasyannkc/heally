"""AWS Lambda entry point: an S3 upload of a CMS file triggers a sync into the warehouse."""
import os
import tempfile
import urllib.parse

import boto3

from heally import config, sync


def handler(event, context):
    s3 = boto3.client("s3")
    out = {"loaded": 0, "ignored": 0, "skipped": 0, "details": []}
    for rec in event.get("Records", []):
        bucket = rec["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(rec["s3"]["object"]["key"])
        name = os.path.basename(key)
        source = config.source_for_filename(name) if name.lower().endswith(".csv") else None
        if not source:
            out["ignored"] += 1
            continue
        with tempfile.TemporaryDirectory() as d:
            local = os.path.join(d, name)
            s3.download_file(bucket, key, local)
            res = sync.sync(os.environ.get("HEALLY_DB", config.DB), source, local)
        out["skipped" if res["status"] == "skipped_unchanged" else "loaded"] += 1
        out["details"].append({"key": key, **res})
    return out
