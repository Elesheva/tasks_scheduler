import sqlite3

def create_db():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    # Создание таблицы teacher_comment (преподаватель)
    cursor.execute("""
             CREATE TABLE IF NOT EXISTS teacher_comment (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 task_id INTEGER,
                 student_id INTEGER,
                 name_teacher TEXT,
                 teacher_id INTEGER,
                 name_of_discipline TEXT,
                 the_task_for_student TEXT,
                 send_time TEXT,
                 date TEXT,
                 group_number TEXT,
                 comment TEXT,
                 mark INTEGER
             )
         """)

    # Создание таблицы tasks (ПЕРСОНАЛЬНАЯ ДЛЯ СТУДЕНТА)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task TEXT,
            task_time TEXT,
            date TEXT,
            regular_task BOOLEAN,
            count_regular_task INTEGER,
            regular_statys INTEGER,
            complete BOOLEAN
        )
    """)
    cursor.execute("DROP TABLE task_list")
    # Создание таблицы task_list (УЧЕБНАЯ ДЛЯ СТУДЕНТА)
    cursor.execute("""
         CREATE TABLE IF NOT EXISTS task_list (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             task_id INTEGER,
             student_id INTEGER,
             name_student TEXT,
             teacher_id INTEGER,
             name_of_discipline TEXT,
             the_task_for_student TEXT,
             document BLOB,
             task_time TEXT,
             date TEXT,
             send_teacher_for_student_date TEXT, 
             send_mark_date TEXT,
             group_number TEXT,
             complete BOOLEAN
         )
     """)


    # Создание таблицы statystic_for_student (Результат по персональным задачам для студента)
    cursor.execute("""
         CREATE TABLE IF NOT EXISTS statystic_for_student (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             student_id INTEGER,
             document BLOB,
             complete INTEGER,
             dont_complete INTEGER,
             all_tasks INTEGER
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
    # Создание таблицы task_for_student
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_for_student (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            send_date TEXT,
            send_time TEXT,
            name_of_discipline TEXT,
            the_task_for_student TEXT,
            document BLOB,
            group_number TEXT, 
            teacher_id INTEGER, 
            faculty TEXT,
            course INTEGER,
            statys BOOLEAN
        )
    """)

    # Создание таблицы parol
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parol (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parol_for_teacher TEXT,
            parol_for_student TEXT,
            id_admin INTEGER
        )
    """)

    # Создание таблицы с обращениями к администратору
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_user INTEGER,
                    text_for_admin TEXT
                )
            """)

    connection.commit()
    cursor.close()
    connection.close()
