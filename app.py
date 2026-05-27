import os
import threading
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

app = Flask(__name__)

# Токен бота (из переменной окружения, настроим позже на Render)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# --- Команды бота ---
async def start(update, context):
    await update.message.reply_text(
        "👋 Привет! Я бот на Render.com!\n"
        "Доступные команды:\n"
        "/info — узнать информацию о себе"
    )

async def info(update, context):
    user = update.effective_user
    await update.message.reply_text(
        f"📌 Ваш ID: {user.id}\n"
        f"👤 Имя: {user.first_name}\n"
        f"🔹 Username: @{user.username if user.username else 'не указан'}"
    )

async def echo(update, context):
    await update.message.reply_text(
        "❓ Я вас не понял.\n"
        "Используйте команды: /start или /info"
    )

# Регистрируем обработчики команд
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("info", info))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Эндпоинт для вебхуков (Telegram будет отправлять сюда обновления)
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        threading.Thread(target=lambda: dispatcher.process_update(update)).start()
        return "ok", 200

# Health check для Render (чтобы не падал)
@app.route("/health")
def health():
    return "OK", 200

@app.route("/")
def index():
    return "🤖 Бот работает!"

def setup_webhook():
    """Устанавливаем вебхук после запуска бота"""
    webhook_url = f"{os.environ.get('RENDER_EXTERNAL_URL')}/webhook/{TOKEN}"
    bot.set_webhook(webhook_url)
    print(f"✅ Webhook установлен: {webhook_url}")

if __name__ == "__main__":
    # Устанавливаем вебхук при запуске
    setup_webhook()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
