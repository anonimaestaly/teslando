"""API REST para o CRUD de tarefas, usando FastAPI."""

from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from crud import (
    inicializar_banco,
    criar_tarefa,
    listar_tarefas,
    buscar_tarefa_por_id,
    atualizar_tarefa,
    concluir_tarefa,
    deletar_tarefa,
)

STATUS_VALIDOS = ("pendente", "em_andamento", "concluida")


@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_banco()
    yield


app = FastAPI(
    title="Gestão de Tarefas",
    description=(
        "API para criar, listar, buscar, atualizar, concluir e apagar "
        "tarefas. Cada tarefa pertence a um usuário (usuario_id)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# ---------- Schemas (Pydantic) ----------

class TarefaCreate(BaseModel):
    titulo: str = Field(
        min_length=1,
        description="Nome curto da tarefa.",
        examples=["Estudar para a prova"],
    )
    descricao: Optional[str] = Field(
        default=None,
        description="Detalhes da tarefa (opcional).",
        examples=["Revisar capítulos 3 e 4"],
    )
    usuario_id: int = Field(
        description="Id do usuário dono da tarefa.",
        examples=[1],
    )
    status: str = Field(
        default="pendente",
        description="Situação da tarefa: pendente, em_andamento ou concluida.",
        examples=["pendente"],
    )


class TarefaUpdate(BaseModel):
    titulo: Optional[str] = Field(default=None, description="Novo título (opcional).")
    descricao: Optional[str] = Field(default=None, description="Nova descrição (opcional).")
    status: Optional[str] = Field(
        default=None,
        description="Novo status: pendente, em_andamento ou concluida (opcional).",
    )


class TarefaOut(BaseModel):
    id: int = Field(description="Id da tarefa.")
    titulo: str = Field(description="Nome da tarefa.")
    descricao: Optional[str] = Field(description="Detalhes da tarefa.")
    status: str = Field(description="Situação atual da tarefa.")
    data_criacao: str = Field(description="Data e hora em que a tarefa foi criada.")
    data_conclusao: Optional[str] = Field(description="Data e hora em que a tarefa foi concluída.")
    usuario_id: int = Field(description="Id do usuário dono da tarefa.")


def _row_to_dict(row):
    return dict(row) if row is not None else None


# ---------- Rotas ----------

@app.post(
    "/tarefas",
    response_model=TarefaOut,
    status_code=201,
    summary="Criar uma nova tarefa",
    description="Cria uma tarefa para um usuário. O status inicial pode ser informado, o padrão é 'pendente'.",
)
def criar(tarefa: TarefaCreate):
    if tarefa.status not in STATUS_VALIDOS:
        raise HTTPException(status_code=422, detail=f"status deve ser um de {STATUS_VALIDOS}")
    tarefa_id = criar_tarefa(tarefa.titulo, tarefa.descricao, tarefa.usuario_id, tarefa.status)
    return _row_to_dict(buscar_tarefa_por_id(tarefa_id))


@app.get(
    "/tarefas",
    response_model=list[TarefaOut],
    summary="Listar tarefas",
    description="Lista todas as tarefas. Se informar usuario_id, mostra só as tarefas daquele usuário.",
)
def listar(usuario_id: Optional[int] = None):
    return [dict(t) for t in listar_tarefas(usuario_id)]


@app.get(
    "/tarefas/{tarefa_id}",
    response_model=TarefaOut,
    summary="Buscar uma tarefa pelo id",
    description="Retorna os dados de uma tarefa específica. Se o id não existir, retorna erro 404.",
)
def buscar(tarefa_id: int):
    tarefa = buscar_tarefa_por_id(tarefa_id)
    if tarefa is None:
        raise HTTPException(status_code=404, detail="tarefa não encontrada")
    return dict(tarefa)


@app.put(
    "/tarefas/{tarefa_id}",
    response_model=TarefaOut,
    summary="Atualizar título, descrição ou status",
    description="Atualiza os campos enviados de uma tarefa existente. Campos não enviados não são alterados.",
)
def atualizar(tarefa_id: int, tarefa: TarefaUpdate):
    if tarefa.status is not None and tarefa.status not in STATUS_VALIDOS:
        raise HTTPException(status_code=422, detail=f"status deve ser um de {STATUS_VALIDOS}")
    atualizado = atualizar_tarefa(
        tarefa_id,
        titulo=tarefa.titulo,
        descricao=tarefa.descricao,
        status=tarefa.status,
    )
    if not atualizado:
        raise HTTPException(status_code=404, detail="tarefa não encontrada")
    return dict(buscar_tarefa_por_id(tarefa_id))


@app.patch(
    "/tarefas/{tarefa_id}/concluir",
    response_model=TarefaOut,
    summary="Marcar tarefa como concluída",
    description="Muda o status da tarefa para 'concluida' e registra a data/hora de conclusão.",
)
def concluir(tarefa_id: int):
    if not concluir_tarefa(tarefa_id):
        raise HTTPException(status_code=404, detail="tarefa não encontrada")
    return dict(buscar_tarefa_por_id(tarefa_id))


@app.delete(
    "/tarefas/{tarefa_id}",
    status_code=204,
    summary="Apagar uma tarefa",
    description="Remove definitivamente a tarefa do banco de dados.",
)
def deletar(tarefa_id: int):
    if not deletar_tarefa(tarefa_id):
        raise HTTPException(status_code=404, detail="tarefa não encontrada")