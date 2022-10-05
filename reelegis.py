import streamlit as st

import pandas as pd
import numpy as np
import plotly.express as px
import numpy
import pathlib
from bs4 import BeautifulSoup
import logging
import shutil
from pathlib import Path

#@st.cache(ttl=60*5)
# def load_data_rel():
#     rel = pd.read_excel('relacao-de-reeleitos.xlsx')
#     return rel

# source venv/bin/activate
col1, mid, col2 = st.beta_columns([4,1,20])
with col1:
    st.image('1-removebg-preview.png', width=99)
with col2:
    st.title("E aí, quem se reelegeu?")

#st.text('Aqui você escolhe o seu/sua Deputado/a Federal!')

st.text("Versão beta 🐟 v.0.0.5")

st.text('Última atualização em 03/10/2022')

st.markdown('No dia 2 de outubro de 2022 você foi às urnas escolher o futuro da nação. Foi uma oportunidade valiosa para escolher como será a nova composição do Congresso Nacional. A Plataforma reeLegis te mostra como os deputados  e as deputadas federais candidatos à reeleição em 2022 apresentaram suas propostas. Com o uso de aprendizagem computacional, a plataforma permite analisar e comparar a atuação de todos os Deputados e Deputadas Federais que buscam a reeleição. **E aí, reelegeu ou renovou?**')

st.markdown('[Aqui, você pode retornar ao site.](https://reelegis.netlify.app)')





    #st.warning('Consulte nosso relatório completo [aqui](link do relatorio)')

st.header("Resultados gerais 📊")

@st.cache(ttl=60*5)
def load_data_rel():
    rel = pd.read_excel('relacao-de-reeleitos-all.xlsx')
    return rel

reeleitos = load_data_rel()

reeleitos = reeleitos.dropna()

se_reelegeu = reeleitos[reeleitos.reeleito == 'sim'].count()
taxa_de_reeleicao = se_reelegeu.iloc[0] /471 * 100
taxa_de_renovacao = 100 -taxa_de_reeleicao
taxas = [['Composição da Câmara',taxa_de_reeleicao],['Composição da Câmara', taxa_de_renovacao]]
taxas = pd.DataFrame(taxas, columns=['Taxa', 'Porcentagem'])
rotulos = ['Reeleição', 'Renovação']
taxas['Taxa de'] = rotulos
figura_pizza=px.bar(taxas,x="Porcentagem",y='Taxa',
orientation='h', color_continuous_scale='Tealgrn',color='Taxa de',
color_discrete_map={"Reeleição": '#21ADA8',
"Renovação": '#C0C0C0'},
labels=dict(Taxa="", Porcentagem="% Porcentagem"))
figura_pizza.update_layout(showlegend=True, yaxis={'categoryorder': 'total ascending'})
figura_pizza.update_traces(width=.6)

st.info(f'**{round(taxa_de_reeleicao)}%** dos parlamentares que concorreram à reeleição conseguiram uma cadeira na Câmara dos Deputados. A Câmara dos Deputados foi renovada em **{round(taxa_de_renovacao)}%**.')
#st.info(f"Nas eleições de 2022, **{round(taxa_de_reeleicao)}%** dos parlamentares concorrendo à reeleição conseguiram se reeleger. Consequentemente, o Congresso Nacional foi renovado em **{round(taxa_de_renovacao)}%**.")

st.plotly_chart(figura_pizza, use_container_width=True)

    #figura_pizza = px.bar(taxas, values='Porcentagem', names='Taxa', color_discrete_sequence=px.colors.qualitative.Pastel)
    # figura_pizza=px.bar(taxas, x='Porcentagem', y='Taxa', orientation='h',
    # color_discrete_sequence=px.colors.qualitative.Pastel)

    # st.plotly_chart(figura_pizza, use_container_width=True)

    # estados
st.header('Resultados por Estado 🇧🇷')

sim_estado = reeleitos[reeleitos.reeleito == 'sim']
sim_estado = sim_estado.groupby(by=['estado_por_extenso']).sum()
sim_estado = pd.DataFrame(sim_estado).reset_index()
sim_estado.rename(columns = {'tentou_reeleicao':'total_sim'}, inplace = True)
nao_estado = reeleitos[reeleitos.reeleito == 'não']
nao_estado = nao_estado.groupby(by=['estado_por_extenso']).sum()
nao_estado = pd.DataFrame(nao_estado).reset_index()
nao_estado.rename(columns = {'tentou_reeleicao':'total_nao'}, inplace = True)
nao_estado.rename(columns = {'estado_por_extenso':'ESTADO'}, inplace = True)
por_estado = pd.concat([sim_estado, nao_estado], axis=1)
    #por_estado = por_estado.drop(por_estado.columns[], axis=1)
