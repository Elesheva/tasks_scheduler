import telebot
from telebot import types

from telegram import Update
from telegram.ext import Updater, CommandHandler, Application, MessageHandler, CallbackContext
from datetime import datetime
import time
import threading

from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
from datetime import datetime


bot = telebot.TeleBot('7206218529:AAGXx1IkHVxZ3IrFt09Xgzytanj1n-bpcUI')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    create_db()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Регистрация", callback_data="registration"))
    lastname = message.from_user.last_name
    if lastname is None:
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name} 👋 Я твой персональный помощник по планированию задач.\nЧтобы начать работу с ботом необходимо пройти регистрацию."
                         , reply_markup= markup)
    else:
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name} {lastname} 👋 Я твой персональный помощник по планированию задач.\nЧтобы начать работу с ботом необходимо пройти регистрацию."
                         , reply_markup= markup)

@bot.callback_query_handler(func=lambda callback: True)
def registr(callback):
    if callback.data == "registration" or "Регистрация":
        bot.send_message(callback.message.chat.id, "Пожалуйста, введи свое ФИО")
        bot.register_next_step_handler(callback.message,lambda msg: register_name(msg))

def register_name (message):
    name = message.text
    bot.send_message(message.chat.id, f'{name}, вы являетесь:\n1. Студентом МУИВ\n2. Преподавателем МУИВ\nВведите ниже')
    bot.register_next_step_handler(message, lambda msg: register_student(msg, name))
    bot.register_next_step_handler(message, lambda msg: register_teacher(msg, name))

def register_student(massage, name):
    if massage.text == "1":
        print(1)


def register_teacher(message, name):
    print(message)

@bot.message_handler(commands=['add_task'])
def new_task(message):
    regular = False
    bot.send_message(message.chat.id, "Какую задачу хочешь запланировать?")
    bot.register_next_step_handler(message, lambda msg: whattime(msg, message.from_user.id, regular))

def whattime(message, user_id, regular):
    regular = regular
    task_plan = message.text
    bot.send_message(message.chat.id, "На какое время? (Например - 13:30)")
    bot.register_next_step_handler(message, lambda msg: save_time(msg, task_plan, user_id, regular))

def save_time(message, task_plan, user_id, regular):
    regular = regular
    what_time = message.text
    # Проверяем, что часы в диапазоне от 0 до 23 и минуты от 0 до 59
    try:
        hours, minutes = map(int, what_time.split(':'))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            bot.send_message(message.chat.id, "На какую дату хочешь запланировать? Пожалуйста, используйте формат: ДД.ММ \n(Например - 12.07)")
            bot.register_next_step_handler(message, lambda msg: save_task(msg, task_plan, user_id, what_time, regular))
        else:
            bot.send_message(message.chat.id,
                             f"Неверный формат. Пожалуйста, используйте формат: ЧЧ:ММ \n Пример (13:30)")
            bot.register_next_step_handler(message, lambda msg: save_time(msg, task_plan, user_id, regular))

    except ValueError:
        bot.send_message(user_id,
                         "Неверный формат. Пожалуйста, используйте формат: ЧЧ:ММ \n Пример (13:30)")
        bot.register_next_step_handler(message, lambda msg: save_time(msg, task_plan, user_id))


def save_task(message, task_plan, user_id, what_time, regular):
    date_time = message.text
    regular = regular
    try:
        days, month = map(int, date_time.split('.'))
        print(month, days)
        if 1 <= month <= 12 and 1 <= days < 32:
            connection = sqlite3.connect('my_database.db')
            cursor = connection.cursor()
            cursor.execute('INSERT INTO tasks (user_id, task, task_time, date, regular_task) VALUES (?, ?, ?, ?, ?)',
                           (user_id, task_plan, what_time, date_time, regular))
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id, "Задача добавлена!")
        else:
            bot.send_message(message.chat.id,
                             f"Неверный формат. Пожалуйста, используйте формат: ДД.ММ \n(Например - 12.07)")
            bot.register_next_step_handler(message, lambda msg: save_task(msg, task_plan, user_id, what_time, regular))

    except ValueError:
        bot.send_message(user_id,
                         "Неверный формат. Пожалуйста, используйте формат: ДД.ММ \n(Например - 12.07)")
        bot.register_next_step_handler(message, lambda msg: save_task(msg, task_plan, user_id, what_time, regular))


# БЛОК ДОБАВЛЕНИЯ НОВОЙ НЕРЕГУЛЯРНОЙ ЗАДАЧИ

@bot.message_handler(commands=['add_regular_task'])
def new_task(message):
    regular = True
    create_db()
    bot.send_message(message.chat.id, "Какую задачу хочешь запланировать?")
    bot.register_next_step_handler(message, lambda msg: whattime(msg, message.from_user.id, regular))


