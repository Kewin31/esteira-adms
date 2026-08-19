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
import streamlit.components.v1 as components
warnings.filterwarnings('ignore')

# ============================================
# PALETA DE CORES - NOVA IDENTIDADE VISUAL
# ============================================
COR_VERDE_ESCURO = "#2E7D32"
COR_AZUL_PETROLEO = "#028a9f"
COR_AZUL_ESCURO = "#005973"
COR_LARANJA = "#F57C00"
COR_VERMELHO = "#C62828"
COR_CINZA_FUNDO = "#F8F9FA"
COR_CINZA_BORDA = "#E9ECEF"
COR_CINZA_TEXTO = "#6C757D"
COR_BRANCO = "#FFFFFF"
COR_PRETO_SUAVE = "#212529"

# ============================================
# MAPEAMENTO COMPLETO DAS EMPRESAS
# ============================================
MAPEAMENTO_EMPRESAS = {
    'EMR': {
        'sigla': 'MG',
        'estado': 'Minas Gerais',
        'regiao': 'Sudeste',
        'nome_completo': 'Energisa Minas Gerais',
        'latitude': -19.9167,
        'longitude': -43.9345
    },
    'EPB': {
        'sigla': 'PB',
        'estado': 'Paraíba',
        'regiao': 'Nordeste',
        'nome_completo': 'Energisa Paraíba',
        'latitude': -7.1195,
        'longitude': -36.7240
    },
    'ESE': {
        'sigla': 'SE',
        'estado': 'Sergipe',
        'regiao': 'Nordeste',
        'nome_completo': 'Energisa Sergipe',
        'latitude': -10.9472,
        'longitude': -37.0731
    },
    'ESS': {
        'sigla': 'SP',
        'estado': 'São Paulo',
        'regiao': 'Sudeste',
        'nome_completo': 'Energisa Sul/Sudeste',
        'latitude': -23.5505,
        'longitude': -46.6333
    },
    'EMS': {
        'sigla': 'MS',
        'estado': 'Mato Grosso do Sul',
        'regiao': 'Centro-Oeste',
        'nome_completo': 'Energisa Mato Grosso do Sul',
        'latitude': -20.4697,
        'longitude': -54.6201
    },
    'EMT': {
        'sigla': 'MT',
        'estado': 'Mato Grosso',
        'regiao': 'Centro-Oeste',
        'nome_completo': 'Energisa Mato Grosso',
        'latitude': -12.6819,
        'longitude': -56.9211
    },
    'ETO': {
        'sigla': 'TO',
        'estado': 'Tocantins',
        'regiao': 'Norte',
        'nome_completo': 'Energisa Tocantins',
        'latitude': -10.1753,
        'longitude': -48.2982
    },
    'ERO': {
        'sigla': 'RO',
        'estado': 'Rondônia',
        'regiao': 'Norte',
        'nome_completo': 'Energisa Rondônia',
        'latitude': -10.9161,
        'longitude': -61.8298
    },
    'EAC': {
        'sigla': 'AC',
        'estado': 'Acre',
        'regiao': 'Norte',
        'nome_completo': 'Energisa Acre',
        'latitude': -9.0238,
        'longitude': -70.8120
    }
}

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
# FUNÇÕES DE GERENCIAMENTO DE ARQUIVO - CORRIGIDAS E MELHORADAS
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
            ' Da ': ' da ',
            ' De ': ' de ',
            ' Do ': ' do ',
            ' Das ': ' das ',
            ' Dos ': ' dos ',
            ' E ': ' e ',
        }
        
        for errado, correto in correcoes.items():
            nome_formatado = nome_formatado.replace(errado, correto)
        
        return nome_formatado
    
    return nome_str.title()

def calcular_hash_arquivo(conteudo):
    """Calcula hash do conteúdo do arquivo para detectar mudanças"""
    return hashlib.md5(conteudo).hexdigest()

def encontrar_arquivo_dados():
    """Tenta encontrar o arquivo de dados em vários caminhos possíveis"""
    # Verifica caminhos principais
    for caminho in [CAMINHO_ARQUIVO_PRINCIPAL] + CAMINHOS_ALTERNATIVOS:
        if caminho and os.path.exists(caminho):
            return caminho
    
    # Verifica por arquivos CSV no diretório atual
    try:
        for arquivo in os.listdir('.'):
            if arquivo.lower().endswith('.csv') and ('esteira' in arquivo.lower() or 'demanda' in arquivo.lower()):
                return arquivo
    except:
        pass
    
    return None

