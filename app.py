import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

#Rodar o codigo com stramlit > python -m stramlit run app.py.

st.set_page_config(page_title='Análise de Funcionários', layout='wide')
st.title('Análise de Funcionários da empresa')

st.sidebar.write('Upload do arquivo Excel')
arquivo = st.sidebar.file_uploader('Seleciona a planilha de funcionários', type=['xlsx'])

if arquivo:
    df = pd.read_excel(arquivo)
    df['Data de Contratacao'] = pd.to_datetime(df['Data de Contratacao'])
    df['Data de Demissao'] = pd.to_datetime(df['Data de Demissao'], errors='coerce')

    #Criar coluna de status
    df['Status'] = df['Data de Demissao'].isna().map({True: 'Ativo', False:'Demitido'})

    #Criar cartões
    total_ativos = df[ df['Status']=='Ativo'].shape[0]
    total_demitidos = df[ df['Status']=='Demitido'].shape[0]
    total_contratacoes = df['Data de Contratacao'].notna().sum()
    folha_salarial = (df['Salario'] + df['VR'] + df['VT'])[df['Status']== 'Ativo'].sum()

    #Filtros
    st.sidebar.markdown('### Filtros')
    status_opcoes = ['Ativo','Demitido']
    status_selecionado = st.sidebar.multiselect('Status', status_opcoes, default=status_opcoes)

    generos = df['Genero'].dropna().unique()
    genero_selecionado = st.sidebar.multiselect('Sexo', sorted(generos), default=sorted(generos))

    
    
    df = df[
        (df['Status'].isin(status_selecionado)) &
        (df['Genero'].isin(genero_selecionado)) 
    ]


    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Ativos', total_ativos)
    col2.metric('Demitidos', total_demitidos)
    col3.metric('Contratações', total_contratacoes)
    col4.metric('Folha Salarial', f"R${folha_salarial:,.2f}")

    #Criar abas dos gráficos
    aba1, aba2, aba3, aba4 = st.tabs(['Visão Geral', 'Gráficos por Área', 'Contratações vs Demissões','Tabela de Dados'])
    with aba1:
         
        contar_genero =  df['Genero'].value_counts()
        #fig = figura (o papel todo)
        #axi = Eixo (ou quadro) desenha os gráficos
        fig1, ax1 = plt.subplots()
        #Criar as barras
        barras = ax1.bar(contar_genero.index, contar_genero.values, color=['skyblue','pink'])
        ax1.set_title('Funcionários por Gênero')
        ax1.bar_label(barras, padding=-15)
        st.pyplot(fig1)

    with aba2:
        col5, col6 = st.columns(2)
        with col5:
            salario_area = df.groupby('Área')['Salario'].median().sort_values()
            fig2, ax2 = plt.subplots()
            salario_area.plot(kind='barh', color='green', ax=ax2)
            ax2.bar_label(ax2.containers[0], padding=-75, fmt='R$ %.2f')
            ax2.set_title('Salário Médio por Área')
            ax2.set_ylabel('')
            st.pyplot(fig2)
        with col6:
            horas_area = df.groupby('Área')['Horas Extras'].sum().sort_values()
            fig3,ax3 = plt.subplots()
            horas_area.plot(kind='barh', color='orange', ax=ax3)
            ax3.set_title('Total de horas extras por áreas')
            ax3.set_ylabel('')
            st.pyplot(fig3)

    with aba3:
        df["Ano Contratacao"] = df["Data de Contratacao"].dt.year
        df["Ano Demissao"] = df["Data de Demissao"].dt.year
        contratacoes_ano = df["Ano Contratacao"].value_counts().sort_index()
        demissoes_ano = df["Ano Demissao"].value_counts().sort_index()

        fig6, ax6 = plt.subplots()
        contratacoes_ano.plot(kind="line", marker="o", label="Contratações", ax=ax6)
        demissoes_ano.plot(kind="line", marker="s", label="Demissões", ax=ax6)
        ax6.set_ylabel("Quantidade")    
        ax6.set_xlabel("")  # Remove o nome do eixo X  
        ax6.legend()
        st.pyplot(fig6)
    
    with aba4:
        st.markdown("### Visualização da Tabela de dados")
        # df["Nome Completo"] = df["Nome"].str.cat(df["Sobrenome"], sep=" ", na_rep="")
        df["Nome Completo"] = df["Nome"] + " " + df["Sobrenome"]
        # Apagando a coluna "Sobrenome"
        df.drop(columns=["Nome","Sobrenome"], inplace=True)
        # Barra de pesquisa
        busca = st.text_input("Pesquisar por nome completo")

        if busca:
            # Filtra linhas que contêm o texto digitado (case insensitive)
            # filtra as linhas que contêm o texto digitado, ignorando maiúsculas/minúsculas.
            # trata valores ausentes (NaN) como False, ou seja, se o campo
            # estiver vazio, não vai causar erro e nem retornar True.
            df_filtrado = df[df["Nome Completo"].str.contains(busca, case=False, na=False)]
        else:
            df_filtrado = df
            # st.dataframe(df)
        st.dataframe(df_filtrado[['Nome Completo', 'Cargo', 'Área', 'Horas Extras', 'Salario']])


else:
    st.warning('Por favor, carregue um arquivo Excel para iniciar a análise')