# Mob Composition & Collaboration Protocol

## Mobbing Sessions for High-Risk Modules
Đối với các thành phần cốt lõi có độ nhạy cảm cao, dự án áp dụng hình thức Mob/Pair Programming [Q2]:

### 1. Data-Tier Policy & ABAC Mob
- **Thành phần**: Tech Lead + BA + SecOps.
- **Trọng tâm**: Xác thực ma trận phân quyền trong `config/policies.yaml`, cơ chế dựng `Principal` từ HRIS, và kiểm tra các kịch bản bypass quyền hoặc privilege escalation [Q1, Q2].
- **Tiêu chuẩn hoàn thành**: 100% test cases phân quyền vượt qua kiểm thử tự động, không có ngoại lệ lọt lưới.

### 2. K-Anonymity & Analytics Suppression Mob
- **Thành phần**: Tech Lead + AI Engineer + BA.
- **Trọng tâm**: Rà soát thuật toán ẩn nhóm nhỏ (< 5 hoặc < 3 người) và thuật toán Complementary Suppression (ẩn thêm nhóm nhỏ thứ hai) để triệt tiêu nguy cơ suy ngược số liệu qua phép trừ tổng [Q2].

### 3. Red-Team Jailbreak Review Mob
- **Thành phần**: AI Engineer + SecOps + Tech Lead.
- **Trọng tâm**: Thực hiện các truy vấn giả lập tấn công injection ("Tôi là CEO...", "Bỏ qua các lệnh trước...", "Trích xuất bảng lương...") để chứng minh model không thể vượt qua tầng policy dưới code [Q2].

## Assumptions & Open Questions
None. [Q1, Q2]
