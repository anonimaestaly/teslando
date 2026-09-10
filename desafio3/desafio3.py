"""
Desafio 03 - Consumo de API e Envio de Arquivos por E-mail
=============================================================
Fluxo do script:
    1. Busca a lista de usuários na API (reqres.in)
    2. Salva essa lista em um arquivo CSV
    3. Envia o arquivo por e-mail, como anexo

Cada etapa está isolada em uma função própria, e a main() é quem
chama todas elas, na ordem certa.
"""

import os
import json
import smtplib
import getpass
from email.message import EmailMessage

import requests
import pandas as pd


# ------------------------------------------------------------------
# Configurações gerais
# ------------------------------------------------------------------
URL_DA_API = "https://reqres.in/api/users"
NOME_BASE_DO_ARQUIVO = "usuarios"  # sem extensão — ela é definida pelo formato escolhido

SERVIDOR_SMTP_GOOGLE = "smtp.gmail.com"
PORTA_SMTP_GOOGLE = 587


# ====================================================================
# 1. Buscar usuários na API
# ====================================================================
def buscar_usuarios_na_api(url_base: str = URL_DA_API) -> list[dict]:
    """
    Busca todos os usuários da API, percorrendo as páginas até acabar.
    Usa uma Session para reaproveitar a conexão entre as requisições.
    """
    usuarios = []

    with requests.Session() as conexao:
        pagina = 1
        while True:
            resposta = conexao.get(url_base, params={"page": pagina}, timeout=10)
            resposta.raise_for_status()  # lança erro se a API responder com falha

            dados = resposta.json()
            usuarios.extend(dados.get("data", []))

            if pagina >= dados.get("total_pages", 1):
                break
            pagina += 1

    if not usuarios:
        raise ValueError("A API não devolveu nenhum usuário.")

    return usuarios


# ====================================================================
# 1.1 Analisar os usuários com pandas (exemplo prático - Desafio 03.1)
# ====================================================================
def analisar_dominios_de_email(usuarios: list[dict]) -> pd.Series:
    """
    Conta quantos usuários existem por domínio de e-mail (a parte
    depois do "@"), usando pandas.

    Por que isso demonstra bem o pacote:
    - str.split("@").str[1] é uma operação VETORIZADA: o pandas
      aplica a divisão em TODA a coluna de uma vez (usando o array
      NumPy por trás do bloco daquela coluna), em vez de percorrer
      usuário por usuário com um for. É justamente esse
      processamento "em bloco, por coluna" que o BlockManager
      viabiliza por trás dos panos.
    - value_counts() agrupa e conta as ocorrências de cada domínio,
      sem precisarmos escrever a lógica de contagem manualmente.
    """
    tabela = pd.DataFrame(usuarios)
    dominios = tabela["email"].str.split("@").str[1]
    return dominios.value_counts()


# ====================================================================
# 2. Salvar usuários em arquivo (CSV, TXT ou JSON)
# ====================================================================
COLUNAS = ["id", "email", "first_name", "last_name", "avatar"]


def salvar_como_csv(usuarios: list[dict], nome_arquivo: str) -> None:
    """
    Salva a lista de usuários em formato CSV usando pandas.

    pd.DataFrame(usuarios) transforma a lista de dicionários direto
    numa tabela (uma linha por usuário, uma coluna por chave do
    dicionário). df.to_csv() já cuida de escrever o cabeçalho e
    tratar acentuação, sem precisar do módulo csv manualmente.
    """
    tabela = pd.DataFrame(usuarios, columns=COLUNAS)
    tabela.to_csv(nome_arquivo, index=False, encoding="utf-8")


def salvar_como_txt(usuarios: list[dict], nome_arquivo: str) -> None:
    """Salva a lista de usuários em um arquivo de texto simples, um usuário por bloco."""
    with open(nome_arquivo, mode="w", encoding="utf-8") as arquivo:
        for usuario in usuarios:
            arquivo.write(f"ID: {usuario.get('id', '')}\n")
            arquivo.write(f"Nome: {usuario.get('first_name', '')} {usuario.get('last_name', '')}\n")
            arquivo.write(f"E-mail: {usuario.get('email', '')}\n")
            arquivo.write(f"Avatar: {usuario.get('avatar', '')}\n")
            arquivo.write("-" * 40 + "\n")


