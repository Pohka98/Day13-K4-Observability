# TV2 — Vòng 3 — Tầng Logs: truy vết theo correlation ID

**Lượt push: 3/5** — chờ `"TV4 xong"` và trace ID từ TV4
**File sở hữu:** `submission/notes/tv2.md`

Đây là lúc phần enrichment bạn làm ở vòng 1 phát huy tác dụng — không có `correlation_id` và
`feature` thì bước này không làm được.

## Việc cần làm

### 1. Lọc log của challenge

`feature` của challenge là `monitoring`, `session_id` dạng `k4-challenge-s01`..`s05`.

```powershell
Get-Content data/logs.jsonl | Select-String '"feature": "monitoring"'
```

### 2. Bám theo request chậm nhất

Từ trace TV4 chỉ ra, tìm đúng request tương ứng rồi lấy `correlation_id` của nó. Lọc toàn bộ log
line cùng ID đó:

```powershell
Get-Content data/logs.jsonl | Select-String 'req-xxxxxxxx'
```

Bạn phải thấy cả `request_received` và `response_sent` của cùng một request — đây chính là điều
correlation ID sinh ra để làm. Ghi lại `latency_ms` trong `response_sent`.

### 3. Đối chiếu log với trace

Số `latency_ms` trong log có khớp thời gian trace TV4 đo không? Nếu khớp, bạn đã nối được ba tầng
Metrics → Traces → Logs thành một chuỗi bằng chứng liền mạch. Đó chính là thứ `RUBRIC.md` A2 chấm.

### 4. Chốt các con số

- Correlation ID của request chậm nhất
- `latency_ms` của nó, so với `latency_threshold_ms: 2000`
- So với `latency_ms` của cùng feature trong `challenge-before.jsonl`

### 5. Ghi `submission/notes/tv2.md`

Dán **nguyên văn** 2–3 log line liên quan (JSON đầy đủ) — trích dẫn cụ thể có giá trị hơn mô tả.

## Cần hiểu để trả lời khi demo

Vì sao phải có correlation ID mới điều tra được? Không có nó, 10 request đan xen trong cùng file log
sẽ không phân biệt được log line nào thuộc request nào — nhất là khi chạy concurrency > 1.

## Push

```powershell
git pull --rebase origin main
git add submission/notes/tv2.md
git commit -m "docs(challenge): trace slow request through correlated log lines"
git pull --rebase origin main
git push origin main
```

Nhắn: `"TV2 xong, commit <sha>, tới lượt TV3."`
