"""Hightouch-style reverse ETL: push the navigator worklist mart to a CRM-like destination, writing only what changed."""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone

import duckdb

KEY = ("facility_id", "measure_code")
MAX_DROP = 0.5


class UnsafeSync(Exception):
    pass


def _hash(row):
    return hashlib.md5(json.dumps(row, sort_keys=True, default=str).encode()).hexdigest()


def sync(db, dest, force=False):
    con = duckdb.connect(db, read_only=True)
    cur = con.execute("select * from marts.mart_navigator_worklist")
    cols = [d[0] for d in cur.description]
    src = {(r[cols.index(KEY[0])], r[cols.index(KEY[1])]): dict(zip(cols, r)) for r in cur.fetchall()}
    con.close()

    d = sqlite3.connect(dest)
    d.execute("""create table if not exists navigator_worklist (facility_id text, measure_code text, priority_tier text, excess_readmissions real,
        payload text, row_hash text, status text, updated_at text, primary key (facility_id, measure_code))""")
    d.execute("create table if not exists sync_log (id integer primary key autoincrement, ran_at text, inserted int, updated int, retired int, unchanged int, forced int)")
    active = {(a, b): h for a, b, h in d.execute("select facility_id, measure_code, row_hash from navigator_worklist where status='active'")}
    if not force:
        if not src:
            raise UnsafeSync("source worklist is empty; refusing to retire every destination record")
        if active and (len(active) - len(set(src) & set(active))) / len(active) > MAX_DROP:
            raise UnsafeSync(f"{len(active) - len(set(src) & set(active))} of {len(active)} active records would be retired (limit {int(MAX_DROP*100)}%)")
    now = datetime.now(timezone.utc).isoformat()
    ins = upd = unch = 0
    existing = {(a, b): (h, s) for a, b, h, s in d.execute("select facility_id, measure_code, row_hash, status from navigator_worklist")}
    for k, row in src.items():
        h = _hash(row)
        payload = json.dumps(row, default=str)
        if k not in existing:
            d.execute("insert into navigator_worklist values (?,?,?,?,?,?,?,?)", [*k, row.get("priority_tier"), row.get("excess_readmissions"), payload, h, "active", now])
            ins += 1
        elif existing[k][0] != h or existing[k][1] != "active":
            d.execute("update navigator_worklist set priority_tier=?, excess_readmissions=?, payload=?, row_hash=?, status='active', updated_at=? where facility_id=? and measure_code=?",
                      [row.get("priority_tier"), row.get("excess_readmissions"), payload, h, now, *k])
            upd += 1
        else:
            unch += 1
    gone = [k for k in active if k not in src]
    for k in gone:
        d.execute("update navigator_worklist set status='retired', updated_at=? where facility_id=? and measure_code=?", [now, *k])
    d.execute("insert into sync_log (ran_at, inserted, updated, retired, unchanged, forced) values (?,?,?,?,?,?)", [now, ins, upd, len(gone), unch, int(force)])
    d.commit()
    d.close()
    return {"inserted": ins, "updated": upd, "retired": len(gone), "unchanged": unch}
