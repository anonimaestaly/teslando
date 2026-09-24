import mysql.connector
from mysql.connector import Error
from datetime import date

# ajuste esses dados de acordo com a sua instalação do mysql
config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "SUA_SENHA_AQUI",
    "database": "meu_banco",
}


def conectar():
    try:
        return mysql.connector.connect(**config)
    except Error as e:
        print("Não consegui conectar no banco:", e)
        return None


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


def menu():
    while True:
        print("\n1 - Nova tarefa")
        print("2 - Ver tarefas")
        print("3 - Editar tarefa")
        print("4 - Concluir tarefa")
        print("5 - Excluir tarefa")
        print("0 - Sair")

        opcao = input("> ").strip()

        if opcao == "1":
            titulo = input("Título: ")
            descricao = input("Descrição: ")
            usuario_id = input("ID do usuário: ")
            criar_tarefa(titulo, descricao, usuario_id)

        elif opcao == "2":
            listar_tarefas()

        elif opcao == "3":
            tarefa_id = input("ID da tarefa: ")
            titulo = input("Novo título (Enter pra manter o mesmo): ")
            descricao = input("Nova descrição (Enter pra manter a mesma): ")
            atualizar_tarefa(tarefa_id, titulo or None, descricao or None)

        elif opcao == "4":
            tarefa_id = input("ID da tarefa: ")
            concluir_tarefa(tarefa_id)

        elif opcao == "5":
            tarefa_id = input("ID da tarefa: ")
            deletar_tarefa(tarefa_id)

        elif opcao == "0":
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()