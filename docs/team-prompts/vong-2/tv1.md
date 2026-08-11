# TV1 — Vòng 2 — Test cho correlation ID

**Lượt push: 3/5** — chờ `"TV5 xong"`
**File sở hữu:** `tests/test_correlation_id.py` — **file mới**, chưa tồn tại

File mới thì không thể conflict với ai. Đừng sửa test có sẵn của repo.

## Việc cần làm

Viết test chứng minh middleware của bạn hoạt động đúng. Tối thiểu 3 case:

1. **Sinh ID khi client không gửi** — POST `/chat` không kèm header, response phải có header
   `x-request-id` khớp format `req-<8 hex>`.
2. **Tôn trọng ID client gửi** — POST kèm `x-request-id: req-testcase`, response phải trả về đúng
   giá trị đó, và log phải mang đúng ID đó.
3. **Không rò rỉ giữa các request** — gọi 2 request liên tiếp, 2 correlation ID phải khác nhau.
   Đây là case chứng minh `clear_contextvars()` có tác dụng.

## Gợi ý kỹ thuật

Xem `tests/test_chat_observability.py` làm mẫu — nó dùng `TestClient` và `monkeypatch.setattr` để
đổi `logging_config.LOG_PATH` sang `tmp_path`, tránh ghi đè log thật:

```python
log_path = tmp_path / "logs.jsonl"
monkeypatch.setattr(logging_config, "LOG_PATH", log_path)
```

Dùng đúng pattern này, đừng đọc `data/logs.jsonl` trong test — sẽ hỏng khi người khác chạy load test
song song.

Đọc log đã ghi:

```python
events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
```

## Tự kiểm tra

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest tests/test_correlation_id.py -v
```

Xong khi: toàn bộ suite pass (22 test cũ + test mới của bạn), và test của bạn **fail nếu cố tình bỏ
`clear_contextvars()`** — test không bắt được lỗi thì không có giá trị.

## Push

```powershell
git pull --rebase origin main
git add tests/test_correlation_id.py
git commit -m "test(logging): cover correlation ID generation and isolation"
git pull --rebase origin main
git push origin main
```

Nhắn nhóm: `"TV1 xong, commit <sha>, tới lượt TV2."`
