{# CMS dates are MM/DD/YYYY text. Parse without failing on bad values; one macro so the Snowflake target differs in one place. #}
{% macro parse_us_date(col) -%}{{ return(adapter.dispatch('parse_us_date', 'heally')(col)) }}{%- endmacro %}
{% macro default__parse_us_date(col) -%}try_strptime({{ col }}, '%m/%d/%Y')::date{%- endmacro %}
{% macro snowflake__parse_us_date(col) -%}try_to_date({{ col }}, 'MM/DD/YYYY'){%- endmacro %}
