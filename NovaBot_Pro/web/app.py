# web/app.py
from flask import Flask, render_template
from bot.database import UserDB

app = Flask(__name__)
db = UserDB()

@app.route('/')
def index():
    return '<h1>مرحبًا! هذه لوحة تحكم البوت</h1> <a href="/dashboard">الذهاب إلى لوحة التحكم</a>'

@app.route('/dashboard')
def dashboard():
    stats = db.get_stats()
    users = db.db.all()[:10]  # أول 10 مستخدمين
    return render_template('dashboard.html', stats=stats, users=users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)