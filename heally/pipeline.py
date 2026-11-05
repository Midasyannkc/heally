"""End to end ELT run, fail closed: sync, dbt build (tests included), observability monitors, then reverse ETL.
Nothing downstream of a failed step runs, so bad data never reaches the CRM."""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

from heally import config, monitors, reverse_etl, sync


class PipelineFailed(Exception):
    pass


def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=config.ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _dbt(db, *args):
    env = {**os.environ, "HEALLY_DB": db, "DBT_SEND_ANONYMOUS_USAGE_STATS": "False"}
    project = os.path.join(config.ROOT, "dbt_heally")
    return subprocess.run([sys.executable, "-m", "dbt.cli.main", *args, "--project-dir", project, "--profiles-dir", project],
                          cwd=config.ROOT, env=env, capture_output=True, text=True)


def _dbt_counts(out):
    m = re.search(r"PASS=(\d+) WARN=(\d+) ERROR=(\d+) SKIP=(\d+)", out)
    return {"passed": int(m[1]), "warned": int(m[2]), "errors": int(m[3]), "skipped": int(m[4])} if m else {"passed": 0, "warned": 0, "errors": 1, "skipped": 0}


def run(db=None, raw_dir=None, crm_path=None, manifest_path=None):
    db = db or config.DB
    raw_dir = raw_dir or config.RAW_DIR
    crm_path = crm_path or os.path.join(config.ROOT, "out", "crm.sqlite")
    manifest_path = manifest_path or os.path.join(config.ROOT, "out", "run_manifest.json")
    os.makedirs(os.path.dirname(db), exist_ok=True)
    manifest = {"generated_at": datetime.now(timezone.utc).isoformat(), "git_sha": _git_sha(),
                "sources": {k: v["dataset"] for k, v in config.SOURCES.items()}, "steps": [], "passed": False, "failed_step": None}

    def finish(step, t0, detail, ok=True):
        manifest["steps"].append({"step": step, "seconds": round(time.time() - t0, 2), "ok": ok, "detail": detail})

    def fail(step, message):
        manifest["failed_step"] = step
        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
        json.dump(manifest, open(manifest_path, "w"), indent=1, default=str)
        raise PipelineFailed(message)

    # 1. sync
    t0, detail = time.time(), {}
    for name in sorted(os.listdir(raw_dir)):
        source = config.source_for_filename(name)
        if not source or not name.lower().endswith(".csv"):
            continue
        try:
            detail[source] = sync.sync(db, source, os.path.join(raw_dir, name))["status"]
        except sync.SchemaDrift as e:
            finish("sync", t0, {**detail, "error": str(e)}, ok=False)
            fail("sync", f"schema drift blocked the load: {e}")
    finish("sync", t0, detail)

    # 2. dbt seed + build (models, tests, unit tests)
    t0 = time.time()
    seed = _dbt(db, "seed")
    build = _dbt(db, "build")
    counts = _dbt_counts(build.stdout)
    manifest["dbt"] = counts
    ok = seed.returncode == 0 and build.returncode == 0 and counts["errors"] == 0
    finish("dbt_build", t0, counts, ok)
    if not ok:
        fail("dbt_build", "dbt build failed:\n" + build.stdout[-1500:])

    # 3. observability monitors
    t0 = time.time()
    results = monitors.run(db)
    bad = [r for r in results if r["status"] == "fail"]
    finish("monitors", t0, {"checks": len(results), "failed": [f"{r['monitor']}:{r['source']}" for r in bad]}, not bad)
    if bad:
        fail("monitors", f"monitors failed: {[(r['monitor'], r['source'], r['detail']) for r in bad]}")

    # 4. reverse ETL
    t0 = time.time()
    try:
        rev = reverse_etl.sync(db, crm_path)
    except reverse_etl.UnsafeSync as e:
        finish("reverse_etl", t0, {"error": str(e)}, False)
        fail("reverse_etl", f"reverse ETL refused: {e}")
    finish("reverse_etl", t0, rev)

    import duckdb
    con = duckdb.connect(db, read_only=True)
    manifest["rows"] = {s: con.execute(f"select count(*) from raw.{s}").fetchone()[0] for s in config.SOURCES}
    con.close()
    manifest["passed"] = True
    json.dump(manifest, open(manifest_path, "w"), indent=1, default=str)
    return manifest


if __name__ == "__main__":
    try:
        m = run()
        print(json.dumps({k: m[k] for k in ("passed", "dbt", "rows")}, default=str))
    except PipelineFailed as e:
        print("PIPELINE FAILED:", e)
        sys.exit(1)
