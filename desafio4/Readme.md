# Gestão de Tarefas — Modelagem + CRUD

Projeto de desafio: modelagem de banco de dados simples e aplicação de gestão
de tarefas, onde usuários podem criar, visualizar, atualizar e excluir suas
próprias tarefas.

## Estrutura do projeto

```
task-manager/
├── README.md
├── docs/
│   └── modelagem.md      # Entidades, atributos e diagrama ER
├── sql/
│   └── schema.sql        # Script de criação das tabelas (SQLite)
└── src/
    └── crud.py           # Script Python com as operações CRUD
```

## Modelagem

Duas entidades: `usuario` (1) — (N) `tarefa`. Detalhes completos, atributos
e o diagrama entidade-relacionamento estão em [`docs/modelagem.md`](docs/modelagem.md).

## Banco de dados

SGBD escolhido: **SQLite** (não exige servidor, ideal para portfólio e fácil
de rodar em qualquer máquina). O script `sql/schema.sql` cria as tabelas
`usuario` e `tarefa`, com chave estrangeira e `ON DELETE CASCADE`.

> O schema também roda em PostgreSQL/MySQL com pequenos ajustes de sintaxe
> (indicados em comentário no próprio arquivo).

## Como rodar

Requer apenas Python 3.10+ (usa só a biblioteca padrão, `sqlite3`).

```bash
cd task-manager
python3 src/crud.py
```

Isso vai:
1. Criar o banco `sql/tarefas.db` executando o `schema.sql` (se ainda não existir).
2. Rodar uma demonstração das operações: criar, listar, atualizar, concluir e deletar tarefas.

## Operações disponíveis (`src/crud.py`)

| Função                     | Operação | Descrição                                      |
|-----------------------------|----------|-------------------------------------------------|
| `criar_tarefa(...)`          | Create   | Insere uma nova tarefa                          |
| `listar_tarefas(usuario_id)` | Read     | Lista tarefas (todas ou de um usuário)          |
| `buscar_tarefa_por_id(id)`   | Read     | Busca uma tarefa específica                     |
| `atualizar_tarefa(...)`      | Update   | Atualiza título, descrição e/ou status          |
| `concluir_tarefa(id)`        | Update   | Marca como concluída e registra a data          |
| `deletar_tarefa(id)`         | Delete   | Remove uma tarefa                               |

## Boas práticas aplicadas

- Queries parametrizadas (`?`) — evita SQL Injection.
- Separação entre camada de acesso a dados e uso (bloco `__main__` como demo).
- Context manager para conexão (commit/rollback e `close()` automáticos).
- Constraint `CHECK` no `status` para garantir valores válidos no banco.