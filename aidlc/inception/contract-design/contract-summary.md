# Contract Summary & Boundary Specifications

## 1. Inter-Unit Contract: Security Policy Boundary (U-01 <-> U-02, U-04)

```python
# Interface: Policy Engine (PEP/PDP Contract)
class PolicyEngine:
    def require(self, principal: Principal, resource: str, target_id: str | None = None) -> bool:
        """
        Thẩm định quyền đối với một bản ghi dữ liệu cụ thể.
        Trả về True nếu hợp lệ; Raise PermissionDeniedError nếu không đủ quyền.
        """
        ...

    def scope(self, principal: Principal, resource: str) -> ScopeResult:
        """
        Trả về tiêu chí lọc (filter condition) cho các truy vấn danh sách hoặc tổng hợp:
        - ScopeResult.allowed: bool
        - ScopeResult.unit_ids: list[str] (phạm vi các đơn vị được phép xem)
        - ScopeResult.k_threshold: int (ngưỡng k-anonymity: 1, 3, hoặc 5)
        """
        ...

    def log_access(self, principal: Principal, resource: str, target_id: str, action: str = "read") -> None:
        """Ghi nhận sự kiện truy cập nhạy cảm C3 vào bảng data_access_log."""
        ...
```

## 2. Inter-Unit Contract: Typed Tools Boundary (U-02 <-> U-03)

```python
# Interface: Tool Execution Contract
class BaseTool(BaseModel):
    name: str
    description: str
    parameters_schema: dict[str, Any]

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        """
        Thực thi công cụ với tham số và context chứa:
        - context.principal: Principal (danh tính người gọi)
        - context.db: Session (kết nối DB)
        Trả về ToolResult(data=..., error=..., requires_approval=...)
        """
        ...
```

## 3. Public Client API Contract: SSE Chat Streaming (U-03 <-> U-05)

```yaml
# OpenAPI / SSE Protocol Specification
endpoint: POST /api/chat
content_type: text/event-stream
request_body:
  conversation_id: string (optional)
  message: string (required)

stream_events:
  - event: agent_start
    data: { agent_id: "people", agent_name: "Trợ lý Nhân sự" }
  - event: tool_call
    data: { tool: "get_payslip", args: { month: 10 } }
  - event: tool_result
    data: { tool: "get_payslip", summary: "Lương gross 45tr, net 37tr" }
  - event: text_delta
    data: { text: "Phiếu lương tháng 10 của bạn..." }
  - event: done
    data: { conversation_id: "conv-123", message_id: "msg-456" }
  - event: error
    data: { code: "POLICY_VIOLATION", detail: "Từ chối quyền truy cập" }
```

## 4. Approval Queue Contract (U-02 <-> U-05)

```json
{
  "request_id": "REQ-102",
  "requester_id": "EMP-DEV-01",
  "requester_name": "Nguyen Van A",
  "action_type": "submit_leave_request",
  "payload": {
    "start_date": "2026-11-12",
    "end_date": "2026-11-13",
    "leave_type": "annual",
    "days": 2
  },
  "status": "PENDING",
  "assigned_approver_id": "EMP-MGR-01",
  "created_at": "2026-11-08T09:00:00Z"
}
```
