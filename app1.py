import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import os

# Função para carregar e limpar os dados
def load_and_clean_data(file_path: str) -> pd.DataFrame:
    """Carrega e limpa os dados do CSV"""
    df = pd.read_csv(file_path, sep=';', low_memory=False)
    
    # Colunas a serem mantidas
    cols = [
        'Número Estação', 'FreqTxMHz', 'FreqRxMHz', 'Designação Emissão', 'Tecnologia',
        'Latitude', 'Longitude', 'Latitude decimal', 'Longitude decimal', 'EnderecoEstacao',
        'EndBairro', 'EndNumero', 'EndComplemento', 'Cep', 'Empresa Estação', 'Faixa Estação',
        'Subfaixa Estação', 'Geração', 'Município-UF', 'UF'
    ]
    df = df[cols]
    
    # Renomear as colunas conforme solicitado
    df = df.rename(columns={
        'EnderecoEstacao': 'Endereço',
        'EndBairro': 'Bairro',
        'Empresa Estação': 'Operadora'
    })
    
    # Limpar todas as colunas de string
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Formatar a coluna 'Número Estação' para numérico com valores nulos
    df['Número Estação'] = pd.to_numeric(df['Número Estação'], errors='coerce').astype('Int64')

    # Converter latitude e longitude decimal para float
    df['Latitude decimal'] = pd.to_numeric(df['Latitude decimal'], errors='coerce')
    df['Longitude decimal'] = pd.to_numeric(df['Longitude decimal'], errors='coerce')

    return df

# Função para salvar os dados no banco SQLite
def save_to_sqlite(df: pd.DataFrame, db_name: str, table_name: str):
    """Salva o DataFrame em um banco SQLite, se o banco não existir"""
    if not os.path.exists(db_name):  # Verifica se o banco de dados já existe
        conn = sqlite3.connect(db_name)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        st.success("Base de dados salva com sucesso no SQLite!")
    else:
        st.warning("Banco de dados já existe. Não foi necessário criar novamente.")

# Caminho do arquivo CSV
file_path = 'src/Estacoes_SMP.csv'

# Carregar os dados
df = load_and_clean_data(file_path)

# Salvar os dados no banco SQLite apenas se o banco não existir
save_to_sqlite(df, 'estacoes_smp.db', 'estacoes')

# Streamlit Dashboard
st.title("Dashboard de Estações SMP")

# Filtros para reduzir os dados
st.sidebar.header("Filtros")
uf_filter = st.sidebar.multiselect("Selecione os estados (UF):", options=df['UF'].unique(), default=df['UF'].unique())
operadora_filter = st.sidebar.multiselect("Selecione as Operadoras:", options=df['Operadora'].unique(), default=df['Operadora'].unique())

# Aplicar filtros
filtered_df = df[(df['UF'].isin(uf_filter)) & (df['Operadora'].isin(operadora_filter))]

# Limitar os dados carregados
max_rows = st.sidebar.slider("Máximo de linhas exibidas:", min_value=100, max_value=5000, step=100, value=1000)
filtered_df = filtered_df.sample(n=min(max_rows, len(filtered_df)), random_state=42)

# Exibir a tabela com as colunas selecionadas
st.subheader("Tabela de Estações")
st.dataframe(filtered_df[['UF', 'Município-UF', 'Bairro', 'Endereço', 'Tecnologia', 'Operadora', 'Geração', 'FreqRxMHz', 'FreqTxMHz']])

# Criar o mapa com as operadoras usando longitude e latitude decimal
st.subheader("Mapa com as Operadoras")
fig = px.scatter_geo(filtered_df,
                     lat='Latitude decimal',
                     lon='Longitude decimal',
                     color='Operadora',
                     hover_name='Endereço',
                     hover_data=['Bairro', 'Tecnologia', 'Geração'],
                     title="Localização das Operadoras")
st.plotly_chart(fig)

# Gráfico de colunas com as Operadoras
st.subheader("Gráfico de Operadoras")
operadoras_count = filtered_df.groupby('Operadora', as_index=False)['Número Estação'].sum()
fig_operadoras = px.bar(operadoras_count,
                        x='Operadora',
                        y='Número Estação',
                        labels={'Operadora': 'Operadora', 'Número Estação': 'Total de Estações'},
                        title="Total de Estações por Operadora")
st.plotly_chart(fig_operadoras)

# Gráfico de colunas com as Gerações
st.subheader("Gráfico de Gerações")
geracoes_count = filtered_df.groupby('Geração', as_index=False)['Número Estação'].sum()
fig_geracoes = px.bar(geracoes_count,
                      x='Geração',
                      y='Número Estação',
                      labels={'Geração': 'Geração', 'Número Estação': 'Total de Estações'},
                      title="Total de Estações por Geração")
st.plotly_chart(fig_geracoes)
