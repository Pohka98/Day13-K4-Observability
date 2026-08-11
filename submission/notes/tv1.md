# TV1 — Correlation ID, kiểm thử và tổng hợp bài nộp

## 1. Phần việc đã thực hiện

### Vòng 1 — Correlation ID

Hoàn thiện `CorrelationIdMiddleware` trong `app/middleware.py`:

- Xóa context cũ bằng `clear_contextvars()` ở đầu mỗi request.
- Tôn trọng header `x-request-id` do client gửi; nếu thiếu thì sinh ID dạng `req-<8 hex>`.
- Bind `correlation_id` vào Structlog contextvars để mọi log trong request tự nhận cùng ID.
- Trả `x-request-id` và `x-response-time-ms` trong response headers.

Commit: [`1c2e335`](https://github.com/Pohka98/Day13-K4-Observability/commit/1c2e335)

### Vòng 2 — Test correlation ID

Thêm `tests/test_correlation_id.py` với 5 kiểm tra:

1. Sinh ID đúng format khi client không gửi header.
2. Giữ nguyên ID do client cung cấp và ghi đúng ID vào log.
3. Hai request liên tiếp có hai ID khác nhau.
4. Context của request chat không rò sang request control tiếp theo.
5. `clear_contextvars()` được gọi trước `bind_contextvars()`.

Commit: [`27adf56`](https://github.com/Pohka98/Day13-K4-Observability/commit/27adf56)

## 2. Đóng góp điều tra challenge

TV1 đối chiếu việc propagation của correlation ID trong chuỗi bằng chứng do TV2–TV4 bàn giao.
Request chậm nhất có:

- Trace ID: `eefb967901f7f8c37378f12f6b23f742`
- Session: `k4-challenge-s01`
- Correlation ID: `req-99b39249`
- Log `request_received` và `response_sent` cùng mang `req-99b39249`.
- Latency trong log: `2662ms`, khớp tổng thời gian trace `2662ms`.

Correlation ID là khóa nối trace/request với các log line khi nhiều request được xử lý xen kẽ.
Evidence tổng hợp: `../evidence/tv3-challenge-rootcause.png`.

## 3. Kiểm tra cuối

- `pytest -q`: **35 passed**.
- `validate_logs.py` trên 10 request mẫu sạch: **100/100**, 10 correlation ID duy nhất, 0 PII leak.
- `validate_dashboard.py`: **HỢP LỆ 6/6 panel**.
- `/health`: cả `rag_slow`, `tool_fail`, `cost_spike` đều `false`.
- `config/challenge.json`: chỉ có commit release gốc `5ba6472`, không bị sửa.
- Không có secret thật trong file tracked; các chuỗi `pk-lf-...`/`sk-lf-...` còn lại chỉ là placeholder tài liệu.

## 4. Điều đã học

- Correlation ID khác trace ID: correlation ID là khóa ứng dụng truyền qua HTTP/log; trace ID là
  định danh của hệ thống tracing. Hai loại ID cần được liên kết bằng metadata/evidence.
- Contextvars phải được xóa trước khi bind request mới để tránh rò metadata giữa các request.
- Validator phải chạy trên log sạch; log append từ process/code cũ có thể làm sai kết quả dù code
  hiện tại đã đúng.
- Một trace chỉ có span tổng `run` chưa đủ để khoanh vùng tự động; production cần span con cho
  retrieval, prompt resolution và LLM generation.

