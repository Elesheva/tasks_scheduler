from os.path import lexists

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

    if callback.data == "Поменять наименование дисциплины" or callback.data == "changing":
        bot.send_message(callback.message.chat.id, "Пожалуйста, введите номер поля, которое хотетите изменить")
        bot.register_next_step_handler(callback.message, lambda msg: nomber_change_discepline(msg))
    if callback.data == "Добавить дисциплину" or callback.data == "add":
        add_data_to_table_discipline(callback.message)

    if callback.data == "Поменять группу" or callback.data == "changing_group":
        bot.send_message(callback.message.chat.id, "Пожалуйста, введите номер поля, которое хотетите изменить")
        bot.register_next_step_handler(callback.message, lambda msg: nomber_change_group(msg))
    if callback.data == "Добавить группу" or callback.data == "add_group":
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
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute("SELECT id, faculty FROM discipline")
        info_about_faculty = cursor.fetchall()
        connection.commit()
        connection.close()
        output = "".join(
            f"{info_about_faculty[i][0]}) {info_about_faculty[i][1]}\n"
            for i in range(len(info_about_faculty)))
        bot.send_message(message.chat.id, f"{name}, укажите ваш Факультет:\n{output} ")
        bot.register_next_step_handler(message, lambda msg: faculty_student(msg, name, student_id, phone_nomber, mail, gender, info_about_faculty))
    else:
        bot.send_message(message.chat.id,
                         f"{name}, вы ввели неверное значение\nваш пол:\n1. Мужской\n2. Женский\nВведите цифру с нужным вариантом:")
        bot.register_next_step_handler(message, lambda msg: gender_student (msg, name, student_id, phone_nomber, mail))


def faculty_student(message, name, student_id, phone_nomber, mail, gender, info_about_faculty):
    try:
        nomber = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Неверный номер факультета. Пожалуйста, попробуйте снова.")
        bot.register_next_step_handler(message,
                                       lambda msg: faculty_student(msg, name, student_id, phone_nomber, mail, gender,
                                                                   info_about_faculty))
        return
    have = False
    for i in range(len(info_about_faculty)):
        if info_about_faculty[i][0] == nomber:
            have = True
            faculty = info_about_faculty[i][1]
            bot.send_message(message.chat.id, f"{name}, укажите ваш курс\nПример: 1")
            bot.register_next_step_handler(message, lambda msg: course_student(msg, name, student_id, phone_nomber, mail, gender, faculty))
    if not have:
        bot.send_message(message.chat.id, "Неверный номер факультета. Пожалуйста, попробуйте снова.")
        bot.register_next_step_handler(message,
                                       lambda msg: faculty_student(msg, name, student_id, phone_nomber, mail, gender,
                                                                   info_about_faculty))

def course_student(message, name, student_id, phone_nomber, mail, gender, faculty):
    course = message.text
    if course == "1" or course == "2" or course == "3" or course == "4":
        course = int(message.text)
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute("SELECT id, group_number, faculty, course FROM groups WHERE faculty = ?, course = ? ", (faculty, course))
        info_about_faculty = cursor.fetchall()
        connection.commit()
        connection.close()
        output = "".join(
            f"{info_about_faculty[i][0]}) {info_about_faculty[i][1]}, факультет: {info_about_faculty[i][2]}, курс: {info_about_faculty[i][3]}\n"
            for i in range(len(info_about_faculty)))
        bot.send_message(message.chat.id, f"{name}, выберите номер группы:\n{output} ")
        bot.register_next_step_handler(message,lambda msg: group_number(msg, name, student_id, phone_nomber, mail, gender, faculty, course, info_about_faculty))
    else:
        bot.send_message(message.chat.id,
                         f"{name}, вы ввели неверное значение, укажите ваш курс\nПример: 1")
        bot.register_next_step_handler(message, lambda msg: course_student(msg, name, student_id, phone_nomber, mail, gender, faculty))

