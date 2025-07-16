import os
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

# Flask app
bot_app = Flask(__name__)

# Telegram Bot Token из переменных окружения
TOKEN = os.environ.get("7739788468:AAGKfIJD3V-Nl7kafJ6YlBmqp6Qkh8r90R0")
WEBHOOK_PATH = f"/{TOKEN}"

# Уроки
lessons = [
    {"text": "👋 Добро пожаловать! Урок 1", "url": "https://youtu.be/video1"},
    {"text": "🚀 Урок 2", "url": "https://youtu.be/video2"},
    {"text": "🎓 Финал!", "url": "https://youtu.be/video3"}
]

# Прогресс пользователей (в памяти)
user_progress = {}

# Функция отправки урока
async def send_lesson(chat_id, user_id, context: ContextTypes.DEFAULT_TYPE, override=None):
    index = override if override is not None else user_progress.get(user_id, 0)
    if index >= len(lessons):
        await context.bot.send_message(chat_id, "🎉 Все уроки пройдены!")
        return

    lesson = lessons[index]
    text = f"{lesson['text']}\n\n📺 {lesson['url']}"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Назад", callback_data="prev"),
            InlineKeyboardButton("⏭️ Пропустить", callback_data="skip"),
            InlineKeyboardButton("➡️ Продолжить", callback_data="next")
        ],
        [InlineKeyboardButton("✅ Завершить курс", callback_data="finish")]
    ])

    await context.bot.send_message(chat_id, text, reply_markup=keyboard)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_progress[user_id] = 0
    await send_lesson(update.effective_chat.id, user_id, context)

# Обработка кнопок
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    index = user_progress.get(user_id, 0)

    if query.data == "next" and index < len(lessons) - 1:
        index += 1
    elif query.data == "prev" and index > 0:
        index -= 1
    elif query.data == "skip":
        index += 1
        user_progress[user_id] = index
        await send_lesson(query.message.chat.id, user_id, context, override=index)
        await query.answer()
        return
    elif query.data == "finish":
        await context.bot.send_message(query.message.chat.id, "✅ Курс завершён! Спасибо!")
        await query.answer()
        return

    user_progress[user_id] = index
    await send_lesson(query.message.chat.id, user_id, context)
    await query.answer()

# Webhook
@bot_app.post(WEBHOOK_PATH)
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

# Telegram bot
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_button))

if __name__ == "__main__":
    import asyncio
    asyncio.run(application.initialize())
    asyncio.run(application.start())
    bot_app.run(host="0.0.0.0", port=5000)
