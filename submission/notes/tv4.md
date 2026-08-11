# TV4 — Vòng 1 — Langfuse và Prompt versioning

## 1. Kết nối Langfuse

| Mục | Giá trị |
| --- | --- |
| Host | `https://jp.cloud.langfuse.com` (region JP) |
| Public key | `pk-lf-94f1f2f4-e676-4e42-87cc-c763b12061ab` |
| Secret key | chỉ nằm trong `.env` local, **không commit** |
| `auth_check()` | `True` |
| `/health` → `tracing_enabled` | `True` |

`.env` đã điền `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`.
Lưu ý cho cả nhóm: host là **`jp.cloud.langfuse.com`**, không phải `cloud.langfuse.com` —
dùng sai host thì auth fail và prompt rơi về `local-fallback`.

## 2. Prompt `day13-chat`

Prompt name: **`day13-chat`**, type `text`. Cả hai version đều giữ đủ 3 biến
`{{feature}}`, `{{docs}}`, `{{message}}`.

| Version | Prompt version ID | Labels | Thời điểm tạo (UTC) |
| --- | --- | --- | --- |
| v1 | `e335baee-f812-4923-88ad-47b7dd9cd645` | `baseline`, `production` | 2026-08-11T08:47:36.488Z |
| v2 | `c3d6154c-dd8f-416b-99e8-009b428ac56a` | `candidate`, `latest` | 2026-08-11T08:47:36.678Z |

**Nội dung v1**

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}
```

**Nội dung v2** — thay đổi nhỏ về format/độ dài câu trả lời:

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}

Answer in at most 3 short bullet points, then one final line starting with 'Summary:'.
```

Label `production` hiện trỏ về **v1**, nên app mặc định
(`LANGFUSE_PROMPT_LABEL=production`) chạy v1.

## 3. Tự kiểm tra

```powershell
Remove-Item data/logs.jsonl
.\.venv\Scripts\python.exe scripts/load_test.py
```

Kết quả: 10/10 request `200`, latency 154–1054ms (request đầu cao do cold start khi
fetch prompt lần đầu, các request sau dùng cache 60s).

Xác nhận prompt lấy từ Langfuse chứ không phải fallback:

```text
resolve_prompt() → source=langfuse | version=1 | label=production | fetch_error=None
```

Metadata trace mới nhất trên Langfuse (GET `/api/public/traces`):

```json
{"prompt_name": "day13-chat", "prompt_label": "production",
 "prompt_version": 1, "prompt_source": "langfuse", "doc_count": 1}
```

Trace ID mẫu:

- `737d661655ddc41ef6f77bc38bb6e794` (session `s10`)
- `0122391375b2fea5fe50158f9f77d0b0` (session `s09`)
- `0cf7e20626b05da6395ac4073373c168` (session `s08`)

Tổng số trace trong project sau load test: 50.

`prompt_source` = `langfuse`, **không phải** `local-fallback` → CP2 đã unblock.

## Ghi chú vận hành

- `prompt_source` / `prompt_version` chỉ đi vào trace metadata trên Langfuse
  (`app/agent.py`), không có trong `data/logs.jsonl` — muốn kiểm tra thì xem trace
  hoặc gọi trực tiếp `resolve_prompt()`.
- Prompt cache TTL 60s (`app/prompt_management.py`), nên sau khi đổi label trên UI
  cần chờ tới 60s hoặc restart API mới thấy hiệu lực.
- API chạy bằng venv Python 3.11: `.\.venv\Scripts\python.exe -m uvicorn app.main:app --env-file .env`.
