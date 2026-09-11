"""
Desafio 03 - Consumo de API e Envio de Arquivos por E-mail
=============================================================
Fluxo do script:
    1. Busca a lista de usuários na API (reqres.in)
    2. Salva essa lista em um arquivo (CSV, TXT ou JSON, à escolha)
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
def pedir_chave_da_api() -> str:
    """
    Pede a chave de API do reqres.in, necessária desde que a API
    passou a exigir autenticação. Gere a sua gratuitamente em
    https://app.reqres.in (cadastro simples, sem cartão).
    """
    print("\n--- A API reqres.in exige uma chave de acesso ---")
    print("Gere a sua gratuitamente em: https://app.reqres.in")
    return input("Cole aqui sua chave de API (x-api-key): ").strip()


def buscar_usuarios_na_api(chave_da_api: str, url_base: str = URL_DA_API) -> list[dict]:
    """
    Busca todos os usuários da API, percorrendo as páginas até acabar.
    Usa uma Session para reaproveitar a conexão entre as requisições,
    enviando a chave de API no cabeçalho "x-api-key" a cada pedido.
    """
    usuarios = []
    cabecalhos = {"x-api-key": chave_da_api}

    with requests.Session() as conexao:
        conexao.headers.update(cabecalhos)  # aplica o header em todas as requisições da sessão
        pagina = 1
        while True:
            resposta = conexao.get(url_base, params={"page": pagina}, timeout=10)

            if resposta.status_code == 403:
                raise ValueError(
                    "A API recusou o acesso (403). Verifique se a chave de API "
                    "está correta — gere uma nova em https://app.reqres.in se precisar."
                )
            resposta.raise_for_status()  # lança erro se a API responder com outra falha

            dados = resposta.json()
            usuarios.extend(dados.get("data", []))

            if pagina >= dados.get("total_pages", 1):
                break
            pagina += 1

    if not usuarios:
        raise ValueError("A API não devolveu nenhum usuário.")

    return usuarios


def analisar_dominios_de_email(usuarios: list[dict]) -> pd.Series:
    tabela = pd.DataFrame(usuarios)
    dominios = tabela["email"].str.split("@").str[1]
    return dominios.value_counts()


COLUNAS = ["id", "email", "first_name", "last_name", "avatar"]


def salvar_como_csv(usuarios: list[dict], nome_arquivo: str) -> None:
    tabela = pd.DataFrame(usuarios, columns=COLUNAS)
    tabela.to_csv(nome_arquivo, index=False, encoding="utf-8")


def salvar_como_txt(usuarios: list[dict], nome_arquivo: str) -> None:
    with open(nome_arquivo, mode="w", encoding="utf-8") as arquivo:
        for usuario in usuarios:
            arquivo.write(f"ID: {usuario.get('id', '')}\n")
            arquivo.write(f"Nome: {usuario.get('first_name', '')} {usuario.get('last_name', '')}\n")
            arquivo.write(f"E-mail: {usuario.get('email', '')}\n")
            arquivo.write(f"Avatar: {usuario.get('avatar', '')}\n")
            arquivo.write("-" * 40 + "\n")


def salvar_como_json(usuarios: list[dict], nome_arquivo: str) -> None:
    with open(nome_arquivo, mode="w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, ensure_ascii=False, indent=2)


FORMATOS_DISPONIVEIS = {
    "1": {"nome": "CSV", "extensao": "csv", "funcao": salvar_como_csv},
    "2": {"nome": "TXT", "extensao": "txt", "funcao": salvar_como_txt},
    "3": {"nome": "JSON", "extensao": "json", "funcao": salvar_como_json},
}


def perguntar_formato_arquivo() -> dict:
    print("\nEm qual formato você quer salvar o arquivo?")
    for tecla, formato in FORMATOS_DISPONIVEIS.items():
        print(f"  {tecla} - {formato['nome']}")

    escolha = input("Digite o número da opção: ").strip()
    while escolha not in FORMATOS_DISPONIVEIS:
        escolha = input("Opção inválida. Digite 1, 2 ou 3: ").strip()

    return FORMATOS_DISPONIVEIS[escolha]


def salvar_usuarios_em_arquivo(usuarios: list[dict], formato: dict, nome_base: str = NOME_BASE_DO_ARQUIVO) -> str:
    if not usuarios:
        raise ValueError("Não há usuários para salvar.")

    nome_arquivo = f"{nome_base}.{formato['extensao']}"
    formato["funcao"](usuarios, nome_arquivo)
    return nome_arquivo


def email_parece_valido(endereco: str) -> bool:
    if "@" not in endereco:
        return False
    return "." in endereco.split("@")[-1]


def pedir_email_valido(mensagem: str) -> str:
    endereco = input(mensagem).strip()
    while not email_parece_valido(endereco):
        print("   E-mail inválido (falta '@' ou '.'). Tente de novo.")
        endereco = input(mensagem).strip()
    return endereco


def perguntar_dados_do_email() -> tuple[str, str, str]:
    print("\n--- Dados para envio do e-mail ---")
    remetente = pedir_email_valido("Seu e-mail (remetente): ")
    senha = getpass.getpass("Senha de app do Google (não aparece ao digitar): ").strip()
    destinatario = pedir_email_valido("E-mail de destino: ")
    return remetente, senha, destinatario


def montar_corpo_html(usuarios: list[dict]) -> str:
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
    email = EmailMessage()
    email["From"] = email_remetente
    email["To"] = email_destinatario
    email["Subject"] = "Listagem de usuários - Desafio 03"

    email.set_content("Segue em anexo a listagem de usuários obtida via API.")
    email.add_alternative(montar_corpo_html(usuarios), subtype="html")

    # Cada extensão tem seu par correto de (maintype, subtype) MIME.
    # "text/json" não é um tipo registrado — JSON deve ir como "application/json".
    extensao = os.path.splitext(caminho_do_arquivo)[1].lstrip(".")
    tipos_mime_por_extensao = {
        "csv": ("text", "csv"),
        "txt": ("text", "plain"),
        "json": ("application", "json"),
    }
    maintype, subtype = tipos_mime_por_extensao.get(extensao, ("text", "plain"))

    with open(caminho_do_arquivo, "rb") as arquivo:
        email.add_attachment(
            arquivo.read(),
            maintype=maintype,
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


def main() -> None:
    try:
        chave_da_api = pedir_chave_da_api()

        print("Passo 1/3: buscando usuários na API...")
        usuarios = buscar_usuarios_na_api(chave_da_api)
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