@st.cache_data(ttl=120)  # Cache de 120 segundos para melhor performance
def carregar_dados_com_cache(caminho_arquivo=None, uploaded_file=None):
    """Carrega dados com cache para melhor performance"""
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
        
        # Limpa e processa o CSV
        lines = conteudo.split('\n')
        
        # Encontra o cabeçalho
        header_line = None
        for i, line in enumerate(lines):
            if '"Chamado"' in line and '"Tipo Chamado"' in line:
                header_line = i
                break
        
        if header_line is None:
            # Tenta encontrar qualquer linha com "Chamado"
            for i, line in enumerate(lines):
                if 'Chamado' in line and ('Tipo' in line or 'Responsável' in line):
                    header_line = i
                    break
        
        if header_line is None:
            return None, "Formato de arquivo inválido - Cabeçalho não encontrado", None
        
        data_str = '\n'.join(lines[header_line:])
        df = pd.read_csv(io.StringIO(data_str), quotechar='"')
        
        # Mapeamento de colunas
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
            'Revisões': 'Revisões',
            'Motivo Revisão': 'Motivo_Revisao',
            'Retorno Cliente': 'Retorno_Cliente'
        }
        
        df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})
        
        # Formata nomes
        if 'Responsável' in df.columns:
            df['Responsável_Formatado'] = df['Responsável'].apply(formatar_nome_responsavel)
        
        # Processa datas
        date_columns = ['Criado', 'Modificado']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Cria colunas de data
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
        
        # Processa revisões
        if 'Revisões' in df.columns:
            df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
        
        # Remove linhas completamente vazias
        df = df.dropna(how='all')
        
        hash_conteudo = calcular_hash_arquivo(conteudo_bytes)
        
        return df, f"✅ Dados carregados com sucesso! {len(df):,} registros", hash_conteudo
    
    except Exception as e:
        return None, f"❌ Erro ao carregar dados: {str(e)}", None

def verificar_mudanca_arquivo():
    """Verifica se o arquivo foi modificado e recarrega automaticamente"""
    if 'df_original' not in st.session_state or st.session_state.df_original is None:
        return False
    
    caminho = encontrar_arquivo_dados()
    if not caminho or not os.path.exists(caminho):
        return False
    
    # Verifica modificação
    mod_atual = os.path.getmtime(caminho)
    
    if 'ultima_modificacao' not in st.session_state:
        st.session_state.ultima_modificacao = mod_atual
        return False
    
    if mod_atual > st.session_state.ultima_modificacao:
        st.session_state.ultima_modificacao = mod_atual
        
        # Verifica se o hash também mudou
        with open(caminho, 'rb') as f:
            conteudo_atual = f.read()
        hash_atual = calcular_hash_arquivo(conteudo_atual)
        
        if 'file_hash' not in st.session_state or hash_atual != st.session_state.file_hash:
            return True
    
    return False

def recarregar_dados():
    """Função principal para recarregar dados"""
    try:
        caminho_atual = encontrar_arquivo_dados()
        
        if caminho_atual and os.path.exists(caminho_atual):
            # Limpa o cache
            st.cache_data.clear()
            
            # Carrega os dados
            df_atualizado, status, hash_conteudo = carregar_dados_com_cache(
                caminho_arquivo=caminho_atual
            )
            
            if df_atualizado is not None:
                st.session_state.df_original = df_atualizado
                st.session_state.df_filtrado = df_atualizado.copy()
                st.session_state.arquivo_atual = caminho_atual
                st.session_state.file_hash = hash_conteudo
                st.session_state.ultima_atualizacao = get_horario_brasilia()
                st.session_state.ultima_modificacao = os.path.getmtime(caminho_atual)
                st.session_state.dados_carregados = True
                return True, f"✅ Dados atualizados! {len(df_atualizado):,} registros"
            else:
                return False, f"❌ Erro ao recarregar: {status}"
        else:
            return False, "❌ Arquivo local não encontrado."
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"

def get_horario_brasilia():
    """Retorna o horário atual de Brasília"""
    try:
        tz = timezone('America/Sao_Paulo')
        return datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    except:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

