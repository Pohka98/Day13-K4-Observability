# TV4 — Vòng 1 — Langfuse và Prompt versioning

## 1. Kết nối Langfuse

| Mục | Giá trị |
| --- | --- |
| Host | `https://jp.cloud.langfuse.com` (region JP) |
| Public key | `*****` |
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

---

# Vòng 2 — Traces và bằng chứng rollback

Project Langfuse: `my-app`, id `cmsobk286001ead0ihy6md6bv`, region JP.
Base URL: `https://jp.cloud.langfuse.com/project/cmsobk286001ead0ihy6md6bv`

## 1. Sinh traces

```powershell
Remove-Item data/logs.jsonl
.\.venv\Scripts\python.exe scripts/load_test.py
```

10/10 request `200`, latency 155–181ms. 10 trace mới trên Langfuse.

Evidence: `../evidence/tv4-trace-list.png`

## 2. Hai label — hai trace

Cùng một input cho cả hai lần chạy:

```text
What is your refund policy for enterprise customers?
```

Mỗi lần đổi `LANGFUSE_PROMPT_LABEL` trong `.env` đều **restart API** (prompt được cache
60s trong process, không restart thì vẫn chạy label cũ).

| Label | Trace ID | prompt_version | prompt_source | session_id |
| --- | --- | --- | --- | --- |
| `baseline` | `5848eca21d2f951f11bf3bcbcb05d0d4` | 1 | `langfuse` | `tv4-v2-baseline` |
| `candidate` | `81e54141b5abd9712464434af07810ca` | 2 | `langfuse` | `tv4-v2-candidate` |

Cùng input, khác label → khác `prompt_version`. Đây là bằng chứng truy xuất được một
câu trả lời đến từ prompt version nào.

Evidence: `../evidence/tv4-prompt-versions.png`, `../evidence/tv4-trace-baseline.png`,
`../evidence/tv4-trace-candidate.png`

## 3. Đổi label và rollback

Thao tác qua Langfuse API `PATCH /api/public/v2/prompts/day13-chat/versions/{version}`
với `newLabels`. Không deploy lại code, không sửa `.env` (vẫn giữ
`LANGFUSE_PROMPT_LABEL=production`).

**Bước 1 — chuyển `production` sang v2:**

```text
v1  e335baee-f812-4923-88ad-47b7dd9cd645  labels: [baseline]
v2  c3d6154c-dd8f-416b-99e8-009b428ac56a  labels: [candidate, production, latest]
```

Request sau khi đổi → trace `70459a4e52f18fda264cfdf85893bb88`
(`prompt_label=production`, `prompt_version=2`).

**Bước 2 — rollback `production` về v1:**

```text
v1  e335baee-f812-4923-88ad-47b7dd9cd645  labels: [baseline, production]
v2  c3d6154c-dd8f-416b-99e8-009b428ac56a  labels: [candidate, latest]
```

Request sau rollback → trace `358ead05f83b87c0a77f8db4d537f005`
(`prompt_label=production`, `prompt_version=1`). Rollback có hiệu lực.

| Thời điểm | Trace ID | production trỏ về |
| --- | --- | --- |
| Sau khi promote | `70459a4e52f18fda264cfdf85893bb88` | v2 |
| Sau khi rollback | `358ead05f83b87c0a77f8db4d537f005` | v1 |

Evidence: `../evidence/tv4-rollback-before.png`, `../evidence/tv4-rollback-after.png`

## 4. Trace waterfall

Trace dùng để chụp: `70459a4e52f18fda264cfdf85893bb88`, tổng latency **568ms**.

| Span | Type | Thời gian | % tổng |
| --- | --- | --- | --- |
| `run` | GENERATION | 568ms | 100% |

**Giới hạn hiện tại:** trace chỉ có **một span**. Starter code chỉ đặt `@observe` ở
`LabAgent.run` (`app/agent.py:29`); ba bước bên trong — `retrieve(message)`,
`resolve_prompt(...)`, `llm.generate(...)` — không có span riêng nên waterfall không
tách được thời gian từng bước.

Span đáng chú ý (cho `REPORT.md` mục 3): `run` — hiện gộp cả retrieval, fetch prompt và
LLM call vào một khối 568ms. Chính vì gộp nên không khoanh vùng được bước nào chậm; muốn
trả lời câu hỏi đó phải instrument thêm span con cho 3 bước trên.

Evidence: `../evidence/tv4-waterfall.png`

## Trả lời khi demo

- **Vì sao cần prompt versioning?** Trace ghi lại `prompt_version` của từng request, nên
  khi có câu trả lời tệ là truy được ngay nó sinh ra từ version nào — ví dụ trace
  `81e54141b5abd9712464434af07810ca` là v2, `5848eca21d2f951f11bf3bcbcb05d0d4` là v1.
  Rollback chỉ là dời label, không cần deploy lại code.
- **`version` vs `label`:** version là bản bất biến (v1 `e335baee-...`, v2 `c3d6154c-...`,
  nội dung không đổi được). Label là con trỏ trỏ vào một version — `production` trong lab
  này đã đi v1 → v2 → v1 mà bản thân hai version không hề thay đổi. Rollback = dời con trỏ.
- **`prompt_source=local-fallback` nghĩa là gì?** App không lấy được prompt managed
  (sai key/host, sai prompt name/label, Langfuse timeout) và đang chạy template local
  trong `app/prompt_management.py`. App ghi rõ `local-fallback` thay vì giả vờ đã fetch
  được, vì nếu ghi `langfuse` thì `prompt_version` trong trace sẽ là số giả — mọi kết luận
  về "version nào gây lỗi" sau đó đều sai. Thà mất tính năng chứ không làm hỏng evidence.
