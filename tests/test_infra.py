"""Infrastructure files that cannot run here (no Snowflake account): pin their structure to the code."""
import os
import re

from heally import config
from heally.sync import norm

ROOT = os.path.dirname(os.path.dirname(__file__))
read = lambda *p: open(os.path.join(ROOT, *p)).read()


def test_snowflake_raw_tables_match_the_source_registry():
    sql = read("snowflake", "01_raw_ddl.sql")
    for source, spec in config.SOURCES.items():
        block = re.search(rf"HEALLY\.RAW\.{source.upper()} \((.*?)\n\);", sql, re.S).group(1)
        cols = re.findall(r"^\s+(\w+) ", block, re.M)
        assert cols[: len(spec["columns"])] == [norm(c).upper() for c in spec["columns"]]
        assert {"_SOURCE_FILE", "_FILE_SHA256", "_ROW_HASH", "_SYNCED_AT"} <= set(cols)


def test_snowpipe_aborts_on_error_and_uses_auto_ingest():
    sql = read("snowflake", "02_stage_and_pipe.sql")
    assert "AUTO_INGEST=TRUE" in sql and "ON_ERROR=ABORT_STATEMENT" in sql


def test_dbt_profile_has_a_snowflake_target_that_reads_secrets_from_the_environment():
    p = read("dbt_heally", "profiles.yml")
    assert "type: snowflake" in p
    assert "password: \"{{ env_var('SNOWFLAKE_PASSWORD'" in p


def test_ci_runs_tests_and_the_pipeline():
    ci = read(".github", "workflows", "ci.yml")
    assert "pytest" in ci and "heally.pipeline" in ci
