import telebot
import sqlite3
import datetime
import schedule
import time
import threading
from telebot import types

<<<<<<< HEAD
'''Configuration'''
DATABASE_FILE = 'todo.db'  
BOT_TOKEN = '8428063292:AAFMBIQc37O5FyDBecyA4dNrxDhsedHwxJs'
REMINDER_HOUR = "06:00"
=======
''' Конфигурация '''
DATABASE_FILE = 'todo.db'  # Имя файла базы данных
BOT_TOKEN = ''
REMINDER_HOUR = "06:00"  # Время для отправки ежедневного напоминания (в формате "ЧЧ:ММ")
>>>>>>> 519ad99c1c23a0ac18e57e32992e051fb3827569

'''Initialization'''
bot = telebot.TeleBot(BOT_TOKEN)


def create_table():
    '''Create database''' 
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,      -- ID пользователя Telegram
                description TEXT NOT NULL,     -- Описание задачи
                date TEXT NOT NULL,            -- Дата выполнения (текст в формате YYYY-MM-DD)
                completed INTEGER DEFAULT 0     -- Статус выполнения (0 - не выполнено, 1 - выполнено)
            )
        ''')
        conn.commit()
        conn.close()
        print("Таблица tasks успешно создана или уже существует.")
    except sqlite3.Error as e:
        print(f"Ошибка при создании таблицы: {e}")


def save_task(user_id, description, date):
    '''Save new task in database''' 
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (user_id, description, date) VALUES (?, ?, ?)",
                       (user_id, description, date.strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()
        print(f"Задача сохранена: user_id={user_id}, description='{description}', date={date}")
    except sqlite3.Error as e:
        print(f"Ошибка при сохранении задачи: {e}")

def get_tasks_for_date(user_id, date):
    '''Rece a task with a date from the user'''
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, description FROM tasks WHERE user_id = ? AND date = ?",
                       (user_id, date.strftime('%Y-%m-%d'),))
        tasks = cursor.fetchall()
        conn.close()
        return tasks
    except sqlite3.Error as e:
        print(f"Ошибка при получении задач: {e}")
        return []


def delete_task(task_id):
    '''Deleting a task from the database by its ID'''
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        print(f"Задача с ID {task_id} удалена.")
    except sqlite3.Error as e:
        print(f"Ошибка при удалении задачи: {e}")


@bot.message_handler(commands=['start'])
def start(message):
    '''Handler of the /start command'''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Мои возможности")
    markup.add(btn1)
    bot.send_message(message.chat.id,
                     '''Привет! Я твой личный бот-напоминатель. Я помогу тебе не забывать о важных задачах. Просто добавь их, и я буду напоминать тебе о них!
                        Чтобы узнать о всех доступных возможностях, используй кнопку 'Мои возможности' 

                        ❗️При возникновении ошибок в работе бота о них можно сообщить, нажав кнопку 'Сообщить об ошибке'. Спасибо!
                     ''', reply_markup=markup)
    

@bot.message_handler(func=lambda message: message.text == 'Мои возможности')
def handle_mis_posibilidades(message):
    '''Handler of the "Мои возможности" command'''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Добавить новую задачу')
    btn2 = types.KeyboardButton('Задачи на сегодня')
    btn4 = types.KeyboardButton('Как работать с ботом')
    markup.add(btn1, btn2, btn4)
    bot.send_message(message.chat.id, '''Что вы хотите сделать?

                                        'Добавить новую задачу': Позволяет создать новую задачу с указанием даты и описания.
                                        'Задачи на сегодня': Показывает список задач, запланированных на сегодняшний день.
                                        'Как работать с ботом': Предоставляет инструкции по использованию бота и его основных функций.  
                                      ''', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Добавить новую задачу')
def ask_for_task_description(message):
    '''Handler of the "Добавить новую задачу" command'''
    bot.send_message(message.chat.id, 'Пожалуйста, введите описание задачи:')
    bot.register_next_step_handler(message, ask_for_task_date)  


def ask_for_task_date(message):
    '''Ask for task date'''
    task_description = message.text
    bot.send_message(message.chat.id, 'Введите дату выполнения задачи в формате ГГГГ-ММ-ДД:')
    bot.register_next_step_handler(message, process_task_date, task_description)


def process_task_date(message, task_description):
    '''Process the entered date and save the task'''
    try:
        task_date = datetime.datetime.strptime(message.text, '%Y-%m-%d').date()
        user_id = message.chat.id
        save_task(user_id, task_description, task_date)
        bot.send_message(user_id, f'Задача "{task_description}" запланирована на {task_date.strftime("%Y-%m-%d")}')
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД.")


@bot.message_handler(func=lambda message: message.text == 'Задачи на сегодня')
def show_tasks_today(message):
    '''Show today's tasks with delete buttons'''
    user_id = message.chat.id
    today = datetime.date.today()
    tasks = get_tasks_for_date(user_id, today)

    if tasks:
        message_text = "Ваши задачи на сегодня:\n"
        keyboard = []
        for task_id, description in tasks:
            message_text += f"- {description} (ID: {task_id})\n"
            keyboard.append([types.InlineKeyboardButton(text=f"Удалить: {description}", callback_data=f"delete_{task_id}")])

        reply_markup = types.InlineKeyboardMarkup(keyboard)
        bot.send_message(user_id, message_text, reply_markup=reply_markup)
    else:
        bot.send_message(user_id, "На сегодня задач нет. Можно и отдохнуть :)")


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def handle_delete_callback(call):
    '''Handler of the "Удалить" command''' 
    try:
        task_id = int(call.data.split('_')[1])
        delete_task(task_id)
        bot.answer_callback_query(call.id, "Задача удалена!")
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Задача удалена.",
                              reply_markup=None)
    except ValueError:
        bot.answer_callback_query(call.id, "ID задачи недопустимый.")
    except Exception as e:
        print(f"Ошибка при удалении задачи: {e}")
        bot.answer_callback_query(call.id, "Ошибка при удалении задачи.")


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


'''Launching the bot'''
if __name__ == '__main__':
    try:
        create_table()
        threading.Thread(target=schedule_daily_reminder, daemon=True).start()
        print("Бот запущен...")
        bot.infinity_polling()
    except Exception as e:
        print(f"Произошла критическая ошибка при запуске бота: {e}")