def group_number(message, name, student_id, phone_nomber, mail, gender, faculty, course, info_about_faculty):
    try:
        nomber = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id,
                         f"{name}, вы ввели неверное значение, укажите вашу группу:")
        bot.register_next_step_handler(message,
                                       lambda msg: group_number(msg, name, student_id, phone_nomber, mail, gender,
                                                                faculty, course, info_about_faculty))
        return

    have = False
    for i in range(len(info_about_faculty)):
        if info_about_faculty[i][0] == nomber:
            have = True
            group = info_about_faculty[i][1]
            connection = sqlite3.connect('my_database.db')
            cursor = connection.cursor()
            cursor.execute('INSERT INTO student (student_id, name, phone_number, mail, gender, faculty, course, group_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           (student_id, name, phone_nomber, mail, gender, faculty, course, group))
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id, "Вы зарегистрированы!")
            changing_student(message, student_id)
    if not have:
        bot.send_message(message.chat.id,
                         f"{name}, вы ввели неверное значение, укажите вашу группу:")
        bot.register_next_step_handler(message,
                                       lambda msg: group_number(msg, name, student_id, phone_nomber, mail, gender,
                                                                faculty, course, info_about_faculty))

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
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id, faculty FROM discipline")
    info_about_faculty = cursor.fetchall()
    connection.commit()
    connection.close()
    if nomber == "1":
        bot.send_message(message.chat.id, "Пожалуйста, введите свое ФИО")
        bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber, info_about_faculty))
    elif nomber == "2":
        bot.send_message(message.chat.id, "Пожалуйста, введите новый номер телефона:")
        bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber, info_about_faculty))
    elif nomber == "3":
        bot.send_message(message.chat.id, "Пожалуйста, введите новый почтовый адрес:")
        bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber, info_about_faculty))
    elif nomber == "4":
        output = "".join(
            f"{info_about_faculty[i][0]}) {info_about_faculty[i][1]}\n"
            for i in range(len(info_about_faculty)))
        bot.send_message(message.chat.id, f"Укажите ваш Факультет:\n{output} ")
        bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber, info_about_faculty))
    elif nomber == "5":
        bot.send_message(message.chat.id, "Пожалуйста, введите номер курса:")
        bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber, info_about_faculty))
    elif nomber == "6":
        try:
            connection = sqlite3.connect('my_database.db')
            cursor = connection.cursor()
            # Получаем информацию о студенте
            cursor.execute("SELECT faculty, course FROM student WHERE student_id = ?", (student_id,))
            info_about_student = cursor.fetchall()
            if not info_about_student:
                bot.send_message(message.chat.id, "Студент не найден.")
                return
            for i in range(len(info_about_student)):
                faculty = info_about_student[i][0]
                course = info_about_student[i][1]
            # Получаем информацию о группах
                cursor.execute("SELECT id, group_number, faculty, course FROM groups WHERE faculty = ? AND course = ?",
                               (faculty, course))
                info_about_faculty = cursor.fetchall()
            if not info_about_faculty:
                bot.send_message(message.chat.id, "Группы не найдены.")
                return
            output = "".join(f"{info_about_faculty[i][0]}) {info_about_faculty[i][1]}, факультет: {info_about_faculty[i][2]}, курс: {info_about_faculty[i][3]}\n"
                for i in range(len(info_about_faculty)))
            bot.send_message(message.chat.id, f"Выберите номер группы:\n{output}")
            bot.register_next_step_handler(message,
                                           lambda msg: changing_db_student(msg, student_id, nomber, info_about_faculty))

        except Exception as e:
            bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")
        finally:
            if 'connection' in locals():
                connection.close()
    else:
        bot.send_message(message.chat.id,
                         "Такого номера нет, попробуйте ещё раз. Введите номер поля, которое хотите изменить:")
        bot.register_next_step_handler(message, nomber_change)

