from datetime import date

from db import conectar


def criar_tarefa(titulo, descricao, usuario_id):
    conexao = conectar()
    if not conexao:
        return

    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO tarefa (titulo, descricao, data_criacao, usuario_id) VALUES (%s, %s, %s, %s)",
        (titulo, descricao, date.today(), usuario_id),
    )
    conexao.commit()
    print("Tarefa criada, id:", cursor.lastrowid)

    cursor.close()
    conexao.close()


def listar_tarefas():
    conexao = conectar()
    if not conexao:
        return

    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tarefa ORDER BY id")
    tarefas = cursor.fetchall()

    if not tarefas:
        print("Ainda não tem nenhuma tarefa cadastrada.")

    for t in tarefas:
        status = "concluída" if t["data_conclusao"] else "pendente"
        print(f"#{t['id']} - {t['titulo']} ({status})")
        if t["descricao"]:
            print("   ", t["descricao"])

    cursor.close()
    conexao.close()


def buscar_tarefa(tarefa_id):
    conexao = conectar()
    if not conexao:
        return None

    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tarefa WHERE id = %s", (tarefa_id,))
    tarefa = cursor.fetchone()

    cursor.close()
    conexao.close()
    return tarefa


def atualizar_tarefa(tarefa_id, titulo=None, descricao=None):
    tarefa = buscar_tarefa(tarefa_id)
    if not tarefa:
        print("Não achei essa tarefa.")
        return

    novo_titulo = titulo or tarefa["titulo"]
    nova_descricao = descricao or tarefa["descricao"]

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "UPDATE tarefa SET titulo = %s, descricao = %s WHERE id = %s",
        (novo_titulo, nova_descricao, tarefa_id),
    )
    conexao.commit()
    print("Tarefa atualizada.")

    cursor.close()
    conexao.close()


def concluir_tarefa(tarefa_id):
    conexao = conectar()
    if not conexao:
        return

    cursor = conexao.cursor()
    cursor.execute(
        "UPDATE tarefa SET data_conclusao = %s WHERE id = %s",
        (date.today(), tarefa_id),
    )
    conexao.commit()

    if cursor.rowcount:
        print("Tarefa marcada como concluída.")
    else:
        print("Não achei essa tarefa.")

    cursor.close()
    conexao.close()


def deletar_tarefa(tarefa_id):
    conexao = conectar()
    if not conexao:
        return

    cursor = conexao.cursor()
    cursor.execute("DELETE FROM tarefa WHERE id = %s", (tarefa_id,))
    conexao.commit()

    if cursor.rowcount:
        print("Tarefa excluída.")
    else:
        print("Não achei essa tarefa.")

    cursor.close()
    conexao.close()