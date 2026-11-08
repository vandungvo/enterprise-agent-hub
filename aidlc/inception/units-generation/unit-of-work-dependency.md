# Unit of Work Dependency DAG

## Dependency Graph (Topology)

```mermaid
graph TD
    U01["U-01: core-security-policy (service)"]
    U02["U-02: data-access-tools (library)"]
    U03["U-03: multi-agent-orchestrator (service)"]
    U04["U-04: hybrid-rag-service (service)"]
    U05["U-05: web-portal-frontend (ui)"]

    U01 --> U02
    U01 --> U04
    U01 --> U03
    U02 --> U03
    U04 --> U03
    U03 --> U05
    U04 --> U05
```

## Dependency Declarations

- **U-01 (`core-security-policy`)**: Không phụ thuộc vào unit nào (Nền tảng bảo mật gốc).
- **U-02 (`data-access-tools`)**: Phụ thuộc `U-01` (Gọi `policy.require` và `policy.scope` trong từng tool).
- **U-04 (`hybrid-rag-service`)**: Phụ thuộc `U-01` (Kiểm tra Document ACL theo Principal).
- **U-03 (`multi-agent-orchestrator`)**: Phụ thuộc `U-01`, `U-02`, `U-04` (Điều phối việc gọi tools và RAG search).
- **U-05 (`web-portal-frontend`)**: Phụ thuộc `U-03`, `U-04` (Giao tiếp qua REST API và SSE streams).
