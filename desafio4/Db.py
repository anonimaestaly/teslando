import os
from contextlib import contextmanager

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


@contextmanager
def obter_cursor(dictionary=False):
    """
    Abre conexão + cursor, garante commit no final e fecha tudo sozinho.
    Uso:
        with obter_cursor() as cursor:
            if cursor is None:
                return
            cursor.execute(...)
    """
    conexao = conectar()
    if not conexao:
        yield None
        return

    cursor = conexao.cursor(dictionary=dictionary)
    try:
        yield cursor
        conexao.commit()
    finally:
        cursor.close()
        conexao.close()