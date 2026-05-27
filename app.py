import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ ОШИБКА: TELEGRAM_TOKEN не задан!")
    exit(1)

# URL для отправки ответов Telegram
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

# --- Функция для отправки сообщений ---
def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, json=data)
        return response.ok
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")
        return False

# --- Обработка команд ---
def handle_start(chat_id):
    send_message(chat_id, "👋 Привет! Я бот на Render.com!\nДоступные команды:\n/info — узнать информацию о себе")

def handle_info(chat_id, user_id, first_name, username):
    text = f"📌 Ваш ID: {user_id}\n👤 Имя: {first_name}\n🔹 Username: @{username if username else 'не указан'}"
    send_message(chat_id, text)

def handle_unknown(chat_id):
    send_message(chat_id, "❓ Я вас не понял.\nИспользуйте команды: /start или /info")

# --- Вебхук (точка входа для сообщений от Telegram) ---
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    try:
        # Получаем данные от Telegram
        update = request.get_json(force=True)
        
        # Извлекаем информацию о сообщении
        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]
            user_id = message["from"]["id"]
            first_name = message["from"].get("first_name", "")
            username = message["from"].get("username", "")
            
            text = message.get("text", "")
            
            # Обрабатываем команды
            if text == "/start":
                handle_start(chat_id)
            elif text == "/info":
                handle_info(chat_id, user_id, first_name, username)
            else:
                handle_unknown(chat_id)
        
        return "ok", 200
    except Exception as e:
        print(f"Ошибка в вебхуке: {e}")
        return "error", 500

# --- Проверка здоровья ---
@app.route("/health")
def health():
    return "OK", 200

# --- Главная страница ---
@app.route("/")
def index():
    return "🤖 Бот работает!"

# --- Установка вебхука при запуске ---
def setup_webhook():
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        print("⚠️ RENDER_EXTERNAL_URL не найден")
        return
    
    webhook_url = f"{render_url}/webhook/{TOKEN}"
    url = f"{TELEGRAM_API_URL}/setWebhook"
    data = {"url": webhook_url}
    
    try:
        response = requests.post(url, json=data)
        if response.ok:
            print(f"✅ Webhook установлен: {webhook_url}")
        else:
            print(f"❌ Ошибка установки вебхука: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🚀 Запуск бота...")
    setup_webhook()
    port = int(os.environ.get("PORT", 10000))
    print(f"✅ Сервер запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)
