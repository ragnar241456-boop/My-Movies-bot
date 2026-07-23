import os
import time
import threading
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Telegram Bot Token နှင့် Storage Channel ID သတ်မှတ်ခြင်း
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8609626698:AAFX9be-pwkM7nn_vMRTwx-1ut97HfMhhmQ")
STORAGE_CHANNEL_ID = -1004321974022  # သင့် Private Channel ID

# Force Join စစ်ဆေးမည့် Public Channel Username
FORCE_SUB_CHANNEL = "@subflix_mm" 

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# Webhook အတွက် Flask App
app = Flask(__name__)

# User Channel ဝင်ထားခြင်း ရှိ/မရှိ စစ်ဆေးသည့် Helper Function
def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        print(f"Error checking channel membership: {e}")
        # Bot ကို Admin မခန့်ထားပါက သို့မဟုတ် Username မှားနေပါက Error မတက်ဘဲ Pass ပေးမည်
        return True

# Channel မဝင်ရသေးပါက ပြသမည့် Message နှင့် Button များ
def send_force_sub_message(chat_id, start_param=""):
    markup = InlineKeyboardMarkup()
    
    # Channel သို့ သွားရန် Link ခလုတ်
    channel_url = f"https://t.me/{FORCE_SUB_CHANNEL.replace('@', '')}"
    join_btn = InlineKeyboardButton("📢 Public Channel သို့ဝင်ရန်", url=channel_url)
    
    # Channel Join ပြီးပါက ပြန်လည် စစ်ဆေးမည့် ခလုတ်
    cb_data = f"check_sub_{start_param}" if start_param else "check_sub"
    try_again_btn = InlineKeyboardButton("✅ Joined (ဝင်ပြီးပါပြီ ပြန်စစ်မည်)", callback_data=cb_data)
    
    markup.add(join_btn)
    markup.add(try_again_btn)
    
    force_text = (
        "⚠️ **သတိပေးချက်** ⚠️\n\n"
        "ဇာတ်ကား/စီးရီးများကို ကြည့်ရှုနိုင်ရန်အတွက် ကျွန်ုပ်တို့၏ **Public Channel** ကို အရင် **Join** ပေးထားရန် လိုအပ်ပါသည်ဗျာ။\n\n"
        "အောက်ပါ ခလုတ်ကို နှိပ်၍ Channel ထဲသို့ ဝင်ရောက်ပြီးပါက **'✅ Joined'** ခလုတ်ကို နှိပ်ပါ။"
    )
    bot.send_message(chat_id, force_text, reply_markup=markup, parse_mode="Markdown")

# မက်ဆေ့ခ်ျကို ၂ မိနစ် (စက္ကန့် ၁၂၀) ပြည့်ရင် Auto ဖျက်မည့် Function
def auto_delete_message(chat_id, message_id):
    time.sleep(120)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

# VIP ကြော်ငြာစာသား (ဈေးနှုန်း ပြင်ဆင်ထားသည်)
VIP_TEXT = (
    "👑 **VIP Movie Channel အစီအစဉ်** 👑\n"
    "တရုတ်/ကိုရီးယားဇာတ်လမ်းတွဲများ၊ အသစ်ထွက်ရုပ်ရှင်များနှင့် Netflix မှရုပ်ရှင်များကို "
    "**၁ လလျှင် ၃,၀၀၀ ကျပ် / ၃ လလျှင် ၅,၀၀၀ ကျပ်** ဖြင့် VIP Member အဖြစ်ဝင်ရောက်ကြည့်ရှုနိုင်ပါတယ်ဗျာ။\n\n"
    "👉 VIP ဝင်ရန် Admin acc - @Lynn_subflix528 ကို ဆက်သွယ်လိုက်ပါဗျို့။"
)

