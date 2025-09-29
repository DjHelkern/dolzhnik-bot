import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Название файла базы данных
# 'debts.db' - значение по умолчанию
DATABASE_NAME = os.getenv('DATABASE_NAME', 'debts.db')
