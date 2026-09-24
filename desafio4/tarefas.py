"""Funções para gerenciar tarefas no banco de dados."""

from datetime import date

from db import obter_cursor


def criar_tarefa(titulo, descricao, usuario_id, prioridade="media", prazo=None):
    """Cria uma nova tarefa vinculada a um usuário."""
    with obter_cursor() as cursor:
        if cursor is None:
            return
        cursor.execute(
            "INSERT INTO tarefa (titulo, descricao, data_criacao, usuario_id, prioridade, prazo) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (titulo, descricao, date.today(), usuario_id, prioridade, prazo),
        )
        print("Tarefa criada, id:", cursor.lastrowid)


def _imprimir_tarefas(tarefas):
    if not tarefas:
        print("Nenhuma tarefa encontrada.")
    for t in tarefas:
        status = "concluída" if t["data_conclusao"] else "pendente"
        prazo = f" | prazo: {t['prazo']}" if t["prazo"] else ""
        print(f"#{t['id']} - {t['titulo']} ({status}) [{t['prioridade']}]{prazo}")
        if t["descricao"]:
            print("   ", t["descricao"])


def listar_tarefas():
    """Mostra todas as tarefas cadastradas."""
    with obter_cursor(dictionary=True) as cursor:
        if cursor is None:
            return
        cursor.execute("SELECT * FROM tarefa ORDER BY id")
        _imprimir_tarefas(cursor.fetchall())


def listar_tarefas_por_usuario(usuario_id):
    """Mostra só as tarefas de um usuário específico."""
    with obter_cursor(dictionary=True) as cursor:
        if cursor is None:
            return
        cursor.execute(
            "SELECT * FROM tarefa WHERE usuario_id = %s ORDER BY id", (usuario_id,)
        )
        _imprimir_tarefas(cursor.fetchall())


def buscar_tarefa(tarefa_id):
    """Retorna os dados de uma tarefa pelo ID, ou None se não existir."""
    with obter_cursor(dictionary=True) as cursor:
        if cursor is None:
            return None
        cursor.execute("SELECT * FROM tarefa WHERE id = %s", (tarefa_id,))
        return cursor.fetchone()


def atualizar_tarefa(tarefa_id, titulo=None, descricao=None, prioridade=None, prazo=None):
    """Atualiza os campos informados de uma tarefa; mantém os demais como estão."""
    tarefa = buscar_tarefa(tarefa_id)
    if not tarefa:
        print("Não achei essa tarefa.")
        return

    novo_titulo = titulo or tarefa["titulo"]
    nova_descricao = descricao or tarefa["descricao"]
    nova_prioridade = prioridade or tarefa["prioridade"]
    novo_prazo = prazo or tarefa["prazo"]

    with obter_cursor() as cursor:
        if cursor is None:
            return
        cursor.execute(
            "UPDATE tarefa SET titulo = %s, descricao = %s, prioridade = %s, prazo = %s WHERE id = %s",
            (novo_titulo, nova_descricao, nova_prioridade, novo_prazo, tarefa_id),
        )
        print("Tarefa atualizada.")


def concluir_tarefa(tarefa_id):
    """Marca uma tarefa como concluída na data de hoje."""
    with obter_cursor() as cursor:
        if cursor is None:
            return
        cursor.execute(
            "UPDATE tarefa SET data_conclusao = %s WHERE id = %s",
            (date.today(), tarefa_id),
        )
        if cursor.rowcount:
            print("Tarefa marcada como concluída.")
        else:
            print("Não achei essa tarefa.")


def deletar_tarefa(tarefa_id):
    """Remove uma tarefa permanentemente."""
    with obter_cursor() as cursor:
        if cursor is None:
            return
        cursor.execute("DELETE FROM tarefa WHERE id = %s", (tarefa_id,))
        if cursor.rowcount:
            print("Tarefa excluída.")
        else:
            print("Não achei essa tarefa.")