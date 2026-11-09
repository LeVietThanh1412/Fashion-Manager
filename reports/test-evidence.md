> T?i li?u l?u tr? tr??c schema v3; kh?ng d?ng l?nh ho?c m? h?nh b?n d??i ?? kh?i t?o. Xem [quy tr?nh hi?n h?nh](../README.md), [ERD](erd.md) v? [ph?n quy?n](permissions.md).

# Test evidence

## Đã chạy
- `py -3 scripts\check_queries.py` -> PASS: 5 files, 50 unique query IDs.
- `$env:PYTHONPATH='backend'; py -3.13 -m pytest backend\tests -q` -> PASS: 4 tests.
- `py -3.13 -m py_compile ...` -> PASS: backend modules compile.
- Query registry smoke check -> PASS: 75 IDs, 15 per member, first `M01_Q01`.
- FastAPI smoke test -> PASS: `GET /health` = 200 and `GET /api/query-explorer` = 200 with 50 items.

## Chưa chạy
- MySQL version, schema/seed integration, 50 query execution, constraint negatives và API
  integration -> NOT RUN: `mysql` CLI không có trong PATH; `verify_db.py` received MySQL
  authentication error for the placeholder `demo_user`, so no database PASS is claimed.

Không sử dụng dữ liệu giả, ảnh giả hoặc log giả để thay thế evidence.
