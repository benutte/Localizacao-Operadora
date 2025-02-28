import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import os
from datetime import datetime
from geopy.distance import geodesic

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

    # Verifica se é necessário recriar o banco
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

    # Configurar filtros para UF
    uf_filter = st.sidebar.multiselect(
        "Selecione os estados (UF):",
        options=query_db("SELECT DISTINCT UF FROM estacoes")['UF'].tolist()
    )

    # Configura filtros para Cidade
    cidade_filter = st.sidebar.multiselect(
        "Selecione as cidades:",
        options=query_db("SELECT DISTINCT `Município-UF` FROM estacoes")["Município-UF"].tolist()
    )

    # Carregar dados filtrados por UF
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

    # Filtra os dados por cidade se algum filtro de cidade for selecionado
    if cidade_filter:
        filtered_df = filtered_df[filtered_df['Municipio'].isin(cidade_filter)]

    # Limita a quantidade de linhas exibidas
    max_rows = st.sidebar.slider("Máximo de linhas exibidas:", min_value=100, max_value=5000, step=100, value=1000)
    filtered_df = filtered_df.head(max_rows)
    # Defina as colunas desejadas
    colunas_desejadas = ['UF', 'Municipio', 'Bairro', 'Endereço', 'Tecnologia', 'Operadora', 'Geração', 'FreqRxMHz', 'FreqTxMHz']

    # Filtra as colunas desejadas no DataFrame
    filtered_df_desejado = filtered_df[colunas_desejadas]

    # Tabela Interativa
    st.subheader("Tabela de Estações")
    st.dataframe(filtered_df_desejado)


    # Mapa Interativo com Estil

    # Definindo as cores específicas para cada operadora
    cores_operadoras = {
        "CLARO": "#FF0B2C",
        "VIVO": "#741B7C",
        "TIM": "#732BF5",
        "BRISANET": "#FAB133",
        "ALGAR": "#7E84F7",
        "GIGA+": "#27B823",
        "UNIFIQUE TELECOMUNICACOES S/A": "#0023F5",
        "SERCOMTEL": "#746FF5"
    }

    # Mapa Interativo com cores personalizadas
    st.subheader("Mapa Personalizado por Operadora")
    fig = px.scatter_mapbox(
        filtered_df,
        lat='Latitude',
        lon='Longitude',
        color='Operadora',  # Variável categórica
        hover_name='Endereço',
        hover_data=['Bairro', 'Tecnologia', 'Geração'],
        title="Localização das Operadoras",
        mapbox_style="carto-positron",
        color_discrete_map=cores_operadoras  # Aplicando cores personalizadas
    )
    st.plotly_chart(fig)

    # Gráfico de Colunas com Operadoras
    st.subheader("Gráfico de Operadoras")
    operadoras_count = filtered_df.groupby('Operadora', as_index=False)['Número Estação'].count()
    fig_operadoras = px.bar(
        operadoras_count,
        x='Operadora',
        y='Número Estação',
        labels={'Operadora': 'Operadora', 'Número Estação': 'Total de Estações'},
        title="Total de Estações por Operadora",
        color='Operadora',  # Usando a coluna 'Operadora' para a cor
        color_discrete_map=cores_operadoras  # Aplicando as cores personalizadas
    )
    st.plotly_chart(fig_operadoras)

    # Gráfico de Colunas com Gerações
    st.subheader("Gráfico de Gerações")
    geracoes_count = filtered_df.groupby('Geração', as_index=False)['Número Estação'].count()
    fig_geracoes = px.bar(
        geracoes_count,
        x='Geração',
        y='Número Estação',
        labels={'Geração': 'Geração', 'Número Estação': 'Total de Estações'},
        title="Total de Estações por Geração"
    )
    st.plotly_chart(fig_geracoes)

    # Entradas para o usuário
    st.sidebar.subheader("Consulta de Estações mais Próximas")

    # Entradas para latitude e longitude com base na precisão (número de casas decimais)
    precisao_lat = st.sidebar.slider("Precisão para Latitude", min_value=1, max_value=10, value=6)
    precisao_lon = st.sidebar.slider("Precisão para Longitude", min_value=1, max_value=10, value=6)

    # Número de casas decimais ajustável
    lat_usuario = st.sidebar.number_input("Latitude", min_value=-90.0, max_value=90.0, step=10**(-precisao_lat), format=f"%.{precisao_lat}f")
    lon_usuario = st.sidebar.number_input("Longitude", min_value=-180.0, max_value=180.0, step=10**(-precisao_lon), format=f"%.{precisao_lon}f")

    # Raio em km
    raio_km = st.sidebar.number_input("Raio (km)", min_value=1, max_value=500, step=1)


    # Função para calcular a distância entre dois pontos geográficos
    def calcular_distancia(lat1, lon1, lat2, lon2):
        """Calcula a distância em quilômetros entre dois pontos geográficos."""
        p1 = (lat1, lon1)
        p2 = (lat2, lon2)
        distancia = geodesic(p1, p2).km
        return distancia

    # Função para encontrar as estações mais próximas
    def encontrar_estacoes_proximas(lat_usuario, lon_usuario, raio_km, filtered_df):
        # Calculando a distância de cada estação para o usuário
        filtered_df['Distancia'] = filtered_df.apply(
            lambda row: calcular_distancia(lat_usuario, lon_usuario, row['Latitude'], row['Longitude']),
            axis=1
        )
        
        # Encontra as estações dentro do raio
        estacoes_proximas = filtered_df[filtered_df['Distancia'] <= raio_km]
        
        if not estacoes_proximas.empty:
            # Ordena as estações mais próximas pela distância
            estacoes_proximas = estacoes_proximas.sort_values(by='Distancia')  # Ordena pela distância
            # Seleciona apenas as colunas desejadas
            colunas_desejadas.append('Distancia')
            estacoes_proximas = estacoes_proximas[colunas_desejadas]
            return estacoes_proximas
        return None

    # Encontra e mostrar as estações mais próximas
    if lat_usuario and lon_usuario and raio_km:
        estacoes_proximas = encontrar_estacoes_proximas(lat_usuario, lon_usuario, raio_km, filtered_df)
        if estacoes_proximas is not None:
            st.subheader(f"As estações mais próximas dentro de {raio_km} km")
            st.dataframe(estacoes_proximas)
        else:
            st.warning(f"Nenhuma estação encontrada dentro de {raio_km} km.")
    else:
        st.warning("Por favor, insira a latitude, longitude e raio para buscar as estações.")
