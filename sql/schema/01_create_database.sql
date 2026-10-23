-- Demo-only reset. Never run against a production database.
-- Usage requires an explicit local/demo target selected by the operator.
DROP DATABASE IF EXISTS quan_ly_chuoi_thoi_trang;
CREATE DATABASE quan_ly_chuoi_thoi_trang
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE quan_ly_chuoi_thoi_trang;
