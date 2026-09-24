import os

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def conectar():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=os.getenv("DB_PORT", "3306"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "meu_banco"),
        )
    except Error as e:
        print("Não consegui conectar no banco:", e)
        return None