por_estado['porcentagem_sucesso'] = por_estado['total_sim']/(por_estado['total_sim'] + por_estado['total_nao']) * 100
por_estado['porcentagem_sem_sucesso'] = por_estado['total_nao']/(por_estado['total_sim'] + por_estado['total_nao']) * 100
reeleitos_por_estado = ["% de Parlamentares reeleitos"] * len(por_estado['estado_por_extenso'])
nao_reeleitos_por_estado = ["% de Parlamentares não reeleitos"] * len(por_estado['estado_por_extenso'])
#st.write(len(por_estado['estado_por_extenso']))
novos_estados_sucesso = por_estado[['estado_por_extenso', 'porcentagem_sucesso']]
novos_estados_sucesso['reeleitos'] = reeleitos_por_estado
novos_estados_sucesso.rename(columns = {'porcentagem_sucesso':'porcentagem'}, inplace = True)

novos_estados_sem_sucesso = pd.DataFrame(por_estado[['estado_por_extenso', 'porcentagem_sem_sucesso']])
novos_estados_sem_sucesso['reeleitos'] = nao_reeleitos_por_estado
novos_estados_sem_sucesso.rename(columns = {'porcentagem_sem_sucesso':'porcentagem'}, inplace = True)
h = pd.concat([novos_estados_sucesso,novos_estados_sem_sucesso])
# st.write(h)

rotulos_estados = por_estado.sort_values(by= 'porcentagem_sucesso', ascending=True)
lista_rotulos_estados = rotulos_estados['estado_por_extenso']
#st.write(lista_rotulos_estados)
    ## grafico
figura_estado=px.bar(h, x='porcentagem', y='estado_por_extenso', height=650,
orientation='h', color='reeleitos', #barmode='group', #color_continuous_scale='Tealgrn',
color_discrete_map={"% de Parlamentares reeleitos": '#21ADA8',
"% de Parlamentares não reeleitos": '#C0C0C0'},
labels=dict(estado_por_extenso="", porcentagem="% Porcentagem"))
#figura_estado.update_layout(showlegend=True, yaxis={'categoryorder': 'total ascending'})
figura_estado.update_yaxes(categoryarray=lista_rotulos_estados)

max_min_estado = por_estado.sort_values(by= 'porcentagem_sucesso', ascending=False)

max_estado = max_min_estado.iloc[:1]
min_estado = max_min_estado.iloc[:-1]
estado_com_maior_taxa = max_estado['estado_por_extenso'].iloc[0]
estado_com_menor_taxa = max_min_estado['estado_por_extenso'].iloc[-1]
minimo = round(min(max_min_estado['porcentagem_sucesso']))


porcentagem_estado_max= int(max_estado['porcentagem_sucesso'].iloc[:1])
    #porcentagem_estado_min= int(min_estado['porcentagem_sucesso'].iloc[:-1])
st.info(f"""
A Unidade Federativa **{estado_com_maior_taxa}** teve uma taxa de **{porcentagem_estado_max}%** de reeleição. Em contrapartida, **{estado_com_menor_taxa}** teve a menor taxa de reeleição, com **{minimo}%**, tendo uma renovação de **{100-minimo}%**.
""")
# st.info(f"""
# **{estado_com_maior_taxa}** está a frente na taxa de reeleição. O estado conta com **{porcentagem_estado_max}%** de Deputados e Deputadas Federais da legislatura anterior.
#
# Em contrapartida, **{estado_com_menor_taxa}** tem menor taxa de reeleição, com **{minimo}%**, tendo renovação de **{100-minimo}%**.
# """)

