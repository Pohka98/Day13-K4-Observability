# TV5 — Vòng 2 — Dashboard và Runbook

**Lượt push: 2/5** — chờ `"TV4 xong"`
**File sở hữu:** `docs/alerts.md`, `submission/evidence/tv5-*.png`

## Việc cần làm

### 1. Dựng dashboard 6 panel

Theo `docs/DASHBOARD_SETUP.md`. Contract nằm ở `config/dashboard.yaml` — file này **đã đủ 6 panel và
validator đã pass**, bạn không cần sửa. Việc của bạn là dựng dashboard thật hiển thị đúng 6 nhóm:

| Panel | Chỉ số | Ngưỡng |
|---|---|---|
| `latency` | p50/p95/p99 của `latency_ms` | p95 ≤ 3000 ms |
| `traffic` | count `request_received` theo phút | ≥ 1 req/phút |
| `errors` | tỉ lệ lỗi + breakdown `error_type` | ≤ 2 % |
| `cost` | `cost_usd` theo phút + tổng | ≤ 2.5 USD |
| `tokens` | tổng `tokens_in`, `tokens_out` | ≤ 50 000 |
| `quality` | trung bình `quality_score` | ≥ 0.75 |

Nguồn dữ liệu là `data/logs.jsonl` — nhớ chạy load test trước để có số:

```powershell
Remove-Item data/logs.jsonl
.\.venv\Scripts\python.exe scripts/load_test.py
```

**Bắt buộc vẽ được SLO line hoặc threshold** trên panel — `CHECKPOINTS.md` đòi rõ mục này.

Chụp `tv5-dashboard-full.png` (toàn cảnh 6 panel) và ít nhất một ảnh cận cảnh panel có SLO line,
ví dụ `tv5-dashboard-latency-slo.png`.

### 2. Viết runbook — `docs/alerts.md`

Với mỗi alert đã định nghĩa ở vòng 1 trong `config/alert_rules.yaml`, runbook cần trả lời:

- Alert này bắn nghĩa là gì?
- Bước đầu tiên phải kiểm tra là gì? (panel nào, log nào)
- Ai chịu trách nhiệm?
- Cách xử lý tạm và cách xử lý gốc

Runbook không có bước hành động cụ thể thì không tính là runbook.

### 3. Chụp kết quả validator

```powershell
.\.venv\Scripts\python.exe scripts/validate_dashboard.py
```

Chụp `tv5-validate-dashboard.png`.

## Cần hiểu để trả lời khi demo

- Vì sao đo p95 mà không đo trung bình? (trung bình che mất đuôi chậm)
- Vì sao error rate tính theo tỉ lệ chứ không theo số tuyệt đối?
- Panel nào bạn sẽ nhìn **đầu tiên** khi có sự cố, và vì sao — CP3 sẽ cần đúng phản xạ này.

## Push

```powershell
git pull --rebase origin main
git add docs/alerts.md submission/evidence/tv5-*.png
git commit -m "docs(dashboard): add 6-panel dashboard evidence and alert runbook"
git pull --rebase origin main
git push origin main
```

Nhắn nhóm: `"TV5 xong, commit <sha>, tới lượt TV1."`