def create_db():
    # Подключение к базе данных
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    # Создание таблицы tasks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task TEXT,
            task_time TEXT,
            date TEXT,
            regular_task BOOLEAN,
            complete BOOLEAN
        )
    """)

    # Создание таблицы teachers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            name TEXT,
            phone_number TEXT,
            mail TEXT,
            number_of_generated_tasks INTEGER,
            gender TEXT,
            department TEXT
        )
    """)

    # Создание таблицы student
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            name TEXT,
            phone_number TEXT,
            mail TEXT,
            gender TEXT,
            faculty TEXT,
            course INTEGER,
            group_number INTEGER
        )
    """)

    # Создание таблицы discipline
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discipline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_of_discipline TEXT,
            teacher_id INTEGER,
            faculty TEXT
        )
    """)

    # Создание таблицы group
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_number INTEGER, 
            student_id INTEGER,
            name TEXT,
            faculty TEXT,
            course INTEGER
        )
    """)

    # Сохранение изменений и закрытие соединения
    connection.commit()
    cursor.close()
    connection.close()


@bot.message_handler(commands=['all_tasks'])
def get_all_tasks_from_db(message):
    user_id = message.from_user.id
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT task, task_time, date FROM tasks WHERE user_id = ?", (user_id,))
    tasks = cursor.fetchall()
    print(tasks)
    connection.commit()
    connection.close()
    output = "".join(f"{i+1}) {tasks[i][0]} в {tasks[i][1]}, {tasks[i][2]}\n" for i in range(len(tasks)))
    print(output)
    if len(output) != 0:
        bot.send_message(message.chat.id, f"{message.from_user.first_name} {message.from_user.last_name}, все твои задачи:")
        bot.send_message(message.chat.id, output)
    else:
        bot.send_message(message.chat.id, f'{message.from_user.first_name} {message.from_user.last_name}, у тебя нет задач:)')
@bot.message_handler(commands=['delete_tasks'])
def delete_task_from_db(message):
    user_id = message.from_user.id
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT (*) FROM tasks WHERE user_id = ?", (user_id,))
    count = cursor.fetchone() [0]
    if count > 0:
        cursor.execute("SELECT id, task, task_time, date FROM tasks WHERE user_id = ?", (user_id,))
        tasks = cursor.fetchall()
        connection.commit()
        connection.close()
        print(tasks)
        proverka_id = "".join(f"{x[0]} " for x in tasks)
        output = "".join(f"{x[0]} - {x[1]} в {x[2]}, {x[3]}\n" for x in tasks)
        print(output)
        bot.send_message(message.chat.id, f"{message.from_user.first_name} {message.from_user.last_name}, все твои задачи:")
        bot.send_message(message.chat.id, output)
        bot.send_message(message.chat.id, "Напиши номер задачи, которую хочешь удалить.")
        bot.register_next_step_handler(message, lambda msg: delete_tasks_from_db(msg, proverka_id))
    else:
        bot.send_message(message.chat.id, "У тебя нет задач")

def delete_tasks_from_db(message, proverka_id):
    id = message.text
    print(proverka_id)
    print(type(id))
    if id in proverka_id:
        user_id = message.from_user.id
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
        cursor.execute("SELECT COUNT (*) FROM tasks WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id, f"Задача {id} удалена")
            get_all_tasks_from_db(message)
        else:
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id, f"Задача {id} удалена")
            bot.send_message(message.chat.id, "Список задач пуст." )
    else:
        bot.send_message(message.chat.id, "Такого номера нет.")

def send_message_ga(user_id, message):
    # Здесь должна быть логика отправки сообщения пользователю
    print(f"Отправлено сообщение '{message}' пользователю {user_id}")


def check_tasks():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%d.%m")

    # Выборка задач с текущим временем и датой
    cursor.execute("""
        SELECT id, user_id, task, regular_task 
        FROM tasks 
        WHERE task_time = ? AND date = ?
    """, (current_time, current_date))
    tasks = cursor.fetchall()

    for task in tasks:
        task_id, user_id, message, regular_task = task
        send_message_ga(user_id, message)

        # Если задача не регулярная, обновляем complete на True
        if not regular_task:
            cursor.execute("""
                UPDATE tasks 
                SET complete = 1 
                WHERE id = ?
            """, (task_id,))

    conn.commit()
    conn.close()


scheduler = BackgroundScheduler()
# Запланируем выполнение функции check_tasks каждую минуту
scheduler.add_job(check_tasks, 'interval', minutes=1)
scheduler.start()


bot.polling(none_stop=True)



