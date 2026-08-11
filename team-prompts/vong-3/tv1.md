# TV1 — Vòng 3 — Gom REPORT.md và chốt bài nộp

**Lượt push: 5/5** — chờ `"TV3 xong"`. Bạn là người cuối, không ai push sau bạn.
**File sở hữu:** `submission/notes/tv1.md`, `submission/REPORT.md`

`REPORT.md` là file duy nhất cả nhóm cùng cần, nên chỉ mình bạn đụng vào, đúng một lần. Đừng bắt đầu
khi chưa đủ 4 file notes của người khác trên `main`.

## Việc cần làm

### 1. Kéo đủ notes về

```powershell
git pull --rebase origin main
Get-ChildItem submission/notes
```

Phải thấy đủ `tv1.md`..`tv5.md`. Thiếu file nào thì hỏi người đó trước khi viết.

### 2. Viết notes của mình

`submission/notes/tv1.md` — phần correlation ID (vòng 1), test (vòng 2), đóng góp điều tra (vòng 3).

### 3. Gom vào `submission/REPORT.md`

| Mục | Nguồn |
|---|---|
| 1. Thông tin nhóm | Bạn — tên nhóm, repo URL, commit SHA cuối, 5 thành viên + vai trò |
| 2. Kết quả kỹ thuật | `validate_logs.py` (100/100), tổng traces (TV4), PII leak = 0 (TV3), link dashboard (TV5) |
| 3. Logging và tracing | notes TV1 (correlation), TV3 (PII), TV4 (waterfall + span đáng chú ý) |
| 4. Prompt versioning | notes TV4 — prompt name, 2 version/label, 2 trace ID, bằng chứng rollback |
| 5. Dashboard, SLO, alerts | notes TV5 — kết quả validator, SLO đã chọn **và lý do**, alert + runbook |
| 6. Điều tra challenge | notes TV5 → TV4 → TV2 → TV3, ghép theo luồng Metrics → Traces → Logs |
| 7. Đóng góp cá nhân | bảng 5 dòng, mỗi dòng một người kèm link commit |

**Mục 6 ghi rõ `challenge_id: day13-k4-observability-v1`.**

**Mục 7 là 20 điểm B2 của từng người** — phần khai phải khớp với commit thật trong Git. Lấy SHA:

```powershell
git log --oneline --format="%h %an %s" -30
```

Ảnh dẫn bằng **đường dẫn tương đối**, ví dụ `evidence/tv4-waterfall.png`.

### 4. Kiểm tra trước khi nộp

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/validate_logs.py
.\.venv\Scripts\python.exe scripts/validate_dashboard.py
git status --short
```

Checklist theo `SUBMISSION.md`:

- [ ] `pytest -q` pass
- [ ] `validate_logs.py` ≥ 80 (nhóm đang ở 100)
- [ ] `validate_dashboard.py` báo 6/6
- [ ] `REPORT.md` không còn mục trống
- [ ] Đủ 11 mục evidence trong `docs/grading-evidence.md`
- [ ] **`git status` không có `.env`**, không có `.venv/`, không có `data/logs.jsonl`
- [ ] `config/challenge.json` chưa bị sửa — kiểm tra: `git log --oneline config/challenge.json` chỉ
      có commit gốc
- [ ] Không còn incident bật: `/health` trả cả 3 incident `false`

Quét secret lần cuối:

```powershell
git grep -nE "sk-lf-|pk-lf-"
```

Không được ra kết quả nào ngoài file tài liệu hướng dẫn. Lộ key là bài **không hợp lệ**, phải nộp lại.

### 5. Push và nộp

```powershell
git add submission/notes/tv1.md submission/REPORT.md
git commit -m "docs(report): compile final Day 13 observability report"
git pull --rebase origin main
git push origin main
git log -1 --format=%H
```

Nộp trên Codelabs: **URL repository + commit SHA cuối** (chính là output lệnh trên). Nhớ cập nhật SHA
đó vào mục 1 của `REPORT.md` nếu bạn đã điền trước — hoặc ghi SHA của commit áp cuối và nói rõ.

### 6. Chuẩn bị demo

Luồng trình bày: **Metrics → Traces → Logs → Root cause**. Mỗi người tự nói phần mình
(`RUBRIC.md` A3 + B1, tổng 40 điểm). Chạy thử một lượt trước khi vào chấm.
