# Monitoramento e Análise de Estações SMP

Este projeto tem como objetivo, realizar consultas, gerar visualizações interativas utilizando o Streamlit. Ele também permite consultar estações próximas a uma localização específica com base em latitude, longitude e raio de busca.

📋 Funcionalidades

    Consulta de Dados: Permite a consulta dos dados filtrados por estado (UF) e cidade.
    Visualizações Interativas: Gera mapas e gráficos interativos utilizando Plotly, incluindo:
        * Mapa de estações por operadora com cores personalizadas.
        * Gráficos de barras mostrando o total de estações por operadora e geração.
    Consulta de Estações Próximas: Permite ao usuário consultar as estações mais próximas a uma localização fornecida, com a distância calculada entre o ponto informado e as estações.

🛠️ Tecnologias Utilizadas

    Python: Linguagem principal do projeto.
    pandas: Para manipulação de dados.
    sqlite3: Para interação com o banco de dados SQLite.
    Streamlit: Para criação da interface interativa.
    Plotly: Para visualizações gráficas e mapas interativos.
    geopy: Para calcular a distância entre pontos geográficos.

📂 Estrutura do Projeto

        monitoramento_estacoes/
      ├── app.py              # Código principal para tratamento de dados e interface com Streamlit
      ├── estacoes_smp.db     # Banco de dados SQLite com as estações
      ├── src/                # Arquivos fontes, como o CSV de entrada
      │   └── Estacoes_SMP.csv  # Arquivo CSV com os dados das estações
      ├── update_log.txt      # Arquivo de log para verificar a necessidade de recriar o banco
      ├── requirements.txt    # Dependências do projeto
      ├── README.md           # Documentação do projeto

📥 Como Rodar o Projeto

    0. Download dos dados:
        https://informacoes.anatel.gov.br/paineis/outorga-e-licenciamento/estacoes-do-smp
    
    1. Clone este repositório:
        git clone https://github.com/benutte/Localizacao-Operadora.git
    
    2. Crie e ative um ambiente virtual:
        python -m venv .venv
        source .venv/bin/activate  # Para Linux/Mac
        .venv\Scripts\activate     # Para Windows

    3. Instale as dependências:
        pip install -r requirements.txt
    
    4. Execute o aplicativo Streamlit:
        streamlit run app.py

    5. Acesse o aplicativo no seu navegador, geralmente disponível em http://localhost:8501.

🛡️ Aviso Legal

    Este projeto foi desenvolvido para fins educacionais e de análise de dados. Certifique-se de utilizar os dados de acordo com as políticas de uso e privacidade dos dados utilizados.

    📧 Contato

    Se tiver dúvidas ou sugestões, entre em contato:

    Email: benutte20@gmail.com
