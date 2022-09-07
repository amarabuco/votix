import streamlit as st
import plotly.express as px
from datetime import datetime
import pandas as pd
import requests
import urllib.parse
from utils import get_score
import webbrowser

st.set_page_config(
    page_title='Votix - Candidato',
    page_icon="📊",
    layout='wide'
)

# def get_score(df):
#     escolaridade = {'Lê e escreve':0, 'Ensino Fundamental incompleto':1, 'Ensino Fundamental completo':2, 'Ensino Médio incompleto':2.5, 'Ensino Médio completo':3, 
#                     'Superior incompleto':4, 'Superior completo':5}
#     escol_pts = escolaridade[df['grauInstrucao']]
#     # escol_pts = (escol_pts - 0)/(len(escolaridade) - 0) * 5
    
#     idades = [20,30,40,50,60,100]
#     idade = ((datetime.now() - pd.to_datetime(df['dataDeNascimento']))/365.2425).days
#     score_idade = 0
#     for k, v in enumerate(idades):
#         if (idade < v):
#             score_idade = k
#             break        
    
#     cargos = {'Nenhum':0,'Vereador':1, 'Deputado Estadual':2, 'Deputado Federal':3, 'Vice-prefeito':2.5,'Prefeito':3, 'Senador':4, 'Vice-governador':4.5, 'Governador':5, 'Vice-presidente':5}
#     eleicoes = pd.DataFrame(df['eleicoesAnteriores'])
#     eleicoes['cargo_pts'] = eleicoes['cargo'].apply(lambda x: cargos[x])
#     eleito = eleicoes.query(f"situacaoTotalizacao == 'Eleito' or situacaoTotalizacao == 'Eleito por QP'")
#     if len(eleito) == 0:
#         cargo_pts = 0
#     else:
#         cargo_pts = eleito['cargo_pts'].max()
    
#     # cargo_pts = (cargo_pts - 0)/(len(cargos) - 0) * 5
    
#     return {'escolaridade': escol_pts, 'idade': score_idade, 'politica': cargo_pts}

st.write(""" 
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-CNMGZ2L10T"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-CNMGZ2L10T');
</script> """, unsafe_allow_html=True)

headers = { "accept": "application/json",
           "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
           }

st.write(""" # 📊  Votix """)

timer = pd.to_datetime('2022-10-02') - datetime.today()
days = (timer.days)
hours = int(timer.seconds // 3600)
# st.write(timer)
st.write(f"#### Faltam {days} dias e {hours} horas para a Eleição 2022.")
st.progress(days)

st.success(""" ## Candidato """)
st.write("Saiba as informações e pontuação de cada candidato.")
if st.button('Ranking'):
    webbrowser.open_new_tab('https://tinyurl.com/votix-br/ranking')


st.write(""" ## Estado """)

uf = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]

sigla = st.selectbox(
    'Estado',
     uf)
cargos = pd.read_json('https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/cargos.json')

cargo = st.selectbox(
    'Cargo',
     cargos['nome'],0)

cargo_id = cargos.query(f'nome == "{cargo}"').values[0,0]

st.write(f""" ## {sigla} | {cargo}""")

# f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos"
# r = requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos", headers=headers)
# st.write(r)
candidatos = requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos", headers=headers ).json()['candidatos']

candidatos_df = pd.DataFrame(candidatos)
candidatos_df['PARTIDO'] = candidatos_df['partido'].apply(lambda x:  x['sigla'])

candidatos_partido = candidatos_df
# candidatos_partido = candidatos_df.query(f'PARTIDO == "{partido}"')

nome = st.selectbox(
    'Candidato',
     candidatos_partido['nomeUrna'])

cid = candidatos_partido.loc[candidatos_partido['nomeUrna'] == nome].values[0,0]
cnum = candidatos_partido.loc[candidatos_partido['nomeUrna'] == nome].values[0,2]

