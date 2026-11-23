# Mutation failed: DM-05D
Written by `afs-mutation` on its last run (base `f415794e3aff44382d65a23c7841c416c0678532`): mutmut failed, so no mutant of these files was tested and there is no score. The survivors of any earlier run no longer apply. The last lines of each failure:

- `src/cargotracker/data_migration/exporter.py`
  ```
  +  where 2 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.13.18/x64/bin/python', '/tmp/afs-mutation-01nbonrr/w0/.migration...ile '/tmp/afs-mutation-01nbonrr/w0/.migration/harness/tools/data_reconcile.py': [Errno 2] No such file or directory\n").returncode
  
  [31m!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!![0m
  
  [31m[31m[1m1 failed[0m, [32m1 passed[0m[31m in 0.56s[0m[0m
  ```
- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py`
  ```
  +  where 2 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.13.18/x64/bin/python', '/tmp/afs-mutation-01nbonrr/w1/.migration...ile '/tmp/afs-mutation-01nbonrr/w1/.migration/harness/tools/data_reconcile.py': [Errno 2] No such file or directory\n").returncode
  
  [31m!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!![0m
  
  [31m[31m[1m1 failed[0m, [32m1 passed[0m[31m in 0.56s[0m[0m
  ```
