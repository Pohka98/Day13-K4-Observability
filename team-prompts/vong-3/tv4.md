# TV4 — Vòng 3 — Tầng Traces: khoanh vùng span

**Lượt push: 2/5** — chờ `"TV5 xong"` và con số triệu chứng của TV5
**File sở hữu:** `submission/notes/tv4.md`, `submission/evidence/tv4-challenge-*.png`

## Việc cần làm

### 1. Tìm trace của challenge

Lọc trace theo `feature = monitoring` và `session_id` bắt đầu bằng `k4-challenge-s`. Có 5 trace ứng
với 5 query.

Chọn trace **chậm nhất** để phân tích sâu.

### 2. Mở waterfall và đo từng span

Với trace chậm nhất, ghi lại bảng:

| Span | Thời gian (ms) | % tổng |
|---|---|---|
| | | |

Span nào chiếm phần lớn thời gian? Nhìn `app/agent.py:30-41` để biết `run()` gồm những bước nào:
`retrieve(message)` → `resolve_prompt(...)` → `llm.generate(...)`.

### 3. Trả lời 3 câu

- **Span nào bất thường?** Tên span + thời gian + % tổng.
- **Trace ID cụ thể là gì?** Bắt buộc — `RULES.md` không tính evidence thiếu ID.
- **Các span còn lại có bình thường không?** Nếu chỉ một span phình ra còn lại không đổi, đó là bằng
  chứng mạnh cho việc khoanh vùng.

So với baseline: mở một trace từ lần chạy trước khi bật incident, đối chiếu cùng span đó.

### 4. Chụp evidence

- `tv4-challenge-waterfall.png` — waterfall của trace chậm nhất, thấy rõ span phình
- `tv4-challenge-baseline-trace.png` — trace tương ứng lúc bình thường, để so

### 5. Ghi `submission/notes/tv4.md`

Trace ID, bảng span, span nghi vấn, đường dẫn ảnh.

## Bàn giao

Nhắn nhóm kèm số liệu:
`"Span <tên> mất Xms / tổng Yms (Z%) trong trace <ID>. TV1–TV3 truy log để chứng minh nguyên nhân."`

## Push

```powershell
git pull --rebase origin main
git add submission/notes/tv4.md submission/evidence/tv4-challenge-*.png
git commit -m "docs(challenge): isolate anomalous span with trace evidence"
git pull --rebase origin main
git push origin main
```

Nhắn: `"TV4 xong, commit <sha>, tới lượt TV2."`
