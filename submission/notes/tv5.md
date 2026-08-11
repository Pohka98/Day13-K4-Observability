# TV5 — Vòng 3 — Tầng Metrics: xác định triệu chứng

Challenge: `day13-k4-observability-v1` | Cohort: K4 | Incident: `rag_slow` | `latency_threshold_ms`: 2000
5 query chính thức từ `config/challenge.json`, chạy qua `scripts/load_test.py --challenge`.

## 1. So sánh before / after

| Chỉ số | Before | After | Ngưỡng | Kết luận |
|---|---|---|---|---|
| Latency p50 | 151 ms | 2652 ms | — | tăng mạnh |
| Latency p95 | 151 ms | 2654 ms | ≤ 3000 ms (dashboard SLO) | vẫn dưới SLO dashboard, nhưng **vượt ngưỡng challenge 2000ms** |
| Latency p99 | 151 ms | 2654 ms | — | tăng mạnh |
| Error rate | 0.0 % (0/5) | 0.0 % (0/5) | ≤ 2 % | không đổi |
| Cost tổng | $0.011085 | $0.00975 | ≤ 2.5 USD | không đổi (giảm nhẹ, trong nhiễu) |
| Quality trung bình | 0.84 | 0.84 | ≥ 0.75 | không đổi |
| Traffic | 5 request | 5 request | — | không đổi |
| Tokens (in/out) | 175 / 704 | 175 / 615 | ≤ 50 000 | không đổi (tokens_out giảm nhẹ) |

Nguồn số liệu: `submission/evidence/challenge-before.jsonl` (before) và `data/logs.jsonl` (after, tại thời
điểm chụp), đối chiếu với snapshot `/metrics` của từng lần chạy (server được restart giữa hai lần để
`/metrics` không cộng dồn before+after).

Chi tiết latency từng request:
- Before: `[151, 151, 151, 151, 151]` ms — cực kỳ đồng nhất
- After: `[2652, 2654, 2652, 2653, 2652]` ms — cũng gần như đồng nhất, không có outlier lẻ tẻ

## 2. Trả lời 3 câu

**Chỉ số nào lệch?**
Chỉ **latency** lệch — cả p50, p95, p99 đều tăng từ 151ms lên ~2652–2654ms (tăng ~2503ms, tương đương
~17.6 lần). Toàn bộ 5/5 request đều bị chậm với mức chậm gần như bằng nhau (chênh lệch giữa các request
chỉ 1–2ms), không phải một vài outlier kéo đuôi — tức đây là một **độ trễ cộng thêm gần như cố định**
trên mọi request, không phải nhiễu tải hệ thống.

**Lệch bao nhiêu so với `latency_threshold_ms: 2000`?**
p95 sau incident = 2654ms, vượt ngưỡng challenge 2000ms là **654ms (32.7%)**. Đáng chú ý: ngay cả p50
(2652ms) cũng đã vượt ngưỡng 2000ms — nghĩa là **100% request** (không chỉ phần đuôi p95/p99) đều vi
phạm ngưỡng challenge, dù vẫn còn nằm dưới ngưỡng SLO chung của dashboard (3000ms). Đây là điểm cần nói
rõ khi demo: hai ngưỡng khác nhau, và ngưỡng challenge chặt hơn ngưỡng SLO mặc định.

**Chỉ số nào KHÔNG lệch?**
Error rate (0% cả hai lần), cost tổng (~$0.01, không đổi), quality trung bình (0.84, không đổi), traffic
(5 request cả hai lần), và tokens_in (175, không đổi). Việc error rate và quality không đổi giúp loại
hai giả thuyết: **"service chết/lỗi"** (vì response vẫn trả về 200 và đúng nội dung) và **"model trả lời
tệ hơn"** (quality_score không giảm). Cost không tăng cũng loại giả thuyết **"tốn thêm token do
retry/loop"**. Điều này thu hẹp phạm vi về đúng một hướng: có một khâu trong luồng xử lý bị **chậm đơn
thuần**, không sinh lỗi, không đổi nội dung/chất lượng, không tốn thêm tài nguyên — khớp với tên incident
`rag_slow` (nghi vấn nằm ở bước truy xuất RAG), nhưng việc xác định chính xác span nào là việc của tầng
Traces (TV4).

## 3. Evidence

- `submission/evidence/tv5-challenge-metrics.png` — panel so sánh before/after: latency percentiles với
  cả hai đường ngưỡng (challenge 2000ms và dashboard SLO 3000ms), cộng 4 panel phụ cho thấy error
  rate/cost/quality/traffic không đổi.
- `submission/evidence/challenge-before.jsonl` — log baseline (before), 5 request, 10 dòng log.
- `data/logs.jsonl` tại thời điểm chạy after — 5 request, 10 dòng log (chưa xóa, giữ cho TV4 dùng để
  điều tra trace/span).

## 4. Ghi chú vận hành cho nhóm

- Server (uvicorn) đang chạy nền, incident `rag_slow` **vẫn đang bật** — cố ý chưa tắt, vì bước 5 của
  quy trình chung ("tắt incident sau khi xong") là bước cuối cùng của **cả nhóm**, sau khi TV4 và
  TV1–TV3 đã điều tra xong tầng traces/logs. TV4 tiếp theo có thể dùng ngay `data/logs.jsonl` hiện tại
  (5 request "after") để khoanh span; nếu cần chạy lại request mới, incident vẫn đang bật nên hành vi sẽ
  nhất quán.
- `/metrics` là số cộng dồn theo tiến trình server, đã reset về 0 khi restart server giữa before/after —
  nếu server bị restart lần nữa, số `/metrics` sẽ mất, nhưng file log (`challenge-before.jsonl` và
  `data/logs.jsonl`) vẫn giữ nguyên số liệu gốc để tính lại bất cứ lúc nào.

## Bàn giao

"Triệu chứng: p95 latency tăng từ 151ms lên 2654ms, vượt ngưỡng 2000ms là 654ms (32.7%). Toàn bộ 5/5
request đều chậm gần như đều nhau (~2652–2654ms), không phải outlier lẻ tẻ. Error rate, cost, quality,
traffic đều không đổi — loại được giả thuyết lỗi/service chết/tốn token. TV4 khoanh span."
