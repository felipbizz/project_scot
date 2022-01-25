# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from geopy import Nominatim
import geopandas as gpds
import time

import re

local_setado = input('Digite o local:')

geocode_setado = gpds.tools.geocode(local_setado, provider = "nominatim", user_agent="Intro Geocode", timeout=10)

table_MN = pd.read_html('https://www.scotconsultoria.com.br/cotacoes/boi-gordo/?ref=smnb')

df = table_MN[0]

data_coleta = df.columns[0]

df = df.dropna(axis='columns')
df = df.drop([0,1,34,35,36,37,38,39,40])
df.columns = ['locais','preco_arroba','preco_30dias','dif_relac_SP','precos_brut','precos_brut_30d']

list_addr = df['locais'].astype(str).values.tolist()

addr_to_statename = {
    #Estados
    'AC': 'Acre,',
    'AL': 'Alagoas,',
    'AP': 'Amapá,',
    'AM': 'Amazonas,',
    'BA': 'Bahia,',
    'CE': 'Ceará,',
    'DF': 'Distrito Federal,',
    'ES': 'Espírito Santo,',
    'GO': 'Goiás,',
    'MA': 'Maranhão,',
    'MT': 'Mato Grosso,',
    'MS': 'Mato Grosso do Sul,',
    'MG': 'Minas Gerais,',
    'PA': 'Pará,',
    'PB': 'Paraíba,',
    'PR': 'Paraná,',
    'PE': 'Pernambuco,',
    'PI': 'Piauí,',
    'RJ': 'Rio de Janeiro,',
    'RN': 'Rio Grande do Norte,',
    'RS': 'Rio Grande do Sul,',
    'RO': 'Rondônia,',
    'RR': 'Roraima,',
    'SC': 'Santa Catarina,',
    'SP': 'São Paulo,',
    'SE': 'Sergipe,',
    'TO': 'Tocantins,',
}

#Será necessário corrigir nomes para encontrar endereço correto.
correcao = {
    'Goiás, Reg. Sul': 'Jataí',
    'Minas Gerais, Norte': 'Montes Claros',
    'Minas Gerais, Sul': 'Juiz de Fora',
    'Rio Grande do Sul, Oeste': 'Porto Alegre',
    'Bahia, Sul': 'Vitória da Conquista',
    'Bahia, Oeste': 'Salvador',
    'Mato Grosso, Norte': 'Juara',
    'Mato Grosso, Sudoeste': 'Nova Xavantina',
    'Mato Grosso, Sudeste': 'Pontes e Lacerda',
    'Paraná, Noroeste': 'Paranavaí',
    'Santa Catarina, Oeste': 'Florianópolis',
    'Maranhão, Oeste': 'Teresina',
    'Rondônia, Sudeste': 'Vilhena',
    'Tocantins, Sul': 'Palmas',
    'Tocantins, Norte': 'Araguaína',
}

def multiple_replace(lookup, text):
  """Perform substituions that map strings in the lookup table to valuees (modification from https://stackoverflow.com/questions/15175142/how-can-i-do-multiple-substitutions-using-regex-in-python)"""
  # re.IGNORECASE flags allows provides case insensitivity (i.e. matches New York, new york, NEW YORK, etc.)
  regex = re.compile(r'\b(' + r'|'.join(lookup.keys()) + r')\b')

  # For each match, look-up corresponding value in dictionary and peform subsstituion
  # we convert match to title to capitalize first letter in each word
  return regex.sub(lambda mo: lookup[mo.string[mo.start():mo.end()]], text)


local = []
for i in list_addr:    
  local.append(multiple_replace(addr_to_statename, i))

local_reg = []
for i in local:
  local_reg.append(multiple_replace(correcao, i))

#string = 'Brasil, '
#local_br = [ string + x for x in local_reg]

geocode_scot = gpds.tools.geocode(local_reg, provider = "nominatim", user_agent="Intro Geocode", timeout=10)

df_prices = df[['preco_arroba','preco_30dias','precos_brut','precos_brut_30d']].astype('float64')
df_prices.reset_index(drop=True, inplace=True)
df_prices = df_prices.div(100)

distancias = geocode_scot.geometry.apply(lambda g: geocode_setado.distance(g))
distancias = pd.DataFrame(distancias)

distancias.columns = ['distancias/km']
distancias = distancias.mul(111.12)

df.reset_index(drop=True, inplace=True)

t = pd.concat([df_prices, distancias], axis=1)

local_br = pd.DataFrame(local_reg)
local_br.columns = ['locais']

v = pd.concat([local_br, t], axis=1)
v = v.set_index('locais')

mins = v.loc[v['distancias/km'].idxmin()]

print(f'  O preço para essa localização é de R${mins[0]}.\n Foi utilizada a referência de {mins.name}, que está a aproximandamente {round(mins[4],2)}km de distância')

