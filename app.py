import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import warnings
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Esteira ADMS - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    /* Estilos gerais */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        color: #666;
        font-size: 0.9rem;
        border-top: 1px solid #eaeaea;
    }
    
    .section-title {
        color: #2d3748;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
        font-size: 1.4rem;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        border-radius: 5px 5px 0 0;
    }
    
    /* Uploader */
    .uploadedFile {
        background-color: #f7fafc;
        border: 2px dashed #cbd5e0;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
    }
    
    /* Dataframe */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def extrair_nome(email):
    """Extrai nome do e-mail ou string"""
    if pd.isna(email):
        return "Não informado"
    
    email_str = str(email).strip()
    
    # Se for e-mail, extrair nome antes do @
    if '@' in email_str:
        nome = email_str.split('@')[0]
        # Remover pontos e números, capitalizar
        nome = nome.replace('.', ' ').replace('_', ' ').title()
        # Remover números no final
        while nome and nome[-1].isdigit():
            nome = nome[:-1]
        return nome.strip()
    else:
        # Já é um nome
        return email_str.title()

def processar_dados(df):
    """Processa os dados e extrai informações"""
    # Extrair nomes dos responsáveis
    if 'Responsável' in df.columns:
        df['Responsável_Nome'] = df['Responsável'].apply(extrair_nome)
    
    # Converter datas
    date_columns = ['Criado', 'Modificado']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', format='ISO8601')
    
    # Extrair informações de tempo
    if 'Criado' in df.columns:
        df['Ano'] = df['Criado'].dt.year
        df['Mês'] = df['Criado'].dt.month
        df['Dia'] = df['Criado'].dt.day
        df['Mês_Ano'] = df['Criado'].dt.strftime('%b/%Y')
        df['Dia_Mês'] = df['Criado'].dt.strftime('%d/%m')
    
    # Converter revisões
    if 'Revisões' in df.columns:
        df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
    
    return df

@st.cache_data
def load_data(file):
    """Carrega e processa o arquivo CSV"""
    try:
        # Ler o arquivo CSV
        content = file.getvalue().decode('utf-8-sig')
        lines = content.split('\n')
        
        # Encontrar cabeçalho
        header_line = None
        for i, line in enumerate(lines):
            if line.startswith('"Chamado","Tipo Chamado"'):
                header_line = i
                break
        
        if header_line is None:
            for i, line in enumerate(lines):
                if '"Chamado"' in line and '"Tipo Chamado"' in line:
                    header_line = i
                    break
        
        if header_line is None:
            st.error("Formato de arquivo inválido.")
            return pd.DataFrame()
        
        # Ler dados
        data_str = '\n'.join(lines[header_line:])
        df = pd.read_csv(io.StringIO(data_str), quotechar='"')
        
        # Renomear colunas
        col_mapping = {
            'Chamado': 'Chamado',
            'Tipo Chamado': 'Tipo_Chamado',
            'Responsável': 'Responsável',
            'Status': 'Status',
            'Criado': 'Criado',
            'Modificado': 'Modificado',
            'Modificado por': 'Modificado_por',
            'Prioridade': 'Prioridade',
            'Sincronização': 'Sincronização',
            'SRE': 'SRE',
            'Empresa': 'Empresa',
            'Revisões': 'Revisões'
        }
        
        df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})
        
        # Processar dados
        df = processar_dados(df)
        
        return df
    
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {str(e)}")
        return pd.DataFrame()

# ============================================
# INTERFACE PRINCIPAL
# ============================================

