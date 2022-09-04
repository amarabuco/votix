import streamlit as st
from datetime import datetime
import pandas as pd
import requests

headers = { "accept": "application/json"}

st.write(""" # Votix """)
st.write(""" O aplicativo Votix apresenta informações e cálculos para auxiliar o eleitor 
         a tomar uma decisão informada e consciente sobre seus candidatos aos cargos eletivos. """)
st.write(""" Dados: https://divulgacandcontas.tse.jus.br/divulga/ """)
st.write(""" Código: https://github.com/amarabuco/votix """)