# Start Command (/start) စနစ်
@bot.message_handler(commands=['start'])
def send_movie_and_vip_info(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    command_args = message.text.split()
    param = command_args[1].strip() if len(command_args) > 1 else ""

    # Force Join စစ်ဆေးခြင်း
    if not is_user_joined(user_id):
        send_force_sub_message(chat_id, param)
        return

    # အခြေအနေ ၁ - ဒီအတိုင်း /start နှိပ်ပြီး ဝင်လာသူကို Public Channel Link ပြရန်
    if not param:
        welcome_text = (
            "မင်္ဂလာပါ။ 🎬 SubFlix Movies Bot မှ ကြိုဆိုပါတယ်ဗျာ။\n"
            "ဇာတ်ကားများကို ကျွန်ုပ်တို့၏ Public Channel ထဲရှိ လင့်ခ်များမှတစ်ဆင့် တိုက်ရိုက် ရယူကြည့်ရှုနိုင်ပါတယ်ဗျာ။\n\n"
            f"🔗 **ကျွန်ုပ်တို့၏ Public Channel သို့ဝင်ရန် -** https://t.me/{FORCE_SUB_CHANNEL.replace('@', '')}\n\n" + VIP_TEXT
        )
        bot.send_message(chat_id, welcome_text)
        
    # အခြေအနေ ၂ - Public Channel ကနေ ဇာတ်ကားလင့်ခ်နှိပ်ပြီး ရောက်လာသူ
    else:
        # (A) စီးရီးအလိုက် ပို့ပေးမည့် စနစ် (ဥပမာ - ?start=series_44_59)
        if param.startswith("series_"):
            try:
                parts = param.split("_")
                start_id = int(parts[1])
                end_id = int(parts[2])

                first_msg = bot.send_message(chat_id, "မင်္ဂလာပါ။ 🎬 စီးရီး အပိုင်းများကို သင့်အတွက် အောက်မှာ တိုက်ရိုက် ပို့ပေးနေပါတယ်ဗျာ... ⏳")

                # အပိုင်းအလိုက် တစ်ခုချင်း ပို့ပေးခြင်း
                for msg_id in range(start_id, end_id + 1):
                    try:
                        sent_movie = bot.forward_message(chat_id, from_chat_id=STORAGE_CHANNEL_ID, message_id=msg_id)
                        threading.Thread(target=auto_delete_message, args=(chat_id, sent_movie.message_id)).start()
                        time.sleep(0.5)  # Telegram Rate Limit မမိစေရန် ၀.၅ စက္ကန့်ခြား ပို့မည်
                    except Exception as err:
                        print(f"Error forwarding message {msg_id}: {err}")

                # ပထမ စာသားကို အပြီးမှာ ဖျက်ပေးခြင်း
                try:
                    bot.delete_message(chat_id, first_msg.message_id)
                except Exception as e:
                    print(f"Error deleting first message: {e}")

                # ဒုတိယ သတိပေးချက်စာသား ပို့ခြင်း
                warning_text = (
                    "⚠️ **သတိပေးချက်** ⚠️\n"
                    "မူပိုင်ခွင့် (Copyright) ဥပဒေအရ ဤဇာတ်ကားဖိုင်များသည် ပို့ပြီး **၂ မိနစ်ပြည့်ပါက အလိုအလျောက် ပျက်သွားမည်** ဖြစ်သည်။ "
                    "ထို့ကြောင့် ဇာတ်ကားကို အပြီးသိမ်းထားလိုပါက ပို့ပေးထားသော ဖိုင်များကို ဖိနှိပ်၍ မိမိ၏ **Saved Messages** (သိမ်းဆည်းထားသော မက်ဆေ့ခ်ျများ) ထဲသို့ ချက်ချင်း **Forward (လက်ဆင့်ကမ်း)** လုပ်ပြီး သိမ်းဆည်းထားပါဗျာ။\n\n" + VIP_TEXT
                )
                second_msg = bot.send_message(chat_id, warning_text)
                threading.Thread(target=auto_delete_message, args=(chat_id, second_msg.message_id)).start()

            except Exception as e:
                bot.send_message(chat_id, "⚠️ စီးရီး ရှာဖွေရာတွင် အမှားအယွင်းတစ်ခု ရှိသွားပါသည်။ လင့်ခ်မှန်ကန်မှု ရှိမရှိ ပြန်လည်စစ်ဆေးပေးပါ။")
                print(f"Error forwarding series: {e}")

        # (B) တစ်ကားတည်း / အပိုင်းတစ်ခုတည်း ပို့ပေးမည့် စနစ် (ဥပမာ - ?start=44)
        else:
            try:
                movie_message_id = int(param)
                
                # ၁။ ပထမစာသား အရင်ပို့ခြင်း
                first_msg = bot.send_message(chat_id, "မင်္ဂလာပါ။ 🎬 ဇာတ်ကားကို သင့်အတွက် အောက်မှာ တိုက်ရိုက် ပို့ပေးထားပါတယ်ဗျာ။")
                
                # ၂။ ဗီဒီယိုဖိုင်ကို Forward လုပ်ခြင်း
                sent_movie = bot.forward_message(chat_id, from_chat_id=STORAGE_CHANNEL_ID, message_id=movie_message_id)
                
                # ပထမစာသားကို ပြန်ဖျက်ခြင်း
                try:
                    bot.delete_message(chat_id, first_msg.message_id)
                except Exception as e:
                    print(f"Error deleting first message: {e}")
                    
                # ၃။ ဒုတိယ သတိပေးချက်စာသားကို ပို့ခြင်း
                warning_text = (
                    "⚠️ **သတိပေးချက်** ⚠️\n"
                    "မူပိုင်ခွင့် (Copyright) ဥပဒေအရ ဤဇာတ်ကားဖိုင်သည် ပို့ပြီး **၂ မိနစ်ပြည့်ပါက အလိုအလျောက် ပျက်သွားမည်** ဖြစ်သည်။ "
                    "ထို့ကြောင့် ဇာတ်ကားကို အပြီးသိမ်းထားလိုပါက ပို့ပေးထားသော ဖိုင်ကို ဖိနှိပ်၍ မိမိ၏ **Saved Messages** (သိမ်းဆည်းထားသော မက်ဆေ့ခ်ျများ) ထဲသို့ ချက်ချင်း **Forward (လက်ဆင့်ကမ်း)** လုပ်ပြီး သိမ်းဆည်းထားပါဗျာ။\n\n" + VIP_TEXT
                )
                second_msg = bot.send_message(chat_id, warning_text)
                
                # ၄။ ဖိုင်ရော စာပါ ၂ မိနစ်ပြည့်ရင် ဖျက်ရန် Thread မောင်းခြင်း
                threading.Thread(target=auto_delete_message, args=(chat_id, sent_movie.message_id)).start()
                threading.Thread(target=auto_delete_message, args=(chat_id, second_msg.message_id)).start()
                
            except Exception as e:
                bot.send_message(chat_id, "⚠️ ဇာတ်ကားရှာဖွေရာတွင် အမှားအယွင်းတစ်ခု ရှိသွားပါသည်။ လင့်ခ်မှန်ကန်မှု ရှိမရှိ ပြန်လည်စစ်ဆေးပေးပါ။")
                print(f"Error forwarding movie: {e}")

# '✅ Joined' ခလုတ်ကို နှိပ်လိုက်ပါက Channel ဝင်/မဝင် ပြန်လည် စစ်ဆေးပေးမည့် Handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("check_sub"))
def callback_check_sub(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if is_user_joined(user_id):
        bot.answer_callback_query(call.id, "✅ ကျေးဇူးတင်ပါတယ်! Channel Join ပြီးပါပြီ။")
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except Exception:
            pass
        
        # User နှိပ်ခဲ့သည့် Param အတိုင်း ပြန်လည် ပို့ပေးခြင်း
        param_data = call.data.replace("check_sub_", "").replace("check_sub", "")
        fake_message = call.message
        fake_message.text = f"/start {param_data}".strip()
        fake_message.from_user = call.from_user
        
        send_movie_and_vip_info(fake_message)
    else:
        bot.answer_callback_query(call.id, "⚠️ မဝင်ရသေးပါဘူး! ကျေးဇူးပြု၍ Channel ကို အရင် Join ပေးပါနော်။", show_alert=True)

# အခြား စာရိုက်မှုများကို တုံ့ပြန်ရန်
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"ဇာတ်ကားများကို ကျွန်ုပ်တို့၏ Public Channel (https://t.me/{FORCE_SUB_CHANNEL.replace('@', '')}) ထဲရှိ လင့်ခ်များမှတစ်ဆင့် တိုက်ရိုက် ရယူနိုင်ပါသည် ခင်ဗျာ။")

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
    time.sleep(1)
    app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://subflix-movies-bot.onrender.com")
    bot.set_webhook(url=f"{app_url}/{BOT_TOKEN}")
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
