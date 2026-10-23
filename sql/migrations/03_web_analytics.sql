-- Additive migration: run against DB_NAME; existing business tables are untouched.
CREATE TABLE IF NOT EXISTS luot_truy_cap_web (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    thoi_gian DATETIME NOT NULL,
    trang_vao VARCHAR(500) NOT NULL,
    ip_an_danh VARCHAR(64) NOT NULL,
    thiet_bi VARCHAR(10) NOT NULL,
    den_tu VARCHAR(500) NOT NULL,
    INDEX idx_luot_truy_cap_thoi_gian (thoi_gian, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
