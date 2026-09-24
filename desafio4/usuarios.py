"""Funções para gerenciar usuários no banco de dados."""

import re

from mysql.connector.errors import IntegrityError

from db import obter_cursor


def email_valido(email):
    """Verifica se o email tem um formato básico válido (algo@algo.algo)."""
    padrao = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(padrao, email) is not None


def criar_usuario(nome, email):
    """Cria um novo usuário. Recusa email inválido ou duplicado."""
    if not email_valido(email):
        print("Email inválido. Usuário não foi criado.")
        return

    try:
        with obter_cursor() as cursor:
            if cursor is None:
                return
            cursor.execute(
                "INSERT INTO usuario (nome, email) VALUES (%s, %s)",
                (nome, email),
            )
            print("Usuário criado, id:", cursor.lastrowid)
    except IntegrityError:
        print("Já existe um usuário com esse email.")


def listar_usuarios():
    """Mostra todos os usuários cadastrados."""
    with obter_cursor(dictionary=True) as cursor:
        if cursor is None:
            return
        cursor.execute("SELECT * FROM usuario ORDER BY id")
        usuarios = cursor.fetchall()

        if not usuarios:
            print("Ainda não tem nenhum usuário cadastrado.")

        for u in usuarios:
            print(f"#{u['id']} - {u['nome']} ({u['email']})")


def usuario_existe(usuario_id):
    """Retorna True se existir um usuário com esse ID."""
    with obter_cursor() as cursor:
        if cursor is None:
            return False
        cursor.execute("SELECT id FROM usuario WHERE id = %s", (usuario_id,))
        return cursor.fetchone() is not None