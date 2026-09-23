"""
CRUD de Tarefas — MySQL
=======================

Requisitos:
    pip install mysql-connector-python

Antes de rodar, execute o script sql/schema.sql no seu servidor MySQL
para criar o banco `gestao_tarefas` e as tabelas `usuario` e `tarefa`.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime

import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "sua_senha_aqui",
    "database": "gestao_tarefas",
}


@contextmanager
def get_connection():
    """Context manager que abre e fecha a conexão automaticamente."""
    conn: MySQLConnection = mysql.connector.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------
def criar_tarefa(titulo: str, descricao: str, usuario_id: int) -> int:
    """Cria uma nova tarefa e retorna o id gerado."""
    sql = """
        INSERT INTO tarefa (titulo, descricao, usuario_id)
        VALUES (%s, %s, %s)
    """
    with get_connection() as conn:
        cursor: MySQLCursor = conn.cursor()
        cursor.execute(sql, (titulo, descricao, usuario_id))
        conn.commit()
        return cursor.lastrowid


# ---------------------------------------------------------------
# READ
# ---------------------------------------------------------------
def listar_tarefas(usuario_id: int | None = None) -> list[dict]:
    """Lista todas as tarefas, ou apenas as de um usuário se informado."""
    sql = "SELECT * FROM tarefa"
    params: tuple = ()
    if usuario_id is not None:
        sql += " WHERE usuario_id = %s"
        params = (usuario_id,)
    sql += " ORDER BY data_criacao DESC"

    with get_connection() as conn:
        cursor: MySQLCursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchall()


def buscar_tarefa_por_id(tarefa_id: int) -> dict | None:
    """Busca uma única tarefa pelo id. Retorna None se não existir."""
    sql = "SELECT * FROM tarefa WHERE id = %s"
    with get_connection() as conn:
        cursor: MySQLCursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (tarefa_id,))
        return cursor.fetchone()


# ---------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------
def atualizar_tarefa(tarefa_id: int, titulo: str, descricao: str) -> bool:
    """Atualiza título e descrição de uma tarefa. Retorna True se alterou algo."""
    sql = """
        UPDATE tarefa
        SET titulo = %s, descricao = %s
        WHERE id = %s
    """
    with get_connection() as conn:
        cursor: MySQLCursor = conn.cursor()
        cursor.execute(sql, (titulo, descricao, tarefa_id))
        conn.commit()
        return cursor.rowcount > 0


def concluir_tarefa(tarefa_id: int) -> bool:
    """Marca a tarefa como concluída e registra a data de conclusão."""
    sql = """
        UPDATE tarefa
        SET status = 'concluida', data_conclusao = %s
        WHERE id = %s
    """
    with get_connection() as conn:
        cursor: MySQLCursor = conn.cursor()
        cursor.execute(sql, (datetime.now(), tarefa_id))
        conn.commit()
        return cursor.rowcount > 0


# ---------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------
def deletar_tarefa(tarefa_id: int) -> bool:
    """Remove uma tarefa pelo id. Retorna True se algo foi removido."""
    sql = "DELETE FROM tarefa WHERE id = %s"
    with get_connection() as conn:
        cursor: MySQLCursor = conn.cursor()
        cursor.execute(sql, (tarefa_id,))
        conn.commit()
        return cursor.rowcount > 0


# ---------------------------------------------------------------
# Demonstração
# ---------------------------------------------------------------
if __name__ == "__main__":
    novo_id = criar_tarefa(
        titulo="Praticar consultas SQL",
        descricao="Resolver 10 exercícios de JOIN",
        usuario_id=1,
    )
    print(f"Tarefa criada com id {novo_id}")

    print("\nTarefas do usuário 1:")
    for tarefa in listar_tarefas(usuario_id=1):
        print(tarefa)

    print("\nBuscando tarefa recém-criada:")
    print(buscar_tarefa_por_id(novo_id))

    atualizar_tarefa(novo_id, "Praticar SQL avançado", "Focar em subqueries e índices")
    concluir_tarefa(novo_id)

    print("\nTarefa após update e conclusão:")
    print(buscar_tarefa_por_id(novo_id))

    deletar_tarefa(novo_id)
    print("\nTarefa deletada.")