def changing_db_student(message, student_id, nomber, info_about_faculty):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    if nomber == '1':
        new = message.text
        cursor.execute("UPDATE student SET name = ? WHERE student_id= ?", (new, student_id))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли ФИО")
        changing_student(message, student_id)
    elif nomber == "2":
        new = message.text
        cursor.execute("UPDATE student SET phone_number = ? WHERE student_id= ?", (new, student_id))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли номер телефона")
        changing_student(message, student_id)
    elif nomber == "3":
        new = message.text
        cursor.execute("UPDATE student SET mail = ? WHERE student_id= ?", (new, student_id))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Вы поменяли почту")
        changing_student(message, student_id)
    elif nomber == "4":
        try:
            new = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер факультета.")
            bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber, info_about_faculty))
            return

        have = False
        for i in range(len(info_about_faculty)):
            if info_about_faculty[i][0] == new:
                have = True
                faculty = info_about_faculty[i][1]
                cursor.execute("UPDATE student SET faculty = ? WHERE student_id= ?", (faculty, student_id))
                connection.commit()
                connection.close()
                bot.send_message(message.chat.id, "Вы поменяли факультет")
                changing_student(message, student_id)

        if not have:
            bot.send_message(message.chat.id, "Вы ввели неверное значение, укажите ваш факультет:")
            bot.register_next_step_handler(message,
                                           lambda msg: changing_db_student(msg, student_id, nomber, info_about_faculty))

    elif nomber == "5":
        new = message.text
        if new == "1" or new == "2" or new == "3" or new == "4":
            cursor.execute("UPDATE student SET course = ? WHERE student_id= ?", (new, student_id))
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id, "Вы поменяли курс")
            changing_student(message, student_id)
        else:
            bot.send_message(message.chat.id, "Вы ввели неверное значение, укажите ваш курс\nПример: 1")
            bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber, info_about_faculty))
    elif nomber == "6":
        try:
            new = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "Вы ввели неверное значение, укажите группу:")
            bot.register_next_step_handler(message, lambda msg: changing_db_student(msg, student_id, nomber, info_about_faculty))
            return
        have = False
        for i in range(len(info_about_faculty)):
            if info_about_faculty[i][0] == new:
                have = True
                groupp = info_about_faculty[i][1]
                cursor.execute("UPDATE student SET group_number = ? WHERE student_id= ?", (groupp, student_id))
                connection.commit()
                connection.close()
                bot.send_message(message.chat.id, "Вы поменяли номер группы")
                changing_student(message, student_id)
        if not have:
            bot.send_message(message.chat.id, "Вы ввели неверное значение, укажите группу:")
            bot.register_next_step_handler(message,
                                           lambda msg: changing_db_student(msg, student_id, nomber,
                                                                           info_about_faculty))

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

#ВЫВОДИМ СПИСОК ВСЕХ ДИСЦИПЛИН
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
    markup.add(types.InlineKeyboardButton("Поменять наименование дисциплины", callback_data="changing"))
    markup.add(types.InlineKeyboardButton("Добавить дисциплину", callback_data="add"))
    bot.send_message(message.chat.id, f"Дисциплины:\n{output}", reply_markup=markup)

#МЕНЯЕМ НАЗВАНИЕ ДИСЦИПЛИНЫ
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
#ДОБАВЛЯЕМ ГРУППУ
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
    try:
        id = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер факультета.")
        bot.register_next_step_handler(message, lambda msg: to_table_groap(msg, teacher_id, faculty))
        return
    have = False
    for i in range(len(faculty)):
        if faculty[i][0] == id:
            have = True
            facultet = faculty[i][1]
            bot.send_message(message.chat.id, f"Вы выбрали: {facultet}\nВведите номер группы:")
            bot.register_next_step_handler(message, lambda msg, f=facultet: to_groap(msg, teacher_id, f))
    if not have:
        # Если мы вышли из цикла без нахождения факультета
        bot.send_message(message.chat.id, "Неверный номер факультета. Пожалуйста, попробуйте снова.")
        bot.register_next_step_handler(message, lambda msg: to_table_groap(msg, teacher_id, faculty))


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
#ВЫВОДИМ СПИСОК ГРУПП
def spisok_grupp(message):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute ("SELECT * FROM groups")
    groups = cursor.fetchall()
    connection.commit()
    connection.close()
    output = "".join(f"{groups[i][0]}) {groups[i][1]}, факультет: {groups[i][2]}, курс: {groups[i][3]}\n" for i in range(len(groups)))
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Поменять группу", callback_data="changing_group"))
    markup.add(types.InlineKeyboardButton("Добавить группу", callback_data="add_group"))
    if output:
        bot.send_message(message.chat.id, f"Все группы:\n{output}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Нет данных с таким идентификатором.")

#МЕНЯЕМ НАЗВАНИЕ ГРУППЫ
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


# ДОБАВЛЕНИЕ РЕГУЛЯРНОЙ (СТУДЕНТ) И НЕРЕГЕГУЛЯРНОЙ ЗАДАЧИ (СТУДЕНТ И ПРЕПОДАВАТЕЛЬ)
@bot.message_handler(commands=['add_regular_task', 'add_task'])
def new_task(message):
    regular = None
    if message.text == "/add_regular_task":
        regular = True
    else:
        regular = False
    print(message.text)
    print(regular)
    user_id = message.from_user.id
    # ПРОВЕРКА РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЯ
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT (*) FROM teachers WHERE teacher_id = ?", (user_id,))
    count_teacher = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT (*) FROM student WHERE student_id = ?", (user_id,))
    count_student = cursor.fetchone()[0]
    if count_teacher > 0 and count_student > 0:
        bot.send_message(message.chat.id,
                         "У вас две учётные записи. Вы зарегистрированы и как студент и как преподаватель. Необходимо удалить неверную учётную запись.")
        # Функция удаления уч. записи
    elif count_teacher > 0 and count_student == 0:
        statys = 1
        bot.send_message(message.chat.id, "Какую задачу хотите запланировать? Введите название:")
        bot.register_next_step_handler(message, lambda msg: whattime(msg, message.from_user.id, regular, statys))
    elif count_teacher == 0 and count_student > 0:
        statys = 2
        bot.send_message(message.chat.id, "Какую задачу хотите запланировать? Введите название:")
        bot.register_next_step_handler(message, lambda msg: whattime(msg, message.from_user.id, regular, statys))
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Регистрация", callback_data="registration"))
        bot.send_message(message.chat.id,
                         "У вас нет учётные записи. Для того, чтобы создать задачу необходимо зарегистрироваться." , reply_markup= markup)

