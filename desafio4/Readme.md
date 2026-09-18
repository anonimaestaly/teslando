# Gestão de Tarefas

Esse é o meu projeto pro desafio de modelagem de banco de dados. A ideia era
simples: montar um banco pra guardar tarefas de usuários, e depois construir
uma forma de mexer nesses dados (criar, ver, editar e apagar tarefas).

Decidi ir um pouco além do pedido e fiz duas formas de usar o sistema: um
menu direto no terminal, e uma API de verdade, pra treinar as duas coisas.

## O que tem em cada arquivo

- `modelagem.md` — como pensei o banco: as entidades, os atributos de cada
  uma, e o diagrama mostrando como elas se relacionam.
- `sql/schema.sql` — o script que cria as tabelas no banco.
- `sql/tarefas.db` — o banco em si (arquivo SQLite). É gerado sozinho na
  primeira vez que você roda qualquer um dos scripts abaixo.
- `crud.py` — onde ficam as funções que realmente mexem no banco: criar,
  listar, buscar, atualizar, concluir e deletar tarefa. Todo o resto do
  projeto usa essas funções, não conversa com o banco diretamente.
- `cli.py` — um menu no terminal pra usar o CRUD sem precisar escrever código.
- `api.py` — a mesma coisa, mas como uma API REST feita com FastAPI, pra
  quem quiser acessar via HTTP em vez de terminal.

## Por que SQLite

Escolhi SQLite porque o banco inteiro fica guardado num arquivo só, sem
precisar instalar nem configurar um servidor separado. Pra um projeto de
portfólio isso facilita muito — quem for testar meu código não precisa
instalar MySQL ou PostgreSQL antes, é só rodar.

## Como rodar

Só precisa de Python (a parte do banco usa `sqlite3`, que já vem
instalado por padrão).

**Testar a lógica direto:**
```bash
cd desafio4
python crud.py
```
Isso cria o banco (se ainda não existir) e roda um teste que cria, atualiza,
conclui e apaga algumas tarefas de exemplo, imprimindo o resultado de cada
passo no terminal.

**Usar o menu interativo:**
```bash
cd desafio4
python cli.py
```
Abre um menu numerado — escolhe a opção digitando o número e segue as
instruções que aparecem na tela.

**Subir a API:**

Primeiro instala o que falta:
```bash
pip install fastapi uvicorn
```

Depois:
```bash
cd desafio4
uvicorn api:app --reload
```

Com o servidor rodando, dá pra abrir `http://127.0.0.1:8000/docs` no
navegador e testar cada rota por lá, sem precisar escrever nenhum código
pra fazer as requisições.

## As rotas da API

| Rota                       | O que faz                                  |
|-----------------------------|---------------------------------------------|
| `POST /tarefas`              | Cria uma tarefa nova                        |
| `GET /tarefas`               | Lista as tarefas (dá pra filtrar por usuário) |
| `GET /tarefas/{id}`          | Busca uma tarefa específica                 |
| `PUT /tarefas/{id}`          | Atualiza título, descrição ou status        |
| `PATCH /tarefas/{id}/concluir` | Marca como concluída                      |
| `DELETE /tarefas/{id}`       | Apaga a tarefa                              |

## Decisões que tomei no código

Separei o projeto assim de propósito: o `crud.py` é a única parte que sabe
escrever SQL. Tanto o `cli.py` quanto o `api.py` só chamam as funções dele —
nenhum dos dois monta uma query sozinho. Isso significa que, se um dia eu
quiser trocar de SQLite pra outro banco, só preciso mexer no `crud.py`, o
resto continua igual.

Outras coisas que me preocupei em fazer certo:

- Todas as consultas usam `?` no lugar dos valores (parâmetros), em vez de
  montar a query colando texto — isso evita SQL Injection.
- A conexão com o banco é aberta e fechada automaticamente (usando um
  context manager), então não corro risco de esquecer uma conexão aberta ou
  de deixar o banco num estado inconsistente se der algum erro no meio do
  caminho.
- O banco tem uma regra (`CHECK`) garantindo que uma tarefa só pode ter data
  de conclusão se o status dela for "concluída" — assim, mesmo que algum bug
  no código tente salvar algo errado, o próprio banco recusa.

## O que ficaria pra uma próxima versão

- Autenticação de verdade (hoje o `cli.py` assume um usuário fixo pra
  simplificar; o banco já tem a tabela de usuário pronta pra isso).
- Rotas na API pra criar e gerenciar usuários, não só tarefas.