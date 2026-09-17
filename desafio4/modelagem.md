# Task Manager

Sistema simples de gerenciamento de tarefas em Python, com persistência em
banco de dados relacional. Projeto pensado como peça de portfólio, com foco
em boas práticas de acesso a dados.

## Modelagem

Duas entidades: `usuario` (1) — (N) `tarefa`. Os atributos completos e o
diagrama entidade-relacionamento estão detalhados em
[`docs/modelagem.md`](docs/modelagem.md).

## Banco de dados

**SGBD escolhido:** SQLite — não exige servidor, é ideal para portfólio e
roda em qualquer máquina sem configuração extra.

O script `sql/schema.sql` cria as tabelas `usuario` e `tarefa`, com chave
estrangeira e `ON DELETE CASCADE`.

> O schema também roda em PostgreSQL/MySQL com pequenos ajustes de sintaxe,
> indicados em comentário no próprio arquivo.

## Como rodar

Requer apenas Python 3.10+ (usa só a biblioteca padrão, via `sqlite3`).

```bash
cd task-manager
python3 src/crud.py
```

Isso vai:

1. Criar o banco `sql/tarefas.db`, executando o `schema.sql` (se ainda não existir).
2. Rodar uma demonstração das operações: criar, listar, atualizar, concluir e deletar tarefas.

## Operações disponíveis (`src/crud.py`)

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
- **Constraint `CHECK`** no campo `status` — garante valores válidos direto no banco.