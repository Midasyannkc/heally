# ADR 3: Business assumptions are dbt variables, never literals

Status: accepted. Cost per readmission, avertable share, minimum volume and tier lines live in `dbt_project.yml`. The savings numbers are not CMS data, so a sensitivity grid is a mart of its own. Stakeholders can disagree with an assumption without reading SQL.
