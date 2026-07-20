import telebot
import os
import time
import threading
from flask import Flask

app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"

# ၁။ ပြင်ဆင်ရန် - သင့်ရဲ့ Bot Token ကို သေချာပြန်ထည့်ပါ
TELEGRAM_BOT_TOKEN = "8609626698:AAFX9be-pwkM7nn_vMRTwx-1ut97HfMhhmQ"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# ၂။ ပြင်ဆင်ရန် - သင့်ရဲ့ Telegram အကောင့် Username ကို @ မပါဘဲ ထည့်ပါ
ADMIN_USERNAME = "Lynn_subflix528" 

# ဇာတ်ကား Database (လင့်ခ်နေရာတွင် Telegram ကားဖိုင် Post Link ကို ထည့်ပါ)
MOVIE_DATABASE = {
    "green mile": "https://t.me/c/4321974022/5", 
}

# ဇာတ်ကားကို ၂ မိနစ် (စက္ကန့် ၁၂၀) ပြည့်ရင် Auto ဖျက်မည့် Function
def delete_message_after_delay(chat_id, message_id, delay=120):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

# ဇာတ်ကားပေးပို့ပြီး Auto-Delete လုပ်မည့် စနစ်
def send_movie_and_manage(chat_id, movie_key):
    target_movie = MOVIE_DATABASE[movie_key]
    
    warning_text = (
        f"🎬 **လူကြီးမင်းတောင်းဆိုထားသော ဇာတ်ကား ရောက်ပါပြီဗျာ**\n\n"
        f"🔗 [ဒီလင့်ခ်ကိုနှိပ်ပြီး ဇာတ်ကားကြည့်ပါ/ဒေါင်းပါ]({target_movie})\n\n"
        f"Copyright ဥပဒေကြောင့် ဤစာသည် **၂ မိနစ်** ပြည့်ပါက အလိုအလျောက် ပျက်သွားပါလိမ့်မည်။ "
        f"အမြဲသိမ်းဆည်းထားလိုပါက ယခုစာကို ဖိနှိပ်၍ လူကြီးမင်း၏ **Saved Messages** ထဲသို့ ချက်ချင်း Forward လုပ်ပြီး သိမ်းဆည်းထားပါဗျို့။"
    )
    
    sent_msg = bot.send_message(chat_id, warning_text, parse_mode="Markdown")
    threading.Thread(target=delete_message_after_delay, args=(chat_id, sent_msg.message_id, 120)).start()

# /start လင့်ခ်မှတစ်ဆင့် ဝင်လာလျှင်
@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    if len(args) > 1:
        movie_key = args[1].replace("_", " ").lower()
        if movie_key in MOVIE_DATABASE:
            send_movie_and_manage(message.chat.id, movie_key)
            return
            
    welcome_text = (
        "မင်္ဂလာပါ။ 🎬 ဇာတ်ကားနာမည်ကို စာလုံးအသေးဖြင့် ရိုက်နှိပ်ရှာဖွေနိုင်ပါတယ်ဗျာ။\n"
        "ဥပမာ - green mile\n\n"
        "👑 **VIP Movie Channel အစီအစဉ်** 👑\n"
        "တစ်လလျှင် ၅,၀၀0 ကျပ်တည်းဖြင့် VIP Member ဝင်ရောက်ပြီး အောက်ပါ အထူးအခွင့်အရေးများကို ရယူပါ -\n\n"
        "၁။ 🎬 ဇာတ်ကားများကို လင့်ခ်ကျော်စရာမလိုဘဲ တိုက်ရိုက် (Direct File) ကြည့်ရှုနိုင်ခြင်း။\n"
        "၂။ ⏳ ၂ မိနစ်ပြည့်ပါက အလိုအလျောက်ပျက်သည့်စနစ် မရှိဘဲ စိတ်ကြိုက် ပြန်ကြည့်နိုင်ခြင်း။\n"
        "၃။ 📺 Netflix စီးရီးတွဲများနှင့် ဇာတ်လမ်းတွဲ အစအဆုံးများကို Exclusive ကြည့်ရှုနိုင်ခြင်း။\n"
        "၄။ 💬 မိမိကြည့်ချင်သော ဇာတ်ကားများကို Admin ထံ တိုက်ရိုက်တောင်းဆိုနိုင်ခြင်း။\n\n"
        f"👉 လူကြီးမင်း VIP ဝင်ရန်အတွက် Admin အကောင့် https://t.me/Lynn_subflix528 သို့ ချက်ချင်း ဆက်သွယ်လိုက်ပါဗျာ။"
    )
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

# စာသားရိုက်ရှာလျှင်
@bot.message_handler(func=lambda message: True)
def search_movie(message):
    search_query = message.text.lower().strip()
    
    if search_query in MOVIE_DATABASE:
        send_movie_and_manage(message.chat.id, search_query)
    else:
        fail_text = (
            "❌ စိတ်မကောင်းပါဘူးဗျာ၊ အဲဒီဇာတ်ကားက ကျွန်ုပ်တို့ Database ထဲမှာ မရှိသေးပါဘူး။\n\n"
            "👑 တရုတ်/ကိုရီးယားဇာတ်လမ်းတွဲများ၊ အသစ်ထွက်ရုပ်ရှင်များနှင့် Netflix မှရုပ်ရှင်များကို တစ်လ ၅,၀၀၀ ကျပ်တည်းဖြင့် VIP Memberအဖြစ်ဝင်ရောက်ကြည့်ရှုနိုင်ပါတယ်။\n"
            f"👉 Vip ဝင်ရန် Admin acc - @{Lynn_subflix528} ကို ဆက်သွယ်လိုက်ပါဗျို့။"
        )
        bot.reply_to(message, fail_text)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    threading.Thread(target=lambda: bot.infinity_polling(timeout=10, long_polling_timeout=5)).start()
    app.run(host='0.0.0.0', port=port)
