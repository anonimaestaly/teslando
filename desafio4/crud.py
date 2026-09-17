"""CRUD de tarefas usando SQLite."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "sql" / "tarefas.db"
SCHEMA_PATH = Path(__file__).parent.parent / "sql" / "schema.sql"


@contextmanager
def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def inicializar_banco():
    with conectar() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def criar_tarefa(titulo, descricao, usuario_id, status="pendente"):
    with conectar() as conn:
        cursor = conn.execute(
            "INSERT INTO tarefa (titulo, descricao, status, usuario_id) VALUES (?, ?, ?, ?)",
            (titulo, descricao, status, usuario_id),
        )
        return cursor.lastrowid


def listar_tarefas(usuario_id=None):
    with conectar() as conn:
        if usuario_id is not None:
            cursor = conn.execute(
                "SELECT * FROM tarefa WHERE usuario_id = ? ORDER BY data_criacao DESC",
                (usuario_id,),
            )
        else:
            cursor = conn.execute("SELECT * FROM tarefa ORDER BY data_criacao DESC")
        return cursor.fetchall()


def buscar_tarefa_por_id(tarefa_id):
    with conectar() as conn:
        return conn.execute("SELECT * FROM tarefa WHERE id = ?", (tarefa_id,)).fetchone()


def atualizar_tarefa(tarefa_id, titulo=None, descricao=None, status=None):
    tarefa = buscar_tarefa_por_id(tarefa_id)
    if tarefa is None:
        return False

    # só troca o que foi passado; o resto mantém o valor atual
    titulo = titulo if titulo is not None else tarefa["titulo"]
    descricao = descricao if descricao is not None else tarefa["descricao"]
    status = status if status is not None else tarefa["status"]

    with conectar() as conn:
        conn.execute(
            "UPDATE tarefa SET titulo = ?, descricao = ?, status = ? WHERE id = ?",
            (titulo, descricao, status, tarefa_id),
        )
    return True


def concluir_tarefa(tarefa_id):
    if buscar_tarefa_por_id(tarefa_id) is None:
        return False

    agora = datetime.now().isoformat(sep=" ", timespec="seconds")
    with conectar() as conn:
        conn.execute(
            "UPDATE tarefa SET status = 'concluida', data_conclusao = ? WHERE id = ?",
            (agora, tarefa_id),
        )
    return True


def deletar_tarefa(tarefa_id):
    with conectar() as conn:
        cursor = conn.execute("DELETE FROM tarefa WHERE id = ?", (tarefa_id,))
        return cursor.rowcount > 0


def _print_tarefas(tarefas):
    if not tarefas:
        print("  nenhuma tarefa encontrada")
    for t in tarefas:
        print(f"  [{t['id']}] {t['titulo']} — {t['status']} (concluída: {t['data_conclusao']})")


if __name__ == "__main__":
    inicializar_banco()
    usuario_id = 1

    id1 = criar_tarefa("Estudar SQL", "Revisar JOINs e normalização", usuario_id)
    id2 = criar_tarefa("Fazer exercícios de Python", "5 problemas no HackerRank", usuario_id)

    print("tarefas criadas:")
    _print_tarefas(listar_tarefas(usuario_id))

    atualizar_tarefa(id1, status="em_andamento")
    concluir_tarefa(id2)

    print("\napós atualizar e concluir:")
    _print_tarefas(listar_tarefas(usuario_id))

    deletar_tarefa(id1)
    print("\napós deletar a primeira:")
    _print_tarefas(listar_tarefas(usuario_id))