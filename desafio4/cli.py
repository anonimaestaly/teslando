"""
CLI - Gestão de Tarefas (MySQL)

Dependências:
    pip install mysql-connector-python

Executar:
    python cli.py
"""

from mysql.connector import Error

import crud

MENU = """
====== GESTÃO DE TAREFAS ======
1. Criar usuário
2. Listar usuários
3. Criar tarefa
4. Listar tarefas
5. Ver detalhes de uma tarefa
6. Atualizar tarefa
7. Concluir tarefa
8. Excluir tarefa
0. Sair
> """


def input_int(mensagem: str) -> int:
    while True:
        valor = input(mensagem).strip()
        if valor.isdigit():
            return int(valor)
        print("Digite um número válido.")


def criar_usuario():
    nome = input("Nome: ").strip()
    email = input("Email: ").strip()
    try:
        usuario_id = crud.criar_usuario(nome, email)
        print(f"Usuário criado com id {usuario_id}.")
    except Error as e:
        print(f"Erro ao criar usuário: {e}")


def listar_usuarios():
    usuarios = crud.listar_usuarios()
    if not usuarios:
        print("Nenhum usuário cadastrado.")
        return
    for u in usuarios:
        print(f"[{u['id']}] {u['nome']} <{u['email']}>")


def criar_tarefa():
    usuario_id = input_int("ID do usuário: ")
    if not crud.buscar_usuario(usuario_id):
        print("Usuário não encontrado.")
        return
    titulo = input("Título: ").strip()
    descricao = input("Descrição: ").strip()
    try:
        tarefa_id = crud.criar_tarefa(usuario_id, titulo, descricao)
        print(f"Tarefa criada com id {tarefa_id}.")
    except Error as e:
        print(f"Erro ao criar tarefa: {e}")


def listar_tarefas():
    filtro = input("Filtrar por ID de usuário (Enter para ver todas): ").strip()
    usuario_id = int(filtro) if filtro.isdigit() else None
    tarefas = crud.listar_tarefas(usuario_id)
    if not tarefas:
        print("Nenhuma tarefa encontrada.")
        return
    for t in tarefas:
        print(
            f"[{t['id']}] {t['titulo']} - status: {t['status']} "
            f"(usuário {t['usuario_id']})"
        )


def ver_tarefa():
    tarefa_id = input_int("ID da tarefa: ")
    tarefa = crud.buscar_tarefa(tarefa_id)
    if not tarefa:
        print("Tarefa não encontrada.")
        return
    for chave, valor in tarefa.items():
        print(f"{chave}: {valor}")


def atualizar_tarefa():
    tarefa_id = input_int("ID da tarefa: ")
    if not crud.buscar_tarefa(tarefa_id):
        print("Tarefa não encontrada.")
        return
    titulo = input("Novo título (Enter para manter): ").strip()
    descricao = input("Nova descrição (Enter para manter): ").strip()

    campos = {}
    if titulo:
        campos["titulo"] = titulo
    if descricao:
        campos["descricao"] = descricao

    if not campos:
        print("Nada para atualizar.")
        return

    crud.atualizar_tarefa(tarefa_id, **campos)
    print("Tarefa atualizada.")


def concluir_tarefa():
    tarefa_id = input_int("ID da tarefa: ")
    if crud.concluir_tarefa(tarefa_id):
        print("Tarefa marcada como concluída.")
    else:
        print("Tarefa não encontrada.")


def excluir_tarefa():
    tarefa_id = input_int("ID da tarefa: ")
    if crud.excluir_tarefa(tarefa_id):
        print("Tarefa excluída.")
    else:
        print("Tarefa não encontrada.")


ACOES = {
    "1": criar_usuario,
    "2": listar_usuarios,
    "3": criar_tarefa,
    "4": listar_tarefas,
    "5": ver_tarefa,
    "6": atualizar_tarefa,
    "7": concluir_tarefa,
    "8": excluir_tarefa,
}


def main():
    while True:
        opcao = input(MENU).strip()
        if opcao == "0":
            print("Até mais!")
            break
        acao = ACOES.get(opcao)
        if acao:
            acao()
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()