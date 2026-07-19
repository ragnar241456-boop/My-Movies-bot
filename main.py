import telebot
import requests
import os
from flask import Flask

app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"

# Token များကို ဖြည့်စွက်ရန်
TELEGRAM_BOT_TOKEN = "8609626698:AAFX9be-pwkM7nn_vMRTwx-1ut97HfMhhmQ"
SHRINKME_API_TOKEN = "8697573017b03e9d1adb33a3afb0f9c27e52b793"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# ဇာတ်ကားနာမည်နှင့် အပိုင်း (၁) မှ ရလာသည့် Private Channel လင့်ခ်များကို တွဲထည့်ရန်
MOVIE_DATABASE = {
    "Green Mile(1999)": "https://t.me/c/4321974022/5",  # နမူနာပြထားခြင်းဖြစ်သည်
    
}

def get_shrinkme_link(long_url):
    api_url = f"https://shrinkme.io/api?api={SHRINKME_API_TOKEN}&url={long_url}"
    try:
        response = requests.get(api_url).json()
        if response.get("status") == "success":
            return response.get("shortenedUrl")
    except:
        pass
    return long_url

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ။ 🎬 ဇာတ်ကားနာမည် ရိုက်ရှာနိုင်ပါတယ်ဗျာ။")

@bot.message_handler(func=lambda message: True)
def search_movie(message):
    query = message.text.lower().strip()
    found_movie = None
    for movie_name in MOVIE_DATABASE:
        if movie_name in query:
            found_movie = movie_name
            break
            
    if found_movie:
        original_link = MOVIE_DATABASE[found_movie]
        bot.reply_to(message, "⏳ ခေတ္တစောင့်ပါ... ဇာတ်ကားလင့်ခ်ကို ထုတ်ပေးနေပါတယ်...")
        short_link = get_shrinkme_link(original_link)
        bot.send_message(message.chat.id, f"🎬 {found_movie.upper()} ဇာတ်ကားရပါပြီ။\n\n👉 အောက်ကလင့်ခ်မှာ ကြည့်ရှု/ဒေါင်းလုဒ်ဆွဲနိုင်ပါပြီ -\n{short_link}")
    else:
        bot.reply_to(message, "❌ စိတ်မရှိပါနဲ့ဗျာ၊ ရှာနေတဲ့ဇာတ်ကား ကျွန်တော့် Database ထဲမှာ မရှိသေးပါဘူး။")

if __name__ == "__main__":
    from threading import Thread
    def run():
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
