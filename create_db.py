import sqlite3

def create_db():
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
            group_number TEXT
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
            group_number TEXT, 
            faculty TEXT,
            course INTEGER
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()
