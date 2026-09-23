# Desafio — Modelagem de Banco de Dados + Gestão de Tarefas (MySQL)

## Estrutura

```
desafio-db/
├── diagrama/
│   └── er-diagram.md      # Diagrama entidade-relacionamento (Mermaid)
├── sql/
│   └── schema.sql         # Criação do banco e tabelas em MySQL
├── src/
│   └── crud.py            # Script Python com o CRUD completo
└── README.md
```

## Entidades

- **usuario** (1) — (N) **tarefa**

## Como rodar

1. **Criar o banco:**
   ```bash
   mysql -u root -p < sql/schema.sql
   ```
   Isso cria o banco `gestao_tarefas`, as tabelas `usuario` e `tarefa`, e insere
   alguns dados de exemplo.

2. **Instalar a dependência do Python:**
   ```bash
   pip install mysql-connector-python
   ```

3. **Ajustar a conexão** em `src/crud.py` (usuário/senha do seu MySQL local).

4. **Rodar a demonstração do CRUD:**
   ```bash
   python src/crud.py
   ```
   Isso vai criar, listar, buscar, atualizar, concluir e deletar uma tarefa,
   imprimindo cada etapa no terminal.

## Boas práticas aplicadas

- Queries **parametrizadas** (`%s`), sem concatenação de string — evita SQL Injection.
- **Context manager** (`get_connection`) garante que a conexão sempre é fechada.
- **Chave estrangeira** com `ON DELETE CASCADE`: ao apagar um usuário, suas tarefas somem junto.
- `status` como **ENUM** em vez de texto livre, evitando valores inconsistentes.
- Separação clara entre criação do schema (SQL) e lógica de acesso a dados (Python).