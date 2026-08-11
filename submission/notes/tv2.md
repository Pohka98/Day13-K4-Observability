# TV2 — Vòng 3 — Tầng Logs: Truy vết theo correlation ID

## 1. Tìm Request Chậm Nhất
Dựa vào Trace ID `eefb967901f7f8c37378f12f6b23f742` (session: `k4-challenge-s01`) mà TV4 cung cấp, correlation ID tương ứng ở tầng log là **`req-99b39249`**.

## 2. Đối chiếu các con số (Latency)
- Correlation ID chậm nhất: `req-99b39249`
- `latency_ms` thực tế: **2662 ms**
- So với ngưỡng báo động (`latency_threshold_ms: 2000`): **Vượt 662 ms** (vi phạm SLO).
- So với lúc bình thường (file `challenge-before.jsonl`, session `k4-challenge-s01` chỉ mất **151 ms**): **Tăng đột biến ~17.6 lần**. 

Điều này hoàn toàn khớp với kết luận của TV4 (span run trên Langfuse là 2662ms). 3 tầng Metrics → Traces → Logs đã chỉ ra cùng một độ trễ ở một request cụ thể.

## 3. Log Line Bằng Chứng
Dưới đây là nguyên văn 2 dòng log (đã lọc qua correlation ID) chứng minh toàn bộ ngữ cảnh của request từ lúc nhận đến lúc trả về:

```json
{"service": "api", "payload": {"message_preview": "Explain why metrics traces and logs work together."}, "event": "request_received", "feature": "monitoring", "session_id": "k4-challenge-s01", "env": "dev", "model": "claude-sonnet-4-5", "user_id_hash": "f00ba60b3772", "correlation_id": "req-99b39249", "level": "info", "ts": "2026-08-11T10:30:15.632496Z"}
{"service": "api", "latency_ms": 2662, "tokens_in": 35, "tokens_out": 115, "cost_usd": 0.00183, "quality_score": 0.8, "payload": {"answer_preview": "Starter answer. Teams should improve this output logic and add better quality ch..."}, "event": "response_sent", "feature": "monitoring", "session_id": "k4-challenge-s01", "env": "dev", "model": "claude-sonnet-4-5", "user_id_hash": "f00ba60b3772", "correlation_id": "req-99b39249", "level": "info", "ts": "2026-08-11T10:30:18.294496Z"}
```
