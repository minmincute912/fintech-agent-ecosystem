# Vận hành trên VPS và cách dùng hằng ngày

Viết 2026-11-25 cho M1 + M2 (nhánh `m2-vn-fundamentals-news`). Công cụ chỉ hỗ trợ nghiên cứu,
không đặt lệnh, không phải lời khuyên đầu tư.

## Chạy cái gì, khi nào

| Lệnh | Tốn tiền? | Khi nào chạy |
|---|---|---|
| `vsi collect-news` | Không (chỉ đọc RSS) | Tự động mỗi giờ bằng cron, để kho tin luôn đủ 7 ngày |
| `vsi analyze <MÃ> --date <NGÀY>` | Có (OpenAI, xem mục Chi phí) | Thủ công, khi bạn cần quyết định vào/ra lệnh |

Lý do cần cron cho tin tức: feed RSS chỉ giữ tin mới nhất (CafeF, VnEconomy khoảng 50 tin, phần
lớn trong 1–2 ngày). Nếu chỉ thu tin lúc chạy phân tích, cửa sổ 7 ngày sẽ thiếu. Cron thu tin
không gọi LLM nên không tốn tiền.

## VPS

- Ubuntu 22.04/24.04, 1 vCPU, 1–2 GB RAM, 10 GB đĩa là đủ: phần nặng (LLM) chạy ở OpenAI.
- Không cần Docker: một người dùng, một tiến trình CLI, chạy theo lệnh. Cron + `uv` đơn giản
  hơn và đúng thiết kế đã duyệt (spec 2026-11-03: "no Docker … cron for scheduled jobs").
- Không mở cổng nào. Chỉ cần SSH bằng khoá, tắt đăng nhập mật khẩu.

## Cài đặt (một lần)

```bash
# 1. Người dùng thường, không phải root
sudo adduser vsi && sudo usermod -aG sudo vsi && su - vsi

# 2. uv và mã nguồn (repo private: dùng deploy key chỉ-đọc của GitHub)
curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh && less /tmp/uv-install.sh && sh /tmp/uv-install.sh
git clone git@github.com:<owner>/fintech-agent-ecosystem.git && cd fintech-agent-ecosystem
uv sync

# 3. Khoá: tạo .env bằng editor trên VPS, không dán vào chat/log
cat > .env <<'EOF'
OPENAI_API_KEY=
DNSE_API_KEY=
DNSE_API_SECRET=
EOF
chmod 600 .env && nano .env

# 4. Kiểm tra
uv run pytest -q
uv run vsi collect-news
```

Cron thu tin mỗi giờ (giờ Việt Nam; `crontab -e`):

```cron
CRON_TZ=Asia/Ho_Chi_Minh
15 * * * * cd $HOME/fintech-agent-ecosystem && $HOME/.local/bin/uv run vsi collect-news >> $HOME/.tradingagents/vsi/collect.log 2>&1
```

Dữ liệu nằm ở `~/.tradingagents/`: `vsi/news.sqlite` (kho tin), `logs/` (báo cáo và
`vsi_runs.jsonl` ghi token mỗi lượt). Sao lưu `news.sqlite` nếu muốn giữ lịch sử tin.

## Cách dùng khi cần vào lệnh

1. **Chọn ngày phân tích = phiên đã đóng cửa gần nhất mà DNSE đã có nến ngày.** Ví dụ tối thứ Ba
   hoặc sáng thứ Tư trước giờ mở cửa: dùng ngày thứ Ba nếu nến đã có, nếu chưa dùng thứ Hai.
   Ngày 2026-11-24 lúc 18:15 nến của chính ngày đó chưa có (M1 Task 9). Đừng chạy với ngày hôm
   nay trong giờ giao dịch.
2. Chạy: `uv run vsi analyze VNM --date 2026-11-23` (2–4 phút).
3. Đọc báo cáo theo đường dẫn in ra. Thứ tự nên đọc: kế hoạch cuối (portfolio manager), rồi
   phần phản biện bull/bear, rồi ba báo cáo nguồn (giá, BCTC, tin tức) để kiểm chứng số liệu.
4. Tự kiểm tra trước khi đặt lệnh:
   - Số liệu BCTC có ngày tạo (`created`) và nhãn "(revised after analysis date)" nếu có.
   - Tin tức có nguồn và giờ; mở link để đọc bản gốc khi tin quyết định ý kiến.
   - Mục nào báo `DATA_UNAVAILABLE` hoặc `NO_DATA_AVAILABLE` là dữ liệu thiếu, không phải
     tín hiệu.
5. Quyết định và đặt lệnh trên app môi giới là việc của bạn. Hệ thống không đặt lệnh.

Nên phân tích nhiều nhất vài mã một lúc trong danh sách theo dõi, không quét cả thị trường:
mỗi lượt tốn tiền và mất vài phút.

## Chi phí

Đo 2026-11-25 (`docs/research/m2-run-cost.md`): mỗi lượt `vsi analyze` khoảng 100–120 nghìn
token vào, 20 nghìn token ra, 2,2–2,7 phút. Chặn trên $0,45/lượt; ước tính thực tế
$0,10–0,20/lượt (số chính xác: OpenAI dashboard → Usage theo model). Ví dụ 3 mã/ngày × 20 ngày
giao dịch ≈ 60 lượt ≈ $6–12/tháng. Nên đặt giới hạn chi tiêu (usage limit) trên OpenAI.
VPS 1 vCPU/1–2 GB khoảng $4–6/tháng (giá tham khảo, chưa kiểm tra nhà cung cấp cụ thể).

## Giới hạn cần nhớ

- Điểm vào, cắt lỗ, khối lượng **chưa** có code tính (để sau M5, theo thứ tự milestone).
  Mức giá trong báo cáo là ý kiến của LLM, không phải phép tính đã kiểm thử.
- Nguồn BCTC (VNDirect finfo) không có tài liệu, chỉ dùng nghiên cứu cá nhân, có thể bị chặn bất
  cứ lúc nào (`docs/research/finfo-probe.md`).
- Dữ liệu DNSE chỉ dùng cho giao dịch của chính bạn; không chia sẻ báo cáo có dữ liệu DNSE cho
  người khác khi chưa có chấp thuận của DNSE.
- Tin tức: chỉ đọc tiêu đề và tóm tắt RSS; không đăng lại.
