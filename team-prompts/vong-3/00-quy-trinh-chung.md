# Vòng 3 — Quy trình chung (cả nhóm đọc trước)

Phần này **cả 5 người làm chung tại một máy hoặc share screen**, trước khi ai đó viết notes riêng.
Điều tra là hoạt động tập thể; chỉ phần ghi chép mới chia theo người.

## Thông tin challenge (đã release)

Đọc từ `config/challenge.json` — **tuyệt đối không sửa file này**, `RULES.md` cấm và
`SUBMISSION.md` coi đó là bài không hợp lệ.

| Trường | Giá trị |
|---|---|
| `challenge_id` | `day13-k4-observability-v1` |
| `cohort` | K4 |
| `incident` | `rag_slow` |
| `affected_feature` | `monitoring` |
| `latency_threshold_ms` | 2000 |
| Số query | 5 |

## Trình tự chạy

**Bước 1 — Lấy baseline sạch trước khi bật incident.** Bỏ qua bước này là mất khả năng so
before/after, và không chứng minh được incident thực sự gây ra thay đổi.

```powershell
Remove-Item data/logs.jsonl
.\.venv\Scripts\python.exe scripts/load_test.py --challenge
```

Ghi lại p95 latency lúc bình thường. Copy log ra chỗ khác để giữ:

```powershell
Copy-Item data/logs.jsonl submission/evidence/challenge-before.jsonl
```

**Bước 2 — Bật incident.** Chạy không kèm tham số để script tự đọc `challenge.json`:

```powershell
.\.venv\Scripts\python.exe scripts/inject_incident.py
```

Xác nhận: `/health` phải trả `"rag_slow": true`.

**Bước 3 — Chạy input chính thức.**

```powershell
Remove-Item data/logs.jsonl
.\.venv\Scripts\python.exe scripts/load_test.py --challenge
```

**Bước 4 — Điều tra theo luồng Metrics → Traces → Logs.** Đúng thứ tự, đừng nhảy cóc — `RUBRIC.md`
A2 chấm việc bạn *chứng minh được luồng này*, không chỉ chấm kết luận đúng.

| Tầng | Ai dẫn | Câu hỏi trả lời |
|---|---|---|
| Metrics | TV5 | Triệu chứng là gì? Chỉ số nào lệch, lệch bao nhiêu so với baseline? |
| Traces | TV4 | Span nào chậm bất thường? Chiếm bao nhiêu % tổng thời gian? |
| Logs | TV1–TV3 | Correlation ID nào? Log line nào chứng minh nguyên nhân? |

**Bước 5 — Tắt incident sau khi xong.**

```powershell
.\.venv\Scripts\python.exe scripts/inject_incident.py --disable
```

## Luật bằng chứng

`RULES.md`: *"Mọi nhận định về incident phải đi kèm trace ID, log line hoặc metric cụ thể. Evidence
không thể kiểm chứng sẽ không được tính."*

Nghĩa là câu "RAG bị chậm" không có điểm. Câu "span `retrieve` mất 2.4s / tổng 2.6s trong trace
`abc123`, xem log correlation ID `req-4f2a91bc`" mới có điểm.

Ngưỡng `latency_threshold_ms: 2000` là mốc đối chiếu — nói rõ vượt bao nhiêu.

## Thứ tự push vòng 3

1. TV5 → 2. TV4 → 3. TV2 → 4. TV3 → 5. TV1 (notes + gom `REPORT.md`)

Mỗi người chỉ ghi vào `submission/notes/tv<N>.md` của mình. **Không ai đụng `REPORT.md`** ngoài TV1
ở lượt cuối.
