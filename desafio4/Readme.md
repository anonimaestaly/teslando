# Gestão de Tarefas — Modelagem + CRUD

Projeto de desafio: modelagem de banco de dados simples e aplicação de gestão
de tarefas, onde usuários podem criar, visualizar, atualizar e excluir suas
próprias tarefas.

## Estrutura do projeto

```
desafio4/
├── Readme.md
├── modelagem.md       # Entidades, atributos e diagrama ER
├── crud.py            # Funções de acesso a dados (Create, Read, Update, Delete)
├── cli.py             # Menu interativo no terminal
├── api.py             # API REST com FastAPI
└── sql/
    ├── schema.sql      # Script de criação das tabelas (SQLite)
    └── tarefas.db      # Criado automaticamente ao rodar o crud.py, cli.py ou api.py
```

## Modelagem

Duas entidades: `usuario` (1) — (N) `tarefa`. Os atributos completos e o
diagrama entidade-relacionamento estão detalhados em
[`modelagem.md`](modelagem.md).

## Banco de dados

**SGBD escolhido:** SQLite — não exige servidor, é ideal para portfólio e
roda em qualquer máquina sem configuração extra.

O script `sql/schema.sql` cria as tabelas `usuario` e `tarefa`, com chave
estrangeira e `ON DELETE CASCADE`.

> O schema também roda em PostgreSQL/MySQL com pequenos ajustes de sintaxe,
> indicados em comentário no próprio arquivo.

## Como rodar

Requer apenas Python 3.10+ (usa só a biblioteca padrão, via `sqlite3`).

### Demonstração fixa (`crud.py`)

```bash
cd desafio4
python crud.py
```

Isso vai:

1. Criar o banco `sql/tarefas.db`, executando o `schema.sql` (se ainda não existir).
2. Rodar uma demonstração das operações: criar, listar, atualizar, concluir e deletar tarefas.

### Menu interativo no terminal (`cli.py`)

```bash
cd desafio4
python cli.py
```

Abre um menu no terminal para criar, listar, buscar, atualizar, concluir e deletar tarefas manualmente.

### API REST (`api.py`)

Requer instalar duas dependências extras:

```bash
pip install fastapi uvicorn
```

Depois, para subir o servidor:

```bash
cd desafio4
uvicorn api:app --reload
```

A documentação interativa fica disponível em `http://127.0.0.1:8000/docs`.

| Método   | Rota                          | Descrição                          |
|----------|-------------------------------|--------------------------------------|
| `POST`   | `/tarefas`                    | Cria uma nova tarefa                 |
| `GET`    | `/tarefas`                    | Lista tarefas (filtro opcional `usuario_id`) |
| `GET`    | `/tarefas/{id}`                | Busca uma tarefa específica          |
| `PUT`    | `/tarefas/{id}`                | Atualiza título, descrição e/ou status |
| `PATCH`  | `/tarefas/{id}/concluir`       | Marca como concluída e registra a data |
| `DELETE` | `/tarefas/{id}`                | Remove uma tarefa                    |

## Operações disponíveis (`crud.py`)

| Função                        | Operação | Descrição                                |
|--------------------------------|----------|-------------------------------------------|
| `criar_tarefa(...)`             | Create   | Insere uma nova tarefa                    |
| `listar_tarefas(usuario_id)`    | Read     | Lista tarefas (todas ou de um usuário)    |
| `buscar_tarefa_por_id(id)`      | Read     | Busca uma tarefa específica               |
| `atualizar_tarefa(...)`         | Update   | Atualiza título, descrição e/ou status    |
| `concluir_tarefa(id)`           | Update   | Marca como concluída e registra a data    |
| `deletar_tarefa(id)`            | Delete   | Remove uma tarefa                         |

## Boas práticas aplicadas

- **Queries parametrizadas** (`?`) — evita SQL Injection.
- **Separação de responsabilidades** — camada de acesso a dados isolada do uso (bloco `__main__` como demonstração).
- **Context manager** para conexão — commit/rollback e `close()` automáticos.
- **Constraint `CHECK`** no campo `status` e no par `status`/`data_conclusao` — garante valores válidos e consistência direto no banco.