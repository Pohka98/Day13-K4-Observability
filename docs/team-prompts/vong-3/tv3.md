# TV3 — Vòng 3 — Root cause, fix và phòng ngừa

**Lượt push: 4/5** — chờ `"TV2 xong"`
**File sở hữu:** `submission/notes/tv3.md`, `submission/evidence/tv3-challenge-*.png`

Bạn chốt kết luận cho cả cuộc điều tra, dựa trên đầu vào của TV5 (metrics), TV4 (span) và TV2 (log).

## Việc cần làm

### 1. Kết luận root cause

Viết theo cấu trúc — mỗi mệnh đề kèm bằng chứng:

```
Triệu chứng : <chỉ số + số liệu>            (nguồn: TV5)
Khoanh vùng : <span + thời gian + trace ID>  (nguồn: TV4)
Bằng chứng  : <log line + correlation ID>    (nguồn: TV2)
Root cause  : <nguyên nhân>
```

Đừng dừng ở "span X chậm" — đó là *triệu chứng của tầng dưới*, chưa phải nguyên nhân. Hỏi tiếp: vì
sao span đó chậm? Đọc code đường đi trong `app/agent.py:30-41` và module mà span đó gọi vào.

### 2. Đề xuất fix action

Cụ thể, chỉ được ra file/hàm. Ví dụ dạng "thêm timeout cho X", "cache Y", "giới hạn Z" — không phải
"tối ưu hệ thống".

### 3. Đề xuất preventive measure

Làm sao phát hiện sớm lần sau? Nối lại với việc TV5 đã làm:

- Alert nào trong `config/alert_rules.yaml` lẽ ra phải bắn?
- Ngưỡng hiện tại có bắt được sự cố này không? Nếu không, đề xuất ngưỡng mới.
- Panel nào trên dashboard cho thấy sớm nhất?

`RUBRIC.md` A2 yêu cầu **cả** fix action **và** preventive measure — thiếu một cái là mất điểm.

### 4. Chụp evidence tổng hợp

`tv3-challenge-rootcause.png` — ảnh ghép hoặc ảnh log line quyết định, thứ chứng minh trực tiếp
nguyên nhân.

### 5. Ghi `submission/notes/tv3.md`

Đầy đủ 4 phần: triệu chứng → khoanh vùng → bằng chứng → root cause, cộng fix và preventive.

## Sau khi xong

Tắt incident, trả hệ thống về trạng thái sạch để buổi demo chạy được:

```powershell
.\.venv\Scripts\python.exe scripts/inject_incident.py --disable
.\.venv\Scripts\python.exe -m pytest -q
```

`RUBRIC.md` A3 (20đ) chấm "hệ thống chạy được trong buổi chấm" — đừng để incident còn bật.

## Push

```powershell
git pull --rebase origin main
git add submission/notes/tv3.md submission/evidence/tv3-challenge-*.png
git commit -m "docs(challenge): conclude root cause with fix and preventive measures"
git pull --rebase origin main
git push origin main
```

Nhắn: `"TV3 xong, commit <sha>, tới lượt TV1 gom REPORT."`
