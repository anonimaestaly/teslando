"""
Desafio 03 - Chamada de API e Envio de Arquivos por E-mail
=======================================================================

O que este script realiza:
1. Consulta a API do reqres.in para obter a lista de usuários.
2. Armazena essa lista em um arquivo (CSV, TXT ou JSON).
3. Envia esse arquivo por e-mail, anexado.

Organização do código
----------------------
O arquivo é dividido em duas camadas:

- CAMADA DE LÓGICA ("core"): funções puras ou quase-puras, que recebem
  parâmetros e devolvem resultados. NÃO chamam input()/print(). São
  essas que os testes automatizados (test_desafio03.py) exercitam.

- CAMADA DE INTERAÇÃO (CLI): funções que conversam com quem está
  rodando o script (perguntam coisas no terminal, mostram mensagens).
  Ficam isoladas para que a lógica de negócio possa ser testada e,
  no futuro, reaproveitada em outro contexto (ex: uma API web) sem
  arrastar código de terminal junto.

Modo de uso
-----------
Interativo (como antes, pergunta tudo no terminal):
    python desafio03.py

Não-interativo (para automação/CI/cron), via argumentos:
    python desafio03.py --formato csv \
        --remetente eu@gmail.com --destinatario voce@gmail.com

    A chave da API e a senha de app continuam vindo de variável de
    ambiente (REQRES_API_KEY / EMAIL_SENHA_APP) ou, na falta delas,
    o script pergunta interativamente mesmo em modo não-interativo
    (senha nunca é aceita como argumento de linha de comando, por
    segurança: apareceria no histórico do shell).
"""

from __future__ import annotations

import argparse
import getpass
import json
import logging
import os
import smtplib
from email.message import EmailMessage
from html import escape

import pandas as pd
import requests

logger = logging.getLogger("desafio03")


# ====================================================================
# Configurações gerais do script
# ====================================================================
URL_DA_API = "https://reqres.in/api/users"
NOME_BASE_DO_ARQUIVO = "usuarios"  # a extensão (.csv, .txt, .json) é adicionada depois

SERVIDOR_SMTP_GOOGLE = "smtp.gmail.com"
PORTA_SMTP_GOOGLE = 587
# Trava de segurança: caso a API não informe corretamente por algum motivo
# quando parar, isso impede que o script entre em um loop infinito.
MAXIMO_DE_PAGINAS = 50

COLUNAS = ["id", "email", "first_name", "last_name", "avatar"]

FORMATOS_DISPONIVEIS = {
    "csv": {"nome": "CSV", "extensao": "csv"},
    "txt": {"nome": "TXT", "extensao": "txt"},
    "json": {"nome": "JSON", "extensao": "json"},
}


# ====================================================================
# CAMADA DE LÓGICA (core) - sem input()/print(), 100% testável
# ====================================================================

# --- Etapa 1: buscar usuários -----------------------------------------
def buscar_usuarios_na_api(chave_da_api: str, url_base: str = URL_DA_API) -> list[dict]:
    """
    Vai página por página na API, juntando todos os usuários em uma
    única lista. Usa uma Session do requests, que reutiliza a conexão
    HTTP entre as chamadas — um pouco mais rápido que abrir conexão nova
    a cada página.
    """
    usuarios: list[dict] = []
    cabecalhos = {"x-api-key": chave_da_api}

    with requests.Session() as conexao:
        conexao.headers.update(cabecalhos)
        pagina = 1

        while pagina <= MAXIMO_DE_PAGINAS:
            resposta = conexao.get(url_base, params={"page": pagina}, timeout=10)

            if resposta.status_code == 403:
                # 403 aqui quase sempre é chave errada ou expirada
                raise ValueError(
                    "Acesso negado pela API (403). Confirme se a chave API "
                    "está correta — gere uma nova em https://app.reqres.in se precisar."
                )
            resposta.raise_for_status()

            dados = resposta.json()
            usuarios.extend(dados.get("data", []))

            if pagina >= dados.get("total_pages", 1):
                break
            pagina += 1
        else:
            raise ValueError(
                f"A busca ultrapassou o limite de {MAXIMO_DE_PAGINAS} páginas. "
                "Algo pode estar errado com a resposta da API."
            )

    if not usuarios:
        raise ValueError("A API não devolveu nenhum usuário.")

    return usuarios


