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
from dadosPartidos import partidos as partidos_dados
from dadosCargos import cargos as cargos_dados

st.set_page_config(
    page_title='Votix - Ranking',
    page_icon="📊",
    layout='wide'
)

# st.write(os.path.dirname(st.__file__))


@st.cache
def load_candidatos(cids):
    candidatos_df = pd.DataFrame()
    for cid in cids['id']:
        cand = pd.json_normalize(requests.get(
            f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/buscar/2024/{sigla}/2045202024/candidato/{cid}", headers=headers).json())
        candidatos_df = pd.concat([candidatos_df, cand])
    return candidatos_df


headers = {"accept": "application/json",
           "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
           }

st.write(""" # 📊  Votix """)
st.success(""" ## Ranking """)
st.write(""" Veja a pontuação dos candidatos. """)

timer = pd.to_datetime('2024-10-06 11:00:00') - datetime.today()
days = (timer.days)
hours = int(timer.seconds // 3600)
# st.write(timer)
st.write(f"#### Faltam {days} dias e {hours} horas para a Eleição 2024.")
st.progress(days)
if st.button('Limpar dados'):
    st.cache.clear()

uf = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
      "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "BR"]

sigla_uf = st.selectbox(
    'Estado',
    uf, 15)

municipios = requests.get(
    f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/eleicao/buscar/{sigla_uf}/2045202024/municipios", headers=headers).json()["municipios"]

sigla = st.selectbox(
    'Município',
    municipios, format_func=lambda x: x['nome'], index=131)

municipio = sigla['nome']

sigla = sigla['codigo']

cargos = pd.DataFrame(cargos_dados)


cargo = st.selectbox(
    'Cargo',
    cargos['nome'], 0)

cargo_id = cargos.query(f'nome == "{cargo}"').values[0, 0]

sexo = st.selectbox(
    'sexo',
    ['TODOS', 'FEMININO', 'MASCULINO'])

cor = st.selectbox(
    'cor',
    ['TODOS', 'PRETA', 'PARDA', 'BRANCA'])


partidos = pd.read_json(
    'https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/partidos.json')

partidos = partidos.sort_values(by='sigla')
partidos.loc[len(partidos)+1] = 'TODOS'

partido = st.selectbox(
    'Partido',
    partidos['sigla'], len(partidos)-1)


reeleicao = st.selectbox(
    'Reeleição',
    ['TODOS', 'Sim', 'Não'])

st_rel = {'Sim': 'S', 'Não': 'N', 'TODOS': 'TODOS'}
reeleicao = st_rel[reeleicao]

escolaridade = st.selectbox(
    'escolaridade',
    ['TODOS', 'SUPERIOR COMPLETO', 'ENSINO MÉDIO COMPLETO', 'ENSINO MÉDIO INCOMPLETO', 'ENSINO FUNDAMENTAL COMPLETO', 'ENSINO FUNDAMENTAL INCOMPLETO', 'LÊ E ESCREVE'])

# candidatos_df = pd.read_csv(f'https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/candidatos/consulta_cand_2022/consulta_cand_2022_{sigla}.csv', sep=';',
#                             encoding='latin1', infer_datetime_format=True, converters={'cpf': lambda x: str(x)})


cids = pd.DataFrame.from_records(requests.get(
    f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2024/{sigla}/2045202024/{cargo_id}/candidatos", headers=headers).json()['candidatos'])

candidatos_df = pd.DataFrame()
with st.spinner('Carregando candidatos... '):
    candidatos_df = load_candidatos(cids)
    # candidatos_df = pd.json_normalize(requests.get(
    #     f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2024/{sigla}/2045202024/{cargo_id}/candidatos", headers=headers).json()['candidatos'])

    candidatos_df
    candidatos_df = candidatos_df.loc[candidatos_df["cargo.codigo"] == cargo_id]

    ocupacoes = pd.Series(
        candidatos_df['ocupacao'].unique()).sort_values().to_list()
    ocupacoes.insert(0, 'TODOS')
    ocupacao = st.selectbox(
        'Ocupação',
        ocupacoes)

    qtd = len(candidatos_df)

    vagas = pd.read_csv(
        f'https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/vagas/consulta_vagas_2024_{sigla_uf}.csv', sep=';', encoding='latin1')
    # st.write(vagas.query(f'(SG_UE == {sigla})'))

    vg = vagas.query(f'(CD_CARGO == {cargo_id}) & (SG_UE == {sigla})')[
        'QT_VAGA'].values[0]
    st.warning(
        f'CANDIDATOS: {qtd} | VAGAS: {vg} | CONCORRÊNCIA: {(qtd/vg).round(2)}')

    # if st.button('Consultar'):
    # vagas = pd.read_json('https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/cargos.json')

    # candidatos_df

    partidos = pd.read_json(
        'https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/partidos.json')
    pos = {1: 'extrema direita', 2: 'direita',
           3: 'centro', 4: 'esquerda', 5: 'extrema esquerda'}
    partidos['posicao'] = partidos['posicao'].apply(lambda x: pos[x])
    # st.write(partidos)

    st.info(f""" ## {municipio} | {cargo} """)
    # st.image(f"https://divulgacandcontas.tse.jus.br/divulga/images/partidos/{partido}.jpg")

    # f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos"
    # candidatos = requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos", headers=headers ).json()['candidatos']
    # candidatos_df = pd.read_csv(f'https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/candidatos/consulta_cand_2022/consulta_cand_2022_{sigla}.csv', sep=';', encoding='latin1')

    # candidatos_df = candidatos_df.query(f'cargo == {cargo_id}')
    # candidatos_df = pd.DataFrame(candidatos)
    # candidatos_df['PARTIDO'] = candidatos_df['partido'].apply(lambda x:  x['sigla'])
    # candidatos_df
    nome_arquivo = f"{sigla}-{cargo}.csv"

    # candidatos_df.columns
    PROPS = ['id',
             'cpf',
             'nomeUrna',
             'partido.nome',
             'numero',
             'descricaoSexo',
             'descricaoEstadoCivil',
             'descricaoCorRaca',
             'descricaoSituacao',
             'nacionalidade',
             'grauInstrucao',
             'ocupacao',
             'dataDeNascimento',
             'nomeMunicipioNascimento',
             'st_REELEICAO']

    # candidatos_df
    resultado = candidatos_df[PROPS]
    # resultado

    if (sexo != 'TODOS'):
        resultado = resultado.query(f"descricaoSexo == '{sexo}'")
    if (cor != 'TODOS'):
        resultado = resultado.query(f"descricaoCorRaca == '{cor}'")
    if (escolaridade != 'TODOS'):
        resultado = resultado.query(f"grauInstrucao == '{escolaridade}'")
    if (partido != 'TODOS'):
        resultado = resultado.query(f'"partido.nome" == {partido}')
    if (reeleicao != 'TODOS'):
        resultado = resultado.query(f"st_REELEICAO == '{reeleicao}'")
    if (ocupacao != 'TODOS'):
        resultado = resultado.query(f"ocupacao == '{ocupacao}'")

    eleicoes_anteriores = pd.concat(get_eleicoes())
    # eleicoes_anteriores

    # eleitos = pd.read_csv('data/consulta_cand_2022_BRASIL.csv',
    #                       sep=';', encoding='latin1')
    # st.write(eleitos.head())
    # eleitos.query(
    #     f"DS_SIT_TOT_TURNO == 'ELEITO' or DS_SIT_TOT_TURNO == 'ELEITO POR QP'")[['SQ_CANDIDATO', 'NR_CPF_CANDIDATO', 'NM_URNA_CANDIDATO', 'SG_PARTIDO', 'NR_CANDIDATO', 'DS_SIT_TOT_TURNO', 'DS_CARGO', 'NM_UE']].to_csv('data/eleitos_2022.csv')

    # eleicoes_anteriores
    # eleicoes_anteriores = resultado.merge(eleicoes_anteriores, on='cpf').query(f"DS_SIT_TOT_TURNO == 'ELEITO'")
    eleicoes_anteriores['NR_CPF_CANDIDATO'] = eleicoes_anteriores['NR_CPF_CANDIDATO'].apply(
        fix_cpf)

    # resultado['cpf'] = resultado['cpf'].apply(fix_cpf)
    # resultado

    # eleicoes_anteriores = resultado.merge(
    #     eleicoes_anteriores, left_on='cpf', right_on='NR_CPF_CANDIDATO')
    eleicoes_anteriores = resultado.merge(
        eleicoes_anteriores, left_on='nomeUrna', right_on='NM_URNA_CANDIDATO')
    # eleicoes_anteriores
    eleicoes_anteriores = eleicoes_anteriores[[
        'NR_CPF_CANDIDATO', 'NM_URNA_CANDIDATO', 'ANO', 'SG_PARTIDO', 'DS_CARGO', 'NM_UE']]

    eleicoes_anteriores['DS_CARGO'] = eleicoes_anteriores['DS_CARGO'].apply(
        lambda x: x.lower())
    eleicoes_anteriores['politica'] = eleicoes_anteriores['DS_CARGO'].apply(
        get_politica)

    cargos_eletivos = eleicoes_anteriores.copy()

    eleicoes_anteriores = eleicoes_anteriores.pivot_table(
        index='NM_URNA_CANDIDATO', values='politica', aggfunc=max)

    resultado['escolaridade'] = resultado['grauInstrucao'].apply(
        get_escolaridade)
    resultado['anos'] = ((datetime.now() - pd.to_datetime(resultado['dataDeNascimento'],
                                                          format='%Y-%m-%d')).dt.days/365.2425).astype('int')
    resultado['idade'] = resultado['anos'].apply(get_idade)

    # resultado['politica'] = resultado['cpf'].apply(lambda x: eleicoes_anteriores.query(f'cpf = {x}')['politica'].max())
    resultado['politica'] = resultado['nomeUrna'].apply(
        lambda x: eleicoes_anteriores.loc[x]['politica'] if x in eleicoes_anteriores.index else 0)
    resultado['ranking'] = (resultado['escolaridade'] +
                            resultado['idade'] + resultado['politica'])/3
    # resultado['posicao'] = resultado['partido.nome'].apply(
    #     lambda x: partidos.query(f'sigla == "{x}"')['posicao'].values[0])
    resultado['posicao'] = ''
    # resultado['st_REELEICAO'] = resultado['st_REELEICAO'].apply(
    #     lambda x: True if x == 'S' else False)
    # resultado['st_REELEICAO'] = resultado['st_REELEICAO'].apply(
    #     lambda x: True if x == 'S' else False)

    cols = ['nomeUrna', 'numero', 'partido.nome', 'posicao', 'st_REELEICAO', 'ranking',
            'escolaridade', 'idade', 'politica', 'anos', 'descricaoSexo', 'descricaoCorRaca', 'grauInstrucao', 'ocupacao', ]

    # with st.spinner('Calculando ranking... '):
    #     for row in stqdm(range(total)):
    #         score = get_score(candidato_resumo)
    #         pass

    # resultado

    # st.write(resultado.reset_index())
    bens = pd.read_csv('https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/bens/bens-ano.csv',
                       float_precision='round_trip', index_col=0)

    st.info(f'Candidatos ({len(resultado[cols])})')
    st.dataframe(resultado[cols].sort_values(
        "ranking", ascending=False))

    fig = px.scatter(resultado,  x='anos', y='ranking', color='st_REELEICAO', hover_data=[
        'nomeUrna', 'numero', 'partido.nome', 'grauInstrucao', 'descricaoSexo', 'descricaoCorRaca', 'ocupacao'])
    st.plotly_chart(fig, use_container_width=True)

    st.info('Cargos Eletivos')
    # cargos_eletivos
    st.dataframe(cargos_eletivos[['NM_URNA_CANDIDATO', 'ANO',
                                  'SG_PARTIDO', 'DS_CARGO', 'NM_UE', 'politica']])

    st.info('Bens declarados')
    resultado_bens = candidatos_df.merge(
        bens, left_on='id', right_on='SQ_CANDIDATO').sort_values('nomeUrna')
    resultado_bens
    resultado_bens['DIFERENCA'] = resultado_bens['2022'] - \
        resultado_bens['2018']
    # resultado_bens = resultado_bens.sort_values('DIFERENCA', ascending=False)
    resultado_bens = resultado_bens.loc[resultado_bens['numero'].isin(
        resultado['numero'])]
    st.dataframe(resultado_bens[['nomeUrna', 'numero',
                                 'partido.nome', '2010', '2014', '2018', '2022', 'DIFERENCA']])
    # st.write(resultado.drop('eleicoesAnteriores', axis=1)[cols].sort_values('ranking', ascending=False))
    # st.markdown('Mais informações na página **candidato** no menu lateral.')
    # st.markdown('Descrição da pontuação na página **sobre** no menu lateral.')

    # st.write(f"👉 <a target='_blank' href='https://tinyurl.com/votix-br/candidato'> Candidato </a>",
    #          unsafe_allow_html=True)
    # st.write(f"👉 <a target='_blank' href='https://tinyurl.com/votix-br/sobre'> Pontuação </a>",
    #          unsafe_allow_html=True)
    # # if st.button('Candidato'):
    # #     webbrowser.open_new_tab('https://tinyurl.com/votix-br/candidato')
    # # if st.button('Pontuacao'):
    # #     webbrowser.open_new_tab('https://tinyurl.com/votix-br/sobre')

    # # st.write(resultado.drop('eleicoesAnteriores', axis=1))

    # del eleicoes_anteriores
    # del candidatos_df
    # del bens
