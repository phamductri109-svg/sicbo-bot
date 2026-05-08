# bot.py
# pip install pyTelegramBotAPI requests

import telebot
import requests
import time
from threading import Thread

TOKEN = "8731298397:AAFTiFjy1wNhef6VEvvp0NcEbUBRFb_qlRo"
API_URL = "https://sunwinsicbo-2r4h.onrender.com/sicbo"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

users_auto = set()

# =========================
# LƯU LỊCH SỬ
# =========================
history = []

# =========================
# THUẬT TOÁN PHÂN TÍCH
# =========================
class SunwinAnalyzer:

    def __init__(self, history):

        self.history = history
        self.length = len(history)

    def is_bet(self, n=4):

        if self.length < n:
            return False

        last_n = self.history[-n:]

        if all(x == 'T' for x in last_n):
            return f"Bệt Tài {n} tay"

        if all(x == 'X' for x in last_n):
            return f"Bệt Xỉu {n} tay"

        return None

    def is_dao_11(self, n=4):

        if self.length < n:
            return False

        last_n = self.history[-n:]

        pattern1 = ['T', 'X'] * (n // 2)
        pattern2 = ['X', 'T'] * (n // 2)

        if last_n == pattern1[:n] or last_n == pattern2[:n]:
            return "Cầu Đảo 1-1"

        return None

    def is_cau_22(self):

        if self.length < 4:
            return False

        last_4 = self.history[-4:]

        if (
            last_4 == ['T', 'T', 'X', 'X']
            or
            last_4 == ['X', 'X', 'T', 'T']
        ):
            return "Cầu 2-2"

        return None

    def is_cau_321(self):

        if self.length < 6:
            return False

        last_6 = self.history[-6:]

        if (
            last_6[:3] == ['T'] * 3
            and
            last_6[3:5] == ['X'] * 2
            and
            last_6[5] == 'T'
        ) or (
            last_6[:3] == ['X'] * 3
            and
            last_6[3:5] == ['T'] * 2
            and
            last_6[5] == 'X'
        ):
            return "Cầu 3-2-1"

        return None

    def is_cau_123(self):

        if self.length < 6:
            return False

        last_6 = self.history[-6:]

        if (
            last_6[0] == 'T'
            and
            last_6[1:3] == ['X'] * 2
            and
            last_6[3:] == ['T'] * 3
        ) or (
            last_6[0] == 'X'
            and
            last_6[1:3] == ['T'] * 2
            and
            last_6[3:] == ['X'] * 3
        ):
            return "Cầu 1-2-3"

        return None

    def analyze(self):

        results = []

        check_321 = self.is_cau_321()
        if check_321:
            results.append(check_321)

        check_123 = self.is_cau_123()
        if check_123:
            results.append(check_123)

        check_bet = self.is_bet(5)
        if check_bet:
            results.append(check_bet)

        check_22 = self.is_cau_22()
        if check_22:
            results.append(check_22)

        check_11 = self.is_dao_11()
        if check_11:
            results.append(check_11)

        if not results:
            return "Xu hướng: Cầu loạn"

        return " | ".join(results)

# =========================
# LẤY API
# =========================
def get_data():

    try:

        r = requests.get(API_URL, timeout=10)

        return r.json()

    except:

        return None

# =========================
# FORMAT TIN NHẮN
# =========================
def format_msg(data):

    global history

    xx1 = data.get("xuc_xac_1")
    xx2 = data.get("xuc_xac_2")
    xx3 = data.get("xuc_xac_3")

    tong = data.get("tong")
    ket_qua = data.get("ket_qua")

    phien = data.get("phien")
    phien_ht = data.get("phien_hien_tai")

    du_doan = data.get("du_doan")

    du_doan_vi = ",".join(
        map(str, data.get("du_doan_vi", []))
    )

    chanle = data.get("du_doan_chan_le")

    goi_y = data.get("goi_y")

    # =========================
    # UPDATE HISTORY
    # =========================

    if "Tài" in ket_qua:
        history.append("T")
    else:
        history.append("X")

    # Giữ tối đa 100 phiên
    history = history[-100:]

    analyzer = SunwinAnalyzer(history)

    phan_tich_cau = analyzer.analyze()

    lich_su_text = " - ".join(history[-15:])

    # =========================
    # THỐNG KÊ
    # =========================

    tai_count = history.count("T")
    xiu_count = history.count("X")

    tong_van = len(history)

    if tong_van > 0:

        tai_percent = round(
            tai_count / tong_van * 100,
            1
        )

        xiu_percent = round(
            xiu_count / tong_van * 100,
            1
        )

    else:

        tai_percent = 0
        xiu_percent = 0

    msg = f"""
╔══════════════════╗
🎲 <b>SICBO AI PREDICT</b>
╚══════════════════╝

🆔 <b>Phiên:</b> <code>{phien}</code>
🎯 <b>Phiên hiện tại:</b> <code>{phien_ht}</code>

🎲 <b>Xúc xắc:</b>
┠ 🎲 1: <b>{xx1}</b>
┠ 🎲 2: <b>{xx2}</b>
┖ 🎲 3: <b>{xx3}</b>

📊 <b>Tổng:</b> <code>{tong}</code>
🏆 <b>Kết quả:</b> <b>{ket_qua}</b>

━━━━━━━━━━━━━━

🔮 <b>Dự đoán:</b> <b>{du_doan}</b>
🎯 <b>Vị đẹp:</b> <code>{du_doan_vi}</code>
⚖ <b>Chẵn/Lẻ:</b> <b>{chanle}</b>

💡 <b>Gợi ý:</b>
<code>{goi_y}</code>

━━━━━━━━━━━━━━

🧠 <b>Phân tích cầu:</b>
<code>{phan_tich_cau}</code>

📜 <b>Lịch sử:</b>
<code>{lich_su_text}</code>

━━━━━━━━━━━━━━

📈 <b>Thống kê:</b>

🎯 Tài: <b>{tai_count}</b> ({tai_percent}%)
🎯 Xỉu: <b>{xiu_count}</b> ({xiu_percent}%)

📊 Tổng phiên lưu:
<code>{tong_van}</code>

━━━━━━━━━━━━━━
⚡ Bot chạy realtime API
"""

    return msg

# =========================
# /start
# =========================
@bot.message_handler(commands=['start'])
def start(message):

    text = f"""
👋 Xin chào <b>{message.from_user.first_name}</b>

🎲 Đây là bot soi cầu Sicbo realtime.

📌 Danh sách lệnh:

/sicbo - Xem phiên mới
/auto - Auto gửi
/stop - Tắt auto
/history - Xem lịch sử
/stats - Thống kê
/ping - Check bot
/help - Hướng dẫn
"""

    bot.reply_to(message, text)

# =========================
# /help
# =========================
@bot.message_handler(commands=['help'])
def help_cmd(message):

    text = """
📚 <b>HƯỚNG DẪN BOT</b>

🔹 /sicbo
Xem dữ liệu mới nhất

🔹 /auto
Bật auto gửi phiên mới

🔹 /stop
Tắt auto gửi

🔹 /history
Xem lịch sử cầu

🔹 /stats
Xem thống kê

🔹 /ping
Check bot online
"""

    bot.reply_to(message, text)

# =========================
# /ping
# =========================
@bot.message_handler(commands=['ping'])
def ping(message):

    bot.reply_to(
        message,
        "🏓 Pong! Bot Online"
    )

# =========================
# /sicbo
# =========================
@bot.message_handler(commands=['sicbo'])
def sicbo(message):

    msg = bot.reply_to(
        message,
        "⏳ Đang lấy dữ liệu..."
    )

    data = get_data()

    if not data:

        bot.edit_message_text(
            "❌ API lỗi hoặc timeout",
            message.chat.id,
            msg.message_id
        )

        return

    bot.edit_message_text(
        format_msg(data),
        message.chat.id,
        msg.message_id
    )

# =========================
# /history
# =========================
@bot.message_handler(commands=['history'])
def history_cmd(message):

    if not history:

        bot.reply_to(
            message,
            "❌ Chưa có dữ liệu"
        )

        return

    text = " - ".join(history[-50:])

    bot.reply_to(
        message,
        f"""
📜 <b>50 phiên gần nhất</b>

<code>{text}</code>
"""
    )

# =========================
# /stats
# =========================
@bot.message_handler(commands=['stats'])
def stats_cmd(message):

    if not history:

        bot.reply_to(
            message,
            "❌ Chưa có dữ liệu"
        )

        return

    tai = history.count("T")
    xiu = history.count("X")

    tong = len(history)

    tai_percent = round(
        tai / tong * 100,
        1
    )

    xiu_percent = round(
        xiu / tong * 100,
        1
    )

    analyzer = SunwinAnalyzer(history)

    bot.reply_to(
        message,
        f"""
📊 <b>THỐNG KÊ BOT</b>

🎯 Tài:
<b>{tai}</b> ({tai_percent}%)

🎯 Xỉu:
<b>{xiu}</b> ({xiu_percent}%)

📦 Tổng phiên:
<b>{tong}</b>

🧠 Phân tích:
<code>{analyzer.analyze()}</code>
"""
    )

# =========================
# /auto
# =========================
@bot.message_handler(commands=['auto'])
def auto(message):

    users_auto.add(message.chat.id)

    bot.reply_to(
        message,
        "✅ Đã bật auto soi cầu"
    )

# =========================
# /stop
# =========================
@bot.message_handler(commands=['stop'])
def stop(message):

    if message.chat.id in users_auto:
        users_auto.remove(message.chat.id)

    bot.reply_to(
        message,
        "🛑 Đã tắt auto"
    )

# =========================
# AUTO CHECK PHIÊN
# =========================
last_phien = None

def auto_send():

    global last_phien

    while True:

        try:

            data = get_data()

            if data:

                phien = data.get("phien")

                if phien != last_phien:

                    last_phien = phien

                    text = format_msg(data)

                    for chat_id in users_auto:

                        try:

                            bot.send_message(
                                chat_id,
                                text
                            )

                        except:
                            pass

        except:
            pass

        time.sleep(5)

# =========================
# START THREAD
# =========================
Thread(target=auto_send).start()

print("BOT RUNNING...")

# =========================
# START BOT
# =========================
bot.infinity_polling()