st.plotly_chart(figura_estado, use_container_width=True)

    ###
    # mapa
    # st.write(por_estado)
    # st.write(localidade)
    # mapa = pd.concat([por_estado, localidade], axis=1)
    # # st.write(mapa)
    # ## por partido
    # mapa_reeleicao = px.scatter_mapbox(mapa, lat="lat", lon="lon", hover_name="UF",
    #               color_continuous_scale=px.colors.cyclical.IceFire, zoom=4,
    #               size = "porcentagem_sucesso", color='porcentagem_sucesso',
    #               mapbox_style="open-street-map")
    # mapa_reeleicao.update_layout(showlegend=True)
    #st.plotly_chart(mapa_reeleicao)

    #
    # m = px.choropleth( mapa, #soybean database
    # locations = "UF", #define the limits on the map/geography
    # geojson = localidade, #shape information
    # color = "porcentagem_sucesso", #defining the color of the scale through the database
    # hover_name = "UF", #the information in the box
    # hover_data =["porcentagem_sucesso","lat","lon"])
    # st.plotly_chart(m)



st.header('Resultados por Partido 🏛️')

sim_partido = reeleitos[reeleitos.reeleito == 'sim']
sim_partido = sim_partido.groupby(by=['partido_ext_sigla']).sum()
sim_partido = pd.DataFrame(sim_partido).reset_index()
sim_partido.rename(columns = {'tentou_reeleicao':'total_sim'}, inplace = True)
nao_partido = reeleitos[reeleitos.reeleito == 'não']
nao_partido = nao_partido[nao_partido.partido_ext_sigla != 'Partido Trabalhista Brasileiro ( PTB )']
nao_partido = nao_partido.groupby(by=['partido_ext_sigla']).sum()
nao_partido = pd.DataFrame(nao_partido).reset_index()
nao_partido.rename(columns = {'tentou_reeleicao':'total_nao'}, inplace = True)
sim_partido.rename(columns = {'partido_ext_sigla':'partido'}, inplace = True)
por_partido = pd.concat([sim_partido, nao_partido], axis=1)

    #por_estado = por_estado.drop(por_estado.columns[], axis=1)
por_partido['porcentagem_sucesso'] = por_partido['total_sim']/(por_partido['total_sim'] + por_partido['total_nao']) * 100
por_partido['porcentagem_sem_sucesso'] = por_partido['total_nao']/(por_partido['total_sim'] + por_partido['total_nao']) * 100
#     ## grafico
# figura_partido=px.bar(por_partido, x='porcentagem_sucesso', y='partido_ext_sigla',
# height=700,
# orientation='h', color='porcentagem_sucesso', color_continuous_scale='Tealgrn',
# labels=dict(partido_atual="", porcentagem_sucesso="% Reeleição"))
# figura_partido.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})

reeleitos_por_partido = ["% de Partidos reeleitos"] * len(por_partido['partido_ext_sigla'])
nao_reeleitos_por_partido = ["% de Partidos não reeleitos"] * len(por_partido['partido_ext_sigla'])
#st.write(len(por_estado['estado_por_extenso']))
novos_partidos_sucesso = por_partido[['partido_ext_sigla', 'porcentagem_sucesso']]
novos_partidos_sucesso['reeleitos'] = reeleitos_por_partido
novos_partidos_sucesso.rename(columns = {'porcentagem_sucesso':'porcentagem'}, inplace = True)

novos_partidos_sem_sucesso = pd.DataFrame(por_partido[['partido_ext_sigla', 'porcentagem_sem_sucesso']])
novos_partidos_sem_sucesso['reeleitos'] = nao_reeleitos_por_partido
novos_partidos_sem_sucesso.rename(columns = {'porcentagem_sem_sucesso':'porcentagem'}, inplace = True)
pl = pd.concat([novos_partidos_sucesso,novos_partidos_sem_sucesso])
# st.write(h)

rotulos_partidos = por_partido.sort_values(by= 'porcentagem_sucesso', ascending=True)
lista_rotulos_partidos = rotulos_partidos['partido_ext_sigla']


max_min_partido = por_partido.sort_values(by= 'porcentagem_sucesso', ascending=False)

max_partido = max_min_partido.iloc[:1]
min_partido = max_min_partido.iloc[:-1]
partido_com_maior_taxa = max_partido['partido_ext_sigla'].iloc[0]
partido_com_menor_taxa = max_min_partido['partido_ext_sigla'].iloc[-1]
minimo_partido = round(min(max_min_partido['porcentagem_sucesso']))

porcentagem_partido_max= int(max_partido['porcentagem_sucesso'].iloc[:1])
    #porcentagem_estado_min= int(min_estado['porcentagem_sucesso'].iloc[:-1])
