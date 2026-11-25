# Vận hành trên VPS và cách dùng hằng ngày

Viết 2026-11-25 cho M1–M3; cập nhật cho bot Telegram (M3). Công cụ chỉ hỗ trợ nghiên cứu,
không đặt lệnh, không phải lời khuyên đầu tư.

## Chạy cái gì, khi nào

| Lệnh | Tốn tiền? | Khi nào chạy |
|---|---|---|
| `vsi bot` | Chỉ khi bạn gửi `/analyze` | Chạy liên tục bằng systemd; tự thu tin mỗi giờ |
| `/analyze MÃ` trong Telegram | Có (OpenAI, xem mục Chi phí) | Khi bạn cần quyết định vào/ra lệnh |
| `vsi analyze <MÃ> --date <NGÀY>` | Có | Gõ tay trên VPS nếu cần; không chạy cùng lúc với bot |
| `vsi collect-news` | Không | Gõ tay nếu muốn thu tin ngay; bot đã tự thu mỗi giờ |

Bot thu tin mỗi giờ vì feed RSS chỉ giữ tin mới nhất (CafeF, VnEconomy khoảng 50 tin, phần lớn
trong 1–2 ngày). Thu tin không gọi LLM nên không tốn tiền. Khi bot đứng im (không có lệnh), chi
phí OpenAI bằng 0.

## VPS

- Ubuntu 22.04/24.04, 1 vCPU, 1–2 GB RAM, 10 GB đĩa là đủ: phần nặng (LLM) chạy ở OpenAI.
- Không cần Docker: một người dùng, một tiến trình. systemd + `uv` đơn giản hơn và đúng thiết
  kế đã duyệt (spec 2026-11-03: "no Docker").
- Không mở cổng nào: bot dùng long polling (tự hỏi Telegram), không cần tên miền hay HTTPS.
  Chỉ cần SSH bằng khoá, tắt đăng nhập mật khẩu.

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
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_CHAT_IDS=
EOF
chmod 600 .env && nano .env

# 4. Kiểm tra
uv run pytest -q
uv run vsi collect-news
```

### Bot Telegram

1. Trong Telegram, nhắn @BotFather lệnh `/newbot`, đặt tên. BotFather trả về **token** dạng
   `123456789:AA…`. Token là mật khẩu của bot: chỉ dán vào `.env` trên VPS, không gửi qua chat,
   email hay ảnh chụp màn hình.
2. Lấy **chat ID** của bạn: nhắn @userinfobot (hoặc bot tương tự), nó trả về số `Id`. Điền vào
   `TELEGRAM_ALLOWED_CHAT_IDS`. Bot chỉ trả lời các ID trong danh sách này.
3. Mở chat với bot của bạn và bấm Start (bot không nhắn trước được cho người chưa nhắn nó).
4. Cài dịch vụ (chạy lại sau khi khởi động VPS, tự khởi động lại nếu lỗi):

```bash
mkdir -p ~/.config/systemd/user && cp deploy/vsi-bot.service ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now vsi-bot
sudo loginctl enable-linger "$USER"      # để bot chạy cả khi bạn thoát SSH
journalctl --user -u vsi-bot -f          # xem log
```

Bot từ chối chạy nếu thiếu token, danh sách chat trống, thiếu khoá OpenAI/DNSE, hoặc `.env` không
phải quyền 600. Nếu nghi token bị lộ: nhắn @BotFather `/revoke`, dán token mới vào `.env`, rồi
`systemctl --user restart vsi-bot`.

Cập nhật code: `git pull && uv sync && systemctl --user restart vsi-bot`. Nếu một phân tích đang
chạy, nó bị dừng và bot báo cho bạn; gửi lại `/analyze` nếu cần.

Dữ liệu nằm ở `~/.tradingagents/`: `vsi/news.sqlite` (kho tin), `vsi/bot.sqlite` (hàng đợi),
`logs/` (báo cáo và `vsi_runs.jsonl` ghi token mỗi lượt), `memory/trading_memory.md` (lịch sử
phân tích cho `/history`).

## Cách dùng khi cần vào lệnh

1. Trong Telegram gửi `/analyze VNM`. Bot tự chọn phiên gần nhất DNSE đã có nến ngày (trước
   15:05 thì không dùng nến của hôm nay). Muốn ngày khác: `/analyze VNM 2026-11-20`.
2. Bot trả "Đã xếp hàng…", 2–4 phút sau gửi tóm tắt và file báo cáo HTML (mở bằng trình duyệt
   trên điện thoại). `/status` xem hàng đợi; giới hạn mặc định 10 lượt/ngày (`VSI_DAILY_RUN_CAP`).
3. Đọc tóm tắt theo thứ tự: dòng dữ liệu (giá DNSE, biên độ, ngày BCTC và tin tức) → xếp hạng →
   mức giá agent điền vào ô riêng (đã kiểm tra biên độ) → "Ý kiến agent" (số trong đó KHÔNG được
   kiểm tra). Cần chi tiết thì mở file: kế hoạch cuối, phản biện bull/bear, ba báo cáo nguồn.
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
