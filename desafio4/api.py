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


app = FastAPI(title="Gestão de Tarefas", lifespan=lifespan)


# ---------- Schemas (Pydantic) ----------

class TarefaCreate(BaseModel):
    titulo: str = Field(min_length=1)
    descricao: Optional[str] = None
    usuario_id: int
    status: str = "pendente"


class TarefaUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[str] = None


class TarefaOut(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    status: str
    data_criacao: str
    data_conclusao: Optional[str]
    usuario_id: int


def _row_to_dict(row):
    return dict(row) if row is not None else None


# ---------- Rotas ----------

@app.post("/tarefas", response_model=TarefaOut, status_code=201)
def criar(tarefa: TarefaCreate):
    if tarefa.status not in STATUS_VALIDOS:
        raise HTTPException(status_code=422, detail=f"status deve ser um de {STATUS_VALIDOS}")
    tarefa_id = criar_tarefa(tarefa.titulo, tarefa.descricao, tarefa.usuario_id, tarefa.status)
    return _row_to_dict(buscar_tarefa_por_id(tarefa_id))


@app.get("/tarefas", response_model=list[TarefaOut])
def listar(usuario_id: Optional[int] = None):
    return [dict(t) for t in listar_tarefas(usuario_id)]


@app.get("/tarefas/{tarefa_id}", response_model=TarefaOut)
def buscar(tarefa_id: int):
    tarefa = buscar_tarefa_por_id(tarefa_id)
    if tarefa is None:
        raise HTTPException(status_code=404, detail="tarefa não encontrada")
    return dict(tarefa)


@app.put("/tarefas/{tarefa_id}", response_model=TarefaOut)
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


@app.patch("/tarefas/{tarefa_id}/concluir", response_model=TarefaOut)
def concluir(tarefa_id: int):
    if not concluir_tarefa(tarefa_id):
        raise HTTPException(status_code=404, detail="tarefa não encontrada")
    return dict(buscar_tarefa_por_id(tarefa_id))


@app.delete("/tarefas/{tarefa_id}", status_code=204)
def deletar(tarefa_id: int):
    if not deletar_tarefa(tarefa_id):
        raise HTTPException(status_code=404, detail="tarefa não encontrada")