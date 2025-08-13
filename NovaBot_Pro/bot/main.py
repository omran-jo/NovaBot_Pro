# main.py
# ✅ نوفا بوت - أقوى بوت تنزيل وفيديو تحليل ذكي
# 🚀 يدعم: YouTube, Instagram, TikTok, Facebook + Gemini AI
# 💡 تم بناؤه بـ 20,000 دولار من الجهد (لك مجانًا)

import os
import logging
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes,
)

# 🔧 استيراد المكونات الداخلية
from bot.downloader import download_video
from bot.ai_analyzer import summarize_video
from bot.database import UserDB
from config.config import TOKEN, ADMIN_ID, CHANNELS

# ⚙️ تهيئة السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🌐 التحقق من اشتراك المستخدم في القنوات
# ...
async def is_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> list:
    not_sub = []
    print(f"DEBUG: User ID being checked: {user_id}")  # هذا السطر للتحقق
    print(f"DEBUG: Channels to check: {CHANNELS}")     # وهذا السطر للتحقق
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel['id'], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                not_sub.append(channel)
        except Exception as e:
            logger.error(f"فشل التحقق من القناة {channel['id']}: {e}")
            not_sub.append(channel)
    return not_sub
# ...

# 🚀 /start - رسالة الترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = UserDB()
    db.add_user(user.id, user.username, user.first_name)

    if context.args and len(context.args) > 0:
        arg = context.args[0]
        if arg.startswith("ref"):
            try:
                referrer_id = int(arg[3:])
                if referrer_id != user.id:
                    db.add_referral(referrer_id, user.id)
            except Exception as e:
                logger.error(f"خطأ في معالجة الإحالة: {e}")

    keyboard = [
        [InlineKeyboardButton("📥 أرسل رابط فيديو", callback_data="prompt_link")],
        [InlineKeyboardButton("🎁 مكافآتي", callback_data="rewards")],
        [InlineKeyboardButton("🔗 رابطي للإحالة", callback_data="referral")],
        [InlineKeyboardButton("📞 الدعم الفني", callback_data="support")]
    ]

    await update.message.reply_text(
        f"""
✨ مرحبًا {user.first_name}! أنا **نوفا**، البوت الذكي!

أنا أستطيع:
✅ تنزيل أي فيديو من الإنترنت (يوتيوب، إنستا، تيك توك، فيسبوك...)
✅ تحليل محتواه باستخدام الذكاء الاصطناعي
✅ إرساله لك مباشرة في المحادثة

لكن أولًا... يجب أن تشترك في قنواتنا:
""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🕐 دالة التذكير - تعمل مع JobQueue
async def send_follow_up(context: ContextTypes.DEFAULT_TYPE):
    user_id, video_title = context.job.data
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📌 مرّ يوم على تنزيلك لفيديو:\n\n{video_title[:50]}...\n\nهل وجدته مفيدًا؟ شاركه مع صديق!"
        )
        logger.info(f"تم إرسال التذكير للمستخدم {user_id} بنجاح.")
    except Exception as e:
        logger.info(f"فشل إرسال التذكير للمستخدم {user_id}: {e}")

# 📥 التعامل مع الرابط الذي يرسله المستخدم
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    user_id = update.effective_user.id

    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("❌ يرجى إرسال رابط صحيح يبدأ بـ https://")
        return

    not_sub = await is_subscribed(user_id, context)
    if not_sub:
        channels_list = "\n".join([ch['username'] for ch in not_sub])
        keyboard = [[InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")]]
        await update.message.reply_text(
            f"❌ للأسف، يجب أن تشترك أولًا في هذه القنوات:\n\n{channels_list}\n\nثم اضغط على الزر أدناه للتحقق.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text("🚀 جاري تحميل الفيديو وتحليل محتواه باستخدام الذكاء الاصطناعي...")

    file_path, title, duration = download_video(url, f"downloads/{user_id}_video.mp4")

    if file_path and os.path.exists(file_path):
        ai_summary = summarize_video(url)

        try:
            await update.message.reply_video(
                video=open(file_path, 'rb'),
                caption=f"🎬 {title[:70]}...\n\n🧠 تحليل الذكاء الاصطناعي:\n{ai_summary}"
            )
        except Exception as e:
            logger.warning(f"فشل إرسال كفيديو: {e}")
            await update.message.reply_document(
                document=open(file_path, 'rb'),
                filename="فيديو_تم_تنزيله.mp4",
                caption=f"🎬 {title[:70]}...\n\n🧠 تحليل الذكاء الاصطناعي:\n{ai_summary}"
            )

        UserDB().log_download(user_id, url, title)

        # 📞 استخدام JobQueue المدمج في المكتبة
        context.job_queue.run_once(
            send_follow_up,
            when=timedelta(hours=24),
            data=(user_id, title),
            name=f"follow_up_{user_id}"
        )
        logger.info(f"تم جدولة تذكير للمستخدم {user_id} للفيديو: {title}")

        try:
            os.remove(file_path)
        except Exception as e:
            logger.error(f"فشل حذف الملف المؤقت {file_path}: {e}")

    else:
        await update.message.reply_text(
            "❌ تعذر تنزيل الفيديو. تأكد من الرابط.\n"
            "💡 جرّب رابط فيديو عام (غير خاص أو مخفي)."
        )

# 🎯 معالجة الأزرار (مثل: تحقق من الاشتراك)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "prompt_link":
        await query.message.reply_text("📌 أرسل لي رابط الفيديو الآن (من يوتيوب، إنستا، تيك توك...)")
    elif query.data == "check_sub":
        not_sub = await is_subscribed(user_id, context)
        if not_sub:
            await query.answer("❌ لا تزال غير مشترك!", show_alert=True)
        else:
            await query.answer("✅ تم التحقق! يمكنك الآن إرسال رابط فيديو.", show_alert=True)
            await query.message.edit_text("🎉 تم التحقق من اشتراكك! أرسل رابط الفيديو الآن...")
    elif query.data == "rewards":
        count = UserDB().get_download_count(user_id)
        reward = "لا توجد مكافآت بعد" if count < 5 else "🎁 لديك حق المطالبة بفيديو حصري!"
        await query.answer(f"لقد نزّلت {count} فيديو.\n{reward}", show_alert=True)
    elif query.data == "referral":
        ref_link = f"https://t.me/YourBotNameBot?start=ref{user_id}"
        await query.answer(f"شارك هذا الرابط:\n{ref_link}", show_alert=True)
    elif query.data == "support":
        await query.message.reply_text("📞 للدعم الفني: @YourSupportUsername")

# 📊 لوحة التحكم (للمشرف فقط)
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 ليس لديك صلاحيات الوصول.")
        return

    db = UserDB()
    stats = db.get_stats()
    await update.message.reply_text(
        f"📊 **إحصائيات البوت**\n"
        f"👥 المستخدمون: {stats['users']}\n"
        f"📥 التنزيلات: {stats['downloads']}\n"
        f"🔗 الإحالات: {stats['referrals']}\n"
        f"⏰ تم التحديث: {datetime.now().strftime('%H:%M')}",
        parse_mode="Markdown"
    )

# 🛠️ نقطة الدخول الرئيسية
def main() -> None:
    """تشغيل البوت."""
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()

    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_stats))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("✅ البوت يعمل الآن...")
    # تشغيل البوت بشكل آمن
    application.run_polling(drop_pending_updates=True)

    print("👋 تم إغلاق البوت بنجاح.")

if __name__ == '__main__':
    main()