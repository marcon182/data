-- Apaga a tabela se ela já existir, para garantir que começamos do zero.
DROP TABLE IF EXISTS ordens;

-- Cria a tabela de ordens de serviço
CREATE TABLE ordens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,        -- Número da OS, automático e crescente
    nome_funcionario TEXT NOT NULL,              -- Nome do funcionário
    descricao_tarefa TEXT NOT NULL,              -- Descrição do que precisa ser feito
    data_hora_inicio TEXT NOT NULL,              -- Data e hora do início
    data_hora_fim TEXT,                          -- Data e hora do fim (pode ser nulo)
    status TEXT NOT NULL                         -- Status: 'Aberto' ou 'Finalizado'
);