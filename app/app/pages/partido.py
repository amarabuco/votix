import streamlit as st
from datetime import datetime
import pandas as pd
import requests
from stqdm import stqdm
import urllib.parse

st.set_page_config(
    page_title='Votix - Partido',
    page_icon="📊",
    layout='wide'
)

headers = {"accept": "application/json",
           "User-Agent": "Mozilla/5.0"
           }


st.write(""" # 📊  Votix """)
st.write(""" ## Partidos """)
st.write("Conheça as características dos candidatos por Estado, Cargo e Partido")

uf = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT",
      "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]

sigla_uf = st.selectbox(
    'Estado',
    uf, 15)

cargos = pd.read_json(
    './data/cargos.json')
# cargos = pd.read_json('/Volumes/EXT/myApps/votix/app/app/data/cargos.json')

cargo = st.selectbox(
    'Cargo',
    cargos['nome'])

cargo_id = cargos.query(f'nome == "{cargo}"').values[0, 0]

municipios = requests.get(
    f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/eleicao/buscar/{sigla_uf}/2045202024/municipios", headers=headers).json()["municipios"]

sigla = st.selectbox(
    'Município',
    municipios, format_func=lambda x: x['nome'])

municipio = sigla['nome']

sigla = sigla['codigo']

partidos = pd.read_json('./data/partidos.json')

partidos = partidos.sort_values(by='sigla')
partido = st.selectbox(
    'Partido',
    partidos['sigla'])

partido_id = partidos.query(f'sigla == "{partido}"').values[0, 0]

# st.write('Estado: ', sigla, 'Cargo: ', cargo, 'Partido:', partido)

partido_info = requests.get(
    f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/prestador/consulta/partido/2030402020/2020/{sigla}/3/{partido_id}", headers=headers).json()

partido_info

st.write(f""" ## {sigla} | {cargo} | {partido} """)
# st.image(
#     f"https://divulgacandcontas.tse.jus.br/divulga/images/partidos/{partido}.jpg")
# nomePartido = partido_info['nomePartido']
# if not ("Partido" in nomePartido):
#     nomePartido = 'Partido ' + nomePartido

st.write("https://pt.wikipedia.org/w/index.php?search={}".format(urllib.parse.quote(nomePartido)))

# f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos"
candidatos = requests.get(
    f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2022/{sigla}/2040602022/{cargo_id}/candidatos", headers=headers).json()['candidatos']

candidatos_df = pd.DataFrame(candidatos)
candidatos_df['PARTIDO'] = candidatos_df['partido'].apply(
    lambda x:  x['sigla'])

candidatos_partido = candidatos_df.query(f'PARTIDO == "{partido}"')

if len(candidatos_partido) == 0:
    st.write(""" Não há dados """)
else:
    candidatos_completo = pd.DataFrame()
    total = len(candidatos_partido)
    for row in stqdm(range(total)):
        cid = candidatos_partido.iloc[row]['id']
        # cid
        # f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/buscar/2022/{sigla}/2040602022/candidato/{cid}"
        candidato = requests.get(
            f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/buscar/2022/{sigla}/2040602022/candidato/{cid}", headers=headers).json()
        props = ['descricaoSexo', 'descricaoEstadoCivil', 'descricaoCorRaca', 'grauInstrucao', 'ocupacao',
                 'dataDeNascimento', 'totalDeBens', 'nomeMunicipioNascimento', 'st_MOTIVO_FICHA_LIMPA']
        cs = pd.Series({p: candidato[p] for p in props}, name=candidato['id'])
        # cs
        # st.write(pd.Series(cs))
        # pd.DataFrame(candidato.values())
        cs['idade'] = (
            (datetime.now() - pd.to_datetime(candidato['dataDeNascimento']))/365.2425).days
        candidatos_completo = candidatos_completo.append(cs)
    try:
        st.write('Receita: ', "{:,.2f}".format(
            partido_info['dadosConsolidados']['totalRecebido']))
        st.write('Despesa: ', "{:,.2f}".format(
            partido_info['despesas']['totalDespesasPagas']))
    except:
        pass
    st.write('Candidatos: ', str(len(candidatos_partido)))

    # candidatos_completo

    # tabs = st.tabs(props)

    # for t, p in zip(tabs, props):
    for p in props:

        st.write(f""" ### {p.replace("descricao", "")} """)
        if (p == 'totalDeBens'):
            df = candidatos_completo[p].describe()
            st.write(df)
        if (p == 'dataDeNascimento'):
            df = candidatos_completo['idade'].describe()
            st.write(df)
        else:
            df = candidatos_completo.groupby(p)[p].count()
            st.bar_chart(pd.DataFrame(df.values, index=df.index))
            st.write(
                pd.concat([df, ((df/df.sum()).round(2) * 100).rename('%')], axis=1))


# df_uf = pd.DataFrame(uf)

# st.write(""" ## Candidato """)

# candidato = requests.get("https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/buscar/2022/PE/2040602022/candidato/170001610442", headers=headers ).json()

# st.write(candidato)
