import sqlite3

from config import DATABASE_FILE


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