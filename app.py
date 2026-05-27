import os
import json
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

app = Flask(__name__)

# Получаем токен из переменной окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    print("❌ ОШИБКА: TELEGRAM_TOKEN не задан!")
    exit(1)

# Создаем приложение (Application вместо Dispatcher)
application = Application.builder().token(TOKEN).build()

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

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("info", info))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Вебхук эндпоинт
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        application.process_update(update)
        return "ok", 200
    except Exception as e:
        print(f"Ошибка обработки: {e}")
        return "error", 500

# Health check
@app.route("/health")
def health():
    return "OK", 200

# Главная страница
@app.route("/")
def index():
    return "🤖 Бот работает!"

# Установка вебхука при запуске
def setup_webhook():
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        print("⚠️ RENDER_EXTERNAL_URL не найден, пропускаем установку вебхука")
        return
    
    webhook_url = f"{render_url}/webhook/{TOKEN}"
    try:
        bot = Bot(token=TOKEN)
        bot.set_webhook(webhook_url)
        print(f"✅ Webhook установлен: {webhook_url}")
    except Exception as e:
        print(f"❌ Ошибка установки webhook: {e}")

if __name__ == "__main__":
    print(f"🚀 Запуск бота с токеном: {TOKEN[:10]}...")
    setup_webhook()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
