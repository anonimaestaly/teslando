"""Interface de linha de comando para o CRUD de tarefas."""

from crud import (
    inicializar_banco,
    criar_tarefa,
    listar_tarefas,
    buscar_tarefa_por_id,
    atualizar_tarefa,
    concluir_tarefa,
    deletar_tarefa,
)

MENU = """
=== Gestão de Tarefas ===
1 - Criar tarefa
2 - Listar tarefas
3 - Buscar tarefa por id
4 - Atualizar tarefa
5 - Concluir tarefa
6 - Deletar tarefa
0 - Sair
"""

USUARIO_ID = 1  # aplicação de usuário único por enquanto


def _print_tarefa(t):
    print(
        f"  [{t['id']}] {t['titulo']} — {t['status']}"
        f" | criada em: {t['data_criacao']}"
        f" | concluída em: {t['data_conclusao']}"
    )


def _print_tarefas(tarefas):
    if not tarefas:
        print("  nenhuma tarefa encontrada")
        return
    for t in tarefas:
        _print_tarefa(t)


def _pedir_id():
    bruto = input("id da tarefa: ").strip()
    if not bruto.isdigit():
        print("id inválido, precisa ser um número.")
        return None
    return int(bruto)


def acao_criar():
    titulo = input("título: ").strip()
    if not titulo:
        print("título é obrigatório, operação cancelada.")
        return
    descricao = input("descrição (opcional): ").strip() or None
    tarefa_id = criar_tarefa(titulo, descricao, USUARIO_ID)
    print(f"tarefa criada com id {tarefa_id}.")


def acao_listar():
    _print_tarefas(listar_tarefas(USUARIO_ID))


def acao_buscar():
    tarefa_id = _pedir_id()
    if tarefa_id is None:
        return
    tarefa = buscar_tarefa_por_id(tarefa_id)
    if tarefa is None:
        print("tarefa não encontrada.")
        return
    _print_tarefa(tarefa)


def acao_atualizar():
    tarefa_id = _pedir_id()
    if tarefa_id is None:
        return
    if buscar_tarefa_por_id(tarefa_id) is None:
        print("tarefa não encontrada.")
        return

    print("deixe em branco pra manter o valor atual.")
    titulo = input("novo título: ").strip() or None
    descricao = input("nova descrição: ").strip() or None
    status = input("novo status (pendente/em_andamento/concluida): ").strip() or None

    if status is not None and status not in ("pendente", "em_andamento", "concluida"):
        print("status inválido, operação cancelada.")
        return

    atualizar_tarefa(tarefa_id, titulo=titulo, descricao=descricao, status=status)
    print("tarefa atualizada.")


def acao_concluir():
    tarefa_id = _pedir_id()
    if tarefa_id is None:
        return
    if concluir_tarefa(tarefa_id):
        print("tarefa marcada como concluída.")
    else:
        print("tarefa não encontrada.")


def acao_deletar():
    tarefa_id = _pedir_id()
    if tarefa_id is None:
        return
    confirmacao = input(f"tem certeza que quer deletar a tarefa {tarefa_id}? (s/N): ").strip().lower()
    if confirmacao != "s":
        print("operação cancelada.")
        return
    if deletar_tarefa(tarefa_id):
        print("tarefa deletada.")
    else:
        print("tarefa não encontrada.")


ACOES = {
    "1": acao_criar,
    "2": acao_listar,
    "3": acao_buscar,
    "4": acao_atualizar,
    "5": acao_concluir,
    "6": acao_deletar,
}


def main():
    inicializar_banco()
    while True:
        print(MENU)
        opcao = input("escolha uma opção: ").strip()
        if opcao == "0":
            print("até mais!")
            break
        acao = ACOES.get(opcao)
        if acao is None:
            print("opção inválida, tente de novo.")
            continue
        acao()


if __name__ == "__main__":
    main()