"""The interview coverage matrix must point at evidence that exists in the repo."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(__file__))
RESPONSIBILITIES = 9
TOOLS = ["Fivetran", "Snowflake", "dbt", "Hightouch", "Snowplow", "DeepNote", "Metaplane", "Omni"]


def matrix():
    return open(os.path.join(ROOT, "docs", "coverage.md")).read()


def test_every_responsibility_and_tool_is_listed():
    text = matrix()
    assert len(re.findall(r"^\| R\d+ ", text, re.M)) == RESPONSIBILITIES
    for t in TOOLS:
        assert f"| {t} |" in text


def test_every_evidence_path_exists():
    paths = re.findall(r"`([\w./-]+\.\w+|[\w./-]+/)`", matrix())
    assert paths
    missing = [p for p in paths if not os.path.exists(os.path.join(ROOT, p))]
    assert not missing, missing
