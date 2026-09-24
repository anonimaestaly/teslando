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
    print("\n--- USUARIOS ---")
    print("6 - Novo usuario")
    print("7 - Ver usuarios")
    print("\n0 - Sair")


def pedir_numero(mensagem):
    """Pede um numero e repete ate a pessoa digitar algo valido."""
    valor = input(mensagem).strip()
    while not valor.isdigit():
        print("Digite apenas numeros.")
        valor = input(mensagem).strip()
    return valor


def opcao_nova_tarefa():
    titulo = input("Titulo: ")
    descricao = input("Descricao: ")
    usuario_id = pedir_numero("ID do usuario: ")
    criar_tarefa(titulo, descricao, usuario_id)


def opcao_editar_tarefa():
    tarefa_id = pedir_numero("ID da tarefa: ")
    titulo = input("Novo titulo (Enter pra manter o mesmo): ")
    descricao = input("Nova descricao (Enter pra manter a mesma): ")
    atualizar_tarefa(tarefa_id, titulo or None, descricao or None)


def opcao_concluir_tarefa():
    tarefa_id = pedir_numero("ID da tarefa: ")
    concluir_tarefa(tarefa_id)


def opcao_excluir_tarefa():
    tarefa_id = pedir_numero("ID da tarefa: ")
    deletar_tarefa(tarefa_id)


def opcao_novo_usuario():
    nome = input("Nome: ")
    email = input("Email: ")
    criar_usuario(nome, email)


def menu():
    opcoes = {
        "1": opcao_nova_tarefa,
        "2": listar_tarefas,
        "3": opcao_editar_tarefa,
        "4": opcao_concluir_tarefa,
        "5": opcao_excluir_tarefa,
        "6": opcao_novo_usuario,
        "7": listar_usuarios,
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