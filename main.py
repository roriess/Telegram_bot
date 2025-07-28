import telebot
import sqlite3
import datetime
import schedule
import time
import threading
from telebot import types

''' Конфигурация '''
DATABASE_FILE = 'todo.db'  # Имя файла базы данных
BOT_TOKEN = '8428063292:AAEuDRbZVdTpD9EDuvnn6mAuHE4gJoBaGIA'
REMINDER_HOUR = "06:00"  # Время для отправки ежедневного напоминания (в формате "ЧЧ:ММ")

''' Инициализация '''
bot = telebot.TeleBot(BOT_TOKEN)

def create_table():
    ''' Создаем базу данных ''' 
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
    ''' Сохраняем новую задачу в базе данных ''' 
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (user_id, description, date) VALUES (?, ?, ?)",
                       (user_id, description, date.strftime('%Y-%m-%d')))  # Преобразуем дату в строку
        conn.commit()
        conn.close()
        print(f"Задача сохранена: user_id={user_id}, description='{description}', date={date}")
    except sqlite3.Error as e:
        print(f"Ошибка при сохранении задачи: {e}")

def get_tasks_for_date(user_id, date):
    ''' Получаем список задач для конкретного пользователя на определенную дату '''
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, description FROM tasks WHERE user_id = ? AND date = ?",
                       (user_id, date.strftime('%Y-%m-%d'),))  # Преобразуем дату в строку
        tasks = cursor.fetchall()
        conn.close()
        return tasks  # Возвращает список кортежей (id, description)
    except sqlite3.Error as e:
        print(f"Ошибка при получении задач: {e}")
        return []  # Возвращаем пустой список в случае ошибки

def delete_task(task_id):
    ''' Удаляем задачу из базы данных по ее ID '''
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        print(f"Задача с ID {task_id} удалена.")
    except sqlite3.Error as e:
        print(f"Ошибка при удалении задачи: {e}")

