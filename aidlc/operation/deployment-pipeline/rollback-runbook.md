# Rollback Runbook & Disaster Recovery

## 1. Rollback Triggers (Khi nào cần Rollback?)
- Tỷ lệ lỗi HTTP 5xx vượt quá 1% trong vòng 5 phút sau khi release.
- Độ trễ phản hồi streaming p95 vượt quá 5.0 giây.
- Phát hiện bất kỳ lỗi hồi quy nào liên quan đến phân quyền dữ liệu (Policy Regression) hoặc rò rỉ dữ liệu nhạy cảm C3.
- Nhà cung cấp LLM chính gặp sự cố kết nối kéo dài mà cơ chế fallback tự động không phục hồi được.

## 2. Immediate Rollback Procedure
1. **Container Orchestrator Rollback**:
   ```bash
   # Nếu dùng Docker Compose / Swarm:
   docker compose rollback
   
   # Nếu dùng Kubernetes:
   kubectl rollout undo deployment/enterprise-agent-hub
   ```
2. **Cấu hình Policy Rollback khẩn cấp**:
   - Nếu lỗi xuất phát từ việc sửa sai quy tắc trong `config/policies.yaml`, revert commit cấu hình về phiên bản trước.
   - Gọi API nạp lại cấu hình:
     ```bash
     curl -X POST http://localhost:8000/api/admin/reload-config -H "Authorization: Bearer <ADMIN_TOKEN>"
     ```
3. **Thông báo và kiểm toán**:
   - Ghi nhận sự cố vào kênh cảnh báo vận hành nội bộ.
   - Auditor rà soát toàn bộ `data_access_log` phát sinh trong thời gian lỗi để xác định có truy cập bất thường hay không.