candidato = requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/buscar/2022/{sigla}/2040602022/candidato/{cid}", headers=headers ).json()
# st.write(candidato)
partido_id = candidato['partido']['numero']
partido = candidato['partido']['sigla']

prestacao = requests.get(f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/prestador/consulta/2040602022/2022/{sigla}/{cargo_id}/{partido_id}/{cnum}/{cid}", headers=headers ).json()

candidato['idade'] = ((datetime.now() - pd.to_datetime(candidato['dataDeNascimento']))/365.2425).days

props = ["grauInstrucao", "descricaoTotalizacao", "eleicoesAnteriores", "dataDeNascimento"]
candidato_resumo = pd.Series({p:candidato[p] for p in props}, name=candidato['id'])


# st.write(prestacao)

with st.container():
    st.image(f"https://divulgacandcontas.tse.jus.br/divulga/images/partidos/{partido}.jpg", width=128)
    partido
    
st.info('### Informações')

col1, col2, col3 = st.columns(3)
with col1:
    st.image(candidato['fotoUrl'])
    releeicao = 'Sim' if candidato['st_REELEICAO'] == True else 'Não'
    st.write('Reeleição:', releeicao)
    wk = f"https://pt.wikipedia.org/w/index.php?search="
    tse = f"https://divulgacandcontas.tse.jus.br/divulga/#/candidato/2022/2040602022/{sigla}/{cid}"
    google = f"https://news.google.com/search?q={urllib.parse.quote(candidato['nomeCompleto'])}"
    # st.write(wk)
    # st.write(tse)
    st.write(f"👉 <a target='_blank' href='{tse}'> TSE</a>", unsafe_allow_html=True)
    st.write(f"👉 <a target='_blank' href='{wk}'> WIKIPEDIA</a>", unsafe_allow_html=True)
    st.write(f"👉 <a target='_blank' href='{google}'> GOOGLE</a>", unsafe_allow_html=True)
with col2:
    st.write('#### Dados ')
    st.write('Nome:', candidato['nomeCompleto'])
    st.write('Estado Civil:', candidato['descricaoEstadoCivil'])
    st.write('Raça:', candidato['descricaoCorRaca'])
    st.write('Idade:', str(candidato['idade']))
    st.write('Escolaridade:', candidato['grauInstrucao'])
    st.write('Ocupação:', candidato['ocupacao'])
    st.write('Patrimônio:', '{:,.2f}'.format(candidato['totalDeBens']))
with col3:
    st.write('#### Redes Sociais')
    for link in candidato['sites']:
        st.write(f'* {link}')
# candidato
# candidato_resumo
st.info("### Pontuação")
score = pd.Series(get_score(candidato_resumo)).reset_index().rename({'index':'critério', 0:'pontos'}, axis=1)
st.write(pd.concat([score, pd.DataFrame({'critério': 'média', 'pontos': score['pontos'].mean()}, index=[len(score)])]))
# st.write(pd.concat[score, pd.Series({'critério': 'média', 'pontos': score['pontos'].mean()})])
# st.write(score.mean().round(2))
st.metric('Nota:', str(score['pontos'].mean().round(2)))

fig = px.line_polar(score,  r='pontos', theta='critério', line_close=True, range_r=[0,5])
fig.update_traces(fill='toself')

st.plotly_chart(fig, use_container_width=True)

st.info("### Histórico de Eleições")
eleicoes = pd.DataFrame(candidato['eleicoesAnteriores'])
st.write(eleicoes[['nrAno', 'nomeUrna', 'partido','cargo', 'situacaoTotalizacao']])

st.info("### Despesas")
try:
    st.metric('Total Recebido', '{:,.2f}'.format(prestacao['dadosConsolidados']['totalRecebido']))
except:
    pass
try:
    st.metric('Despesas Contratadas', '{:,.2f}'.format(prestacao['despesas']['totalDespesasContratadas']))
except:
    pass
st.warning("#### Doadores")
st.write(pd.DataFrame(prestacao['rankingDoadores']))



