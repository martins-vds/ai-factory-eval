# Mutation failed: DM-05D
Written by `afs-mutation` on its last run (base `f415794e3aff44382d65a23c7841c416c0678532`): mutmut failed, so no mutant of these files was tested and there is no score. The survivors of any earlier run no longer apply. The last lines of each failure:

- `src/cargotracker/data_migration/exporter.py`
  ```
  [31mERROR: not found: /tmp/afs-mutation-zba2slbx/w0/tests/data_migration/test_export.py::test_export_data_snapshot_rejects_invalid_mappings
  
  (no match in any of [<Module test_export.py>])
  
  [0m
  ```
- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py`
  ```
  [31mERROR: not found: /tmp/afs-mutation-zba2slbx/w1/tests/data_migration/test_export.py::test_export_data_snapshot_rejects_invalid_mappings
  
  (no match in any of [<Module test_export.py>])
  
  [0m
  ```
