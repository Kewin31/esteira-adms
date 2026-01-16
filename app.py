import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Configuração da página
st.set_page_config(
    page_title="Esteira de Demandas ADMS",
    page_icon="📊",
    layout="wide"
)

# Título com atualização
st.title("📊 Esteira de Demandas ADMS")

# Processar o arquivo CSV
@st.cache_data
def load_data(file):
    # Ler o arquivo CSV
    content = file.getvalue().decode('utf-8-sig')
    
    # Encontrar onde começam os dados (após o schema)
    lines = content.split('\n')
    
    # Procurar a linha de cabeçalho
    header_line = None
    for i, line in enumerate(lines):
        if line.startswith('"Chamado","Tipo Chamado"'):
            header_line = i
            break
    
    if header_line is None:
        # Tentar encontrar com formato ligeiramente diferente
        for i, line in enumerate(lines):
            if '"Chamado"' in line and '"Tipo Chamado"' in line:
                header_line = i
                break
    
    if header_line is None:
        st.error("Não foi possível encontrar o cabeçalho dos dados no arquivo.")
        return pd.DataFrame()
    
    # Ler os dados a partir da linha do cabeçalho
    data_str = '\n'.join(lines[header_line:])
    df = pd.read_csv(io.StringIO(data_str), quotechar='"')
    
    # Renomear colunas para padronizar
    col_mapping = {
        'Chamado': 'Chamado',
        'Tipo Chamado': 'Tipo Chamado',
        'Responsável': 'Responsável',
        'Status': 'Status',
        'Criado': 'Criado',
        'Modificado': 'Modificado',
        'Modificado por': 'Modificado por',
        'Prioridade': 'Prioridade',
        'Sincronização': 'Sincronização',
        'SRE': 'SRE',
        'Empresa': 'Empresa',
        'Revisões': 'Revisões'
    }
    
    # Renomear colunas para nomes mais consistentes
    df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})
    
    # Converter colunas de data
    date_columns = ['Criado', 'Modificado']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', format='ISO8601')
    
    # Extrair ano da data de criação
    if 'Criado' in df.columns:
        df['Ano'] = df['Criado'].dt.year
    
    # Converter Revisões para numérico
    if 'Revisões' in df.columns:
        df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
    
    return df

# Interface principal
uploaded_file = st.file_uploader("📁 Carregue o arquivo CSV da Esteira de Demandas", type=['csv'])

