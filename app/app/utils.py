import streamlit as st
from datetime import datetime
import pandas as pd



def get_score(df):
    escolaridade = {'Lê e escreve':0, 'Ensino Fundamental incompleto':1, 'Ensino Fundamental completo':2, 'Ensino Médio incompleto':2.5, 'Ensino Médio completo':3, 
                    'Superior incompleto':4, 'Superior completo':5}
    escol_pts = escolaridade[df['grauInstrucao']]
    # escol_pts = (escol_pts - 0)/(len(escolaridade) - 0) * 5
    
    idades = [20,30,40,50,60,100]
    idade = ((datetime.now() - pd.to_datetime(df['dataDeNascimento']))/365.2425).days
    score_idade = 0
    for k, v in enumerate(idades):
        if (idade < v):
            score_idade = k
            break        
    
    cargos = {'Nenhum':0, '1º Suplente':0, '2º Suplente': 0,  '1º Suplente Senador':0, '2º Suplente Senador': 0, 'Vereador':1, 'Deputado Estadual':2, 'Deputado Federal':3, 'Vice-prefeito':2.5, 'Vice-Prefeito':2.5, 'Prefeito':3, 'Senador':3.5, 'Vice-governador':4, 'Vice-Governador':4, 'Governador':4.5, 'Vice-presidente':4.5, 'Presidente': 5}
    eleicoes = pd.DataFrame(df['eleicoesAnteriores'])
    eleicoes = eleicoes.query(f"situacaoTotalizacao == 'Eleito' or situacaoTotalizacao == 'Eleito por QP'")
    eleicoes['cargo_pts'] = eleicoes['cargo'].apply(lambda x: cargos[x])
    if len(eleicoes) == 0:
        cargo_pts = 0
    else:
        cargo_pts = eleicoes['cargo_pts'].max()
    
    # cargo_pts = (cargo_pts - 0)/(len(cargos) - 0) * 5
    
    return {'escolaridade': escol_pts, 'idade': score_idade, 'politica': cargo_pts}

def get_escolaridade(x):
    escolaridade = {'lê e escreve':0, 'ensino fundamental incompleto':1, 'ensino fundamental completo':2, 'ensino médio incompleto':2.5, 'ensino médio completo':3, 
                    'superior incompleto':4, 'superior completo':5}
    escol_pts = escolaridade[x.lower()]
    # escol_pts = (escol_pts - 0)/(len(escolaridade) - 0) * 5
    
    return escol_pts

def get_idade(x):
    idades = [20,30,40,50,60,100]
    score_idade = 0
    for k, v in enumerate(idades):
        if (x < v):
            score_idade = k
            break    
    
    return score_idade

def get_politica(x):
    cargos = {'nenhum':0, '1º suplente':0, '2º suplente': 0,  '1º suplente Senador':0, '2º suplente Senador': 0, 'vereador':1, 'deputado estadual':2, 'deputado federal':3, 'vice-prefeito':2.5, 'prefeito':3, 'senador':3.5, 'vice-governador':4, 'governador':4.5, 'vice-presidente':4.5, 'presidente': 5}
    cargo_pts = cargos[x.lower()]
    
    return cargo_pts

@st.cache
def get_eleicoes():
    eleitos2010 = pd.read_csv(f'https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/candidatos/consulta_cand_2010/eleitos_2010.csv', 
                                    sep=',', converters={'NR_CPF_CANDIDATO': lambda x: str(x)} )
    eleitos2010['ANO'] = 2010
    eleitos2012 = pd.read_csv(f'https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/candidatos/consulta_cand_2012/eleitos_2012.csv', 
                                    sep=',', converters={'NR_CPF_CANDIDATO': lambda x: str(x)} )
    eleitos2012['ANO'] = 2012
    eleitos2014 = pd.read_csv(f'https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/candidatos/consulta_cand_2014/eleitos_2014.csv', 
                                    sep=',', converters={'NR_CPF_CANDIDATO': lambda x: str(x)} )
    eleitos2014['ANO'] = 2014
    eleitos2016 = pd.read_csv(f'https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/candidatos/consulta_cand_2016/eleitos_2016.csv', 
                                    sep=',', converters={'NR_CPF_CANDIDATO': lambda x: str(x)} )
    eleitos2016['ANO'] = 2016
    eleitos2018 = pd.read_csv(f'https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/candidatos/consulta_cand_2018/eleitos_2018.csv', 
                                    sep=',',  converters={'NR_CPF_CANDIDATO': lambda x: str(x)} )
    eleitos2018['ANO'] = 2018
    eleitos2020 = pd.read_csv(f'https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/candidatos/consulta_cand_2020/eleitos_2020.csv', 
                                    sep=',',  converters={'NR_CPF_CANDIDATO': lambda x: str(x)} )
    eleitos2020['ANO'] = 2020
    eleicoes = [eleitos2010, eleitos2012, eleitos2014, eleitos2016, eleitos2018, eleitos2020]
    return eleicoes

def fix_cpf(x):
    if len(x) < 11:
        zeros = 11 - len(x)
        return '0' * zeros + x
    return x