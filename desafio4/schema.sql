-- =========================================================
-- Gestão de Tarefas — Modelagem em MySQL
-- =========================================================

CREATE DATABASE IF NOT EXISTS gestao_tarefas
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE gestao_tarefas;

-- ---------------------------------------------------------
-- Tabela: usuario
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuario (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(100)  NOT NULL,
    email           VARCHAR(150)  NOT NULL UNIQUE,
    senha           VARCHAR(255)  NOT NULL,
    data_cadastro   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Tabela: tarefa
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS tarefa (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    titulo           VARCHAR(150) NOT NULL,
    descricao        TEXT,
    data_criacao     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_conclusao   DATETIME     NULL,
    status           ENUM('pendente', 'em_andamento', 'concluida')
                         NOT NULL DEFAULT 'pendente',
    usuario_id       INT NOT NULL,

    CONSTRAINT fk_tarefa_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_tarefa_usuario (usuario_id),
    INDEX idx_tarefa_status (status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Dados de exemplo (opcional, útil para testar o CRUD)
-- ---------------------------------------------------------
INSERT INTO usuario (nome, email, senha) VALUES
    ('Ana Silva', 'ana.silva@email.com', 'senha_hash_1'),
    ('Bruno Costa', 'bruno.costa@email.com', 'senha_hash_2');

INSERT INTO tarefa (titulo, descricao, usuario_id) VALUES
    ('Estudar SQL', 'Revisar joins e subqueries', 1),
    ('Montar portfólio', 'Subir projetos no GitHub', 1),
    ('Preparar entrevista', 'Revisar perguntas técnicas comuns', 2);