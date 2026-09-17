-- ============================================
-- Schema do banco de dados - Gestão de Tarefas
-- SGBD: SQLite
-- (funciona também em PostgreSQL/MySQL com pequenos
--  ajustes de sintaxe, indicados nos comentários)
-- ============================================

PRAGMA foreign_keys = ON;

-- ============================================
-- Tabela: usuario
-- ============================================
CREATE TABLE IF NOT EXISTS usuario (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    senha_hash    VARCHAR(255) NOT NULL,
    data_criacao  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Tabela: tarefa
-- Em PostgreSQL: troque AUTOINCREMENT por
-- GENERATED ALWAYS AS IDENTITY (ou SERIAL)
-- ============================================
CREATE TABLE IF NOT EXISTS tarefa (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo           VARCHAR(150) NOT NULL,
    descricao        TEXT,
    status           VARCHAR(20) NOT NULL DEFAULT 'pendente'
                     CHECK (status IN ('pendente', 'em_andamento', 'concluida')),
    data_criacao     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_conclusao   DATETIME,
    usuario_id       INTEGER NOT NULL,

    FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE,

    -- Garante consistência entre status e data_conclusao:
    -- só pode ter data_conclusao preenchida se status = 'concluida',
    -- e toda tarefa concluída precisa ter uma data_conclusao.
    CHECK (
        (status = 'concluida' AND data_conclusao IS NOT NULL)
        OR (status != 'concluida' AND data_conclusao IS NULL)
    )
);

-- ============================================
-- Índices
-- ============================================

-- Acelera buscas de tarefas por usuário
CREATE INDEX IF NOT EXISTS idx_tarefa_usuario ON tarefa (usuario_id);

-- ============================================
-- Dados de exemplo
-- (opcional, útil para testar o CRUD)
-- ============================================
INSERT INTO usuario (nome, email, senha_hash)
VALUES ('Ester Dev', 'ester@example.com', 'hash_fake_apenas_para_teste')
ON CONFLICT (email) DO NOTHING;