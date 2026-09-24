"""Ponto de entrada do sistema: menu interativo de tarefas e usuários."""

from datetime import datetime

from tarefas import (
    criar_tarefa,
    listar_tarefas,
    listar_tarefas_por_usuario,
    atualizar_tarefa,
    concluir_tarefa,
    deletar_tarefa,
)
from usuarios import criar_usuario, listar_usuarios, usuario_existe

PRIORIDADES_VALIDAS = ("baixa", "media", "alta")


def mostrar_menu():
    print("\n--- TAREFAS ---")
    print("1 - Nova tarefa")
    print("2 - Ver tarefas")
    print("3 - Editar tarefa")
    print("4 - Concluir tarefa")
    print("5 - Excluir tarefa")
    print("8 - Ver tarefas de um usuario")
    print("\n--- USUARIOS ---")
    print("6 - Novo usuario")
    print("7 - Ver usuarios")
    print("\n0 - Sair")


def pedir_numero(mensagem):
    """Pede um número e repete até a pessoa digitar algo válido."""
    valor = input(mensagem).strip()
    while not valor.isdigit():
        print("Digite apenas numeros.")
        valor = input(mensagem).strip()
    return valor


def pedir_prioridade():
    """Pede a prioridade por menu numérico, sem deixar a pessoa digitar texto livre."""
    print("Prioridade: 1-baixa, 2-media, 3-alta (Enter = media)")
    opcao = input("> ").strip()
    return {"1": "baixa", "2": "media", "3": "alta"}.get(opcao, "media")


def pedir_prazo():
    """Pede uma data no formato AAAA-MM-DD e valida antes de aceitar."""
    while True:
        prazo = input("Prazo (AAAA-MM-DD, Enter pra deixar em branco): ").strip()
        if not prazo:
            return None
        try:
            datetime.strptime(prazo, "%Y-%m-%d")
            return prazo
        except ValueError:
            print("Data inválida. Use o formato AAAA-MM-DD, ex: 2026-12-31.")


def opcao_nova_tarefa():
    print("\nUsuários cadastrados:")
    listar_usuarios()
    titulo = input("\nTitulo: ")
    descricao = input("Descricao: ")
    usuario_id = pedir_numero("ID do usuario: ")

    if not usuario_existe(usuario_id):
        print(f"Não existe usuário com ID {usuario_id}. Tarefa não foi criada.")
        return

    prioridade = pedir_prioridade()
    prazo = pedir_prazo()

    criar_tarefa(titulo, descricao, usuario_id, prioridade, prazo)


def opcao_editar_tarefa():
    tarefa_id = pedir_numero("ID da tarefa: ")
    titulo = input("Novo titulo (Enter pra manter o mesmo): ")
    descricao = input("Nova descricao (Enter pra manter a mesma): ")

    print("Nova prioridade: 1-baixa, 2-media, 3-alta (Enter pra manter)")
    opcao = input("> ").strip()
    prioridade = {"1": "baixa", "2": "media", "3": "alta"}.get(opcao)

    prazo = pedir_prazo()

    atualizar_tarefa(tarefa_id, titulo or None, descricao or None, prioridade, prazo)


def opcao_concluir_tarefa():
    tarefa_id = pedir_numero("ID da tarefa: ")
    concluir_tarefa(tarefa_id)


def opcao_excluir_tarefa():
    tarefa_id = pedir_numero("ID da tarefa: ")
    confirmacao = input(f"Tem certeza que quer excluir a tarefa {tarefa_id}? (s/n): ").strip().lower()
    if confirmacao == "s":
        deletar_tarefa(tarefa_id)
    else:
        print("Exclusão cancelada.")


def opcao_novo_usuario():
    nome = input("Nome: ")
    email = input("Email: ")
    criar_usuario(nome, email)


def opcao_tarefas_por_usuario():
    print("\nUsuários cadastrados:")
    listar_usuarios()
    usuario_id = pedir_numero("\nID do usuario: ")
    listar_tarefas_por_usuario(usuario_id)


def menu():
    opcoes = {
        "1": opcao_nova_tarefa,
        "2": listar_tarefas,
        "3": opcao_editar_tarefa,
        "4": opcao_concluir_tarefa,
        "5": opcao_excluir_tarefa,
        "6": opcao_novo_usuario,
        "7": listar_usuarios,
        "8": opcao_tarefas_por_usuario,
    }

    while True:
        mostrar_menu()
        opcao = input("> ").strip()

        if opcao == "0":
            break
        elif opcao in opcoes:
            opcoes[opcao]()
        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    menu()