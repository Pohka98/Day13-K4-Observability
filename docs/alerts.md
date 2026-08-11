# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: HighLatencyP95
- Severity: critical
- SLI/SLO liên quan: `latency_p95_ms` — SLO 99.5% request có p95 < 3000ms trong cửa sổ 28 ngày (`config/slo.yaml`)
- Điều kiện và thời gian duy trì: panel `latency` — p95(`latency_ms`) > 3000ms, duy trì liên tục 5 phút
- Ảnh hưởng tới người dùng: request trả lời chậm, trải nghiệm chat bị treo/lag, có nguy cơ timeout ở phía client
- Ba bước kiểm tra đầu tiên:
  1. Mở panel `latency` trên dashboard, xác nhận p95/p99 đang tăng và từ thời điểm nào
  2. Mở trace của một request chậm gần nhất trong Langfuse, xem span nào chiếm phần lớn thời gian (RAG retrieval, LLM call, hay xử lý nội bộ)
  3. Tìm log có cùng `correlation_id` với trace đó trong `data/logs.jsonl` để đọc chi tiết field (model, feature, payload) tại thời điểm chậm
- Mitigation tạm thời: bật lại/circuit-break tính năng đang chậm nếu xác định được (vd tắt RAG, dùng fallback đơn giản hơn), hoặc giảm concurrency để giảm tải backend đang nghẽn
- Owner: HaiTrieu

## Alert 2

- Tên: HighErrorRate
- Severity: critical
- SLI/SLO liên quan: `error_rate_pct` — SLO 99.0% request thành công (error rate ≤ 2%) trong cửa sổ 28 ngày
- Điều kiện và thời gian duy trì: panel `errors` — error_rate_pct = count(`request_failed`) / count(`request_received`) × 100 > 2%, duy trì liên tục 5 phút
- Ảnh hưởng tới người dùng: một tỉ lệ request nhận lỗi (HTTP 500) thay vì câu trả lời, tính năng chat coi như gián đoạn một phần
- Ba bước kiểm tra đầu tiên:
  1. Mở panel `errors`, xem breakdown theo `error_type` để biết lỗi tập trung ở loại nào
  2. Lọc log `event == "request_failed"` trong `data/logs.jsonl`, đọc `payload.detail` và `error_type` để biết nguyên nhân (vd timeout, exception nội bộ, input không hợp lệ)
  3. Đối chiếu `correlation_id` của các request lỗi với trace tương ứng để xác định span thất bại
- Mitigation tạm thời: rollback prompt/label vừa đổi gần nhất nếu lỗi mới xuất hiện sau khi đổi version, hoặc bật flag tắt tính năng đang gây lỗi trong khi chờ fix gốc
- Owner: HaiTrieu

## Alert 3

- Tên: DailyCostBudgetExceeded
- Severity: warning
- SLI/SLO liên quan: `daily_cost_usd` — SLO tổng cost trong ngày ở mức tin cậy 100% phải ≤ 2.5 USD
- Điều kiện và thời gian duy trì: panel `cost` — sum(`cost_usd`) toàn cửa sổ trong ngày > 2.5 USD (kiểm tra tại thời điểm đánh giá, không cần duy trì liên tục vì cost là tích lũy)
- Ảnh hưởng tới người dùng: không ảnh hưởng trực tiếp ngay lập tức, nhưng là dấu hiệu chi phí vận hành vượt ngân sách nhóm, có thể dẫn tới việc phải giới hạn traffic hoặc tắt tính năng nếu tiếp diễn
- Ba bước kiểm tra đầu tiên:
  1. Mở panel `cost` (theo phút) để tìm khoảng thời gian cost tăng đột biến
  2. Mở panel `tokens` cùng thời điểm — cost tăng thường đi cùng `tokens_in`/`tokens_out` tăng bất thường
  3. Lọc log `event == "response_sent"` theo `feature`/`session_id` trong khoảng đó để xác định request hoặc user nào tiêu tốn token nhiều nhất
- Mitigation tạm thời: giới hạn độ dài input/output (max tokens) cho feature đang tốn nhiều nhất, hoặc tạm giới hạn rate limit cho session/user gây spike
- Owner: HaiTrieu
