"""Metaplane-style data observability: freshness, volume, null rate and schema drift, persisted for trend review."""
import datetime as dt
import json

import duckdb

from heally.config import SOURCES

VOLUME_DROP_LIMIT = 0.20
FRESHNESS_HOURS = 24 * 7


def _status(ok, warn=False):
    return "pass" if ok else ("warn" if warn else "fail")


def run(db, as_of=None):
    as_of = as_of or dt.datetime.now(dt.timezone.utc)
    con = duckdb.connect(db)
    out = []
    try:
        con.execute("create schema if not exists ops")
        con.execute("""create table if not exists ops.monitor_results (checked_at timestamptz, monitor varchar, source varchar,
            status varchar, value double, threshold double, detail varchar)""")
        for source, spec in SOURCES.items():
            if not con.execute("select count(*) from information_schema.tables where table_schema='raw' and table_name=?", [source]).fetchone()[0]:
                continue
            loads = con.execute("select rows, finished_at, status, details from raw._sync_log where source=? and status in ('loaded','blocked_schema_drift') order by sync_id desc", [source]).fetchall()
            loaded = [r for r in loads if r[2] == "loaded"]
            latest = loaded[0]
            # volume
            if len(loaded) > 1 and loaded[1][0]:
                change = (latest[0] - loaded[1][0]) / loaded[1][0]
                out.append(dict(monitor="volume", source=source, status=_status(change > -VOLUME_DROP_LIMIT), value=change, threshold=-VOLUME_DROP_LIMIT,
                                detail=f"{loaded[1][0]} -> {latest[0]} rows"))
            else:
                out.append(dict(monitor="volume", source=source, status="pass", value=0.0, threshold=-VOLUME_DROP_LIMIT, detail="baseline load"))
            # freshness
            age_h = (as_of - latest[1]).total_seconds() / 3600
            out.append(dict(monitor="freshness", source=source, status=_status(age_h <= FRESHNESS_HOURS), value=age_h, threshold=FRESHNESS_HOURS,
                            detail=f"last successful sync {age_h:.1f}h before check"))
            # null rate on keys
            nulls = 0
            for k in spec["key_columns"]:
                nulls += con.execute(f"select count(*) from raw.{source} where {k} is null or trim({k}) = ''").fetchone()[0]
            out.append(dict(monitor="null_rate", source=source, status=_status(nulls == 0), value=float(nulls), threshold=0.0, detail=f"{nulls} null or blank key values"))
            # schema drift
            blocked = [r for r in loads if r[2] == "blocked_schema_drift"]
            newest_blocked = bool(blocked) and (not loaded or loads[0][2] == "blocked_schema_drift")
            out.append(dict(monitor="schema_drift", source=source, status=_status(not newest_blocked), value=float(newest_blocked), threshold=0.0,
                            detail=json.loads(blocked[0][3]) if newest_blocked else "no drift"))
        for r in out:
            con.execute("insert into ops.monitor_results values (?,?,?,?,?,?,?)", [as_of, r["monitor"], r["source"], r["status"], r["value"], r["threshold"], str(r["detail"])])
        return out
    finally:
        con.close()
