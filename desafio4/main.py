from tarefas import (
    criar_tarefa,
    listar_tarefas,
    atualizar_tarefa,
    concluir_tarefa,
    deletar_tarefa,
)
from usuarios import criar_usuario, listar_usuarios


def mostrar_menu():
    print("\n--- TAREFAS ---")
    print("1 - Nova tarefa")
    print("2 - Ver tarefas")
    print("3 - Editar tarefa")
    print("4 - Concluir tarefa")
    print("5 - Excluir tarefa")
    print("\n--- USUÁRIOS ---")
    print("6 - Novo usuário")
    print("7 - Ver usuários")
    print("\n0 - Sair")


def pedir_numero(mensagem):
    """Pede um número e repete até a pessoa digitar algo válido."""
    valor = input(mensagem).strip()
    while not valor.isdigit():
        print("Digite apenas números.")
        valor = input(mensagem).strip()
    return valor


def opcao_nova_tarefa():
    titulo = input("Título: ")
    descricao = input("Descrição: ")
    usuario_id = pedir_numero("ID do usuário: ")
    criar_tarefa(titulo, descricao, usuario_id)


def opcao_editar_tarefa():
    tarefa_id = pedir_numero("ID da tarefa: ")
    titulo = input("Novo título (Enter pra manter o mesmo): ")
    descricao = input("Nova descrição (Enter pra manter a mesma): ")
    atualizar_tarefa(tarefa_id, titulo or None, descricao or None)


def opcao_concluir_tarefa():
    tarefa_id = pedir_numero("ID da tarefa: ")
    concluir_tarefa(tarefa_id)


def opcao_excluir_tarefa():
    tarefa_id = pedir_numero("ID da tarefa: ")