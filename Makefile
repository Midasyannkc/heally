export HEALLY_DB ?= $(CURDIR)/out/heally.duckdb
export DBT_SEND_ANONYMOUS_USAGE_STATS=False
DBT = dbt --project-dir dbt_heally --profiles-dir dbt_heally

.PHONY: test run build docs export dashboard notebook incidents
test:
	python -m pytest -q
run:            ## sync, dbt build (models, tests, unit tests), monitors, reverse ETL; fails closed
	python -m heally.pipeline
build:
	$(DBT) seed && $(DBT) build
docs:
	$(DBT) docs generate --static && cp out/dbt_target/static_index.html docs/dbt_docs.html
export:
	python scripts/export_marts.py
dashboard:
	python scripts/build_dashboard.py
notebook:
	python scripts/build_notebook.py
incidents:
	python scripts/incidents.py && python scripts/verify_incidents.py
