-- ============================================================
-- NutriChat - Script SQL do Banco de Dados
-- ============================================================

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    idade INTEGER,
    peso REAL,
    altura REAL,
    objetivo TEXT DEFAULT 'manter_peso',  -- emagrecer | ganhar_massa | manter_peso
    nivel_atividade TEXT DEFAULT 'sedentario',
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP
);

-- Tabela de Histórico de Conversas
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,       -- 'user' ou 'assistant'
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabela de Registros de IMC (evolução do usuário)
CREATE TABLE IF NOT EXISTS imc_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    peso REAL NOT NULL,
    altura REAL NOT NULL,
    imc REAL NOT NULL,
    classificacao TEXT NOT NULL,
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_imc_user ON imc_records(user_id, data_registro);
