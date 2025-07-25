import telebot
from telebot import types
import datetime
import schedule
import time
import threading
import sqlite3

bot = telebot.TeleBot('')

waiting_for_task = {}
waiting_for_delete_task = {}

DATABASE_FILE = 'tasks.db' 

def create_table():
    """Создаем таблицу tasks, если она не существует."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            description TEXT,
            date TEXT,
            completed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def save_task(user_id, description, date):
    """Сохраняем задачу в базу данных."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (user_id, description, date) VALUES (?, ?, ?)",
                   (user_id, description, date.strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()

def get_tasks_for_date(user_id, date):
    """Получаем список задач с id для пользователя на указанную дату."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, description FROM tasks WHERE user_id = ? AND date = ?",
                   (user_id, date.strftime('%Y-%m-%d'),))
    tasks = cursor.fetchall() 
    conn.close()
    return tasks

def delete_task(task_id):
    """Удаляем задачу из базы данных по ID."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

create_table()



@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Мои возможности")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "🗓 Привет! Я твой личный бот-напоминатель. Я буду помогать тебе не забывать о важных задачах и всегда быть в курсе своих планов. Просто добавь свои задачи, и я буду напоминать о них в нужное время!", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user_id = message.from_user.id

    if message.text == 'Мои возможности':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Добавить новую задачу')
        btn2 = types.KeyboardButton('Задачи на сегодня')
        btn4 = types.KeyboardButton('Как работать с ботом')
        markup.add(btn1, btn2, btn4)
        bot.send_message(user_id, 'Выберете действие:', reply_markup=markup)

    elif message.text == 'Добавить новую задачу':
        bot.send_message(user_id, 'Введите описание задачи:')
        global waiting_for_task
        waiting_for_task[user_id] = True

    elif user_id in waiting_for_task and waiting_for_task[user_id]:
        task_description = message.text
        waiting_for_task[user_id] = False

        bot.send_message(user_id, 'Введите дату выполнения задачи в формате ГГГГ-ММ-ДД:')
        bot.register_next_step_handler(message, process_date, task_description)

    elif message.text == 'Задачи на сегодня':
        show_tasks_today(message)


@bot.message_handler(func=lambda message: message.text == 'Задачи на сегодня')
def show_tasks_today(message):
    """Показывает задачи на сегодня с кнопками удаления"""
    user_id = message.from_user.id
    today = datetime.date.today()
    tasks = get_tasks_for_date(user_id, today)

    if tasks:
        keyboard = []
        message_text = "Ваши задачи на сегодня:\n"
        for task_id, description in tasks:
            message_text += f"- ID: {task_id}, {description}\n"
            keyboard.append([types.InlineKeyboardButton(text=f"Удалить: {description}", callback_data=f"delete_{task_id}")])

        reply_markup = types.InlineKeyboardMarkup(keyboard)
        bot.send_message(user_id, message_text, reply_markup=reply_markup) 
    else:
        bot.send_message(user_id, "На сегодня задач нет.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def callback_query(call):
    """Обрабатываем нажатия на кнопки "Удалить"."""
    task_id = call.data.split('_')[1]
    delete_task(task_id)
    bot.answer_callback_query(call.id, "Задача удалена!") 

    show_tasks_today(call.message)

def send_daily_reminder():
    """Отправляем ежедневные напоминания о задачах."""
    now = datetime.date.today()
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM tasks WHERE date = ?", (now.strftime('%Y-%m-%d'),)) 
    user_ids = [row[0] for row in cursor.fetchall()]

    for user_id in user_ids:
        tasks = get_tasks_for_date(user_id, now)
        if tasks:
             task_list = "\n- ".join([f"ID: {task_id}, {description}" for task_id, description in tasks])
             message = f"Доброе утро! Вот ваши задачи на сегодня:\n- {task_list}"
             bot.send_message(user_id, message)

def schedule_daily_reminder():
    """Планируем отправку ежедневных напоминаний в 6 утра."""
    schedule.every().day.at("06:00").do(send_daily_reminder)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    create_table()
    threading.Thread(target=schedule_daily_reminder, daemon=True).start()
    bot.polling(none_stop=True, interval=0)