if uploaded_file is not None:
    # Carregar dados
    df = load_data(uploaded_file)
    
    if not df.empty:
        # Mostrar data de atualização
        last_update = df['Modificado'].max() if 'Modificado' in df.columns else datetime.now()
        st.sidebar.markdown(f"**Atualizado em:** {last_update.strftime('%d/%m/%Y %H:%M') if pd.notnull(last_update) else 'N/A'}")
        
        # Filtrar por ano
        if 'Ano' in df.columns:
            anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
            ano_selecionado = st.sidebar.selectbox(
                "📅 Selecione o Ano para Análise",
                options=anos_disponiveis,
                index=len(anos_disponiveis)-1 if anos_disponiveis else 0
            )
            
            df_filtrado = df[df['Ano'] == ano_selecionado].copy()
        else:
            st.warning("Não foi possível extrair o ano dos dados.")
            df_filtrado = df.copy()
            ano_selecionado = "Todos"
        
        # Mostrar estatísticas básicas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_demandas = len(df_filtrado)
            st.metric("Total de Demandas", total_demandas)
        
        with col2:
            sincronizados = len(df_filtrado[df_filtrado['Status'] == 'Sincronizado']) if 'Status' in df_filtrado.columns else 0
            st.metric("Sincronizados", sincronizados)
        
        with col3:
            if 'Tipo Chamado' in df_filtrado.columns:
                correcoes = len(df_filtrado[df_filtrado['Tipo Chamado'].str.contains('Correção', na=False)])
                st.metric("Correções/Ajustes", correcoes)
            else:
                st.metric("Correções/Ajustes", 0)
        
        with col4:
            if 'Revisões' in df_filtrado.columns:
                total_revisoes = df_filtrado['Revisões'].sum()
                st.metric("Total de Revisões", total_revisoes)
            else:
                st.metric("Total de Revisões", 0)
        
        # Abas para diferentes visualizações
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Visão Geral", "👥 Por Responsável", "🏢 Por Empresa", "📋 Dados Detalhados"])
        
        with tab1:
            st.subheader(f"Visão Geral - Ano {ano_selecionado}")
            
            # Gráfico 1: Distribuição por Tipo de Chamado
            if 'Tipo Chamado' in df_filtrado.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    tipo_dist = df_filtrado['Tipo Chamado'].value_counts()
                    fig1 = px.pie(
                        values=tipo_dist.values,
                        names=tipo_dist.index,
                        title="Distribuição por Tipo de Chamado",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig1.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Gráfico 2: Distribuição por Status
                    if 'Status' in df_filtrado.columns:
                        status_dist = df_filtrado['Status'].value_counts()
                        fig2 = px.bar(
                            x=status_dist.index,
                            y=status_dist.values,
                            title="Distribuição por Status",
                            labels={'x': 'Status', 'y': 'Quantidade'},
                            color=status_dist.values,
                            color_continuous_scale='Viridis'
                        )
                        st.plotly_chart(fig2, use_container_width=True)
            
            # Gráfico 3: Evolução mensal
            if 'Criado' in df_filtrado.columns:
                df_filtrado['Mês'] = df_filtrado['Criado'].dt.strftime('%Y-%m')
                evolucao_mensal = df_filtrado.groupby('Mês').size().reset_index(name='Quantidade')
                
                fig3 = px.line(
                    evolucao_mensal,
                    x='Mês',
                    y='Quantidade',
                    title="Evolução Mensal de Demandas",
                    markers=True
                )
                fig3.update_xaxes(tickangle=45)
                st.plotly_chart(fig3, use_container_width=True)
        
        with tab2:
            st.subheader(f"Análise por Responsável - Ano {ano_selecionado}")
            
            # CORREÇÃO: Analisar por quem criou o card (Responsável) e não quem modificou
            if 'Responsável' in df_filtrado.columns:
                # Limpar e padronizar emails
                df_filtrado['Responsável_limpo'] = df_filtrado['Responsável'].str.strip().str.lower()
                
                # Gráfico 4: Top 10 responsáveis por quantidade de demandas criadas
                top_responsaveis = df_filtrado['Responsável_limpo'].value_counts().head(10)
                
                fig4 = px.bar(
                    x=top_responsaveis.values,
                    y=top_responsaveis.index,
                    orientation='h',
                    title="Top 10 Responsáveis por Demandas Criadas",
                    labels={'x': 'Quantidade de Demandas', 'y': 'Responsável'},
                    color=top_responsaveis.values,
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig4, use_container_width=True)
                
                # Gráfico 5: Tipo de chamado por responsável
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'Tipo Chamado' in df_filtrado.columns:
                        tipo_por_responsavel = df_filtrado.groupby(['Responsável_limpo', 'Tipo Chamado']).size().unstack(fill_value=0)
                        tipo_por_responsavel = tipo_por_responsavel.head(10)  # Top 10
                        
                        fig5 = px.bar(
                            tipo_por_responsavel,
                            barmode='group',
                            title="Tipo de Chamado por Responsável (Top 10)",
                            labels={'value': 'Quantidade', 'variable': 'Tipo Chamado'}
                        )
                        fig5.update_xaxes(tickangle=45)
                        st.plotly_chart(fig5, use_container_width=True)
                
                with col2:
                    # Gráfico 6: Revisões por responsável
                    if 'Revisões' in df_filtrado.columns:
                        revisoes_por_responsavel = df_filtrado.groupby('Responsável_limpo')['Revisões'].sum().sort_values(ascending=False).head(10)
                        
                        fig6 = px.bar(
                            x=revisoes_por_responsavel.values,
                            y=revisoes_por_responsavel.index,
                            orientation='h',
                            title="Top 10 Responsáveis por Total de Revisões",
                            labels={'x': 'Total de Revisões', 'y': 'Responsável'},
                            color=revisoes_por_responsavel.values,
                            color_continuous_scale='Reds'
                        )
                        st.plotly_chart(fig6, use_container_width=True)
        
        with tab3:
            st.subheader(f"Análise por Empresa - Ano {ano_selecionado}")
            
            if 'Empresa' in df_filtrado.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico 7: Distribuição por Empresa
                    empresa_dist = df_filtrado['Empresa'].value_counts()
                    fig7 = px.pie(
                        values=empresa_dist.values,
                        names=empresa_dist.index,
                        title="Distribuição por Empresa",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig7.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig7, use_container_width=True)
                
                with col2:
                    # Gráfico 8: Tipo de chamado por empresa
                    if 'Tipo Chamado' in df_filtrado.columns:
                        tipo_por_empresa = df_filtrado.groupby(['Empresa', 'Tipo Chamado']).size().unstack(fill_value=0)
                        
                        fig8 = px.bar(
                            tipo_por_empresa,
                            barmode='group',
                            title="Tipo de Chamado por Empresa",
                            labels={'value': 'Quantidade', 'variable': 'Tipo Chamado'}
                        )
                        st.plotly_chart(fig8, use_container_width=True)
                
                # Gráfico 9: Status por empresa
                if 'Status' in df_filtrado.columns:
                    status_por_empresa = df_filtrado.groupby(['Empresa', 'Status']).size().unstack(fill_value=0)
                    
                    fig9 = px.bar(
                        status_por_empresa,
                        barmode='group',
                        title="Status por Empresa",
                        labels={'value': 'Quantidade', 'variable': 'Status'}
                    )
                    st.plotly_chart(fig9, use_container_width=True)
        
        with tab4:
            st.subheader(f"Dados Detalhados - Ano {ano_selecionado}")
            
            # Filtros para a tabela
            st.subheader("Filtros")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'Tipo Chamado' in df_filtrado.columns:
                    tipos = ['Todos'] + list(df_filtrado['Tipo Chamado'].dropna().unique())
                    tipo_filtro = st.selectbox("Tipo de Chamado", tipos)
            
            with col2:
                if 'Status' in df_filtrado.columns:
                    status_list = ['Todos'] + list(df_filtrado['Status'].dropna().unique())
                    status_filtro = st.selectbox("Status", status_list)
            
            with col3:
                if 'Empresa' in df_filtrado.columns:
                    empresas = ['Todos'] + list(df_filtrado['Empresa'].dropna().unique())
                    empresa_filtro = st.selectbox("Empresa", empresas)
            
            # Aplicar filtros
            df_filtrado_tabela = df_filtrado.copy()
            
            if 'Tipo Chamado' in df_filtrado_tabela.columns and tipo_filtro != 'Todos':
                df_filtrado_tabela = df_filtrado_tabela[df_filtrado_tabela['Tipo Chamado'] == tipo_filtro]
            
            if 'Status' in df_filtrado_tabela.columns and status_filtro != 'Todos':
                df_filtrado_tabela = df_filtrado_tabela[df_filtrado_tabela['Status'] == status_filtro]
            
            if 'Empresa' in df_filtrado_tabela.columns and empresa_filtro != 'Todos':
                df_filtrado_tabela = df_filtrado_tabela[df_filtrado_tabela['Empresa'] == empresa_filtro]
            
            # Mostrar tabela
            st.dataframe(
                df_filtrado_tabela[[
                    'Chamado', 'Tipo Chamado', 'Responsável', 'Status', 
                    'Criado', 'Modificado', 'Prioridade', 'Empresa', 'Revisões'
                ]].sort_values('Criado', ascending=False),
                use_container_width=True,
                height=400
            )
            
            # Opção para download dos dados filtrados
            csv = df_filtrado_tabela.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Download dos dados filtrados (CSV)",
                data=csv,
                file_name=f"esteira_demandas_filtrado_{ano_selecionado}.csv",
                mime="text/csv"
            )
        
        # Resumo estatístico
        st.sidebar.subheader("📊 Resumo Estatístico")
        
        if 'Revisões' in df_filtrado.columns:
            st.sidebar.metric("Média de Revisões", f"{df_filtrado['Revisões'].mean():.1f}")
            st.sidebar.metric("Máximo de Revisões", df_filtrado['Revisões'].max())
        
        if 'Tipo Chamado' in df_filtrado.columns:
            tipo_mais_comum = df_filtrado['Tipo Chamado'].mode()[0] if not df_filtrado['Tipo Chamado'].mode().empty else "N/A"
            st.sidebar.metric("Tipo Mais Comum", tipo_mais_comum)
        
        if 'Empresa' in df_filtrado.columns:
            empresa_mais_comum = df_filtrado['Empresa'].mode()[0] if not df_filtrado['Empresa'].mode().empty else "N/A"
            st.sidebar.metric("Empresa Mais Comum", empresa_mais_comum)
        
    else:
        st.error("Não foi possível carregar os dados do arquivo.")
else:
    st.info("👆 Por favor, faça upload do arquivo CSV para começar a análise.")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.markdown("**Desenvolvido para análise da Esteira de Demandas ADMS**")
