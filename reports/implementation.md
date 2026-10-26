# Đối chiếu yêu cầu với bản triển khai

Nguồn: `yeucau.txt`, `yeucaubaitoan.txt` và chỉ đạo dùng MySQL/phân quyền của người dùng. PDF GudJobs là tài liệu mẫu về bố cục báo cáo; giao diện ứng dụng dựa trên frontend có sẵn.

| Yêu cầu | Vị trí thực hiện |
|---|---|
| Mục đích, đối tượng, quy tắc nghiệp vụ | chapter_01.md |
| Thực thể, liên kết, ER, mô hình quan hệ, PK/FK | chapter_02.md, sql/1.TaoCoSoDuLieu.sql |
| Phụ thuộc hàm và BCNF | chapter_02.md |
| DDL, CHECK, UNIQUE, dữ liệu hợp lệ | sql/1.TaoCoSoDuLieu.sql |
| Mỗi quan hệ ít nhất 20 dòng, dữ liệu trùng không khóa và trường hợp biên | sql/2.ThemDuLieu.sql |
| UPDATE, DELETE và minh họa dữ liệu sai bị chặn | sql/3.UpdateDeleteRangBuoc.sql |
| Cập nhật phân quyền trên CSDL cũ | sql/4.CapNhatPhanQuyen.sql |
| 10 SELECT/thành viên, 5 thành viên | sql/query/member_01.sql đến member_05.sql |
| CRUD danh mục, sản phẩm, cửa hàng | app/catalog.py; tab tương ứng |
| Nhân sự, bổ nhiệm, hạ chức, lương/cấp bậc | app/employees.py; tab Nhân sự & phân quyền |
| Người quản lý theo thời gian | lich_su_quan_ly; nút Lịch sử bổ nhiệm |
| Chủ thương hiệu quản lý cấp dưới toàn chuỗi | permissions.py, employees.py |
| Quản lý khu vực chỉ quản lý cấp dưới trong miền | store_scope + validate_assignment + can_manage |
| Quản lý cửa hàng chỉ quản lý nhân viên cửa hàng | store_scope + kiểm tra thứ bậc |
| Nhân viên lập đơn, nhìn số lượng phân phối | documents.py; tab Đơn hàng/Phân phối |
| Nhân viên nhận phải cùng cửa hàng | save_document |
| Khách và lịch sử mua hàng | catalog.py; /customers/{id}/history |
| Giá lịch sử, thành tiền và tổng tiền | chi_tiet_don_hang.don_gia_ban; documents.py; form đơn hàng |
| Thống kê theo thời gian/nhân viên/cửa hàng | reports.py; tab Báo cáo doanh thu |
| Tab/nút hiển thị theo vai trò và dữ liệu theo phạm vi | management.js và backend permissions |
| Giao diện giữ bố cục dashboard đã làm | index.html, dashboard.css, charts.js |
| Kiểm thử | backend/tests, frontend/tests, test-evidence.md |

Các chương Markdown là tài liệu kỹ thuật đã cập nhật theo code. Chưa xuất thành báo cáo nộp chính thức ít nhất 20 trang; các PDF/DOCX mẫu ban đầu được giữ nguyên. Triển khai MySQL theo chỉ đạo, không tuyên bố chạy SQL Server.
