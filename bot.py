import telebot
from pyexpat.errors import messages
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

#ПРИВЕТСВИЕ И РЕГИСТРАЦИЯ
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
    if callback.data == "Поменять данные" or callback.data == "changing_student":
        bot.send_message(callback.message.chat.id, "Пожалуйста, введите номер поля, которое хотетите изменить")
        bot.register_next_step_handler(callback.message, lambda msg: nomber_change(msg))
    if callback.data == "Поменять данные " or callback.data == "changing_teacher":
        bot.send_message(callback.message.chat.id, "Пожалуйста, введите номер поля, которое хотетите изменить")
        bot.register_next_step_handler(callback.message, lambda msg: nomber_change_teacher(msg))

    if callback.data == "Поменять" or callback.data == "changing":
        bot.send_message(callback.message.chat.id, "Пожалуйста, введите номер поля, которое хотетите изменить")
        bot.register_next_step_handler(callback.message, lambda msg: nomber_change_discepline(msg))
    if callback.data == "Добавить" or callback.data == "add":
        add_data_to_table_discipline(callback.message)

    if callback.data == "Поменять данные" or callback.data == "changing_group":
        bot.send_message(callback.message.chat.id, "Пожалуйста, введите номер поля, которое хотетите изменить")
        bot.register_next_step_handler(callback.message, lambda msg: nomber_change_group(msg))
    if callback.data == "Добавить данные" or callback.data == "add_group":
        groap_table(callback.message)


def register_name (message):
    name = message.text
    bot.send_message(message.chat.id, f"{name}, вы являетесь:\n1. Студентом МУИВ\n2. Преподавателем МУИВ\nВведите номер:")
    bot.register_next_step_handler(message, lambda msg: register_student(msg, name, message.chat.id))

#РЕГИСТРАЦИЯ СТУДЕНТОВ
def register_student(message, name, student_id):
    if message.text == "1":
        #ПРОВЕРКА ЗАРЕГ-Н ПОЛЬЗОВАТЕЛЬ ИЛИ НЕТ
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT (*) FROM student WHERE student_id = ?", (student_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            bot.send_message(message.chat.id, f"{name}, вы уже зарегистрированы")
            changing_student(message,student_id)
        else:
            bot.send_message(message.chat.id, f"{name}, вы являетесь студентом МУИВ, пожалуйста введите ваш номер телефона.\nЭти данные будут доступны только вашему преподавателю")
            bot.register_next_step_handler(message, lambda msg: student_nomber(msg, name, student_id))
    elif message.text == "2":
        print(2)
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT (*) FROM teachers WHERE teacher_id = ?", (student_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            bot.send_message(message.chat.id, f"{name}, вы уже зарегистрированы")
            changing_teacher(message, student_id)
        else:
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
    changing_student(message, student_id)


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
    changing_teacher(message, teacher_id)

#ИЗМЕНЕНИЕ ДАННЫХ ДЛЯ СТУДЕНТОВ И ПРЕПОДАВАТЕЛЕЙ
def changing_student(message, student_id):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT name, phone_number, mail, faculty, course, group_number FROM student WHERE student_id = ?", (student_id,))
    info_about_student = cursor.fetchall()
    connection.commit()
    connection.close()
    output = "".join(f"Ваши данные:\n1) Имя: {info_about_student[i][0]}\n2) Номер телефона: {info_about_student[i][1]}\n3) Почта: {info_about_student[i][2]}\n4) Факультет: {info_about_student[i][3]}\n5) Курс: {info_about_student[i][4]}\n6) Номер группы: {info_about_student[i][5]}" for i in range(len(info_about_student)))
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Поменять данные", callback_data="changing_student"))
    bot.send_message(message.chat.id, output, reply_markup= markup)

def nomber_change(message):
    nomber = message.text
    print(nomber)
    student_id = message.chat.id
    if nomber == "1":
        bot.send_message(message.chat.id, "Пожалуйста, введите свое ФИО")
        bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber))
    elif nomber == "2":
        bot.send_message(message.chat.id, "Пожалуйста, введите новый номер телефона:")
        bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber))
    elif nomber == "3":
        bot.send_message(message.chat.id, "Пожалуйста, введите новый почтовый адрес:")
        bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber))
    elif nomber == "4":
        bot.send_message(message.chat.id, "Пожалуйста, введите название факультета:")
        bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber))
    elif nomber == "5":
        bot.send_message(message.chat.id, "Пожалуйста, введите номер курса:")
        bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber))
    elif nomber == "6":
        bot.send_message(message.chat.id, "Пожалуйста, введите номер группы:")
        bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber))
    else:
        bot.send_message(message.chat.id, "Такого номера нет, попробуйте ещё раз. Введите номер поля, которое хотите изменить:")
        bot.register_next_step_handler(message, nomber_change)

