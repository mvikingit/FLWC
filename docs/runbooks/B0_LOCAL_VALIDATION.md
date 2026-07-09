# B0 Local Validation

Run from repository root:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests/unit
PYTHONPATH=src python3 scripts/run_fixture_validation.py tests/fixtures/valid/synthetic_candidate_package_valid.json
```

Expected result: unit tests pass and the valid synthetic package returns `aggregate_result=ACCEPT`.
