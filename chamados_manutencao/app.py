import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, Response
from datetime import datetime
import io
import pandas as pd

app = Flask(__name__)

# Caminho do Disco Persistente no Render
DATA_DIR = '/var/data'
DB_PATH = os.path.join(DATA_DIR, 'chamados.db')

def get_db_connection():
    # Cria o diretório de dados se ele não existir
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Rota principal - exibe a interface e o histórico
@app.route('/')
def index():
    conn = get_db_connection()
    ordens_db = conn.execute('SELECT * FROM ordens ORDER BY id DESC').fetchall()
    
    # Lista para armazenar as ordens com o novo campo 'tempo_gasto'
    ordens_processadas = []

    for ordem in ordens_db:
        ordem_dict = dict(ordem) # Converte a linha do banco para um dicionário mutável
        
        # --- LÓGICA DO TEMPO GASTO ---
        if ordem_dict['status'] == 'Finalizado' and ordem_dict['data_hora_fim']:
            # Converte as strings de data/hora para objetos datetime
            formato_data = '%d/%m/%Y %H:%M:%S'
            inicio = datetime.strptime(ordem_dict['data_hora_inicio'], formato_data)
            fim = datetime.strptime(ordem_dict['data_hora_fim'], formato_data)
            
            # Calcula a duração
            duracao = fim - inicio
            
            # Formata a duração para um formato legível (HH:MM:SS)
            total_seconds = int(duracao.total_seconds())
            horas = total_seconds // 3600
            minutos = (total_seconds % 3600) // 60
            segundos = total_seconds % 60
            
            ordem_dict['tempo_gasto'] = f"{horas:02d}h {minutos:02d}m {segundos:02d}s"
        else:
            ordem_dict['tempo_gasto'] = '---'
        
        ordens_processadas.append(ordem_dict)

    ordens_abertas = conn.execute("SELECT * FROM ordens WHERE status = 'Aberto' ORDER BY id ASC").fetchall()
    conn.close()
    
    return render_template('index.html', ordens=ordens_processadas, ordens_abertas=ordens_abertas)


# Rota para iniciar uma nova ordem de serviço
@app.route('/iniciar', methods=['POST'])
def iniciar():
    nome = request.form['nome']
    tarefa = request.form['tarefa']
    
    if not nome or not tarefa:
        return redirect(url_for('index'))

    data_hora_inicio = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO ordens (nome_funcionario, descricao_tarefa, data_hora_inicio, status) VALUES (?, ?, ?, ?)',
        (nome, tarefa, data_hora_inicio, 'Aberto')
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

# Rota para finalizar uma ordem de serviço
@app.route('/finalizar', methods=['POST'])
def finalizar():
    ordem_id = request.form['ordem_id']
    data_hora_fim = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE ordens SET data_hora_fim = ?, status = ? WHERE id = ?',
        (data_hora_fim, 'Finalizado', ordem_id)
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

# Rota para exportar dados para Excel (.xlsx)
@app.route('/exportar_excel')
def exportar_excel():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM ordens ORDER BY id ASC", conn)
    conn.close()

    # Converte colunas de data/hora para o formato datetime do pandas
    formato_data = '%d/%m/%Y %H:%M:%S'
    df['data_hora_inicio'] = pd.to_datetime(df['data_hora_inicio'], format=formato_data)
    df['data_hora_fim'] = pd.to_datetime(df['data_hora_fim'], format=formato_data, errors='coerce') # 'coerce' transforma erros em NaT (Not a Time)

    # Calcula a coluna 'Tempo Gasto'
    df['Tempo Gasto'] = df['data_hora_fim'] - df['data_hora_inicio']

    # Formata a coluna 'Tempo Gasto' para string, tratando os valores nulos
    df['Tempo Gasto'] = df['Tempo Gasto'].apply(lambda x: str(x).split('.')[0] if pd.notna(x) else '---')
    
    # Formata as colunas de data de volta para string para melhor visualização no Excel
    df['data_hora_inicio'] = df['data_hora_inicio'].dt.strftime(formato_data)
    df['data_hora_fim'] = df['data_hora_fim'].dt.strftime(formato_data).fillna('---')

    # Renomeia as colunas para ficarem mais amigáveis
    df.rename(columns={
        'id': 'Nº da OS',
        'nome_funcionario': 'Funcionário',
        'descricao_tarefa': 'Descrição da Tarefa',
        'data_hora_inicio': 'Data e Hora de Início',
        'data_hora_fim': 'Data e Hora de Fim',
        'status': 'Status',
        'Tempo Gasto': 'Tempo Gasto (dias, H:M:S)' # Novo nome de coluna
    }, inplace=True)

    output = io.BytesIO()
    df.to_excel(output, index=False, sheet_name='Ordens de Serviço')
    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": "attachment;filename=historico_chamados.xlsx"}
    )

# Roda a aplicação
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)