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
from werkzeug.security import generate_password_hash

# Conecta ao banco de dados
connection = sqlite3.connect('chamados.db')
cursor = connection.cursor()

print("Criando usuários iniciais...")

# --- Usuário Master ---
# A senha 'admin' será armazenada de forma segura
# master_password = generate_password_hash('admin', method='pbkdf2:sha256')
# cursor.execute(
  #  "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
   # ('master', master_password, 'master')
# )

# --- Usuário Padrão ---
# A senha '1234' será armazenada de forma segura
user_password = generate_password_hash('1234', method='pbkdf2:sha256')
cursor.execute(
    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
    ('marco', user_password, 'user')
)

connection.commit()
connection.close()

print("'marco' (senha: 1234) criados com sucesso.")