from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
import sqlite3
import os

app = Flask(__name__)
TOKEN = os.environ.get("7739788468:AAGKfIJD3V-Nl7kafJ6YlBmqp6Qkh8r90R0")
bot = Bot(token=TOKEN)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER PRIMARY KEY,
            lesson_index INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

lessons = [
    {"text": "👋 Добро пожаловать! Урок 1", "url": "https://youtu.be/video1"},
    {"text": "🚀 Урок 2", "url": "https://youtu.be/video2"},
    {"text": "🎓 Финал!", "url": "https://youtu.be/video3"}
]

def get_progress(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT lesson_index FROM progress WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def set_progress(user_id, index):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO progress (user_id, lesson_index) VALUES (?, ?)", (user_id, index))
    conn.commit()
    conn.close()

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

def start(update, context):
    user_id = update.effective_user.id
    set_progress(user_id, 0)
    send_lesson(update.effective_chat.id, user_id)

def handle_button(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    index = get_progress(user_id)

    if data == "next" and index < len(lessons) - 1:
        index += 1
        set_progress(user_id, index)
    elif data == "prev" and index > 0:
        index -= 1
        set_progress(user_id, index)
    elif data == "skip":
        index += 1
        send_lesson(query.message.chat.id, user_id, override=index)
        query.answer()
        return
    elif data == "finish":
        bot.send_message(query.message.chat.id, "✅ Курс завершён! Спасибо за прохождение 🙌")
        query.answer()
        return

    send_lesson(query.message.chat.id, user_id)
    query.answer()

def send_lesson(chat_id, user_id, override=None):
    index = override if override is not None else get_progress(user_id)
    if index >= len(lessons):
        bot.send_message(chat_id, "🎉 Все уроки пройдены!")
        return

    lesson = lessons[index]
    text = f"{lesson['text']}\n\n📺 {lesson['url']}"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Назад", callback_data="prev"),
            InlineKeyboardButton("⏭️ Пропустить", callback_data="skip"),
            InlineKeyboardButton("➡️ Продолжить", callback_data="next")
        ],
        [
            InlineKeyboardButton("✅ Завершить курс", callback_data="finish")
        ]
    ])

    bot.send_message(chat_id, text, reply_markup=keyboard)

from telegram.ext import Dispatcher
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(handle_button))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
