from mysql.connector import connect, Error


def init_db():
    create_db = """CREATE DATABASE IF NOT EXISTS wallet"""
    use_wallet = """USE wallet"""

    create_db_users = """
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT, 
    chat_id INTEGER NOT NULL UNIQUE,
    balance FLOAT(50, 2) DEFAULT 0.00
    )
    """

    create_db_categories = """
    CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTO_INCREMENT, 
    name VARCHAR(50) NOT NULL UNIQUE
    )
    """

    create_db_finances = """
    CREATE TABLE IF NOT EXISTS finances (
    id INTEGER PRIMARY KEY AUTO_INCREMENT, 
    time DATE NOT NULL, 
    amount REAL NOT NULL,
    comment TEXT, 
    user_id INTEGER NOT NULL, 
    category_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
    )
    """

    conn = connect(
        host="localhost",
        user='root',
        password='root',
    )
    cursor = conn.cursor()

    cursor.execute(create_db)
    cursor.execute(use_wallet)
    cursor.execute(create_db_users)
    cursor.execute(create_db_categories)
    cursor.execute(create_db_finances)

    conn.commit()
    conn.close()


def get_wallet_conn():
    conn = connect(
        host="localhost",
        user='root',
        password='root',
        database='wallet',
    )
    return conn


def add_user_to_bd(chat_id):
    conn = get_wallet_conn()
    cursor = conn.cursor()

    add_user = """INSERT IGNORE INTO users (chat_id) VALUES(%s)""", (chat_id, )

    cursor.execute(*add_user)

    conn.commit()
    conn.close()


def add_category_to_bd(name):
    conn = get_wallet_conn()
    cursor = conn.cursor()

    add_category = """INSERT IGNORE INTO categories (name) VALUES(%s)""", (name.lower(), )

    cursor.execute(*add_category)

    conn.commit()
    conn.close()


def get_user_id(chat_id):
    conn = get_wallet_conn()
    cursor = conn.cursor()

    sql_user_id = """SELECT id FROM users WHERE chat_id = %s""", (chat_id,)

    cursor.execute(*sql_user_id)
    row = cursor.fetchone()
    user_id = row[0]

    conn.close()

    return user_id


def get_user_balance(chat_id):
    conn = get_wallet_conn()
    cursor = conn.cursor()

    user_balance = """SELECT balance FROM users WHERE chat_id = %s""", (chat_id, )

    cursor.execute(*user_balance)
    row = cursor.fetchone()
    user_balance = row[0]

    conn.close()

    return user_balance


def update_user_balance(chat_id, increment):
    conn = get_wallet_conn()
    cursor = conn.cursor()

    user_balance = """UPDATE users SET balance = balance + %s WHERE chat_id = %s""", (increment, chat_id)
    cursor.execute(*user_balance)

    conn.commit()
    conn.close()


def get_category_id(category):
    conn = get_wallet_conn()
    cursor = conn.cursor()

    sql_category_id = """SELECT id FROM categories WHERE name = %s""", (category.lower(),)

    cursor.execute(*sql_category_id)
    row = cursor.fetchone()
    category_id = row[0]

    conn.close()

    return category_id


def get_categories():
    conn = get_wallet_conn()
    cursor = conn.cursor()

    categories = """
    SELECT id, name FROM categories
    ORDER BY id
    """
    cursor.execute(categories)
    rows = cursor.fetchall()

    conn.close()

    result = ('*Номер | Категория\n'
              + '\n'.join(['| '.join(map(str, row)) for row in rows]))
    return result


def add_row_to_finances(time, amount, chat_id, category, comment=None):
    conn = get_wallet_conn()
    cursor = conn.cursor()

    user_id = get_user_id(chat_id)
    category_id = get_category_id(category)
    insert_row = """
    INSERT INTO finances (time, amount, user_id, category_id, comment) 
    VALUES(%s, %s, %s, %s, %s)
    """, (time, amount, user_id, category_id, comment)
    cursor.execute(*insert_row)

    conn.commit()
    conn.close()

    update_user_balance(chat_id, amount)

    return get_user_balance(chat_id)


def update_row_in_table(table, key, name_parametr, new_value):
    conn = get_wallet_conn()
    cursor = conn.cursor()

    update_row = f"""
    UPDATE {table} SET {name_parametr} = %s 
    WHERE id = %s
    """, (new_value, key)
    cursor.execute(*update_row)

    conn.commit()
    conn.close()


def delete_row_from_finaces(key):
    conn = get_wallet_conn()
    cursor = conn.cursor()

    delete = """DELETE FROM finances WHERE id = %s """, (key, )

    cursor.execute(*delete)

    conn.commit()
    conn.close()


def get_data_in_finances(request):
    conn = get_wallet_conn()
    cursor = conn.cursor()

    cursor.execute(*request)
    rows = cursor.fetchall()

    conn.close()

    result = ('*Номер | Дата | Стоимость | Категория | Комментарий* \n'
              + '\n'.join(['| '.join(map(str, row)) for row in rows]))
    return result


def get_all_data_in_finances(chat_id):
    user_id = get_user_id(chat_id)
    request = """
    SELECT finances.id, finances.time, finances.amount, categories.name, finances.comment 
    FROM finances 
    JOIN categories 
    ON categories.id=finances.category_id 
    WHERE finances.user_id = %s
    """, (user_id, )

    return get_data_in_finances(request)


def get_data_in_finances_from_day(chat_id, day):
    user_id = get_user_id(chat_id)

    request = """
        SELECT finances.id, finances.time, finances.amount, categories.name, finances.comment 
        FROM finances 
        JOIN categories 
        ON categories.id=finances.category_id 
        WHERE finances.user_id = %s 
        AND finances.time = %s
        """, (user_id, day)

    return get_data_in_finances(request)


def get_data_in_finances_from_interval(chat_id, start_date, end_date):
    user_id = get_user_id(chat_id)

    request = """
        SELECT finances.id, finances.time, finances.amount, categories.name, finances.comment 
        FROM finances 
        JOIN categories 
        ON categories.id=finances.category_id 
        WHERE finances.user_id = %s 
        AND finances.time BETWEEN %s AND %s
        """, (user_id, start_date, end_date)

    return get_data_in_finances(request)


def get_row_from_table(table, key_name, key_value):
    conn = get_wallet_conn()
    cursor = conn.cursor()

    request = f"""
        SELECT * FROM {table}
        WHERE {key_name} = %s
        """, (key_value, )

    cursor.execute(*request)
    row = cursor.fetchone()

    conn.close()

    return row
