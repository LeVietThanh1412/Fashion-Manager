# Phân quyền hiện hành

Ma trận triển khai nằm trong phần `-- @system` của [`sql/data/02_seed_data.sql`](../sql/data/02_seed_data.sql). Vai trò không được suy từ mã nhân viên, chức vụ, nơi làm việc, cấp quản lý hay số cấp dưới.

| Vai trò | Quyền |
| --- | --- |
| `system_admin` | Toàn bộ quyền trong danh mục, gồm `auth.grant`, `queries.execute`, `analytics.read` |
| `operations_manager` | Các quyền vận hành, bán hàng, kho, nhân sự, báo cáo; không có `auth.grant`, `queries.execute`, `analytics.read` |
| `regional_manager` | `catalog.read`, `stores.read`, `employees.read/write/salary`, `sales.read/cancel`, `reports.read`, `inventory.read/transfer` |
| `store_manager` | `catalog.read`, `stores.read`, `employees.read/write/salary`, `sales.read/create/cancel`, `reports.read`, `inventory.read`, `customers.read/write` |
| `sales_staff` | `catalog.read`, `stores.read`, `sales.read/create`, `inventory.read`, `customers.read/write` |
| `warehouse_staff` | `catalog.read`, `inventory.read/adjust/transfer` |

Một quyền chỉ có hiệu lực trong **phạm vi của chính phân công** chứa quyền đó. Phạm vi `region` bao phủ cửa hàng trong vùng và kho trung tâm gắn vùng; `store` bao phủ cửa hàng và kho của cửa hàng khi chức năng cho phép; `warehouse` chỉ bao phủ kho đó. Phân công `system` bao phủ mọi nơi. `queries.execute` và `analytics.read` yêu cầu phạm vi hệ thống.

Phân công chỉ có hiệu lực khi trạng thái `active`, đã đến `tu_ngay`, chưa tới `den_ngay` và chưa bị thu hồi. Quyền được nạp lại mỗi request. Trang **Tài khoản của tôi** hiển thị riêng từng vai trò, phạm vi, thời hạn và các quyền của nó; không trộn quyền giữa hai phạm vi.

Người cấp quyền cần một phân công có `auth.grant`, `duoc_uy_quyen=true`, đang hiệu lực, chứa **toàn bộ** quyền của vai trò được cấp, bao phủ phạm vi và thời hạn được cấp. Backend khóa tài khoản người cấp và đọc lại phân công trong transaction. Người có `employees.write` được xem danh sách tài khoản trong phạm vi của mình và tạo thông tin đăng nhập cho nhân viên đang làm việc trong cùng phạm vi; backend kiểm tra lại phạm vi khi tạo. Quyền này không cho phép gán vai trò, khóa tài khoản hoặc đặt lại mật khẩu. Các thao tác quản trị đó yêu cầu `auth.grant` ở phạm vi hệ thống. Tài khoản được tạo không có vai trò; người dùng chỉ xem trang cá nhân cho tới khi được gán quyền.

Đổi mật khẩu cá nhân yêu cầu mật khẩu hiện tại và mật khẩu mới tối thiểu 12 ký tự. Đổi/đặt lại mật khẩu hoặc khóa tài khoản tăng `auth_version`; tự đổi mật khẩu trả token mới cho phiên hiện tại và vô hiệu hóa các token khác. Ngừng làm việc khóa tài khoản nhưng không xóa lịch sử. Mật khẩu/hash không được trả qua API danh sách tài khoản hoặc giao diện.
