import streamlit as st
from keplergl import KeplerGl
import pandas as pd

# Exemplo de dataframe
data = {
    'Latitude': [51.5074, 48.8566, 40.7128],
    'Longitude': [-0.1278, 2.3522, -74.0060],
    'Operadora': ['Operadora 1', 'Operadora 2', 'Operadora 3'],
    'Endereço': ['Endereço 1', 'Endereço 2', 'Endereço 3']
}
df = pd.DataFrame(data)

# Criação de um mapa KeplerGl
kepler_map = KeplerGl(height=600)

# Adicionando os dados no mapa
kepler_map.add_data(data=df, name="Estações")

# Exibir o mapa
st.subheader("Mapa Interativo com Kepler.gl")
st.write(kepler_map)
