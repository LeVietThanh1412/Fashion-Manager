# SQL assets

Backend hiện dùng schema từ `data/1.TaoCoSoDuLieu.sql` + `data/2.ThemDuLieu.sql` + migration `data/3.UpdateDeleteRangBuoc.sql`. Database đang cấu hình đã có dữ liệu và vai trò. Bộ `schema/` + `data/01_seed.sql` dưới đây là bộ demo khác, không dùng lẫn. Xem `../INTEGRATION.md`.

- `schema/00_original_snapshot.sql` is an untouched copy of the supplied schema.
- `schema/01_create_database.sql` is a demo-only destructive reset.
- `schema/02_create_tables.sql` creates the InnoDB/utf8mb4 schema, role/salary columns and region
  mapping (`1 = Miền Bắc`, `2 = Miền Trung`, `3 = Miền Nam`).
- `data/01_seed.sql` is deterministic demo data; every table has at least 20 rows.
- `data/3.UpdateDeleteRangBuoc.sql` is a one-time additive upgrade for the legacy
  `data/1.TaoCoSoDuLieu.sql` + `data/2.ThemDuLieu.sql` setup. Do not run it on the new schema.
- `query/member_01.sql` through `member_05.sql` contain 51 registered academic queries.
- `app/` contains parameterized statements used by the backend; Python loads some through
  `QueryLoader`; several repositories currently embed SQL adapted to the active schema. Older SQL files may target the other demo schema, so check repository call sites before using them.
- `tests/` contains verification and negative examples. Run negative statements one at a time
  in a disposable database; never disable foreign-key checks.
