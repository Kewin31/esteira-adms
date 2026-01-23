import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import os
import time
import hashlib
import warnings
from pytz import timezone
import numpy as np
warnings.filterwarnings('ignore')

# ============================================
# VARIÁVEIS GLOBAIS DE CONFIGURAÇÃO
# ============================================
CAMINHO_ARQUIVO_PRINCIPAL = "esteira_demandas.csv"
CAMINHOS_ALTERNATIVOS = [
    "data/esteira_demandas.csv",
    "dados/esteira_demandas.csv",
    "database/esteira_demandas.csv",
    "base_dados.csv",
    "dados.csv"
]

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Esteira ADMS - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO (SIMPLIFICADO)
# ============================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0c2461 0%, #1e3799 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .metric-card-exec {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3799;
        margin: 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    .section-title-exec {
        color: #1e3799;
        border-bottom: 3px solid #1e3799;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
        font-size: 1.2rem;
        font-weight: 700;
    }
    
    .sidebar-section {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .info-base {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e3799;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES AUXILIARES OTIMIZADAS
# ============================================
def formatar_nome_responsavel(nome):
    """Formata nomes dos responsáveis - OTIMIZADA"""
    if pd.isna(nome):
        return "Não informado"
    
    nome_str = str(nome).strip()
    
    if '@' in nome_str:
        partes = nome_str.split('@')[0]
        for separador in ['.', '_', '-']:
            partes = partes.replace(separador, ' ')
        
        palavras = [p.capitalize() for p in partes.split() if not p.isdigit()]
        nome_formatado = ' '.join(palavras)
        
        correcoes = {
            ' Da ': ' da ', ' De ': ' de ', ' Do ': ' do ',
            ' Das ': ' das ', ' Dos ': ' dos ', ' E ': ' e ',
        }
        
        for errado, correto in correcoes.items():
            nome_formatado = nome_formatado.replace(errado, correto)
        
        return nome_formatado
    
    return nome_str.title()

def criar_card_indicador_simples(valor, label, icone="📊"):
    """Cria card de indicador SIMPLES - OTIMIZADO"""
    if isinstance(valor, (int, float)):
        valor_formatado = f"{valor:,}"
    else:
        valor_formatado = str(valor)
    
    return f'''
    <div class="metric-card-exec">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <span style="font-size: 1.5rem;">{icone}</span>
            <div style="flex-grow: 1;">
                <div class="metric-value">{valor_formatado}</div>
                <div class="metric-label">{label}</div>
            </div>
        </div>
    </div>
    '''

@st.cache_data(ttl=300, max_entries=3)  # Cache por 5 minutos, máximo 3 entradas
def carregar_dados_otimizado(uploaded_file=None, caminho_arquivo=None):
    """Carrega e processa os dados - OTIMIZADA"""
    try:
        # Determinar fonte dos dados
        if uploaded_file:
            conteudo = uploaded_file.getvalue()
            conteudo_str = conteudo.decode('utf-8-sig')
            modo = 'upload'
        elif caminho_arquivo and os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'rb') as f:
                conteudo = f.read()
            conteudo_str = conteudo.decode('utf-8-sig')
            modo = 'arquivo'
        else:
            return None, "Nenhum arquivo fornecido", None, None
        
        # Encontrar cabeçalho de forma eficiente
        linhas = conteudo_str.split('\n')
        header_line = None
        
        # Buscar linha de cabeçalho
        for i, line in enumerate(linhas[:10]):  # Limitar busca às primeiras 10 linhas
            if '"Chamado"' in line and '"Tipo Chamado"' in line:
                header_line = i
                break
        
        if header_line is None:
            return None, "Formato de arquivo inválido", None, None
        
        # Ler apenas os dados necessários
        data_str = '\n'.join(linhas[header_line:])
        
        # Usar pandas com tipos de dados otimizados
        df = pd.read_csv(
            io.StringIO(data_str), 
            quotechar='"',
            dtype={
                'Chamado': 'str',
                'Tipo Chamado': 'category',
                'Responsável': 'str',
                'Status': 'category',
                'Prioridade': 'category',
                'Sincronização': 'str',
                'SRE': 'category',
                'Empresa': 'category',
                'Revisões': 'float32'  # Usar float para depois converter para int
            },
            parse_dates=['Criado', 'Modificado']
        )
        
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
        
        # OTIMIZAÇÃO: Formatar nomes apenas se necessário
        if 'Responsável' in df.columns:
            df['Responsável_Formatado'] = df['Responsável'].apply(formatar_nome_responsavel)
        
        # Converter datas com erro handling
        date_columns = ['Criado', 'Modificado']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce', utc=True).dt.tz_convert(None)
        
        # Extrair informações temporais
        if 'Criado' in df.columns:
            df['Ano'] = df['Criado'].dt.year
            df['Mês'] = df['Criado'].dt.month
            df['Mês_Num'] = df['Criado'].dt.month
            df['Dia'] = df['Criado'].dt.day
            df['Hora'] = df['Criado'].dt.hour
            
            # Mapeamento de meses otimizado
            meses_abreviados = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                               'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            df['Nome_Mês'] = df['Mês'].apply(lambda x: meses_abreviados[x-1] if 1 <= x <= 12 else '')
            
            meses_completos = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                              'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            df['Nome_Mês_Completo'] = df['Mês'].apply(lambda x: meses_completos[x-1] if 1 <= x <= 12 else '')
            
            df['Mês_Ano'] = df['Criado'].dt.strftime('%b/%Y')
            df['Ano_Mês'] = df['Criado'].dt.strftime('%Y-%m')
        
        # Converter revisões
        if 'Revisões' in df.columns:
            df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype('int32')
        
        # Calcular hash para verificar mudanças
        hash_conteudo = hashlib.md5(conteudo).hexdigest()
        
        return df, "✅ Dados carregados com sucesso", hash_conteudo, modo
    
    except Exception as e:
        return None, f"Erro: {str(e)}", None, None

def encontrar_arquivo_dados():
    """Tenta encontrar o arquivo de dados"""
    if os.path.exists(CAMINHO_ARQUIVO_PRINCIPAL):
        return CAMINHO_ARQUIVO_PRINCIPAL
    
    for caminho in CAMINHOS_ALTERNATIVOS:
        if os.path.exists(caminho):
            return caminho
    
    return None

def limpar_sessao_dados():
    """Limpa dados da sessão"""
    keys_to_clear = [
        'df_original', 'df_filtrado', 'arquivo_atual',
        'file_hash', 'uploaded_file_name',
        'ultima_atualizacao', 'modo_carregamento'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Limpar cache específico
    if 'cache_clear' not in st.session_state:
        st.cache_data.clear()
        st.session_state.cache_clear = True

def get_horario_brasilia():
    """Retorna horário atual de Brasília"""
    try:
        tz = timezone('America/Sao_Paulo')
        return datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    except:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

# ============================================
# FUNÇÕES DE ANÁLISE OTIMIZADAS
# ============================================
@st.cache_data
def calcular_metricas_rapidas(df):
    """Calcula métricas rápidas para exibição inicial"""
    metricas = {}
    
    # Métricas básicas
    metricas['total_demandas'] = len(df)
    
    if 'Status' in df.columns:
        metricas['sincronizados'] = len(df[df['Status'] == 'Sincronizado'])
    
    if 'Revisões' in df.columns:
        metricas['total_revisoes'] = int(df['Revisões'].sum())
    
    if 'Responsável_Formatado' in df.columns:
        metricas['top_responsavel'] = df['Responsável_Formatado'].value_counts().head(1).index[0]
    
    if 'SRE' in df.columns:
        metricas['total_sres'] = df['SRE'].nunique()
    
    return metricas

@st.cache_data
def gerar_grafico_evolucao(df, ano_selecionado):
    """Gera gráfico de evolução mensal otimizado"""
    if 'Ano' not in df.columns or 'Mês' not in df.columns:
        return None
    
    df_ano = df[df['Ano'] == ano_selecionado].copy()
    
    if df_ano.empty:
        return None
    
    # Agrupar por mês
    demanda_mes = df_ano.groupby('Mês_Num').size().reset_index()
    demanda_mes.columns = ['Mês_Num', 'Quantidade']
    
    # Criar todos os meses
    meses_abreviados = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    todos_meses = pd.DataFrame({
        'Mês_Num': range(1, 13),
        'Nome_Mês': meses_abreviados
    })
    
    demanda_completa = pd.merge(todos_meses, demanda_mes, on='Mês_Num', how='left')
    demanda_completa['Quantidade'] = demanda_completa['Quantidade'].fillna(0).astype(int)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=demanda_completa['Nome_Mês'],
        y=demanda_completa['Quantidade'],
        mode='lines+markers',
        name='Demandas',
        line=dict(color='#1e3799', width=3),
        marker=dict(size=10, color='#0c2461')
    ))
    
    fig.update_layout(
        title=f"Demandas em {ano_selecionado}",
        xaxis_title="Mês",
        yaxis_title="Número de Demandas",
        plot_bgcolor='white',
        height=400,
        showlegend=False,
        margin=dict(t=40, b=40, l=40, r=40)
    )
    
    return fig

