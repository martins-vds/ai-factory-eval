# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:40:29+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:44:18+00:00 | destination-red | 2 | 2.42 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c2db4cbd54279054` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:45:18+00:00 | destination-get | 1 | 1.99 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e8eb035f18689b20` | assert first_response.status_code == 200 |  |
| 2026-11-18T12:45:28+00:00 | destination-get | 1 | 1.84 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a21a7efbf83058ba` | assert first_response.status_code == 200 |  |
| 2026-11-18T12:45:39+00:00 | destination-get | 1 | 1.87 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `00578af47d1c544b` | assert first_response.status_code == 200 |  |
| 2026-11-18T12:45:58+00:00 | destination-get | 1 | 1.84 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6f84d9c19deac764` | assert first_response.status_code == 200 |  |
| 2026-11-18T12:46:06+00:00 | destination-get | 1 | 1.9 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4876e89860e7dfce` | assert first_response.status_code == 200 |  |
| 2026-11-18T12:46:16+00:00 | destination-get | 0 | 1.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `67ecf94f55b8e441` |  |  |
| 2026-11-18T12:46:30+00:00 | deadline-get-red | 1 | 2.18 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4db3cadd25ad7e41` | >       assert response.status_code == 200 |  |
| 2026-11-18T12:46:49+00:00 | deadline-get | 1 | 2.16 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ea5c1d869ea1a692` | assert response.status_code == 200 |  |
| 2026-11-18T12:47:11+00:00 | deadline-get | 1 | 2.21 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `35f1bd9ba15c44a1` | assert response.status_code == 200 |  |
| 2026-11-18T12:47:20+00:00 | deadline-get | 1 | 2.21 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ba52ccc6552999ff` | assert response.status_code == 200 |  |
| 2026-11-18T12:47:32+00:00 | deadline-get | 0 | 2.13 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `825826ec75aed015` |  |  |
| 2026-11-18T12:48:05+00:00 | deadline-error-red | 1 | 2.59 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `cffd48ef25b7bcfe` | assert original is not None |  |
| 2026-11-18T12:48:26+00:00 | deadline-error | 0 | 2.48 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `cf96176e01db94c8` |  |  |
| 2026-11-18T12:48:43+00:00 | destination-update-red | 1 | 2.93 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6952d4d9dbaf994d` | assert original is not None |  |
| 2026-11-18T12:49:03+00:00 | destination-update | 0 | 2.85 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `b45312b5d3e71208` |  |  |
| 2026-11-18T12:49:19+00:00 | deadline-update | 0 | 3.29 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `90dfd6d8ae1500b9` |  |  |
| 2026-11-18T12:49:48+00:00 | table-dialogs-red | 1 | 3.64 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bc4ff0cd4ba4cf20` | >       assert 'Change destination' in row |  |
| 2026-11-18T12:50:09+00:00 | dialog-actions | 0 | 4.6 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `7fc2ff7391ccd856` |  |  |
| 2026-11-18T12:50:48+00:00 | dialogs-targeted | 0 | 4.71 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `ec40d53ff0784cbc` |  |  |
