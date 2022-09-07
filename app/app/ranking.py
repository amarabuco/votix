import streamlit as st
from datetime import datetime
import pandas as pd
import requests
from utils import get_score
from stqdm import stqdm
import webbrowser

st.set_page_config(
    page_title='Votix - Ranking',
    page_icon="📊",
    layout='wide'
)

headers = { "accept": "application/json",
           "User-Agent": "Mozilla/5.0"
           }


st.write(""" # 📊  Votix """)
st.success(""" ## Ranking """)
st.write(""" Veja a pontuação dos candidatos. """)

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

sexo = st.selectbox(
    'sexo',
     ['TODOS','FEM.', 'MASC.'])

cor = st.selectbox(
    'cor',
     ['TODOS','PRETA', 'PARDA', 'BRANCA'])

reeleicao = st.selectbox(
    'Reeleição',
     ['TODOS','Sim', 'Não'])

st_rel = {'Sim': True, 'Não': False, 'TODOS':'TODOS'}
reeleicao = st_rel[reeleicao]

escolaridade = st.selectbox(
    'escolaridade',
     ['TODOS','Superior completo', 'Ensino Médio completo', 'Ensino Médio incompleto', 'Ensino Fundamental completo', 'Ensino Fundamental incompleto', 'Lê e escreve'])

# partidos = pd.read_json('https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/partidos.json')

# partidos = partidos.sort_values(by='sigla')
# partido = st.selectbox(
#     'Partido',
#      partidos['sigla'])

# partido_id = partidos.query(f'sigla == "{partido}"').values[0,0]

# st.write('Estado: ', sigla, 'Cargo: ', cargo, 'Partido:', partido)

# partido_info =  requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/prestador/consulta/partido/2040602022/2022/{sigla}/3/{partido_id}", headers=headers ).json()

# partido_info

partidos = pd.read_json('https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/partidos.json')
pos = {1:'extrema direita', 2:'direita', 3:'centro', 4:'esquerda', 5:'extrema esquerda'}
partidos['posicao'] = partidos['posicao'].apply(lambda x: pos[x])
st.write(partidos)

st.info(f""" ## {sigla} | {cargo} """)
# st.image(f"https://divulgacandcontas.tse.jus.br/divulga/images/partidos/{partido}.jpg")


# f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos"
candidatos = requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos", headers=headers ).json()['candidatos']

candidatos_df = pd.DataFrame(candidatos)
candidatos_df['PARTIDO'] = candidatos_df['partido'].apply(lambda x:  x['sigla'])
# candidatos_df
nome_arquivo = f"{sigla}-{cargo}.csv"

try:
    candidatos_completo = pd.read_csv(f"./data/candidatos/{nome_arquivo}")
    st.write(len(candidatos_completo.columns))
    if len(candidatos_completo.columns) < 22:
        1+'1'
except:
    candidatos_completo = pd.DataFrame()
    total = len(candidatos_df)
    un = 1/total
    i=0
    for row in stqdm(range(total)):
        cid = candidatos_df.loc[row]['id']
        # cid
        #f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/buscar/2022/{sigla}/2040602022/candidato/{cid}"
        candidato = requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/buscar/2022/{sigla}/2040602022/candidato/{cid}", headers=headers ).json()
        # candidato
        props = [
                'nomeUrna',
                'partido',
                'numero',
                'descricaoSexo',
                'descricaoEstadoCivil',
                'descricaoCorRaca',
                'descricaoSituacao',
                'nacionalidade',
                'grauInstrucao',
                'ocupacao',
                'dataDeNascimento',
                'totalDeBens',
                'nomeMunicipioNascimento',
                'eleicoesAnteriores',
                'st_REELEICAO'
                ]
        cs = {p:candidato[p] for p in props}
        cs['partido'] = cs['partido']['sigla']
        cs = pd.Series(cs, name=candidato['id'])
        # cs
        # st.write(pd.Series(cs))
        # pd.DataFrame(candidato.values())
        cs['idade'] = ((datetime.now() - pd.to_datetime(candidato['dataDeNascimento']))/365.2425).days
        props = ["grauInstrucao", "eleicoesAnteriores", "dataDeNascimento"]
        candidato_resumo = cs[props]
        score = get_score(candidato_resumo)
        cs['escolaridade_pts'] = "{:.2f}".format(score['escolaridade'])
        cs['idade_pts'] = "{:.2f}".format(score['idade'])
        cs['politica_pts'] = "{:.2f}".format(score['politica'])
        
        cs['ranking'] = "{:.2f}".format(pd.Series(score).mean())
        cs['posicao'] = partidos.loc[partidos.sigla == cs['partido']]['posicao'].values[0]
        # cs['TSE'] = f"<a target='_blank' href='https://divulgacandcontas.tse.jus.br/divulga/#/candidato/2022/2040602022/{sigla}/{cid}'> TSE</a>"
        candidatos_completo = candidatos_completo.append(cs)
        # st.write(candidatos_completo)    
    candidatos_completo.to_csv(f"./data/candidatos/{nome_arquivo}")

candidatos_completo = candidatos_completo.set_index(['nomeUrna','numero'])
resultado = candidatos_completo
cols = ['partido', 'ranking',  'escolaridade_pts', 'idade_pts', 'politica_pts','posicao', 'grauInstrucao','idade', 'descricaoSexo', 'descricaoCorRaca', 'ocupacao','totalDeBens', 'st_REELEICAO']

if(sexo != 'TODOS'):
    resultado = resultado.query(f"descricaoSexo == '{sexo}'")
if(cor != 'TODOS'):
    resultado = resultado.query(f"descricaoCorRaca == '{cor}'")
if(escolaridade != 'TODOS'):
    resultado = resultado.query(f"grauInstrucao == '{escolaridade}'")
if(reeleicao != 'TODOS'):
    resultado = resultado.query(f"st_REELEICAO == {reeleicao}")

st.write(resultado.drop('eleicoesAnteriores', axis=1)[cols].sort_values('ranking', ascending=False))
# st.markdown('Mais informações na página **candidato** no menu lateral.')
# st.markdown('Descrição da pontuação na página **sobre** no menu lateral.')
st.write(f"👉 <a target='_blank' href='https://tinyurl.com/votix-br/candidato'> Candidato </a>", unsafe_allow_html=True)
st.write(f"👉 <a target='_blank' href='https://tinyurl.com/votix-br/sobre'> Pontuação </a>", unsafe_allow_html=True)
# if st.button('Candidato'):
#     webbrowser.open_new_tab('https://tinyurl.com/votix-br/candidato')
# if st.button('Pontuacao'):
#     webbrowser.open_new_tab('https://tinyurl.com/votix-br/sobre')

# st.write(resultado.drop('eleicoesAnteriores', axis=1))