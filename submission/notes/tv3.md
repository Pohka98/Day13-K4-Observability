# TV3 — Vòng 3 — Root cause, fix và phòng ngừa

Challenge: `day13-k4-observability-v1` | Cohort K4 | Incident: `rag_slow` | `latency_threshold_ms`: 2000
Tổng hợp từ TV5 (metrics, `submission/notes/tv5.md`), TV4 (traces, `submission/notes/tv4.md`) và
TV2 (logs, `submission/notes/tv2.md`).

## 1. Kết luận root cause

```
Triệu chứng : latency p95 tăng từ 151ms → 2654ms (+2503ms, x17.6), 5/5 request vượt ngưỡng
              challenge 2000ms (654ms/32.7%); error rate, cost, quality, traffic không đổi.
              (nguồn: TV5 — submission/notes/tv5.md, mục 1–2)

Khoanh vùng : trace `eefb967901f7f8c37378f12f6b23f742` (session k4-challenge-s01), span `run`
              (GENERATION) = 2662ms / 2662ms (100% — Langfuse chỉ có 1 span cho toàn bộ
              LabAgent.run). Bóc theo hàm bên trong run() [app/agent.py:30-41]:
              retrieve() = 2500.7ms (94.3%), resolve_prompt() ≈ 0ms (cache), llm.generate() =
              150.4ms (5.7%, đúng bằng baseline). Toàn bộ 5 trace của challenge dao động
              2651–2662ms, không phải outlier đơn lẻ.
              (nguồn: TV4 — submission/notes/tv4.md, mục 2–3)

Bằng chứng  : log correlation_id `req-99b39249` (cùng trace ở trên):
              {"event":"request_received","correlation_id":"req-99b39249",
               "session_id":"k4-challenge-s01","feature":"monitoring", ...}
              {"event":"response_sent","correlation_id":"req-99b39249",
               "latency_ms":2662,"session_id":"k4-challenge-s01", ...}
              Baseline cùng session trong `challenge-before.jsonl`: latency_ms = 151.
              (nguồn: TV2 — submission/notes/tv2.md, mục 2–3)

Root cause  : `app/mock_rag.py:16-17` — trong retrieve():
                  if STATE["rag_slow"]:
                      time.sleep(2.5)
              Đây là một sleep cố định 2500ms, không có timeout/circuit-breaker nào bao quanh
              lệnh gọi retrieve() ở app/agent.py:32, nên toàn bộ 2500ms cộng thẳng 1:1 vào
              latency tổng của request. STATE["rag_slow"] được bật qua
              scripts/inject_incident.py → POST /incidents/rag_slow/enable (app/incidents.py).
              "Span run chậm" (kết luận của TV4) chỉ là triệu chứng tầng dưới; nguyên nhân thật
              là bước RAG retrieval không có giới hạn thời gian khi backend (giả lập) chậm.
```

Evidence tổng hợp: `submission/evidence/tv3-challenge-rootcause.png` — ảnh ghép 4 tầng
Metric → Trace → Log → Code, cho thấy cùng một con số (2662ms / req-99b39249 / trace
eefb9679...) xuất hiện nhất quán ở cả ba tầng quan sát, và dòng code gây ra nó.

## 2. Fix action

1. **Thêm timeout cho `retrieve()`** — `app/agent.py:32` (lệnh gọi `docs = retrieve(message)`
   trong `LabAgent.run`). Bọc lời gọi bằng một giới hạn thời gian cứng (ví dụ chạy trong thread
   pool với `concurrent.futures.ThreadPoolExecutor().submit(...).result(timeout=0.8)`), khi vượt
   timeout thì fallback về `["No domain document matched. Use general fallback answer."]` (docs
   rỗng đã có sẵn trong `app/mock_rag.py:22`) thay vì chờ vô thời hạn. 0.8s được chọn vì
   `llm.generate()` baseline chỉ mất ~150ms, nên 0.8s đủ dư cho truy xuất bình thường mà vẫn giữ
   tổng latency dưới ngưỡng challenge 2000ms.
2. **Giới hạn số lần retry/không retry khi timeout** — đảm bảo nhánh timeout ở trên không tự động
   thử lại `retrieve()` (retry sẽ nhân đôi latency thay vì cắt); log rõ một field mới, ví dụ
   `payload={"rag_fallback": true}` trong sự kiện `request_received`/`response_sent` tại
   `app/main.py:54-58`, để tầng log phân biệt được request nào bị fallback do timeout.
