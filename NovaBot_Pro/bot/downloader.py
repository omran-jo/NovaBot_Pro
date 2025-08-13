# bot/downloader.py
import yt_dlp
import os


def download_video(url: str, output_path: str = "downloads/video.mp4") -> tuple:
    """
    تنزيل فيديو من أي رابط (يوتيوب، إنستا، تيك توك، فيسبوك...إلخ)

    :param url: رابط الفيديو
    :param output_path: مسار الحفظ المؤقت
    :return: (مسار_الملف, العنوان, المدة_بالدقائق) أو (None, None, None) عند الفشل
    """
    # التأكد من وجود مجلد التنزيلات
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    ydl_opts = {
        'format': 'best[height<=1080]',  # أفضل جودة حتى 1080p
        'outtmpl': output_path,  # مكان الحفظ
        'noplaylist': True,  # لا تنزّل قوائم
        'quiet': True,  # لا تظهر تفاصيل كثيرة
        'no_warnings': True,
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'http_headers': {
            'Referer': 'https://www.google.com/',
            'Origin': 'https://www.google.com'
        },
        # دعم أوسع للمواقع
        'extractor_retries': 3,
        'ignoreerrors': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'فيديو بدون عنوان')
            duration = info.get('duration', 0) // 60  # بالدقائق
            filepath = ydl.prepare_filename(info)
            # تغيير الامتداد إذا لزم
            if not os.path.exists(filepath):
                filepath = output_path  # البديل
            return filepath, title, duration

    except Exception as e:
        print(f"[downloader.py] خطأ في التنزيل: {e}")
        return None, None, None


# --------------------------
# ✅ دالة تجريبية (للتحقق)
# --------------------------
if __name__ == "__main__":
    # مثال على استخدام الدالة
    url = input("أدخل رابط الفيديو: ").strip()
    path, title, duration = download_video(url, "downloads/test_video.mp4")

    if path and os.path.exists(path):
        print(f"✅ تم التنزيل: {title}")
        print(f"📁 المسار: {path}")
        print(f"⏱️ المدة: {duration} دقيقة")
    else:
        print("❌ فشل التنزيل. تحقق من الرابط.")