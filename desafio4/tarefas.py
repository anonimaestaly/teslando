"""Funções para gerenciar tarefas no banco de dados."""

from contextlib import contextmanager
from datetime import date

from db import obter_cursor

PRIORIDADES = {"baixa", "media", "alta"}

# Valor especial para saber se o argumento foi informado ou não.
# Assim None pode significar "limpar o campo" (ex.: remover o prazo).
_NAO_INFORMADO = object()


@contextmanager
def _cursor(**kwargs):
    """Abre um cursor e levanta erro claro se a conexão falhar."""
    with obter_cursor(**kwargs) as cursor:
        if cursor is None:
            raise ConnectionError("Não foi possível conectar ao banco de dados.")
        yield cursor


def _validar_prioridade(prioridade):
    if prioridade not in PRIORIDADES:
        opcoes = ", ".join(sorted(PRIORIDADES))
        raise ValueError(f"Prioridade inválida: {prioridade!r}. Use uma de: {opcoes}.")


def criar_tarefa(titulo, descricao, usuario_id, prioridade="media", prazo=None):
    """Cria uma nova tarefa vinculada a um usuário e retorna o id dela."""
    if not titulo or not titulo.strip():
        raise ValueError("O título não pode ser vazio.")
    _validar_prioridade(prioridade)

    with _cursor() as cursor:
        cursor.execute(
            "INSERT INTO tarefa (titulo, descricao, data_criacao, usuario_id, prioridade, prazo) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (titulo.strip(), descricao, date.today(), usuario_id, prioridade, prazo),
        )
        return cursor.lastrowid


def imprimir_tarefas(tarefas):
    """Imprime uma lista de tarefas (dicionários) de forma legível."""
    if not tarefas:
        print("Nenhuma tarefa encontrada.")
        return
    for t in tarefas:
        status = "concluída" if t["data_conclusao"] else "pendente"
        prazo = f" | prazo: {t['prazo']}" if t["prazo"] else ""
        print(f"#{t['id']} - {t['titulo']} ({status}) [{t['prioridade']}]{prazo} | usuário: #{t['usuario_id']}")
        if t["descricao"]:
            print("   ", t["descricao"])


def listar_tarefas():
    """Retorna todas as tarefas cadastradas."""
    with _cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM tarefa ORDER BY id")
        return cursor.fetchall()


def listar_tarefas_por_usuario(usuario_id):
    """Retorna só as tarefas de um usuário específico."""
    with _cursor(dictionary=True) as cursor:
        cursor.execute(
            "SELECT * FROM tarefa WHERE usuario_id = %s ORDER BY id", (usuario_id,)
        )
        return cursor.fetchall()


def buscar_tarefa(tarefa_id):
    """Retorna os dados de uma tarefa pelo ID, ou None se não existir."""
    with _cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM tarefa WHERE id = %s", (tarefa_id,))
        return cursor.fetchone()


def atualizar_tarefa(
    tarefa_id,
    titulo=_NAO_INFORMADO,
    descricao=_NAO_INFORMADO,
    prioridade=_NAO_INFORMADO,
    prazo=_NAO_INFORMADO,
):
    """Atualiza só os campos informados; os demais ficam como estão.

    Passe None em descricao ou prazo para limpar o campo.
    Retorna True se a tarefa existe, False se não foi encontrada.
    """
    tarefa = buscar_tarefa(tarefa_id)
    if not tarefa:
        return False

    if titulo is not _NAO_INFORMADO and (not titulo or not titulo.strip()):
        raise ValueError("O título não pode ser vazio.")
    if prioridade is not _NAO_INFORMADO:
        _validar_prioridade(prioridade)

    novo_titulo = tarefa["titulo"] if titulo is _NAO_INFORMADO else titulo.strip()
    nova_descricao = tarefa["descricao"] if descricao is _NAO_INFORMADO else descricao
    nova_prioridade = tarefa["prioridade"] if prioridade is _NAO_INFORMADO else prioridade
    novo_prazo = tarefa["prazo"] if prazo is _NAO_INFORMADO else prazo

    with _cursor() as cursor:
        cursor.execute(
            "UPDATE tarefa SET titulo = %s, descricao = %s, prioridade = %s, prazo = %s "
            "WHERE id = %s",
            (novo_titulo, nova_descricao, nova_prioridade, novo_prazo, tarefa_id),
        )
    return True


def concluir_tarefa(tarefa_id):
    """Marca uma tarefa como concluída hoje, sem sobrescrever conclusão anterior.

    Retorna "concluida", "ja_concluida" ou "nao_encontrada".
    """
    with _cursor() as cursor:
        cursor.execute(
            "UPDATE tarefa SET data_conclusao = %s "
            "WHERE id = %s AND data_conclusao IS NULL",
            (date.today(), tarefa_id),
        )
        if cursor.rowcount:
            return "concluida"

    # Nenhuma linha mudou: ou não existe, ou já estava concluída.
    return "ja_concluida" if buscar_tarefa(tarefa_id) else "nao_encontrada"


def deletar_tarefa(tarefa_id):
    """Remove uma tarefa permanentemente. Retorna True se ela existia."""
    with _cursor() as cursor:
        cursor.execute("DELETE FROM tarefa WHERE id = %s", (tarefa_id,))
        return cursor.rowcount > 0