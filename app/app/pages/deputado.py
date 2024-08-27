import streamlit as st
from datetime import datetime
import pandas as pd
import requests
from stqdm import stqdm
from PIL import Image
# from wordcloud import WordCloud, ImageColorGenerator


st.set_page_config(
    page_title='Votix - Deputados',
    page_icon="📊",
    layout='wide'
)

headers = {"User-Agent": "Mozilla/5.0",

           }
headers2 = {"User-Agent": "Mozilla/5.0",
            "Accept": "application/xml"
            }

st.write(""" # Votix 📊 """)
st.write(""" Consulta por Estado """)

st.write(""" ## Estado """)

uf = requests.get(
    "https://dadosabertos.camara.leg.br/api/v2/referencias/deputados/siglaUF", headers=headers).json()

df_uf = pd.DataFrame(uf['dados'])

sigla = st.selectbox(
    'Estado',
    df_uf['sigla'])


# deps = requests.get(
#     f"https://dadosabertos.camara.leg.br/api/v2/deputados?siglaUf={sigla}", headers=headers)
deps = requests.get(
    f"https://dadosabertos.camara.leg.br/api/v2/deputados", headers=headers)
# df_deps = pd.read_xml(deps.content, xpath='.//deputado_')
df_deps = pd.DataFrame(deps.json()['dados'])

df_ids = df_deps.loc[df_deps['siglaUf'] == sigla]['id']

eventos = {}
discursos = {}
despesas = {}
orgaos = {}
resumo = {}

proposicoes = pd.read_csv('https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/deputados/proposicoes/proposicoes-ano.csv',
                          float_precision='round_trip', index_col=0)
proposicoes = proposicoes.query(f'siglaUFAutor == "{sigla}"')
proposicoes['total'] = proposicoes[['2019', '2020',
                                    '2021', '2022']].sum(axis=1).astype('int')
proposicoes = proposicoes.sort_values('total', ascending=False)
votacoes = pd.read_csv('https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/deputados/votacoes/votacoes-ano.csv',
                       float_precision='round_trip', index_col=0)
votacoes = votacoes.query(f'deputado_siglaUf == "{sigla}"')
votacoes['total'] = votacoes[['2019', '2020',
                              '2021', '2022']].sum(axis=1).astype('int')
votacoes = votacoes.sort_values('total', ascending=False)

st.info('Proposições por ano')
st.write(proposicoes)

st.info('Votações por ano')
st.write(votacoes)

st.write(""" ## Deputado """)
nome = st.selectbox(
    'Nome',
    df_deps['nome'])

dep = df_deps.query(f"nome == '{nome}'").to_dict(orient='list')
print(dep)

dep_id = df_deps.query(f"nome == '{nome}'")['id'].values[0]
print(dep_id)


st.write(""" ### Dados Gerais """)

info = requests.get(
    f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}", headers=headers).json()['dados']

status = info['ultimoStatus']

col1, col2, col3 = st.columns(3, gap="small")
with col1:
    st.image(status['urlFoto'])

with col2:
    st.write(info['nomeCivil'])
    st.write('Partido: ', status['siglaPartido'])
    idade = (
        (datetime.now() - pd.to_datetime(info['dataNascimento']))/365.2425).days
    st.write('Nascido em ', info['municipioNascimento'])
    st.write('Data de Nascimento:', info['dataNascimento'])
    st.write('Idade:', str(idade))
    st.write('Escolaridade:', info['escolaridade'])

with col3:

    if (info['urlWebsite'] != None):
        st.write('Website', info['urlWebsite'])
    if len(info['redeSocial']) > 0:
        st.write('Redes Sociais')
        for rede in info['redeSocial']:
            st.markdown(f"- {rede}")

ocupacoes = requests.get(
    f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/ocupacoes", headers=headers).json()['dados']


ocupacoes = pd.DataFrame(ocupacoes)
if len(ocupacoes) > 1:
    st.info(""" Curriculo """)
    st.write(ocupacoes)

# st.write(""" ### Atuação """)


# frentes = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/frentes", headers=headers ).json()['dados']

# st.write('frentes', frentes)

st.info(""" Discursos """)

discursos = pd.DataFrame(requests.get(
    f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/discursos?idLegislatura=56&itens=100", headers=headers).json()['dados'])
st.write('Quantidade: ', str(len(discursos)))

if len(discursos) > 1:
    st.write("".join(discursos.sumario.to_list()).split())
#     if st.button('Gerar nuvem'):
#         words = "".join(discursos.sumario.to_list())
#         # st.write(words)
#         STOPWORDS = requests.get(
#             'https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/stopwords.txt').text.split(' ')
#         wordcloud = WordCloud(
#             stopwords=STOPWORDS, background_color='black', width=800, height=400).generate(words)
#         st.image(wordcloud.to_image())
else:
    st.write('Não há dados.')


st.info(""" Proposições """)

props = requests.get(
    f"https://dadosabertos.camara.leg.br/api/v2/proposicoes?idDeputadoAutor={dep_id}", headers=headers).json()['dados']
siglasTipo = requests.get(
    f"https://dadosabertos.camara.leg.br/api/v2/referencias/proposicoes/siglaTipo", headers=headers).json()['dados']

props = pd.DataFrame(props).merge(pd.DataFrame(siglasTipo),
                                  left_on='siglaTipo', right_on='sigla')
st.write(props)

st.write(props.pivot_table(index=['siglaTipo'],
         columns='ano', values='cod', aggfunc='count'))


# st.write(""" ### Votações """)


# st.write(""" ### Despesas """)

# despesas = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/despesas", headers=headers ).json()['dados']

# tab1, tab2, tab3 = st.tabs(['mensal', 'tipo', 'fornecedor'])


# df_desp = pd.DataFrame(despesas)
# df_desp['valorDocumento'] = df_desp['valorDocumento'].round(2)

# with tab1:
#     mensal = df_desp.groupby('mes')['valorDocumento','valorGlosa'].sum()
#     # mensal
#     st.line_chart(mensal, y='valorDocumento')

# with tab2:
#     tipo = df_desp.groupby('tipoDespesa')['valorDocumento'].sum()
#     # tipo
#     st.bar_chart(tipo, y='valorDocumento')

# with tab3:
#     fornecedor = df_desp.groupby('nomeFornecedor')['valorDocumento'].sum()
#     # fornecedor
#     st.bar_chart(fornecedor,  y='valorDocumento')
