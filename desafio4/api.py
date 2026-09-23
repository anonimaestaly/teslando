"""
API REST - Gestão de Tarefas (MySQL)

Dependências:
    pip install flask mysql-connector-python

Executar:
    python api.py
    (por padrão sobe em http://localhost:5000)
"""

from flask import Flask, jsonify, request
from mysql.connector import Error

import crud

app = Flask(__name__)


def erro(mensagem: str, codigo: int = 400):
    return jsonify({"erro": mensagem}), codigo


# ---------------------------------------------------------------------------
# USUÁRIOS
# ---------------------------------------------------------------------------

@app.route("/usuarios", methods=["POST"])
def criar_usuario():
    dados = request.get_json(silent=True) or {}
    nome = dados.get("nome")
    email = dados.get("email")
    if not nome or not email:
        return erro("Campos 'nome' e 'email' são obrigatórios.")
    try:
        usuario_id = crud.criar_usuario(nome, email)
        return jsonify({"id": usuario_id, "nome": nome, "email": email}), 201
    except Error as e:
        return erro(str(e), 500)


@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    return jsonify(crud.listar_usuarios())


@app.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscar_usuario(usuario_id):
    usuario = crud.buscar_usuario(usuario_id)
    if not usuario:
        return erro("Usuário não encontrado.", 404)
    return jsonify(usuario)


# ---------------------------------------------------------------------------
# TAREFAS
# ---------------------------------------------------------------------------

@app.route("/tarefas", methods=["POST"])
def criar_tarefa():
    dados = request.get_json(silent=True) or {}
    usuario_id = dados.get("usuario_id")
    titulo = dados.get("titulo")
    descricao = dados.get("descricao", "")

    if not usuario_id or not titulo:
        return erro("Campos 'usuario_id' e 'titulo' são obrigatórios.")
    if not crud.buscar_usuario(usuario_id):
        return erro("Usuário não encontrado.", 404)

    try:
        tarefa_id = crud.criar_tarefa(usuario_id, titulo, descricao)
        return jsonify(crud.buscar_tarefa(tarefa_id)), 201
    except Error as e:
        return erro(str(e), 500)


@app.route("/tarefas", methods=["GET"])
def listar_tarefas():
    usuario_id = request.args.get("usuario_id", type=int)
    return jsonify(crud.listar_tarefas(usuario_id))


@app.route("/tarefas/<int:tarefa_id>", methods=["GET"])
def buscar_tarefa(tarefa_id):
    tarefa = crud.buscar_tarefa(tarefa_id)
    if not tarefa:
        return erro("Tarefa não encontrada.", 404)
    return jsonify(tarefa)


@app.route("/tarefas/<int:tarefa_id>", methods=["PUT"])
def atualizar_tarefa(tarefa_id):
    if not crud.buscar_tarefa(tarefa_id):
        return erro("Tarefa não encontrada.", 404)

    dados = request.get_json(silent=True) or {}
    if not dados:
        return erro("Envie ao menos um campo para atualizar.")

    crud.atualizar_tarefa(tarefa_id, **dados)
    return jsonify(crud.buscar_tarefa(tarefa_id))


@app.route("/tarefas/<int:tarefa_id>/concluir", methods=["PATCH"])
def concluir_tarefa(tarefa_id):
    if not crud.buscar_tarefa(tarefa_id):
        return erro("Tarefa não encontrada.", 404)
    crud.concluir_tarefa(tarefa_id)
    return jsonify(crud.buscar_tarefa(tarefa_id))


@app.route("/tarefas/<int:tarefa_id>", methods=["DELETE"])
def excluir_tarefa(tarefa_id):
    if not crud.buscar_tarefa(tarefa_id):
        return erro("Tarefa não encontrada.", 404)
    crud.excluir_tarefa(tarefa_id)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)