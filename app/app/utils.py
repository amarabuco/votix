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