figura_partido=px.bar(pl, x='porcentagem', y='partido_ext_sigla', height=650,
orientation='h', color='reeleitos', #barmode='group', #color_continuous_scale='Tealgrn',
color_discrete_map={"% de Partidos reeleitos": '#21ADA8',
"% de Partidos não reeleitos": '#C0C0C0'},
labels=dict(partido_ext_sigla="", porcentagem="% Porcentagem"))
#figura_estado.update_layout(showlegend=True, yaxis={'categoryorder': 'total ascending'})
figura_partido.update_yaxes(categoryarray=lista_rotulos_partidos)
st.info(f"""
O **{partido_com_maior_taxa}** teve uma taxa de **{porcentagem_estado_max}%** de reeleição. Em contrapartida, **{partido_com_menor_taxa}** teve a menor taxa de reeleição, com **{minimo_partido}%**, tendo uma renovação de **{100-minimo_partido}%**.
""")
st.plotly_chart(figura_partido, use_container_width=True)



# st.plotly_chart(figura_partido, use_container_width=True)
@st.cache(ttl=60*5)
def load_enfase():
    data_enfase = pd.read_excel('enfase-reeleitos.xlsx')
    return data_enfase
enfase = load_enfase()
enfase = enfase.dropna()


st.header('Consulte todos os parlamentares candidatos à reeleição em 2022 ⬇️')

