import streamlit as st
from datetime import datetime
import pandas as pd
import requests

headers = { "accept": "application/json",
           "User-Agent": "Mozilla/5.0"
           }

st.write(""" # Votix """)
st.write(""" ## Legislação """)
st.write("O que um deputado faz? Essa e outras repostas.")


cargos = pd.read_json('./data/cargos_descricao.json', encoding='utf-8')

cargo = st.selectbox(
    'Cargo',
     cargos['nome'],3)

descricao = cargos.query(f'nome == "{cargo}"')

st.write('### Deveres')
for v in descricao['competencias']:
    for i in v:
        st.write(f"{i}")