def whattime(message, user_id, regular, statys):
    regular = regular
    task_plan = message.text
    #ПРЕПОДАВАТЕЛЬ
    if statys == 1:
        bot.send_message(message.chat.id, "В какое время отправить задачу? (Например - 13:30)")
        bot.register_next_step_handler(message, lambda msg: save_time(msg, task_plan, user_id, regular, statys))
    #СТУДЕНТ
    elif statys == 2:
        bot.send_message(message.chat.id, "На какое время? (Например - 13:30)")
        bot.register_next_step_handler(message, lambda msg: save_time(msg, task_plan, user_id, regular, statys))

def save_time(message, task_plan, user_id, regular, statys):
    regular = regular
    what_time = message.text
    # Проверяем, что часы в диапазоне от 0 до 23 и минуты от 0 до 59
    try:
        hours, minutes = map(int, what_time.split(':'))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            bot.send_message(message.chat.id, "На какую дату хотите запланировать? Пожалуйста, используйте формат: ДД.ММ \n(Например - 12.07)")
            bot.register_next_step_handler(message, lambda msg: save_task(msg, task_plan, user_id, what_time, regular, statys))
        else:
            bot.send_message(message.chat.id,
                             f"Неверный формат. Пожалуйста, используйте формат: ЧЧ:ММ \n Пример (13:30)")
            bot.register_next_step_handler(message, lambda msg: save_time(msg, task_plan, user_id, regular, statys))

    except ValueError:
        bot.send_message(user_id,
                         "Неверный формат. Пожалуйста, используйте формат: ЧЧ:ММ \n Пример (13:30)")
        bot.register_next_step_handler(message, lambda msg: save_time(msg, task_plan, user_id, regular, statys))

def save_task(message, task_plan, user_id, what_time, regular, statys):
    date_time = message.text
    if statys == 1:
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute("SELECT id, name_of_discipline,faculty FROM discipline WHERE teacher_id = ?", (user_id,))
        discipline = cursor.fetchall()
        connection.commit()
        connection.close()
        output = "".join(f"{discipline[i][0]}) {discipline[i][1]}, факультет: {discipline[i][2]}" for i in
                         range(len(discipline)))
        if output:
            bot.send_message(message.chat.id, f"Выберите дисциплину:{output}")
            bot.register_next_step_handler(message,
                                           lambda msg: discipline_number_statys_teacher_1(msg, task_plan, user_id, what_time, date_time, discipline))
        else:
            bot.send_message(message.chat.id, f"Вы ещё не добавили дисциплину.")
    if statys == 2:
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
                                 "Неверный формат. Пожалуйста, используйте формат: ДД.ММ \n(Например - 12.07)")
                bot.register_next_step_handler(message, lambda msg: save_task(msg, task_plan, user_id, what_time, regular, statys))
        except ValueError:
            bot.send_message(user_id,
                             "Неверный формат. Пожалуйста, используйте формат: ДД.ММ \n(Например - 12.07)")
            bot.register_next_step_handler(message, lambda msg: save_task(msg, task_plan, user_id, what_time, regular, statys))
        except Exception as e:
            bot.send_message(user_id, f"Произошла ошибка: {str(e)}")

