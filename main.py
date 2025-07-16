import os
from quart import Quart, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

app = Quart(__name__)
application = Application.builder().token(TOKEN).updater(None).build()

# 10 уроков
lessons = [
    {"text": "👋 Урок 1", "url": "https://youtu.be/vid1"},
    {"text": "📘 Урок 2", "url": "https://youtu.be/vid2"},
    {"text": "📗 Урок 3", "url": "https://youtu.be/vid3"},
    {"text": "📕 Урок 4", "url": "https://youtu.be/vid4"},
    {"text": "🎯 Урок 5 — Сделай домашку!", "url": "https://youtu.be/vid5"},
    {"text": "🚀 Урок 6", "url": "https://youtu.be/vid6"},
    {"text": "🎓 Урок 7", "url": "https://youtu.be/vid7"},
    {"text": "💡 Урок 8", "url": "https://youtu.be/vid8"},
    {"text": "🔍 Урок 9", "url": "https://youtu.be/vid9"},
    {"text": "🏁 Финальный Урок", "url": "https://youtu.be/vid10"},
]

user_progress = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_progress[user_id] = 0
    await send_lesson(update.effective_chat.id, user_id, context)

# Обработка нажатий кнопок
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    index = user_progress.get(user_id, 0)

    if query.data == "next":
        index += 1
    elif query.data == "finish":
        await query.message.reply_text("✅ Курс завершён! Поздравляю 🎉")
        await query.answer()
        return

    user_progress[user_id] = index
    await send_lesson(query.message.chat.id, user_id, context)
    await query.answer()

# Отправка текущего урока
async def send_lesson(chat_id, user_id, context, override=None):
    index = override if override is not None else user_progress.get(user_id, 0)

    if index >= len(lessons):
        await context.bot.send_message(chat_id, "🎉 Все уроки завершены!")
        return

    lesson = lessons[index]
    text = f"{lesson['text']}\n{lesson['url']}"

    # Выбор кнопки в зависимости от урока
    if index == 4:
        button = InlineKeyboardButton("📚 Я выполнил ДЗ, хочу идти дальше", callback_data="next")
    elif index == 9:
        button = InlineKeyboardButton("🏁 Завершить курс", callback_data="finish")
    else:
        button = InlineKeyboardButton("✅ Я просмотрел урок, хочу следующий!", callback_data="next")

    keyboard = InlineKeyboardMarkup([[button]])
    await context.bot.send_message(chat_id, text, reply_markup=keyboard)

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_button))

@app.route("/")
async def root():
    return "🤖 Telegram bot is running!"

@app.post(f"/{TOKEN}")
async def webhook():
    data = await request.get_json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

if __name__ == "__main__":
    import asyncio

    async def main():
        await application.initialize()
        await application.start()
        await application.bot.set_webhook(f"https://telegram-bot-akmz.onrender.com/{TOKEN}")
        await app.run_task(host="0.0.0.0", port=5000)

    asyncio.run(main())
