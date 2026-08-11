# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: **K4-C4-2** (theo tên repository)
- Repository URL: https://github.com/Pohka98/Day13-K4-Observability
- Commit SHA trước khi tổng hợp report: `070e51c7`.
- Commit SHA nộp bài: dùng `HEAD` của nhánh `main` được ghi trên Codelabs sau khi push report này
  (một commit không thể tự chứa trước SHA của chính nó).
- Thành viên và vai trò:
  - **Nguyễn Xuân Hải - 2A202602022 — TV1:** correlation ID, test isolation/propagation, tổng hợp report.
  - **Vũ Bảo Khánh - 2A202601122 — TV2:** log enrichment, user ID hashing, truy vết challenge theo log.
  - **Trần Minh Quân - 2A202601768 — TV3:** PII redaction/test, kết luận root cause và biện pháp phòng ngừa.
  - **Võ Hồ Nhật Nam - 2A202601700 — TV4:** Langfuse, prompt versioning/rollback, trace investigation.
  - **Phạm Đức Hải Triều - 2A202601980 — TV5:** SLO/alerts, dashboard và phân tích metrics.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: **100/100** trên 10 request mẫu sạch; 21 record, 10 correlation ID
  duy nhất, không thiếu required/enrichment field. Evidence: [`evidence/tv3-validate-logs.png`](evidence/tv3-validate-logs.png).
- Tổng số traces: **ít nhất 56 trace đã được ghi nhận** — TV4 ghi nhận 50 trace sau load test,
  sau đó có thêm 5 challenge trace và 1 baseline trace tương đương; vượt yêu cầu tối thiểu 10.
- Số PII leak còn lại: **0** theo validator và kiểm tra end-to-end.
- Dashboard: [`evidence/tv5-dashboard-full.png`](evidence/tv5-dashboard-full.png), nguồn chuẩn
  `data/logs.jsonl`, time range 60 phút, refresh 30 giây.
- Public tests: **35 passed**, 2 deprecation warnings của FastAPI `on_event`, không có test fail.

## 3. Logging và tracing

- Correlation ID: middleware sinh `req-<8 hex>` hoặc giữ `x-request-id` từ client, bind vào
  Structlog và trả lại qua response header. Trong challenge, `request_received` và `response_sent`
  cùng mang `req-99b39249`; xem [`notes/tv2.md`](notes/tv2.md) và
  [`evidence/tv3-challenge-rootcause.png`](evidence/tv3-challenge-rootcause.png).
- Log enrichment: mọi API log có `user_id_hash`, `session_id`, `feature`, `model`, `env`; không ghi
  raw `user_id`.
- PII redaction: processor chạy trước `JsonlFileProcessor`, che email, số điện thoại Việt Nam,
  CCCD, thẻ tín dụng, hộ chiếu và mẫu địa chỉ. Evidence:
  [`evidence/tv3-pii-redacted.png`](evidence/tv3-pii-redacted.png).
- Langfuse trace list: [`evidence/Log-trace.png`](evidence/Log-trace.png).
- Span đáng chú ý: trace challenge `eefb967901f7f8c37378f12f6b23f742` có span duy nhất `run`
  dài **2662ms**, chiếm 100% trace. Đo từng hàm cho thấy `retrieve()` chiếm 2500.7ms/2651.1ms
  (94.3%), `llm.generate()` 150.4ms (5.7%). Giới hạn hiện tại: starter code chưa instrument
  child span riêng cho retrieval/prompt/LLM, vì vậy waterfall chỉ có một thanh `run`.

## 4. Prompt versioning

- Prompt name: `day13-chat`, loại text; giữ đủ biến `{{feature}}`, `{{docs}}`, `{{message}}`.
- Version 1: ID `e335baee-f812-4923-88ad-47b7dd9cd645`, labels `baseline`, `production` sau rollback.
- Version 2: ID `c3d6154c-dd8f-416b-99e8-009b428ac56a`, labels `candidate`, `latest`.
- Trace cùng input theo từng label:
  - Baseline/v1: `5848eca21d2f951f11bf3bcbcb05d0d4`.
  - Candidate/v2: `81e54141b5abd9712464434af07810ca`.
- Promote và rollback `production`:
  - Promote sang v2: trace `70459a4e52f18fda264cfdf85893bb88`.
  - Rollback về v1: trace `358ead05f83b87c0a77f8db4d537f005`.
- Evidence hai version: [`evidence/Prompts.png`](evidence/Prompts.png). Việc đổi label chỉ dời
  con trỏ `production`, không cần deploy lại code.

## 5. Dashboard, SLO và alerts

- `validate_dashboard.py`: **HỢP LỆ 6/6 panel**. Evidence:
  [`evidence/tv5-validate-dashboard.png`](evidence/tv5-validate-dashboard.png).
- Dashboard đủ latency, traffic, errors, cost, tokens, quality:
  [`evidence/tv5-dashboard-full.png`](evidence/tv5-dashboard-full.png).
- SLO line latency:
  [`evidence/tv5-dashboard-latency-slo.png`](evidence/tv5-dashboard-latency-slo.png).
