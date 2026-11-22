# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T23:45:20+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:46:09+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-21T23:47:30+00:00 | export-red | 1 | 2.25 | `pytest -q tests/data_migration/test_export.py` | `91ef70aa4a01af63` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-21T23:48:06+00:00 | export-green | 0 | 2.01 | `pytest -q tests/data_migration/test_export.py` | `8178d932945c4da3` |  |  |
| 2026-11-21T23:48:23+00:00 | data-migration-tests | 0 | 5.61 | `pytest -q tests/data_migration` | `7b536d067d217eb0` |  |  |
| 2026-11-21T23:48:34+00:00 | export-utc-check | 0 | 2.01 | `pytest -q tests/data_migration/test_export.py` | `8178d932945c4da3` |  |  |
| 2026-11-21T23:48:41+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:48:41+00:00 | build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T23:48:41+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:48:41+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `44e78b49361054e6` |  |  |
| 2026-11-21T23:48:54+00:00 | export-postformat | 0 | 5.51 | `pytest -q tests/data_migration` | `1c46cbe5c20c138f` |  |  |
| 2026-11-21T23:48:54+00:00 | idiom-format-final | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-21T23:52:04+00:00 | final-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:52:05+00:00 | final-build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T23:52:05+00:00 | final-idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:52:05+00:00 | final-idiom-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-21T23:52:52+00:00 | regression | 0 | 47.05 | `pytest -q` | `cacecdf9f64e730a` |  |  |
| 2026-11-21T23:53:52+00:00 | crap-coverage | 0 | 56.37 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `924d1b8079258ecb` |  |  |
| 2026-11-21T23:53:52+00:00 | crap-lizard | 0 | 0.17 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:53:52+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `17662030e42e504c` |  | gate=crap max=26.0 threshold=30 over=0 methods=186 |
| 2026-11-21T23:54:02+00:00 | mutation-changed | 2 | 7.64 | `python .migration/harness/tools/afs-mutation` | `faf2c315bcb86468` | afs-mutation: mutmut failed on src/cargotracker/data_migration/exporter.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=2 files=2 base=ca4f4a255d67adf64ba1c12a6ec4fb144588807b |
| 2026-11-21T23:54:40+00:00 | export-independent-test | 0 | 1.96 | `pytest -q tests/data_migration/test_export.py` | `8f6abe38f9b13362` |  |  |
| 2026-11-21T23:57:33+00:00 | mutation-changed-final | 1 | 169.76 | `python .migration/harness/tools/afs-mutation` | `0a27cff5f1557c1f` | afs-mutation: FAILED score=0.596 threshold=0.8 killed=59 survived=40 skipped=0 files=2 jobs=2 base=ca4f4a255d67adf64ba1c | gate=mutation score=0.596 threshold=0.8 killed=59 survived=40 files=2 base=ca4f4a255d67adf64ba1c12a6ec4fb144588807b |
| 2026-11-21T23:59:34+00:00 | export-validation-tests | 0 | 2.24 | `pytest -q tests/data_migration/test_export.py` | `2042d19250109bab` |  |  |
| 2026-11-22T00:02:08+00:00 | mutation-changed-final-2 | 2 | 151.44 | `python .migration/harness/tools/afs-mutation` | `55bebdbad7c648da` | afs-mutation: mutmut failed on src/cargotracker/data_migration/management/commands/export_data_snapshot.py; its mutants  | gate=mutation score=n/a error=mutmut-failed failed_files=1 files=2 base=ca4f4a255d67adf64ba1c12a6ec4fb144588807b |
| 2026-11-22T00:03:32+00:00 | timestamp-test-node | 0 | 1.49 | `pytest -q tests/data_migration/test_export.py::test_export_snapshot_rejects_invalid_timestamp_defaults` | `336ed2da889ce4d7` |  |  |
| 2026-11-22T00:04:43+00:00 | export-safe-test-ids | 0 | 2.21 | `pytest -q tests/data_migration/test_export.py` | `22211176911fef0b` |  |  |
| 2026-11-22T00:07:21+00:00 | mutation-changed-final-3 | 1 | 153.11 | `python .migration/harness/tools/afs-mutation` | `92860cc47ba2da6e` | afs-mutation: FAILED score=0.768 threshold=0.8 killed=73 survived=22 skipped=0 files=2 jobs=2 base=ca4f4a255d67adf64ba1c | gate=mutation score=0.768 threshold=0.8 killed=73 survived=22 files=2 base=ca4f4a255d67adf64ba1c12a6ec4fb144588807b |
| 2026-11-22T00:07:45+00:00 | export-assertion-precision | 0 | 2.21 | `pytest -q tests/data_migration/test_export.py` | `22211176911fef0b` |  |  |
| 2026-11-22T00:07:45+00:00 | export-ruff | 1 | 0.01 | `ruff check` | `f2d066777c5aa68b` | Found 1 error. |  |
| 2026-11-22T00:07:54+00:00 | export-assertion-precision-final | 0 | 2.2 | `pytest -q tests/data_migration/test_export.py` | `bcd2653294f68bbb` |  |  |
| 2026-11-22T00:07:54+00:00 | export-ruff-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T00:07:54+00:00 | export-format-final | 1 | 0.01 | `ruff format --check` | `f363338487bfc493` |  |  |
| 2026-11-22T00:10:31+00:00 | mutation-changed-final-4 | 0 | 146.39 | `python .migration/harness/tools/afs-mutation` | `961d021434b5078b` |  | gate=mutation score=0.905 threshold=0.8 killed=86 survived=9 files=2 base=ca4f4a255d67adf64ba1c12a6ec4fb144588807b |
| 2026-11-22T00:11:20+00:00 | export-command-contract | 1 | 2.3 | `pytest -q tests/data_migration/test_export.py` | `42135ab91cf61857` | E               KeyError: 'help' |  |
| 2026-11-22T00:11:37+00:00 | export-command-contract-final | 1 | 2.28 | `pytest -q tests/data_migration/test_export.py` | `505822c0e00e3aa2` | assert help_exit.value.code == 0 |  |
| 2026-11-22T00:11:47+00:00 | export-command-contract-verify | 0 | 2.23 | `pytest -q tests/data_migration/test_export.py` | `ea19c68133dc8232` |  |  |
| 2026-11-22T00:14:17+00:00 | mutation-changed-final-5 | 0 | 146.41 | `python .migration/harness/tools/afs-mutation` | `c4bf3226758bad26` |  | gate=mutation score=0.968 threshold=0.8 killed=92 survived=3 files=2 base=ca4f4a255d67adf64ba1c12a6ec4fb144588807b |
| 2026-11-22T00:16:02+00:00 | export-timezone-test | 0 | 2.4 | `pytest -q tests/data_migration/test_export.py` | `080ce0e9fa70f090` |  |  |
| 2026-11-22T00:16:02+00:00 | export-final-ruff | 1 | 0.01 | `ruff check` | `f71d65051fdb9be6` | Found 1 error. |  |
| 2026-11-22T00:16:13+00:00 | export-timezone-final | 0 | 2.4 | `pytest -q tests/data_migration/test_export.py` | `e417491f7b513e95` |  |  |
| 2026-11-22T00:16:13+00:00 | export-ruff-final-2 | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T00:16:13+00:00 | export-format-final-2 | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-22T00:18:43+00:00 | mutation-changed-final-6 | 0 | 146.64 | `python .migration/harness/tools/afs-mutation` | `0065577dc77f7e69` |  | gate=mutation score=0.979 threshold=0.8 killed=93 survived=2 files=2 base=ca4f4a255d67adf64ba1c12a6ec4fb144588807b |
| 2026-11-22T00:20:05+00:00 | verified-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T00:20:06+00:00 | verified-build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T00:20:06+00:00 | verified-idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T00:20:06+00:00 | verified-idiom-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-22T00:20:54+00:00 | verified-regression | 0 | 48.48 | `pytest -q` | `82c81273fa7f3f20` |  |  |
| 2026-11-22T00:21:45+00:00 | verified-crap-coverage | 0 | 46.69 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `5898c147c171f767` |  |  |
| 2026-11-22T00:21:45+00:00 | verified-crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T00:21:45+00:00 | verified-crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `f8b7d23c709279da` |  | gate=crap max=26.0 threshold=30 over=0 methods=186 |
| 2026-11-22T00:24:16+00:00 | verified-mutation-changed | 0 | 146.68 | `python .migration/harness/tools/afs-mutation` | `0065577dc77f7e69` |  | gate=mutation score=0.979 threshold=0.8 killed=93 survived=2 files=2 base=ca4f4a255d67adf64ba1c12a6ec4fb144588807b |
| 2026-11-22T00:25:35+00:00 | export-command-contract-post | 0 | 2.39 | `pytest -q tests/data_migration/test_export.py` | `b3cee2e7657d8536` |  |  |
| 2026-11-22T00:28:06+00:00 | mutation-changed-help-assert | 0 | 147.01 | `python .migration/harness/tools/afs-mutation` | `0065577dc77f7e69` |  | gate=mutation score=0.979 threshold=0.8 killed=93 survived=2 files=2 base=ca4f4a255d67adf64ba1c12a6ec4fb144588807b |
| 2026-11-22T00:29:16+00:00 | export-command-contract-exact | 0 | 2.38 | `pytest -q tests/data_migration/test_export.py` | `b3cee2e7657d8536` |  |  |
| 2026-11-22T00:31:49+00:00 | mutation-changed-exact-help | 0 | 151.2 | `python .migration/harness/tools/afs-mutation` | `164d608c9bd5727b` |  | gate=mutation score=0.989 threshold=0.8 killed=94 survived=1 files=2 base=ca4f4a255d67adf64ba1c12a6ec4fb144588807b |