#ДАЛЬШЕ ТОЛЬКО ДЛЯ ПРЕПОДАВАТЕЛЯ
def discipline_number_statys_teacher_1 (message, task_plan, user_id, what_time, date_time, discipline):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(user_id,
                         "Неверный номер. Попробуйте ещё раз:")
        bot.register_next_step_handler(message,
                                       lambda msg: discipline_number_statys_teacher_1(msg, task_plan, user_id,
                                                                                      what_time, date_time, discipline))
        return
    have = False
    for i in range(len(discipline)):
        if discipline[i][0] == nomer:
            have = True
            facultet = discipline[i][2]
            name_of_discipline = discipline[i][1]
            connection = sqlite3.connect('my_database.db')
            cursor = connection.cursor()
            cursor.execute("SELECT id, group_number, faculty, course FROM groups WHERE faculty = ?", (facultet,))
            group = cursor.fetchall()
            connection.commit()
            connection.close()
            output = "".join(f"{group[i][0]}) {group[i][1]}, факультет: {group[i][2]}, {group[i][3]}\n" for i in
                             range(len(group)))
            if output:
                bot.send_message(message.chat.id, f"Выберите группу:\n{output}")
                bot.register_next_step_handler(message, lambda msg: group_number_statys_teacher_1 (msg, task_plan, user_id, what_time, date_time, name_of_discipline, facultet, group))
            else:
                bot.send_message(message.chat.id, f"Вы ещё не добавили группу.")
    if not have:
        bot.send_message(user_id,
                         "Неверный номер. Попробуйте ещё раз:")
        bot.register_next_step_handler(message,
                                       lambda msg: discipline_number_statys_teacher_1 (msg, task_plan, user_id, what_time, date_time, discipline))

def group_number_statys_teacher_1(message, task_plan, user_id, what_time, date_time, name_of_discipline, facultet, group):
    try:
        id = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер группы.")
        bot.register_next_step_handler(message, lambda msg: group_number_statys_teacher_1(msg, task_plan, user_id, what_time, date_time, name_of_discipline, facultet, group))
        return
    have = True
    for i in range(len(group)):
        if group[i][0] == id:
            have = False
            group_number = group[i][1]
            course = group[i][3]
            bot.send_message(message.chat.id, "Загрузите задание: документ или текст.")
            bot.register_next_step_handler(message,
                                           lambda msg: document_number_statys_teacher_1(msg, task_plan, user_id, what_time,
                                                                                      date_time,
                                                                                      name_of_discipline, facultet, group_number, course))
    if not have:
        bot.send_message(message.chat.id, "Неверный номер. Попробуйте ещё раз:")
        bot.register_next_step_handler(message,
                                       lambda msg: group_number_statys_teacher_1(msg, task_plan, user_id, what_time, date_time, name_of_discipline, facultet, group))
def document_number_statys_teacher_1(message, task_plan, user_id, what_time, date_time, name_of_discipline, facultet, group_number, course):
    if message.document:
        document = message.document
        file_id = document.file_id
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO task_for_student (send_date, send_time, name_of_discipline, the_task_for_student, document, group_number, teacher_id, faculty, course) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (date_time, what_time, name_of_discipline, task_plan, file_id, group_number, user_id, facultet, course))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id,"Вся информация загружена.\nПосле отправки задания придёт уведомление.")
        #ВЫВОД ЗАГРУЖЕНОЙ ИНФОРМАЦИИ
    else:
        bot.send_message(message.chat.id, "Пожалуйста, загрузите документ или текст.")
        bot.register_next_step_handler(message,
                                       lambda msg: document_number_statys_teacher_1(msg, task_plan, user_id, what_time, date_time, name_of_discipline, facultet, group_number, course))


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
    bot.send_message(chat_id=user_id, text=message)
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

def send_doc():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%d.%m")
    cursor.execute("""
            SELECT id, document, group_number, name_of_discipline, the_task_for_student, teacher_id, statys
            FROM task_for_student 
            WHERE send_time = ? AND send_date = ? """, (current_time, current_date))
    tasks = cursor.fetchall()
    for task in tasks:
        id, document, group_number, name_of_discipline, the_task_for_student, teacher_id, statys = task
        if not statys:
            cursor.execute("""
                UPDATE task_for_student 
                SET statys = 1 
                WHERE id = ?
            """, (id,))
            cursor.execute("""
                    SELECT student_id 
                    FROM student 
                    WHERE group_number = ? """, (group_number,))
            for_student = cursor.fetchall()
            for student in for_student:
                student_id = student[0]
                send_message_ga(student_id, f"{name_of_discipline}\nЗАДАНИЕ:\n{the_task_for_student}\n{document}")
                cursor.execute("UPDATE task_for_student SET document = NULL WHERE id= ?", (id,))
                send_message_ga(teacher_id, f"{name_of_discipline}\nЗадача{the_task_for_student}\n отправлена студентам группы {group_number}")
                conn.commit()
                conn.close()


scheduler = BackgroundScheduler()
# Запланируем выполнение функции check_tasks каждую минуту
scheduler.add_job(check_tasks, 'interval', minutes=1)
scheduler.add_job(send_doc,'interval', minutes=1)
scheduler.start()


bot.polling(none_stop=True)