def analisar_dominios_de_email(usuarios: list[dict]) -> pd.Series:
    """Quantos usuários existem por domínio de e-mail (gmail.com, yahoo.com etc)."""
    tabela = pd.DataFrame(usuarios)
    tabela = tabela.dropna(subset=["email"])
    dominios = tabela["email"].str.split("@").str[1]
    return dominios.value_counts()


# --- Etapa 2: salvar em arquivo ----------------------------------------
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


_FUNCAO_POR_EXTENSAO = {
    "csv": salvar_como_csv,
    "txt": salvar_como_txt,
    "json": salvar_como_json,
}


def salvar_usuarios_em_arquivo(
    usuarios: list[dict], formato_chave: str, nome_base: str = NOME_BASE_DO_ARQUIVO
) -> str:
    if not usuarios:
        raise ValueError("Não há usuários para salvar.")
    if formato_chave not in FORMATOS_DISPONIVEIS:
        raise ValueError(f"Formato desconhecido: {formato_chave!r}")

    extensao = FORMATOS_DISPONIVEIS[formato_chave]["extensao"]
    nome_arquivo = f"{nome_base}.{extensao}"
    _FUNCAO_POR_EXTENSAO[formato_chave](usuarios, nome_arquivo)
    return nome_arquivo


# --- Etapa 3: enviar por e-mail -----------------------------------------
def email_parece_valido(endereco: str) -> bool:
    # Validação simples, só pra pegar erros de digitação óbvios.
    if "@" not in endereco:
        return False
    return "." in endereco.split("@")[-1]


def montar_corpo_html(usuarios: list[dict]) -> str:
    """Monta uma tabela HTML simples com os usuários para o corpo do e-mail."""
    linhas = []
    for usuario in usuarios:
        id_usuario = escape(str(usuario.get("id", "")))
        nome_usuario = escape(f"{usuario.get('first_name', '')} {usuario.get('last_name', '')}")
        email_usuario = escape(str(usuario.get("email", "")))
        linhas.append(
            "<tr>"
            f'<td style="padding: 6px 12px; border: 1px solid #ddd;">{id_usuario}</td>'
            f'<td style="padding: 6px 12px; border: 1px solid #ddd;">{nome_usuario}</td>'
            f'<td style="padding: 6px 12px; border: 1px solid #ddd;">{email_usuario}</td>'
            "</tr>"
        )
    linhas_da_tabela = "".join(linhas)

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


# ====================================================================
# CAMADA DE INTERAÇÃO (CLI) - só aqui existem input()/print()
# ====================================================================
def obter_chave_da_api() -> str:
    chave = os.environ.get("REQRES_API_KEY")
    if chave:
        return chave.strip()

    print("\n--- A API reqres.in exige uma chave de acesso ---")
    print("Gere a sua gratuitamente em: https://app.reqres.in")
    print("(Dica: defina a variável de ambiente REQRES_API_KEY para não")
    print(" precisar colar isso toda vez que rodar o script.)")
    return input("Cole aqui sua chave de API (x-api-key): ").strip()


def perguntar_formato_arquivo() -> str:
    print("\nEm qual formato você quer salvar o arquivo?")
    opcoes = list(FORMATOS_DISPONIVEIS.items())
    for indice, (chave, formato) in enumerate(opcoes, start=1):
        print(f"  {indice} - {formato['nome']}")

    escolha = input("Digite o número da opção: ").strip()
    validas = {str(i) for i in range(1, len(opcoes) + 1)}
    while escolha not in validas:
        escolha = input(f"Opção inválida. Digite um número de 1 a {len(opcoes)}: ").strip()

    return opcoes[int(escolha) - 1][0]