# ============================================
# SIDEBAR OTIMIZADA
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h3 style="color: #1e3799; margin: 0;">⚙️ Painel de Controle</h3>
        <p style="color: #6c757d; margin: 0; font-size: 0.9rem;">Filtros e Configurações</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Inicializar session state
    if 'df_original' not in st.session_state:
        st.session_state.df_original = None
        st.session_state.df_filtrado = None
        st.session_state.arquivo_atual = None
        st.session_state.file_hash = None
        st.session_state.uploaded_file_name = None
        st.session_state.ultima_atualizacao = None
        st.session_state.modo_carregamento = None
    
    # SEÇÃO DE UPLOAD PRIMEIRO (mais visível)
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**📤 Importar Dados**")
        
        uploaded_file = st.file_uploader(
            "Selecione um arquivo CSV",
            type=['csv'],
            key="file_uploader",
            help="Faça upload de um novo arquivo CSV",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            # Verificar tamanho do arquivo
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            
            if file_size_mb > 50:  # Limite de 50MB
                st.warning(f"Arquivo muito grande ({file_size_mb:.1f}MB). Use um arquivo menor ou contate o suporte.")
            else:
                with st.spinner('Carregando dados...'):
                    start_time = time.time()
                    
                    df_novo, status, hash_conteudo, modo = carregar_dados_otimizado(uploaded_file=uploaded_file)
                    
                    if df_novo is not None:
                        # Atualizar session state
                        st.session_state.df_original = df_novo
                        st.session_state.df_filtrado = df_novo.copy()
                        st.session_state.arquivo_atual = uploaded_file.name
                        st.session_state.file_hash = hash_conteudo
                        st.session_state.uploaded_file_name = uploaded_file.name
                        st.session_state.ultima_atualizacao = get_horario_brasilia()
                        st.session_state.modo_carregamento = modo
                        
                        st.success(f"✅ {len(df_novo):,} registros carregados em {time.time() - start_time:.1f}s!")
                        
                        # Forçar recarregamento
                        st.rerun()
                    else:
                        st.error(f"❌ {status}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SEÇÃO DE FILTROS (apenas se houver dados)
    if st.session_state.df_original is not None:
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**🔍 Filtros de Análise**")
            
            df = st.session_state.df_original.copy()
            
            # Filtros essenciais apenas
            if 'Ano' in df.columns:
                anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                if anos_disponiveis:
                    ano_selecionado = st.selectbox(
                        "📅 Ano",
                        options=['Todos'] + list(anos_disponiveis),
                        key="filtro_ano"
                    )
                    if ano_selecionado != 'Todos':
                        df = df[df['Ano'] == int(ano_selecionado)]
            
            if 'Status' in df.columns:
                status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox(
                    "📊 Status",
                    options=status_opcoes,
                    key="filtro_status"
                )
                if status_selecionado != 'Todos':
                    df = df[df['Status'] == status_selecionado]
            
            if 'SRE' in df.columns:
                sres = ['Todos'] + sorted(df['SRE'].dropna().unique())
                sre_selecionado = st.selectbox(
                    "🔧 SRE",
                    options=sres,
                    key="filtro_sre"
                )
                if sre_selecionado != 'Todos':
                    df = df[df['SRE'] == sre_selecionado]
            
            # Atualizar dados filtrados
            st.session_state.df_filtrado = df
            
            st.markdown(f"**📈 Registros filtrados:** {len(df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # SEÇÃO DE CONTROLES
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**🔄 Controles**")
        
        if st.session_state.df_original is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Recarregar", use_container_width=True):
                    caminho_atual = encontrar_arquivo_dados()
                    if caminho_atual:
                        with st.spinner('Recarregando...'):
                            df_recarregado, status, hash_conteudo, modo = carregar_dados_otimizado(caminho_arquivo=caminho_atual)
                            if df_recarregado is not None:
                                st.session_state.df_original = df_recarregado
                                st.session_state.df_filtrado = df_recarregado.copy()
                                st.session_state.ultima_atualizacao = get_horario_brasilia()
                                st.success("✅ Dados recarregados!")
                                st.rerun()
            
            with col2:
                if st.button("🗑️ Limpar", use_container_width=True):
                    limpar_sessao_dados()
                    st.success("✅ Dados limpos!")
                    st.rerun()
        
        # Carregamento automático inicial
        if st.session_state.df_original is None:
            if st.button("📂 Carregar arquivo local", use_container_width=True):
                caminho_encontrado = encontrar_arquivo_dados()
                if caminho_encontrado:
                    with st.spinner('Carregando dados locais...'):
                        df_local, status, hash_conteudo, modo = carregar_dados_otimizado(caminho_arquivo=caminho_encontrado)
                        if df_local is not None:
                            st.session_state.df_original = df_local
                            st.session_state.df_filtrado = df_local.copy()
                            st.session_state.arquivo_atual = caminho_encontrado
                            st.session_state.file_hash = hash_conteudo
                            st.session_state.ultima_atualizacao = get_horario_brasilia()
                            st.session_state.modo_carregamento = modo
                            st.rerun()
                        else:
                            st.error(f"❌ {status}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# CONTEÚDO PRINCIPAL OTIMIZADO
# ============================================
st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="color: white; margin: 0; font-size: 1.8rem;">📊 ESTEIRA ADMS</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0;">
            Sistema de Análise de Chamados | SRE
            </p>
        </div>
        <div style="text-align: right;">
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
            Dashboard de Performance
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# DASHBOARD PRINCIPAL
# ============================================
if st.session_state.df_original is not None:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    # 1. INFORMAÇÕES RÁPIDAS
    st.markdown("## 📊 Informações da Base")
    
    if 'Criado' in df.columns and not df.empty:
        data_min = df['Criado'].min()
        data_max = df['Criado'].max()
        
        ultima_atualizacao = st.session_state.get('ultima_atualizacao', get_horario_brasilia())
        
        st.markdown(f"""
        <div class="info-base">
            <p style="margin: 0; font-weight: 600;">📅 Base atualizada: {ultima_atualizacao}</p>
            <p style="margin: 0.3rem 0 0 0; color: #6c757d;">
            Período: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')} | 
            Registros: {len(df):,}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 2. INDICADORES PRINCIPAIS (RÁPIDOS)
    st.markdown("## 📈 INDICADORES PRINCIPAIS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_atual = len(df)
        st.markdown(criar_card_indicador_simples(total_atual, "Total de Demandas", "📋"), unsafe_allow_html=True)
    
    with col2:
        if 'Status' in df.columns:
            sincronizados = len(df[df['Status'] == 'Sincronizado'])
            st.markdown(criar_card_indicador_simples(sincronizados, "Sincronizados", "✅"), unsafe_allow_html=True)
    
    with col3:
        if 'Revisões' in df.columns:
            total_revisoes = int(df['Revisões'].sum())
            st.markdown(criar_card_indicador_simples(total_revisoes, "Total de Revisões", "📝"), unsafe_allow_html=True)
    
    # 3. GRÁFICOS ESSENCIAIS COM CACHE
    st.markdown("---")
    
    # Abas principais
    tab1, tab2, tab3 = st.tabs([
        "📅 Evolução Mensal", 
        "📊 Revisões", 
        "👥 Top Responsáveis"
    ])
    
    with tab1:
        st.markdown('<div class="section-title-exec">EVOLUÇÃO DE DEMANDAS</div>', unsafe_allow_html=True)
        
        if 'Ano' in df.columns:
            anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
            if anos_disponiveis:
                ano_selecionado = st.selectbox(
                    "Selecionar Ano:",
                    options=anos_disponiveis,
                    index=len(anos_disponiveis)-1,
                    key="ano_evolucao_principal"
                )
                
                fig_evolucao = gerar_grafico_evolucao(df, ano_selecionado)
                if fig_evolucao:
                    st.plotly_chart(fig_evolucao, use_container_width=True)
    
    with tab2:
        st.markdown('<div class="section-title-exec">REVISÕES POR RESPONSÁVEL</div>', unsafe_allow_html=True)
        
        if 'Revisões' in df.columns and 'Responsável_Formatado' in df.columns:
            df_com_revisoes = df[df['Revisões'] > 0]
            
            if not df_com_revisoes.empty:
                revisoes_por_responsavel = df_com_revisoes.groupby('Responsável_Formatado')['Revisões'].sum().reset_index()
                revisoes_por_responsavel = revisoes_por_responsavel.sort_values('Revisões', ascending=False).head(15)
                
                fig_revisoes = px.bar(
                    revisoes_por_responsavel,
                    x='Responsável_Formatado',
                    y='Revisões',
                    title='Top 15 Responsáveis com Mais Revisões',
                    labels={'Responsável_Formatado': 'Responsável', 'Revisões': 'Total de Revisões'},
                    color='Revisões',
                    color_continuous_scale='Reds'
                )
                
                fig_revisoes.update_layout(
                    height=500,
                    xaxis_tickangle=45
                )
                
                st.plotly_chart(fig_revisoes, use_container_width=True)
    
    with tab3:
        st.markdown('<div class="section-title-exec">TOP 10 RESPONSÁVEIS</div>', unsafe_allow_html=True)
        
        if 'Responsável_Formatado' in df.columns:
            top_responsaveis = df['Responsável_Formatado'].value_counts().head(10).reset_index()
            top_responsaveis.columns = ['Responsável', 'Demandas']
            
            fig_top = px.bar(
                top_responsaveis,
                x='Demandas',
                y='Responsável',
                orientation='h',
                title='Top 10 Responsáveis com Mais Demandas',
                text='Demandas',
                color='Demandas',
                color_continuous_scale='Blues'
            )
            
            fig_top.update_layout(
                height=500,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig_top, use_container_width=True)
    
    # 4. VISUALIZAÇÃO DE DADOS (SIMPLIFICADA)
    st.markdown("---")
    st.markdown('<div class="section-title-exec">📋 VISUALIZAÇÃO DE DADOS</div>', unsafe_allow_html=True)
    
    # Controles para visualização
    col_view1, col_view2, col_view3 = st.columns(3)
    
    with col_view1:
        num_linhas = st.slider("Número de linhas:", 10, 100, 20, key="num_linhas_view")
    
    with col_view2:
        colunas_selecionadas = st.multiselect(
            "Colunas:",
            options=[col for col in df.columns if col not in ['Criado', 'Modificado', 'Ano', 'Mês', 'Dia', 'Hora']],
            default=['Chamado', 'Tipo_Chamado', 'Responsável_Formatado', 'Status', 'Revisões'],
            key="colunas_view"
        )
    
    with col_view3:
        ordenar_por = st.selectbox(
            "Ordenar por:",
            options=['Data (Recente)', 'Data (Antiga)', 'Revisões', 'Chamado'],
            key="ordenar_view"
        )
    
    # Aplicar ordenação
    df_view = df.copy()
    
    if ordenar_por == 'Data (Recente)' and 'Criado' in df_view.columns:
        df_view = df_view.sort_values('Criado', ascending=False)
    elif ordenar_por == 'Data (Antiga)' and 'Criado' in df_view.columns:
        df_view = df_view.sort_values('Criado', ascending=True)
    elif ordenar_por == 'Revisões' and 'Revisões' in df_view.columns:
        df_view = df_view.sort_values('Revisões', ascending=False)
    elif ordenar_por == 'Chamado' and 'Chamado' in df_view.columns:
        df_view = df_view.sort_values('Chamado')
    
    # Exibir dados
    if colunas_selecionadas:
        st.dataframe(
            df_view[colunas_selecionadas].head(num_linhas),
            use_container_width=True,
            height=400
        )
    
    # Botão de exportação
    csv = df_view[colunas_selecionadas].head(num_linhas).to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Exportar dados visíveis",
        data=csv,
        file_name=f"dados_esteira_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    # TELA INICIAL SIMPLIFICADA
    st.markdown("""
    <div style="text-align: center; padding: 4rem; background: #f8f9fa; border-radius: 10px;">
        <h3 style="color: #495057;">📊 Esteira ADMS Dashboard</h3>
        <p style="color: #6c757d; margin-bottom: 2rem;">
            Sistema de análise e monitoramento de chamados
        </p>
        
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 2rem;">
            <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="font-size: 3rem;">📤</div>
                <h4>Upload de Arquivo</h4>
                <p>Use a barra lateral para fazer upload do CSV</p>
            </div>
            
            <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="font-size: 3rem;">📂</div>
                <h4>Arquivo Local</h4>
                <p>Clique no botão na barra lateral</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")

ultima_atualizacao = st.session_state.get('ultima_atualizacao', get_horario_brasilia())

st.markdown(f"""
<div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e9ecef;">
    <p style="margin: 0; color: #495057;">
    Desenvolvido por: <span style="color: #1e3799;">Kewin Marcel | GEAT</span>
    </p>
    <p style="margin: 0.3rem 0 0 0; color: #6c757d; font-size: 0.85rem;">
    Última atualização: {ultima_atualizacao} | Versão 5.5 Otimizada
    </p>
</div>
""", unsafe_allow_html=True)
