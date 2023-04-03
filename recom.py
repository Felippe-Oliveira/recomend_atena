import streamlit as st
from collections import Counter
import pandas as pd
import numpy as np
import networkx as nx

st.set_page_config(page_title='RECOM_ATENA.AI',layout='centered')

col1, col2, col3 = st.columns(3)
with col1:
    st.write(' ')
with col2:
    st.image("icon-removebg-preview.png")
    st.header('  ATENA.AI')
with col3:
    st.write(' ')


st.markdown('Este é um sistema de recomendação construído exclusivamente para o uso da empresa Atena.Ai\n\nO objetivo desse sistema visa realizar o teste do sistema na seguinte ordem:')
st.markdown('1° - Verificar os produtos contidos no arquivo csv ou txt e separa-los.\n\n2° - O sistema realiza a análise dos produtos e verifica quais seus vizinhos em vendas, com base nisso, definindo quais as melhores recomendações.\n\n3° - Coleta as recomendações com base na quantidade selecionada pelo usuário, oferecendo posteriormente a opção de baixar os produtos recomendados em csv.')
st.write('\n\n')
st.success('Váriaveis importantes: "product" e "cart"')

data = st.file_uploader('Suba seus dados em csv: ')
if data:
    df_model = pd.read_csv(data,sep="\t|;",header=0,engine='python',dtype=str)
    #tratamento:
    df_model.drop_duplicates(inplace = True)
    df_model = df_model[['product','cart']]
    df_model['peso'] = 1


    product_list = list(df_model['product'].unique())
    selected_product = st.selectbox("Selecione o produto que deseja recomendações:",product_list)
    num_recomend = st.selectbox('Quantas recomendações deseja?', np.arange(1,11))

    st.markdown(f'_Aqui estão as **{num_recomend}** recomendações ideais para esse produto:')

    G = nx.Graph()
    G.add_nodes_from(df_model['product'].unique(), node_type='item')
    G.add_nodes_from(df_model['cart'].unique(), node_type='user')
    G.add_weighted_edges_from(df_model[['cart', 'product','peso']].values)

    def recommend_neighbor_items(G:nx.Graph, target_id, n=10):
        # Validando tipo do nó
        node_type = nx.get_node_attributes(G, 'node_type')[target_id]
        if node_type != 'item':
            raise ValueError('Node is not of item type.')

        # Analisando consumo dos usuários vizinhos
        neighbor_consumed_items = []
        for user_id in G.neighbors(target_id):
            user_consumed_items = G.neighbors(user_id)
            neighbor_consumed_items +=list(user_consumed_items)

        # Contabilizando itens consumidos pelos vizinhos
        consumed_items_count = Counter(neighbor_consumed_items)
        
        # Criando dataframe
        df_neighbors = pd.DataFrame(zip(consumed_items_count.keys(), consumed_items_count.values()))
        df_neighbors.columns = ['item_id', 'score']
        df_neighbors = df_neighbors.sort_values(by='score', ascending=False).set_index('item_id')
        return df_neighbors.iloc[1:].head(n) #o iloc recorta a primeira linha, onde contém o próprio prod solicitado.
    
    resultado = recommend_neighbor_items(G, selected_product, n=num_recomend)
    st.write(resultado)

    csv = resultado.to_csv(index=False).encode('utf-8')
    st.download_button('Baixar recomendações em CSV', csv, file_name='dados.csv', mime='text/csv')


else:
    st.markdown('As variáveis que são reconhecidas para o sistema de recomendação são: **product e cart**')
    st.write('é importante que possuam esses nomes.')

st.write('by: Felippe Oliveira - Aluno de DATA SCIENCE pela DNC')