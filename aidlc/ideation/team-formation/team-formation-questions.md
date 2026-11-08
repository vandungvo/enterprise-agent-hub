# Team Formation Questions

## Sources
- [desc] Initial description: "Tài liệu hóa toàn diện hệ thống hiện tại (Brownfield Baseline từ Ideation, Reverse Engineering đến Ops)"
- [scope] Workflow-selected scope: `enterprise`.
- [scope-doc] `aidlc/ideation/scope-definition/scope-document.md`
- [backlog] `aidlc/ideation/scope-definition/intent-backlog.md`

## Q1. [Delivery] Cấu trúc đội ngũ nòng cốt (Core Squad) để phát triển và duy trì hệ thống là gì?
A. Squad liên chức năng (Cross-functional squad) gồm: 1 Solution Architect / Tech Lead (ABAC & Backend), 1 AI/RAG Engineer, 1 Fullstack Frontend Dev, 1 Business Analyst chuyên trách nhân sự & tài chính, 1 DevOps/SecOps Engineer.
B. Toàn bộ giao cho 1 lập trình viên duy nhất thực hiện.
C. Đội ngũ thuần túy là các chuyên gia Prompt Engineering.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q2. [Delivery] Mô hình phối hợp (Collaboration & Mobbing Model)?
A. Mô hình Pair/Mob programming đối với các module bảo mật nhạy cảm (Policy engine, K-anonymity, Data tier access); làm việc độc lập theo Unit ở tầng giao diện và tài liệu RAG, có rà soát chéo (Peer Review).
B. Mỗi người tự làm một phần riêng biệt và không cần review chéo.
X. Khác (vui lòng nêu rõ)
[Answer]: A