3. (Ngoài phạm vi lab, dành cho production thật) Khi `app/mock_rag.py:retrieve()` được thay bằng
   client vector store thật, đặt deadline phía client (ví dụ `timeout=` của SDK/gRPC) thay vì dựa
   vào timeout tầng ứng dụng — timeout kép giúp tránh cả trường hợp thread bị treo cứng.

## 3. Preventive measure

- **Alert `HighLatencyP95` (`config/alert_rules.yaml`) không bắt được sự cố này.** Điều kiện hiện
  tại là `p95(latency_ms) > 3000ms for 5m`, trong khi p95 thực tế của incident chỉ là 2654–2662ms —
  **thấp hơn ngưỡng alert**, dù đã vượt `latency_threshold_ms: 2000` của chính challenge tới 32%.
  Đây là khoảng trống thật: dashboard "xanh" trong khi SLA nghiệp vụ đã bị vi phạm.
  → Đề xuất: hạ ngưỡng `HighLatencyP95` xuống khớp với SLA nghiệp vụ, ví dụ tách hai mức —
  `warning` tại `p95 > 2000ms for 5m` (khớp `latency_threshold_ms` của challenge.json) và giữ
  `critical` tại `p95 > 3000ms for 5m` như hiện tại. Warning sẽ bắn ngay ở lần đo p95 = 2654ms.
- **Panel phát hiện sớm nhất: `latency` panel** (`config/dashboard.yaml`, panel `id: latency`,
  p50/p95/p99). Panel này đổi giá trị ngay ở request đầu tiên bị ảnh hưởng (151ms → ~2650ms),
  sớm hơn nhiều so với việc chờ đủ điều kiện "for 5m" của alert, và sớm hơn cả `errors`/`cost`
  panel (hai panel này không đổi trong incident `rag_slow` — xem mục 2 của TV5 — nên vô dụng cho
  đúng loại sự cố này).
- **Khoảng trống quan sát ở tầng trace (ghi nhận từ TV4):** `LabAgent.run` chỉ có một span duy
  nhất bao toàn bộ hàm, không tách được `retrieve()` / `resolve_prompt()` / `llm.generate()`
  thành span con. Vì vậy Traces hiện tại không thể tự khoanh vùng "RAG chậm" mà không đọc code —
  toàn bộ việc quy kết 94.3% về `retrieve()` ở vòng điều tra này được làm bằng đo thời gian thủ
  công, không phải từ trace. Đề xuất preventive lâu dài: thêm span con cho `retrieve()` trong
  `app/agent.py` (decorator `@observe` hoặc context manager riêng), để lần sau một alert latency
  có thể trỏ thẳng vào đúng bước RAG mà không cần đọc source code.

## 4. Trạng thái hệ thống sau điều tra

```
.venv/bin/python -m -c "disable rag_slow / tool_fail / cost_spike qua /incidents/{name}/disable"
.venv/bin/python -m pytest -q
```

- Cả 3 incident (`rag_slow`, `tool_fail`, `cost_spike`) đã được xác nhận **tắt** — `STATE` là
  in-memory theo tiến trình uvicorn nên mỗi lần khởi động lại server đều về `False`; đã gọi
  `POST /incidents/{name}/disable` cho cả 3 tên để đảm bảo tường minh, `GET /health` xác nhận
  `{"rag_slow": false, "tool_fail": false, "cost_spike": false}`.
- `pytest -q`: **35 passed**.
- Ghi chú Linux: không dùng được cổng 8000 mặc định của `scripts/inject_incident.py` vì cổng đó
  đang bị một tiến trình container khác (không thuộc repo này, user Linux khác) chiếm dụng —
  đã chạy `uvicorn app.main:app --host 127.0.0.1 --port 8010` và gọi thẳng các endpoint
  `/incidents/*/disable` qua `curl` tới cổng 8010 thay vì sửa `BASE_URL` trong script.

## Bàn giao

"Root cause: `time.sleep(2.5)` không có timeout trong `app/mock_rag.py:17` khi
`STATE['rag_slow']=True`, cộng thẳng vào latency vì `retrieve()` ở `app/agent.py:32` không bị
giới hạn thời gian. Fix: thêm timeout ~0.8s quanh `retrieve()` với fallback docs rỗng có sẵn.
Preventive: alert `HighLatencyP95` (ngưỡng 3000ms) không bắt được incident này vì p95 thực tế chỉ
2654–2662ms — cần thêm mức warning tại 2000ms khớp SLA challenge; panel `latency` là nơi phát
hiện sớm nhất. Đã tắt cả 3 incident, pytest 35 passed, hệ thống sạch cho demo. TV1 gom REPORT."
