# TV1 — Vòng 1 — Correlation ID

**Lượt push: 1/5** (bạn đi đầu, không cần chờ ai)
**File sở hữu:** `app/middleware.py` — không đụng file nào khác

## Bối cảnh

Hiện mọi log của API đều thiếu `correlation_id`, nên không thể lần theo một request xuyên suốt
các log line. `scripts/validate_logs.py` đang trừ 50 điểm vì lỗi này (30 điểm "missing required
fields" + 20 điểm "correlation ID propagation").

## Việc cần làm

Hoàn thiện 4 khối `TODO` trong `CorrelationIdMiddleware.dispatch`:

1. **Dọn contextvars đầu mỗi request** — `clear_contextvars()`. Bỏ qua bước này thì context của
   request trước rò sang request sau, vì uvicorn tái sử dụng task.
2. **Lấy hoặc sinh correlation ID** — đọc header `x-request-id`; không có thì tự sinh theo format
   `req-<8 ký tự hex>`. Gợi ý: `uuid.uuid4().hex[:8]` (`uuid` đã import sẵn).
3. **Bind vào structlog** — `bind_contextvars(correlation_id=correlation_id)`.
4. **Trả về client** — gắn `x-request-id` và `x-response-time-ms` vào `response.headers`.
   Biến `start` đã có sẵn ở dòng 25 để tính thời gian.

## Cần hiểu để trả lời khi demo

`merge_contextvars` đã nằm đầu chuỗi processor trong `app/logging_config.py:42`. Nên chỉ cần bind
một lần ở middleware là **mọi** log line trong request đó tự có `correlation_id` — không phải
truyền tay qua từng hàm. Đây là câu hỏi rất dễ bị hỏi.

## Tự kiểm tra

```powershell
Remove-Item data/logs.jsonl
.\.venv\Scripts\python.exe scripts/load_test.py
.\.venv\Scripts\python.exe scripts/validate_logs.py
.\.venv\Scripts\python.exe -m pytest -q
```

Xong khi:

- Load test in ra ID dạng `req-xxxxxxxx`, **không phải** `MISSING`
- `Unique correlation IDs found: 10` (mỗi request một ID khác nhau)
- `[PASSED] Basic JSON schema` và `[PASSED] Correlation ID propagation`
- **Điểm đạt 80/100** (còn thiếu 20 điểm enrichment là phần của TV2)
- `pytest -q` vẫn 22 passed

Nếu `Unique correlation IDs` = 1, bạn đang sinh ID ở scope module thay vì trong `dispatch`.

## Push

```powershell
git pull --rebase origin main
git add app/middleware.py
git commit -m "feat(logging): propagate correlation ID per request"
git pull --rebase origin main
git push origin main
```

Nhắn nhóm: `"TV1 xong, commit <sha>, validate_logs 80/100, tới lượt TV2."`
