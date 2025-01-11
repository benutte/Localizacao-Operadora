import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import os
from datetime import datetime

# Função para tratar e salvar os dados no banco
def tratar_dados(csv_path, db_path='estacoes_smp.db'):
    """Trata os dados do CSV e salva no banco de dados SQLite."""
    # Carregar os dados
    df = pd.read_csv(csv_path, sep=';', low_memory=False)

    # Selecionar colunas relevantes
    colunas_relevantes = [
        'UF', 'Município-UF', 'EndBairro', 'EnderecoEstacao', 'Tecnologia',
        'Empresa Estação', 'Geração', 'FreqRxMHz', 'FreqTxMHz',
        'Latitude decimal', 'Longitude decimal', 'Número Estação'
    ]
    df = df[colunas_relevantes]

    # Renomear colunas
    df.rename(columns={
        'EndBairro': 'Bairro',
        'EnderecoEstacao': 'Endereço',
        'Empresa Estação': 'Operadora',
    }, inplace=True)

    # Formatar strings
    for col in ['UF', 'Município-UF', 'Bairro', 'Endereço', 'Tecnologia', 'Operadora', 'Geração']:
        df[col] = df[col].astype(str).str.strip()

    # Converter para tipos numéricos
    df['FreqRxMHz'] = pd.to_numeric(df['FreqRxMHz'], errors='coerce')
    df['FreqTxMHz'] = pd.to_numeric(df['FreqTxMHz'], errors='coerce')
    df['Latitude decimal'] = pd.to_numeric(df['Latitude decimal'], errors='coerce')
    df['Longitude decimal'] = pd.to_numeric(df['Longitude decimal'], errors='coerce')
    df['Número Estação'] = pd.to_numeric(df['Número Estação'], errors='coerce').astype('Int64')

    # Remover linhas inválidas
    df.dropna(subset=['UF', 'Município-UF', 'Bairro', 'Endereço', 'Latitude decimal', 'Longitude decimal'], inplace=True)

    # Salvar no banco SQLite
    conn = sqlite3.connect(db_path)
    df.to_sql('estacoes', conn, if_exists='replace', index=False)
    conn.close()
    print("Dados tratados e salvos no banco SQLite com sucesso!")

# Função para verificar se o banco precisa ser recriado
def precisa_recriar_banco(log_path='update_log.txt'):
    """Verifica se o banco de dados precisa ser recriado com base na última data de atualização."""
    hoje = datetime.now().date()
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            ultima_atualizacao = f.read().strip()
        if ultima_atualizacao == str(hoje):
            return False  # Já foi atualizado hoje
    # Atualizar o arquivo com a data de hoje
    with open(log_path, 'w') as f:
        f.write(str(hoje))
    return True

# Main
if __name__ == "__main__":
    # Caminhos para o CSV, banco e log
    csv_path = 'src/Estacoes_SMP.csv'
    db_path = 'estacoes_smp.db'
    log_path = 'update_log.txt'

    # Verificar se é necessário recriar o banco
    if precisa_recriar_banco(log_path):
        st.info("Atualizando o banco de dados com os dados mais recentes...")
        tratar_dados(csv_path, db_path)
    else:
        st.success("O banco já foi atualizado hoje. Pulando recriação.")

    # Streamlit Interface
    st.title("Análise de Estações SMP")
    st.sidebar.header("Filtros")

    # Função para consultar o banco de dados
    @st.cache_data
    def query_db(query: str, db_path: str = 'estacoes_smp.db'):
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    # Configurar filtros
    uf_filter = st.sidebar.multiselect(
        "Selecione os estados (UF):",
        options=query_db("SELECT DISTINCT UF FROM estacoes")['UF'].tolist()
    )

    # Carregar dados filtrados
    if uf_filter:
        query = f"""
        SELECT 
            UF, 
            `Município-UF` AS Municipio, 
            Bairro, 
            Endereço, 
            Tecnologia, 
            Operadora, 
            Geração, 
            FreqRxMHz, 
            FreqTxMHz, 
            `Latitude decimal` AS Latitude, 
            `Longitude decimal` AS Longitude,
            `Número Estação`
        FROM estacoes
        WHERE UF IN ({','.join([f"'{uf}'" for uf in uf_filter])})
        """
        filtered_df = query_db(query)
    else:
        st.info("Selecione ao menos um estado (UF) para carregar os dados.")
        st.stop()

    # Limitar a quantidade de linhas exibidas
    max_rows = st.sidebar.slider("Máximo de linhas exibidas:", min_value=100, max_value=5000, step=100, value=1000)
    filtered_df = filtered_df.head(max_rows)

    # Tabela Interativa
    st.subheader("Tabela de Estações")
    st.dataframe(filtered_df)

    # Mapa Interativo
    st.subheader("Mapa com as Operadoras")
    fig = px.scatter_geo(
        filtered_df,
        lat='Latitude',
        lon='Longitude',
        color='Operadora',
        hover_name='Endereço',
        hover_data=['Bairro', 'Tecnologia', 'Geração'],
        title="Localização das Operadoras"
    )
    st.plotly_chart(fig)

    # Gráfico de Colunas com Operadoras
    st.subheader("Gráfico de Operadoras")
    operadoras_count = filtered_df.groupby('Operadora', as_index=False)['Número Estação'].sum()
    fig_operadoras = px.bar(
        operadoras_count,
        x='Operadora',
        y='Número Estação',
        labels={'Operadora': 'Operadora', 'Número Estação': 'Total de Estações'},
        title="Total de Estações por Operadora"
    )
    st.plotly_chart(fig_operadoras)

    # Gráfico de Colunas com Gerações
    st.subheader("Gráfico de Gerações")
    geracoes_count = filtered_df.groupby('Geração', as_index=False)['Número Estação'].sum()
    fig_geracoes = px.bar(
        geracoes_count,
        x='Geração',
        y='Número Estação',
        labels={'Geração': 'Geração', 'Número Estação': 'Total de Estações'},
        title="Total de Estações por Geração"
    )
    st.plotly_chart(fig_geracoes)
