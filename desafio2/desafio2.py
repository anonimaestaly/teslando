import os
import shutil

from colorama import init, Fore, Style

init(autoreset=True)


def pausar():
    input("\nENTER para voltar...")


def ls():
    print("\nQuer ver os arquivos ocultos também? (aqueles que começam com '.')")
    resposta = input("Mostrar ocultos? (s/n): ").strip().lower()
    mostrar_ocultos = resposta == "s"

    itens = os.listdir()

    if not mostrar_ocultos:
        itens = [item for item in itens if not item.startswith(".")]

    itens.sort()

    print("\nConteúdo da pasta:\n")

    if not itens:
        print(Fore.YELLOW + "Essa pasta está vazia.")
    else:
        for item in itens:
            if os.path.isdir(item):
                print(Fore.BLUE + "[PASTA]   " + item)
            else:
                print("[ARQUIVO] " + item)

    pausar()


def cat():
    entrada = input("\nNome do(s) arquivo(s), separados por espaço: ")
    nomes_dos_arquivos = entrada.split()

    if not nomes_dos_arquivos:
        print(Fore.YELLOW + "\nVocê não digitou nenhum arquivo.")
        pausar()
        return

    for nome in nomes_dos_arquivos:
        if len(nomes_dos_arquivos) > 1:
            print(Fore.CYAN + f"\n--- {nome} ---")

        try:
            with open(nome, "r", encoding="utf-8") as arquivo:
                print(arquivo.read())

        except FileNotFoundError:
            print(Fore.RED + f"Não encontrei o arquivo '{nome}'.")

        except IsADirectoryError:
            print(Fore.RED + f"'{nome}' é uma pasta, não um arquivo.")

        except PermissionError:
            print(Fore.RED + f"Sem permissão para abrir '{nome}'.")

        except UnicodeDecodeError:
            print(Fore.RED + f"'{nome}' parece ser um arquivo binário, não dá pra mostrar como texto.")

    pausar()


def echo():
    texto = input("\nDigite o texto: ")

    print("\n" + texto)

    pausar()


def tee():
    nome = input("\nNome do arquivo: ").strip()

    if not nome:
        print(Fore.YELLOW + "\nVocê precisa digitar um nome de arquivo.")
        pausar()
        return

    texto = input("Texto que vai ser salvo: ")

    print("\nO que você quer fazer com esse arquivo?")
    print("1 - Substituir tudo que já tinha nele")
    print("2 - Adicionar esse texto no final, sem apagar o resto")

    modo = input("Escolha (1 ou 2): ")

    if modo not in ("1", "2"):
        print(Fore.YELLOW + "\nOpção inválida, tente de novo.")
        pausar()
        return

    modo_de_abertura = "w" if modo == "1" else "a"

    try:
        with open(nome, modo_de_abertura, encoding="utf-8") as arquivo:
            arquivo.write(texto + "\n")

        print("\n" + texto)
        print(Fore.GREEN + "\nProntinho, arquivo salvo!")

    except IsADirectoryError:
        print(Fore.RED + f"\n'{nome}' é uma pasta, não dá pra escrever nela.")

    except PermissionError:
        print(Fore.RED + f"\nSem permissão para escrever em '{nome}'.")

    pausar()


def cp():
    origem = input("\nArquivo que deseja copiar: ").strip()
    destino = input("Nome da cópia: ").strip()

    if not origem or not destino:
        print(Fore.YELLOW + "\nDigite os dois nomes.")
        pausar()
        return

    try:
        shutil.copy(origem, destino)

        print(Fore.GREEN + "\nArquivo copiado com sucesso!")

    except FileNotFoundError:
        print(Fore.RED + f"\nNão encontrei '{origem}'.")

    except PermissionError:
        print(Fore.RED + "\nSem permissão para copiar o arquivo.")

    except IsADirectoryError:
        print(Fore.RED + "\nEsse comando está configurado para copiar arquivos.")

    pausar()


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_titulo():
    print(Fore.MAGENTA + Style.BRIGHT + "=== TERMINAL PYTHON ===")


def menu():
    while True:
        limpar_tela()

        mostrar_titulo()

        print("\nEscolha um comando:")
        print("1 - ls    (listar arquivos da pasta)")
        print("2 - cat   (mostrar conteúdo de um arquivo)")
        print("3 - echo  (repetir um texto)")
        print("4 - tee   (salvar um texto em um arquivo)")
        print("5 - cp    (copiar arquivo)")
        print("0 - sair")

        escolha = input(Fore.CYAN + "\nuser@python:~$ ")

        if escolha == "1":
            ls()

        elif escolha == "2":
            cat()

        elif escolha == "3":
            echo()

        elif escolha == "4":
            tee()

        elif escolha == "5":
            cp()

        elif escolha == "0":
            limpar_tela()

            print(Fore.GREEN + "Até mais! Programa encerrado.")

            break

        else:
            print(Fore.YELLOW + "\nOpção inválida, escolha um número do menu.")

            pausar()


if __name__ == "__main__":
    try:
        menu()

    except KeyboardInterrupt:
        print(Fore.GREEN + "\n\nAté mais! Programa encerrado.")