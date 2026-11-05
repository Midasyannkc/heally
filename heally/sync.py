"""Fivetran-style ELT loader: land source files as text with lineage, idempotently, and refuse silent schema drift."""
import csv
import hashlib
import json
import os
import re
from datetime import datetime, timezone

import duckdb

from heally.config import SOURCES


class SchemaDrift(Exception):
    pass


def norm(col):
    return re.sub(r"[^0-9a-z]+", "_", col.strip().lower()).strip("_")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _header(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return next(csv.reader(f))


def _log(con, source, path, sha, status, rows=0, details=None, started=None):
    con.execute(
        "insert into raw._sync_log values ((select coalesce(max(sync_id),0)+1 from raw._sync_log), ?,?,?,?,?,?,?,?)",
        [source, os.path.basename(path), sha, status, rows, json.dumps(details or {}), started, datetime.now(timezone.utc)])


def sync(db, source, path, now=None):
    spec = SOURCES[source]
    started = now or datetime.now(timezone.utc)
    sha = _sha256(path)
    con = duckdb.connect(db)
    try:
        con.execute("create schema if not exists raw")
        con.execute("""create table if not exists raw._sync_log (sync_id bigint, source varchar, file_name varchar,
            file_sha256 varchar, status varchar, rows bigint, details varchar, started_at timestamptz, finished_at timestamptz)""")
        last = con.execute("select file_sha256 from raw._sync_log where source=? and status='loaded' order by sync_id desc limit 1", [source]).fetchone()
        if last and last[0] == sha:
            _log(con, source, path, sha, "skipped_unchanged", started=started)
            return {"status": "skipped_unchanged", "rows": 0, "added_columns": []}

        header = _header(path)
        missing = [c for c in spec["columns"] if c not in header]
        added = [c for c in header if c not in spec["columns"]]
        if missing:
            detail = {"missing": missing, "unexpected": added}
            _log(con, source, path, sha, "blocked_schema_drift", details=detail, started=started)
            raise SchemaDrift(f"{source}: expected columns missing {missing}; unexpected columns {added}")

        con.execute("create or replace temp table _incoming as select * from read_csv(?, header=true, all_varchar=true, quote='\"', strict_mode=false)", [path])
        con.execute("create or replace temp table _typed as select " + ", ".join(f'"{c}" as {norm(c)}' for c in header) + " from _incoming")
        cols = [norm(c) for c in header]
        hash_expr = "md5(" + " || '|' || ".join(f"coalesce({c}, '')" for c in cols) + ")"
        exists = con.execute("select count(*) from information_schema.tables where table_schema='raw' and table_name=?", [source]).fetchone()[0]
        con.execute("begin")
        if not exists:
            con.execute(f"create table raw.{source} as select *, null::varchar as _source_file, null::varchar as _file_sha256, null::varchar as _row_hash, null::timestamptz as _synced_at from _typed where false")
        have = {r[0] for r in con.execute("select column_name from information_schema.columns where table_schema='raw' and table_name=?", [source]).fetchall()}
        for c in cols:
            if c not in have:
                con.execute(f'alter table raw.{source} add column "{c}" varchar')
        con.execute(f"delete from raw.{source}")
        con.execute(f"""insert into raw.{source} by name select *, ? as _source_file, ? as _file_sha256, {hash_expr} as _row_hash, ? as _synced_at from _typed""",
                    [os.path.basename(path), sha, started])
        rows = con.execute(f"select count(*) from raw.{source}").fetchone()[0]
        _log(con, source, path, sha, "loaded", rows, {"added_columns": added}, started)
        con.execute("commit")
        return {"status": "loaded", "rows": rows, "added_columns": added}
    finally:
        con.close()
