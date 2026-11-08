# Practices Discovery Questions

## Sources
- [codekb] `aidlc/codekb/enterprise-agent-hub/`
- [scope] `enterprise`

## Q1. [Developer] Các quy ước lập trình và chuẩn kiến trúc chính đã được phát hiện trong codebase là gì?
A. Python 3.11+, Pydantic v2 schemas cho 100% request/response và tool parameters; Tách bạch giữa Router, Specialist Agent và Data-tier Policy; Sử dụng Type Hinting đầy đủ.
B. Viết mã tùy do, không tuân thủ quy ước hay schema chung.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q2. [DevSecOps] Các nguyên tắc bảo mật bất di bất dịch (Invariants) được phát hiện là gì?
A. Không sử dụng Text-to-SQL; Mọi truy vấn nhạy cảm phải gọi policy engine trước; Principal tái dựng từ HRIS mỗi request; Che mờ kết quả tool C3 trong log (`REDACTED_TOOL_OUTPUTS`); K-anonymity kết hợp complementary suppression cho số liệu tổng hợp.
B. Chỉ kiểm tra quyền ở frontend hoặc qua prompt LLM.
X. Khác (vui lòng nêu rõ)
[Answer]: A