# Header principal
st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin: 0;">📊 Demandas Esteira ADMS</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Dashboard de análise e monitoramento de demandas</p>
</div>
""", unsafe_allow_html=True)

# Barra superior com informações
col_header1, col_header2, col_header3 = st.columns([2, 1, 2])
with col_header1:
    st.markdown("**Sistema de Gestão de Demandas**")
with col_header3:
    st.markdown("**Última atualização:** Aguardando dados...")

# Upload de arquivo (com opção de usar cache)
upload_col1, upload_col2 = st.columns([3, 1])

with upload_col1:
    uploaded_file = st.file_uploader(
        "📁 **Importar nova base de dados**",
        type=['csv'],
        help="Carregue o arquivo CSV mais recente da esteira de demandas"
    )

with upload_col2:
    if st.button("🔄 Limpar Cache", type="secondary"):
        st.cache_data.clear()
        st.rerun()

# Verificar se há dados em cache
if 'df' not in st.session_state:
    st.session_state.df = None
    st.session_state.last_update = None

# Carregar dados
if uploaded_file is not None:
    with st.spinner('Processando dados...'):
        df = load_data(uploaded_file)
        if not df.empty:
            st.session_state.df = df
            st.session_state.last_update = datetime.now()
            st.success("✅ Base de dados carregada com sucesso!")
        else:
            st.error("Erro ao processar o arquivo.")

# Usar dados em cache ou carregados
df = st.session_state.df

if df is not None and not df.empty:
    # Atualizar header com data
    with col_header3:
        if 'Modificado' in df.columns:
            last_update = df['Modificado'].max()
            if pd.notnull(last_update):
                st.markdown(f"**Última atualização:** {last_update.strftime('%d/%m/%Y %H:%M')}")
            else:
                st.markdown(f"**Última atualização:** {st.session_state.last_update.strftime('%d/%m/%Y %H:%M')}")
    
    # ============================================
    # KPI CARDS
    # ============================================
    st.markdown("## 📈 Indicadores Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_demandas = len(df)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #2d3748;">{total_demandas}</h3>
            <p style="margin: 0; color: #718096;">Total de Demandas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if 'Status' in df.columns:
            sincronizados = len(df[df['Status'] == 'Sincronizado'])
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #2d3748;">{sincronizados}</h3>
                <p style="margin: 0; color: #718096;">Sincronizados</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if 'Tipo_Chamado' in df.columns:
            correcoes = len(df[df['Tipo_Chamado'].str.contains('Correção', na=False)])
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #2d3748;">{correcoes}</h3>
                <p style="margin: 0; color: #718096;">Correções/Ajustes</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if 'Revisões' in df.columns:
            total_revisoes = df['Revisões'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #2d3748;">{total_revisoes}</h3>
                <p style="margin: 0; color: #718096;">Total de Revisões</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ============================================
    # PRIMEIRA LINHA DE GRÁFICOS
    # ============================================
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="section-title">📅 Demandas por Mês/Ano</div>', unsafe_allow_html=True)
        
        if 'Mês_Ano' in df.columns:
            demandas_mes = df.groupby('Mês_Ano').size().reset_index(name='Quantidade')
            demandas_mes = demandas_mes.sort_values('Mês_Ano')
            
            fig_mes = px.bar(
                demandas_mes,
                x='Mês_Ano',
                y='Quantidade',
                title='',
                color='Quantidade',
                color_continuous_scale='Viridis',
                text='Quantidade'
            )
            fig_mes.update_traces(textposition='outside')
            fig_mes.update_layout(
                xaxis_title="Mês/Ano",
                yaxis_title="Quantidade",
                plot_bgcolor='white',
                showlegend=False
            )
            st.plotly_chart(fig_mes, use_container_width=True)
    
    with col_right:
        st.markdown('<div class="section-title">📊 Demandas do Mês Atual</div>', unsafe_allow_html=True)
        
        # Filtrar mês atual
        mes_atual = datetime.now().month
        ano_atual = datetime.now().year
        df_mes_atual = df[(df['Criado'].dt.month == mes_atual) & (df['Criado'].dt.year == ano_atual)]
        
        if not df_mes_atual.empty and 'Dia_Mês' in df_mes_atual.columns:
            demandas_dia = df_mes_atual.groupby('Dia_Mês').size().reset_index(name='Quantidade')
            demandas_dia = demandas_dia.sort_values('Dia_Mês')
            
            fig_dia = px.line(
                demandas_dia,
                x='Dia_Mês',
                y='Quantidade',
                title='',
                markers=True,
                line_shape='spline'
            )
            fig_dia.update_traces(line=dict(color='#667eea', width=3))
            fig_dia.update_layout(
                xaxis_title="Dia do Mês",
                yaxis_title="Quantidade",
                plot_bgcolor='white'
            )
            st.plotly_chart(fig_dia, use_container_width=True)
        else:
            st.info("Sem dados para o mês atual")
    
    # ============================================
    # SEGUNDA LINHA - TOP RANKINGS
    # ============================================
    col_left2, col_right2 = st.columns(2)
    
    with col_left2:
        st.markdown('<div class="section-title">🏆 Top 10 - Mais Revisões</div>', unsafe_allow_html=True)
        
        if 'Responsável_Nome' in df.columns and 'Revisões' in df.columns:
            top_revisoes = df.groupby('Responsável_Nome')['Revisões'].sum().reset_index()
            top_revisoes = top_revisoes.sort_values('Revisões', ascending=False).head(10)
            
            fig_top = px.bar(
                top_revisoes,
                x='Revisões',
                y='Responsável_Nome',
                orientation='h',
                title='',
                color='Revisões',
                color_continuous_scale='Reds',
                text='Revisões'
            )
            fig_top.update_traces(textposition='outside')
            fig_top.update_layout(
                xaxis_title="Total de Revisões",
                yaxis_title="Responsável",
                plot_bgcolor='white',
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_top, use_container_width=True)
    
    with col_right2:
        st.markdown('<div class="section-title">👥 Top 10 - Mais Demandas</div>', unsafe_allow_html=True)
        
        if 'Responsável_Nome' in df.columns:
            top_demandas = df['Responsável_Nome'].value_counts().head(10).reset_index()
            top_demandas.columns = ['Responsável_Nome', 'Quantidade']
            
            fig_demandas = px.bar(
                top_demandas,
                x='Quantidade',
                y='Responsável_Nome',
                orientation='h',
                title='',
                color='Quantidade',
                color_continuous_scale='Blues',
                text='Quantidade'
            )
            fig_demandas.update_traces(textposition='outside')
            fig_demandas.update_layout(
                xaxis_title="Quantidade de Demandas",
                yaxis_title="Responsável",
                plot_bgcolor='white',
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_demandas, use_container_width=True)
    
    # ============================================
    # ÚLTIMAS DEMANDAS REGISTRADAS
    # ============================================
    st.markdown('<div class="section-title">🕒 Últimas Demandas Registradas</div>', unsafe_allow_html=True)
    
    if 'Criado' in df.columns:
        ultimas_demandas = df.sort_values('Criado', ascending=False).head(10)
        
        # Formatar colunas para exibição
        display_cols = []
        if 'Chamado' in ultimas_demandas.columns:
            display_cols.append('Chamado')
        if 'Tipo_Chamado' in ultimas_demandas.columns:
            display_cols.append('Tipo_Chamado')
        if 'Responsável_Nome' in ultimas_demandas.columns:
            display_cols.append('Responsável_Nome')
        if 'Status' in ultimas_demandas.columns:
            display_cols.append('Status')
        if 'Prioridade' in ultimas_demandas.columns:
            display_cols.append('Prioridade')
        if 'Criado' in ultimas_demandas.columns:
            display_cols.append('Criado')
        
        if display_cols:
            # Estilizar a tabela
            st.dataframe(
                ultimas_demandas[display_cols],
                use_container_width=True,
                height=300,
                column_config={
                    "Criado": st.column_config.DatetimeColumn(
                        "Data Criação",
                        format="DD/MM/YYYY HH:mm"
                    ),
                    "Status": st.column_config.TextColumn(
                        "Status",
                        help="Status da demanda"
                    )
                }
            )
    
    # ============================================
    # VISUALIZAÇÕES DETALHADAS (TABS)
    # ============================================
    st.markdown("## 📋 Visualizações Detalhadas")
    
    tab1, tab2, tab3 = st.tabs(["📊 Distribuição Geral", "🏢 Por Empresa", "📁 Dados Completos"])
    
    with tab1:
        col_tab1, col_tab2 = st.columns(2)
        
        with col_tab1:
            if 'Tipo_Chamado' in df.columns:
                tipo_dist = df['Tipo_Chamado'].value_counts()
                fig_tipo = px.pie(
                    values=tipo_dist.values,
                    names=tipo_dist.index,
                    title="Distribuição por Tipo de Chamado",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_tipo.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_tipo, use_container_width=True)
        
        with col_tab2:
            if 'Status' in df.columns:
                status_dist = df['Status'].value_counts()
                fig_status = px.bar(
                    x=status_dist.index,
                    y=status_dist.values,
                    title="Distribuição por Status",
                    labels={'x': 'Status', 'y': 'Quantidade'},
                    color=status_dist.values,
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_status, use_container_width=True)
    
    with tab2:
        if 'Empresa' in df.columns:
            empresa_dist = df['Empresa'].value_counts()
            fig_empresa = px.pie(
                values=empresa_dist.values,
                names=empresa_dist.index,
                title="Distribuição por Empresa",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_empresa.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_empresa, use_container_width=True)
    
    with tab3:
        # Filtros para tabela detalhada
        st.subheader("Filtros Avançados")
        
        col_filt1, col_filt2, col_filt3 = st.columns(3)
        
        with col_filt1:
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos'] + list(df['Tipo_Chamado'].dropna().unique())
                tipo_filtro = st.selectbox("Tipo de Chamado", tipos)
        
        with col_filt2:
            if 'Status' in df.columns:
                status_list = ['Todos'] + list(df['Status'].dropna().unique())
                status_filtro = st.selectbox("Status", status_list)
        
        with col_filt3:
            if 'Empresa' in df.columns:
                empresas = ['Todos'] + list(df['Empresa'].dropna().unique())
                empresa_filtro = st.selectbox("Empresa", empresas)
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if 'Tipo_Chamado' in df_filtrado.columns and tipo_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Tipo_Chamado'] == tipo_filtro]
        
        if 'Status' in df_filtrado.columns and status_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Status'] == status_filtro]
        
        if 'Empresa' in df_filtrado.columns and empresa_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Empresa'] == empresa_filtro]
        
        # Mostrar dados filtrados
        st.dataframe(
            df_filtrado[[
                'Chamado', 'Tipo_Chamado', 'Responsável_Nome', 'Status',
                'Criado', 'Modificado', 'Prioridade', 'Empresa', 'Revisões'
            ]].sort_values('Criado', ascending=False),
            use_container_width=True,
            height=400
        )
        
        # Botão de download
        csv = df_filtrado.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Exportar Dados Filtrados (CSV)",
            data=csv,
            file_name=f"esteira_demandas_filtrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

else:
    # Tela inicial sem dados
    st.markdown("""
    <div style="text-align: center; padding: 4rem; background: #f7fafc; border-radius: 10px;">
        <h3 style="color: #4a5568;">📊 Dashboard Esteira ADMS</h3>
        <p style="color: #718096; margin-bottom: 2rem;">
            Faça upload do arquivo CSV para visualizar as análises da esteira de demandas.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Instruções
    with st.expander("ℹ️ Instruções de uso", expanded=True):
        st.markdown("""
        1. **Prepare seu arquivo**: Exporte os dados da esteira ADMS em formato CSV
        2. **Faça o upload**: Use o botão acima para carregar o arquivo
        3. **Visualize**: Os dados serão processados e as análises serão exibidas
        
        **Funcionalidades disponíveis:**
        - 📈 Indicadores principais em tempo real
        - 📊 Gráficos interativos de distribuição
        - 🏆 Ranking de responsáveis
        - 📅 Análise temporal por mês e dia
        - 📋 Tabela detalhada com filtros
        - 📥 Exportação de dados
        """)

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col1:
    st.markdown("**Versão:** 1.0.0")

with footer_col2:
    st.markdown("""
    <div style="text-align: center;">
        <p style="color: #666; font-size: 0.9rem;">
        © 2024 Esteira ADMS Dashboard | 
        <strong style="color: #e53e3e;">⚠️ Proibida a reprodução total ou parcial</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

with footer_col3:
    st.markdown("**Desenvolvedor:** Kewin Marcel Ramirez Ferreira")

# Adicionar informações técnicas
with st.expander("🔧 Informações técnicas", expanded=False):
    if df is not None:
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.write("**Estatísticas:**")
            st.write(f"- Total de registros: {len(df)}")
            if 'Criado' in df.columns:
                st.write(f"- Período: {df['Criado'].min().strftime('%d/%m/%Y')} a {df['Criado'].max().strftime('%d/%m/%Y')}")
            if 'Revisões' in df.columns:
                st.write(f"- Média de revisões: {df['Revisões'].mean():.1f}")
        
        with col_info2:
            st.write("**Colunas disponíveis:**")
            st.write(", ".join(df.columns.tolist()))
    else:
        st.info("Carregue um arquivo para ver informações técnicas")
