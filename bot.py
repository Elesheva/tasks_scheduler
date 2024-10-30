import telebot
import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, Application, MessageHandler, CallbackContext
from datetime import datetime
import pytz
import schedule
import time
import threading
from telebot import types

x = 'test'

bot = telebot.TeleBot('7206218529:AAGXx1IkHVxZ3IrFt09Xgzytanj1n-bpcUI')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    lastname = message.from_user.last_name
    if lastname is None:
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name} 👋 Я твой персональный помощник по планированию задач.")
    else:
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name} {lastname} 👋 Я твой персональный помощник по планированию задач.")

@bot.message_handler(commands=['add_task'])
def new_task(message):
    create_db()
    bot.send_message(message.chat.id, "Какую задачу хочешь запланировать?")
    bot.register_next_step_handler(message, lambda msg: whattime(msg, message.from_user.id))

def whattime(message, user_id):
    task_plan = message.text
    bot.send_message(message.chat.id, "На какое время?")
    bot.register_next_step_handler(message, lambda msg: save_task(msg, task_plan, user_id))

def save_task(message, task_plan, user_id):
    what_time = message.text
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO tasks (user_id, task, task_time) VALUES (?, ?, ?)', (user_id, task_plan, what_time))
    connection.commit()
    connection.close()
    bot.send_message(message.chat.id, "Задача добавлена!")

def create_db():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task TEXT,
        task_time TEXT
    ) """)
    connection.commit()
    cursor.close()
    connection.close()

@bot.message_handler(commands=['all_tasks'])
def get_all_tasks_from_db(message):
    user_id = message.from_user.id
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT task, task_time FROM tasks WHERE user_id = ?", (user_id,))
    tasks = cursor.fetchall()
    connection.commit()
    connection.close()
    output = "".join(f"{x[0]} - {x[1]}\n" for x in tasks)
    print(output)
    bot.send_message(message.chat.id, f"{message.from_user.first_name} {message.from_user.last_name}, все твои задачи:")
    bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['delete_tasks'])
def delete_task_from_db(message):
    user_id = message.from_user.id
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT (*) FROM tasks WHERE user_id = ?", (user_id,))
    count = cursor.fetchone() [0]
    if count > 0:
        cursor.execute("SELECT id, task, task_time FROM tasks WHERE user_id = ?", (user_id,))
        tasks = cursor.fetchall()
        connection.commit()
        connection.close()
        print(tasks)
        output = "".join(f"{x[0]} - {x[1]}, {x[2]}\n" for x in tasks)
        print(output)
        bot.send_message(message.chat.id, f"{message.from_user.first_name} {message.from_user.last_name}, все твои задачи:")
        bot.send_message(message.chat.id, output)
        bot.send_message(message.chat.id, "Напиши номер задачи, которую хочешь удалить.")
        bot.register_next_step_handler(message, lambda msg: delete_tasks_from_db(msg))
    else:
        bot.send_message(message.chat.id, "У тебя нет задач")

def delete_tasks_from_db(message):
    id = message.text
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
        bot.send_message(message.chat.id, "Список задач пуст.")






bot.polling(none_stop=True)