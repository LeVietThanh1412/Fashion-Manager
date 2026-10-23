# SQL assets

- `schema/00_original_snapshot.sql` is an untouched copy of the supplied schema.
- `schema/01_create_database.sql` is a demo-only destructive reset.
- `schema/02_create_tables.sql` creates the InnoDB/utf8mb4 schema.
- `data/01_seed.sql` is deterministic demo data; every table has at least 20 rows.
- `query/member_01.sql` through `member_05.sql` contain the 50 academic queries.
- `app/` contains one parameterized statement per backend use case.
- `tests/` contains verification and negative examples. Run negative statements one at a time
  in a disposable database; never disable foreign-key checks.
