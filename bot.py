import telebot
from telebot import types
import create_db
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
    create_db.create_db()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Регистрация", callback_data="registration"))
    lastname = message.from_user.last_name
    if lastname is None:
        bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name} 👋 Я ваш персональный помощник по планированию задач.\nЧтобы начать работу с ботом необходимо пройти регистрацию."
                         , reply_markup= markup)
    else:
        bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name} {lastname} 👋 Я ваш персональный помощник по планированию задач.\nЧтобы начать работу с ботом необходимо пройти регистрацию."
                         , reply_markup= markup)

@bot.callback_query_handler(func=lambda callback: True)
def registr(callback):
    if callback.data == "registration" or callback.data == "Регистрация":
        bot.send_message(callback.message.chat.id, "Пожалуйста, введите свое ФИО")
        bot.register_next_step_handler(callback.message,lambda msg: register_name(msg))

def register_name (message):
    name = message.text
    bot.send_message(message.chat.id, f"{name}, вы являетесь:\n1. Студентом МУИВ\n2. Преподавателем МУИВ\nВведите номер:")
    bot.register_next_step_handler(message, lambda msg: register_student(msg, name, message.chat.id))

#РЕГИСТРАЦИЯ СТУДЕНТОВ
def register_student(message, name, student_id):
    if message.text == "1":
        print(1)
        bot.send_message(message.chat.id, f"{name}, вы являетесь студентом МУИВ, пожалуйста введите ваш номер телефона.\nЭти данные будут доступны только вашему преподавателю")
        bot.register_next_step_handler(message, lambda msg: student_nomber(msg, name, student_id))
    elif message.text == "2":
        print(2)
        bot.send_message(message.chat.id,f"{name}, вы являетесь преподавателем МУИВ, пожалуйста введите ваш номер телефона:")
        bot.register_next_step_handler(message, lambda msg: register_teacher(msg, name, message.chat.id))
    else:
        bot.send_message(message.chat.id, f"{name}, вы ввели неверное значение, попробуйте ещё раз.\nВы являетесь:\n1. Студентом МУИВ\n2. Преподавателем МУИВ\nВведите номер:")
        bot.register_next_step_handler(message, lambda msg: register_student(msg, name, student_id))

def student_nomber(message, name, student_id):
    phone_nomber = message.text
    bot.send_message(message.chat.id, f"{name}, введите вашу почту\nПример: plan_it@mail.com")
    bot.register_next_step_handler(message, lambda msg: mail_student (msg, name, student_id, phone_nomber))

def mail_student(message, name, student_id, phone_nomber):
    mail = message.text
    bot.send_message(message.chat.id, f"{name}, ваш пол:\n1. Мужской\n2. Женский\nВведите цифру с нужным вариантом:")
    bot.register_next_step_handler(message, lambda msg: gender_student (msg, name, student_id, phone_nomber, mail))

def gender_student(message, name, student_id, phone_nomber, mail):
    gender = message.text
    if gender == "1" or gender == "2":
        bot.send_message(message.chat.id, f"{name}, укажите ваш Факультет\nПример: Информационные технологии")
        bot.register_next_step_handler(message, lambda msg: faculty_student(msg, name, student_id, phone_nomber, mail, gender))
    else:
        bot.send_message(message.chat.id,
                         f"{name}, вы ввели неверное значение\nваш пол:\n1. Мужской\n2. Женский\nВведите цифру с нужным вариантом:")
        bot.register_next_step_handler(message, lambda msg: gender_student (msg, name, student_id, phone_nomber, mail))

def faculty_student(message, name, student_id, phone_nomber, mail, gender):
    faculty = message.text
    bot.send_message(message.chat.id, f"{name}, укажите ваш курс\nПример: 1")
    bot.register_next_step_handler(message, lambda msg: course_student(msg, name, student_id, phone_nomber, mail, gender, faculty))

def course_student(message, name, student_id, phone_nomber, mail, gender, faculty):
    course = message.text
    if course == "1" or course == "2" or course == "3" or course == "4":
        bot.send_message(message.chat.id, f"{name}, укажите номер вашей группы \nПример: ИД23-3")
        bot.register_next_step_handler(message,lambda msg: group_number(msg, name, student_id, phone_nomber, mail, gender, faculty, course))
    else:
        bot.send_message(message.chat.id,
                         f"{name}, вы ввели неверное значение, укажите ваш курс\nПример: 1")
        bot.register_next_step_handler(message, lambda msg: course_student(msg, name, student_id, phone_nomber, mail, gender, faculty))

def group_number(message, name, student_id, phone_nomber, mail, gender, faculty, course):
    group = message.text
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO student (student_id, name, phone_number, mail, gender, faculty, course, group_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (student_id, name, phone_nomber, mail, gender, faculty, course, group))
    connection.commit()
    connection.close()
    bot.send_message(message.chat.id, "Вы зарегистрированы!")

#РЕГИСТРАЦИЯ ПРЕПОДАВАТЕЛЯ
def register_teacher(message, name, teacher_id):
    teacher_phone_nomber = message.text
    bot.send_message(message.chat.id, f"{name}, введите вашу почту\nПример: plan_it@mail.com")
    bot.register_next_step_handler(message, lambda msg: mail_teacher (msg, name, teacher_id, teacher_phone_nomber))

def mail_teacher(message, name, teacher_id, teacher_phone_nomber):
    mail = message.text
    bot.send_message(message.chat.id, f"{name}, ваш пол:\n1. Мужской\n2. Женский\nВведите цифру с нужным вариантом:")
    bot.register_next_step_handler(message, lambda msg: gender_teacher (msg, name, teacher_id, teacher_phone_nomber, mail))

def gender_teacher(message, name, teacher_id, teacher_phone_nomber, mail):
    gender = message.text
    if gender == "1" or gender == "2":
        bot.send_message(message.chat.id, f"{name}, укажите наименование вашей кафедры\nПример: Информационные системы")
        bot.register_next_step_handler(message, lambda msg: department_teacher(msg, name, teacher_id, teacher_phone_nomber, mail, gender))
    else:
        bot.send_message(message.chat.id,
                         f"{name}, вы ввели неверное значение\nваш пол:\n1. Мужской\n2. Женский\nВведите цифру с нужным вариантом:")
        bot.register_next_step_handler(message, lambda msg: gender_teacher (msg, name, teacher_id, teacher_phone_nomber, mail))

def department_teacher(message, name, teacher_id, teacher_phone_nomber, mail, gender):
    department = message.text
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO teachers (teacher_id, name, phone_number, mail, gender, department) VALUES (?, ?, ?, ?, ?, ?)',
                   (teacher_id, name, teacher_phone_nomber, mail, gender, department))
    connection.commit()
    connection.close()
    bot.send_message(message.chat.id, "Вы зарегистрированы!")

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