def pedir_email_valido(mensagem: str) -> str:
    endereco = input(mensagem).strip()
    while not email_parece_valido(endereco):
        print("   E-mail inválido (falta '@' ou '.'). Tente de novo.")
        endereco = input(mensagem).strip()
    return endereco


def obter_dados_do_email(remetente_cli: str | None, destinatario_cli: str | None) -> tuple[str, str, str]:
    """
    Resolve remetente/senha/destinatário na seguinte ordem de prioridade:
    argumento de linha de comando > variável de ambiente > pergunta interativa.
    A senha NUNCA vem de argumento de linha de comando (ficaria exposta no
    histórico do shell) — só de variável de ambiente ou prompt escondido.
    """
    print("\n--- Dados para envio do e-mail ---")

    remetente = remetente_cli or os.environ.get("EMAIL_REMETENTE")
    if not remetente:
        remetente = pedir_email_valido("Seu e-mail (remetente): ")
    elif not email_parece_valido(remetente):
        raise ValueError(f"E-mail remetente inválido: {remetente!r}")

    senha = os.environ.get("EMAIL_SENHA_APP")
    if not senha:
        senha = getpass.getpass("Senha de app do Google (não aparece ao digitar): ").strip()

    destinatario = destinatario_cli
    if destinatario and not email_parece_valido(destinatario):
        raise ValueError(f"E-mail destinatário inválido: {destinatario!r}")
    if not destinatario:
        destinatario = pedir_email_valido("E-mail de destino: ")

    return remetente, senha, destinatario


# ====================================================================
# Orquestração
# ====================================================================
def configurar_logging(verboso: bool = False) -> None:
    nivel = logging.DEBUG if verboso else logging.INFO
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def montar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Busca usuários na API reqres.in, salva em arquivo e envia por e-mail."
    )
    parser.add_argument(
        "--formato",
        choices=sorted(FORMATOS_DISPONIVEIS.keys()),
        help="Formato do arquivo de saída. Sem isso, pergunta interativamente.",
    )
    parser.add_argument(
        "--remetente",
        help="E-mail remetente. Sem isso, usa EMAIL_REMETENTE ou pergunta interativamente.",
    )
    parser.add_argument(
        "--destinatario",
        help="E-mail destinatário. Sem isso, pergunta interativamente.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Ativa logs em nível DEBUG."
    )
    return parser


def main() -> None:
    args = montar_parser().parse_args()
    configurar_logging(args.verbose)

    try:
        chave_da_api = obter_chave_da_api()

        logger.info("Passo 1/3: buscando usuários na API...")
        usuarios = buscar_usuarios_na_api(chave_da_api)
        logger.info("%d usuários encontrados.", len(usuarios))

        contagem_por_dominio = analisar_dominios_de_email(usuarios)
        logger.debug("Usuários por domínio de e-mail:")
        for dominio, quantidade in contagem_por_dominio.items():
            logger.debug("  - %s: %d", dominio, quantidade)

        logger.info("Passo 2/3: salvando usuários em arquivo...")
        formato_chave = args.formato or perguntar_formato_arquivo()
        arquivo = salvar_usuarios_em_arquivo(usuarios, formato_chave)
        logger.info("Arquivo criado: %s", arquivo)

        logger.info("Passo 3/3: enviando o arquivo por e-mail...")
        remetente, senha, destinatario = obter_dados_do_email(args.remetente, args.destinatario)
        enviar_arquivo_por_email(arquivo, remetente, senha, destinatario, usuarios)
        logger.info("E-mail enviado com sucesso!")

    except requests.exceptions.RequestException:
        logger.error("Falha ao conectar com a API. Verifique sua internet e tente de novo.")
    except ValueError as erro:
        logger.error(str(erro))
    except Exception:
        logger.exception("Erro inesperado durante a execução.")


if __name__ == "__main__":
    main()