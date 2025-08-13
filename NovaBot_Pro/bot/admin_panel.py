async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    stats = {
        'users': len(database.UserDB().db),
        'downloads': len(database.UserDB().downloads),
        'referrals': len(database.UserDB().referrals)
    }
    await update.message.reply_text(
        f"📊 الإحصائيات:\n"
        f"المستخدمون: {stats['users']}\n"
        f"التنزيلات: {stats['downloads']}\n"
        f"الإحالات: {stats['referrals']}"
    )