# Manual test matrix

`actual`, trạng thái và evidence chỉ được điền sau khi chạy thật. Chưa có MySQL CLI/server
trong môi trường audit nên các ca phụ thuộc DB hiện là `NOT RUN (MySQL CLI unavailable)`.

| ID | module | preconditions | test data/steps | expected SQL/HTTP/UI result | actual | PASS/FAIL/NOT RUN | evidence |
|---|---|---|---|---|---|---|---|
| MT01 | bootstrap | MySQL | tạo DB sạch, chạy schema/seed | chạy không lỗi, counts deterministic | | NOT RUN | |
| MT02 | seed | seed | đếm `danh_muc` | >=20 | | NOT RUN | |
| MT03 | seed | seed | đếm `cua_hang` | >=20 | | NOT RUN | |
| MT04 | seed | seed | đếm `san_pham` | >=20 | | NOT RUN | |
| MT05 | seed | seed | đếm `nhan_vien` | >=20 | | NOT RUN | |
| MT06 | seed | seed | đếm `phan_phoi` | >=20 | | NOT RUN | |
| MT07 | seed | seed | đếm `chi_tiet_phan_phoi` | >=20 | | NOT RUN | |
| MT08 | seed | seed | đếm `khach_hang` | >=20 | | NOT RUN | |
| MT09 | seed | seed | đếm `don_hang` | >=20 | | NOT RUN | |
| MT10 | seed | seed | đếm `chi_tiet_don_hang` | >=20 | | NOT RUN | |
| MT11 | queries | seed | chạy member_01 | 10/10 query chạy | | NOT RUN | |
| MT12 | queries | seed | chạy member_02 | 10/10 query chạy | | NOT RUN | |
| MT13 | queries | seed | chạy member_03 | 10/10 query chạy | | NOT RUN | |
| MT14 | queries | seed | chạy member_04 | 10/10 query chạy | | NOT RUN | |
| MT15 | queries | seed | chạy member_05 | 10/10 query chạy | | NOT RUN | |
| MT16 | constraint | seed | insert duplicate PK | reject | | NOT RUN | |
| MT17 | constraint | seed | insert unknown FK category | reject | | NOT RUN | |
| MT18 | constraint | seed | insert quantity 0 | reject | | NOT RUN | |
| MT19 | constraint | seed | insert quantity -1 | reject | | NOT RUN | |
| MT20 | constraint | seed | insert negative price | reject | | NOT RUN | |
| MT21 | constraint | seed | duplicate product variant | reject | | NOT RUN | |
| MT22 | constraint | seed | NULL required customer name | reject | | NOT RUN | |
| MT23 | self FK | seed | manager NULL | accept | | NOT RUN | |
| MT24 | self FK | seed | unknown manager | reject | | NOT RUN | |
| MT25 | referential | seed | delete referenced category | reject | | NOT RUN | |
| MT26 | search | API | search no match | empty list, 200 | | NOT RUN | |
| MT27 | search | API | Unicode name search | matching rows | | NOT RUN | |
| MT28 | search | API | `%` and `_` input | treated as data per policy | | NOT RUN | |
| MT29 | API | backend | malformed JSON customer | 422 | | NOT RUN | |
| MT30 | API | backend | unknown product ID | 404/empty by contract | | NOT RUN | |
| MT31 | API | backend | duplicate customer | 409 | | NOT RUN | |
| MT32 | API | backend | SQL injection string as name | literal data/no SQL execution | | NOT RUN | |
| MT33 | transaction | backend+DB | invalid order detail | header/details rollback | | NOT RUN | |
| MT34 | transaction | backend+DB | valid multiple details | one commit, exact total | | NOT RUN | |
| MT35 | query explorer | backend | unknown query ID | 404 | | NOT RUN | |
| MT36 | query explorer | backend | attempt UPDATE query | rejected, read-only only | | NOT RUN | |
| MT37 | reporting | seed | revenue by month | non-empty grouped output | | NOT RUN | |
| MT38 | reporting | seed | product with no sale | LEFT JOIN/NOT EXISTS behavior | | NOT RUN | |
| MT39 | frontend gate | template supplied | responsive UI | execute only after template | | NOT RUN | |
| MT40 | frontend gate | template supplied | loading/error/empty states | execute only after template | | NOT RUN | |
