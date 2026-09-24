from tarefas import (
    criar_tarefa,
    listar_tarefas,
    atualizar_tarefa,
    concluir_tarefa,
    deletar_tarefa,
)




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

