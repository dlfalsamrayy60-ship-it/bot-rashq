import telebot
from telebot import types

# 1. تم وضع توكن البوت الخاص بك بنجاح ✅
API_TOKEN = '7871968716:AAEuZGNGEktYqj97nWjDZzft-4P-SSjbDO'

# 2. آيدي حسابك لتلقي الأرباح وصلاحيات الأدمن
ADMIN_ID = 7280802849

# 3. تم وضع معرف قناتك للاشتراك الإجباري بنجاح ✅
REQUIRED_CHANNEL = "@amkbeos" 

bot = telebot.TeleBot(API_TOKEN)

# قواعد البيانات المؤقتة لتخزين رصيد المستخدمين
users_db = {}

def get_user_points(user_id):
    """دالة فحص الرصيد: تمنح المالك نقاطاً لا تنتهي"""
    if user_id == ADMIN_ID:
        return 99999999
    if user_id not in users_db:
        users_db[user_id] = {'points': 0}
    return users_db[user_id]['points']

def change_user_points(user_id, amount):
    """دالة تعديل الرصيد"""
    if user_id == ADMIN_ID:
        return
    if user_id not in users_db:
        users_db[user_id] = {'points': 0}
    users_db[user_id]['points'] += amount

def check_subscription(user_id):
    """دالة التحقق من الاشتراك الإجباري في القناة"""
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception:
        # إذا لم يكن البوت مشرفاً بالقناة بعد، سيمر المشترك تلقائياً لتفادي توقف البوت
        return True

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    # تفعيل الاشتراك الإجباري
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("📢 اشترك في القناة أولاً", url=f"https://t.me{REQUIRED_CHANNEL.replace('@', '')}")
        check_btn = types.InlineKeyboardButton("🔄 تحقق من الاشتراك", callback_data="check_sub")
        markup.add(btn)
        markup.add(check_btn)
        bot.send_message(message.chat.id, f"❌ عذراً عزيزي، يجب عليك الاشتراك في قناة البوت أولاً لتتمكن من استخدامه!\n\nاشترك ثم اضغط على زر التحقق.", reply_markup=markup)
        return

    if user_id not in users_db:
        users_db[user_id] = {'points': 0}
        
    main_menu(message.chat.id, user_id)

def main_menu(chat_id, user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton("🚀 طلب رشق جديد")
    item2 = types.KeyboardButton("⭐ شحن نقاط بالنجوم")
    item3 = types.KeyboardButton("👤 حسابي ورصيدي")
    markup.add(item1, item2, item3)
    bot.send_message(chat_id, f"مرحباً بك في بوت الرشق المطور! 🤖\n\n💰 رصيدك الحالي: {get_user_points(user_id)} نقطة.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check_sub(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        main_menu(call.message.chat.id, user_id)
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك في القناة بعد!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    
    if not check_subscription(user_id):
        send_welcome(message)
        return

    if message.text == "🚀 طلب رشق جديد":
        bot.send_message(message.chat.id, "قريباً.. أرسل رابط قناتك وعدد الأعضاء المطلوبة للرشق.\n💡 ملاحظة: تكلفة العضو الواحد هي 30 نقطة.")
        
    elif message.text == "⭐ شحن نقاط بالنجوم":
        # إرسال فاتورة دفع حقيقية بنجوم تليجرام (Telegram Stars)
        prices = [types.LabeledPrice(label="1000 نقطة رشق", amount=50)] # بقيمة 50 نجمة تليجرام
        bot.send_invoice(
            message.chat.id,
            title="شحن نقاط الرشق ✨",
            description="شحن 1000 نقطة في البوت باستخدام نجوم تليجرام بشكل فوري وآمن.",
            provider_token="", # يترك فارغاً عند الدفع بالنجوم XTR
            currency="XTR",
            prices=prices,
            start_parameter="buy_points",
            payload="points_50_stars"
        )
        
    elif message.text == "👤 حسابي ورصيدي":
        points = get_user_points(user_id)
        bot.send_message(message.chat.id, f"معلومات حسابك:\n👤 الآيدي: {user_id}\n💰 رصيدك: {points} نقطة.")

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    """تضاف النقاط تلقائياً للمستخدم فور نجاح الدفع بالنجوم"""
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload
    
    if payload == "points_50_stars":
        change_user_points(user_id, 1000)
        bot.send_message(message.chat.id, "✅ تم الدفع بنجاح! تم إضافة 1000 نقطة إلى رصيدك فوراً. شكراً لك! ⭐")
        bot.send_message(ADMIN_ID, f"💰 عملية شراء جديدة! قام مستخدم بآيدي {user_id} بشحن نقاط عبر النجوم.")

if __name__ == '__main__':
    print("البوت يعمل الآن مع ميزات النجوم والاشتراك الإجباري...")
    bot.infinity_polling()

