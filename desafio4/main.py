"""Ponto de entrada do sistema: menu interativo de tarefas e usuários."""

from datetime import datetime
from mysql.connector import Error

from tarefas import (
    criar_tarefa,
    listar_tarefas,
    listar_tarefas_por_usuario,
    imprimir_tarefas,
    atualizar_tarefa,
    concluir_tarefa,
    deletar_tarefa,
)
from usuarios import criar_usuario, listar_usuarios, usuario_existe

PRIORIDADES_MENU = {"1": "baixa", "2": "media", "3": "alta"}


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
    return PRIORIDADES_MENU.get(opcao, "media")


def data_valida(texto):
    """Retorna True se o texto está no formato AAAA-MM-DD e é uma data real."""
    try:
        datetime.strptime(texto, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def pedir_prazo():
    """Pede uma data no formato AAAA-MM-DD e valida antes de aceitar."""
    while True:
        prazo = input("Prazo (AAAA-MM-DD, Enter pra deixar em branco): ").strip()
        if not prazo:
            return None
        if data_valida(prazo):
            return prazo
        print("Data inválida. Use o formato AAAA-MM-DD, ex: 2026-12-31.")


def opcao_nova_tarefa():
    print("\nUsuários cadastrados:")
    listar_usuarios()

    titulo = input("\nTitulo: ").strip()
    while not titulo:
        print("O título não pode ficar vazio.")
        titulo = input("Titulo: ").strip()

    descricao = input("Descricao: ")
    usuario_id = pedir_numero("ID do usuario: ")

    if not usuario_existe(usuario_id):
        print(f"Não existe usuário com ID {usuario_id}. Tarefa não foi criada.")
        return

    prioridade = pedir_prioridade()
    prazo = pedir_prazo()

    tarefa_id = criar_tarefa(titulo, descricao, usuario_id, prioridade, prazo)
    print(f"Tarefa #{tarefa_id} criada.")


def opcao_ver_tarefas():
    print("\nTarefas cadastradas:")
    imprimir_tarefas(listar_tarefas())


def opcao_editar_tarefa():
    tarefa_id = pedir_numero("ID da tarefa: ")

    # Só entra em "campos" o que a pessoa realmente quis mudar.
    campos = {}

    titulo = input("Novo titulo (Enter pra manter o mesmo): ").strip()
    if titulo:
        campos["titulo"] = titulo

    descricao = input("Nova descricao (Enter pra manter a mesma): ").strip()
    if descricao:
        campos["descricao"] = descricao

    print("Nova prioridade: 1-baixa, 2-media, 3-alta (Enter pra manter)")
    prioridade = PRIORIDADES_MENU.get(input("> ").strip())
    if prioridade:
        campos["prioridade"] = prioridade

    while True:
        prazo = input(
            "Novo prazo (AAAA-MM-DD, Enter pra manter, - pra remover o prazo): "
        ).strip()
        if not prazo:
            break
        if prazo == "-":
            campos["prazo"] = None
            break
        if data_valida(prazo):
            campos["prazo"] = prazo
            break
        print("Data inválida. Use o formato AAAA-MM-DD, ex: 2026-12-31.")

    if not campos:
        print("Nada foi alterado.")
        return

    if atualizar_tarefa(tarefa_id, **campos):
        print("Tarefa atualizada.")
    else:
        print("Tarefa não encontrada.")


def opcao_concluir_tarefa():
    tarefa_id = pedir_numero("ID da tarefa: ")
    resultado = concluir_tarefa(tarefa_id)
    mensagens = {
        "concluida": "Tarefa concluída.",
        "ja_concluida": "Essa tarefa já estava concluída.",
        "nao_encontrada": "Tarefa não encontrada.",
    }
    print(mensagens[resultado])


def opcao_excluir_tarefa():
    tarefa_id = pedir_numero("ID da tarefa: ")
    confirmacao = input(f"Tem certeza que quer excluir a tarefa {tarefa_id}? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("Exclusão cancelada.")
        return

    if deletar_tarefa(tarefa_id):
        print("Tarefa excluída.")
    else:
        print("Tarefa não encontrada.")


def opcao_novo_usuario():
    nome = input("Nome: ")
    email = input("Email: ")
    criar_usuario(nome, email)


def opcao_tarefas_por_usuario():
    print("\nUsuários cadastrados:")
    listar_usuarios()
    usuario_id = pedir_numero("\nID do usuario: ")
    imprimir_tarefas(listar_tarefas_por_usuario(usuario_id))


def menu():
    opcoes = {
        "1": opcao_nova_tarefa,
        "2": opcao_ver_tarefas,
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
            try:
                opcoes[opcao]()
            except (ValueError, ConnectionError, Error) as erro:
                print(f"Erro: {erro}")
        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    menu()