def salvar_como_json(usuarios: list[dict], nome_arquivo: str) -> None:
    """Salva a lista de usuários em formato JSON, preservando a estrutura original."""
    with open(nome_arquivo, mode="w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, ensure_ascii=False, indent=2)


# Mapeia cada formato ao nome da extensão e à função que sabe escrever nele.
# Assim, adicionar um novo formato no futuro é só acrescentar uma linha aqui.
FORMATOS_DISPONIVEIS = {
    "1": {"nome": "CSV", "extensao": "csv", "funcao": salvar_como_csv},
    "2": {"nome": "TXT", "extensao": "txt", "funcao": salvar_como_txt},
    "3": {"nome": "JSON", "extensao": "json", "funcao": salvar_como_json},
}


def perguntar_formato_arquivo() -> dict:
    """Pergunta ao usuário em qual formato ele quer salvar o arquivo."""
    print("\nEm qual formato você quer salvar o arquivo?")
    for tecla, formato in FORMATOS_DISPONIVEIS.items():
        print(f"  {tecla} - {formato['nome']}")

    escolha = input("Digite o número da opção: ").strip()
    while escolha not in FORMATOS_DISPONIVEIS:
        escolha = input("Opção inválida. Digite 1, 2 ou 3: ").strip()

    return FORMATOS_DISPONIVEIS[escolha]


def salvar_usuarios_em_arquivo(usuarios: list[dict], formato: dict, nome_base: str = NOME_BASE_DO_ARQUIVO) -> str:
    """
    Salva a lista de usuários no formato escolhido e retorna o nome
    do arquivo gerado (com a extensão correta).
    """
    if not usuarios:
        raise ValueError("Não há usuários para salvar.")

    nome_arquivo = f"{nome_base}.{formato['extensao']}"
    formato["funcao"](usuarios, nome_arquivo)
    return nome_arquivo


# ====================================================================
# 3. Coletar dados de e-mail do usuário
# ====================================================================
def email_parece_valido(endereco: str) -> bool:
    """Checagem simples: precisa ter '@' e um '.' depois dele."""
    if "@" not in endereco:
        return False
    return "." in endereco.split("@")[-1]


def pedir_email_valido(mensagem: str) -> str:
    """Pergunta um e-mail e insiste até a pessoa digitar um formato válido."""
    endereco = input(mensagem).strip()
    while not email_parece_valido(endereco):
        print("   E-mail inválido (falta '@' ou '.'). Tente de novo.")
        endereco = input(mensagem).strip()
    return endereco


def perguntar_dados_do_email() -> tuple[str, str, str]:
    """
    Coleta, em tempo de execução, os dados necessários para enviar o
    e-mail. A senha é digitada com getpass (não aparece na tela) e
    nunca fica salva em nenhum lugar do código.
    """
    print("\n--- Dados para envio do e-mail ---")
    remetente = pedir_email_valido("Seu e-mail (remetente): ")
    senha = getpass.getpass("Senha de app do Google (não aparece ao digitar): ").strip()
    destinatario = pedir_email_valido("E-mail de destino: ")
    return remetente, senha, destinatario


# ====================================================================
# 4. Enviar o arquivo por e-mail
# ====================================================================
def montar_corpo_html(usuarios: list[dict]) -> str:
    """
    Monta uma tabela HTML simples com os usuários, para deixar o
    corpo do e-mail mais visual do que um texto plano.
    """
    linhas_da_tabela = ""
    for usuario in usuarios:
        linhas_da_tabela += f"""
            <tr>
                <td style="padding: 6px 12px; border: 1px solid #ddd;">{usuario.get('id', '')}</td>
                <td style="padding: 6px 12px; border: 1px solid #ddd;">{usuario.get('first_name', '')} {usuario.get('last_name', '')}</td>
                <td style="padding: 6px 12px; border: 1px solid #ddd;">{usuario.get('email', '')}</td>
            </tr>"""

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Listagem de usuários - Desafio 03</h2>
        <p>Segue em anexo o arquivo com a listagem completa. Resumo abaixo:</p>
        <p><b>Total de usuários encontrados:</b> {len(usuarios)}</p>
        <table style="border-collapse: collapse; margin-top: 10px;">
          <tr style="background-color: #f0f0f0;">
            <th style="padding: 6px 12px; border: 1px solid #ddd;">ID</th>
            <th style="padding: 6px 12px; border: 1px solid #ddd;">Nome</th>
            <th style="padding: 6px 12px; border: 1px solid #ddd;">E-mail</th>
          </tr>
          {linhas_da_tabela}
        </table>
      </body>
    </html>
    """


def enviar_arquivo_por_email(
    caminho_do_arquivo: str,
    email_remetente: str,
    senha_remetente: str,
    email_destinatario: str,
    usuarios: list[dict],
) -> None:
    """Monta o e-mail (com corpo em HTML) com o arquivo em anexo e envia via SMTP do Gmail."""
    email = EmailMessage()
    email["From"] = email_remetente
    email["To"] = email_destinatario
    email["Subject"] = "Listagem de usuários - Desafio 03"

    # set_content() define a versão em texto simples (fallback, caso o
    # cliente de e-mail não consiga exibir HTML). add_alternative()
    # adiciona a versão em HTML, que é a que a maioria dos clientes mostra.
    email.set_content("Segue em anexo a listagem de usuários obtida via API.")
    email.add_alternative(montar_corpo_html(usuarios), subtype="html")

    # O subtype do anexo (csv/plain/json) é definido pela extensão do
    # arquivo, para que ele apareça com o tipo certo no anexo.
    extensao = os.path.splitext(caminho_do_arquivo)[1].lstrip(".")
    subtype_por_extensao = {"csv": "csv", "txt": "plain", "json": "json"}
    subtype = subtype_por_extensao.get(extensao, "plain")

    with open(caminho_do_arquivo, "rb") as arquivo:
        email.add_attachment(
            arquivo.read(),
            maintype="text",
            subtype=subtype,
            filename=os.path.basename(caminho_do_arquivo),
        )

    try:
        with smtplib.SMTP(SERVIDOR_SMTP_GOOGLE, PORTA_SMTP_GOOGLE) as servidor:
            servidor.starttls()
            servidor.login(email_remetente, senha_remetente)
            servidor.send_message(email)

    except smtplib.SMTPAuthenticationError:
        raise ValueError(
            "Login recusado pelo Gmail. Verifique se o e-mail está certo e se "
            "você usou a SENHA DE APP (16 letras), não a senha normal da conta."
        )
    except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected):
        raise ValueError("Não foi possível conectar ao servidor do Gmail. Verifique sua internet.")
    except smtplib.SMTPException as erro:
        raise ValueError(f"Erro ao enviar o e-mail: {erro}")


# ====================================================================
# Orquestração
# ====================================================================
def main() -> None:
    try:
        print("Passo 1/3: buscando usuários na API...")
        usuarios = buscar_usuarios_na_api()
        print(f"   -> {len(usuarios)} usuários encontrados.")

        print("   Análise rápida com pandas (usuários por domínio de e-mail):")
        contagem_por_dominio = analisar_dominios_de_email(usuarios)
        for dominio, quantidade in contagem_por_dominio.items():
            print(f"     - {dominio}: {quantidade}")

        print("Passo 2/3: salvando usuários em arquivo...")
        formato = perguntar_formato_arquivo()
        arquivo = salvar_usuarios_em_arquivo(usuarios, formato)
        print(f"   -> Arquivo criado: {arquivo}")

        print("Passo 3/3: enviando o arquivo por e-mail...")
        remetente, senha, destinatario = perguntar_dados_do_email()
        enviar_arquivo_por_email(arquivo, remetente, senha, destinatario, usuarios)
        print("   -> E-mail enviado com sucesso!")

    except requests.exceptions.RequestException:
        print("\n[ERRO] Falha ao conectar com a API. Verifique sua internet e tente de novo.")
    except ValueError as erro:
        print(f"\n[ERRO] {erro}")
    except Exception as erro:
        print(f"\n[ERRO INESPERADO] {erro}")


if __name__ == "__main__":
    main()