import streamlit as st
from datetime import datetime
import pandas as pd
import requests

headers = { "accept": "application/json"}

st.write(""" # Votix """)
st.write(""" Consulta por Deputado """)

st.write(""" ## Estado """)

uf = requests.get("https://dadosabertos.camara.leg.br/api/v2/referencias/deputados/siglaUF", headers=headers ).json()

df_uf = pd.DataFrame(uf['dados'])

sigla = st.selectbox(
    'Estado',
     df_uf['sigla'])

st.write(""" ## Deputado """)

deps = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/deputados?siglaUf={sigla}", headers=headers ).json()
df_deps = pd.DataFrame(deps['dados'])

nome = st.selectbox(
    'Estado',
     df_deps['nome'])

dep = df_deps.query(f"nome == '{nome}'").to_dict(orient='list')
print(dep)

dep_id = df_deps.query(f"nome == '{nome}'")['id'].values[0]
print(dep_id)



st.write(""" ### Dados Gerais """)

info = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}", headers=headers ).json()['dados']

status = info['ultimoStatus']

col1, col2, col3 = st.columns(3, gap="small")
with col1:
    st.image(status['urlFoto'])

with col2:
    st.write(info['nomeCivil'])
    idade = ((datetime.now() - pd.to_datetime(info['dataNascimento']))/365.2425).days
    st.write('Nascido em ', info['municipioNascimento'])
    st.write('Data de Nascimento:', info['dataNascimento'])
    st.write('Idade:', str(idade))
    st.write('Escolaridade:', info['escolaridade'])

with col3:
    st.write('Partido: ', status['siglaPartido'])
    if (info['urlWebsite'] != None):
        st.write('Website', info['urlWebsite'])
    if len(info['redeSocial']) > 0:
        st.write('Redes Sociais')
        for rede in info['redeSocial']:
            st.markdown(f"- {rede}")
    
ocupacoes = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/ocupacoes", headers=headers ).json()['dados']


ocupacoes = pd.DataFrame(ocupacoes)
if len(ocupacoes) > 1:
    st.write('Curriculo', ocupacoes)

# st.write(""" ### Atuação """)


# frentes = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/frentes", headers=headers ).json()['dados']

# st.write('frentes', frentes)

st.write(""" ### Proposições """)

props = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/proposicoes?idDeputadoAutor={dep_id}", headers=headers ).json()['dados']
siglasTipo = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/referencias/proposicoes/siglaTipo", headers=headers ).json()['dados']

props = pd.DataFrame(props).merge(pd.DataFrame(siglasTipo), left_on='siglaTipo', right_on='sigla')
st.write('props', props)

st.write(props.pivot_table(index=['siglaTipo'], columns='ano', values='cod', aggfunc='count'))


# st.write(""" ### Votações """)


st.write(""" ### Despesas """)

despesas = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/despesas", headers=headers ).json()['dados']

tab1, tab2, tab3 = st.tabs(['mensal', 'tipo', 'fornecedor'])


df_desp = pd.DataFrame(despesas)
df_desp['valorDocumento'] = df_desp['valorDocumento'].round(2)

with tab1:
    mensal = df_desp.groupby('mes')['valorDocumento','valorGlosa'].sum()
    # mensal
    st.line_chart(mensal, y='valorDocumento')

with tab2:
    tipo = df_desp.groupby('tipoDespesa')['valorDocumento'].sum()
    # tipo
    st.bar_chart(tipo, y='valorDocumento')

with tab3:
    fornecedor = df_desp.groupby('nomeFornecedor')['valorDocumento'].sum()
    # fornecedor
    st.bar_chart(fornecedor,  y='valorDocumento')

