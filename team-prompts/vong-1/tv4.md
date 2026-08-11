# TV4 — Vòng 1 — Langfuse và Prompt versioning

**Lượt push: 5/5** — nhưng **bắt đầu làm ngay từ phút đầu tiên của buổi lab**
**File sở hữu:** `submission/notes/tv4.md`

## Bạn đang giữ blocker của cả nhóm

`.env` hiện chưa có key Langfuse, `/health` trả `tracing_enabled: false`. Không có key thì **toàn bộ
CP2 không làm được** — mà CP2 chiếm 10/30 điểm A1 cộng phần lớn evidence bắt buộc trong
`SUBMISSION.md`. Làm việc này trước mọi thứ khác.

May là phần của bạn gần như không đụng code, nên không vướng lượt push của ai — cứ làm song song
trên Langfuse UI, cuối vòng mới push notes.

## Việc cần làm

### 1. Lấy API key

Xin key chung của Lab Coach. Không có thì tự đăng ký [cloud.langfuse.com](https://cloud.langfuse.com)
miễn phí, tạo project mới, vào **Settings → API Credentials**.

Điền vào `.env` (file này đã gitignore, **không commit**):

```dotenv
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PROMPT_NAME=day13-chat
LANGFUSE_PROMPT_LABEL=production
```

**Gửi key cho 4 người còn lại qua chat nhóm**, mỗi người tự dán vào `.env` máy mình.

Restart API rồi xác nhận:

```powershell
.\.venv\Scripts\python.exe -c "import httpx; print(httpx.get('http://127.0.0.1:8000/health').json())"
```

Phải thấy `tracing_enabled: True`. Còn `False` là key sai hoặc chưa restart.

### 2. Tạo prompt `day13-chat` trên Langfuse

Theo `docs/PROMPT_VERSIONING.md`. Prompt **bắt buộc giữ 3 biến**, sai tên là app không render được:

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}
```

- **Version 1** — gắn label `baseline` **và** `production`
- **Version 2** — đổi nhỏ về format hoặc độ dài câu trả lời, gắn label `candidate`

Không chấm prompt nào hay hơn. Điểm nằm ở khả năng truy xuất version và rollback.

### 3. Ghi chú vào `submission/notes/tv4.md`

Prompt name, ID của v1 và v2, label từng version, thời điểm tạo.

## Tự kiểm tra

```powershell
Remove-Item data/logs.jsonl
.\.venv\Scripts\python.exe scripts/load_test.py
```

Mở Langfuse UI, phải thấy trace mới xuất hiện. Mở một trace xem metadata: `prompt_source` phải là
`langfuse`, **không phải** `local-fallback`. Nếu ra `local-fallback` thì kiểm tra host/key và
prompt name/label trong `.env`.

## Push

```powershell
git pull --rebase origin main
git add submission/notes/tv4.md
git commit -m "docs(prompt): record day13-chat prompt versions and labels"
git pull --rebase origin main
git push origin main
```

Kiểm tra `git status` trước khi push — **không được thấy `.env`** trong danh sách.

Nhắn nhóm: `"TV4 xong, commit <sha>, hết vòng 1."`