def changing_db_student(message, student_id, nomber):
    new = message.text
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    if nomber == '1':
        cursor.execute("UPDATE student SET name = ? WHERE student_id= ?", (new, student_id))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли ФИО")
        changing_student(message, student_id)
    elif nomber == "2":
        cursor.execute("UPDATE student SET phone_number = ? WHERE student_id= ?", (new, student_id))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли номер телефона")
        changing_student(message, student_id)
    elif nomber == "3":
        cursor.execute("UPDATE student SET mail = ? WHERE student_id= ?", (new, student_id))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли почту")
        changing_student(message, student_id)
    elif nomber == "4":
        cursor.execute("UPDATE student SET faculty = ? WHERE student_id= ?", (new, student_id))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли факультет")
        changing_student(message, student_id)
    elif nomber == "5":
        if new == "1" or new == "2" or new == "3" or new == "4":
            cursor.execute("UPDATE student SET course = ? WHERE student_id= ?", (new, student_id))
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id, "Вы поменяли курс")
            changing_student(message, student_id)
        else:
            bot.send_message(message.chat.id, "Вы ввели неверное значение, укажите ваш курс\nПример: 1")
            bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber))
    elif nomber == "6":
        cursor.execute("UPDATE student SET group_number = ? WHERE student_id= ?", (new, student_id))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли номер группы")
        changing_student(message, student_id)

def changing_teacher (message, teacher_id):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT name, phone_number, mail, department FROM teachers WHERE teacher_id = ?", (teacher_id,))
    info_about_teacher = cursor.fetchall()
    connection.commit()
    connection.close()
    output = "".join(
        f"Ваши данные:\n1) Имя: {info_about_teacher[i][0]}\n2) Номер телефона: {info_about_teacher[i][1]}\n3) Почта: {info_about_teacher[i][2]}\n4) Кафедра: {info_about_teacher[i][3]}"
        for i in range(len(info_about_teacher)))
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Поменять данные ", callback_data="changing_teacher"))
    bot.send_message(message.chat.id, output, reply_markup= markup)

def nomber_change_teacher(message):
    nomber = message.text
    teacher_id = message.chat.id
    if nomber == "1":
        bot.send_message(message.chat.id, "Пожалуйста, введите свое ФИО")
        bot.register_next_step_handler(message, lambda msg: changing_db_teacher(msg, teacher_id, nomber))
    elif nomber == "2":
        bot.send_message(message.chat.id, "Пожалуйста, введите новый номер телефона:")
        bot.register_next_step_handler(message, lambda msg: changing_db_teacher(msg, teacher_id, nomber))
    elif nomber == "3":
        bot.send_message(message.chat.id, "Пожалуйста, введите новый почтовый адрес:")
        bot.register_next_step_handler(message, lambda msg: changing_db_teacher(msg, teacher_id, nomber))
    elif nomber == "4":
        bot.send_message(message.chat.id, "Пожалуйста, введите название кафедры:")
        bot.register_next_step_handler(message, lambda msg: changing_db_teacher(msg, teacher_id, nomber))
    else:
        bot.send_message(message.chat.id, "Такого номера нет, попробуйте ещё раз. Введите номер поля, которое хотетите изменить:")
        bot.register_next_step_handler(message, nomber_change_teacher)

def changing_db_teacher(message, teacher_id, nomber):
    new = message.text
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    if nomber == '1':
        cursor.execute("UPDATE teachers SET name = ? WHERE teacher_id= ?", (new, teacher_id))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли ФИО")
        changing_teacher (message, teacher_id)
    if nomber == "2":
        cursor.execute("UPDATE teachers SET phone_number = ? WHERE teacher_id= ?", (new, teacher_id))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли номер телефона")
        changing_teacher (message, teacher_id)
    if nomber == "3":
        cursor.execute("UPDATE teachers SET mail = ? WHERE teacher_id= ?", (new, teacher_id))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли почту")
        changing_teacher (message, teacher_id)
    if nomber == "4":
        cursor.execute("UPDATE teachers SET department = ? WHERE teacher_id= ?", (new, teacher_id))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли кафедру")
        changing_teacher (message, teacher_id)

