# TV3 — Vòng 1 — PII redaction

**Lượt push: 3/5** — chờ tin nhắn `"TV2 xong"`
**File sở hữu:** `app/pii.py`, `app/logging_config.py`

## Bối cảnh

Đọc kỹ chỗ này, phần của bạn dễ bị hiểu nhầm nhất:

`validate_logs.py` **đang báo PII pass sẵn** từ baseline, và sẽ vẫn pass dù bạn không làm gì. Lý do:
`summarize_text()` đã che PII ở trường `message_preview`, mà load test chỉ sinh PII ở đúng chỗ đó.

Nhưng script chỉ dò 4 regex cố định. `RUBRIC.md` mục A1 chấm **chất lượng redaction thật**, không
chấm con số script in ra. Việc của bạn là làm cho log sạch thật, không phải làm cho script xanh.

## Việc cần làm

### 1. Bật processor — `app/logging_config.py:45`

Bỏ comment dòng `scrub_event`.

**Vị trí là điều then chốt:** nó phải nằm **trước** `JsonlFileProcessor()` (dòng 49).
`JsonlFileProcessor` là thứ ghi ra file — processor đặt sau nó thì file đã ghi xong rồi, che cũng
vô nghĩa. Chỗ `TODO` đang đặt sẵn đúng vị trí, cứ để nguyên đó.

### 2. Mở rộng pattern — `app/pii.py:11`

Đã có `email`, `phone_vn`, `cccd`, `credit_card`. Thêm ít nhất một loại nữa, ví dụ số hộ chiếu VN
(`[A-Z]\d{7}`) hoặc từ khóa địa chỉ (`số ... đường/phường/quận`).

### 3. Kiểm tra vùng phủ của `scrub_event`

Đọc `app/logging_config.py:26-34`. Hàm này chỉ quét `payload` (giá trị string) và `event`. Field
top-level như `error_type` **không** được quét. Cân nhắc có cần mở rộng không — và chuẩn bị giải
thích lựa chọn của bạn khi demo.

## Tự kiểm tra

```powershell
Remove-Item data/logs.jsonl
.\.venv\Scripts\python.exe scripts/load_test.py
.\.venv\Scripts\python.exe scripts/validate_logs.py
.\.venv\Scripts\python.exe -m pytest -q
```

Xong khi:

- Điểm vẫn **100/100**, `Potential PII leaks detected: 0`
- `pytest -q` vẫn 22 passed (chú ý `tests/test_pii.py` đang test hàm của bạn)
- **Tự đọc `data/logs.jsonl` bằng mắt** — đây mới là phần ăn điểm. Tìm xem còn sót email, số điện
  thoại, CCCD hay địa chỉ nào không.

Test nhanh pattern mới:

```powershell
.\.venv\Scripts\python.exe -c "from app.pii import scrub_text; print(scrub_text('hộ chiếu C1234567'))"
```

## Push

```powershell
git pull --rebase origin main
git add app/pii.py app/logging_config.py
git commit -m "feat(pii): enable scrub processor and extend PII patterns"
git pull --rebase origin main
git push origin main
```

Nhắn nhóm: `"TV3 xong, commit <sha>, tới lượt TV5."`
