# TV2 — Vòng 1 — Log enrichment

**Lượt push: 2/5** — chờ tin nhắn `"TV1 xong"` rồi mới bắt đầu
**File sở hữu:** `app/main.py` — không đụng file nào khác

## Bối cảnh

Log API hiện chỉ có `service`, `event`, `payload`. Thiếu ngữ cảnh nghiệp vụ nên không thể lọc log
theo user, theo feature hay theo model khi điều tra sự cố. `validate_logs.py` trừ 20 điểm mục
"Log enrichment".

## Việc cần làm

Hoàn thiện `TODO` ở `app/main.py:47`, trong hàm `chat()`, **đặt trước** lời gọi
`log.info("request_received")` ở dòng 50.

Bind 5 field vào contextvars:

| Field | Lấy từ đâu |
|---|---|
| `user_id_hash` | `hash_user_id(body.user_id)` — đã import sẵn dòng 14 |
| `session_id` | `body.session_id` |
| `feature` | `body.feature` |
| `model` | `agent.model` (= `"claude-sonnet-4-5"`, xem `app/agent.py:25`) |
| `env` | `os.getenv("APP_ENV", "dev")` |

**Tuyệt đối không log `body.user_id` thô** — phải hash. Đây là yêu cầu PII, log user ID thật là mất
điểm và vi phạm `RULES.md`.

Validator đòi đúng 4 field đầu trên record có `service == "api"`; `env` là yêu cầu thêm của
`CHECKPOINTS.md`.

## Cần hiểu để trả lời khi demo

Chỉ cần bind **một lần** ở đầu `chat()` là phủ được cả ba log line: `request_received`,
`response_sent` và `request_failed` — vì cả ba cùng nằm trong một request, dùng chung contextvars
mà TV1 đã dọn sạch ở middleware.

Vì sao hash user_id thay vì bỏ hẳn? Vì vẫn cần nhóm log theo user để điều tra, nhưng không lộ danh
tính. `hash_user_id` dùng SHA-256 cắt 12 ký tự (`app/pii.py:27`).

## Tự kiểm tra

```powershell
Remove-Item data/logs.jsonl
.\.venv\Scripts\python.exe scripts/load_test.py
.\.venv\Scripts\python.exe scripts/validate_logs.py
.\.venv\Scripts\python.exe -m pytest -q
```

Xong khi:

- `Records with missing enrichment (context): 0`
- `[PASSED] Log enrichment`
- **Điểm đạt 100/100**
- `pytest -q` vẫn 22 passed

Mở `data/logs.jsonl` xem một dòng: phải thấy đủ `correlation_id`, `user_id_hash`, `session_id`,
`feature`, `model`, `env`. Nếu điểm vẫn 80, khả năng cao bạn bind **sau** `log.info` đầu tiên.

## Push

```powershell
git pull --rebase origin main
git add app/main.py
git commit -m "feat(logging): enrich request logs with business context"
git pull --rebase origin main
git push origin main
```

Nhắn nhóm: `"TV2 xong, commit <sha>, validate_logs 100/100, tới lượt TV3."`
