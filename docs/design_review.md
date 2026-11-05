# Open design questions for a senior review

Decisions made here that a senior analytics engineer should confirm before production.

1. **Excess readmissions are estimated** from published rates (discharges x (predicted - expected) / 100). CMS publishes counts only for some pairs. Is the estimate acceptable for partner-facing numbers, or should the definition use CMS's own penalty formula?
2. **Positive-only sums.** The marts floor each pair at zero before summing, so a good hospital does not offset a bad one. Right for outreach, not for a net view. Should both exist?
3. **Tier boundary rule.** The pair that crosses the 50% line is tier A. An alternative is to stop just before it. The unit test documents the chosen rule.
4. **Annualizing** divides the 3 year window by 3. Seasonality and volume trends are ignored.
5. **Full refresh of raw tables** on each changed file. At larger volume this should become an incremental merge on the row hash.
6. **Reverse ETL guard** refuses to retire more than 50% of destination rows. Is 50% the right number for the CRM team?
7. **Population.** HRRP covers Medicare fee-for-service. Commercial and Medicare Advantage members are out of scope for these data.
