import os
import sys

print("1. Начало загрузки...")

try:
    from flask import Flask, request
    print("2. Flask импортирован")
except Exception as e:
    print(f"Ошибка импорта Flask: {e}")
    sys.exit(1)

try:
    from telegram import Bot, Update
    print("3. telegram.Bot и Update импортированы")
except Exception as e:
    print(f"Ошибка импорта telegram: {e}")
    sys.exit(1)

try:
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    print("4. Application и обработчики импортированы")
except Exception as e:
    print(f"Ошибка импорта telegram.ext: {e}")
    sys.exit(1)

app = Flask(__name__)
print("5. Flask app создан")

# Получаем токен из переменной окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN")
print(f"6. Токен получен: {TOKEN[:10] if TOKEN else 'None'}...")

if not TOKEN:
    print("❌ ОШИБКА: TELEGRAM_TOKEN не задан!")
    sys.exit(1)

# Создаем приложение (Application вместо Dispatcher)
try:
    application = Application.builder().token(TOKEN).build()
    print("7. Application успешно создан")
except Exception as e:
    print(f"Ошибка создания Application: {e}")
    sys.exit(1)

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
print("8. Обработчики зарегистрированы")

# Вебхук эндпоинт
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
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
    print("9. Запуск main...")
    setup_webhook()
    port = int(os.environ.get("PORT", 10000))
    print(f"10. Запуск сервера на порту {port}")
    app.run(host="0.0.0.0", port=port)
