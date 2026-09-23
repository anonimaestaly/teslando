
import mysql.connector
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "mysql" / "schema.mysql"

# troque pelos dados reais do seu MySQL antes de rodar
DB_CONFIG = {
    "host": "localhost",
    "user": "seu_usuario",
    "password": "sua_senha",
    "database": "gestao_tarefas",
}


@contextmanager
def conectar():
    """Abre uma conexão, garante commit no final e rollback se algo quebrar.

    No SQLite eu usava `conn.row_factory = sqlite3.Row` pra pegar os
    resultados como dict. Aqui isso não existe — cada função que lê
    dados abre o cursor com `dictionary=True` na hora, então o resto
    do código (tipo `tarefa["titulo"]`) continua funcionando igual.
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def inicializar_banco():
    # aqui não dá pra usar conectar() direto, porque ele já assume que
    # o banco "gestao_tarefas" existe — e o schema.sql é quem cria esse
    # banco (CREATE DATABASE + USE). Então essa primeira conexão precisa
    # ser "sem banco nenhum selecionado" ainda.
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )
    try:
        cursor = conn.cursor()
        script = SCHEMA_PATH.read_text(encoding="utf-8")
        # o executescript do sqlite não existe aqui — o jeito do
        # mysql-connector rodar vários comandos SQL de uma vez é isso,
        # passando multi=True e iterando os resultados
        for _ in cursor.execute(script, multi=True):
            pass
        conn.commit()
        cursor.close()
    finally:
        conn.close()


def criar_tarefa(titulo, descricao, usuario_id, status="pendente"):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tarefa (titulo, descricao, status, usuario_id) VALUES (%s, %s, %s, %s)",
            (titulo, descricao, status, usuario_id),
        )
        novo_id = cursor.lastrowid
        cursor.close()
        return novo_id


def listar_tarefas(usuario_id=None):
    # se vier usuario_id, filtra só as tarefas dele; senão, lista geral
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        if usuario_id is not None:
            cursor.execute(
                "SELECT * FROM tarefa WHERE usuario_id = %s ORDER BY data_criacao DESC",
                (usuario_id,),
            )
        else:
            cursor.execute("SELECT * FROM tarefa ORDER BY data_criacao DESC")
        resultado = cursor.fetchall()
        cursor.close()
        return resultado


def buscar_tarefa_por_id(tarefa_id):
    with conectar() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tarefa WHERE id = %s", (tarefa_id,))
        resultado = cursor.fetchone()
        cursor.close()
        return resultado


def atualizar_tarefa(tarefa_id, titulo=None, descricao=None, status=None):
    tarefa = buscar_tarefa_por_id(tarefa_id)
    if tarefa is None:
        return False

    # só troca o que foi passado; o resto mantém o valor atual
    titulo = titulo if titulo is not None else tarefa["titulo"]
    descricao = descricao if descricao is not None else tarefa["descricao"]
    status = status if status is not None else tarefa["status"]

    # o schema exige: data_conclusao preenchida SE E SOMENTE SE status = 'concluida'.
    # se o status está deixando de ser 'concluida', a data_conclusao tem que ser zerada
    # pra não violar o CHECK do banco.
    if status == "concluida":
        data_conclusao = (
            tarefa["data_conclusao"]
            if tarefa["status"] == "concluida"
            else datetime.now().replace(microsecond=0)
        )
    else:
        data_conclusao = None

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "update tarefa"
        )