#Функции для преподавателя
#ДОБАВЛЕНИЕ ПРЕПОДАВАТЕЛЕМ ДАННЫХ В ТАБЛИЦУ ДИСЦИПЛИНА
@bot.message_handler(commands=['add_discipline'])
def add_data_to_table_discipline(message):
    bot.send_message(message.chat.id, "Введите название вашей дисциплины:")
    bot.register_next_step_handler(message, lambda msg: to_table_discipline(msg, message.from_user.id))

def to_table_discipline(message, teacher_id):
    name_discipline = message.text
    bot.send_message(message.chat.id, "Введите название факультета:")
    bot.register_next_step_handler(message, lambda msg: to_table_dis(msg, name_discipline, teacher_id))

def to_table_dis(message, name_discipline, teacher_id):
    name_facyltet = message.text
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO discipline (name_of_discipline, teacher_id, faculty) VALUES (?, ?, ?)',
                   (name_discipline, teacher_id, name_facyltet))
    connection.commit()
    connection.close()
    bot.send_message(message.chat.id, f"Дисциплина создана")
    select_data_for_teacher(message, teacher_id)

def select_data_for_teacher(message, teacher_id):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id, name_of_discipline, faculty FROM discipline WHERE teacher_id = ?", (teacher_id,))
    info_about_discipline = cursor.fetchall()
    connection.commit()
    connection.close()
    output = "".join(
        f"{info_about_discipline[i][0]}) {info_about_discipline[i][1]}, {info_about_discipline[i][2]}\n"
        for i in range(len(info_about_discipline)))
    print(output)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Поменять", callback_data="changing"))
    markup.add(types.InlineKeyboardButton("Добавить", callback_data="add"))
    bot.send_message(message.chat.id, f"Дисциплины:\n{output}", reply_markup=markup)

def nomber_change_discepline(message):
    nomber= message.text
    bot.send_message(message.chat.id, "Пожалуйста, введите новое название дисциплины")
    bot.register_next_step_handler(message, lambda msg: changing_discepline(msg, nomber))

def changing_discepline(message,  nomber):
    discepline = message.text
    bot.send_message(message.chat.id, "Пожалуйста, введите новое название факультета:")
    bot.register_next_step_handler(message, lambda msg: changing_disceplineee(msg,nomber, discepline))

def changing_disceplineee(message, nomber, discepline):
    name_facyltet = message.text
    nomber = int(nomber)
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id, name_of_discipline, faculty FROM discipline WHERE id = ?", (nomber,))
    faculty = cursor.fetchall()
    connection.commit()
    connection.close()
    if not faculty:
        bot.send_message(message.chat.id, "Нет данных с таким идентификатором. Вы ввели неверное число")
        return
    output = "".join(f"{faculty[i][0]}) {faculty[i][1]}\n" for i in range(len(faculty)))
    if output:
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute("UPDATE discipline SET name_of_discipline = ?, faculty = ? WHERE id= ?", (discepline, name_facyltet, nomber))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли данные.")
        select_data_for_teacher(message, message.chat.id)
    else:
        bot.send_message(message.chat.id, "Нет данных с таким идентификатором.")

@bot.message_handler(commands=['add_group'])
def groap_table(message):
    teacher_id = message.chat.id
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id, faculty FROM discipline WHERE teacher_id = ?", (teacher_id,))
    faculty = cursor.fetchall()
    connection.commit()
    connection.close()
    if not faculty:
        bot.send_message(message.chat.id, "Нет доступных факультетов.")
        return
    output = "".join(f"{faculty[i][0]}) {faculty[i][1]}\n"for i in range(len(faculty)))
    bot.send_message(message.chat.id, f"Вы создали следующие факультеты:\n{output}\nУкажите номер факультета, в котором создаётся группа:")
    print(output)
    bot.register_next_step_handler(message, lambda msg: to_table_groap(msg, teacher_id, faculty))

def to_table_groap(message, teacher_id, faculty):
    id = int(message.text)
    if any(f[0] == id for f in faculty):
        facultet = faculty[id-1][1]
        bot.send_message(message.chat.id, f"Вы выбрали: {facultet}\nВведите номер группы:")
        bot.register_next_step_handler(message, lambda msg: to_groap(msg, teacher_id, facultet))
    else:
        bot.send_message(message.chat.id, "Неверный номер факультета. Пожалуйста, попробуйте снова.")
        bot.register_next_step_handler(message, lambda msg: to_table_groap(msg, teacher_id, facultet))

