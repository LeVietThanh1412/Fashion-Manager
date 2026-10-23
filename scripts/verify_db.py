"""Integration verification. It deliberately returns NOT RUN when MySQL is unavailable."""
import os
import sys

try:
    import mysql.connector
except ImportError:
    print("NOT RUN: mysql-connector-python is not installed")
    raise SystemExit(2)


def main() -> int:
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            database=os.getenv("DB_NAME", "quan_ly_chuoi_thoi_trang"),
            user=os.getenv("DB_USER", "demo_user"),
            password=os.getenv("DB_PASSWORD", ""),
            connection_timeout=3,
        )
    except Exception as exc:
        print(f"NOT RUN: cannot connect to MySQL ({exc})")
        return 2
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        print(f"MySQL version: {cursor.fetchone()[0]}")
        for table in (
            "danh_muc", "cua_hang", "san_pham", "nhan_vien", "phan_phoi",
            "chi_tiet_phan_phoi", "khach_hang", "don_hang", "chi_tiet_don_hang",
        ):
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            if count < 20:
                print(f"FAIL: {table} has {count} rows")
                return 1
            print(f"PASS: {table} has {count} rows")
        return 0
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
