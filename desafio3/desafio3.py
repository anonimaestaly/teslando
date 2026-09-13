""" 
Desafio 03 - Chamada de API e Envio de Arquivos por E-mail 
======================================================================= 

Em resumo, o que este script realiza:
1. Consulte a API do reqres.in para obter a lista de usuários.
2.  Armazena essa lista em um arquivo (você decide: CSV, TXT ou JSON) 
3. Envie esse arquivo por e-mail, anexado.

Código organizado: 
As funções de cada uma dessas 3 etapas são bem distintas, com suas atribuições separadas.
No final, a função main() apenas atua como uma "chefe": ela chama tudo na ordem 
certa e zela para que os erros não apareçam pelo caminho. 
"""

import os
import json
import smtplib
import getpass
from html import escape
from email.message import EmailMessage

import requests
import pandas as pd


# ------------------------------------------------------------------
# Configurações gerais do script
# ------------------------------------------------------------------
URL_DA_API = "https://reqres.in/api/users"
NOME_BASE_DO_ARQUIVO = "usuarios"  # a extensão (.csv, .txt, .json) é adicionada depois

SERVIDOR_SMTP_GOOGLE = "smtp.gmail.com"
PORTA_SMTP_GOOGLE = 587
# Trava de segurança: caso a API não informe corretamente por algum motivo 
# quando parar, isso impede que o script entre em um loop infinito.
MAXIMO_DE_PAGINAS = 50


# ====================================================================
# ETAPA 1 - Buscar os usuários na API
# ====================================================================
def obter_chave_da_api() -> str:
    """
    A API do reqres.in passou a exigir uma chave de acesso. Aqui a gente
    dá um jeitinho de facilitar a vida: se a chave já estiver salva na
    variável de ambiente REQRES_API_KEY, usamos ela direto. Senão,
    pedimos pro usuário colar a chave na hora.

    (Quem ainda não tem chave, pode gerar de graça em app.reqres.in)
    """
    chave = os.environ.get("REQRES_API_KEY")
    if chave:
        return chave.strip()

    print("\n--- A API reqres.in exige uma chave de acesso ---")
    print("Gere a sua gratuitamente em: https://app.reqres.in")
    print("(Dica: se definir a variável de ambiente REQRES_API_KEY,")
    print(" não precisa colar isso toda vez que rodar o script.)")
    return input("Cole aqui sua chave de API (x-api-key): ").strip()


def buscar_usuarios_na_api(chave_da_api: str, url_base: str = URL_DA_API) -> list[dict]:
    """
    Vai página por página na API, juntando todos os usuários em uma única lista.
      Usamos uma Session do requests, pois ela reutiliza a conexão HTTP entre as 
      chamadas.Isso torna tudo um pouco mais rápido.
    """
    usuarios = []
    cabecalhos = {"x-api-key": chave_da_api}

    with requests.Session() as conexao:
        conexao.headers.update(cabecalhos)  # esse header vale pra toda a sessão, não precisa repetir
        pagina = 1

        while pagina <= MAXIMO_DE_PAGINAS:
            resposta = conexao.get(url_base, params={"page": pagina}, timeout=10)

            if resposta.status_code == 403:
                # 403 aqui quase sempre é chave errada ou expirada
                raise ValueError(

                   "Acesso negado pela API (403).  Confirme se a chave API " 
"está correta — gere uma nova em https://app.reqres.in se precisar."
                )
            resposta.raise_for_status()  # qualquer outro erro HTTP, estoura aqui mesmo

            dados = resposta.json()
            usuarios.extend(dados.get("data", []))

            # Se já chegamos na última página, para o loop
            if pagina >= dados.get("total_pages", 1):
                break
            pagina += 1
        else:
            # Só cai aqui se o while terminar por ter estourado MAXIMO_DE_PAGINAS,
            # sem nunca ter dado o "break" — sinal de que algo não está normal
            raise ValueError(
                f"A busca ultrapassou o limite de {MAXIMO_DE_PAGINAS} páginas. "
                "Algo pode estar errado com a resposta da API."
            )

    if not usuarios:
        raise ValueError("A API não devolveu nenhum usuário.")

    return usuarios


