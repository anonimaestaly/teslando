-- ============================================
-- Schema do banco de dados - Gestão de Tarefas
-- SGBD: MySQL
-- ============================================

CREATE DATABASE IF NOT EXISTS gestao_tarefas;
USE gestao_tarefas;

-- ============================================
-- Tabela: usuario
-- ============================================
CREATE TABLE IF NOT EXISTS usuario (
    id            INT PRIMARY KEY AUTO_INCREMENT,
    nome          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    senha_hash    VARCHAR(255) NOT NULL,
    data_criacao  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Tabela: tarefa
-- ============================================
CREATE TABLE IF NOT EXISTS tarefa (
    id               INT PRIMARY KEY AUTO_INCREMENT,
    titulo           VARCHAR(150) NOT NULL,
    descricao        TEXT,
    status           VARCHAR(20) NOT NULL DEFAULT 'pendente'
                     CHECK (status IN ('pendente', 'em_andamento', 'concluida')),
    data_criacao     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_conclusao   DATETIME,
    usuario_id       INT NOT NULL,

    FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE CASCADE,

    CHECK (
        (status = 'concluida' AND data_conclusao IS NOT NULL)
        OR (status != 'concluida' AND data_conclusao IS NULL)
    )
);

-- ============================================
-- Índices
-- ============================================
CREATE INDEX idx_tarefa_usuario ON tarefa (usuario_id);

-- ============================================
-- Dados de exemplo
-- ============================================
INSERT INTO usuario (nome, email, senha_hash)
VALUES ('Ester Dev', 'ester@example.com', 'hash_fake_apenas_para_teste')
ON DUPLICATE KEY UPDATE email = email;