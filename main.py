import telebot
import threading

from database import create_table
from handlers import bot
from scheduler import schedule_daily_reminder

'''Launching the bot'''
if __name__ == '__main__':
    try:
        create_table()
        threading.Thread(target=schedule_daily_reminder, daemon=True).start()
        print("Бот запущен...")
        bot.infinity_polling()
    except Exception as e:
        print(f"Произошла критическая ошибка при запуске бота: {e}")