- SLO chính: 99.5% request trong cửa sổ rolling 28 ngày có P95 latency không vượt `3000ms`.
  Chọn P95 thay mean vì mean che tail latency; P95 vẫn ít nhạy với một outlier đơn lẻ hơn P99/max.
  Các SLO còn lại: error rate ≤2%, daily cost ≤2.5 USD, quality trung bình ≥0.75.
- Alert rules: `HighLatencyP95`, `HighErrorRate`, `DailyCostBudgetExceeded` tại
  [`../config/alert_rules.yaml`](../config/alert_rules.yaml). Runbook có bước kiểm tra,
  mitigation và owner tại [`../docs/alerts.md`](../docs/alerts.md).

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1`; incident `rag_slow`; feature `monitoring`;
  ngưỡng challenge `2000ms`.
- Metrics: P95 tăng từ **151ms lên 2654ms** (+2503ms, khoảng 17.6 lần), vượt ngưỡng challenge
  654ms/32.7%. Cả 5/5 request bị ảnh hưởng; error rate, cost, quality và traffic không đổi.
  Evidence: [`evidence/tv5-challenge-metrics.png`](evidence/tv5-challenge-metrics.png).
- Trace chậm nhất: `eefb967901f7f8c37378f12f6b23f742`, session `k4-challenge-s01`, tổng 2662ms.
  Baseline tương đương: `a52ba55ac71c87ccb0378a441285c6d3`, 154ms.
- Log/correlation ID: `req-99b39249`; hai event `request_received` và `response_sent` cùng ID,
  log response ghi `latency_ms=2662`. Chi tiết: [`notes/tv2.md`](notes/tv2.md).
- Root cause: `app/mock_rag.py` gọi `time.sleep(2.5)` khi `STATE["rag_slow"]` bật; lời gọi
  `retrieve()` trong `LabAgent.run()` không có timeout/circuit breaker nên toàn bộ 2.5 giây cộng
  trực tiếp vào request latency. Evidence tổng hợp:
  [`evidence/tv3-challenge-rootcause.png`](evidence/tv3-challenge-rootcause.png).
- Fix action: đặt deadline khoảng 0.8 giây quanh retrieval, fallback sang tài liệu mặc định khi
  timeout, không retry trong deadline và log rõ `rag_fallback=true`. Với vector store thật, đặt
  thêm timeout ở client SDK/gRPC.
- Preventive measure: thêm mức warning P95 >2000ms trong 5 phút để khớp SLA challenge, giữ critical
  >3000ms; bổ sung child span `retrieve`, `resolve_prompt`, `llm.generate`; theo dõi panel latency
  đầu tiên khi alert bắn.
- Sau điều tra: cả ba incident đã tắt; `/health` trả `rag_slow=false`, `tool_fail=false`,
  `cost_spike=false`.

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| HaiNguyenXuan3124 (TV1) | Correlation ID middleware, test isolation/propagation, report cuối | [`1c2e335`](https://github.com/Pohka98/Day13-K4-Observability/commit/1c2e335), [`27adf56`](https://github.com/Pohka98/Day13-K4-Observability/commit/27adf56) | Contextvars, correlation ID và cách nối request với log |
| Khanh Vu (TV2) | Log enrichment, hashing, correlated challenge logs | [`44f7fef`](https://github.com/Pohka98/Day13-K4-Observability/commit/44f7fef), [`2f60907`](https://github.com/Pohka98/Day13-K4-Observability/commit/2f60907), [`828d984`](https://github.com/Pohka98/Day13-K4-Observability/commit/828d984) | Metadata nghiệp vụ và truy vết log theo correlation ID |
| mihhquan (TV3) | PII processor/pattern, test end-to-end, root cause/fix/preventive | [`d339e20`](https://github.com/Pohka98/Day13-K4-Observability/commit/d339e20), [`b88801f`](https://github.com/Pohka98/Day13-K4-Observability/commit/b88801f), [`070e51c`](https://github.com/Pohka98/Day13-K4-Observability/commit/070e51c) | Thứ tự processor, tránh false positive và kết luận bằng evidence |
| Võ Hồ Nhật Nam (TV4) | Langfuse, prompt v1/v2, rollback, trace investigation | [`48a62ab`](https://github.com/Pohka98/Day13-K4-Observability/commit/48a62ab), [`45f3c8a`](https://github.com/Pohka98/Day13-K4-Observability/commit/45f3c8a), [`0d9362a`](https://github.com/Pohka98/Day13-K4-Observability/commit/0d9362a) | Version bất biến, label là con trỏ và giới hạn trace một span |
| Haitriu (TV5) | SLO/alerts, dashboard/runbook, metrics before/after | [`e0374b0`](https://github.com/Pohka98/Day13-K4-Observability/commit/e0374b0), [`bfdf004`](https://github.com/Pohka98/Day13-K4-Observability/commit/bfdf004), [`e174796`](https://github.com/Pohka98/Day13-K4-Observability/commit/e174796) | P95, symptom-based alert và thu hẹp sự cố bằng metrics |
