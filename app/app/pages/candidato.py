import streamlit as st
import plotly.express as px
from datetime import datetime
import pandas as pd
import requests
import urllib.parse

def get_score(df):
    escolaridade = ['Lê e escreve', 'Ensino Fundamental incompleto', 'Ensino Fundamental completo', 'Ensino Médio incompleto', 'Ensino Médio completo', 'Superior incompleto','Superior completo']
    escol_pts = escolaridade.index(df['grauInstrucao'])
    escol_pts = (escol_pts - 0)/(len(escolaridade) - 0) * 5
    
    idades = [20,30,40,50,60,100]
    idade = ((datetime.now() - pd.to_datetime(df['dataDeNascimento']))/365.2425).days
    score_idade = 0
    for k, v in enumerate(idades):
        if (idade < v):
            score_idade = k
            break        
    
    cargos = ['Nenhum','Vereador', 'Deputado Estadual', 'Deputado Federal', 'Vice-Prefeito','Prefeito', 'Senador', 'Governador']
    eleicoes = pd.DataFrame(df['eleicoesAnteriores'])
    eleicoes['cargo_pts'] = eleicoes['cargo'].apply(lambda x: cargos.index(x))
    eleito = eleicoes.query(f"situacaoTotalizacao == 'Eleito' or situacaoTotalizacao == 'Eleito por QP'")
    if len(eleito) == 0:
        cargo_pts = 0
    else:
        cargo_pts = eleito['cargo_pts'].max()
    
    cargo_pts = (cargo_pts - 0)/(len(cargos) - 0) * 5
    
    # eleicoes = len([1 for el in df['eleicoesAnteriores'] if el == 'Eleito'])
    return {'escolaridade': escol_pts, 'idade': score_idade, 'politica': cargo_pts}

headers = { "accept": "application/json",
           "User-Agent": "Mozilla/5.0"
           }

st.write(""" # Votix """)
st.write(""" ## Candidato """)
st.write("Saiba as informações e pontuação de cada candidato.")

st.write(""" ## Estado """)

uf = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]

sigla = st.selectbox(
    'Estado',
     uf)
cargos = pd.read_json('./data/cargos.json')
# cargos = pd.read_json('/Volumes/EXT/myApps/votix/app/app/data/cargos.json')

cargo = st.selectbox(
    'Cargo',
     cargos['nome'],0)

cargo_id = cargos.query(f'nome == "{cargo}"').values[0,0]

# partidos = pd.read_json('./data/partidos.json')

# partidos = partidos.sort_values(by='sigla')
# partido = st.selectbox(
#     'Partido',
#      partidos['sigla'])

# partido_id = partidos.query(f'sigla == "{partido}"').values[0,0]

# st.write('Estado: ', sigla, 'Cargo: ', cargo, 'Partido:', partido)

# partido_info =  requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/prestador/consulta/partido/2040602022/2022/{sigla}/3/{partido_id}", headers=headers ).json()

# partido_info

st.write(f""" ## {sigla} | {cargo}""")


# f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos"
candidatos = requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos", headers=headers ).json()['candidatos']

candidatos_df = pd.DataFrame(candidatos)
candidatos_df['PARTIDO'] = candidatos_df['partido'].apply(lambda x:  x['sigla'])

candidatos_partido = candidatos_df
# candidatos_partido = candidatos_df.query(f'PARTIDO == "{partido}"')

nome = st.selectbox(
    'Candidato',
     candidatos_partido['nomeUrna'])

cid = candidatos_partido.loc[candidatos_partido['nomeUrna'] == nome].values[0,0]

candidato = requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/buscar/2022/{sigla}/2040602022/candidato/{cid}", headers=headers ).json()
partido = candidato['partido']['sigla']
candidato['idade'] = ((datetime.now() - pd.to_datetime(candidato['dataDeNascimento']))/365.2425).days

props = ["grauInstrucao", "descricaoTotalizacao", "eleicoesAnteriores", "dataDeNascimento"]
candidato_resumo = pd.Series({p:candidato[p] for p in props}, name=candidato['id'])

with st.container():
    st.image(f"https://divulgacandcontas.tse.jus.br/divulga/images/partidos/{partido}.jpg", width=128)
    partido
    

col1, col2, col3 = st.columns(3)
with col1:
    st.image(candidato['fotoUrl'])
    st.write('Reeleição:', str(candidato['st_REELEICAO']))
    st.write("https://pt.wikipedia.org/w/index.php?search={}".format(urllib.parse.quote(candidato['nomeCompleto'])))
with col2:
    st.write('### Dados ')
    st.write('Nome:', candidato['nomeCompleto'])
    st.write('Estado Civil:', candidato['descricaoEstadoCivil'])
    st.write('Raça:', candidato['descricaoCorRaca'])
    st.write('Idade:', str(candidato['idade']))
    st.write('Escolaridade:', candidato['grauInstrucao'])
    st.write('Ocupação:', candidato['ocupacao'])
    st.write('Patrimônio:', '{:,.2f}'.format(candidato['totalDeBens']))
with col3:
    st.write('### Redes Sociais')
    for link in candidato['sites']:
        st.write(f'* {link}')
    
st.write("### Histórico de Eleições")
eleicoes = pd.DataFrame(candidato['eleicoesAnteriores'])
st.write(eleicoes[['nrAno', 'nomeUrna', 'partido','cargo', 'situacaoTotalizacao']])

# candidato
# candidato_resumo
st.write("### Pontuação")
score = pd.Series(get_score(candidato_resumo)).reset_index()
st.write(score)
st.write('Nota:', str(score[0].mean().round(2)))

fig = px.line_polar(score,  r=0, theta='index', line_close=True, range_r=[0,5])
fig.update_traces(fill='toself')

st.plotly_chart(fig, use_container_width=True)


