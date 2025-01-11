import pandas as pd
import sqlite3

# Carregar os dados com o ajuste para lidar com os tipos mistos
df = pd.read_csv('src/Estacoes_SMP.csv', sep=';', low_memory=False)

# Selecionar apenas as colunas necessárias
df = df[['Número Estação', 'FreqTxMHz', 'FreqRxMHz', 'Designação Emissão', 'Tecnologia',
         'Latitude', 'Longitude', 'Latitude decimal', 'Longitude decimal', 'EnderecoEstacao',
         'EndBairro', 'EndNumero', 'EndComplemento', 'Cep', 'Empresa Estação', 'Faixa Estação',
         'Subfaixa Estação', 'Geração', 'Município-UF', 'UF']]

# Formatar as colunas conforme solicitado
df['Número Estação'] = pd.to_numeric(df['Número Estação'], errors='coerce').astype('Int64')
df['FreqTxMHz'] = df['FreqTxMHz'].astype(str).str.strip()
df['FreqRxMHz'] = df['FreqRxMHz'].astype(str).str.strip()
df['Designação Emissão'] = df['Designação Emissão'].astype(str).str.strip()
df['Tecnologia'] = df['Tecnologia'].astype(str).str.strip()
df['Latitude'] = df['Latitude'].astype(str).str.strip()
df['Longitude'] = df['Longitude'].astype(str).str.strip()
df['Latitude decimal'] = df['Latitude decimal'].astype(str).str.strip()
df['Longitude decimal'] = df['Longitude decimal'].astype(str).str.strip()
df['EnderecoEstacao'] = df['EnderecoEstacao'].astype(str).str.strip()
df['EndBairro'] = df['EndBairro'].astype(str).str.strip()
df['EndNumero'] = df['EndNumero'].astype(str).str.strip()
df['EndComplemento'] = df['EndComplemento'].astype(str).str.strip()
df['Cep'] = df['Cep'].astype(str).str.strip()
df['Empresa Estação'] = df['Empresa Estação'].astype(str).str.strip()
df['Faixa Estação'] = df['Faixa Estação'].astype(str).str.strip()
df['Subfaixa Estação'] = df['Subfaixa Estação'].astype(str).str.strip()
df['Geração'] = df['Geração'].astype(str).str.strip()
df['Município-UF'] = df['Município-UF'].astype(str).str.strip()
df['UF'] = df['UF'].astype(str).str.strip()

# Conectar ao banco de dados SQLite (criar se não existir)
conn = sqlite3.connect('estacoes_smp.db')

# Salvar o DataFrame como uma tabela no banco de dados
df.to_sql('estacoes', conn, if_exists='replace', index=False)

# Fechar a conexão
conn.close()

print("Base de dados salva com sucesso no SQLite!")
