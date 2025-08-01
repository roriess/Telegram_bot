import sqlite3
import schedule
import datetime
import time

from config import DATABASE_FILE, REMINDER_HOUR
from database import get_tasks_for_date
from handlers import bot


def send_daily_reminder():
    '''Send daily reminders to users about their tasks for today''' 
    now = datetime.date.today()
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT user_id FROM tasks WHERE date = ?", (now.strftime('%Y-%m-%d'),))
        user_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        for user_id in user_ids:
            tasks = get_tasks_for_date(user_id, now)
            if tasks:
                task_list = "\n- ".join([f"{description} (ID: {task_id})" for task_id, description in tasks])
                message = f"Доброе утро! Вот ваши задачи на сегодня:\n- {task_list}"
                bot.send_message(user_id, message)
    except sqlite3.Error as e:
        print(f"Ошибка при отправке ежедневного напоминания: {e}")


def schedule_daily_reminder():
    '''Planning to send daily reminders'''
    schedule.every().day.at(REMINDER_HOUR).do(send_daily_reminder)
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            print(f"Ошибка в цикле планировщика: {e}")
            time.sleep(60)