def analisar_dominios_de_email(usuarios: list[dict]) -> pd.Series:
    """
    Só uma curiosidade rápida usando pandas: quantos usuários existem
    por domínio de e-mail (gmail.com, yahoo.com, etc).
    """
    tabela = pd.DataFrame(usuarios)

    # Se algum usuário vier sem e-mail, melhor descartar essa linha
    # aqui do que deixar isso bagunçar a contagem lá na frente
    tabela = tabela.dropna(subset=["email"])

    dominios = tabela["email"].str.split("@").str[1]
    return dominios.value_counts()


# ====================================================================
# ETAPA 2 - Salvar os usuários em arquivo
# ====================================================================
COLUNAS = ["id", "email", "first_name", "last_name", "avatar"]


def salvar_como_csv(usuarios: list[dict], nome_arquivo: str) -> None:
    tabela = pd.DataFrame(usuarios, columns=COLUNAS)
    tabela.to_csv(nome_arquivo, index=False, encoding="utf-8")


def salvar_como_txt(usuarios: list[dict], nome_arquivo: str) -> None:
    # Aqui optei por um formato bem legível, tipo "ficha" de cada usuário,
    # já que TXT não tem estrutura de tabela como o CSV
    with open(nome_arquivo, mode="w", encoding="utf-8") as arquivo:
        for usuario in usuarios:
            arquivo.write(f"ID: {usuario.get('id', '')}\n")
            arquivo.write(f"Nome: {usuario.get('first_name', '')} {usuario.get('last_name', '')}\n")
            arquivo.write(f"E-mail: {usuario.get('email', '')}\n")
            arquivo.write(f"Avatar: {usuario.get('avatar', '')}\n")
            arquivo.write("-" * 40 + "\n")


