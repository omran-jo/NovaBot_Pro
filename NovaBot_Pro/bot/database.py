# bot/database.py
import os
import tinydb
from datetime import datetime


class UserDB:
    def __init__(self):
        # 1. التأكد من وجود مجلد 'data'
        # هذا السطر يحل مشكلة FileNotFoundError
        if not os.path.exists('data'):
            os.makedirs('data')

        # 2. الآن يمكن إنشاء قواعد البيانات بأمان
        self.db = tinydb.TinyDB('data/users.json')
        self.downloads = tinydb.TinyDB('data/downloads.json')
        self.referrals = tinydb.TinyDB('data/referrals.json')

    def add_user(self, user_id, username, name):
        """إضافة مستخدم جديد"""
        if not self.db.search(tinydb.Query().user_id == user_id):
            self.db.insert({
                'user_id': user_id,
                'username': username,
                'name': name,
                'join_date': datetime.now().isoformat(),
                'downloads': 0
            })

    def log_download(self, user_id, url, title):
        """تسجيل تنزيل فيديو"""
        self.downloads.insert({
            'user_id': user_id,
            'url': url,
            'title': title,
            'time': datetime.now().isoformat()
        })
        # تحديث عدد التنزيلات
        user = self.db.search(tinydb.Query().user_id == user_id)
        if user:
            new_count = user[0]['downloads'] + 1
            self.db.update({'downloads': new_count}, tinydb.Query().user_id == user_id)

    def add_referral(self, referrer_id, referred_id):
        """تسجيل إحالة"""
        self.referrals.insert({
            'referrer': referrer_id,
            'referred': referred_id,
            'date': datetime.now().isoformat()
        })

    def get_download_count(self, user_id):
        """الحصول على عدد التنزيلات"""
        user = self.db.search(tinydb.Query().user_id == user_id)
        return user[0]['downloads'] if user else 0

    def get_stats(self):
        """إحصائيات عامة"""
        return {
            'users': len(self.db),
            'downloads': len(self.downloads.all()),
            'referrals': len(self.referrals.all())
        }