import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Получаем токен из переменной окружения
TOKEN = os.environ.get("BOT_TOKEN")

# Инициализируем Flask и telegram-application
bot_app = Flask(__name__)
application = Application.builder().token(TOKEN).updater(None).build()

# Простая структура уроков
lessons = [
    {"text": "👋 Урок 1", "url": "https://youtu.be/vid1"},
    {"text": "🚀 Урок 2", "url": "https://youtu.be/vid2"},
    {"text": "🎓 Финал", "url": "https://youtu.be/vid3"}
]
user_progress = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_progress[user_id] = 0
    await send_lesson(update.effective_chat.id, user_id, context)

# Кнопки
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

# Отправка урока
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

# Обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_button))

# Корневой маршрут для проверки статуса
@bot_app.route("/")
def index():
    return "🤖 Telegram бот работает!"

# Webhook endpoint (с обёрткой синхронной)
@bot_app.post(f"/{TOKEN}")
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

# Запуск
if __name__ == "__main__":
    async def main():
        await application.initialize()
        await application.start()

        # Установить webhook
        webhook_url = f"https://telegram-bot-akmz.onrender.com/{TOKEN}"
        await application.bot.set_webhook(webhook_url)
        print(f"✅ Webhook установлен: {webhook_url}")

        # Запуск Flask
        bot_app.run(host="0.0.0.0", port=5000)

    asyncio.run(main())
