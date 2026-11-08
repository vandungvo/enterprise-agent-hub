# Alarms & Alert Thresholds

| Alarm ID | Metric Name | Threshold | Severity | Notification Channel | Action Required |
|---|---|---|---|---|---|
| **ALM-01** | `Policy Denials Spike` | > 20 lần DENIED / 10 phút từ 1 IP hoặc 1 User | CRITICAL | Slack #secops-alerts + SMS | Tạm khóa phiên, rà soát hành vi nghi ngờ tấn công injection |
| **ALM-02** | `LLM 429 Rate Limit Rate`| > 5% tổng request gặp lỗi 429 liên tục 5 phút | HIGH | Slack #ai-platform-alerts | Kiểm tra hạn mức Anthropic/Gemini, tăng tier quota hoặc bật fallback |
| **ALM-03** | `Response Latency p95` | p95 > 4.5 giây trong 15 phút | MEDIUM | Slack #ai-dev-team | Điều tra độ trễ mạng LLM API hoặc tắc nghẽn truy vấn DB |
| **ALM-04** | `Daily Token Cost Spike` | Chi phí trong ngày vượt 150% ngân sách định mức | MEDIUM | Email CFO / IT Director | Rà soát các phiên hỏi đáp bất thường, kiểm tra loop tool calls |
