# web.py
from flask import Flask
import threading
import os
import asyncio

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Бот работает!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))

if __name__ == "__main__":
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=run_web)
    web_thread.start()
    
    # Запускаем бота
    import asyncio
    from main import main
    asyncio.run(main())