# TV2 — Vòng 2 — Test cho enrichment

**Lượt push: 4/5** — chờ `"TV1 xong"`
**File sở hữu:** `tests/test_enrichment.py` — **file mới**, chưa tồn tại

## Việc cần làm

Viết test chứng minh log đã được enrich đúng. Tối thiểu 3 case:

1. **Đủ field** — POST `/chat`, log `request_received` và `response_sent` đều phải có
   `user_id_hash`, `session_id`, `feature`, `model`, `env`.
2. **user_id được hash, không lộ thô** — gửi `user_id="student-01"`, đọc toàn bộ file log và assert
   chuỗi `"student-01"` **không xuất hiện**, còn `hash_user_id("student-01")` thì có.
   Đây là case quan trọng nhất của bạn.
3. **Giá trị đúng nguồn** — `feature` khớp giá trị gửi lên, `model` khớp `agent.model`.

## Gợi ý kỹ thuật

Theo mẫu `tests/test_chat_observability.py`:

```python
log_path = tmp_path / "logs.jsonl"
monkeypatch.setattr(logging_config, "LOG_PATH", log_path)
```

Cho case 2, assert trên toàn văn file là cách chắc nhất:

```python
raw = log_path.read_text(encoding="utf-8")
assert "student-01" not in raw
```

## Tự kiểm tra

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest tests/test_enrichment.py -v
```

Xong khi toàn bộ suite pass và test của bạn fail nếu xóa dòng `bind_contextvars` trong `app/main.py`.

Thử nghiệm ngược đó rất đáng làm một lần: sửa tạm, chạy test thấy đỏ, rồi khôi phục. Nó chứng minh
test có tác dụng thật — và là câu trả lời tốt khi bị hỏi "làm sao biết test của bạn đúng".
**Nhớ khôi phục `app/main.py` về nguyên trạng, và đừng commit thay đổi tạm đó.**

## Push

```powershell
git pull --rebase origin main
git status                                  # xác nhận CHỈ có tests/test_enrichment.py
git add tests/test_enrichment.py
git commit -m "test(logging): cover context enrichment and user_id hashing"
git pull --rebase origin main
git push origin main
```

Nhắn nhóm: `"TV2 xong, commit <sha>, tới lượt TV3."`
