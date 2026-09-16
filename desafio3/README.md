# App de Dieta — API Back-end

API REST em Node.js + Express + Prisma para um app de dieta que:
- calcula metas diárias de calorias e macronutrientes;
- permite montar cardápio a partir de um banco de alimentos;
- compara o consumo do dia com a meta;
- registra e lista o progresso de peso do usuário.

## Stack

- Node.js + Express
- PostgreSQL + Prisma ORM
- Autenticação com JWT + bcrypt

## Como rodar

1. Instale as dependências:
   ```bash
   npm install
   ```

2. Copie `.env.example` para `.env` e preencha com sua string de conexão do PostgreSQL e um `JWT_SECRET`:
   ```bash
   cp .env.example .env
   ```

3. Rode as migrações (cria as tabelas no banco):
   ```bash
   npm run prisma:migrate
   ```

4. Popule o banco com alimentos de exemplo:
   ```bash
   npm run prisma:seed
   ```

5. Suba o servidor em modo desenvolvimento:
   ```bash
   npm run dev
   ```

A API sobe em `http://localhost:3000`.

## Fluxo de uso da API

### 1. Registrar usuário
```
POST /auth/registrar
{
  "nome": "Maria Silva",
  "email": "maria@email.com",
  "senha": "senha123",
  "dataNascimento": "1998-05-10",
  "sexo": "feminino",
  "alturaCm": 165
}
```
Retorna `{ usuario, token }`. Use o `token` no header `Authorization: Bearer <token>` em todas as rotas abaixo.

### 2. Definir perfil nutricional (calcula metas automaticamente)
```
POST /usuarios/me/perfil
{
  "pesoAtualKg": 68,
  "nivelAtividade": "moderado",
  "objetivo": "emagrecer"
}
```
Retorna as metas calculadas de calorias, proteína, carboidrato e gordura.

### 3. Buscar alimentos
```
GET /alimentos?busca=frango
```

### 4. Montar uma refeição
```
POST /refeicoes
{
  "tipo": "almoco",
  "itens": [
    { "alimentoId": 3, "quantidadeG": 150 },
    { "alimentoId": 1, "quantidadeG": 100 }
  ]
}
```

### 5. Ver resumo do dia (consumido x meta)
```
GET /refeicoes/resumo-diario?data=2026-09-14
```

### 6. Registrar progresso de peso
```
POST /progresso
{ "pesoKg": 67.5 }
```

### 7. Listar histórico de progresso (para o gráfico)
```
GET /progresso
```

## Estrutura de pastas

```
src/
  config/db.js          -> instância do Prisma Client
  middleware/auth.js     -> valida token JWT
  middleware/errorHandler.js -> tratamento central de erros
  utils/macroCalculator.js   -> lógica pura de cálculo de TMB e macros
  controllers/           -> lógica de cada recurso
  routes/                -> definição das rotas Express
  app.js                 -> configuração do Express
  server.js              -> ponto de entrada
prisma/
  schema.prisma          -> modelagem do banco
  seed.js                -> popula alimentos de exemplo
```

## Próximos passos sugeridos

- Front-end em React consumindo essa API (tela de login, montagem de cardápio e gráfico de progresso com Recharts).
- Testes automatizados para `macroCalculator.js` (é a lógica mais sensível a bugs).
- Deploy do back-end (Render/Railway) e do banco (Neon/Supabase para Postgres gratuito).
