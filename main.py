import telebot
from config import BOT_TOKEN
from handlers import register_handlers
import db

if not BOT_TOKEN:
    raise ValueError("Необходимо указать BOT_TOKEN в .env файле")

# Инициализируем бота
bot = telebot.TeleBot(BOT_TOKEN)

if __name__ == '__main__':
    # Инициализируем базу данных
    db.init_db()

    # Регистрируем все обработчики
    register_handlers(bot)

    print("Бот запущен...")

    # Запускаем бота (бесконечный опрос серверов Telegram)
    bot.polling(none_stop=True)