def to_groap(message, teacher_id, facultet):
    group = message.text
    bot.send_message(message.chat.id, "Укажите курс:")
    bot.register_next_step_handler(message, lambda msg: to_tableee_groap(msg, teacher_id, facultet, group))

def to_tableee_groap(message, teacher_id, facultet, group):
    cyrs = message.text
    if cyrs == "1" or cyrs == "2" or cyrs == "3" or cyrs == "4":
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO groups (group_number, faculty, course) VALUES (?, ?, ?)',
                   (group, facultet, cyrs))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Группа добавлена, теперь в неё могут добавляться студенты.")
        spisok_grupp(message)
    else:
        bot.send_message(message.chat.id, "Вы ввели неверное значение. Укажите курс:")
        bot.register_next_step_handler(message, lambda msg:to_tableee_groap(msg, teacher_id, facultet, group))

def spisok_grupp(message):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute ("SELECT * FROM groups")
    groups = cursor.fetchall()
    connection.commit()
    connection.close()
    output = "".join(f"{groups[i][0]}) {groups[i][1]}, факультет: {groups[i][2]}, курс: {groups[i][3]}\n" for i in range(len(groups)))
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Поменять данные", callback_data="changing_group"))
    markup.add(types.InlineKeyboardButton("Добавить данные", callback_data="add_group"))
    if output:
        bot.send_message(message.chat.id, f"Все группы:\n{output}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Нет данных с таким идентификатором.")

def nomber_change_group(message):
    nomber= message.text
    bot.send_message(message.chat.id, "Пожалуйста, введите новый номер группы:")
    bot.register_next_step_handler(message, lambda msg: changing_group(msg, nomber))

def changing_group(message, nomber):
    nomber_group = message.text
    bot.send_message(message.chat.id, "Пожалуйста, введите курс:")
    bot.register_next_step_handler(message, lambda msg: changing_grouppp(msg, nomber, nomber_group))

def changing_grouppp(message, nomber, nomber_group):
    cyrs = message.text
    if cyrs == "1" or cyrs == "2" or cyrs == "3" or cyrs == "4":
        nomber = int(nomber)
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute ("UPDATE groups SET group_number = ?, course = ? WHERE id= ?", (nomber_group, cyrs, nomber))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "вы поменяли данные.")
        spisok_grupp(message)
    else:
        bot.send_message(message.chat.id, "Вы ввели неверное значение. Укажите курс:")
        bot.register_next_step_handler(message, lambda msg:changing_grouppp(msg, nomber, nomber_group))

#ДОБАВЛЕНИЕ ПЕРСОНАЛЬНОЙ НЕРЕГУЛЯРНОЙ ЗАДАЧИ
@bot.message_handler(commands=['add_task'])
def new_task(message):
    regular = False
    bot.send_message(message.chat.id, "Какую задачу хотите запланировать?")
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
            bot.send_message(message.chat.id, "На какую дату хотите запланировать? Пожалуйста, используйте формат: ДД.ММ \n(Например - 12.07)")
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

# БЛОК ДОБАВЛЕНИЯ НОВОЙ РЕГУЛЯРНОЙ ЗАДАЧИ
@bot.message_handler(commands=['add_regular_task'])
def new_task(message):
    regular = True
    bot.send_message(message.chat.id, "Какую задачу хотите запланировать?")
    bot.register_next_step_handler(message, lambda msg: whattime(msg, message.from_user.id, regular))

#ДОСТАЁМ ВСЕ ЗАДАЧИ ИЗ БД
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
        bot.send_message(message.chat.id, f"{message.from_user.first_name} {message.from_user.last_name}, все ваши задачи:")
        bot.send_message(message.chat.id, output)
    else:
        bot.send_message(message.chat.id, f'{message.from_user.first_name} {message.from_user.last_name}, у вас нет задач:)')

#УДАЛЕНИЕ ЗАДАЧИ ИЗ БД
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
        bot.send_message(message.chat.id, f"{message.from_user.first_name} {message.from_user.last_name}, все ваши задачи:")
        bot.send_message(message.chat.id, output)
        bot.send_message(message.chat.id, "Напишите номер задачи, которую хотите удалить.")
        bot.register_next_step_handler(message, lambda msg: delete_tasks_from_db(msg, proverka_id))
    else:
        bot.send_message(message.chat.id, "У вас нет задач")

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

#НАПОМИНАНИЕ ПОЛЬЗОВАТЕЛЮ
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



