import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Esteira ADMS - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar expandida por padrão
)

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    /* Estilos gerais */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
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
        border-left: 4px solid #2a5298;
        margin-bottom: 1rem;
    }
    
    .section-title {
        color: #2d3748;
        border-bottom: 2px solid #2a5298;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
        font-size: 1.4rem;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* Status de carregamento */
    .load-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-weight: bold;
    }
    
    .load-success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .load-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    /* Gráficos */
    .plotly-graph-div {
        border-radius: 10px;
        border: 1px solid #e9ecef;
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
        # Remover pontos, underlines e números, capitalizar
        nome = nome.replace('.', ' ').replace('_', ' ').replace('-', ' ').title()
        # Remover números no final
        while nome and nome[-1].isdigit():
            nome = nome[:-1]
        return nome.strip()
    else:
        # Já é um nome - melhorar formatação
        nome = email_str.title()
        # Corrigir abreviações comuns
        correcoes = {
            'Adm': 'ADM',
            'Sre': 'SRE',
            'T.i': 'T.I',
            'Rh': 'RH',
            'Ti': 'T.I',
        }
        for errado, correto in correcoes.items():
            nome = nome.replace(errado, correto)
        return nome

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
        df['Ano_Mês'] = df['Criado'].dt.strftime('%Y-%m')
    
    # Converter revisões
    if 'Revisões' in df.columns:
        df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
    
    return df

@st.cache_data
def carregar_arquivo_local(caminho_arquivo):
    """Carrega arquivo do sistema de arquivos"""
    try:
        if os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
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
                return None, "Formato de arquivo inválido: cabeçalho não encontrado"
            
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
            
            return df, "Arquivo carregado com sucesso!"
        
        else:
            return None, f"Arquivo não encontrado: {caminho_arquivo}"
    
    except Exception as e:
        return None, f"Erro ao carregar arquivo: {str(e)}"

@st.cache_data
def carregar_do_upload(uploaded_file):
    """Carrega arquivo do upload"""
    try:
        content = uploaded_file.getvalue().decode('utf-8-sig')
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
            return None, "Formato de arquivo inválido: cabeçalho não encontrado"
        
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
        
        return df, "Arquivo carregado com sucesso!"
    
    except Exception as e:
        return None, f"Erro ao processar arquivo: {str(e)}"

# ============================================
# CARREGAMENTO AUTOMÁTICO DO ARQUIVO
# ============================================
CAMINHOS_POSSIVEIS = [
    'data/esteira_demandas.csv',
    'esteira_demandas.csv',
    'dados/esteira_demandas.csv',
    'arquivos/esteira_demandas.csv',
    'base_dados.csv',
    'demandas.csv',
]

# ============================================
# SIDEBAR - FILTROS
# ============================================
with st.sidebar:
    st.markdown("## ⚙️ Filtros")
    st.markdown("---")
    
    # Inicializar session state
    if 'df' not in st.session_state:
        st.session_state.df = None
        st.session_state.load_status = "Aguardando carregamento..."
        st.session_state.arquivo_carregado = None
    
    # TENTAR CARREGAR ARQUIVO LOCAL AUTOMATICAMENTE
    if st.session_state.df is None:
        with st.spinner('Procurando arquivo...'):
            df_carregado = None
            status_mensagem = "Nenhum arquivo encontrado"
            caminho_encontrado = None
            
            for caminho in CAMINHOS_POSSIVEIS:
                if os.path.exists(caminho):
                    df_carregado, status_mensagem = carregar_arquivo_local(caminho)
                    if df_carregado is not None:
                        caminho_encontrado = caminho
                        break
            
            if df_carregado is not None and not df_carregado.empty:
                st.session_state.df = df_carregado
                st.session_state.load_status = f"✅ {status_mensagem}"
                st.session_state.arquivo_carregado = caminho_encontrado
            else:
                st.session_state.load_status = f"⚠️ {status_mensagem}"
    
    # UPLOAD DE NOVO ARQUIVO
    st.markdown("### 📤 Atualizar Dados")
    uploaded_file = st.file_uploader(
        "Carregar novo arquivo CSV",
        type=['csv'],
        help="Faça upload do arquivo CSV mais recente",
        key="sidebar_uploader"
    )
    
    if uploaded_file is not None:
        with st.spinner('Processando...'):
            df_novo, status = carregar_do_upload(uploaded_file)
            if df_novo is not None:
                st.session_state.df = df_novo
                st.session_state.load_status = f"✅ Arquivo atualizado: {uploaded_file.name}"
                st.session_state.arquivo_carregado = uploaded_file.name
                st.success("✅ Dados atualizados!")
                st.rerun()
            else:
                st.error(f"❌ Erro: {status}")
    
    st.markdown("---")
    
    # FILTROS APENAS SE HOUVER DADOS
    df = st.session_state.df
    
    if df is not None and not df.empty:
        st.markdown("### 🔍 Filtrar Dados")
        
        # FILTRO POR ANO
        if 'Ano' in df.columns:
            anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
            ano_selecionado = st.selectbox(
                "📅 Selecionar Ano",
                options=anos_disponiveis,
                index=len(anos_disponiveis)-1 if anos_disponiveis else 0
            )
            df_filtrado = df[df['Ano'] == ano_selecionado].copy()
        else:
            df_filtrado = df.copy()
            ano_selecionado = "Todos"
        
        # FILTRO POR RESPONSÁVEL
        if 'Responsável_Nome' in df_filtrado.columns:
            responsaveis = ['Todos'] + sorted(df_filtrado['Responsável_Nome'].dropna().unique().tolist())
            responsavel_selecionado = st.selectbox(
                "👤 Filtrar por Responsável",
                options=responsaveis
            )
            
            if responsavel_selecionado != 'Todos':
                df_filtrado = df_filtrado[df_filtrado['Responsável_Nome'] == responsavel_selecionado]
        
        # BUSCA POR NÚMERO DO CHAMADO
        if 'Chamado' in df_filtrado.columns:
            busca_chamado = st.text_input(
                "🔎 Buscar por Número do Chamado",
                placeholder="Digite o número do chamado..."
            )
            
            if busca_chamado:
                df_filtrado = df_filtrado[df_filtrado['Chamado'].astype(str).str.contains(busca_chamado, case=False, na=False)]
        
        # FILTRO POR STATUS
        if 'Status' in df_filtrado.columns:
            status_opcoes = ['Todos'] + sorted(df_filtrado['Status'].dropna().unique().tolist())
            status_selecionado = st.selectbox(
                "📊 Filtrar por Status",
                options=status_opcoes
            )
            
            if status_selecionado != 'Todos':
                df_filtrado = df_filtrado[df_filtrado['Status'] == status_selecionado]
        
        # FILTRO POR TIPO DE CHAMADO
        if 'Tipo_Chamado' in df_filtrado.columns:
            tipos = ['Todos'] + sorted(df_filtrado['Tipo_Chamado'].dropna().unique().tolist())
            tipo_selecionado = st.selectbox(
                "📝 Filtrar por Tipo de Chamado",
                options=tipos
            )
            
            if tipo_selecionado != 'Todos':
                df_filtrado = df_filtrado[df_filtrado['Tipo_Chamado'] == tipo_selecionado]
        
        # BOTÃO PARA LIMPAR FILTROS
        if st.button("🔄 Limpar Todos os Filtros"):
            df_filtrado = df.copy()
            st.rerun()
        
        st.markdown(f"**Registros filtrados:** {len(df_filtrado)}")
        
        # BOTÃO PARA LIMPAR CACHE
        st.markdown("---")
        if st.button("🗑️ Limpar Cache do Sistema", type="secondary"):
            st.cache_data.clear()
            st.session_state.df = None
            st.rerun()
    
    else:
        st.info("📂 Faça upload de um arquivo para habilitar os filtros")
        df_filtrado = None

# ============================================
# CONTEÚDO PRINCIPAL
# ============================================

# HEADER PRINCIPAL
st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin: 0; font-size: 2.5rem;">📊 Demandas Esteira ADMS</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
    Dashboard de Análise e Monitoramento | GEAT
    </p>
</div>
""", unsafe_allow_html=True)

# BARRA SUPERIOR COM INFORMAÇÕES
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    if st.session_state.df is not None and 'Criado' in st.session_state.df.columns:
        periodo = f"{st.session_state.df['Criado'].min().strftime('%d/%m/%Y')} a {st.session_state.df['Criado'].max().strftime('%d/%m/%Y')}"
        st.markdown(f"**Período:** {periodo}")

with col_info2:
    if st.session_state.df is not None:
        st.markdown(f"**Total de Registros:** {len(st.session_state.df):,}")

with col_info3:
    if st.session_state.arquivo_carregado:
        st.markdown(f"**Arquivo:** {st.session_state.arquivo_carregado}")

# ============================================
# EXIBIR DASHBOARD SE HOUVER DADOS
# ============================================
df = st.session_state.df

if df is not None and not df.empty:
    # Usar dados filtrados ou completos
    df_display = df_filtrado if df_filtrado is not None else df
    
    # KPI CARDS
    st.markdown("## 📈 Indicadores Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_demandas = len(df_display)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #2d3748; font-size: 2rem;">{total_demandas:,}</h3>
            <p style="margin: 0; color: #718096;">Total de Demandas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if 'Status' in df_display.columns:
            sincronizados = len(df_display[df_display['Status'] == 'Sincronizado'])
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #2d3748; font-size: 2rem;">{sincronizados:,}</h3>
                <p style="margin: 0; color: #718096;">Sincronizados</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if 'Tipo_Chamado' in df_display.columns:
            correcoes = len(df_display[df_display['Tipo_Chamado'].str.contains('Correção', na=False)])
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #2d3748; font-size: 2rem;">{correcoes:,}</h3>
                <p style="margin: 0; color: #718096;">Correções/Ajustes</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if 'Revisões' in df_display.columns:
            total_revisoes = df_display['Revisões'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #2d3748; font-size: 2rem;">{total_revisoes:,}</h3>
                <p style="margin: 0; color: #718096;">Total de Revisões</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ============================================
    # PRIMEIRA LINHA DE GRÁFICOS
    # ============================================
    st.markdown("---")
    st.markdown("## 📊 Análises Temporais")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="section-title">📅 Demandas por Mês/Ano</div>', unsafe_allow_html=True)
        
        if 'Mês_Ano' in df_display.columns:
            demandas_mes = df_display.groupby('Mês_Ano').size().reset_index(name='Quantidade')
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
                showlegend=False,
                height=400
            )
            fig_mes.update_xaxes(tickangle=45)
            st.plotly_chart(fig_mes, use_container_width=True)
    
    with col_right:
        st.markdown('<div class="section-title">📈 Erros por Mês/Ano</div>', unsafe_allow_html=True)
        
        if 'Status' in df_display.columns and 'Ano_Mês' in df_display.columns:
            # Filtrar apenas status que indicam erro ou pendência
            status_erro = ['Pendente', 'Erro', 'Falha', 'Rejeitado', 'Cancelado']
            
            # Encontrar status que contêm essas palavras
            df_erros = df_display.copy()
            df_erros['É_Erro'] = df_erros['Status'].str.contains('|'.join(status_erro), case=False, na=False)
            
            erros_mes = df_erros[df_erros['É_Erro']].groupby('Ano_Mês').size().reset_index(name='Quantidade_Erros')
            
            if not erros_mes.empty:
                erros_mes = erros_mes.sort_values('Ano_Mês')
                
                fig_erros = px.line(
                    erros_mes,
                    x='Ano_Mês',
                    y='Quantidade_Erros',
                    title='',
                    markers=True,
                    line_shape='spline',
                    color_discrete_sequence=['#e74c3c']
                )
                fig_erros.update_traces(line=dict(width=3))
                fig_erros.update_layout(
                    xaxis_title="Mês/Ano",
                    yaxis_title="Quantidade de Erros",
                    plot_bgcolor='white',
                    height=400
                )
                fig_erros.update_xaxes(tickangle=45)
                st.plotly_chart(fig_erros, use_container_width=True)
            else:
                st.info("Nenhum erro identificado no período")
        else:
            st.info("Dados insuficientes para análise de erros")
    
    # ============================================
    # SEGUNDA LINHA - TOP RANKINGS
    # ============================================
    st.markdown("---")
    st.markdown("## 🏆 Rankings e Desempenho")
    
    col_left2, col_right2 = st.columns(2)
    
    with col_left2:
        st.markdown('<div class="section-title">👥 Top 10 - Mais Demandas</div>', unsafe_allow_html=True)
        
        if 'Responsável_Nome' in df_display.columns:
            top_demandas = df_display['Responsável_Nome'].value_counts().head(10).reset_index()
            top_demandas.columns = ['Responsável', 'Quantidade']
            
            fig_demandas = px.bar(
                top_demandas,
                x='Quantidade',
                y='Responsável',
                orientation='h',
                title='',
                color='Quantidade',
                color_continuous_scale='Blues',
                text='Quantidade'
            )
            fig_demandas.update_traces(textposition='outside')
            fig_demandas.update_layout(
                xaxis_title="Quantidade de Demandas",
                yaxis_title="",
                plot_bgcolor='white',
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                height=400
            )
            st.plotly_chart(fig_demandas, use_container_width=True)
    
    with col_right2:
        st.markdown('<div class="section-title">🏆 Top SRE - Sincronismos</div>', unsafe_allow_html=True)
        
        if 'SRE' in df_display.columns and 'Status' in df_display.columns:
            # Filtrar apenas sincronizados
            df_sincronizados = df_display[df_display['Status'] == 'Sincronizado']
            
            if not df_sincronizados.empty:
                top_sre = df_sincronizados['SRE'].value_counts().head(10).reset_index()
                top_sre.columns = ['SRE', 'Sincronismos']
                
                fig_sre = px.bar(
                    top_sre,
                    x='Sincronismos',
                    y='SRE',
                    orientation='h',
                    title='',
                    color='Sincronismos',
                    color_continuous_scale='Greens',
                    text='Sincronismos'
                )
                fig_sre.update_traces(textposition='outside')
                fig_sre.update_layout(
                    xaxis_title="Quantidade de Sincronismos",
                    yaxis_title="",
                    plot_bgcolor='white',
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'},
                    height=400
                )
                st.plotly_chart(fig_sre, use_container_width=True)
            else:
                st.info("Nenhum sincronismo encontrado")
        else:
            st.info("Dados de SRE não disponíveis")
    
    # ============================================
    # TERCEIRA LINHA - MAIS INFORMAÇÕES
    # ============================================
    col_left3, col_right3 = st.columns(2)
    
    with col_left3:
        st.markdown('<div class="section-title">📊 Distribuição por Status</div>', unsafe_allow_html=True)
        
        if 'Status' in df_display.columns:
            status_dist = df_display['Status'].value_counts()
            fig_status = px.pie(
                values=status_dist.values,
                names=status_dist.index,
                title='',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_status.update_traces(textposition='inside', textinfo='percent+label')
            fig_status.update_layout(height=400)
            st.plotly_chart(fig_status, use_container_width=True)
    
    with col_right3:
        st.markdown('<div class="section-title">📈 Top 10 - Mais Revisões</div>', unsafe_allow_html=True)
        
        if 'Responsável_Nome' in df_display.columns and 'Revisões' in df_display.columns:
            top_revisoes = df_display.groupby('Responsável_Nome')['Revisões'].sum().reset_index()
            top_revisoes = top_revisoes.sort_values('Revisões', ascending=False).head(10)
            
            fig_revisoes = px.bar(
                top_revisoes,
                x='Revisões',
                y='Responsável_Nome',
                orientation='h',
                title='',
                color='Revisões',
                color_continuous_scale='Reds',
                text='Revisões'
            )
            fig_revisoes.update_traces(textposition='outside')
            fig_revisoes.update_layout(
                xaxis_title="Total de Revisões",
                yaxis_title="",
                plot_bgcolor='white',
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                height=400
            )
            st.plotly_chart(fig_revisoes, use_container_width=True)
    
    # ============================================
    # ÚLTIMAS DEMANDAS REGISTRADAS
    # ============================================
    st.markdown("---")
    st.markdown('<div class="section-title">🕒 Últimas Demandas Registradas</div>', unsafe_allow_html=True)
    
    if 'Criado' in df_display.columns:
        ultimas_demandas = df_display.sort_values('Criado', ascending=False).head(15)
        
        # Formatar colunas para exibição
        display_cols = []
        if 'Chamado' in ultimas_demandas.columns:
            display_cols.append('Chamado')
        if 'Tipo_Chamado' in ultimas_demandas.columns:
            display_cols.append('Tipo_Chamado')
        if 'Responsável_Nome' in ultimas_demandas.columns:
            display_cols.append('Responsável')
        if 'Status' in ultimas_demandas.columns:
            display_cols.append('Status')
        if 'Prioridade' in ultimas_demandas.columns:
            display_cols.append('Prioridade')
        if 'Criado' in ultimas_demandas.columns:
            display_cols.append('Data_Criação')
            ultimas_demandas['Data_Criação'] = ultimas_demandas['Criado'].dt.strftime('%d/%m/%Y %H:%M')
        
        if display_cols:
            # Estilizar a tabela
            st.dataframe(
                ultimas_demandas[display_cols],
                use_container_width=True,
                height=400,
                column_config={
                    "Chamado": st.column_config.TextColumn(
                        "Chamado",
                        width="medium"
                    ),
                    "Responsável": st.column_config.TextColumn(
                        "Responsável",
                        width="medium"
                    ),
                    "Status": st.column_config.TextColumn(
                        "Status",
                        width="small"
                    )
                }
            )
    
    # ============================================
    # BOTÃO PARA EXPORTAR DADOS
    # ============================================
    st.markdown("---")
    col_export1, col_export2 = st.columns([3, 1])
    
    with col_export2:
        if st.button("📥 Exportar Dados Filtrados", type="primary"):
            csv = df_display.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="Clique para baixar CSV",
                data=csv,
                file_name=f"esteira_demandas_filtrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_csv"
            )

else:
    # TELA INICIAL SEM DADOS
    st.markdown("""
    <div style="text-align: center; padding: 4rem; background: #f8f9fa; border-radius: 10px; border: 2px dashed #dee2e6;">
        <h3 style="color: #495057;">📊 Dashboard Esteira ADMS</h3>
        <p style="color: #6c757d; margin-bottom: 2rem;">
            Sistema de análise e monitoramento de demandas
        </p>
        <div style="margin-top: 2rem; padding: 2rem; background: white; border-radius: 8px;">
            <h4 style="color: #2a5298;">📋 Como começar:</h4>
            <p>1. <strong>Use a barra lateral esquerda</strong> para fazer upload do arquivo CSV</p>
            <p>2. Ou <strong>adicione um arquivo</strong> chamado "esteira_demandas.csv" na pasta "data/"</p>
            <p>3. <strong>Utilize os filtros</strong> para análise específica dos dados</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")

footer_col1, footer_col2 = st.columns([1, 2])

with footer_col1:
    st.markdown("**Versão:** 2.0.0")
    st.markdown(f"**Atualizado:** {datetime.now().strftime('%d/%m/%Y')}")

with footer_col2:
    st.markdown("""
    <div style="text-align: center;">
        <p style="color: #495057; font-size: 0.9rem;">
        <strong>Desenvolvido por:</strong> Kewin Marcel Ramirez Ferreira | GEAT
        </p>
        <p style="color: #6c757d; font-size: 0.8rem; margin-top: 0.5rem;">
        © 2024 Esteira ADMS Dashboard | Sistema proprietário - Proibida reprodução
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# INFORMAÇÕES TÉCNICAS
# ============================================
with st.expander("🔧 Informações Técnicas do Sistema", expanded=False):
    if df is not None:
        col_tech1, col_tech2 = st.columns(2)
        
        with col_tech1:
            st.write("**📊 Estatísticas Gerais:**")
            st.write(f"- Total de registros: {len(df):,}")
            if 'Criado' in df.columns:
                st.write(f"- Período coberto: {df['Criado'].min().strftime('%d/%m/%Y')} a {df['Criado'].max().strftime('%d/%m/%Y')}")
            if 'Revisões' in df.columns:
                st.write(f"- Média de revisões por demanda: {df['Revisões'].mean():.1f}")
            if 'Responsável_Nome' in df.columns:
                st.write(f"- Total de responsáveis únicos: {df['Responsável_Nome'].nunique()}")
        
        with col_tech2:
            st.write("**⚙️ Configuração:**")
            st.write(f"- Arquivo carregado: {st.session_state.arquivo_carregado}")
            st.write(f"- Status: {st.session_state.load_status}")
            st.write(f"- Filtros ativos: {len(df_filtrado) if df_filtrado is not None else len(df)} registros")
            st.write("**📁 Colunas disponíveis:**")
            st.write(", ".join(sorted(df.columns.tolist())))
    else:
        st.info("Sistema aguardando carregamento de dados...")

# ============================================
# requirements.txt (separado)
# ============================================
"""
streamlit>=1.28.0
plotly>=5.18.0
pandas>=2.1.4
numpy>=1.24.0
"""
