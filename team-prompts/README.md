# Prompt phân công — Day 13 Observability

15 file prompt, chia theo 3 vòng × 5 thành viên. Mỗi người mở đúng file của mình trong vòng đang chạy.

```
vong-1/  CP1 — Logging & PII        (0:30–1:30)
vong-2/  CP2 — Traces & Dashboard   (1:30–2:30)
vong-3/  CP3 — Challenge & Report   (2:30–4:00)
```

## Luật chung cho mọi vòng

**Thứ tự push.** Trong mỗi vòng, chỉ một người push tại một thời điểm. Push xong nhắn nhóm
`"TV<N> xong, commit <sha>, tới lượt TV<N+1>"`. Chưa có tin nhắn đó thì người sau chưa được push.

**5 lệnh git mỗi lượt:**

```powershell
git pull --rebase origin main
git add <đúng file của mình>
git commit -m "..."
git pull --rebase origin main
git push origin main
```

**Ba điều cấm:**

1. `git add .` — kéo theo file người khác đang sửa dở.
2. `git push --force` — xóa vĩnh viễn commit người khác. Push bị từ chối thì `git pull --rebase` rồi push lại.
3. Sửa `submission/REPORT.md` khi không phải lượt của mình. Chỉ TV1 đụng file này, một lần duy nhất ở vòng 3.

**Python:** máy dùng venv Python 3.11, không phải `python` mặc định (3.14). Luôn gọi:

```powershell
.\.venv\Scripts\python.exe scripts/validate_logs.py
```

hoặc `.\.venv\Scripts\Activate.ps1` một lần đầu buổi.

**Đo lại điểm log:** `data/logs.jsonl` ghi kiểu append, record cũ hỏng sẽ kéo điểm xuống mãi.
Trước mỗi lần đo, xóa file rồi chạy lại load test:

```powershell
Remove-Item data/logs.jsonl
.\.venv\Scripts\python.exe scripts/load_test.py
.\.venv\Scripts\python.exe scripts/validate_logs.py
```

File này đã gitignore nên xóa thoải mái, không ảnh hưởng ai.

**Quy ước đặt tên file riêng** (file mới không bao giờ conflict):

- Ảnh evidence: `submission/evidence/tv<N>-<mô-tả>.png`
- Ghi chú cá nhân: `submission/notes/tv<N>.md`
- Test tự viết: `tests/test_<chủ-đề>.py`

## Về việc dùng AI

`RULES.md` cho phép dùng AI để giải thích lỗi và gợi ý cách kiểm tra, nhưng **cấm chép lời giải** —
mỗi người phải tự triển khai phần mình. Các prompt trong đây viết theo hướng đó: mô tả việc cần làm
và cách tự kiểm chứng. Khi bí, hỏi AI kiểu *"giải thích vì sao X không chạy"* thay vì *"viết hộ X"*.

Rubric B1 (20đ) chấm bạn có giải thích được phần mình làm khi bị hỏi hay không — chép xong không
hiểu là mất điểm ngay tại buổi demo.