if st.checkbox("Consultar Parlamentares e Partidos por Estado", False):
    st.header('Escolha o Estado')
    uf = reeleitos['estado_por_extenso'].unique()
    uf = np.append(uf, '')
    uf.sort()
    uf_escolha = st.selectbox("Selecione o Estado", uf)
    if uf_escolha != '':
        if uf_escolha == 'Acre':
            reeleicao_no_acre = reeleitos.loc[reeleitos.estado_por_extenso == 'Acre', :]
            reeleicao_no_acre = reeleicao_no_acre[reeleicao_no_acre.reeleito == 'sim']
            acre = reeleicao_no_acre[['nome_candaditado', 'partido_ext_sigla']]
            acre.rename(columns = {'nome_candaditado':'Parlamentar'}, inplace = True)
            acre.rename(columns = {'partido_ext_sigla':'Partido'}, inplace = True)
            #acre.rename(columns = {'estado_por_extenso':'Estado'}, inplace = True)
            acre = pd.DataFrame(acre).set_index('Parlamentar')
            if st.checkbox('Visualizar relação de Parlamentares reeleitos', False):
                st.table(acre)
            st.header('Ênfase Temática dos Parlamentares reeleitos')
            st.warning('Na Unidade Federativa **Acre**, **Antônia Lúcia ( REPUBLICANOS )** assumiu como suplente após a coleta dos dados. Portanto, a ênfase temática no gráfico abaixo é do partido dela, o **Republicanos ( REPUBLICANOS )**.')
            enfase_acre = enfase.loc[enfase.nomeUrna == 'Antônia Lucia ( REPUBLICANOS )', :]
            enfase_acre.prop_mean = enfase_acre.prop_mean * 100
            estado_parla = px.bar(enfase_acre, x='prop_mean', y='label_pt', height=500, color='prop_mean',
        #color_continuous_scale=px.colors.sequential.Viridis,
            color_continuous_scale='Sunsetdark',
        # site com as cores: https://plotly.com/python/builtin-colorscales/
            labels=dict(label_pt="", prop_mean="Ênfase Temática %"), orientation='h')
            estado_parla.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(estado_parla, use_container_width=True)
            maior_enfase = pd.DataFrame(enfase_acre[['label_pt', 'prop_mean']]).sort_values(by = ['prop_mean'],
            ascending=False)
            #first = maior_enfase.iloc[:-1].round()

            #maior_enfase_label = maior_enfase.iloc[0]
            maior_enfase_percent = maior_enfase.iloc[:1]
            rotulo = maior_enfase_percent['label_pt'].iloc[:1]
            porcentagem = int(maior_enfase_percent['prop_mean'].iloc[:1])
            #st.write(maior_enfase_label)



            #st.info(f'**{escolha_parlamentar_do_estado}** apresentou **{str(n_proposta_uf)} propostas legislativas** ao total. A maior ênfase temática d{genero.index[0]} foi **{saliente_uf.index[0]}**, com aproximadamente **{first}% do total.**')
            st.info(f'O tema de maior ênfase média nas propostas apresentadas pelo partido de **Antônia Lúcia ( REPUBLICANOS )** é **{rotulo.to_string(index=False)}**, com **{porcentagem}%** do total.')

        else:
            reeleicao_no_estado = reeleitos.loc[reeleitos.estado_por_extenso == uf_escolha, :]
            st.title(f'Parlamentares reeleitos na Unidade Federativa **{uf_escolha}**')
            filtro_de_reeleitos = reeleicao_no_estado[reeleicao_no_estado.reeleito == 'sim']
            quantidade_de_reeleitos = len(filtro_de_reeleitos)
            taxa_reeleicao_estado = por_estado[por_estado.estado_por_extenso == uf_escolha]
            tx_estado = taxa_reeleicao_estado['porcentagem_sucesso'].iloc[0]
            st.info(f"""
                A Unidade Federativa **{uf_escolha}** teve uma taxa de **reeleição** de **{round(tx_estado)}%**. O estado agora conta com **{round(100-tx_estado)}%** de **renovação** na Câmara dos Deputados.
                """)
            reeleicao_estados = reeleitos.loc[reeleitos.estado_por_extenso == uf_escolha, :]
            reeleicao_estados = reeleicao_estados[reeleicao_estados.reeleito == 'sim']
            geral_estados = reeleicao_estados[['nome_candaditado', 'partido_ext_sigla']]
            geral_estados.rename(columns = {'nome_candaditado':'Parlamentar'}, inplace = True)
            geral_estados.rename(columns = {'partido_ext_sigla':'Partido'}, inplace = True)
            todos_estados = pd.DataFrame(geral_estados).set_index('Parlamentar')
            #todos_estados = todos_estados.rename_axis("limbs", axis="columns")
            if st.checkbox('Visualizar relação de Parlamentares reeleitos', False):
                st.table(todos_estados)
            st.header('Ênfase Temática dos Parlamentares reeleitos')
            enfase_total = enfase.loc[enfase.estado_por_extenso == uf_escolha, :]

            nomes_reeleitos = enfase_total['nomeUrna'].unique()
            quantidade_de_reeleitos_por_estado = len(nomes_reeleitos)
            enfase_grafico = enfase_total[['label_pt', 'prop_mean']]
            enfase_grafico = enfase_grafico.groupby('label_pt').sum() / quantidade_de_reeleitos_por_estado * 100

            estado_parla = px.bar(enfase_grafico, x='prop_mean', height=500, color='prop_mean',
            #color_continuous_scale=px.colors.sequential.Viridis,
            color_continuous_scale='Sunsetdark',
            # site com as cores: https://plotly.com/python/builtin-colorscales/
            labels=dict(label_pt="", prop_mean="Ênfase Temática %"), orientation='h')
            estado_parla.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(estado_parla, use_container_width=True)


            #sorteio = random_val.loc[random_val.label_pt == random_tema]
            maior_enfase = pd.DataFrame(enfase_grafico[['prop_mean']]).sort_values(by = ['prop_mean'],
            ascending=False).reset_index()

            #first = maior_enfase.iloc[:-1].round()

            #maior_enfase_label = maior_enfase.iloc[0]
            maior_enfase_percent = maior_enfase.iloc[:1]
                #rotulo = maior_enfase_percent['label_pt'].iloc[:0]
            porcentagem = int(maior_enfase_percent['prop_mean'].iloc[:1])
            #st.write(maior_enfase_label)
            rotulo = maior_enfase_percent['label_pt'].iloc[:1]

            st.info(f'O tema de maior ênfase média nas propostas apresentadas pelos Parlamentares reeleitos do Estado é **{rotulo.to_string(index=False)}**, com **{porcentagem}%** do total.')


st.header('📢  Conta pra gente!')
st.warning('Fique à vontade para nos informar sobre algo que queria ter visto nesta aba ou sobre a plataforma, para melhorarmos no futuro!')
contact_form = """
            <form action="https://formsubmit.co/reelegis@gmail.com" method="POST">
            <input type="hidden" name="_captcha" value="false">
            <input type="text" name="name" placeholder="Nome" required>
            <input type="email" name="email" placeholder="E-mail" required>
            <textarea name="message" placeholder="Sua mensagem"></textarea>
            <button type="submit">Enviar</button>
            </form>
            """
st.markdown(contact_form, unsafe_allow_html=True)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style.css")


            #st.info(f'**{escolha_parlamentar_do_estado}** apresentou **{str(n_proposta_uf)} propostas legislativas** ao total. A maior ênfase temática d{genero.index[0]} foi **{saliente_uf.index[0]}**, com aproximadamente **{first}% do total.**')
