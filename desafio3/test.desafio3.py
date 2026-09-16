"""
Testes da camada de lógica de desafio03.py.

Só testamos funções que NÃO chamam input()/print() — é exatamente por
isso que elas foram separadas da camada de CLI: dá pra testar sem
precisar simular teclado nem rede de verdade (a chamada de API é
mockada com unittest.mock).

Para rodar:
    pip install -r requirements.txt
    pytest -v
"""

from unittest.mock import patch, MagicMock

import pytest

import desafio03 as d

USUARIOS_EXEMPLO = [
    {"id": 1, "email": "george.bluth@reqres.in", "first_name": "George", "last_name": "Bluth", "avatar": ""},
    {"id": 2, "email": "janet.weaver@reqres.in", "first_name": "Janet", "last_name": "Weaver", "avatar": ""},
    {"id": 3, "email": "alguem@gmail.com", "first_name": "Alguem", "last_name": "X", "avatar": ""},
]


# ------------------------------------------------------------------
# email_parece_valido
# ------------------------------------------------------------------
@pytest.mark.parametrize(
    "endereco, esperado",
    [
        ("nome@dominio.com", True),
        ("nome@dominio.co.uk", True),
        ("sem-arroba.com", False),
        ("nome@semponto", False),
        ("", False),
    ],
)
def test_email_parece_valido(endereco, esperado):
    assert d.email_parece_valido(endereco) is esperado


# ------------------------------------------------------------------
# analisar_dominios_de_email
# ------------------------------------------------------------------
def test_analisar_dominios_de_email_conta_corretamente():
    contagem = d.analisar_dominios_de_email(USUARIOS_EXEMPLO)
    assert contagem["reqres.in"] == 2
    assert contagem["gmail.com"] == 1


def test_analisar_dominios_de_email_ignora_usuarios_sem_email():
    usuarios = USUARIOS_EXEMPLO + [{"id": 4, "first_name": "SemEmail", "last_name": ""}]
    contagem = d.analisar_dominios_de_email(usuarios)
    assert contagem.sum() == 3  # o usuário sem e-mail não deve ser contado


# ------------------------------------------------------------------
# montar_corpo_html
# ------------------------------------------------------------------
def test_montar_corpo_html_inclui_total_e_escapa_html():
    usuarios = [{"id": 1, "email": "x@x.com", "first_name": "<script>", "last_name": "Bad"}]
    html = d.montar_corpo_html(usuarios)
    assert "Total de usuários encontrados:</b> 1" in html
    assert "<script>" not in html  # precisa ter sido escapado
    assert "&lt;script&gt;" in html


# ------------------------------------------------------------------
# salvar_usuarios_em_arquivo (CSV / TXT / JSON)
# ------------------------------------------------------------------
def test_salvar_como_csv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    nome = d.salvar_usuarios_em_arquivo(USUARIOS_EXEMPLO, "csv", nome_base="teste")
    conteudo = (tmp_path / nome).read_text(encoding="utf-8")
    assert "george.bluth@reqres.in" in conteudo
    assert nome == "teste.csv"


def test_salvar_como_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    nome = d.salvar_usuarios_em_arquivo(USUARIOS_EXEMPLO, "json", nome_base="teste")
    conteudo = (tmp_path / nome).read_text(encoding="utf-8")
    assert "janet.weaver@reqres.in" in conteudo


def test_salvar_usuarios_em_arquivo_sem_usuarios_da_erro(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError):
        d.salvar_usuarios_em_arquivo([], "csv")


def test_salvar_usuarios_em_arquivo_formato_invalido_da_erro(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError):
        d.salvar_usuarios_em_arquivo(USUARIOS_EXEMPLO, "xml")


# ------------------------------------------------------------------
# buscar_usuarios_na_api (rede mockada, sem chamar a internet de verdade)
# ------------------------------------------------------------------
def _resposta_falsa(pagina_atual, total_paginas, usuarios_da_pagina):
    resposta = MagicMock()
    resposta.status_code = 200
    resposta.json.return_value = {"data": usuarios_da_pagina, "total_pages": total_paginas}
    resposta.raise_for_status.return_value = None
    return resposta


def test_buscar_usuarios_na_api_junta_todas_as_paginas():
    respostas = [
        _resposta_falsa(1, 2, [USUARIOS_EXEMPLO[0]]),
        _resposta_falsa(2, 2, [USUARIOS_EXEMPLO[1]]),
    ]
    with patch("requests.Session.get", side_effect=respostas):
        usuarios = d.buscar_usuarios_na_api("chave-falsa")
    assert len(usuarios) == 2


def test_buscar_usuarios_na_api_403_da_erro_claro():
    resposta = MagicMock()
    resposta.status_code = 403
    with patch("requests.Session.get", return_value=resposta):
        with pytest.raises(ValueError, match="Acesso negado"):
            d.buscar_usuarios_na_api("chave-errada")


def test_buscar_usuarios_na_api_vazia_da_erro():
    resposta = _resposta_falsa(1, 1, [])
    with patch("requests.Session.get", return_value=resposta):
        with pytest.raises(ValueError, match="não devolveu nenhum usuário"):
            d.buscar_usuarios_na_api("chave-falsa")