# ============================================
# FUNÇÕES DO DASHBOARD (MANTIDAS)
# ============================================

def criar_card_indicador_simples(valor, label, icone="📊"):
    """Cria card de indicador SIMPLES - sem delta"""
    if isinstance(valor, (int, float)):
        valor_formatado = f"{valor:,}"
    else:
        valor_formatado = str(valor)
    
    return f'''
    <div class="metric-card">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 1.8rem;">{icone}</span>
            <div>
                <div class="metric-value">{valor_formatado}</div>
                <div class="metric-label">{label}</div>
            </div>
        </div>
    </div>
    '''

def is_retorno_sim(valor):
    """Verifica se o valor indica retorno do cliente (Sim)"""
    if pd.isna(valor):
        return False
    valor_str = str(valor).strip().upper()
    return valor_str in ['SIM', 'S', 'YES', 'Y', '1', 'TRUE']

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown(f"""
<style>
    /* Reset e estilos base */
    .stApp {{
        background-color: {COR_CINZA_FUNDO};
    }}
    
    /* Main header */
    .main-header-monitoring {{
        background: {COR_CINZA_FUNDO};
        padding: 1.2rem 2rem;
        margin-bottom: 1.5rem;
        border-bottom: 4px solid {COR_AZUL_ESCURO};
        border-radius: 0;
    }}
    
    /* Cards de métricas */
    .metric-card {{
        background: {COR_BRANCO};
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid {COR_CINZA_BORDA};
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 89, 115, 0.1);
        border-color: {COR_AZUL_PETROLEO};
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {COR_AZUL_ESCURO};
        margin: 0;
        line-height: 1.2;
    }}
    
    .metric-label {{
        font-size: 0.85rem;
        color: {COR_CINZA_TEXTO};
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }}
    
    .section-title {{
        color: {COR_AZUL_ESCURO};
        border-left: 4px solid {COR_VERDE_ESCURO};
        padding-left: 1rem;
        margin-bottom: 1.5rem;
        font-size: 1.2rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {COR_BRANCO};
        border-right: 1px solid {COR_CINZA_BORDA};
    }}
    
    .sidebar-section {{
        background: {COR_CINZA_FUNDO};
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid {COR_CINZA_BORDA};
    }}
    
    .info-base {{
        background: {COR_CINZA_FUNDO};
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {COR_VERDE_ESCURO};
        margin-bottom: 1.5rem;
    }}
    
    .status-success {{
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        border-left: 4px solid {COR_VERDE_ESCURO};
        padding: 0.75rem;
        border-radius: 8px;
    }}
    
    .status-warning {{
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
        border-left: 4px solid {COR_LARANJA};
        padding: 0.75rem;
        border-radius: 8px;
    }}
    
    .status-danger {{
        background: linear-gradient(135deg, #FFEBEE, #FFCDD2);
        border-left: 4px solid {COR_VERMELHO};
        padding: 0.75rem;
        border-radius: 8px;
    }}
    
    .footer {{
        text-align: center;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 2px solid {COR_CINZA_BORDA};
        color: {COR_CINZA_TEXTO};
        font-size: 0.85rem;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# DETECÇÃO AUTOMÁTICA DE MUDANÇAS NO ARQUIVO
# ============================================
if verificar_mudanca_arquivo():
    with st.spinner("🔄 Detectada mudança no arquivo. Recarregando..."):
        st.cache_data.clear()
        caminho = encontrar_arquivo_dados()
        if caminho and os.path.exists(caminho):
            df, status, hash_conteudo = carregar_dados_com_cache(caminho_arquivo=caminho)
            if df is not None:
                st.session_state.df_original = df
                st.session_state.df_filtrado = df.copy()
                st.session_state.file_hash = hash_conteudo
                st.session_state.ultima_atualizacao = get_horario_brasilia()
                st.session_state.dados_carregados = True
                st.success("✅ Dados recarregados automaticamente!")
                time.sleep(0.5)
                st.rerun()

# ============================================
# SIDEBAR - FILTROS E CONTROLES
# ============================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <h3 style="color: {COR_AZUL_ESCURO}; margin: 0;">⚙️ Painel de Controle</h3>
        <p style="color: {COR_CINZA_TEXTO}; margin: 0; font-size: 0.85rem;">Filtros e Configurações</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============================================
    # SEÇÃO DE UPLOAD E GERENCIAMENTO DE DADOS
    # ============================================
    
    # Inicializa variáveis de sessão se não existirem
    if 'df_original' not in st.session_state:
        st.session_state.df_original = None
        st.session_state.df_filtrado = None
        st.session_state.arquivo_atual = None
        st.session_state.file_hash = None
        st.session_state.uploaded_file_name = None
        st.session_state.ultima_atualizacao = None
        st.session_state.dados_carregados = False
        st.session_state.cache_limpo = False
    
    # Tenta carregar arquivo local automaticamente
    if st.session_state.df_original is None:
        caminho_encontrado = encontrar_arquivo_dados()
        
        if caminho_encontrado:
            with st.spinner('📂 Carregando dados locais...'):
                df_local, status, hash_conteudo = carregar_dados_com_cache(caminho_arquivo=caminho_encontrado)
                if df_local is not None:
                    st.session_state.df_original = df_local
                    st.session_state.df_filtrado = df_local.copy()
                    st.session_state.arquivo_atual = caminho_encontrado
                    st.session_state.file_hash = hash_conteudo
                    st.session_state.ultima_atualizacao = get_horario_brasilia()
                    st.session_state.dados_carregados = True
                    if os.path.exists(caminho_encontrado):
                        st.session_state.ultima_modificacao = os.path.getmtime(caminho_encontrado)
    
    # Exibe status dos dados
    if st.session_state.df_original is not None:
        st.markdown(f"""
        <div style="background: {COR_CINZA_FUNDO}; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0 0 0.3rem 0; font-weight: 600; color: {COR_VERDE_ESCURO};">
                ✅ Dados Carregados
            </p>
            <p style="margin: 0; font-size: 0.85rem; color: {COR_PRETO_SUAVE};">
                📊 {len(st.session_state.df_original):,} registros
            </p>
            <p style="margin: 0.3rem 0 0 0; font-size: 0.75rem; color: {COR_CINZA_TEXTO};">
                🕐 {st.session_state.get('ultima_atualizacao', 'N/A')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Informações do arquivo
        arquivo_atual = st.session_state.get('arquivo_atual')
        if arquivo_atual and isinstance(arquivo_atual, str) and os.path.exists(arquivo_atual):
            tamanho_kb = os.path.getsize(arquivo_atual) / 1024
            ultima_mod = datetime.fromtimestamp(os.path.getmtime(arquivo_atual))
            
            st.markdown(f"""
            <div style="background: {COR_CINZA_FUNDO}; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="margin: 0; font-size: 0.8rem; color: {COR_CINZA_TEXTO};">
                    📄 {os.path.basename(arquivo_atual)}
                </p>
                <p style="margin: 0.2rem 0 0 0; font-size: 0.7rem; color: {COR_CINZA_TEXTO};">
                    📏 {tamanho_kb:.1f} KB | 📅 {ultima_mod.strftime('%d/%m/%Y %H:%M')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Botões de controle
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("🔄 Recarregar", 
                       use_container_width=True,
                       type="primary",
                       help="Recarrega os dados do arquivo local",
                       key="btn_recarregar"):
                with st.spinner('🔄 Recarregando dados...'):
                    sucesso, mensagem = recarregar_dados()
                    if sucesso:
                        st.success(mensagem)
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(mensagem)
        
        with col_btn2:
            if st.button("🧹 Limpar Cache", 
                       use_container_width=True,
                       help="Limpa o cache do Streamlit",
                       key="btn_limpar_cache"):
                st.cache_data.clear()
                st.session_state.cache_limpo = True
                st.success("✅ Cache limpo com sucesso!")
                time.sleep(0.5)
                st.rerun()
        
        with col_btn3:
            if st.button("🗑️ Reset", 
                       use_container_width=True,
                       help="Reseta todos os dados e recarrega",
                       key="btn_reset"):
                st.cache_data.clear()
                for key in ['df_original', 'df_filtrado', 'file_hash', 'dados_carregados']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("✅ Dados resetados!")
                time.sleep(0.5)
                st.rerun()
        
        st.markdown("---")
    
    # ============================================
    # SEÇÃO DE UPLOAD DE ARQUIVO
    # ============================================
    with st.container():
        st.markdown("**📤 Importar Dados**")
        
        uploaded_file = st.file_uploader(
            "Selecione um arquivo CSV",
            type=['csv'],
            key="file_uploader",
            help="Faça upload de um novo arquivo CSV para substituir os dados atuais",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            st.markdown(f"""
            <div style="background: {COR_CINZA_FUNDO}; padding: 0.5rem; border-radius: 5px; margin: 0.5rem 0;">
                <p style="margin: 0; font-size: 0.85rem;">
                    📄 <strong>{uploaded_file.name}</strong>
                </p>
                <p style="margin: 0; font-size: 0.75rem; color: {COR_CINZA_TEXTO};">
                    📏 {uploaded_file.size / 1024:.1f} KB
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📥 Processar Arquivo", 
                       use_container_width=True, 
                       type="primary", 
                       key="btn_processar"):
                with st.spinner('📥 Processando arquivo...'):
                    df_novo, status, hash_conteudo = carregar_dados_com_cache(
                        uploaded_file=uploaded_file
                    )
                    
                    if df_novo is not None:
                        st.session_state.df_original = df_novo
                        st.session_state.df_filtrado = df_novo.copy()
                        st.session_state.arquivo_atual = uploaded_file.name
                        st.session_state.file_hash = hash_conteudo
                        st.session_state.uploaded_file_name = uploaded_file.name
                        st.session_state.ultima_atualizacao = get_horario_brasilia()
                        st.session_state.dados_carregados = True
                        
                        st.success(f"✅ {len(df_novo):,} registros carregados!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"❌ {status}")
    
    # ============================================
    # FILTROS DE ANÁLISE (se dados carregados)
    # ============================================
    if st.session_state.df_original is not None:
        st.markdown("---")
        st.markdown("**🔍 Filtros de Análise**")
        
        df = st.session_state.df_original.copy()
        
        # Filtro de Ano
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
        
        # Filtro de Mês
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
        
        # Filtro de Responsável
        if 'Responsável_Formatado' in df.columns:
            responsaveis = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
            responsavel_selecionado = st.selectbox(
                "👤 Responsável",
                options=responsaveis,
                key="filtro_responsavel"
            )
            if responsavel_selecionado != 'Todos':
                df = df[df['Responsável_Formatado'] == responsavel_selecionado]
        
        # Busca por chamado
        busca_chamado = st.text_input(
            "🔎 Buscar Chamado",
            placeholder="Digite número do chamado...",
            key="busca_chamado"
        )
        if busca_chamado:
            df = df[df['Chamado'].astype(str).str.contains(busca_chamado, na=False)]
        
        # Filtro de Status
        if 'Status' in df.columns:
            status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
            status_selecionado = st.selectbox(
                "📊 Status",
                options=status_opcoes,
                key="filtro_status"
            )
            if status_selecionado != 'Todos':
                df = df[df['Status'] == status_selecionado]
        
        # Filtro de Tipo
        if 'Tipo_Chamado' in df.columns:
            tipos = ['Todos'] + sorted(df['Tipo_Chamado'].dropna().unique())
            tipo_selecionado = st.selectbox(
                "📝 Tipo de Chamado",
                options=tipos,
                key="filtro_tipo"
            )
            if tipo_selecionado != 'Todos':
                df = df[df['Tipo_Chamado'] == tipo_selecionado]
        
        # Filtro de Empresa
        if 'Empresa' in df.columns:
            empresas = ['Todas'] + sorted(df['Empresa'].dropna().unique())
            empresa_selecionada = st.selectbox(
                "🏢 Empresa",
                options=empresas,
                key="filtro_empresa"
            )
            if empresa_selecionada != 'Todas':
                df = df[df['Empresa'] == empresa_selecionada]
        
        # Filtro de SRE
        if 'SRE' in df.columns:
            sres = ['Todos'] + sorted(df['SRE'].dropna().unique())
            sre_selecionado = st.selectbox(
                "🔧 SRE Responsável",
                options=sres,
                key="filtro_sre"
            )
            if sre_selecionado != 'Todos':
                df = df[df['SRE'] == sre_selecionado]
        
        # Atualiza dados filtrados
        st.session_state.df_filtrado = df
        
        st.markdown(f"""
        <div style="background: {COR_CINZA_FUNDO}; padding: 0.5rem; border-radius: 5px; margin-top: 0.5rem;">
            <p style="margin: 0; font-size: 0.85rem;">
                📊 <strong>Registros filtrados:</strong> {len(df):,}
            </p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# HEADER PRINCIPAL
# ============================================
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {COR_AZUL_PETROLEO} 0%, {COR_AZUL_ESCURO} 100%);
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    border-radius: 0;
    box-shadow: 0 4px 15px rgba(2, 138, 159, 0.3);
">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
        <div>
            <h1 style="
                color: {COR_BRANCO};
                margin: 0;
                font-size: 1.6rem;
                font-weight: 600;
                letter-spacing: -0.3px;
                text-shadow: 0 1px 2px rgba(0,0,0,0.1);
            ">
                📊 ESTEIRA SRE (Site Reliability Engineering)
            </h1>
            <p style="
                color: rgba(255,255,255,0.9);
                margin: 0.3rem 0 0 0;
                font-size: 0.85rem;
                font-weight: 400;
            ">
                Acompanhamento das validações da EAC | EMR | EMS | EMT | EPB | ERO | ESE | ESS | ETO
            </p>
        </div>
        <div style="text-align: right;">
            <p style="
                color: rgba(255,255,255,0.9);
                margin: 0;
                font-size: 0.85rem;
                font-weight: 500;
            ">
                Dashboard de Performance
            </p>
            <p style="
                color: rgba(255,255,255,0.8);
                margin: 0.2rem 0 0 0;
                font-size: 0.75rem;
            ">
                v5.5 | Sistema de Performance SRE
            </p>
            <p style="
                color: rgba(255,255,255,0.7);
                margin: 0.3rem 0 0 0;
                font-size: 0.7rem;
                font-weight: 500;
            ">
                {datetime.now().strftime('%d/%m/%Y')}
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
    # INDICADORES PRINCIPAIS
    # ============================================
    st.markdown("## 📈 INDICADORES PRINCIPAIS")
    
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    with col4:
        if 'Empresa' in df.columns:
            total_empresas = df['Empresa'].nunique()
            st.markdown(criar_card_indicador_simples(
                total_empresas,
                "Empresas Ativas",
                "🏢"
            ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============================================
    # TABS PRINCIPAIS
    # ============================================
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "📈 Análise de Revisões", "🗺️ Mapa"])
    
    with tab1:
        st.markdown(f'<div class="section-title">📊 VISÃO GERAL</div>', unsafe_allow_html=True)
        
        # Gráfico de evolução mensal
        if 'Criado' in df.columns and not df.empty:
            st.markdown("### 📅 Evolução Mensal de Demandas")
            
            df_ano_atual = df[df['Ano'] == df['Ano'].max()].copy() if 'Ano' in df.columns else df
            
            if not df_ano_atual.empty and 'Nome_Mês' in df_ano_atual.columns:
                demandas_por_mes = df_ano_atual.groupby('Nome_Mês').size().reset_index()
                demandas_por_mes.columns = ['Mês', 'Quantidade']
                
                # Ordenar meses
                ordem_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                              'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                demandas_por_mes['Mês_Ordenado'] = demandas_por_mes['Mês'].apply(
                    lambda x: ordem_meses.index(x) if x in ordem_meses else 99
                )
                demandas_por_mes = demandas_por_mes.sort_values('Mês_Ordenado')
                
                fig_mensal = go.Figure()
                fig_mensal.add_trace(go.Bar(
                    x=demandas_por_mes['Mês'],
                    y=demandas_por_mes['Quantidade'],
                    text=demandas_por_mes['Quantidade'],
                    textposition='outside',
                    marker_color=COR_AZUL_ESCURO,
                    marker_line_color=COR_AZUL_PETROLEO,
                    marker_line_width=1.5,
                    opacity=0.8
                ))
                
                fig_mensal.update_layout(
                    title=f'Evolução Mensal - {df_ano_atual["Ano"].iloc[0] if "Ano" in df_ano_atual.columns else "Ano Atual"}',
                    xaxis_title='Mês',
                    yaxis_title='Quantidade de Demandas',
                    height=400,
                    plot_bgcolor=COR_BRANCO,
                    showlegend=False,
                    margin=dict(t=50, b=50, l=50, r=50),
                    xaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
                    yaxis=dict(gridcolor='rgba(0,0,0,0.05)', rangemode='tozero')
                )
                
                st.plotly_chart(fig_mensal, use_container_width=True)
                
                # Estatísticas rápidas
                col_est1, col_est2, col_est3 = st.columns(3)
                with col_est1:
                    mes_max = demandas_por_mes.loc[demandas_por_mes['Quantidade'].idxmax()]
                    st.metric("📈 Mês com mais demandas", f"{mes_max['Mês']}: {int(mes_max['Quantidade'])}")
                with col_est2:
                    mes_min = demandas_por_mes.loc[demandas_por_mes['Quantidade'].idxmin()]
                    st.metric("📉 Mês com menos demandas", f"{mes_min['Mês']}: {int(mes_min['Quantidade'])}")
                with col_est3:
                    media_mensal = int(demandas_por_mes['Quantidade'].mean())
                    st.metric("📊 Média mensal", f"{media_mensal}")
    
    with tab2:
        st.markdown(f'<div class="section-title">📈 ANÁLISE DE REVISÕES</div>', unsafe_allow_html=True)
        
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
                    text=revisoes_por_responsavel['Total_Revisões'].head(15),
                    textposition='outside',
                    marker_color=COR_AZUL_ESCURO,
                    marker_line_color=COR_AZUL_PETROLEO,
                    marker_line_width=1.5,
                    opacity=0.8
                ))
                
                fig_revisoes.update_layout(
                    title='Top 15 Responsáveis com Mais Revisões',
                    xaxis_title='Responsável',
                    yaxis_title='Total de Revisões',
                    height=500,
                    plot_bgcolor=COR_BRANCO,
                    showlegend=False,
                    margin=dict(t=50, b=100, l=50, r=50),
                    xaxis=dict(tickangle=45, gridcolor='rgba(0,0,0,0.05)'),
                    yaxis=dict(gridcolor='rgba(0,0,0,0.05)')
                )
                
                st.plotly_chart(fig_revisoes, use_container_width=True)
            else:
                st.info("ℹ️ Nenhuma revisão encontrada nos dados.")
    
    with tab3:
        st.markdown(f'<div class="section-title">🗺️ MAPA DE SINCRONIZAÇÕES</div>', unsafe_allow_html=True)
        st.info("🗺️ Mapa interativo - em desenvolvimento")

else:
    st.markdown(f"""
    <div style="text-align: center; padding: 4rem; background: {COR_CINZA_FUNDO}; border-radius: 12px; border: 2px dashed {COR_CINZA_BORDA};">
        <h3 style="color: {COR_PRETO_SUAVE};">📊 Esteira ADMS Dashboard</h3>
        <p style="color: {COR_CINZA_TEXTO}; margin-bottom: 2rem;">
            Sistema de análise e monitoramento de chamados - Setor SRE
        </p>
        <div style="margin-top: 2rem; padding: 2rem; background: {COR_BRANCO}; border-radius: 8px; display: inline-block;">
            <h4 style="color: {COR_AZUL_ESCURO};">📋 Para começar:</h4>
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
<div class="footer">
    <div style="margin-bottom: 0.8rem;">
        <p style="margin: 0; color: {COR_PRETO_SUAVE}; font-weight: 500;">
        Desenvolvido por: <span style="color: {COR_AZUL_ESCURO};">Kewin Marcel Ramirez Ferreira | GEAT</span>
        </p>
        <p style="margin: 0.3rem 0 0 0; color: {COR_CINZA_TEXTO}; font-size: 0.8rem;">
        📧 Contato: <a href="mailto:kewin.ferreira@energisa.com.br" style="color: {COR_AZUL_ESCURO}; text-decoration: none;">kewin.ferreira@energisa.com.br</a>
        </p>
    </div>
    <div>
        <p style="margin: 0; color: {COR_CINZA_TEXTO}; font-size: 0.75rem;">
        © 2024 Esteira ADMS Dashboard | Sistema proprietário - Energisa Group
        </p>
        <p style="margin: 0.2rem 0 0 0; color: {COR_CINZA_TEXTO}; font-size: 0.7rem;">
        Versão 5.5 | Sistema de Performance SRE | Última atualização: {ultima_atualizacao} (Brasília)
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
