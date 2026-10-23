# Chương 2 - Phân tích và thiết kế CSDL

Mô hình gồm chín quan hệ theo schema gốc. Khóa chính là mã của từng thực thể; hai bảng chi
tiết thể hiện quan hệ nhiều-nhiều thông qua khóa ngoại, trong đó chi tiết phân phối có khóa
ghép. Các khóa ngoại dùng InnoDB và mặc định RESTRICT để bảo vệ lịch sử.

Các phụ thuộc hàm và lập luận BCNF được trình bày trong
`plans/03-database-design.md`. Bản triển khai giữ snapshot schema gốc tại
`sql/schema/00_original_snapshot.sql`; script mới chỉ bổ sung tên constraint, charset và
engine, không đổi miền nghiệp vụ.
