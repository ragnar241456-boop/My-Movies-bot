import os
import time
import threading
import telebot
from flask import Flask, request

# Telegram Bot Token သတ်မှတ်ခြင်း
BOT_TOKEN = "8609626698:AAFX9be-pwkM7nn_vMRTwx-1ut97HfMhhmQ"
bot = telebot.TeleBot(BOT_TOKEN)

# Webhook အတွက် Flask App
app = Flask(__name__)

# ဖိုင်ကို ၂ မိနစ် (စက္ကန့် ၁၂၀) ပြည့်ရင် Auto ဖျက်မည့် Function
def auto_delete_message(chat_id, message_id):
    time.sleep(120)  # ၂ မိနစ် စောင့်ဆိုင်းခြင်း
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

# Public Channel က လင့်ခ်နှိပ်ပြီး ဝင်လာချိန် (ဥပမာ - t.me/your_bot?start=movie_id_001)
@bot.message_handler(commands=['start'])
def send_movie_and_vip_info(message):
    chat_id = message.chat.id
    command_args = message.text.split()
    
    # VIP ကြော်ငြာနှင့် လမ်းညွှန်စာသား
    welcome_text = (
        "မင်္ဂလာပါ။ 🎬 ဇာတ်ကားကို သင့်အတွက် အောက်မှာ တိုက်ရိုက် ပို့ပေးထားပါတယ်ဗျာ။\n\n"
        "⚠️ **သတိပေးချက်** ⚠️\n"
        "မူပိုင်ခွင့် (Copyright) ဥပဒေအရ ဤဇာတ်ကားဖိုင်သည် ပို့ပြီး **၂ မိနစ်ပြည့်ပါက အလိုအလျောက် ပျက်သွားမည်** ဖြစ်သည်။ "
        "ထို့ကြောင့် ဇာတ်ကားကို အပြီးသိမ်းထားလိုပါက ပို့ပေးထားသော ဖိုင်ကို ဖိနှိပ်၍ မိမိ၏ **Saved Messages** (သိမ်းဆည်းထားသော မက်ဆေ့ခ်ျများ) ထဲသို့ ချက်ချင်း **Forward (လက်ဆင့်ကမ်း)** လုပ်ပြီး သိမ်းဆည်းထားပါဗျာ။\n\n"
        "👑 **VIP Movie Channel အစီအစဉ်** 👑\n"
        "တရုတ်/ကိုရီးယားဇာတ်လမ်းတွဲများ၊ အသစ်ထွက်ရုပ်ရှင်များနှင့် Netflix မှရုပ်ရှင်များကို "
        "တစ်လ ၅,၀၀၀ ကျပ်တည်းဖြင့် VIP Member အဖြစ်ဝင်ရောက်ကြည့်ရှုနိုင်ပါတယ်ဗျာ။\n\n"
        "👉 VIP ဝင်ရန် Admin acc - @Lynn_subflix528 ကို ဆက်သွယ်လိုက်ပါဗျို့။"
    )
    
    # VIP စာသားကို အရင်ပို့ခြင်း
    bot.send_message(chat_id, welcome_text)
    
    # လင့်ခ်ကနေ ဇာတ်ကား ID ပါလာခဲ့လျှင် (ဥပမာ စမ်းသပ်ရန်)
    if len(command_args) > 1:
        movie_id = command_args[1]
        
        # ဇာတ်ကားဖိုင် တိုက်ရိုက်ပို့ခြင်း (ဤနေရာတွင် ဇာတ်ကားဖိုင် ပို့မည့်ကုဒ် ထည့်ရမည်)
        # ဥပမာ - bot.send_video(chat_id, video=movie_file_id)
        sent_movie = bot.send_message(chat_id, f"🎬 [ဒီနေရာတွင် သင့်ဇာတ်ကားဖိုင် ပေါ်လာမည် - Movie ID: {movie_id}]")
        
        # ပို့ပြီးတာနဲ့ ၂ မိနစ်ပြည့်ရင် ဖျက်ဖို့ Thread မောင်းလိုက်ခြင်း
        threading.Thread(target=auto_delete_message, args=(chat_id, sent_movie.message_id)).start()

# အခြား စာရိုက်မှုများကို တုံ့ပြန်ရန်
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "ဇာတ်ကားများကို Channel ထဲရှိ လင့်ခ်များမှတစ်ဆင့် တိုက်ရိုက် ရယူနိုင်ပါသည် ခင်ဗျာ။")

# Render Webhook ရယူခြင်း
@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://subflix-movies-bot.onrender.com/' + BOT_TOKEN)
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
