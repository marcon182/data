import os # Garanta que este import está no topo do arquivo
import sqlite3

# Caminho do Disco Persistente no Render
DATA_DIR = '/var/data'
DB_PATH = os.path.join(DATA_DIR, 'chamados.db')

def get_db_connection():
    # Cria o diretório de dados se ele não existir
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Conecta ao banco de dados (cria o arquivo se não existir)
connection = sqlite3.connect('chamados.db')

# Abre e lê o arquivo schema.sql
with open('schema.sql') as f:
    connection.executescript(f.read())

# Confirma as alterações e fecha a conexão
connection.commit()
connection.close()

print("Banco de dados inicializado com sucesso.")