# scheduler.py
import logging
from datetime import datetime, timedelta
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

# 🕹️ مُجدول المهام (للتذكيرات)
scheduler = AsyncIOScheduler()

async def send_follow_up_coroutine(bot: Bot, user_id: int, video_title: str):
    """
    دالة غير متزامنة لإرسال رسالة تذكير إلى المستخدم.
    """
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"📌 مرّ يوم على تنزيلك لفيديو:\n\n{video_title[:50]}...\n\nهل وجدته مفيدًا؟ شاركه مع صديق!"
        )
        logger.info(f"تم إرسال التذكير للمستخدم {user_id} بنجاح.")
    except Exception as e:
        logger.info(f"فشل إرسال التذكير للمستخدم {user_id}: {e}")

def schedule_follow_up(bot: Bot, user_id: int, video_title: str):
    """
    دالة متزامنة تقوم بجدولة مهمة غير متزامنة.
    """
    scheduler.add_job(
        send_follow_up_coroutine, # تمرير الدالة غير المتزامنة مباشرة
        'date',
        run_date=datetime.now() + timedelta(hours=24),
        args=[bot, user_id, video_title]
    )
    logger.info(f"تم جدولة تذكير للمستخدم {user_id} للفيديو: {video_title}")

def start_scheduler_callback(application):
    """
    دالة يتم استدعاؤها لبدء الجدولة.
    """
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler بدأ التشغيل بنجاح مع حلقة الأحداث الخاصة بالبوت.")

def shutdown_scheduler_callback(application):
    """
    دالة يتم استدعاؤها لإيقاف الجدولة.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler تم إيقافه بنجاح.")