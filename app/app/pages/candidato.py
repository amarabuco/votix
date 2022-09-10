import streamlit as st
import plotly.express as px
from datetime import datetime
import pandas as pd
import requests
import urllib.parse
from utils import get_score
import webbrowser

# wordcloud
from bs4 import BeautifulSoup
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
from stqdm import stqdm
import matplotlib.pyplot as plt

st.set_page_config(
    page_title='Votix - Candidato',
    page_icon="📊",
    layout='wide'
)


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
st.write(f"👉 <a target='_blank' href='https://tinyurl.com/votix-br/ranking'> RANKING</a>", unsafe_allow_html=True)


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
    wk = f"https://pt.wikipedia.org/w/index.php?search={urllib.parse.quote(candidato['nomeCompleto'])}"
    tse = f"https://divulgacandcontas.tse.jus.br/divulga/#/candidato/2022/2040602022/{sigla}/{cid}"
    news = f"https://news.google.com/search?q={urllib.parse.quote(candidato['nomeCompleto'])}"
    google = f"https://www.google.com/search?q={urllib.parse.quote(candidato['nomeCompleto'])}"
    lattes = f"http://buscatextual.cnpq.br/buscatextual/busca.do"
    # st.write(wk)
    # st.write(tse)
    st.write(f"👉 <a target='_blank' href='{tse}'> TSE</a>", unsafe_allow_html=True)
    st.write(f"👉 <a target='_blank' href='{wk}'> WIKIPEDIA</a>", unsafe_allow_html=True)
    st.write(f"👉 <a target='_blank' href='{news}'> NOTÍCIAS</a>", unsafe_allow_html=True)
with col2:
    st.write('#### 📋 Dados ')
    st.write('🏷 Nome:', candidato['nomeCompleto'])
    st.write('💍 Estado Civil:', candidato['descricaoEstadoCivil'])
    st.write('🎨 Cor:', candidato['descricaoCorRaca'])
    st.write('⏳ Idade:', str(candidato['idade']))
    st.write('📚 Escolaridade:',  f"{candidato['grauInstrucao']} <a target='_blank' href='{lattes}'> LATTES</a>", unsafe_allow_html=True)
    st.write('🛠  Ocupação:', candidato['ocupacao'])
    st.write('💼 Partido:', partido)
    # st.write('Patrimônio:', '{:,.2f}'.format(candidato['totalDeBens']))
    st.write('💰 Patrimônio:', '{:,.2f}'.format(candidato['totalDeBens']))
with col3:
    st.write('#### Redes Sociais')
    for link in candidato['sites']:
        st.write(f'* {link}')
# candidato
# candidato_resumo
if cargo_id == 3:
    st.info("### Proposta")
    proposta = f"https://raw.githubusercontent.com/amarabuco/votix/data/app/app/data/propostas/{sigla}/2022{sigla}{candidato['id']}.pdf"
    st.write(f"📔 <a target='_blank' href='{proposta}'> PROPOSTA</a>", unsafe_allow_html=True)

st.info("### Nuvem de palavras")
if st.button('Gerar'):
    results = []
    for page in stqdm([1,10,20,30]):
        r = requests.get(f"https://www.google.com/search?q={candidato['nomeCompleto']}&start={page}")
        soup = BeautifulSoup(r.text, 'html.parser')
        for h in soup.find_all('h3'):
            for s in h.parent.parent.parent :
                text = s.nextSibling
                if text != None:
                    results.append(text.text.lower())
    
    STOPWORDS = requests.get('https://raw.githubusercontent.com/amarabuco/votix/main/app/app/data/stopwords.txt').text.split(' ')
        
    for w in candidato['nomeCompleto'].split(' '):
        STOPWORDS.append(w)
    # Start with one review:
    words = "".join(results)

    # Create and generate a word cloud image:
    wordcloud = WordCloud(stopwords=STOPWORDS, background_color='black', width=800, height=400).generate(words)

    # Display the generated image:
    # fig, ax = plt.subplots(figsize=(15,15))
    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis("off")
    st.image(wordcloud.to_image())
    st.caption('Fonte: Google. 4 primeiras páginas da pesquisa')    
    st.write(f"👉 <a target='_blank' href='{google}'> GOOGLE</a>", unsafe_allow_html=True)
    
                    
else:
    st.write(f"👉 <a target='_blank' href='{google}'> GOOGLE</a>", unsafe_allow_html=True)

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
