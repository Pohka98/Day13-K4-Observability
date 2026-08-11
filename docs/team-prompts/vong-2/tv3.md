# TV3 — Vòng 2 — Test PII và bằng chứng redaction

**Lượt push: 5/5** — chờ `"TV2 xong"`
**File sở hữu:** `tests/test_pii_extended.py` (**file mới**), `submission/evidence/tv3-*.png`

Đừng sửa `tests/test_pii.py` có sẵn — tạo file mới.

## Việc cần làm

### 1. Test cho pattern mở rộng

Tối thiểu 3 case:

1. **Pattern mới bạn thêm ở vòng 1** — ví dụ hộ chiếu `C1234567` phải bị che.
2. **Processor thật sự chặn ghi ra file** — POST `/chat` với message chứa email + số điện thoại +
   số thẻ, rồi assert file log **không** chứa nguyên văn các giá trị đó. Đây là case chứng minh
   `scrub_event` được đăng ký đúng vị trí trong chuỗi processor, không chỉ test hàm rời.
3. **Không che nhầm** — chuỗi vô hại (ví dụ `"version 4111 of the doc"` hoặc một số có 4 chữ số bình
   thường) không bị redact. False positive cũng là lỗi.

Dùng `monkeypatch.setattr(logging_config, "LOG_PATH", tmp_path / "logs.jsonl")` như
`tests/test_chat_observability.py`.

### 2. Evidence redaction

`SUBMISSION.md` đòi "log chứng minh PII đã được redact". Chạy load test rồi chụp
`tv3-pii-redacted.png` — một dòng log thấy rõ `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`.

Chụp thêm `tv3-validate-logs.png`: kết quả cuối `validate_logs.py` với `Potential PII leaks
detected: 0` và điểm 100/100.

## Tự kiểm tra

```powershell
Remove-Item data/logs.jsonl
.\.venv\Scripts\python.exe scripts/load_test.py
.\.venv\Scripts\python.exe scripts/validate_logs.py
.\.venv\Scripts\python.exe -m pytest -q
```

Một phép thử đáng làm: tạm dời `scrub_event` xuống **sau** `JsonlFileProcessor()` trong
`app/logging_config.py`, chạy lại — PII sẽ hiện nguyên văn trong file log. Đó là bằng chứng trực
tiếp cho câu hỏi "vì sao thứ tự processor quan trọng". **Nhớ khôi phục lại và đừng commit.**

## Push

```powershell
git pull --rebase origin main
git status                                  # xác nhận app/logging_config.py KHÔNG bị sửa
git add tests/test_pii_extended.py submission/evidence/tv3-*.png
git commit -m "test(pii): cover extended patterns and end-to-end scrubbing"
git pull --rebase origin main
git push origin main
```

Nhắn nhóm: `"TV3 xong, commit <sha>, hết vòng 2."`