''' Обработчики сообщений бота '''
@bot.message_handler(commands=['start'])
def start(message):
    ''' Обработчик команды /start '''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создаем клавиатуру
    btn1 = types.KeyboardButton("Мои возможности")
    markup.add(btn1)  # Добавляем кнопку на клавиатуру
    bot.send_message(message.chat.id,
                     "Привет! Я твой личный бот-напоминатель. Я помогу тебе не забывать о важных задачах. Просто добавь их, и я буду напоминать тебе о них!",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Мои возможности')
def handle_mis_posibilidades(message):
    ''' Обработчик нажатия кнопки "Мои возможности" '''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Добавить новую задачу')
    btn2 = types.KeyboardButton('Задачи на сегодня')
    btn4 = types.KeyboardButton('Как работать с ботом')
    markup.add(btn1, btn2, btn4)
    bot.send_message(message.chat.id, 'Что вы хотите сделать?', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Добавить новую задачу')
def ask_for_task_description(message):
    ''' Обработчик нажатия кнопки 'Добавить новую задачу' - спрашивает описание задачи '''
    bot.send_message(message.chat.id, 'Пожалуйста, введите описание задачи:')
    bot.register_next_step_handler(message, ask_for_task_date)  # Переходим к следующему шагу - запросу даты

def ask_for_task_date(message):
    ''' Спрашиваем дату выполнения задачи '''
    task_description = message.text  # Получаем описание задачи из предыдущего шага
    bot.send_message(message.chat.id, 'Введите дату выполнения задачи в формате ГГГГ-ММ-ДД:')
    bot.register_next_step_handler(message, process_task_date, task_description)  # Переходим к обработке даты

def process_task_date(message, task_description):
    '''  Обрабатываем веденную дату и сохраняем задачу '''
    try:
        task_date = datetime.datetime.strptime(message.text, '%Y-%m-%d').date()  # Преобразуем строку в дату
        user_id = message.chat.id  # Получаем ID пользователя
        save_task(user_id, task_description, task_date)  # Сохраняем задачу в базу данных
        bot.send_message(user_id, f'Задача "{task_description}" запланирована на {task_date.strftime("%Y-%m-%d")}')
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД.")

@bot.message_handler(func=lambda message: message.text == 'Задачи на сегодня')
def show_tasks_today(message):
    ''' Показываем задачи на сегодня с кнопками для удаления '''
    user_id = message.chat.id
    today = datetime.date.today()  # Получаем сегодняшнюю дату
    tasks = get_tasks_for_date(user_id, today)  # Получаем задачи из базы данных

    if tasks:
        message_text = "Ваши задачи на сегодня:\n"
        keyboard = []
        for task_id, description in tasks:
            message_text += f"- {description} (ID: {task_id})\n"  # Формируем текст сообщения
            keyboard.append([types.InlineKeyboardButton(text=f"Удалить: {description}", callback_data=f"delete_{task_id}")])  # Создаем кнопку "Удалить"

        reply_markup = types.InlineKeyboardMarkup(keyboard)  # Создаем клавиатуру с кнопками "Удалить"
        bot.send_message(user_id, message_text, reply_markup=reply_markup)  # Отправляем сообщение с задачами и кнопками
    else:
        bot.send_message(user_id, "На сегодня задач нет.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def handle_delete_callback(call):
    ''' Обработчик нажатий на кнопки "Удалить" ''' 
    try:
        task_id = int(call.data.split('_')[1])  # Извлекаем ID задачи из callback_data
        delete_task(task_id)  # Удаляем задачу из базы данных
        bot.answer_callback_query(call.id, "Задача удалена!")  # Отправляем уведомление об удалении
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Задача удалена.",
                              reply_markup=None)  # Удаляем кнопки из сообщения
    except ValueError:
        bot.answer_callback_query(call.id, "ID задачи недопустимый.")
    except Exception as e:
        print(f"Ошибка при удалении задачи: {e}")
        bot.answer_callback_query(call.id, "Ошибка при удалении задачи.")

# ========== Функции для отправки напоминаний ==========
def send_daily_reminder():
    ''' Отправляем ежедневные напоминания пользователям о задачах на сегодня ''' 
    now = datetime.date.today()
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT user_id FROM tasks WHERE date = ?", (now.strftime('%Y-%m-%d'),))  # Получаем список уникальных user_id
        user_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        for user_id in user_ids:
            tasks = get_tasks_for_date(user_id, now)  # Получаем задачи для пользователя
            if tasks:
                task_list = "\n- ".join([f"{description} (ID: {task_id})" for task_id, description in tasks])  # Формируем список задач
                message = f"Доброе утро! Вот ваши задачи на сегодня:\n- {task_list}"
                bot.send_message(user_id, message)  # Отправляем сообщение пользователю
    except sqlite3.Error as e:
        print(f"Ошибка при отправке ежедневного напоминания: {e}")

def schedule_daily_reminder():
    ''' Планируем отправку ежедневных напоминаний '''
    schedule.every().day.at(REMINDER_HOUR).do(send_daily_reminder)  # Задаем расписание - каждый день в заданное время
    while True:
        try:
            schedule.run_pending()  # Запускаем запланированные задачи
            time.sleep(60)  # Ждем 60 секунд (1 минута)
        except Exception as e:
            print(f"Ошибка в цикле планировщика: {e}")
            time.sleep(60)  # Пауза, чтобы избежать постоянных ошибок

''' Запуск бота '''
if __name__ == '__main__':
    try:
        create_table()  # Создаем таблицу задач
        threading.Thread(target=schedule_daily_reminder, daemon=True).start()  # Запускаем планировщик в отдельном потоке
        print("Бот запущен...")
        bot.infinity_polling()  # Запускаем бота в бесконечном цикле
    except Exception as e:
        print(f"Произошла критическая ошибка при запуске бота: {e}")

