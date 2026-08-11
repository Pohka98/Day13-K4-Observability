# TV5 — Vòng 1 — SLO và Alert rules

**Lượt push: 4/5** — chờ tin nhắn `"TV3 xong"`
**File sở hữu:** `config/slo.yaml`, `config/alert_rules.yaml`

Phần này **không phụ thuộc log chạy được**, nên bạn làm ngay từ đầu buổi, chỉ chờ đến lượt để push.

## Việc cần làm

### 1. `config/alert_rules.yaml` — điền 3 alert

File đang toàn `TODO`. Mỗi rule cần `name`, `severity`, `condition`, `runbook`, `owner`.

Lấy ngưỡng từ `config/dashboard.yaml` cho khớp — đừng bịa số mới:

| Chỉ số | Ngưỡng có sẵn | Panel |
|---|---|---|
| Latency p95 | ≤ 3000 ms | `latency` |
| Error rate | ≤ 2 % | `errors` |
| Tổng cost | ≤ 2.5 USD | `cost` |
| Quality trung bình | ≥ 0.75 | `quality` |

Chọn 3 trong số đó. `owner` ghi tên thật một thành viên, không để `TODO`.

### 2. `config/slo.yaml` — thay target của nhóm

Dòng 7 đang ghi `note: Replace with your group's target`. Xem lại 4 SLI (`latency_p95_ms`,
`error_rate_pct`, `daily_cost_usd`, `quality_score_avg`), quyết định target của nhóm và **ghi lý do**.

`CHECKPOINTS.md` đòi "SLO line hoặc threshold rõ ràng" và `REPORT.md` mục 5 hỏi "SLO đã chọn và lý
do" — nên phần giải thích quan trọng ngang phần con số.

### 3. Chuẩn bị runbook

`docs/alerts.md` là việc của vòng 2, nhưng đọc trước để viết `condition` cho nhất quán.

## Cần hiểu để trả lời khi demo

Phân biệt được **SLO** (mục tiêu dài hạn, cửa sổ 28 ngày, ví dụ "99.5% request có p95 < 3s") và
**alert threshold** (ngưỡng bắn cảnh báo tức thời). Rất hay bị hỏi.

Vì sao dùng p95 chứ không phải trung bình? Chuẩn bị câu trả lời — `RUBRIC.md` B1 liệt kê
"percentile" là một trong các chủ đề sẽ hỏi.

## Tự kiểm tra

```powershell
.\.venv\Scripts\python.exe scripts/validate_dashboard.py
.\.venv\Scripts\python.exe -m pytest -q
```

Xong khi:

- `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- `pytest -q` vẫn 22 passed
- Không còn chữ `TODO` nào trong `config/alert_rules.yaml`

## Push

```powershell
git pull --rebase origin main
git add config/slo.yaml config/alert_rules.yaml
git commit -m "feat(observability): define group SLO targets and alert rules"
git pull --rebase origin main
git push origin main
```

Nhắn nhóm: `"TV5 xong, commit <sha>, tới lượt TV4."`
