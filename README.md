# Telegram bot for task planning

This is a simple Telegram bot designed to help users manage their daily tasks and stay organized. Users can add tasks with a description and due date, view their tasks for the current day, and delete tasks either individually from the daily task list. The bot also sends a daily reminder at 6:00 AM with a list of tasks due for that day.

## Features

•   **Add Tasks:**  Users can add tasks with a description and due date (YYYY-MM-DD).
•   **View Today's Tasks:**  Displays a list of tasks scheduled for the current day, including the task ID and a delete button for each.
•   **Delete Tasks:**  Delete individual tasks directly from the daily task list.
•   **Daily Reminders:** Sends a daily notification at 6:00 AM with a list of tasks scheduled for that day.

## Technologies Used

•   Python
•   Telethon library
•   SQLite Database
•   Schedule library

## Database

The bot uses an SQLite database (`tasks.db`) to store task information. The database schema includes fields for task ID, user ID, description, due date, and completion status.

You can find the bot on Telegram to try out its features by using this nickname: @Tufaforubot


Это простой Telegram бот, предназначенный для помощи пользователям в управлении ежедневными задачами и поддержании организованности. Пользователи могут добавлять задачи с описанием и датой выполнения, просматривать свои задачи на текущий день и удалять задачи либо индивидуально из списка задач на день. Бот также отправляет ежедневное напоминание в 6:00 утра со списком задач на этот день.

## Функции

•   **Добавление Задач:** Пользователи могут добавлять задачи с описанием и датой выполнения (ГГГГ-ММ-ДД).
•   **Просмотр Задач на Сегодня:** Отображает список задач, запланированных на текущий день, включая ID задачи и кнопку удаления для каждой.
•   **Удаление Задач:**   Удаление отдельных задач непосредственно из списка задач на день.
•   **Ежедневные Напоминания:** Отправляет ежедневное уведомление в 6:00 утра со списком задач, запланированных на этот день.

## Используемые Технологии

•   Python
•   Библиотека Telethon
•   База Данных SQLite
•   Библиотека Schedule

## База Данных

Бот использует базу данных SQLite (`tasks.db`) для хранения информации о задачах. Схема базы данных включает поля для ID задачи, ID пользователя, описания, даты выполнения и статуса завершения.

Найти бота в телеграмм, чтобы попробовать его возможности, можно по этому нику: @Tufaforubot
