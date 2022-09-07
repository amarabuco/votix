import streamlit as st
from datetime import datetime
import pandas as pd
import requests

st.set_page_config(
    page_title='Votix - Partidos',
    page_icon="📊",
    layout='wide'
)

headers = { "accept": "application/json",
           "User-Agent": "Mozilla/5.0"
           }


st.write(""" # 📊  Votix """)
st.write(""" ## Partidos - Visão Geral """)
st.write("Conheça as estatísticas de candidaturas por Estado e Cargo.")

uf = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]

sigla = st.selectbox(
    'Estado',
     uf, 15)

cargos = pd.read_json('https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/cargos.json')
# cargos = pd.read_json('/Volumes/EXT/myApps/votix/app/app/data/cargos.json')

cargo = st.selectbox(
    'Cargo',
     cargos['nome'],3)

cargo_id = cargos.query(f'nome == "{cargo}"').values[0,0]

partidos = pd.read_json('https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/partidos.json')

st.write(f""" ## {sigla} | {cargo}""")

# f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos"
candidatos_2018 = requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2018/{sigla}/2022802018/{cargo_id}/candidatos", headers=headers ).json()['candidatos']
candidatos = requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos", headers=headers ).json()['candidatos']


candidatos_df_2018 = pd.DataFrame(candidatos_2018) 
candidatos_df_2018['ANO'] = '2018'
candidatos_df_2018['PARTIDO'] = candidatos_df_2018['partido'].apply(lambda x:  x['sigla'])
candidatos_df = pd.DataFrame(candidatos)
candidatos_df['PARTIDO'] = candidatos_df['partido'].apply(lambda x:  x['sigla'])
candidatos_df['ANO'] = 2022
# candidatos_df_2018_eleitos = candidatos_df_2018.loc[(candidatos_df_2018.descricaoTotalizacao == 'Eleito')]
candidatosdf = pd.concat([candidatos_df_2018, candidatos_df_2018_eleitos, candidatos_df], axis=0)

st.write("### Candidatos")
candidatosdf

colig = candidatos_df[['nomeColigacao', 'PARTIDO']].drop_duplicates()
st.write("### Coligações")
st.dataframe(colig.sort_values('nomeColigacao'), width=800)

cdf = candidatosdf.pivot_table(index=['PARTIDO'], columns=['ANO'], values='id', aggfunc='count').fillna(0)
cdf = cdf.sort_values(cdf.columns[-1], ascending=False)
#cdf = candidatos_df.pivot_table(index='PARTIDO', columns='descricaoSituacao', values='id', aggfunc='count', margins=True).fillna(0).sort_values('All', ascending=False)
st.write("### Estatísticas", )
st.dataframe(cdf, width=1000)

st.write("### Quociente eleitoral")
st.write('...' )

#st.write(cdf.merge(partidos, left_on='PARTIDO', right_on='sigla')['posicao','all'])

