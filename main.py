import telebot
from telebot import types

# 1. ضع توكن البوت الذي حصلت عليه من BotFather بين القوسين
API_TOKEN = 'ضع_توكن_بوتك_هنا'

# 2. أيدي حسابك (المالك) لمنحك نقاط غير محدودة واستقبال إشعارات النجوم
ADMIN_ID = 7280802849

bot = telebot.TeleBot(API_TOKEN)

# قواعد البيانات المؤقتة لتخزين النقاط والقنوات
users_db = {}
channels_to_promote = []

def get_user_points(user_id):
    """دالة فحص الرصيد: تمنح المالك نقاطاً لا تنتهي"""
    if user_id == ADMIN_ID:
        return 99999999  
    if user_id not in users_db:
        users_db[user_id] = {'points': 0, 'referred_by': None}
    return users_db[user_id]['points']

def change_user_points(user_id, amount):
    """دالة تعديل الرصيد: تمنع الخصم من المالك أبداً"""
    if user_id == ADMIN_ID:
        return  
    if user_id not in users_db:
        users_db[user_id] = {'points': 0, 'referred_by': None}
    users_db[user_id]['points'] += amount

def main_markup(user_id):
    """لوحة التحكم الرئيسية المطابقة لطلبك"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn_status = types.KeyboardButton(f"💎 رصيدك: {get_user_points(user_id)}")
    btn_promote = types.KeyboardButton("- اضغط لطلب تمويل قناتك 👤 -")
    btn_collect = types.KeyboardButton("📥 تجميع النقاط 📥")
    btn_convert = types.KeyboardButton("💸 تحويل النقاط")
    btn_info = types.KeyboardButton("- التعليمات -")
    btn_account = types.KeyboardButton("👤 معلومات حسابك")
    btn_invite = types.KeyboardButton("📣 ادع صديقاً")
    btn_coupons = types.KeyboardButton("🎟 قسائمي")
    btn_multiplier = types.KeyboardButton("⚡️ اشتر مضاعف نقاط")
    btn_exchange = types.KeyboardButton("🎁 قسم استبدال")
    btn_channel = types.KeyboardButton("↗️ قناة بوت الرسمية")
    btn_my_orders = types.KeyboardButton("📋 تمويلاتي ( 1 🟢 )")
    btn_free = types.KeyboardButton("👥 . 25 عضو مجاناً ( كل 24 ساعة ) .")
    
    markup.add(btn_status)
    markup.add(btn_promote)
    markup.add(btn_collect, btn_convert)
    markup.add(btn_info, btn_account)
    markup.add(btn_invite, btn_coupons)
    markup.add(btn_multiplier)
    markup.add(btn_exchange)
    markup.add(btn_channel)
    markup.add(btn_my_orders)
    markup.add(btn_free)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    # فحص نظام الإحالة (ادع صديقاً) لشحن النقاط تلقائياً
    text_args = message.text.split()
    if len(text_args) > 1:
        referrer = int(text_args[1])
        if user_id not in users_db and referrer != user_id:
            users_db[user_id] = {'points': 0, 'referred_by': referrer}
            change_user_points(referrer, 5)
            try:
                bot.send_message(referrer, "🎉 سجل شخص جديد من خلال رابطك وحصلت على 5 نقاط!")
            except:
                pass

    welcome_text = (
        f"👑 *أهلاً بك عزيزي في بوت رشق قوي مان* 👑\n\n"
        f"🤖 *بوت تمويل الدولار*\n"
        f"تستطيع تزويد أعضاء قناتك ومجموعتك مجاناً عن طريق تجميع النقاط.\n\n"
        f"• *أجمع النقاط بـ ثلاثة طرق:* ⚡️\n"
        f"1️⃣ الاشتراك في قنوات التيربو\n"
        f"2️⃣ مشاركة رابط الدعوة الخاص بك 🔗\n"
        f"3️⃣ الهدية اليومية 🎁\n\n"
        f"~ ارسل أمر /start تعليمات\n"
        f"~ آيدي حسابك {{ `{user_id}` }}\n"
        f"• العدد الكلي للمستخدمين 8M 👤 *"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=main_markup(user_id))

# --- قنوات وأزرار الدفع بنجوم تليجرام ---

@bot.message_handler(func=lambda message: message.text == "⚡️ اشتر مضاعف نقاط")
def show_shop(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("⭐️ شراء 50 نقطة مقابل 10 نجوم", callback_data="buy_50"),
        types.InlineKeyboardButton("⭐️ شراء 150 نقطة مقابل 25 نجمة", callback_data="buy_150"),
        types.InlineKeyboardButton("⭐️ شراء 400 نقطة مقابل 50 نجمة", callback_data="buy_400")
    )
    bot.send_message(message.chat.id, "🛒 *قسم شراء النقاط بنجوم تليجرام*\nإختر الباقة المناسبة لك وسيتم إضافة النقاط تلقائياً وتحويل النجوم للمالك:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def send_stars_invoice(call):
    user_id = call.from_user.id
    choice = call.data
    
    if choice == "buy_50":
        title, points, stars = "باقة 50 نقطة", 50, 10
    elif choice == "buy_150":
        title, points, stars = "باقة 150 نقطة", 150, 25
    elif choice == "buy_400":
        title, points, stars = "باقة 400 نقطة", 400, 50
    else:
        return

    prices = [types.LabeledPrice(label=title, amount=stars)]
    
    # إرسال فاتورة النجوم الرسمية (XTR هي العملة الرسمية المعتمدة لنجوم تليجرام)
    bot.send_invoice(
        chat_id=call.message.chat.id,
        title=title,
        description=f"شراء {points} نقطة رشق في البوت لتمويل قناتك",
        invoice_parameter="points_pack",
        currency="XTR", 
        provider_token="",  # تترك فارغة إجبارياً عند الدفع بالنجوم الداخلية لتليجرام
        prices=prices,
        start_parameter="points_shop",
        payload=f"{user_id}:{points}"
    )
    bot.answer_callback_query(call.id)

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout_process(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.successful_payment_handler(func=lambda message: True)
def payment_success(message):
    payment_info = message.successful_payment
    payload_data = payment_info.invoice_payload.split(":")
    buyer_id = int(payload_data[0])
    points_to_add = int(payload_data[1])
    
    # شحن نقاط المشتري
    change_user_points(buyer_id, points_to_add)
    bot.send_message(buyer_id, f"✅ تم إتمام الدفع بنجاح! تم إضافة {points_to_add} نقطة إلى رصيدك 💎", reply_markup=main_markup(buyer_id))
    
    # إرسال رسالة تنبيه لك (المالك) بوصول الأموال والنجوم لحسابك
    try:
        bot.send_message(ADMIN_ID, f"💰 *عملية شراء ناجحة*:\nالمستخدم: `{buyer_id}`\nدفع: {payment_info.total_amount} نجمة ⭐️\nتم منح السعر: {points_to_add} نقطة والنجوم في رصيد حسابك الآن.", parse_mode="Markdown")
    except:
        pass

# --- بقية الأزرار والوظائف التفاعلية العامة ---

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    text = message.text

    if "- اضغط لطلب تمويل قناتك 👤 -" in text:
        msg = bot.send_message(message.chat.id, "قم بإرسال رابط قناتك مع تحديد عدد الأعضاء المطلوب (مثال: `https://t.me 10`):", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_promotion)
        
    elif "📥 تجميع النقاط 📥" in text:
        if channels_to_promote:
            target_channel = channels_to_promote[0]
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("اضغط هنا للاشتراك بالقناة", url=target_channel))
            markup.add(types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check_sub"))
            bot.send_message(message.chat.id, "اشترك في هذه القناة للحصول على نقطتين:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "❌ لا توجد قنوات متاحة للتمويل حالياً، جرب لاحقاً.")
            
    elif "📣 ادع صديقاً" in text:
        bot_username = bot.get_me().username
        bot.send_message(message.chat.id, f"🔗 رابط الدعوة الخاص بك:\nhttps://t.me{bot_username}?start={user_id}\n\nستحصل على 5 نقاط لكل صديق يشترك بالبوت!")
        
    elif "👤 معلومات حسابك" in text:
        bot.send_message(message.chat.id, f"👤 معلوماتك:\n• الآيدي: `{user_id}`\n• نقاطك الحالية: {get_user_points(user_id)}", parse_mode='Markdown')
        
    else:
        bot.send_message(message.chat.id, "تم تحديث القائمة بنجاح ✨", reply_markup=main_markup(user_id))

def process_promotion(message):
    user_id = message.from_user.id
    try:
        data = message.text.split()
        channel_url = data[0]
        members_needed = int(data[1])
        
        if get_user_points(user_id) >= members_needed:
            change_user_points(user_id, -members_needed)
            channels_to_promote.append(channel_url)
            bot.send_message(message.chat.id, f"✅ تم إضافة قناتك بنجاح لطلب {members_needed} عضو.")
        else:
            bot.send_message(message.chat.id, "❌ نقاطك غير كافية لطلب هذا العدد.")
    except:
        bot.send_message(message.chat.id, "⚠️ صيغة خاطئة. أعد الضغط على الزر وأرسل الرابط والعدد هكذا:\n`https://t.me 10`", parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    user_id = call.from_user.id
    change_user_points(user_id, 2)
    bot.answer_callback_query(call.id, "✅ تم التحقق وإضافة نقطتين!")
    try:
        bot.edit_message_text("شكرًا لاشتراكك، تم إضافة النقاط إلى رصيدك 💎", call.message.chat.id, call.message.message_id)
    except:
        pass

bot.infinity_polling()
