import sqlite3


def init_db():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY, 
        chat_id TEXT UNIQUE NOT NULL)"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS categories
        (id INTEGER PRIMARY KEY, 
        name TEXT UNIQUE NOT NULL)"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS finances
        (id INTEGER PRIMARY KEY, 
        time TEXT NOT NULL, 
        amount REAL NOT NULL,
        comment TEXT, 
        user_id INTEGER NOT NULL, 
        category_id NOT NULL)"""
    )
    conn.commit()


def add_user_to_db(chat_id):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR IGNORE INTO users (chat_id) VALUES(?);""", (chat_id, )
    )
    conn.commit()


def add_category_to_db(name):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR IGNORE INTO categories (name) VALUES(?);""", (name.lower(), )
    )
    conn.commit()


def add_row_to_finances(time, amount, chat_id, category, comment=None):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute("""SELECT id FROM users WHERE chat_id = ?""", (chat_id, ))
    row = cursor.fetchone()
    user_id = row[0]
    cursor.execute("""SELECT id FROM categories WHERE name = ?""", (category.lower(), ))
    row = cursor.fetchone()
    category_id = row[0]
    cursor.execute(
        """INSERT INTO finances (time, amount, user_id, category_id, comment) 
        VALUES(?, ?, ?, ?, ?);""", (time, amount, user_id, category_id, comment)
    )
    conn.commit()


def change_row_in_finances(key, name_parametr, new_value):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    # Сделать кастомную ошибку на случай, если нет id
    # или неверное имя параметра

    if name_parametr == 'amount':
        new_value = float(new_value)
    if name_parametr == 'category_id':
        cursor.execute("""SELECT id FROM categories WHERE name = ?""",
                       (new_value.lower(),))
        new_value = cursor.fetchone()
        new_value = new_value[0]

    cursor.execute(
        f"""UPDATE finances SET {name_parametr} = {new_value} 
        WHERE id = {key};"""
    )
    conn.commit()


def delete_row_from_finaces(key):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    delete = f"""DELETE FROM finances WHERE id = {key} """
    cursor.execute(delete)
    conn.commit()


def read_data_in_finances(chat_id):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute("""SELECT id FROM users WHERE chat_id = ?""", (chat_id, ))
    row = cursor.fetchone()
    user_id = row[0]
    cursor.execute(
        """SELECT finances.id, finances.time, finances.amount, 
        categories.name, finances.comment 
        FROM 'finances' 
        JOIN categories ON categories.id=finances.category_id 
        WHERE finances.user_id = ?""", (user_id, )
    )
    rows = cursor.fetchall()

    result = ('*Номер | Дата | Стоимость | Категория | Комментарий* \n'
              + '\n'.join(['| '.join(map(str, row)) for row in rows]))
    return result

