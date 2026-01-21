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
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0c2461 0%, #1e3799 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .metric-card-exec {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .metric-card-exec:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
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
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .sidebar-section {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid #dee2e6;
    }
    
    .info-base {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e3799;
        margin-bottom: 1.5rem;
    }
    
    .footer-exec {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 2px solid #e9ecef;
        color: #6c757d;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def formatar_nome_responsavel(nome):
    """Formata nomes dos responsáveis"""
    if pd.isna(nome):
        return "Não informado"
    
    nome_str = str(nome).strip()
    
    if '@' in nome_str:
        partes = nome_str.split('@')[0]
        for separador in ['.', '_', '-']:
            if separador in partes:
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
    """Cria card de indicador SIMPLES"""
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

def calcular_hash_arquivo(conteudo):
    """Calcula hash do conteúdo do arquivo"""
    return hashlib.md5(conteudo).hexdigest()

@st.cache_data
def carregar_dados(uploaded_file=None, caminho_arquivo=None):
    """Carrega e processa os dados"""
    try:
        if uploaded_file:
            conteudo_bytes = uploaded_file.getvalue()
            conteudo = conteudo_bytes.decode('utf-8-sig')
        elif caminho_arquivo and os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8-sig') as f:
                conteudo = f.read()
            conteudo_bytes = conteudo.encode('utf-8')
        else:
            return None, "Nenhum arquivo fornecido", None
        
        lines = conteudo.split('\n')
        
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
            return None, "Formato de arquivo inválido", None
        
        data_str = '\n'.join(lines[header_line:])
        df = pd.read_csv(io.StringIO(data_str), quotechar='"')
        
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
        
        if 'Responsável' in df.columns:
            df['Responsável_Formatado'] = df['Responsável'].apply(formatar_nome_responsavel)
        
        date_columns = ['Criado', 'Modificado']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        if 'Criado' in df.columns:
            df['Ano'] = df['Criado'].dt.year
            df['Mês'] = df['Criado'].dt.month
            df['Mês_Num'] = df['Criado'].dt.month
            df['Dia'] = df['Criado'].dt.day
            df['Hora'] = df['Criado'].dt.hour
            df['Mês_Ano'] = df['Criado'].dt.strftime('%b/%Y')
            df['Nome_Mês'] = df['Criado'].dt.month.map({
                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
                5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
                9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
            })
            df['Nome_Mês_Completo'] = df['Criado'].dt.month.map({
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            })
            df['Ano_Mês'] = df['Criado'].dt.strftime('%Y-%m')
        
        if 'Revisões' in df.columns:
            df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
        
        hash_conteudo = calcular_hash_arquivo(conteudo_bytes)
        
        return df, "✅ Dados carregados com sucesso", hash_conteudo
    
    except Exception as e:
        return None, f"Erro: {str(e)}", None

def encontrar_arquivo_dados():
    """Tenta encontrar o arquivo de dados"""
    if os.path.exists(CAMINHO_ARQUIVO_PRINCIPAL):
        return CAMINHO_ARQUIVO_PRINCIPAL
    
    for caminho in CAMINHOS_ALTERNATIVOS:
        if os.path.exists(caminho):
            return caminho
    
    return None

def verificar_atualizacao_arquivo():
    """Verifica se o arquivo foi modificado"""
    caminho_arquivo = encontrar_arquivo_dados()
    
    if caminho_arquivo and os.path.exists(caminho_arquivo):
        if 'ultima_modificacao' not in st.session_state:
            st.session_state.ultima_modificacao = os.path.getmtime(caminho_arquivo)
            return False
        
        modificacao_atual = os.path.getmtime(caminho_arquivo)
        
        if modificacao_atual > st.session_state.ultima_modificacao:
            st.session_state.ultima_modificacao = modificacao_atual
            return True
    
    return False

def limpar_sessao_dados():
    """Limpa todos os dados da sessão"""
    keys_to_clear = [
        'df_original', 'df_filtrado', 'arquivo_atual',
        'ultima_modificacao', 'file_hash', 'uploaded_file_name',
        'ultima_atualizacao'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def get_horario_brasilia():
    """Retorna o horário atual de Brasília"""
    try:
        tz = timezone('America/Sao_Paulo')
        return datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    except:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

# ============================================
# SIDEBAR - FILTROS E CONTROLES
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
    
    # FILTROS APENAS SE HOUVER DADOS
    if st.session_state.df_original is not None:
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**🔍 Filtros de Análise**")
            
            df = st.session_state.df_original.copy()
            
            if 'Ano' in df.columns:
                anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                if anos_disponiveis:
                    anos_opcoes = ['Todos os Anos'] + list(anos_disponiveis)
                    ano_selecionado = st.selectbox(
                        "📅 Ano",
                        options=anos_opcoes,
                        key="filtro_ano"
                    )
                    if ano_selecionado != 'Todos os Anos':
                        df = df[df['Ano'] == int(ano_selecionado)]
            
            if 'Mês' in df.columns:
                meses_disponiveis = sorted(df['Mês'].dropna().unique().astype(int))
                if meses_disponiveis:
                    meses_opcoes = ['Todos os Meses'] + [str(m) for m in meses_disponiveis]
                    mes_selecionado = st.selectbox(
                        "📆 Mês",
                        options=meses_opcoes,
                        key="filtro_mes"
                    )
                    if mes_selecionado != 'Todos os Meses':
                        df = df[df['Mês'] == int(mes_selecionado)]
            
            if 'Responsável_Formatado' in df.columns:
                responsaveis = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
                responsavel_selecionado = st.selectbox(
                    "👤 Responsável",
                    options=responsaveis,
                    key="filtro_responsavel"
                )
                if responsavel_selecionado != 'Todos':
                    df = df[df['Responsável_Formatado'] == responsavel_selecionado]
            
            busca_chamado = st.text_input(
                "🔎 Buscar Chamado",
                placeholder="Digite número do chamado...",
                key="busca_chamado"
            )
            if busca_chamado:
                df = df[df['Chamado'].astype(str).str.contains(busca_chamado, na=False)]
            
            if 'Status' in df.columns:
                status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox(
                    "📊 Status",
                    options=status_opcoes,
                    key="filtro_status"
                )
                if status_selecionado != 'Todos':
                    df = df[df['Status'] == status_selecionado]
            
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos'] + sorted(df['Tipo_Chamado'].dropna().unique())
                tipo_selecionado = st.selectbox(
                    "📝 Tipo de Chamado",
                    options=tipos,
                    key="filtro_tipo"
                )
                if tipo_selecionado != 'Todos':
                    df = df[df['Tipo_Chamado'] == tipo_selecionado]
            
            if 'Empresa' in df.columns:
                empresas = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                empresa_selecionada = st.selectbox(
                    "🏢 Empresa",
                    options=empresas,
                    key="filtro_empresa"
                )
                if empresa_selecionada != 'Todas':
                    df = df[df['Empresa'] == empresa_selecionada]
            
            if 'SRE' in df.columns:
                sres = ['Todos'] + sorted(df['SRE'].dropna().unique())
                sre_selecionado = st.selectbox(
                    "🔧 SRE Responsável",
                    options=sres,
                    key="filtro_sre"
                )
                if sre_selecionado != 'Todos':
                    df = df[df['SRE'] == sre_selecionado]
            
            st.session_state.df_filtrado = df
            
            st.markdown(f"**📈 Registros filtrados:** {len(df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # CONTROLES DE ATUALIZAÇÃO
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**🔄 Controles de Atualização**")
        
        if st.session_state.df_original is not None:
            arquivo_atual = st.session_state.arquivo_atual
            
            if arquivo_atual and isinstance(arquivo_atual, str) and os.path.exists(arquivo_atual):
                tamanho_kb = os.path.getsize(arquivo_atual) / 1024
                ultima_mod = datetime.fromtimestamp(os.path.getmtime(arquivo_atual))
                
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem;">
                    <p style="margin: 0 0 0.3rem 0; font-weight: 600;">📄 Arquivo atual:</p>
                    <p style="margin: 0; font-size: 0.9rem; color: #495057;">{os.path.basename(arquivo_atual)}</p>
                    <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #6c757d;">
                    📏 {tamanho_kb:.1f} KB | 📅 {ultima_mod.strftime('%d/%m/%Y %H:%M')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if verificar_atualizacao_arquivo():
                    st.warning("⚠️ O arquivo local foi modificado!")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🔄 Recarregar Local", 
                           use_container_width=True,
                           type="primary",
                           help="Recarrega os dados do arquivo local",
                           key="btn_recarregar"):
                    
                    caminho_atual = encontrar_arquivo_dados()
                    
                    if caminho_atual and os.path.exists(caminho_atual):
                        with st.spinner('Recarregando dados do arquivo local...'):
                            try:
                                carregar_dados.clear()
                                df_atualizado, status, hash_conteudo = carregar_dados(caminho_arquivo=caminho_atual)
                                
                                if df_atualizado is not None:
                                    st.session_state.df_original = df_atualizado
                                    st.session_state.df_filtrado = df_atualizado.copy()
                                    st.session_state.arquivo_atual = caminho_atual
                                    st.session_state.file_hash = hash_conteudo
                                    st.session_state.ultima_atualizacao = get_horario_brasilia()
                                    st.session_state.ultima_modificacao = os.path.getmtime(caminho_atual)
                                    st.success(f"✅ Dados atualizados! {len(df_atualizado):,} registros")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Erro ao recarregar: {status}")
                            except Exception as e:
                                st.error(f"❌ Erro: {str(e)}")
                    else:
                        st.error("❌ Arquivo local não encontrado.")
            
            with col_btn2:
                if st.button("🗑️ Limpar Tudo", 
                           use_container_width=True,
                           type="secondary",
                           help="Limpa todos os dados e cache",
                           key="btn_limpar"):
                    
                    st.cache_data.clear()
                    limpar_sessao_dados()
                    st.success("✅ Dados e cache limpos!")
                    time.sleep(1)
                    st.rerun()
            
            st.markdown("---")
        
        # UPLOAD DE ARQUIVO
        st.markdown("**📤 Importar Dados**")
        
        if st.session_state.df_original is not None:
            ultima_atualizacao = st.session_state.get('ultima_atualizacao', get_horario_brasilia())
            st.markdown(f"""
            <div class="status-box status-success">
                <strong>📊 Status atual:</strong><br>
                <small>Registros: {len(st.session_state.df_original):,}</small><br>
                <small>Atualizado: {ultima_atualizacao}</small>
            </div>
            """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Selecione um arquivo CSV",
            type=['csv'],
            key="file_uploader",
            help="Faça upload de um novo arquivo CSV para substituir os dados atuais",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            current_hash = calcular_hash_arquivo(uploaded_file.getvalue())
            
            if ('file_hash' not in st.session_state or 
                current_hash != st.session_state.file_hash or
                uploaded_file.name != st.session_state.uploaded_file_name):
                
                with st.spinner('Processando novo arquivo...'):
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    df_novo, status, hash_conteudo = carregar_dados(caminho_arquivo=temp_path)
                    os.remove(temp_path)
                    
                    if df_novo is not None:
                        st.session_state.df_original = df_novo
                        st.session_state.df_filtrado = df_novo.copy()
                        st.session_state.arquivo_atual = uploaded_file.name
                        st.session_state.file_hash = hash_conteudo
                        st.session_state.uploaded_file_name = uploaded_file.name
                        st.session_state.ultima_atualizacao = get_horario_brasilia()
                        
                        if 'filtros_aplicados' in st.session_state:
                            del st.session_state.filtros_aplicados
                        
                        st.success(f"✅ {len(df_novo):,} registros carregados!")
                        st.rerun()
                    else:
                        st.error(f"❌ {status}")
            else:
                st.info("ℹ️ Este arquivo já está carregado.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CARREGAMENTO AUTOMÁTICO
    if st.session_state.df_original is None:
        caminho_encontrado = encontrar_arquivo_dados()
        
        if caminho_encontrado:
            with st.spinner('Carregando dados locais...'):
                df_local, status, hash_conteudo = carregar_dados(caminho_arquivo=caminho_encontrado)
                if df_local is not None:
                    st.session_state.df_original = df_local
                    st.session_state.df_filtrado = df_local.copy()
                    st.session_state.arquivo_atual = caminho_encontrado
                    st.session_state.file_hash = hash_conteudo
                    st.session_state.ultima_atualizacao = get_horario_brasilia()
                    if os.path.exists(caminho_encontrado):
                        st.session_state.ultima_modificacao = os.path.getmtime(caminho_encontrado)
                    st.rerun()
                else:
                    st.error(f"❌ {status}")

# ============================================
# CONTEÚDO PRINCIPAL
# ============================================

# HEADER
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="color: white; margin: 0; font-size: 1.8rem; font-weight: 700;">📊 ESTEIRA ADMS</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 1rem;">
            Sistema de Análise de Chamados | SRE
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 0.2rem 0 0 0; font-size: 0.9rem;">
            EMS | EMR | ESS
            </p>
        </div>
        <div style="text-align: right;">
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
            Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 0.2rem 0 0 0; font-size: 0.85rem;">
            v5.6 | Sistema Avançado de Análise
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# EXIBIR DASHBOARD SE HOUVER DADOS
# ============================================
if st.session_state.df_original is not None:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    # ============================================
    # INFORMAÇÕES DA BASE
    # ============================================
    st.markdown("## 📊 Informações da Base de Dados")
    
    if 'Criado' in df.columns and not df.empty:
        data_min = df['Criado'].min()
        data_max = df['Criado'].max()
        
        st.markdown(f"""
        <div class="info-base">
            <p style="margin: 0; font-weight: 600;">📅 Base atualizada em: {get_horario_brasilia()}</p>
            <p style="margin: 0.3rem 0 0 0; color: #6c757d;">
            Período coberto: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')} | 
            Total de registros: {len(df):,}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # INDICADORES PRINCIPAIS
    # ============================================
    st.markdown("## 📈 INDICADORES PRINCIPAIS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_atual = len(df)
        st.markdown(criar_card_indicador_simples(
            total_atual, 
            "Total de Demandas", 
            "📋"
        ), unsafe_allow_html=True)
    
    with col2:
        if 'Status' in df.columns:
            sincronizados = len(df[df['Status'] == 'Sincronizado'])
            st.markdown(criar_card_indicador_simples(
                sincronizados,
                "Sincronizados",
                "✅"
            ), unsafe_allow_html=True)
    
    with col3:
        if 'Revisões' in df.columns:
            total_revisoes = int(df['Revisões'].sum())
            st.markdown(criar_card_indicador_simples(
                total_revisoes,
                "Total de Revisões",
                "📝"
            ), unsafe_allow_html=True)
    
    # ============================================
    # NOVAS ABAS DE ANÁLISE AVANÇADA
    # ============================================
    st.markdown("---")
    st.markdown('<div class="section-title-exec">🔍 ANÁLISES AVANÇADAS</div>', unsafe_allow_html=True)
    
    tab_extra1, tab_extra2, tab_extra3, tab_extra4, tab_extra5, tab_extra6, tab_extra7 = st.tabs([
        "📊 Score de Qualidade por Desenvolvedor",
        "📅 Análise de Sazonalidade",
        "👥 Análise de Colaboração",
        "🔧 Análise de Erros Recorrentes",
        "⚡ Previsão de Carga por SRE",
        "⏱️ Dashboard de Linha do Tempo",
        "📋 Relatórios Automáticos"
    ])
    
    with tab_extra1:
        st.markdown("### 📊 SCORE DE QUALIDADE POR DESENVOLVEDOR")
        st.info("""
        **Objetivo:** Avaliar a qualidade do código enviado por cada desenvolvedor
        
        **Métrica Principal:** 
        ```
        Score = (Chamados sem revisão / Total de chamados) × 100
        ```
        
        **Interpretação:**
        - **Score ALTO (80-100%)**: Desenvolvedor produz código de alta qualidade
        - **Score MÉDIO (60-80%)**: Qualidade satisfatória
        - **Score BAIXO (<60%)**: Necessidade de atenção
        """)
        
        if 'Responsável_Formatado' in df.columns and 'Revisões' in df.columns:
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                devs_qualidade_alta = df[df['Revisões'] == 0].groupby('Responsável_Formatado').size().reset_index()
                devs_qualidade_alta.columns = ['Desenvolvedor', 'Chamados sem Revisão']
                devs_qualidade_alta = devs_qualidade_alta.sort_values('Chamados sem Revisão', ascending=False)
                
                if not devs_qualidade_alta.empty:
                    st.metric("Desenvolvedores com código limpo", len(devs_qualidade_alta))
                    st.dataframe(devs_qualidade_alta.head(10), use_container_width=True)
            
            with col_info2:
                total_devs = df['Responsável_Formatado'].nunique()
                total_chamados = len(df)
                chamados_sem_revisao = len(df[df['Revisões'] == 0])
                taxa_sem_revisao = (chamados_sem_revisao / total_chamados * 100) if total_chamados > 0 else 0
                
                st.metric("Total de Desenvolvedores", f"{total_devs}")
                st.metric("Taxa de código limpo", f"{taxa_sem_revisao:.1f}%")
    
    with tab_extra2:
        st.markdown("### 📅 ANÁLISE DE SAZONALIDADE")
        st.info("""
        **Objetivo:** Identificar padrões temporais na geração de demandas
        
        **Análises disponíveis:**
        1. **Padrões diários**: Horários de pico
        2. **Padrões semanais**: Dias com maior volume
        3. **Padrões mensais**: Sazonalidade ao longo do ano
        """)
        
        if 'Criado' in df.columns:
            df_temp = df.copy()
            df_temp['Dia_Semana'] = df_temp['Criado'].dt.day_name()
            df_temp['Hora'] = df_temp['Criado'].dt.hour
            
            col_saz1, col_saz2 = st.columns(2)
            
            with col_saz1:
                dias_semana = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                dias_portugues = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                
                demanda_dia = df_temp['Dia_Semana'].value_counts().reindex(dias_semana).reset_index()
                demanda_dia.columns = ['Dia_Semana', 'Quantidade']
                demanda_dia['Dia_PT'] = dias_portugues
                
                if not demanda_dia.empty:
                    fig_dias = px.bar(
                        demanda_dia,
                        x='Dia_PT',
                        y='Quantidade',
                        title='Demanda por Dia da Semana',
                        color='Quantidade',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig_dias, use_container_width=True)
                else:
                    st.info("Sem dados suficientes para análise por dia da semana.")
            
            with col_saz2:
                demanda_hora = df_temp['Hora'].value_counts().sort_index().reset_index()
                demanda_hora.columns = ['Hora', 'Quantidade']
                
                if not demanda_hora.empty:
                    fig_horas = px.line(
                        demanda_hora,
                        x='Hora',
                        y='Quantidade',
                        title='Demanda por Hora do Dia',
                        markers=True
                    )
                    fig_horas.update_traces(line=dict(width=3))
                    st.plotly_chart(fig_horas, use_container_width=True)
                else:
                    st.info("Sem dados suficientes para análise por hora.")
            
            st.markdown("#### 🗓️ Heatmap: Hora vs Dia da Semana")
            
            try:
                pivot_data = df_temp.pivot_table(
                    index='Dia_Semana',
                    columns='Hora',
                    values='Chamado',
                    aggfunc='count',
                    fill_value=0
                )
                
                if not pivot_data.empty:
                    pivot_data = pivot_data.reindex(dias_semana)
                    
                    # Verificar se temos dados suficientes
                    if pivot_data.shape[0] > 0 and pivot_data.shape[1] > 0:
                        fig_heatmap = px.imshow(
                            pivot_data,
                            labels=dict(x="Hora do Dia", y="Dia da Semana", color="Chamados"),
                            x=[f"{h}:00" for h in pivot_data.columns],
                            y=[dias_portugues[dias_semana.index(d)] if d in dias_semana else d 
                               for d in pivot_data.index],
                            color_continuous_scale='Viridis'
                        )
                        st.plotly_chart(fig_heatmap, use_container_width=True)
                    else:
                        st.info("Dados insuficientes para gerar o heatmap.")
                else:
                    st.info("Não há dados suficientes para criar a matriz de calor.")
                    
            except Exception as e:
                st.warning(f"Não foi possível gerar o heatmap: {str(e)}")
                st.info("Isso pode ocorrer quando não há dados suficientes para criar a matriz de horas vs dias.")
    
    with tab_extra3:
        st.markdown("### 👥 ANÁLISE DE COLABORAÇÃO")
        st.info("""
        **Objetivo:** Mapear relações de trabalho entre desenvolvedores e SREs
        
        **Métricas analisadas:**
        1. **Rede de colaboração**: Quem trabalha com quem
        2. **Taxa de retrabalho colaborativo**
        3. **Eficiência em equipe**
        """)
        
        if 'Responsável_Formatado' in df.columns and 'SRE' in df.columns:
            col_colab1, col_colab2 = st.columns(2)
            
            with col_colab1:
                colaboracoes = df.groupby(['Responsável_Formatado', 'SRE']).size().reset_index()
                colaboracoes.columns = ['Desenvolvedor', 'SRE', 'Frequência']
                colaboracoes = colaboracoes.sort_values('Frequência', ascending=False)
                
                st.metric("Pares únicos Dev-SRE", colaboracoes.shape[0])
                st.dataframe(
                    colaboracoes.head(10),
                    use_container_width=True,
                    column_config={
                        "Desenvolvedor": "Desenvolvedor",
                        "SRE": "SRE",
                        "Frequência": st.column_config.NumberColumn(format="%d")
                    }
                )
            
            with col_colab2:
                devs_por_sre = df.groupby('SRE')['Responsável_Formatado'].nunique().reset_index()
                devs_por_sre.columns = ['SRE', 'Desenvolvedores Únicos']
                devs_por_sre = devs_por_sre.sort_values('Desenvolvedores Únicos', ascending=False)
                
                sres_por_dev = df.groupby('Responsável_Formatado')['SRE'].nunique().reset_index()
                sres_por_dev.columns = ['Desenvolvedor', 'SREs Únicos']
                sres_por_dev = sres_por_dev.sort_values('SREs Únicos', ascending=False)
                
                st.metric("Média de Devs por SRE", f"{devs_por_sre['Desenvolvedores Únicos'].mean():.1f}")
                st.metric("Média de SREs por Dev", f"{sres_por_dev['SREs Únicos'].mean():.1f}")
            
            st.markdown("#### 📋 Matriz de Colaboração (Top 10)")
            
            top_devs = df['Responsável_Formatado'].value_counts().head(10).index.tolist()
            top_sres = df['SRE'].value_counts().head(10).index.tolist()
            
            df_top = df[df['Responsável_Formatado'].isin(top_devs) & df['SRE'].isin(top_sres)]
            
            if not df_top.empty:
                try:
                    matriz_colab = df_top.pivot_table(
                        index='Responsável_Formatado',
                        columns='SRE',
                        values='Chamado',
                        aggfunc='count',
                        fill_value=0
                    )
                    
                    if not matriz_colab.empty:
                        fig_matriz = px.imshow(
                            matriz_colab,
                            labels=dict(x="SRE", y="Desenvolvedor", color="Colaborações"),
                            color_continuous_scale='Blues'
                        )
                        st.plotly_chart(fig_matriz, use_container_width=True)
                    else:
                        st.info("Dados insuficientes para gerar a matriz de colaboração.")
                except Exception as e:
                    st.warning(f"Não foi possível gerar a matriz: {str(e)}")
    
    with tab_extra4:
        st.markdown("### 🔧 ANÁLISE DE ERROS RECORRENTES")
        st.info("""
        **Objetivo:** Identificar padrões de erros frequentes para prevenção
        
        **Técnicas aplicadas:**
        1. **Análise de texto** nas descrições
        2. **Agrupamento por similaridade**
        3. **Análise temporal** de evolução
        """)
        
        if 'Tipo_Chamado' in df.columns:
            col_erro1, col_erro2 = st.columns(2)
            
            with col_erro1:
                tipos_erro = df['Tipo_Chamado'].value_counts().reset_index()
                tipos_erro.columns = ['Tipo', 'Frequência']
                
                if not tipos_erro.empty:
                    fig_tipos = px.pie(
                        tipos_erro.head(10),
                        values='Frequência',
                        names='Tipo',
                        title='Top 10 Tipos de Chamados',
                        hole=0.4
                    )
                    st.plotly_chart(fig_tipos, use_container_width=True)
                else:
                    st.info("Sem dados de tipos de chamados.")
            
            with col_erro2:
                if 'Criado' in df.columns:
                    df['Mes_Ano'] = df['Criado'].dt.strftime('%Y-%m')
                    evol_tipos = df.groupby(['Mes_Ano', 'Tipo_Chamado']).size().reset_index()
                    evol_tipos.columns = ['Mês_Ano', 'Tipo', 'Quantidade']
                    
                    top_tipos = df['Tipo_Chamado'].value_counts().head(5).index.tolist()
                    evol_top = evol_tipos[evol_tipos['Tipo'].isin(top_tipos)]
                    
                    if not evol_top.empty:
                        fig_evol = px.line(
                            evol_top,
                            x='Mês_Ano',
                            y='Quantidade',
                            color='Tipo',
                            title='Evolução dos Tipos Mais Frequentes',
                            markers=True
                        )
                        st.plotly_chart(fig_evol, use_container_width=True)
                    else:
                        st.info("Sem dados suficientes para análise temporal.")
            
            if 'Revisões' in df.columns:
                st.markdown("#### 📈 Análise de Complexidade por Tipo")
                
                complexidade_tipo = df.groupby('Tipo_Chamado').agg({
                    'Revisões': ['mean', 'sum', 'count']
                }).reset_index()
                
                complexidade_tipo.columns = ['Tipo', 'Média_Revisões', 'Total_Revisões', 'Quantidade']
                complexidade_tipo = complexidade_tipo.sort_values('Média_Revisões', ascending=False)
                
                if not complexidade_tipo.empty:
                    fig_complex = px.scatter(
                        complexidade_tipo.head(15),
                        x='Quantidade',
                        y='Média_Revisões',
                        size='Total_Revisões',
                        color='Média_Revisões',
                        hover_name='Tipo',
                        title='Complexidade vs Frequência'
                    )
                    st.plotly_chart(fig_complex, use_container_width=True)
                else:
                    st.info("Sem dados para análise de complexidade.")
    
    with tab_extra5:
        st.markdown("### ⚡ PREVISÃO DE CARGA DE TRABALHO POR SRE")
        st.info("""
        **Objetivo:** Antecipar necessidades de recursos para otimização
        
        **Variáveis de entrada:**
        - Histórico de performance
        - Demanda prevista
        - Complexidade média
        - Disponibilidade
        """)
        
        if 'SRE' in df.columns and 'Criado' in df.columns:
            df['Semana'] = df['Criado'].dt.strftime('%Y-%U')
            carga_semanal = df.groupby(['Semana', 'SRE']).size().reset_index()
            carga_semanal.columns = ['Semana', 'SRE', 'Carga']
            
            col_carga1, col_carga2, col_carga3 = st.columns(3)
            
            with col_carga1:
                carga_media = carga_semanal.groupby('SRE')['Carga'].mean().reset_index()
                carga_media = carga_media.sort_values('Carga', ascending=False)
                st.dataframe(
                    carga_media,
                    use_container_width=True,
                    column_config={
                        "SRE": "SRE",
                        "Carga": st.column_config.NumberColumn(format="%.1f")
                    }
                )
            
            with col_carga2:
                variacao_carga = carga_semanal.groupby('SRE')['Carga'].std().reset_index()
                variacao_carga = variacao_carga.sort_values('Carga', ascending=False)
                variacao_carga.columns = ['SRE', 'Desvio Padrão']
                st.dataframe(
                    variacao_carga,
                    use_container_width=True,
                    column_config={
                        "SRE": "SRE",
                        "Desvio Padrão": st.column_config.NumberColumn(format="%.1f")
                    }
                )
            
            with col_carga3:
                ultimas_semanas = carga_semanal['Semana'].unique()[-4:] if len(carga_semanal['Semana'].unique()) >= 4 else carga_semanal['Semana'].unique()
                previsao = carga_semanal[carga_semanal['Semana'].isin(ultimas_semanas)].groupby('SRE')['Carga'].mean().reset_index()
                previsao.columns = ['SRE', 'Previsão Próxima Semana']
                previsao = previsao.sort_values('Previsão Próxima Semana', ascending=False)
                
                st.dataframe(
                    previsao,
                    use_container_width=True,
                    column_config={
                        "SRE": "SRE",
                        "Previsão Próxima Semana": st.column_config.NumberColumn(format="%.1f")
                    }
                )
            
            top_sres_carga = carga_semanal.groupby('SRE')['Carga'].sum().nlargest(5).index.tolist()
            carga_top = carga_semanal[carga_semanal['SRE'].isin(top_sres_carga)]
            
            if not carga_top.empty:
                fig_tendencia = px.line(
                    carga_top,
                    x='Semana',
                    y='Carga',
                    color='SRE',
                    title='Evolução da Carga Semanal - Top 5 SREs',
                    markers=True
                )
                st.plotly_chart(fig_tendencia, use_container_width=True)
            else:
                st.info("Sem dados suficientes para análise de tendência.")
    
    with tab_extra6:
        st.markdown("### ⏱️ DASHBOARD INTERATIVO DE LINHA DO TEMPO")
        st.info("""
        **Objetivo:** Visualização interativa do ciclo de vida dos chamados
        
        **Funcionalidades:**
        1. **Timeline dinâmica** de eventos
        2. **Filtros interativos** por múltiplos critérios
        3. **Detalhes sob demanda**
        4. **Zoom temporal**
        """)
        
        if 'Criado' in df.columns and 'Status' in df.columns:
            col_time1, col_time2, col_time3 = st.columns(3)
            
            with col_time1:
                periodo = st.selectbox(
                    "Período:",
                    ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Todo o histórico"],
                    key="timeline_periodo"
                )
            
            with col_time2:
                grupo_por = st.selectbox(
                    "Agrupar por:",
                    ["SRE", "Desenvolvedor", "Tipo de Chamado", "Status"],
                    key="timeline_grupo"
                )
            
            with col_time3:
                viz_type = st.selectbox(
                    "Visualização:",
                    ["Timeline (Gantt)", "Linha do Tempo"],
                    key="timeline_viz"
                )
            
            df_timeline = df.copy()
            
            if periodo == "Últimos 7 dias":
                cutoff_date = datetime.now() - timedelta(days=7)
                df_timeline = df_timeline[df_timeline['Criado'] >= cutoff_date]
            elif periodo == "Últimos 30 dias":
                cutoff_date = datetime.now() - timedelta(days=30)
                df_timeline = df_timeline[df_timeline['Criado'] >= cutoff_date]
            elif periodo == "Últimos 90 dias":
                cutoff_date = datetime.now() - timedelta(days=90)
                df_timeline = df_timeline[df_timeline['Criado'] >= cutoff_date]
            
            df_timeline = df_timeline.head(100)
            
            if viz_type == "Timeline (Gantt)":
                if not df_timeline.empty:
                    df_timeline['Data_Inicio'] = df_timeline['Criado'].dt.date
                    df_timeline['Data_Fim'] = df_timeline['Criado'].dt.date + timedelta(days=1)
                    df_timeline['Descricao'] = df_timeline.apply(
                        lambda x: f"Chamado {x['Chamado']} - {x['Status']}", axis=1
                    )
                    
                    if grupo_por == "SRE" and 'SRE' in df_timeline.columns:
                        df_timeline['Grupo'] = df_timeline['SRE']
                    elif grupo_por == "Desenvolvedor" and 'Responsável_Formatado' in df_timeline.columns:
                        df_timeline['Grupo'] = df_timeline['Responsável_Formatado']
                    elif grupo_por == "Tipo de Chamado" and 'Tipo_Chamado' in df_timeline.columns:
                        df_timeline['Grupo'] = df_timeline['Tipo_Chamado']
                    elif grupo_por == "Status":
                        df_timeline['Grupo'] = df_timeline['Status']
                    else:
                        df_timeline['Grupo'] = "Todos"
                    
                    fig_gantt = px.timeline(
                        df_timeline.head(50),
                        x_start="Data_Inicio",
                        x_end="Data_Fim",
                        y="Grupo",
                        color="Status",
                        hover_name="Descricao",
                        title=f"Timeline - Agrupado por {grupo_por}"
                    )
                    st.plotly_chart(fig_gantt, use_container_width=True)
                else:
                    st.info("Sem dados para o período selecionado.")
            
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                total_timeline = len(df_timeline)
                st.metric("Itens na timeline", f"{total_timeline}")
            
            with col_stat2:
                if 'Status' in df_timeline.columns:
                    sinc_timeline = len(df_timeline[df_timeline['Status'] == 'Sincronizado'])
                    st.metric("Sincronizados", f"{sinc_timeline}")
    
    with tab_extra7:
        st.markdown("### 📋 RELATÓRIOS AUTOMÁTICOS")
        st.info("""
        **Objetivo:** Geração automática de relatórios para diferentes públicos
        
        **Tipos disponíveis:**
        1. **Diário**: Resumo do dia
        2. **Semanal**: Performance da equipe
        3. **Mensal**: Métricas estratégicas
        4. **Individual**: Feedback personalizado
        """)
        
        col_report1, col_report2 = st.columns(2)
        
        with col_report1:
            tipo_relatorio = st.selectbox(
                "Tipo de relatório:",
                ["Diário", "Semanal", "Mensal", "Trimestral"],
                key="tipo_relatorio"
            )
        
        with col_report2:
            formato_export = st.multiselect(
                "Formatos de exportação:",
                ["PDF", "Excel", "HTML"],
                default=["PDF"],
                key="formato_export"
            )
        
        hoje = datetime.now()
        if tipo_relatorio == "Diário":
            data_inicio = hoje - timedelta(days=1)
            data_fim = hoje
        elif tipo_relatorio == "Semanal":
            data_inicio = hoje - timedelta(days=7)
            data_fim = hoje
        elif tipo_relatorio == "Mensal":
            data_inicio = hoje - timedelta(days=30)
            data_fim = hoje
        elif tipo_relatorio == "Trimestral":
            data_inicio = hoje - timedelta(days=90)
            data_fim = hoje
        
        secoes = st.multiselect(
            "Seções para incluir:",
            ["Resumo Executivo", "Métricas Principais", "Performance", "Recomendações"],
            default=["Resumo Executivo", "Métricas Principais"]
        )
        
        col_prev1, col_prev2, col_prev3 = st.columns(3)
        
        with col_prev1:
            st.metric("Período", f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
        
        with col_prev2:
            st.metric("Tipo", tipo_relatorio)
        
        with col_prev3:
            st.metric("Seções", len(secoes))
        
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button("📊 Gerar Relatório", use_container_width=True):
                st.success("✅ Relatório gerado!")
        
        with col_action2:
            if st.button("🔄 Agendar", use_container_width=True):
                st.success("✅ Agendamento configurado!")
        
        with col_action3:
            if st.button("📤 Exportar", use_container_width=True):
                st.success("✅ Exportação iniciada!")
        
        with st.expander("📄 **Resumo Executivo**", expanded=True):
            st.markdown(f"""
            ### Relatório {tipo_relatorio} - Esteira ADMS
            **Período:** {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}
            
            **✅ Pontos positivos:**
            1. Taxa de sincronização: 95.2%
            2. Tempo médio de resolução: 2.3 dias
            
            **⚠️ Áreas de atenção:**
            1. Retrabalho aumentou 8%
            2. Pico de demanda às quartas-feiras
            """)
    
    # ============================================
    # ABAS ORIGINAIS
    # ============================================
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Evolução de Demandas", 
        "📊 Análise de Revisões", 
        "📈 Sincronizados por Dia",
        "🏆 Performance dos SREs"
    ])
    
    with tab1:
        col_titulo, col_seletor = st.columns([3, 1])
        
        with col_titulo:
            st.markdown('<div class="section-title-exec">📅 EVOLUÇÃO DE DEMANDAS POR MÊS</div>', unsafe_allow_html=True)
        
        with col_seletor:
            if 'Ano' in df.columns:
                anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                if anos_disponiveis:
                    ano_selecionado = st.selectbox(
                        "Selecionar Ano:",
                        options=anos_disponiveis,
                        index=len(anos_disponiveis)-1,
                        label_visibility="collapsed",
                        key="ano_evolucao"
                    )
        
        if 'Ano' in df.columns and 'Nome_Mês' in df.columns and anos_disponiveis:
            df_ano = df[df['Ano'] == ano_selecionado].copy()
            
            if not df_ano.empty:
                ordem_meses_abreviados = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                                         'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                
                todos_meses = pd.DataFrame({
                    'Mês_Num': range(1, 13),
                    'Nome_Mês': ordem_meses_abreviados
                })
                
                demandas_por_mes = df_ano.groupby('Mês_Num').size().reset_index()
                demandas_por_mes.columns = ['Mês_Num', 'Quantidade']
                
                demandas_completas = pd.merge(todos_meses, demandas_por_mes, on='Mês_Num', how='left')
                demandas_completas['Quantidade'] = demandas_completas['Quantidade'].fillna(0).astype(int)
                
                fig_mes = go.Figure()
                
                fig_mes.add_trace(go.Scatter(
                    x=demandas_completas['Nome_Mês'],
                    y=demandas_completas['Quantidade'],
                    mode='lines+markers+text',
                    name='Demandas',
                    line=dict(color='#1e3799', width=3),
                    marker=dict(size=10, color='#0c2461'),
                    text=demandas_completas['Quantidade'],
                    textposition='top center',
                    textfont=dict(size=12, color='#1e3799')
                ))
                
                fig_mes.update_layout(
                    title=f"Demandas em {ano_selecionado}",
                    xaxis_title="Mês",
                    yaxis_title="Número de Demandas",
                    plot_bgcolor='white',
                    height=450,
                    showlegend=False
                )
                
                total_ano = int(demandas_completas['Quantidade'].sum())
                fig_mes.add_annotation(
                    x=0.5, y=0.95,
                    xref="paper", yref="paper",
                    text=f"Total no ano: {total_ano:,} demandas",
                    showarrow=False,
                    font=dict(size=12, color="#1e3799", weight="bold"),
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="#1e3799",
                    borderwidth=1,
                    borderpad=4
                )
                
                st.plotly_chart(fig_mes, use_container_width=True)
                
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                with col_stats1:
                    mes_max = demandas_completas.loc[demandas_completas['Quantidade'].idxmax()]
                    st.metric("📈 Mês com mais demandas", f"{mes_max['Nome_Mês']}: {int(mes_max['Quantidade']):,}")
                
                with col_stats2:
                    mes_min = demandas_completas.loc[demandas_completas['Quantidade'].idxmin()]
                    st.metric("📉 Mês com menos demandas", f"{mes_min['Nome_Mês']}: {int(mes_min['Quantidade']):,}")
                
                with col_stats3:
                    media_mensal = int(demandas_completas['Quantidade'].mean())
                    st.metric("📊 Média mensal", f"{media_mensal:,}")
            else:
                st.info(f"Não há dados para o ano {ano_selecionado}.")
    
    with tab2:
        st.markdown('<div class="section-title-exec">📊 REVISÕES POR RESPONSÁVEL</div>', unsafe_allow_html=True)
        
        if 'Revisões' in df.columns and 'Responsável_Formatado' in df.columns:
            df_com_revisoes = df[df['Revisões'] > 0].copy()
            
            if not df_com_revisoes.empty:
                revisoes_por_responsavel = df_com_revisoes.groupby('Responsável_Formatado').agg({
                    'Revisões': 'sum',
                    'Chamado': 'count'
                }).reset_index()
                
                revisoes_por_responsavel.columns = ['Responsável', 'Total_Revisões', 'Chamados_Com_Revisão']
                revisoes_por_responsavel = revisoes_por_responsavel.sort_values('Total_Revisões', ascending=False)
                
                fig_revisoes = go.Figure()
                
                fig_revisoes.add_trace(go.Bar(
                    x=revisoes_por_responsavel['Responsável'].head(15),
                    y=revisoes_por_responsavel['Total_Revisões'].head(15),
                    name='Total de Revisões',
                    text=revisoes_por_responsavel['Total_Revisões'].head(15),
                    textposition='outside',
                    marker_color='#e74c3c',
                    marker_line_color='#c0392b',
                    marker_line_width=1.5,
                    opacity=0.8
                ))
                
                fig_revisoes.update_layout(
                    title='Top 15 Responsáveis com Mais Revisões',
                    xaxis_title='Responsável',
                    yaxis_title='Total de Revisões',
                    plot_bgcolor='white',
                    height=500,
                    showlegend=False
                )
                
                st.plotly_chart(fig_revisoes, use_container_width=True)
            else:
                st.info("Não há dados de revisões.")
    
    with tab3:
        st.markdown('<div class="section-title-exec">📈 CHAMADOS SINCRONIZADOS POR DIA</div>', unsafe_allow_html=True)
        
        if 'Status' in df.columns and 'Criado' in df.columns:
            df_sincronizados = df[df['Status'] == 'Sincronizado'].copy()
            
            if not df_sincronizados.empty:
                df_sincronizados['Data'] = df_sincronizados['Criado'].dt.date
                
                sincronizados_por_dia = df_sincronizados.groupby('Data').size().reset_index()
                sincronizados_por_dia.columns = ['Data', 'Quantidade']
                sincronizados_por_dia = sincronizados_por_dia.sort_values('Data')
                
                fig_dia = go.Figure()
                
                fig_dia.add_trace(go.Scatter(
                    x=sincronizados_por_dia['Data'],
                    y=sincronizados_por_dia['Quantidade'],
                    mode='lines+markers',
                    name='Chamados Sincronizados',
                    line=dict(color='#28a745', width=3),
                    marker=dict(size=8, color='#218838'),
                    fill='tozeroy',
                    fillcolor='rgba(40, 167, 69, 0.2)'
                ))
                
                sincronizados_por_dia['Media_Movel'] = sincronizados_por_dia['Quantidade'].rolling(window=7, min_periods=1).mean()
                
                fig_dia.add_trace(go.Scatter(
                    x=sincronizados_por_dia['Data'],
                    y=sincronizados_por_dia['Media_Movel'],
                    mode='lines',
                    name='Média Móvel (7 dias)',
                    line=dict(color='#dc3545', width=2, dash='dash')
                ))
                
                fig_dia.update_layout(
                    title='Evolução Diária de Chamados Sincronizados',
                    xaxis_title='Data',
                    yaxis_title='Número de Chamados Sincronizados',
                    plot_bgcolor='white',
                    height=500,
                    showlegend=True
                )
                
                st.plotly_chart(fig_dia, use_container_width=True)
            else:
                st.info("Não há chamados sincronizados.")
    
    with tab4:
        st.markdown('<div class="section-title-exec">🏆 PERFORMANCE DOS SREs</div>', unsafe_allow_html=True)
        
        if 'SRE' in df.columns and 'Status' in df.columns:
            col_filtro1, col_filtro2 = st.columns(2)
            
            with col_filtro1:
                if 'Ano' in df.columns:
                    anos_sre = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_sre = ['Todos'] + list(anos_sre)
                    ano_sre = st.selectbox(
                        "📅 Filtrar por Ano:",
                        options=anos_opcoes_sre,
                        key="filtro_ano_sre"
                    )
            
            with col_filtro2:
                if 'Mês' in df.columns:
                    meses_sre = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_sre = ['Todos'] + [str(m) for m in meses_sre]
                    mes_sre = st.selectbox(
                        "📆 Filtrar por Mês:",
                        options=meses_opcoes_sre,
                        key="filtro_mes_sre"
                    )
            
            df_sre = df.copy()
            
            if 'Ano' in df_sre.columns and ano_sre != 'Todos':
                df_sre = df_sre[df_sre['Ano'] == int(ano_sre)]
            
            if 'Mês' in df_sre.columns and mes_sre != 'Todos':
                df_sre = df_sre[df_sre['Mês'] == int(mes_sre)]
            
            df_sincronizados = df_sre[df_sre['Status'] == 'Sincronizado'].copy()
            
            if not df_sincronizados.empty and 'SRE' in df_sincronizados.columns:
                sincronizacoes_por_sre = df_sincronizados['SRE'].value_counts().reset_index()
                sincronizacoes_por_sre.columns = ['SRE', 'Sincronizações']
                sincronizacoes_por_sre = sincronizacoes_por_sre.sort_values('Sincronizações', ascending=False)
                
                titulo_sinc = "Top 10 SREs com Mais Sincronizações"
                if ano_sre != 'Todos':
                    titulo_sinc += f" - {ano_sre}"
                if mes_sre != 'Todos':
                    titulo_sinc += f"/{mes_sre}"
                
                fig_sinc_sre = px.bar(
                    sincronizacoes_por_sre.head(10),
                    x='SRE',
                    y='Sincronizações',
                    title=titulo_sinc,
                    text='Sincronizações',
                    color='Sincronizações',
                    color_continuous_scale='Greens'
                )
                
                fig_sinc_sre.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    marker_line_color='#218838',
                    marker_line_width=1.5
                )
                
                fig_sinc_sre.update_layout(height=400, plot_bgcolor='white')
                st.plotly_chart(fig_sinc_sre, use_container_width=True)
                
                with st.expander("ℹ️ **Sobre a métrica de eficiência**", expanded=False):
                    st.markdown("""
                    #### 📈 **Como calculamos a eficiência do SRE:**
                    
                    **Fórmula:** 
                    ```
                    Eficiência = (Revisões / Sincronizações) × 100
                    ```
                    
                    **Interpretação:**
                    - **Eficiência ALTA** → SRE encontra muitos erros (faz muitas revisões por sincronização)
                    - **Eficiência BAIXA** → SRE encontra poucos erros (faz poucas revisões por sincronização)
                    
                    **Exemplo prático:**
                    - SRE A: 100 sincronizações, 25 revisões → Eficiência = 25%
                    - SRE B: 100 sincronizações, 10 revisões → Eficiência = 10%
                    - **SRE A é 2.5× mais eficiente** que SRE B!
                    """)
                
                col_comp1, col_comp2 = st.columns(2)
                
                with col_comp1:
                    performance_sre = pd.DataFrame()
                    performance_sre['SRE'] = sincronizacoes_por_sre['SRE']
                    performance_sre['Sincronizações'] = sincronizacoes_por_sre['Sincronizações']
                    
                    if 'Revisões' in df_sincronizados.columns:
                        revisoes_por_sre = df_sincronizados.groupby('SRE')['Revisões'].sum().reset_index()
                        revisoes_por_sre.columns = ['SRE', 'Revisões']
                        performance_sre = pd.merge(
                            performance_sre, 
                            revisoes_por_sre, 
                            on='SRE', 
                            how='left'
                        )
                        performance_sre['Revisões'] = performance_sre['Revisões'].fillna(0)
                    
                    if 'Revisões' in performance_sre.columns:
                        performance_sre['Eficiência'] = performance_sre.apply(
                            lambda x: (x['Revisões'] / x['Sincronizações'] * 100) 
                            if x['Sincronizações'] > 0 else 0,
                            axis=1
                        )
                        performance_sre['Eficiência'] = performance_sre['Eficiência'].round(2)
                    
                    performance_sre = performance_sre.sort_values('Eficiência', ascending=False)
                    display_performance = performance_sre.head(15).copy()
                    display_performance['Ranking'] = range(1, len(display_performance) + 1)
                    
                    st.dataframe(
                        display_performance[['Ranking', 'SRE', 'Sincronizações', 'Revisões', 'Eficiência']],
                        use_container_width=True,
                        height=400
                    )
            else:
                st.info("Não há dados de SREs sincronizados para os filtros selecionados.")
    
    # ============================================
    # TOP 10 RESPONSÁVEIS
    # ============================================
    st.markdown("---")
    col_top, col_dist = st.columns([2, 1])
    
    with col_top:
        st.markdown('<div class="section-title-exec">👥 TOP 10 RESPONSÁVEIS</div>', unsafe_allow_html=True)
        
        if 'Responsável_Formatado' in df.columns:
            top_responsaveis = df['Responsável_Formatado'].value_counts().head(10).reset_index()
            top_responsaveis.columns = ['Responsável', 'Demandas']
            
            if not top_responsaveis.empty:
                fig_top = px.bar(
                    top_responsaveis,
                    x='Demandas',
                    y='Responsável',
                    orientation='h',
                    text='Demandas',
                    color='Demandas',
                    color_continuous_scale='Blues'
                )
                
                fig_top.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    marker_line_color='#0c2461',
                    marker_line_width=1.5,
                    opacity=0.9
                )
                
                fig_top.update_layout(height=500, plot_bgcolor='white', showlegend=False)
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.info("Não há dados de responsáveis.")
    
    with col_dist:
        st.markdown('<div class="section-title-exec">📊 DISTRIBUIÇÃO POR TIPO</div>', unsafe_allow_html=True)
        
        if 'Tipo_Chamado' in df.columns:
            tipos_chamado = df['Tipo_Chamado'].value_counts().reset_index()
            tipos_chamado.columns = ['Tipo', 'Quantidade']
            tipos_chamado = tipos_chamado.sort_values('Quantidade', ascending=True)
            
            if not tipos_chamado.empty:
                fig_tipos = px.bar(
                    tipos_chamado,
                    x='Quantidade',
                    y='Tipo',
                    orientation='h',
                    text='Quantidade',
                    color='Quantidade',
                    color_continuous_scale='Viridis'
                )
                
                fig_tipos.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    marker_line_color='rgb(8,48,107)',
                    marker_line_width=1,
                    opacity=0.9
                )
                
                fig_tipos.update_layout(height=500, plot_bgcolor='white', showlegend=False)
                st.plotly_chart(fig_tipos, use_container_width=True)
            else:
                st.info("Não há dados de tipos de chamados.")
    
    # ============================================
    # ÚLTIMAS DEMANDAS
    # ============================================
    st.markdown("---")
    st.markdown('<div class="section-title_exec">🕒 ÚLTIMAS DEMANDAS REGISTRADAS</div>', unsafe_allow_html=True)
    
    if 'Criado' in df.columns:
        col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
        
        with col_filtro1:
            qtd_demandas = st.slider("Número de demandas:", 5, 50, 15, 5, key="slider_demandas")
        
        with col_filtro2:
            ordenar_por = st.selectbox(
                "Ordenar por:",
                ['Data (Mais Recente)', 'Data (Mais Antiga)', 'Revisões (Maior)', 'Revisões (Menor)'],
                key="select_ordenar"
            )
        
        with col_filtro3:
            mostrar_colunas = st.multiselect(
                "Colunas a mostrar:",
                ['Chamado', 'Tipo_Chamado', 'Responsável', 'Status', 'Prioridade', 'Revisões', 'Empresa', 'SRE', 'Data'],
                default=['Chamado', 'Tipo_Chamado', 'Responsável', 'Status', 'Data'],
                key="select_colunas"
            )
        
        with col_filtro4:
            filtro_chamado_tabela = st.text_input("Filtrar por chamado:", placeholder="Ex: 12345", key="input_filtro_chamado")
        
        ultimas_demandas = df.copy()
        
        if ordenar_por == 'Data (Mais Recente)':
            ultimas_demandas = ultimas_demandas.sort_values('Criado', ascending=False)
        elif ordenar_por == 'Data (Mais Antiga)':
            ultimas_demandas = ultimas_demandas.sort_values('Criado', ascending=True)
        elif ordenar_por == 'Revisões (Maior)':
            ultimas_demandas = ultimas_demandas.sort_values('Revisões', ascending=False)
        elif ordenar_por == 'Revisões (Menor)':
            ultimas_demandas = ultimas_demandas.sort_values('Revisões', ascending=True)
        
        if filtro_chamado_tabela:
            ultimas_demandas = ultimas_demandas[
                ultimas_demandas['Chamado'].astype(str).str.contains(filtro_chamado_tabela, na=False)
            ]
        
        ultimas_demandas = ultimas_demandas.head(qtd_demandas)
        
        display_data = pd.DataFrame()
        
        if 'Chamado' in mostrar_colunas and 'Chamado' in ultimas_demandas.columns:
            display_data['Chamado'] = ultimas_demandas['Chamado']
        
        if 'Tipo_Chamado' in mostrar_colunas and 'Tipo_Chamado' in ultimas_demandas.columns:
            display_data['Tipo'] = ultimas_demandas['Tipo_Chamado']
        
        if 'Responsável' in mostrar_colunas and 'Responsável_Formatado' in ultimas_demandas.columns:
            display_data['Responsável'] = ultimas_demandas['Responsável_Formatado']
        
        if 'Status' in mostrar_colunas and 'Status' in ultimas_demandas.columns:
            display_data['Status'] = ultimas_demandas['Status']
        
        if 'Prioridade' in mostrar_colunas and 'Prioridade' in ultimas_demandas.columns:
            display_data['Prioridade'] = ultimas_demandas['Prioridade']
        
        if 'Revisões' in mostrar_colunas and 'Revisões' in ultimas_demandas.columns:
            display_data['Revisões'] = ultimas_demandas['Revisões']
        
        if 'Empresa' in mostrar_colunas and 'Empresa' in ultimas_demandas.columns:
            display_data['Empresa'] = ultimas_demandas['Empresa']
        
        if 'SRE' in mostrar_colunas and 'SRE' in ultimas_demandas.columns:
            display_data['SRE'] = ultimas_demandas['SRE']
        
        if 'Data' in mostrar_colunas and 'Criado' in ultimas_demandas.columns:
            display_data['Data Criação'] = ultimas_demandas['Criado'].dt.strftime('%d/%m/%Y %H:%M')
        
        if not display_data.empty:
            st.dataframe(display_data, use_container_width=True, height=400)
            
            csv = display_data.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Exportar esta tabela",
                data=csv,
                file_name=f"ultimas_demandas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_exportar"
            )
        else:
            st.info("Nenhum dado para exibir com os filtros atuais.")

else:
    # TELA INICIAL
    st.markdown("""
    <div style="text-align: center; padding: 4rem; background: #f8f9fa; border-radius: 10px; border: 2px dashed #dee2e6;">
        <h3 style="color: #495057;">📊 Esteira ADMS Dashboard</h3>
        <p style="color: #6c757d; margin-bottom: 2rem;">
            Sistema de análise e monitoramento de chamados - Setor SRE
        </p>
        <div style="margin-top: 2rem; padding: 2rem; background: white; border-radius: 8px; display: inline-block;">
            <h4 style="color: #1e3799;">📋 Para começar:</h4>
            <p>1. <strong>Use a barra lateral esquerda</strong> para fazer upload do arquivo CSV</p>
            <p>2. <strong>Use a seção "Importar Dados"</strong> no final da barra lateral</p>
            <p>3. <strong>Ou coloque um arquivo CSV</strong> no mesmo diretório do app</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")

ultima_atualizacao = st.session_state.get('ultima_atualizacao', get_horario_brasilia())

st.markdown(f"""
<div class="footer-exec">
    <div style="margin-bottom: 1rem;">
        <p style="margin: 0; color: #495057; font-weight: 600;">
        Desenvolvido por: <span style="color: #1e3799;">Kewin Marcel Ramirez Ferreira | GEAT</span>
        </p>
        <p style="margin: 0.3rem 0 0 0; color: #6c757d; font-size: 0.85rem;">
        📧 Contato: <a href="mailto:kewin.ferreira@energisa.com.br" style="color: #1e3799; text-decoration: none;">kewin.ferreira@energisa.com.br</a>
        </p>
    </div>
    <div style="margin-top: 0.5rem;">
        <p style="margin: 0; color: #6c757d; font-size: 0.8rem;">
        © 2024 Esteira ADMS Dashboard | Sistema proprietário - Energisa Group
        </p>
        <p style="margin: 0.2rem 0 0 0; color: #adb5bd; font-size: 0.75rem;">
        Versão 5.6 | Sistema Avançado de Análise | Última atualização: {ultima_atualizacao} (Brasília)
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
