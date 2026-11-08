# Rollback Runbook & Disaster Recovery

## 1. Rollback Triggers (Khi nào cần Rollback?)
- Tỷ lệ lỗi HTTP 5xx vượt quá 1% trong vòng 5 phút sau khi release.
- Độ trễ phản hồi streaming p95 vượt quá 5.0 giây.
- Phát hiện bất kỳ lỗi hồi quy nào liên quan đến phân quyền dữ liệu (Policy Regression) hoặc rò rỉ dữ liệu nhạy cảm C3.
- Nhà cung cấp LLM chính gặp sự cố kết nối kéo dài mà cơ chế fallback tự động không phục hồi được.

## 2. Immediate Rollback Procedure
1. **Rollback bản deploy**:
   ```bash
   # Vercel (môi trường hiện tại): đưa production về bản deploy trước đó
   vercel rollback                      # hoặc: vercel rollback <deployment-url>
   vercel ls enterprise-agent-hub       # xem danh sách deployment để chọn bản

   # Kubernetes (mục tiêu production):
   kubectl rollout undo deployment/enterprise-agent-hub
   ```
   Trên Vercel cũng có thể vào Dashboard → *Deployments* → chọn bản tốt → *Promote to Production*.
   **Lưu ý:** sau `vercel rollback`, Vercel **tắt tự gán domain** cho các bản deploy production mới. Khi bản sửa đã sẵn sàng: `vercel --prod` rồi `vercel promote <deployment-url>` (bật lại tự gán).
2. **Cấu hình Policy Rollback khẩn cấp**:
   - Nếu lỗi xuất phát từ việc sửa sai quy tắc trong `config/policies.yaml`, revert commit cấu hình về phiên bản trước.
   - Trên Vercel: deploy lại (`vercel --prod`), vì mỗi instance đọc cấu hình đóng gói kèm bản deploy.
   - Trên máy chủ cố định: gọi API nạp lại cấu hình bằng token của `platform_admin`:
     ```bash
     curl -X POST https://<host>/api/admin/reload -H "Authorization: Bearer <ADMIN_TOKEN>"
     ```
3. **Thông báo và kiểm toán**:
   - Ghi nhận sự cố vào kênh cảnh báo vận hành nội bộ.
   - Auditor rà soát toàn bộ `data_access_log` phát sinh trong thời gian lỗi (trang *Kiểm toán dữ liệu* hoặc `GET /api/audit/data-access`) để xác định có truy cập bất thường hay không.
4. **Thu hồi phiên khẩn cấp**: đổi `AGENTHUB_SECRET` rồi deploy lại; mọi token đăng nhập cũ lập tức mất hiệu lực.

## 3. Sự cố đã gặp: 2026-11-09, deploy ADR-08

- **Triệu chứng**: mọi request trả `500 FUNCTION_INVOCATION_FAILED`; log: `ModuleNotFoundError: No module named 'fastapi'`.
- **Nguyên nhân**: thêm `pyproject.toml` (chỉ chứa cấu hình tool). Vercel ưu tiên `pyproject.toml` hơn `requirements.txt` ("Installing required dependencies from pyproject.toml") nên không cài dependency nào.
- **Xử lý**: `vercel rollback` về bản trước (~1 phút gián đoạn); khai báo dependency trong `[project].dependencies`; thêm `tests/test_dependencies.py` giữ `pyproject.toml` và `requirements*.txt` khớp nhau; deploy **preview** kiểm tra `/api/health` trước, rồi `vercel --prod` + `vercel promote`.
- **Bài học**: luôn deploy preview và gọi `/api/health` (`vercel curl /api/health --deployment <url>`) trước khi lên production; đọc build log khi đổi file manifest/cấu hình build.
