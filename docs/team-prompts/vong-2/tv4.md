# TV4 — Vòng 2 — Traces và bằng chứng rollback

**Lượt push: 1/5** (bạn đi đầu vòng này)
**File sở hữu:** `submission/evidence/tv4-*.png`, `submission/notes/tv4.md`

Đây là vòng nặng nhất của bạn — 10/30 điểm A1 nằm ở đây, cộng 4 mục evidence bắt buộc trong
`SUBMISSION.md`.

## Việc cần làm

### 1. Sinh tối thiểu 10 traces

```powershell
Remove-Item data/logs.jsonl
.\.venv\Scripts\python.exe scripts/load_test.py
```

Chụp `tv4-trace-list.png` — danh sách phải thấy rõ ≥ 10 trace.

### 2. Chạy hai label, so hai trace

Đổi `LANGFUSE_PROMPT_LABEL` trong `.env` rồi **restart API** mỗi lần (không restart là vẫn chạy
label cũ):

```dotenv
LANGFUSE_PROMPT_LABEL=baseline     # chạy 1 request, ghi lại trace ID
LANGFUSE_PROMPT_LABEL=candidate    # chạy CÙNG input, ghi lại trace ID
```

Mở hai trace, kiểm tra `prompt_name`, `prompt_label`, `prompt_version`. Chụp `tv4-prompt-versions.png`
(danh sách 2 version) và `tv4-trace-baseline.png`, `tv4-trace-candidate.png`.

**Ghi lại 2 trace ID** — `RULES.md` quy định mọi nhận định phải kèm trace ID cụ thể, evidence không
kiểm chứng được thì không tính điểm.

### 3. Đổi label và rollback

1. Chuyển label `production` sang version 2 → chạy lại một request
2. Rollback `production` về version 1
3. Chụp ảnh **trước và sau**: `tv4-rollback-before.png`, `tv4-rollback-after.png`

### 4. Trace waterfall

Mở một trace bất kỳ ở chế độ waterfall, chụp `tv4-waterfall.png`. Phải thấy được các span con và
thời gian từng span.

Chọn sẵn **một span đáng chú ý** để giải thích — `REPORT.md` mục 3 hỏi thẳng câu này.

### 5. Cập nhật notes

Bổ sung vào `submission/notes/tv4.md`: 2 trace ID, version/label tương ứng, đường dẫn tương đối tới
từng ảnh.

## Cần hiểu để trả lời khi demo

- Vì sao cần prompt versioning? Để biết một câu trả lời tệ đến từ prompt nào, và rollback được mà
  không phải deploy lại code.
- Khác nhau giữa `version` và `label`: version là bản bất biến, label là con trỏ trỏ vào version —
  rollback chính là dời con trỏ.
- `prompt_source=local-fallback` nghĩa là gì và vì sao app không giả vờ đã lấy được prompt managed.

## Push

```powershell
git pull --rebase origin main
git add submission/evidence/tv4-*.png submission/notes/tv4.md
git commit -m "docs(evidence): add trace, prompt version and rollback evidence"
git pull --rebase origin main
git push origin main
```

`git status` không được thấy `.env`. Nhắn nhóm: `"TV4 xong, commit <sha>, tới lượt TV5."`
