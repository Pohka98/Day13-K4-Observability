# TV4 — Vòng 3 — Tầng Traces: khoanh vùng span

Challenge: `day13-k4-observability-v1` | Cohort K4 | Incident: `rag_slow` | `latency_threshold_ms`: 2000
Kế thừa kết luận metrics của TV5: p95 tăng 151ms → 2654ms, error rate/cost/quality không đổi.

## 1. Trace của challenge

Lọc `feature=monitoring`, `session_id` bắt đầu bằng `k4-challenge-s`. 5 trace ứng với 5 query:

| session_id | trace ID | latency |
| --- | --- | --- |
| `k4-challenge-s01` | `eefb967901f7f8c37378f12f6b23f742` | 2662ms |
| `k4-challenge-s02` | `047299d5f8091d0341956e9d5320e565` | 2659ms |
| `k4-challenge-s03` | `cbb9baf8936343a86a46aef582690f8d` | 2653ms |
| `k4-challenge-s04` | `2591e7528c969d28313d7b9f3c9c9f2e` | 2655ms |
| `k4-challenge-s05` | `31a195d73c7886ef3790dc2540697c19` | 2651ms |

Trace **chậm nhất**: `eefb967901f7f8c37378f12f6b23f742` (session `k4-challenge-s01`, 2662ms) — dùng để
phân tích sâu.

## 2. Waterfall và bảng span

**Giới hạn quan trọng:** trace trên Langfuse chỉ có **một span duy nhất** —
`app/agent.py:29` chỉ đặt `@observe` ở toàn bộ `LabAgent.run`, ba bước bên trong không có
span con riêng. Waterfall vì vậy không tách được `retrieve()` / `resolve_prompt()` /
`llm.generate()` như ba mũi tên mô tả trong `run()` (`app/agent.py:30-41`).

| Span (Langfuse) | Thời gian | % tổng |
| --- | --- | --- |
| `run` (GENERATION) | 2662ms | 100% |

Để vẫn trả lời được câu "span nào chiếm phần lớn thời gian" mà không sửa `app/agent.py`
(ngoài phạm vi file này), đo trực tiếp từng hàm ở mức code với cùng input, incident đang bật:

| Bước trong `run()` | Hàm | Thời gian đo | % của 2651ms |
| --- | --- | --- | --- |
| 1 | `retrieve(message)` — `app/mock_rag.py:19` | **2500.7ms** | **94.3%** |
| 2 | `resolve_prompt(...)` | ~không đáng kể (prompt cache 60s, đã fetch trước) | ~0% |
| 3 | `llm.generate(...)` — `app/mock_llm.py:26` | 150.4ms | 5.7% |
| | Tổng đo được | 2651.1ms | — |

2651.1ms đo được khớp với 2662ms của trace thật (chênh ~11ms là overhead network/framework
+ `resolve_prompt`). Đọc thẳng `app/mock_rag.py:19-20`:

```python
if STATE["rag_slow"]:
    time.sleep(2.5)
```

`retrieve()` cộng thêm đúng **2.5s (2500ms) cố định** khi `rag_slow=True` — đây là nguồn gốc
toàn bộ độ trễ.

## 3. Trả lời 3 câu

**Span nào bất thường?**
Span duy nhất trên Langfuse là `run`, 2662ms, 100% tổng thời gian — bất thường so với baseline
~151-154ms (xem mục so sánh bên dưới), tức tăng gấp **~17.5 lần**. Khi bóc theo hàm bên trong,
phần bất thường nằm gọn ở `retrieve()`: 2500.7ms / 2651.1ms tổng = **94.3%**, đúng bằng hằng số
`time.sleep(2.5)` trong `app/mock_rag.py:20`, được kích bởi `STATE["rag_slow"]`.

**Trace ID cụ thể?**
`eefb967901f7f8c37378f12f6b23f742` (chậm nhất, dùng phân tích) — kèm 4 trace còn lại của challenge
ở bảng mục 1, tất cả cùng dao động 2651-2662ms nên không phải outlier đơn lẻ.

**Các span còn lại có bình thường không?**
`llm.generate()` = 150.4ms — **đúng bằng** thời gian `generate()` lúc bình thường (baseline trace
`a52ba55ac71c87ccb0378a441285c6d3` cũng 151-154ms tổng, mà `generate()` luôn có `time.sleep(0.15)`
cố định trong `app/mock_llm.py:26` bất kể `rag_slow`). `resolve_prompt()` không đổi (prompt được
cache 60s, source vẫn `langfuse`). Chỉ một khâu — `retrieve()` — phình ra, các khâu khác giữ
nguyên. Đây là bằng chứng khoanh vùng: root cause nằm đúng ở bước RAG retrieval, khớp tên incident
`rag_slow`, không phải LLM call hay prompt fetch chậm.

## So với baseline

Vì 5 trace baseline gốc của TV5 (chạy lúc 2026-08-11T10:10Z, trước khi bật incident) **không lên
Langfuse** — có thể do máy TV5 lúc đó chưa cấu hình `LANGFUSE_*` — nên không đối chiếu trực tiếp
được trace cũ. Để có bằng chứng trace thật (không chỉ số liệu trong log), tạo lại một trace baseline
tương đương: tắt `rag_slow`, chạy đúng nội dung của `k4-challenge-s01`
(`"Explain why metrics traces and logs work together."`, feature `monitoring`), rồi bật lại
`rag_slow` ngay sau đó để không ảnh hưởng nhóm điều tra tiếp theo.

| | Trace ID | Span `run` | So với threshold 2000ms |
| --- | --- | --- | --- |
| Baseline (rag_slow tắt) | `a52ba55ac71c87ccb0378a441285c6d3` | 154ms | dưới ngưỡng |
| Challenge (rag_slow bật) | `eefb967901f7f8c37378f12f6b23f742` | 2662ms | vượt ngưỡng 662ms (33.1%) |

Baseline trace 154ms khớp với 151ms TV5 đo trong `submission/notes/tv5.md` — cùng một hệ số quy mô,
xác nhận số liệu TV5 đáng tin dù không truy lại được trace gốc của họ trên Langfuse.

## 4. Evidence

- `tv4-challenge-waterfall.png` — mở trace `eefb967901f7f8c37378f12f6b23f742`, chế độ waterfall.
  Lưu ý: vì chỉ có 1 span nên ảnh sẽ chỉ có một thanh `run` 2662ms — đúng hiện trạng, không phải
  thiếu chụp.
- `tv4-challenge-baseline-trace.png` — trace `a52ba55ac71c87ccb0378a441285c6d3` (154ms), baseline
  tương đương để so sánh cùng span `run`.

## Bàn giao

"Span `run` mất 2662ms / tổng 2662ms (100%) trong trace `eefb967901f7f8c37378f12f6b23f742` — do
Langfuse chỉ trace một span cho cả `run()`. Bóc theo hàm: `retrieve()` chiếm 2500.7ms/2651.1ms
(94.3%), khớp `time.sleep(2.5)` trong `app/mock_rag.py:20` khi `rag_slow=True`. `llm.generate()`
không đổi (150.4ms, như baseline). TV1–TV3 truy log correlation ID `req-99b39249` (trace
`eefb967901f7f8c37378f12f6b23f742`) để chứng minh nguyên nhân ở tầng log."
