import sqlite3

connection = sqlite3.connect("Get_weather.db")

cursor = connection.cursor()
# Создание таблиц базы
cursor.execute("""
CREATE TABLE IF NOT EXISTS weather_icons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_icon BLOB NOT NULL,
    night_icon TEXT UNIQUE NOT NULL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weather TEXT NOT NULL,
    icon_id INTEGER NOT NULL,
    FOREIGN KEY (icon_id) REFERENCES weather_icons(id) ON DELETE CASCADE
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    surname INTEGER NOT NULL,
    tg_name TEXT NOT NULL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

# Регистрация пользователя
def register_user(first_name, last_name, tg_name, town):
    connection = sqlite3.connect("Get_weather.db")
    cursor = connection.cursor()
    print(tg_name)
    print(is_user_registered(tg_name))
    if is_user_registered(tg_name) == None:
        cursor.execute(
            "INSERT INTO users (name, surname, tg_name, main_town) VALUES (?, ?, ?, ?)",
            (first_name, last_name, tg_name, town)
        )
        connection.commit()
        connection.close()
    else:
        return 'Вы уже зарегистрированы'
# Проверка регистрации пользователя
def is_user_registered(tg_name):
    connection = sqlite3.connect("Get_weather.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE tg_name = ?", (tg_name,))
    user = cursor.fetchone()
    connection.close()
    return user

def get_user_info(tg_name):
    connection = sqlite3.connect('Get_weather.db')
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE tg_name = ?"
    cursor.execute(query, (tg_name,))
    rows = cursor.fetchall()
    connection.close()
    return rows

def get_operations(user_id):
    connection = sqlite3.connect("Get_weather.db")
    cursor = connection.cursor()
    cursor.execute("SELECT city, operation_type FROM operations WHERE user_id = ? LIMIT 10",
             (user_id,))
    rows = cursor.fetchall()
    connection.close()
    return rows



def set_operation(city, operation, user_id):
    connection = sqlite3.connect("Get_weather.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO operations (city, operation_type, user_id) VALUES (?, ?, ?)",
                   (city, operation, user_id)
                   )
    connection.commit()
    connection.close()
    print("Correct")


connection.commit()
connection.close()

