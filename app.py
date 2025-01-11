import pandas as pd
import sqlite3

def load_and_clean_data(file_path: str) -> pd.DataFrame:
    """Carrega e limpa os dados do CSV"""
    # Carregar dados com o ajuste para lidar com tipos mistos
    df = pd.read_csv(file_path, sep=';', low_memory=False)
    
    # Colunas a serem mantidas
    cols = [
        'Número Estação', 'FreqTxMHz', 'FreqRxMHz', 'Designação Emissão', 'Tecnologia',
        'Latitude', 'Longitude', 'Latitude decimal', 'Longitude decimal', 'EnderecoEstacao',
        'EndBairro', 'EndNumero', 'EndComplemento', 'Cep', 'Empresa Estação', 'Faixa Estação',
        'Subfaixa Estação', 'Geração', 'Município-UF', 'UF'
    ]
    df = df[cols]
    
    # Função para limpar strings (remover espaços em branco)
    def clean_string_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        df[column_name] = df[column_name].astype(str).str.strip()
        return df

    # Limpar todas as colunas de string
    for col in df.select_dtypes(include=['object']).columns:
        df = clean_string_column(df, col)
    
    # Formatar a coluna 'Número Estação' para numérico com valores nulos
    df['Número Estação'] = pd.to_numeric(df['Número Estação'], errors='coerce').astype('Int64')

    return df

def save_to_sqlite(df: pd.DataFrame, db_name: str, table_name: str):
    """Salva o DataFrame em um banco SQLite"""
    conn = sqlite3.connect(db_name)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

# Caminho do arquivo CSV
file_path = 'src/Estacoes_SMP.csv'

# Carregar e limpar os dados
df = load_and_clean_data(file_path)

# Salvar os dados no banco SQLite
save_to_sqlite(df, 'estacoes_smp.db', 'estacoes')

print("Base de dados salva com sucesso no SQLite!")
