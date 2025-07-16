import os
from quart import Quart, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

# Quart вместо Flask
app = Quart(__name__)
application = Application.builder().token(TOKEN).updater(None).build()

lessons = [
    {"text": "👋 Урок 1", "url": "https://youtu.be/vid1"},
    {"text": "🚀 Урок 2", "url": "https://youtu.be/vid2"},
    {"text": "🎓 Финал", "url": "https://youtu.be/vid3"}
]
user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_progress[user_id] = 0
    await send_lesson(update.effective_chat.id, user_id, context)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    index = user_progress.get(user_id, 0)

    if query.data == "next":
        index += 1
    elif query.data == "prev" and index > 0:
        index -= 1
    elif query.data == "skip":
        index += 1
    elif query.data == "finish":
        await query.message.reply_text("✅ Курс завершён!")
        await query.answer()
        return

    user_progress[user_id] = index
    await send_lesson(query.message.chat.id, user_id, context)
    await query.answer()

async def send_lesson(chat_id, user_id, context, override=None):
    index = override if override is not None else user_progress.get(user_id, 0)
    if index >= len(lessons):
        await context.bot.send_message(chat_id, "🎉 Все уроки завершены!")
        return

    lesson = lessons[index]
    text = f"{lesson['text']}\n{lesson['url']}"
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Назад", callback_data="prev"),
            InlineKeyboardButton("⏭️ Пропустить", callback_data="skip"),
            InlineKeyboardButton("➡️ Продолжить", callback_data="next")
        ],
        [InlineKeyboardButton("✅ Завершить курс", callback_data="finish")]
    ])
    await context.bot.send_message(chat_id, text, reply_markup=keyboard)

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_button))

# Root
@app.route("/")
async def root():
    return "🤖 Telegram bot is running!"

# Webhook
@app.post(f"/{TOKEN}")
async def webhook():
    data = await request.get_json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

# Startup
if __name__ == "__main__":
    import asyncio

    async def main():
        await application.initialize()
        await application.start()
        await application.bot.set_webhook(f"https://telegram-bot-akmz.onrender.com/{TOKEN}")
        await app.run_task(host="0.0.0.0", port=5000)

    asyncio.run(main())
