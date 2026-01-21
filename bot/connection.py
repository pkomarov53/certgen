import pymysql
import pymysql.cursors
from datetime import datetime

DB_CONFIG = {
    "host": "",
    "port": "",
    "user": "",
    "password": "",
    "database": "",
    "cursorclass": pymysql.cursors.DictCursor
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS certificates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    full_name VARCHAR(255),
                    cert_number VARCHAR(50) UNIQUE,
                    issue_date DATETIME
                )
            ''')
        conn.commit()
    finally:
        conn.close()

def check_user_exists(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT cert_number FROM certificates WHERE user_id = %s", (user_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def save_cert(user_id, name, cert_num):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO certificates (user_id, full_name, cert_number, issue_date) VALUES (%s, %s, %s, %s)",
                (user_id, name, cert_num, datetime.now())
            )
        conn.commit()
    finally:
        conn.close()
