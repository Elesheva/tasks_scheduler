import telebot
import sqlite3

bot = telebot.TeleBot('7206218529:AAGXx1IkHVxZ3IrFt09Xgzytanj1n-bpcUI')

def create_db():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task TEXT,
            task_time TEXT
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    lastname = message.from_user.last_name
    if lastname is None:
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name} 👋 Я твой персональный помощник по планированию задач.")
    else:
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name} {lastname} 👋 Я твой персональный помощник по планированию задач.")

@bot.message_handler(commands=['add_task'])
def new_task(message):
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

# Создаем базу данных при запуске бота
create_db()

# Запускаем бота
bot.polling(none_stop=True)