# User Flow & Interaction Diagrams

## Core User Flow: Asking a Question with Policy & Delegation

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 Người dùng (Nhân viên)
    participant UI as 💻 Web UI (Chat)
    participant Router as 🧭 Router Agent
    participant Policy as 🛡️ Policy Engine (Data Tier)
    participant Agent as 🤖 Domain Agent (e.g. People)
    participant DB as 🗄️ Database / HRIS
    participant LLM as 🧠 LLM Provider (Claude / Gemini)

    User->>UI: Nhập câu hỏi: "Xem lương tháng 10 của tôi"
    UI->>Router: POST /api/chat (Kèm Session Cookie)
    Note over Router: Dựng lại Principal: dev.alpha (L3, Games)
    Router->>LLM: Gọi LLM phân tích ý định
    LLM-->>Router: Tool call: delegate_to_agent("people", query)
    Router->>Agent: Chuyển tiếp ngữ cảnh tới People Agent
    Agent->>LLM: Gửi prompt + tool definitions của People Agent
    LLM-->>Agent: Tool call: get_payslip(employee_id="dev.alpha", month=10)
    Agent->>Policy: Kiểm tra quyền: require("compensation.individual", target="dev.alpha")
    Note over Policy: So sánh Principal.employee_id == target -> HỢP LỆ (self)
    Policy-->>Agent: PERMITTED
    Agent->>DB: Query bảng payslips WHERE emp_id="dev.alpha"
    DB-->>Agent: Dữ liệu lương chi tiết
    Agent->>Policy: Ghi log kiểm toán truy cập C3 (data_access_log)
    Agent->>LLM: Gửi kết quả tool về cho LLM
    LLM-->>Agent: Trả về câu trả lời giải thích tự nhiên
    Agent-->>Router: Tổng hợp kết quả
    Router-->>UI: Stream SSE token về giao diện người dùng
    UI-->>User: Hiển thị câu trả lời và trace bước thực thi
```

## Secondary Flow: Action with Approval Queue (Human-in-the-Loop)

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 Nhân viên
    participant UI as 💻 Web UI
    participant Agent as 🤖 Agent
    participant Approval as 📋 Approval Queue
    actor Manager as 👔 Quản lý trực tiếp

    User->>UI: "Tôi muốn xin nghỉ phép ngày 12/11 và 13/11"
    UI->>Agent: Gọi tool submit_leave_request
    Agent->>Approval: Tạo yêu cầu phê duyệt mới (Trạng thái: PENDING)
    Note over Approval: Tìm manager_id trong HRIS -> manager.alpha
    Approval-->>Agent: Yêu cầu đã ghi nhận, mã REQ-102
    Agent-->>UI: "Đơn nghỉ phép đã được gửi tới Quản lý Nguyen Van B để duyệt."
    
    Manager->>UI: Mở trang "Phê duyệt" -> Thấy REQ-102
    Manager->>UI: Bấm nút [Phê duyệt]
    UI->>Approval: POST /api/approvals/REQ-102/approve
    Approval->>Approval: Kiểm tra: User == manager_id, Trạng thái == PENDING
    Approval->>Approval: Cập nhật: APPROVED, trừ số dư phép trong DB
    Approval-->>UI: Thành công
```

## Assumptions & Open Questions
None. [Q1, Q2]