def salvar_como_json(usuarios: list[dict], nome_arquivo: str) -> None:
    # indent=2 só pra deixar o arquivo legível se alguém for abrir manualmente
    with open(nome_arquivo, mode="w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, ensure_ascii=False, indent=2)


# Esse dicionário funciona como um "menu": cada opção sabe seu nome,
# sua extensão de arquivo e qual função deve chamar para salvar.
# Assim a gente evita um monte de if/elif espalhado pelo código.
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
    formato["funcao"](usuarios, nome_arquivo)  # chama a função certa de acordo com o formato escolhido
    return nome_arquivo


# ====================================================================
# ETAPA 3 - Enviar o arquivo por e-mail
# ====================================================================
def email_parece_valido(endereco: str) -> bool:
    # Validação bem simples, só pra pegar os erros de digitação mais óbvios
    # (não é uma validação de e-mail "de verdade", mas resolve aqui)
    if "@" not in endereco:
        return False
    return "." in endereco.split("@")[-1]


def pedir_email_valido(mensagem: str) -> str:
    endereco = input(mensagem).strip()
    while not email_parece_valido(endereco):
        print("   E-mail inválido (falta '@' ou '.'). Tente de novo.")
        endereco = input(mensagem).strip()
    return endereco


def obter_dados_do_email() -> tuple[str, str, str]:
    """
    Assim como fizemos com a chave da API, aqui também damos a opção de
    usar variáveis de ambiente (EMAIL_REMETENTE e EMAIL_SENHA_APP) pra
    evitar digitar tudo de novo a cada execução. O que não estiver
    definido, a gente pergunta na hora mesmo.
    """
    print("\n--- Dados para envio do e-mail ---")

    remetente = os.environ.get("EMAIL_REMETENTE")
    if not remetente:
        remetente = pedir_email_valido("Seu e-mail (remetente): ")

    senha = os.environ.get("EMAIL_SENHA_APP")
    if not senha:
        # getpass esconde o que está sendo digitado, então a senha não
        # fica visível na tela nem no histórico do terminal
        senha = getpass.getpass("Senha de app do Google (não aparece ao digitar): ").strip()

    destinatario = pedir_email_valido("E-mail de destino: ")
    return remetente, senha, destinatario


def montar_corpo_html(usuarios: list[dict]) -> str:
    """
    Monta uma tabelinha HTML simples com os usuários, pra deixar o
    corpo do e-mail mais apresentável do que só texto puro.
    """
    linhas_da_tabela = ""
    for usuario in usuarios:
        # escape() protege contra usuários com "<", ">" ou "&" no nome/e-mail,
        # que senão bagunçariam a estrutura do HTML
        id_usuario = escape(str(usuario.get("id", "")))
        nome_usuario = escape(f"{usuario.get('first_name', '')} {usuario.get('last_name', '')}")
        email_usuario = escape(str(usuario.get("email", "")))

        linhas_da_tabela += f"""
            <tr>
                <td style="padding: 6px 12px; border: 1px solid #ddd;">{id_usuario}</td>
                <td style="padding: 6px 12px; border: 1px solid #ddd;">{nome_usuario}</td>
                <td style="padding: 6px 12px; border: 1px solid #ddd;">{email_usuario}</td>
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

    # Enviamos as duas versões: texto simples (fallback) e HTML (a "bonita")
    email.set_content("Segue em anexo a listagem de usuários obtida via API.")
    email.add_alternative(montar_corpo_html(usuarios), subtype="html")

    # Cada tipo de arquivo tem seu par (maintype, subtype) certinho no
    # padrão MIME. Vale lembrar: "text/json" não existe oficialmente,
    # o correto pra JSON é "application/json".
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
            servidor.starttls()  # criptografa a conexão antes de mandar login/senha
            servidor.login(email_remetente, senha_remetente)
            servidor.send_message(email)

    except smtplib.SMTPAuthenticationError:
        # Esse é, de longe, o erro mais comum: confundir a senha normal
        # da conta Google com a senha de app (que tem 16 letras)
        raise ValueError(
            "Login recusado pelo Gmail. Verifique se o e-mail está certo e se "
            "você usou a SENHA DE APP (16 letras), não a senha normal da conta."
        )
    except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected):
        raise ValueError("Não foi possível conectar ao servidor do Gmail. Verifique sua internet.")
    except smtplib.SMTPException as erro:
        raise ValueError(f"Erro ao enviar o e-mail: {erro}")


# ====================================================================
# Funçõezinhas de log — só pra deixar o main() mais limpo de ler
# ====================================================================
def log_passo(numero: str, mensagem: str) -> None:
    print(f"Passo {numero}: {mensagem}")


def log_info(mensagem: str) -> None:
    print(f"   -> {mensagem}")


# ====================================================================
# main() - aqui é onde tudo se junta
# ====================================================================
def main() -> None:
    try:
        chave_da_api = obter_chave_da_api()

        log_passo("1/3", "buscando usuários na API...")
        usuarios = buscar_usuarios_na_api(chave_da_api)
        log_info(f"{len(usuarios)} usuários encontrados.")

        # Só uma análise extra, de bônus, pra mostrar o pandas em ação
        print("   Análise rápida com pandas (usuários por domínio de e-mail):")
        contagem_por_dominio = analisar_dominios_de_email(usuarios)
        for dominio, quantidade in contagem_por_dominio.items():
            print(f"     - {dominio}: {quantidade}")

        log_passo("2/3", "salvando usuários em arquivo...")
        formato = perguntar_formato_arquivo()
        arquivo = salvar_usuarios_em_arquivo(usuarios, formato)
        log_info(f"Arquivo criado: {arquivo}")

        log_passo("3/3", "enviando o arquivo por e-mail...")
        remetente, senha, destinatario = obter_dados_do_email()
        enviar_arquivo_por_email(arquivo, remetente, senha, destinatario, usuarios)
        log_info("E-mail enviado com sucesso!")

   # Cada tipo de erro exibe uma mensagem específica para auxiliar o usuário 
# a compreender precisamente o que ocorreu de errado (e não apenas um traceback bruto)
    except requests.exceptions.RequestException:
        print("\n[ERRO] Falha ao conectar com a API. Verifique sua internet e tente de novo.")
    except ValueError as erro:
        print(f"\n[ERRO] {erro}")
    except Exception as erro:
        print(f"\n[ERRO INESPERADO] {erro}")


if __name__ == "__main__":
    main()