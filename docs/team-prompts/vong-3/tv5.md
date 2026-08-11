# TV5 — Vòng 3 — Tầng Metrics: xác định triệu chứng

**Lượt push: 1/5**
**File sở hữu:** `submission/notes/tv5.md`, `submission/evidence/tv5-challenge-*.png`

Đọc `00-quy-trinh-chung.md` trước. Bạn dẫn **bước đầu tiên** của cuộc điều tra — cả nhóm chờ kết
luận của bạn để biết đào tiếp chỗ nào.

## Việc cần làm

### 1. So sánh before / after

Bạn đã có `submission/evidence/challenge-before.jsonl` (baseline) và `data/logs.jsonl` (sau khi bật
incident). Với cùng 5 query của challenge, so:

| Chỉ số | Before | After | Ngưỡng |
|---|---|---|---|
| Latency p50 / p95 / p99 | | | p95 ≤ 3000 ms |
| Error rate | | | ≤ 2 % |
| Cost tổng | | | ≤ 2.5 USD |
| Quality trung bình | | | ≥ 0.75 |
| Traffic | | | — |

Xem thêm endpoint `/metrics` để lấy số tổng hợp trực tiếp.

### 2. Trả lời chính xác 3 câu

- **Chỉ số nào lệch?** Nêu tên chỉ số, con số before và after.
- **Lệch bao nhiêu so với `latency_threshold_ms: 2000`?**
- **Chỉ số nào KHÔNG lệch?** Câu này quan trọng ngang câu trên — nó thu hẹp phạm vi. Ví dụ nếu error
  rate không đổi thì loại được giả thuyết "service chết".

### 3. Chụp evidence

`tv5-challenge-metrics.png` — dashboard panel cho thấy rõ độ lệch so với đường SLO.

### 4. Ghi `submission/notes/tv5.md`

Số liệu before/after, chỉ số lệch, chỉ số không lệch, đường dẫn ảnh. Đây là nguyên liệu cho
`REPORT.md` mục 5 và mục 6 ("Triệu chứng từ metrics").

## Bàn giao

Nhắn nhóm kết luận cụ thể, ví dụ:
`"Triệu chứng: p95 latency tăng từ Xms lên Yms, vượt ngưỡng 2000ms. Error rate không đổi. TV4 khoanh span."`

Không nói chung chung kiểu "hệ thống chậm" — TV4 cần con số để biết tìm span dài bao nhiêu.

## Push

```powershell
git pull --rebase origin main
git add submission/notes/tv5.md submission/evidence/tv5-challenge-*.png
git commit -m "docs(challenge): record metric symptoms and before/after comparison"
git pull --rebase origin main
git push origin main
```

Nhắn: `"TV5 xong, commit <sha>, tới lượt TV4."`
