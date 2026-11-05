# AI-assisted development log

The posting asks for judgment when using AI tools to write, explain and QA code. This project was built with an AI coding assistant under these rules: a failing test comes before the code; generated code is not trusted until a test or a real-data run has exercised it; a surprising result is investigated, not patched around.

What the review caught (the assistant's own output, corrected after reading failures):

| What happened | How it was caught | What changed |
| --- | --- | --- |
| A test expected an AMI row to have null discharges, but the fixture row kept 100 | The failing assertion showed `100`; the test was wrong, not the model | Expectation corrected inside the reproduce commit (INC-2) |
| A dbt unit test expected the second worklist pair to be tier B | The unit test failed; recomputing the cumulative shares (40%, 60%) showed the pair crosses the 50% line | Expectation corrected and the rule documented in the test description |
| An incident test passed on the real data before the fix | A reproduce test that passes proves nothing | Rewrote it with a fixture that triggers the defect, and labeled INC-5 as latent |
| The MetricFlow command line failed to load the manifest | Diagnosed in logs; version mismatch | Did not claim it worked; replaced with a parse check and an equivalence test |
| The semantic metric omitted the volume rule the marts use | Comparing definitions during review | INC-5 |

What the assistant did well: scaffolding loaders, dbt YAML and test boilerplate quickly. What still needed a person: the grain of every table, which defects are real versus latent, which numbers are assumptions, and what may not be claimed.
