import telebot

from telebot import types
from config import BOT_TOKEN
from database import save_task, get_tasks_for_date, delete_task
import datetime

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    '''Handler of the /start command'''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Мои возможности")
    markup.add(btn1)
    bot.send_message(message.chat.id,
'''Привет! Я твой личный бот-напоминатель. Я помогу тебе не забывать о важных задачах. Просто добавь их, и я буду напоминать тебе о них!

Чтобы узнать о всех доступных возможностях, используй кнопку "Мои возможности" 

❗️При возникновении ошибок в работе бота о них можно сообщить, нажав кнопку 'Сообщить об ошибке'. Спасибо!'''
                    , reply_markup=markup)
    

@bot.message_handler(func=lambda message: message.text == 'Мои возможности')
def handle_mis_posibilidades(message):
    '''Handler of the "Мои возможности" command'''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('➕ Добавить новую задачу')
    btn2 = types.KeyboardButton('🗓 Задачи на сегодня')
    btn3 = types.KeyboardButton('🗓 Задачи на определенную дату')
    btn4 = types.KeyboardButton('❓ Как работать с ботом')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, 
'''Что вы хотите сделать?

📌 "Добавить новую задачу": Позволяет создать новую задачу с указанием даты и описания.
📌 "Задачи на сегодня": Показывает список задач, запланированных на сегодняшний день.
📌 "Задачи на определенную дату": Показывает список задач, запланированных на определенный день.
📌 "Как работать с ботом": Предоставляет инструкции по использованию бота и его основных функций.'''
                    , reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '➕ Добавить новую задачу')
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


@bot.message_handler(func=lambda message: message.text == '🗓 Задачи на сегодня')
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


@bot.message_handler(func=lambda message: message.text == '🗓 Задачи на определенную дату')
def ask_for_tasks_date(message):
    '''Ask for tasks date'''
    global task_description
    task_description = message.text
    bot.send_message(message.chat.id, 'Введите необходимую дату в формате ГГГГ-ММ-ДД:')
    bot.register_next_step_handler(message, show_tasks)

def show_tasks(message):
    '''Show tasks with delete buttons'''
    global task_description
    user_id = message.chat.id
    try:
        tasks_date = datetime.datetime.strptime(message.text, '%Y-%m-%d').date()
    except ValueError:
        bot.send_message(user_id, "Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")
        return

    tasks = get_tasks_for_date(user_id, tasks_date)

    if tasks:
        message_text = f"Ваши задачи (Описание: {task_description}):\n"
        keyboard = []
        for task_id, description in tasks:
            message_text += f"- {description} (ID: {task_id})\n"
            keyboard.append([types.InlineKeyboardButton(text=f"Удалить: {description}", callback_data=f"delete_{task_id}")])

        reply_markup = types.InlineKeyboardMarkup(keyboard)
        bot.send_message(user_id, message_text, reply_markup=reply_markup)
    else:
        bot.send_message(user_id, "Задач нет. Можно и отдохнуть :)")


@bot.message_handler(func=lambda message: message.text == '❓ Как работать с ботом')
def handle_mis_posibilidades(message):
    '''Handler of the "Как работать с ботом" command'''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('➕ Добавить новую задачу')
    btn2 = types.KeyboardButton('🗓 Задачи на сегодня')
    btn4 = types.KeyboardButton('❓ Как работать с ботом')
    markup.add(btn1, btn2, btn4)
    bot.send_message(message.chat.id, 
'''✨ Как пользоваться ботом: ✨

1️⃣  /start - Запускает бота и выводит приветственное сообщение.
2️⃣  Как работать с ботом - Выводит это справочное сообщение.
3️⃣  Добавить новую задачу - Добавление новой задачи с описанием на определенную дату
4️⃣  Задачи на сегодня - Просмотр всех задач, добавленных на сегодня.'''
                    , reply_markup=markup)


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