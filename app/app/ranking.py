import streamlit as st
from datetime import datetime
import numpy as np
import pandas as pd
import requests
from utils import get_score, get_escolaridade, get_idade, get_politica, get_eleicoes, fix_cpf
from stqdm import stqdm
import webbrowser
import os
import plotly.express as px

st.set_page_config(
    page_title='Votix - Ranking',
    page_icon="📊",
    layout='wide'
)

#st.write(os.path.dirname(st.__file__))


headers = { "accept": "application/json",
           "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
           }

st.write(""" # 📊  Votix """)
st.success(""" ## Ranking """)
st.write(""" Veja a pontuação dos candidatos. """)

timer = pd.to_datetime('2022-10-02') - datetime.today()
days = (timer.days)
hours = int(timer.seconds // 3600)
# st.write(timer)
st.write(f"#### Faltam {days} dias e {hours} horas para a Eleição 2022.")
st.progress(days)

uf = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO", "BR"]

sigla = st.selectbox(
    'Estado',
     uf, 15)

cargos = pd.read_json('https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/cargos.json')
# cargos = pd.read_json('/Volumes/EXT/myApps/votix/app/app/data/cargos.json')

cargo = st.selectbox(
    'Cargo',
     cargos['nome'],0)

cargo_id = cargos.query(f'nome == "{cargo}"').values[0,0]

sexo = st.selectbox(
    'sexo',
     ['TODOS','FEMININO', 'MASCULINO'])

cor = st.selectbox(
    'cor',
     ['TODOS','PRETA', 'PARDA', 'BRANCA'])


partidos = pd.read_json('https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/partidos.json')

partidos = partidos.sort_values(by='sigla')
partidos.loc[len(partidos)+1] = 'TODOS'

partido = st.selectbox(
    'Partido',
     partidos['sigla'],len(partidos)-1)


reeleicao = st.selectbox(
    'Reeleição',
     ['TODOS','Sim', 'Não'])

st_rel = {'Sim': 'S', 'Não': 'N', 'TODOS':'TODOS'}
reeleicao = st_rel[reeleicao]

escolaridade = st.selectbox(
    'escolaridade',
     ['TODOS','SUPERIOR COMPLETO', 'ENSINO MÉDIO COMPLETO', 'ENSINO MÉDIO INCOMPLETO', 'ENSINO FUNDAMENTAL COMPLETO', 'ENSINO FUNDAMENTAL INCOMPLETO', 'LÊ E ESCREVE'])

candidatos_df = pd.read_csv(f'https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/candidatos/consulta_cand_2022/consulta_cand_2022_{sigla}.csv', sep=';', 
                            encoding='latin1', infer_datetime_format=True, converters={'NR_CPF_CANDIDATO': lambda x: str(x)} )
candidatos_df = candidatos_df.query(f'CD_CARGO == {cargo_id}')

ocupacoes = pd.Series(candidatos_df['DS_OCUPACAO'].unique()).sort_values().to_list()
ocupacoes.insert(0,'TODOS')
ocupacao = st.selectbox(
    'Ocupação',
     ocupacoes)


qtd = len(candidatos_df)

vagas = pd.read_csv(f'https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/candidatos/consulta_vagas_2022/consulta_vagas_2022_{sigla}.csv', sep=';', encoding='latin1')
vg = vagas.query(f'CD_CARGO == {cargo_id}')['QT_VAGAS'].values[0]
st.warning(f'CANDIDATOS: {qtd} | VAGAS: {vg} | CONCORRÊNCIA: {(qtd/vg).round(2)}')

# if st.button('Consultar'):
# vagas = pd.read_json('https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/cargos.json')


partidos = pd.read_json('https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/partidos.json')
pos = {1:'extrema direita', 2:'direita', 3:'centro', 4:'esquerda', 5:'extrema esquerda'}
partidos['posicao'] = partidos['posicao'].apply(lambda x: pos[x])
# st.write(partidos)

st.info(f""" ## {sigla} | {cargo} """)
# st.image(f"https://divulgacandcontas.tse.jus.br/divulga/images/partidos/{partido}.jpg")



# f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos"
# candidatos = requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos", headers=headers ).json()['candidatos']
# candidatos_df = pd.read_csv(f'https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/candidatos/consulta_cand_2022/consulta_cand_2022_{sigla}.csv', sep=';', encoding='latin1')


# candidatos_df = candidatos_df.query(f'CD_CARGO == {cargo_id}')
# candidatos_df = pd.DataFrame(candidatos)
# candidatos_df['PARTIDO'] = candidatos_df['partido'].apply(lambda x:  x['sigla'])
# candidatos_df
nome_arquivo = f"{sigla}-{cargo}.csv"
PROPS = ['SQ_CANDIDATO',
        'NR_CPF_CANDIDATO', 
        'NM_URNA_CANDIDATO',
        'SG_PARTIDO',
        'NR_CANDIDATO',
        'DS_GENERO',
        'DS_ESTADO_CIVIL',
        'DS_COR_RACA',
        'DS_DETALHE_SITUACAO_CAND',
        'DS_NACIONALIDADE',
        'DS_GRAU_INSTRUCAO',
        'DS_OCUPACAO',
        'DT_NASCIMENTO',
        'NM_MUNICIPIO_NASCIMENTO',
        'ST_REELEICAO']


resultado = candidatos_df[PROPS]

if(sexo != 'TODOS'):
    resultado = resultado.query(f"DS_GENERO == '{sexo}'")
if(cor != 'TODOS'):
    resultado = resultado.query(f"DS_COR_RACA == '{cor}'")
if(escolaridade != 'TODOS'):
    resultado = resultado.query(f"DS_GRAU_INSTRUCAO == '{escolaridade}'")
if(partido != 'TODOS'):
    resultado = resultado.query(f"SG_PARTIDO == '{partido}'")
if(reeleicao != 'TODOS'):
    resultado = resultado.query(f"ST_REELEICAO == '{reeleicao}'")
if(ocupacao != 'TODOS'):
    resultado = resultado.query(f"DS_OCUPACAO == '{ocupacao}'")




eleicoes_anteriores = pd.concat(get_eleicoes())

# eleicoes_anteriores
# eleicoes_anteriores = resultado.merge(eleicoes_anteriores, on='NR_CPF_CANDIDATO').query(f"DS_SIT_TOT_TURNO == 'ELEITO'")
eleicoes_anteriores['NR_CPF_CANDIDATO'] = eleicoes_anteriores['NR_CPF_CANDIDATO'].apply(fix_cpf)
resultado['NR_CPF_CANDIDATO'] = resultado['NR_CPF_CANDIDATO'].apply(fix_cpf)

eleicoes_anteriores = resultado.merge(eleicoes_anteriores, on='NR_CPF_CANDIDATO').query(f"DS_SIT_TOT_TURNO == 'ELEITO' or DS_SIT_TOT_TURNO == 'ELEITO POR QP'")
eleicoes_anteriores = eleicoes_anteriores[['NR_CPF_CANDIDATO', 'NM_URNA_CANDIDATO_x', 'ANO', 'SG_PARTIDO_y', 'DS_CARGO', 'NM_UE']]

eleicoes_anteriores['politica'] = eleicoes_anteriores['DS_CARGO'].apply(get_politica)

cargos_eletivos = eleicoes_anteriores.copy()

eleicoes_anteriores = eleicoes_anteriores.pivot_table(index='NR_CPF_CANDIDATO', values='politica', aggfunc=max)

resultado['escolaridade'] = resultado['DS_GRAU_INSTRUCAO'].apply(get_escolaridade)
resultado['anos'] = ((datetime.now() - pd.to_datetime(resultado['DT_NASCIMENTO'], format='%d/%m/%Y')).dt.days/365.2425).astype('int')
resultado['idade'] = resultado['anos'].apply(get_idade)

# resultado['politica'] = resultado['NR_CPF_CANDIDATO'].apply(lambda x: eleicoes_anteriores.query(f'NR_CPF_CANDIDATO = {x}')['politica'].max()) 
resultado['politica'] = resultado['NR_CPF_CANDIDATO'].apply(lambda x: eleicoes_anteriores.loc[x]['politica'] if x in eleicoes_anteriores.index else 0)
resultado['ranking'] = (resultado['escolaridade'] + resultado['idade'] + resultado['politica'])/3
resultado['posicao'] = resultado['SG_PARTIDO'].apply(lambda x: partidos.query(f'sigla == "{x}"')['posicao'].values[0])
resultado['ST_REELEICAO'] = resultado['ST_REELEICAO'].apply(lambda x: True if x == 'S'  else False)

cols = ['NM_URNA_CANDIDATO','NR_CANDIDATO','SG_PARTIDO', 'posicao', 'ST_REELEICAO', 'ranking', 'escolaridade', 'idade', 'politica','anos', 'DS_GENERO', 'DS_COR_RACA', 'DS_GRAU_INSTRUCAO', 'DS_OCUPACAO', ]

# for row in stqdm(range(total)):
#     # score = get_score(candidato_resumo)
#     pass




# st.write(resultado.reset_index())
bens = pd.read_csv('https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/bens/bens-ano.csv', float_precision='round_trip', index_col=0)

st.info(f'Candidatos ({len(resultado[cols])})')
st.write(resultado[cols].sort_values("ranking", ascending=False))

fig = px.scatter(resultado,  x='ranking', y='anos', color='ST_REELEICAO', hover_data=['NM_URNA_CANDIDATO','NR_CANDIDATO','SG_PARTIDO', 'DS_GRAU_INSTRUCAO', 'DS_GENERO', 'DS_COR_RACA','DS_OCUPACAO'])
st.plotly_chart(fig, use_container_width=True)

st.info('Cargos Eletivos')
st.dataframe(cargos_eletivos[['NM_URNA_CANDIDATO_x', 'ANO', 'SG_PARTIDO_y', 'DS_CARGO', 'NM_UE', 'politica']])

st.info('Bens declarados')
resultado_bens = candidatos_df.merge(bens, on='SQ_CANDIDATO').sort_values('NM_URNA_CANDIDATO')
resultado_bens['DIFERENCA'] = resultado_bens['2022'] - resultado_bens['2018']
# resultado_bens = resultado_bens.sort_values('DIFERENCA', ascending=False)
resultado_bens = resultado_bens.loc[resultado_bens['NR_CANDIDATO'].isin(resultado['NR_CANDIDATO'])]
st.write(resultado_bens[['NM_URNA_CANDIDATO', 'NR_CANDIDATO','SG_PARTIDO','2010','2014','2018','2022', 'DIFERENCA']])
# st.write(resultado.drop('eleicoesAnteriores', axis=1)[cols].sort_values('ranking', ascending=False))
# st.markdown('Mais informações na página **candidato** no menu lateral.')
# st.markdown('Descrição da pontuação na página **sobre** no menu lateral.')
       

st.write(f"👉 <a target='_blank' href='https://tinyurl.com/votix-br/candidato'> Candidato </a>", unsafe_allow_html=True)
st.write(f"👉 <a target='_blank' href='https://tinyurl.com/votix-br/sobre'> Pontuação </a>", unsafe_allow_html=True)
# if st.button('Candidato'):
#     webbrowser.open_new_tab('https://tinyurl.com/votix-br/candidato')
# if st.button('Pontuacao'):
#     webbrowser.open_new_tab('https://tinyurl.com/votix-br/sobre')

# st.write(resultado.drop('eleicoesAnteriores', axis=1))

del eleicoes_anteriores
del candidatos_df
del bens