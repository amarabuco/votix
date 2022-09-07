import streamlit as st
from datetime import datetime
import pandas as pd
import requests

st.set_page_config(
    page_title='Votix - Sobre',
    page_icon="📊",
    layout='wide'
)

headers = { "accept": "application/json"}

st.write(""" # 📊  Votix """)
st.write(""" O aplicativo Votix apresenta informações e cálculos para auxiliar o eleitor a tomar uma decisão informada e consciente sobre seus candidatos aos cargos eletivos. """)

st.write(""" ## Pontuação """)
st.caption(""" A definição dos critérios considerou as informações fornecidas pelo TSE e utilizou parâmetros da Constituição Federal para exercício de cargos públicos: idade, conhecimento e experiência. 
         Está sujeita a alterações e melhorias, e representa uma avaliação básica, mas deve ser complementada com mais informações e visão política do eleitor.""")

st.write(""" #### Escolaridade: mais estudo, mais pontos. """)
escolaridade = {'Lê e escreve':0, 'Ensino Fundamental incompleto':1, 'Ensino Fundamental completo':2, 'Ensino Médio incompleto':2.5, 'Ensino Médio completo':3, 
                    'Superior incompleto':4, 'Superior completo':5}
st.write(pd.Series(escolaridade, name='Escolaridade'))
st.write(""" #### Idade: mais idade, mais pontos. """)
idade = {' < 30': 1,' < 40': 2,'< 50': 3,' < 60':4, ' > 60':5}
st.write(pd.Series(idade, name='Idade'))

st.write(""" #### Política: eleição para o cargo mais importante, mais pontos. """)
politica = {'Nenhum':0,'Vereador':1, 'Deputado Estadual':2, 'Deputado Federal':3, 'Vice-prefeito':2.5,'Prefeito':3, 'Senador':4, 'Vice-governador':4.5, 'Governador':5, 'Vice-presidente':5}
st.write(pd.Series(politica, name='Experiência Política'))
st.write('Exemplo: candidato foi eleito Senador 2010 e Prefeito em 2020. Vai pontuar 4, pois o cargo pra Senador vale mais que o de prefeito.')

st.write(""" #### Resultado: média dos critérios anteriores """)

st.write(""" ## Outras informações """)
st.write(""" Fonte dos Dados: https://divulgacandcontas.tse.jus.br/divulga/ """)
st.write(""" Código: https://github.com/amarabuco/votix """)
