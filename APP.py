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
import gc  # NOVO: Para coleta de lixo
import re  # NOVO: Para regex pré-compilado
import logging  # NOVO: Para logging
from typing import Optional, Tuple, Dict, List, Any, Union  # NOVO: Type hints
import signal  # NOVO: Para timeout

# ============================================
# CONFIGURAÇÃO INICIAL OTIMIZADA
# ============================================

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Melhor tratamento de warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.simplefilter('always', category=UserWarning)

# ============================================
# CONSTANTES E CONFIGURAÇÕES (OTIMIZADAS)
# ============================================

# CONFIGURE AQUI O CAMINHO DO SEU ARQUIVO
CAMINHO_ARQUIVO_PRINCIPAL = "esteira_demandas.csv"
CAMINHOS_ALTERNATIVOS = [
    "data/esteira_demandas.csv",
    "dados/esteira_demandas.csv",
    "database/esteira_demandas.csv",
    "base_dados.csv",
    "dados.csv"
]

# NOVO: Configurações de performance
MAX_ENTRIES_CACHE = 5
CACHE_TTL = 300  # 5 minutos
MAX_FILE_SIZE_MB = 100
TIMEOUT_SECONDS = 30

# NOVO: Timezone cacheado
TZ_BRASIL = timezone('America/Sao_Paulo')

# NOVO: Mapeamento de meses (cacheado)
MESES_ABREVIADOS = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}

MESES_COMPLETOS = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

# NOVO: Ordem dos meses
ORDEM_MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
               'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

# NOVO: Dias da semana
DIAS_SEMANA_ING = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
DIAS_SEMANA_PT = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
DIAS_MAPPING = dict(zip(DIAS_SEMANA_ING, DIAS_SEMANA_PT))

# NOVO: Colunas obrigatórias
COLUNAS_OBRIGATORIAS = ['Chamado', 'Tipo_Chamado', 'Status', 'Criado']

# NOVO: Regex pré-compilado
REGEX_EMAIL = re.compile(r'@')
REGEX_SEPARADORES = re.compile(r'[._-]')
REGEX_DIGITOS = re.compile(r'\d+')
REGEX_CONECTIVOS = re.compile(r'\b(Da|De|Do|Das|Dos|E)\b', re.IGNORECASE)

# NOVO: Mapeamento de tipos de dados para otimização
DTYPE_OPTIMIZATION = {
    'Chamado': 'str',
    'Revisões': 'Int32',
    'Prioridade': 'category',
    'Status': 'category',
    'Tipo Chamado': 'category',
    'Tipo_Chamado': 'category',
    'Empresa': 'category',
    'SRE': 'category',
    'Responsável': 'str',
    'Modificado por': 'str',
    'Sincronização': 'str'
}

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
# CSS PERSONALIZADO OTIMIZADO
# ============================================
st.markdown("""
<style>
    /* Estilos gerais consolidados */
    .main-header {
        background: linear-gradient(135deg, #0c2461 0%, #1e3799 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .card-base {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        background: white;
    }
    
    .card-base:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    
    .metric-card-exec {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e9ecef;
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
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .sidebar-section {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid #dee2e6;
    }
    
    /* Cards de status */
    .performance-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fff9 100%);
        border-left: 4px solid #28a745;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ffffff 0%, #fff8f8 100%);
        border-left: 4px solid #dc3545;
    }
    
    .info-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fcff 100%);
        border-left: 4px solid #17a2b8;
    }
    
    .info-base {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e3799;
        margin-bottom: 1.5rem;
    }
    
    /* SRE cards */
    .sre-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%);
        border-left: 4px solid #1e3799;
    }
    
    .sre-rank {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e3799;
        margin-right: 0.5rem;
    }
    
    /* Badges */
    .badge-excelente {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .bom {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    
    .regular {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .melhorar {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    /* Matrix */
    .matrix-quadrant {
        padding: 10px;
        border-radius: 8px;
        margin: 5px;
        font-weight: bold;
        text-align: center;
    }
    
    .quadrant-stars {
        background-color: #d4edda;
        color: #155724;
        border: 2px solid #28a745;
    }
    
    .quadrant-efficient {
        background-color: #fff3cd;
        color: #856404;
        border: 2px solid #ffc107;
    }
    
    .quadrant-careful {
        background-color: #cce5ff;
        color: #004085;
        border: 2px solid #007bff;
    }
    
    .quadrant-needs-help {
        background-color: #f8d7da;
        color: #721c24;
        border: 2px solid #dc3545;
    }
    
    /* Footer */
    .footer-exec {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 2px solid #e9ecef;
        color: #6c757d;
        font-size: 0.9rem;
    }
    
    /* Trends */
    .trend-up { color: #28a745; font-weight: bold; }
    .trend-down { color: #dc3545; font-weight: bold; }
    .trend-neutral { color: #6c757d; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ============================================
# CLASSES AUXILIARES
# ============================================

class TimeoutException(Exception):
    """Exceção para timeout"""
    pass

# ============================================
# FUNÇÕES AUXILIARES OTIMIZADAS
# ============================================

def formatar_nome_responsavel(nome: str) -> str:
    """Formata nomes dos responsáveis - OTIMIZADA COM REGEX"""
    if pd.isna(nome):
        return "Não informado"
    
    nome_str = str(nome).strip()
    
    # Se for e-mail, extrair nome
    if REGEX_EMAIL.search(nome_str):
        partes = nome_str.split('@')[0]
        # Remover números e separadores usando regex
        partes = REGEX_SEPARADORES.sub(' ', partes)
        partes = REGEX_DIGITOS.sub('', partes)
        
        # Capitalizar e formatar
        palavras = [p.capitalize() for p in partes.split() if p.strip()]
        nome_formatado = ' '.join(palavras)
        
        # Corrigir conectivos usando regex
        nome_formatado = REGEX_CONECTIVOS.sub(
            lambda m: m.group().lower(), 
            nome_formatado
        )
        
        return nome_formatado if nome_formatado else "Não informado"
    
    # Se já for nome, apenas formatar
    palavras = nome_str.split()
    palavras_formatadas = []
    for palavra in palavras:
        if palavra.isupper() or len(palavra) <= 2:
            palavras_formatadas.append(palavra)
        else:
            palavras_formatadas.append(palavra.title())
    
    return ' '.join(palavras_formatadas)


def criar_card_indicador_simples(valor: Any, label: str, icone: str = "📊") -> str:
    """Cria card de indicador SIMPLES - OTIMIZADA"""
    if isinstance(valor, (int, float)):
        if valor >= 1000:
            valor_formatado = f"{valor:,.0f}".replace(",", ".")
        else:
            valor_formatado = f"{valor:,}"
    else:
        valor_formatado = str(valor)
    
    return f'''
    <div class="metric-card-exec card-base">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <span style="font-size: 1.5rem;">{icone}</span>
            <div style="flex-grow: 1;">
                <div class="metric-value">{valor_formatado}</div>
                <div class="metric-label">{label}</div>
            </div>
        </div>
    </div>
    '''


def calcular_hash_arquivo(conteudo: bytes) -> str:
    """Calcula hash do conteúdo do arquivo"""
    return hashlib.md5(conteudo).hexdigest()


def validar_arquivo_tamanho(conteudo: bytes) -> bool:
    """Valida tamanho máximo do arquivo"""
    tamanho_mb = len(conteudo) / (1024 * 1024)
    if tamanho_mb > MAX_FILE_SIZE_MB:
        logger.warning(f"Arquivo muito grande: {tamanho_mb:.2f}MB")
        return False
    return True


def get_horario_brasilia() -> str:
    """Retorna o horário atual de Brasília - OTIMIZADA"""
    try:
        agora = datetime.now(TZ_BRASIL)
        return agora.strftime('%d/%m/%Y %H:%M:%S')
    except Exception as e:
        logger.error(f"Erro ao obter horário: {e}")
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


@st.cache_data(ttl=CACHE_TTL, max_entries=MAX_ENTRIES_CACHE, show_spinner=False)
def carregar_dados(uploaded_file=None, caminho_arquivo=None) -> Tuple[Optional[pd.DataFrame], str, Optional[str]]:
    """Carrega e processa os dados - OTIMIZADA"""
    start_time = time.time()
    df = None
    status = ""
    hash_conteudo = None
    
    try:
        # Validar inputs
        if not uploaded_file and not caminho_arquivo:
            return None, "Nenhum arquivo fornecido", None
        
        # Ler conteúdo
        conteudo_bytes = None
        if uploaded_file:
            conteudo_bytes = uploaded_file.getvalue()
            if not validar_arquivo_tamanho(conteudo_bytes):
                return None, f"Arquivo muito grande (max {MAX_FILE_SIZE_MB}MB)", None
            conteudo = conteudo_bytes.decode('utf-8-sig')
        else:
            if not os.path.exists(caminho_arquivo):
                return None, f"Arquivo não encontrado: {caminho_arquivo}", None
            
            with open(caminho_arquivo, 'rb') as f:
                conteudo_bytes = f.read()
            
            if not validar_arquivo_tamanho(conteudo_bytes):
                return None, f"Arquivo muito grande (max {MAX_FILE_SIZE_MB}MB)", None
            
            conteudo = conteudo_bytes.decode('utf-8-sig')
        
        # Encontrar cabeçalho
        lines = conteudo.split('\n')
        header_line = None
        
        for i, line in enumerate(lines[:20]):  # Verificar apenas as primeiras 20 linhas
            if '"Chamado"' in line and '"Tipo Chamado"' in line:
                header_line = i
                break
        
        if header_line is None:
            return None, "Formato de arquivo inválido: cabeçalho não encontrado", None
        
        # Ler dados com otimização de tipos
        data_str = '\n'.join(lines[header_line:])
        
        # Primeira leitura para identificar colunas
        df_temp = pd.read_csv(io.StringIO(data_str), quotechar='"', nrows=10)
        
        # Criar dtypes específicos para otimização
        dtypes = {}
        for col in df_temp.columns:
            if col in DTYPE_OPTIMIZATION:
                dtypes[col] = DTYPE_OPTIMIZATION[col]
            elif df_temp[col].dtype == 'object':
                unique_ratio = df_temp[col].nunique() / len(df_temp)
                if unique_ratio < 0.5:
                    dtypes[col] = 'category'
        
        # Ler dados completos com dtypes otimizados
        df = pd.read_csv(
            io.StringIO(data_str), 
            quotechar='"',
            dtype=dtypes,
            parse_dates=['Criado', 'Modificado'],
            infer_datetime_format=True,
            dayfirst=True,
            on_bad_lines='warn'
        )
        
        # Liberar memória
        del df_temp, data_str, lines, conteudo
        gc.collect()
        
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
        
        # Validar colunas obrigatórias
        colunas_faltantes = [col for col in COLUNAS_OBRIGATORIAS if col not in df.columns]
        if colunas_faltantes:
            logger.warning(f"Colunas faltantes: {colunas_faltantes}")
        
        # Formatar nomes dos responsáveis
        if 'Responsável' in df.columns:
            df['Responsável_Formatado'] = df['Responsável'].apply(formatar_nome_responsavel)
        
        # Converter datas
        date_columns = ['Criado', 'Modificado']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
        
        # Extrair informações temporais
        if 'Criado' in df.columns:
            dt_series = df['Criado']
            
            df['Ano'] = dt_series.dt.year
            df['Mês'] = dt_series.dt.month
            df['Mês_Num'] = df['Mês']
            df['Dia'] = dt_series.dt.day
            df['Hora'] = dt_series.dt.hour
            df['Mês_Ano'] = dt_series.dt.strftime('%b/%Y')
            df['Nome_Mês'] = df['Mês'].map(MESES_ABREVIADOS)
            df['Nome_Mês_Completo'] = df['Mês'].map(MESES_COMPLETOS)
            df['Ano_Mês'] = dt_series.dt.strftime('%Y-%m')
            
            del dt_series
        
        # Converter revisões
        if 'Revisões' in df.columns:
            df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce')
            df['Revisões'] = df['Revisões'].fillna(0).astype('Int32')
        
        # Validar datas
        if 'Criado' in df.columns:
            data_atual = pd.Timestamp.now(tz='UTC')
            datas_futuras = df['Criado'] > data_atual
            if datas_futuras.any():
                logger.warning(f"Encontradas {datas_futuras.sum()} datas futuras")
                df.loc[datas_futuras, 'Criado'] = data_atual
        
        # Calcular hash
        hash_conteudo = calcular_hash_arquivo(conteudo_bytes)
        
        # Limpar memória
        del conteudo_bytes
        gc.collect()
        
        tempo_execucao = time.time() - start_time
        logger.info(f"Dados carregados: {len(df)} registros em {tempo_execucao:.2f}s")
        
        return df, "✅ Dados carregados com sucesso", hash_conteudo
    
    except pd.errors.EmptyDataError:
        return None, "Arquivo CSV vazio", None
    except pd.errors.ParserError as e:
        logger.error(f"Erro de parsing CSV: {e}")
        return None, f"Erro no formato do CSV: {str(e)}", None
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {e}", exc_info=True)
        return None, f"Erro: {str(e)}", None
    finally:
        gc.collect()


def encontrar_arquivo_dados() -> Optional[str]:
    """Tenta encontrar o arquivo de dados"""
    if os.path.exists(CAMINHO_ARQUIVO_PRINCIPAL):
        return CAMINHO_ARQUIVO_PRINCIPAL
    
    for caminho in CAMINHOS_ALTERNATIVOS:
        if os.path.exists(caminho):
            return caminho
    
    return None


def verificar_atualizacao_arquivo() -> bool:
    """Verifica se o arquivo foi modificado"""
    caminho_arquivo = encontrar_arquivo_dados()
    
    if caminho_arquivo and os.path.exists(caminho_arquivo):
        ultima_mod_key = 'ultima_modificacao'
        
        if ultima_mod_key not in st.session_state:
            st.session_state[ultima_mod_key] = os.path.getmtime(caminho_arquivo)
            return False
        
        modificacao_atual = os.path.getmtime(caminho_arquivo)
        
        if modificacao_atual > st.session_state[ultima_mod_key]:
            st.session_state[ultima_mod_key] = modificacao_atual
            return True
    
    return False


def limpar_sessao_dados():
    """Limpa todos os dados da sessão"""
    keys_to_clear = [
        'df_original', 'df_filtrado', 'arquivo_atual',
        'ultima_modificacao', 'file_hash', 'uploaded_file_name',
        'ultima_atualizacao', 'filtros_aplicados', 'estatisticas_cache'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            try:
                if isinstance(st.session_state[key], pd.DataFrame):
                    st.session_state[key] = None
                del st.session_state[key]
            except:
                pass
    
    gc.collect()


def validar_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Valida integridade do DataFrame"""
    problemas = []
    
    if df is None:
        return False, ["DataFrame é None"]
    
    if df.empty:
        return False, ["DataFrame vazio"]
    
    # Verificar colunas mínimas
    colunas_minimas = ['Chamado', 'Status']
    for col in colunas_minimas:
        if col not in df.columns:
            problemas.append(f"Coluna obrigatória '{col}' não encontrada")
    
    # Verificar duplicatas
    if 'Chamado' in df.columns:
        duplicatas = df['Chamado'].duplicated().sum()
        if duplicatas > 0:
            problemas.append(f"Encontrados {duplicatas} chamados duplicados")
    
    # Verificar valores nulos
    if 'Chamado' in df.columns:
        nulos = df['Chamado'].isna().sum()
        if nulos > 0:
            problemas.append(f"Encontrados {nulos} chamados sem número")
    
    return len(problemas) == 0, problemas


def inicializar_sessao():
    """Inicializa ou limpa a sessão de forma segura"""
    chaves_essenciais = {
        'df_original': None,
        'df_filtrado': None,
        'arquivo_atual': None,
        'file_hash': None,
        'uploaded_file_name': None,
        'ultima_modificacao': None,
        'ultima_atualizacao': get_horario_brasilia(),
        'filtros_aplicados': False,
        'estatisticas_cache': None
    }
    
    for key, default in chaves_essenciais.items():
        if key not in st.session_state:
            st.session_state[key] = default
    
    # Limpar chaves obsoletas
    chaves_obsoletas = [k for k in st.session_state.keys() 
                       if k.startswith('temp_') or k.startswith('cache_')]
    
    for key in chaves_obsoletas:
        try:
            del st.session_state[key]
        except:
            pass


def aplicar_filtros_seguros(df: pd.DataFrame, filtros: Dict[str, Any]) -> pd.DataFrame:
    """Aplica filtros de forma segura e otimizada"""
    if df.empty:
        return df
    
    df_filtrado = df.copy()
    
    try:
        if 'ano' in filtros and filtros['ano'] and 'Ano' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Ano'] == filtros['ano']]
        
        if 'mes' in filtros and filtros['mes'] and 'Mês' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Mês'] == filtros['mes']]
        
        if 'responsavel' in filtros and filtros['responsavel'] and filtros['responsavel'] != 'Todos':
            if 'Responsável_Formatado' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Responsável_Formatado'] == filtros['responsavel']]
        
        if 'status' in filtros and filtros['status'] and filtros['status'] != 'Todos':
            if 'Status' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Status'] == filtros['status']]
        
        if 'tipo' in filtros and filtros['tipo'] and filtros['tipo'] != 'Todos':
            if 'Tipo_Chamado' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Tipo_Chamado'] == filtros['tipo']]
        
        if 'sre' in filtros and filtros['sre'] and filtros['sre'] != 'Todos':
            if 'SRE' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['SRE'] == filtros['sre']]
        
        if 'chamado' in filtros and filtros['chamado']:
            if 'Chamado' in df_filtrado.columns:
                busca = str(filtros['chamado']).strip()
                if busca:
                    df_filtrado = df_filtrado[df_filtrado['Chamado'].astype(str).str.contains(busca, na=False)]
        
        if len(df_filtrado) < len(df) * 0.5:
            del df
            gc.collect()
        
        return df_filtrado
    
    except Exception as e:
        logger.error(f"Erro ao aplicar filtros: {e}")
        return df


def timeout_handler(signum, frame):
    """Handler para timeout"""
    raise TimeoutException("Operação excedeu o tempo limite")


def executar_com_timeout(func, *args, timeout=TIMEOUT_SECONDS, **kwargs):
    """Executa função com timeout"""
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
    
    try:
        result = func(*args, **kwargs)
        return result
    except TimeoutException:
        logger.warning(f"Timeout na função {func.__name__}")
        return None
    finally:
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)


def limpeza_periodica():
    """Executa limpeza periódica de memória"""
    gc.collect()
    
    tempo_atual = time.time()
    if 'ultima_interacao' in st.session_state:
        tempo_inativo = tempo_atual - st.session_state.ultima_interacao
        if tempo_inativo > 3600:
            limpar_sessao_dados()
    
    st.session_state.ultima_interacao = tempo_atual


# ============================================
# FUNÇÕES DE ANÁLISE COM CACHE
# ============================================

@st.cache_data(ttl=300, max_entries=3)
def calcular_taxa_retorno_sre(df: pd.DataFrame, sre_nome: str) -> Tuple[float, int, int]:
    """Calcula taxa de retorno específica para um SRE"""
    if df.empty or 'SRE' not in df.columns:
        return 0.0, 0, 0
    
    mask = df['SRE'] == sre_nome
    if not mask.any():
        return 0.0, 0, 0
    
    total_cards = mask.sum()
    
    if 'Revisões' in df.columns:
        cards_com_revisoes = (mask & (df['Revisões'] > 0)).sum()
        taxa_retorno = (cards_com_revisoes / total_cards * 100) if total_cards > 0 else 0.0
    else:
        taxa_retorno = 0.0
        cards_com_revisoes = 0
    
    if 'Status' in df.columns:
        cards_sincronizados = (mask & (df['Status'] == 'Sincronizado')).sum()
    else:
        cards_sincronizados = 0
    
    return round(taxa_retorno, 2), cards_com_revisoes, cards_sincronizados


@st.cache_data(ttl=300, max_entries=2)
def criar_matriz_performance_dev(df: pd.DataFrame) -> pd.DataFrame:
    """Cria matriz de performance para Desenvolvedores"""
    if df.empty or 'Responsável_Formatado' not in df.columns:
        return pd.DataFrame()
    
    devs = df['Responsável_Formatado'].dropna().unique()
    matriz_data = []
    
    for dev in devs:
        mask = df['Responsável_Formatado'] == dev
        df_dev = df.loc[mask].copy()
        
        if len(df_dev) == 0:
            continue
        
        total_cards = len(df_dev)
        
        if 'Criado' in df_dev.columns:
            meses_ativos = df_dev['Criado'].dt.to_period('M').nunique()
            eficiencia = total_cards / max(meses_ativos, 1)
        else:
            eficiencia = total_cards
        
        if 'Revisões' in df_dev.columns:
            cards_sem_revisao = (df_dev['Revisões'] == 0).sum()
            qualidade = (cards_sem_revisao / total_cards * 100) if total_cards > 0 else 0.0
        else:
            qualidade = 100.0
        
        peso_qualidade = 0.5
        peso_eficiencia = 0.3
        peso_volume = 0.2
        
        fator_eficiencia = min(eficiencia * 5, 100)
        fator_volume = (total_cards / max(len(df), 1)) * 100
        
        score = (qualidade * peso_qualidade) + (fator_eficiencia * peso_eficiencia) + (fator_volume * peso_volume)
        
        matriz_data.append({
            'Desenvolvedor': dev,
            'Eficiencia': round(eficiencia, 1),
            'Qualidade': round(qualidade, 1),
            'Score': round(score, 1),
            'Total_Cards': total_cards
        })
    
    result_df = pd.DataFrame(matriz_data)
    del matriz_data
    gc.collect()
    
    return result_df


@st.cache_data(ttl=300, max_entries=5)
def analisar_tendencia_mensal_sre(df: pd.DataFrame, sre_nome: str) -> Optional[pd.DataFrame]:
    """Analisa tendência mensal de sincronizações"""
    if df.empty or 'SRE' not in df.columns or 'Criado' not in df.columns:
        return None
    
    mask = df['SRE'] == sre_nome
    if not mask.any():
        return None
    
    df_sre = df.loc[mask].copy()
    
    df_sre['Mes_Ano'] = df_sre['Criado'].dt.strftime('%Y-%m')
    
    sinc_mes = df_sre[df_sre['Status'] == 'Sincronizado'].groupby('Mes_Ano').size().reset_index()
    sinc_mes.columns = ['Mes_Ano', 'Sincronizados']
    
    total_mes = df_sre.groupby('Mes_Ano').size().reset_index()
    total_mes.columns = ['Mes_Ano', 'Total']
    
    dados_mes = pd.merge(total_mes, sinc_mes, on='Mes_Ano', how='left').fillna(0)
    
    dados_mes = dados_mes.sort_values('Mes_Ano')
    dados_mes['Sincronizados'] = dados_mes['Sincronizados'].astype('int32')
    dados_mes['Total'] = dados_mes['Total'].astype('int32')
    
    return dados_mes


@st.cache_data(ttl=600, max_entries=10)
def gerar_recomendacoes_dev(df: pd.DataFrame, dev_nome: str) -> List[Dict[str, Any]]:
    """Gera recomendações personalizadas para um Desenvolvedor"""
    if df.empty or 'Responsável_Formatado' not in df.columns:
        return []
    
    mask = df['Responsável_Formatado'] == dev_nome
    if not mask.any():
        return []
    
    df_dev = df.loc[mask].copy()
    total_cards = len(df_dev)
    
    if total_cards == 0:
        return []
    
    if 'Revisões' in df_dev.columns:
        cards_sem_revisao = (df_dev['Revisões'] == 0).sum()
        qualidade = (cards_sem_revisao / total_cards * 100) if total_cards > 0 else 0.0
    else:
        qualidade = 100.0
    
    if 'Criado' in df_dev.columns:
        meses_ativos = df_dev['Criado'].dt.to_period('M').nunique()
        eficiencia = total_cards / max(meses_ativos, 1)
    else:
        eficiencia = total_cards
    
    recomendacoes = []
    
    if qualidade < 70:
        recomendacoes.append({
            'prioridade': 'ALTA',
            'titulo': 'Melhorar qualidade do código',
            'descricao': f'Taxa de aprovação sem revisão: {qualidade:.1f}% (abaixo de 70%)',
            'acao': 'Implementar testes mais rigorosos antes do envio',
            'score': round(qualidade, 1)
        })
    
    if eficiencia < 3:
        recomendacoes.append({
            'prioridade': 'MÉDIA',
            'titulo': 'Aumentar produtividade',
            'descricao': f'Eficiência atual: {eficiencia:.1f} cards/mês',
            'acao': 'Otimizar processo de desenvolvimento',
            'score': round(eficiencia, 1)
        })
    
    if 'Status' in df_dev.columns:
        cards_sincronizados = (df_dev['Status'] == 'Sincronizado').sum()
        if cards_sincronizados < total_cards * 0.6:
            recomendacoes.append({
                'prioridade': 'ALTA',
                'titulo': 'Melhorar taxa de sincronização',
                'descricao': f'Apenas {cards_sincronizados}/{total_cards} cards sincronizados',
                'acao': 'Revisar critérios antes do envio para SRE',
                'score': round(cards_sincronizados / total_cards * 100, 1)
            })
    
    if qualidade > 90 and eficiencia > 8:
        recomendacoes.append({
            'prioridade': 'BAIXA',
            'titulo': 'Manter excelente performance',
            'descricao': 'Excelente equilíbrio entre qualidade e eficiência',
            'acao': 'Compartilhar melhores práticas com a equipe',
            'score': round((qualidade + eficiencia * 10) / 2, 1)
        })
    
    ordem_prioridade = {'ALTA': 0, 'MÉDIA': 1, 'BAIXA': 2}
    recomendacoes.sort(key=lambda x: ordem_prioridade.get(x['prioridade'], 3))
    
    return recomendacoes


@st.cache_data(ttl=300, max_entries=3)
def calcular_estatisticas_basicas(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula estatísticas básicas do DataFrame"""
    if df.empty:
        return {}
    
    stats = {
        'total_registros': len(df),
        'total_sincronizados': 0,
        'total_revisoes': 0,
        'data_min': None,
        'data_max': None,
        'top_responsavel': None,
        'top_tipo': None
    }
    
    if 'Status' in df.columns:
        stats['total_sincronizados'] = (df['Status'] == 'Sincronizado').sum()
    
    if 'Revisões' in df.columns:
        stats['total_revisoes'] = df['Revisões'].sum()
    
    if 'Criado' in df.columns:
        stats['data_min'] = df['Criado'].min()
        stats['data_max'] = df['Criado'].max()
    
    if 'Responsável_Formatado' in df.columns:
        top_resp = df['Responsável_Formatado'].value_counts().head(1)
        if not top_resp.empty:
            stats['top_responsavel'] = top_resp.index[0]
    
    if 'Tipo_Chamado' in df.columns:
        top_tipo = df['Tipo_Chamado'].value_counts().head(1)
        if not top_tipo.empty:
            stats['top_tipo'] = top_tipo.index[0]
    
    return stats


def substituir_nome_sre(sre_nome):
    """Substitui e-mail pelo nome correto do SRE"""
    if pd.isna(sre_nome):
        return "Não informado"
    
    sre_nome_str = str(sre_nome).lower()
    
    if "kewin" in sre_nome_str or "ferreira" in sre_nome_str:
        return "Kewin Marcel"
    elif "pierry" in sre_nome_str or "perez" in sre_nome_str:
        return "Pierry Perez"
    elif "bruna" in sre_nome_str or "maciel" in sre_nome_str:
        return "Bruna Maciel"
    elif "ramiza" in sre_nome_str or "irineu" in sre_nome_str:
        return "Ramiza Irineu"
    else:
        return sre_nome

# ============================================
# SIDEBAR - FILTROS E CONTROLES
# ============================================
with st.sidebar:
    # Logo e título
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h3 style="color: #1e3799; margin: 0;">⚙️ Painel de Controle</h3>
        <p style="color: #6c757d; margin: 0; font-size: 0.9rem;">Filtros e Configurações</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Inicializar sessão
    inicializar_sessao()
    limpeza_periodica()
    
    # FILTROS APENAS SE HOUVER DADOS
    if st.session_state.df_original is not None:
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**🔍 Filtros de Análise**")
            
            df = st.session_state.df_original.copy()
            filtros = {}
            
            # FILTRO POR ANO
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
                        filtros['ano'] = int(ano_selecionado)
            
            # FILTRO POR MÊS
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
                        filtros['mes'] = int(mes_selecionado)
            
            # FILTRO POR RESPONSÁVEL
            if 'Responsável_Formatado' in df.columns:
                responsaveis = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
                responsavel_selecionado = st.selectbox(
                    "👤 Responsável",
                    options=responsaveis,
                    key="filtro_responsavel"
                )
                if responsavel_selecionado != 'Todos':
                    filtros['responsavel'] = responsavel_selecionado
            
            # BUSCA POR CHAMADO
            busca_chamado = st.text_input(
                "🔎 Buscar Chamado",
                placeholder="Digite número do chamado...",
                key="busca_chamado"
            )
            if busca_chamado:
                filtros['chamado'] = busca_chamado
            
            # FILTRO POR STATUS
            if 'Status' in df.columns:
                status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox(
                    "📊 Status",
                    options=status_opcoes,
                    key="filtro_status"
                )
                if status_selecionado != 'Todos':
                    filtros['status'] = status_selecionado
            
            # FILTRO POR TIPO
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos'] + sorted(df['Tipo_Chamado'].dropna().unique())
                tipo_selecionado = st.selectbox(
                    "📝 Tipo de Chamado",
                    options=tipos,
                    key="filtro_tipo"
                )
                if tipo_selecionado != 'Todos':
                    filtros['tipo'] = tipo_selecionado
            
            # FILTRO POR EMPRESA
            if 'Empresa' in df.columns:
                empresas = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                empresa_selecionada = st.selectbox(
                    "🏢 Empresa",
                    options=empresas,
                    key="filtro_empresa"
                )
                if empresa_selecionada != 'Todas':
                    filtros['empresa'] = empresa_selecionada
            
            # FILTRO POR SRE
            if 'SRE' in df.columns:
                sres = ['Todos'] + sorted(df['SRE'].dropna().unique())
                sre_selecionado = st.selectbox(
                    "🔧 SRE Responsável",
                    options=sres,
                    key="filtro_sre"
                )
                if sre_selecionado != 'Todos':
                    filtros['sre'] = sre_selecionado
            
            # Aplicar filtros seguros
            if filtros:
                df_filtrado = aplicar_filtros_seguros(df, filtros)
                st.session_state.df_filtrado = df_filtrado
                st.session_state.filtros_aplicados = True
            else:
                st.session_state.df_filtrado = df
            
            # Validar DataFrame
            valido, problemas = validar_dataframe(st.session_state.df_filtrado)
            if not valido and problemas:
                st.warning(f"⚠️ Problemas nos dados: {', '.join(problemas[:2])}")
            
            st.markdown(f"**📈 Registros filtrados:** {len(st.session_state.df_filtrado):,}")
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
                                logger.error(f"Erro ao recarregar: {e}")
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
            <div class="info-base">
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
            # Validar arquivo
            if not uploaded_file.name.endswith('.csv'):
                st.error("❌ Apenas arquivos CSV são permitidos")
                st.stop()
            
            if len(uploaded_file.getvalue()) > MAX_FILE_SIZE_MB * 1024 * 1024:
                st.error(f"❌ Arquivo muito grande. Máximo: {MAX_FILE_SIZE_MB}MB")
                st.stop()
            
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
    
    # CARREGAMENTO AUTOMÁTICO DO ARQUIVO LOCAL
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
st.markdown("""
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
            Dashboard de Performance
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 0.2rem 0 0 0; font-size: 0.85rem;">
            v5.5 | Sistema de Performance SRE
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# EXIBIR DASHBOARD SE HOUVER DADOS
# ============================================
if st.session_state.df_original is not None:
    df_uso = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    # Validar antes de usar
    valido, problemas = validar_dataframe(df_uso)
    if not valido:
        st.error(f"❌ Dados inválidos: {', '.join(problemas)}")
        df_uso = st.session_state.df_original
        valido, _ = validar_dataframe(df_uso)
        if not valido:
            st.stop()
    
    # Calcular estatísticas básicas
    stats = calcular_estatisticas_basicas(df_uso)
    
    # INFORMAÇÕES DA BASE DE DADOS
    st.markdown("## 📊 Informações da Base de Dados")
    
    if 'Criado' in df_uso.columns and not df_uso.empty:
        data_min = df_uso['Criado'].min()
        data_max = df_uso['Criado'].max()
        
        st.markdown(f"""
        <div class="info-base">
            <p style="margin: 0; font-weight: 600;">📅 Base atualizada em: {get_horario_brasilia()}</p>
            <p style="margin: 0.3rem 0 0 0; color: #6c757d;">
            Período coberto: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')} | 
            Total de registros: {len(df_uso):,}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # INDICADORES PRINCIPAIS SIMPLES
    st.markdown("## 📈 INDICADORES PRINCIPAIS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_atual = len(df_uso)
        st.markdown(criar_card_indicador_simples(
            total_atual, 
            "Total de Demandas", 
            "📋"
        ), unsafe_allow_html=True)
    
    with col2:
        if 'Status' in df_uso.columns:
            sincronizados = len(df_uso[df_uso['Status'] == 'Sincronizado'])
            st.markdown(criar_card_indicador_simples(
                sincronizados,
                "Sincronizados",
                "✅"
            ), unsafe_allow_html=True)
    
    with col3:
        if 'Revisões' in df_uso.columns:
            total_revisoes = int(df_uso['Revisões'].sum())
            st.markdown(criar_card_indicador_simples(
                total_revisoes,
                "Total de Revisões",
                "📝"
            ), unsafe_allow_html=True)
    
    # ABAS PRINCIPAIS
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
            if 'Ano' in df_uso.columns:
                anos_disponiveis = sorted(df_uso['Ano'].dropna().unique().astype(int))
                if anos_disponiveis:
                    ano_selecionado = st.selectbox(
                        "Selecionar Ano:",
                        options=anos_disponiveis,
                        index=len(anos_disponiveis)-1,
                        label_visibility="collapsed",
                        key="ano_evolucao"
                    )
        
        if 'Ano' in df_uso.columns and 'Nome_Mês' in df_uso.columns and anos_disponiveis:
            df_ano = df_uso[df_uso['Ano'] == ano_selecionado].copy()
            
            if not df_ano.empty:
                todos_meses = pd.DataFrame({
                    'Mês_Num': range(1, 13),
                    'Nome_Mês': ORDEM_MESES
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
                    showlegend=False,
                    margin=dict(t=50, b=50, l=50, r=50),
                    xaxis=dict(
                        gridcolor='rgba(0,0,0,0.05)',
                        tickmode='array',
                        tickvals=list(range(12)),
                        ticktext=ORDEM_MESES
                    ),
                    yaxis=dict(
                        gridcolor='rgba(0,0,0,0.05)',
                        rangemode='tozero'
                    )
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
    
    with tab2:
        st.markdown('<div class="section-title-exec">📊 REVISÕES POR RESPONSÁVEL</div>', unsafe_allow_html=True)
        
        col_rev_filtro1, col_rev_filtro2 = st.columns(2)
        
        with col_rev_filtro1:
            if 'Ano' in df_uso.columns:
                anos_rev = sorted(df_uso['Ano'].dropna().unique().astype(int))
                anos_opcoes_rev = ['Todos os Anos'] + list(anos_rev)
                ano_rev = st.selectbox(
                    "📅 Filtrar por Ano:",
                    options=anos_opcoes_rev,
                    key="filtro_ano_revisoes"
                )
        
        with col_rev_filtro2:
            if 'Mês' in df_uso.columns:
                meses_rev = sorted(df_uso['Mês'].dropna().unique().astype(int))
                meses_opcoes_rev = ['Todos os Meses'] + [str(m) for m in meses_rev]
                mes_rev = st.selectbox(
                    "📆 Filtrar por Mês:",
                    options=meses_opcoes_rev,
                    key="filtro_mes_revisoes"
                )
        
        df_rev = df_uso.copy()
        
        if ano_rev != 'Todos os Anos':
            df_rev = df_rev[df_rev['Ano'] == int(ano_rev)]
        
        if mes_rev != 'Todos os Meses':
            df_rev = df_rev[df_rev['Mês'] == int(mes_rev)]
        
        if 'Revisões' in df_rev.columns and 'Responsável_Formatado' in df_rev.columns:
            df_com_revisoes = df_rev[df_rev['Revisões'] > 0].copy()
            
            if not df_com_revisoes.empty:
                revisoes_por_responsavel = df_com_revisoes.groupby('Responsável_Formatado').agg({
                    'Revisões': 'sum',
                    'Chamado': 'count'
                }).reset_index()
                
                revisoes_por_responsavel.columns = ['Responsável', 'Total_Revisões', 'Chamados_Com_Revisão']
                revisoes_por_responsavel = revisoes_por_responsavel.sort_values('Total_Revisões', ascending=False)
                
                titulo_rev = 'Top 15 Responsáveis com Mais Revisões'
                if ano_rev != 'Todos os Anos':
                    titulo_rev += f' - {ano_rev}'
                if mes_rev != 'Todos os Meses':
                    meses_nomes = MESES_COMPLETOS
                    titulo_rev += f' - {meses_nomes[int(mes_rev)]}'
                
                fig_revisoes = go.Figure()
                
                max_revisoes = revisoes_por_responsavel['Total_Revisões'].max()
                min_revisoes = revisoes_por_responsavel['Total_Revisões'].min()
                
                colors = []
                for valor in revisoes_por_responsavel['Total_Revisões']:
                    if max_revisoes == min_revisoes:
                        colors.append('#e74c3c')
                    else:
                        normalized = (valor - min_revisoes) / (max_revisoes - min_revisoes)
                        red = int(231 * normalized + 40 * (1 - normalized))
                        green = int(76 * normalized + 167 * (1 - normalized))
                        blue = int(60 * normalized + 69 * (1 - normalized))
                        colors.append(f'rgb({red}, {green}, {blue})')
                
                fig_revisoes.add_trace(go.Bar(
                    x=revisoes_por_responsavel['Responsável'].head(15),
                    y=revisoes_por_responsavel['Total_Revisões'].head(15),
                    name='Total de Revisões',
                    text=revisoes_por_responsavel['Total_Revisões'].head(15),
                    textposition='outside',
                    marker_color=colors[:15],
                    marker_line_color='#2c3e50',
                    marker_line_width=1.5,
                    opacity=0.8
                ))
                
                fig_revisoes.update_layout(
                    title=titulo_rev,
                    xaxis_title='Responsável',
                    yaxis_title='Total de Revisões',
                    plot_bgcolor='white',
                    height=500,
                    showlegend=False,
                    margin=dict(t=50, b=100, l=50, r=50),
                    xaxis=dict(
                        tickangle=45,
                        gridcolor='rgba(0,0,0,0.05)'
                    ),
                    yaxis=dict(
                        gridcolor='rgba(0,0,0,0.05)'
                    )
                )
                
                st.plotly_chart(fig_revisoes, use_container_width=True)
    
    with tab3:
        st.markdown('<div class="section-title-exec">📈 CHAMADOS SINCRONIZADOS POR DIA</div>', unsafe_allow_html=True)
        
        col_sinc_filtro1, col_sinc_filtro2 = st.columns(2)
        
        with col_sinc_filtro1:
            if 'Ano' in df_uso.columns:
                anos_sinc = sorted(df_uso['Ano'].dropna().unique().astype(int))
                anos_opcoes_sinc = ['Todos os Anos'] + list(anos_sinc)
                ano_sinc = st.selectbox(
                    "📅 Filtrar por Ano:",
                    options=anos_opcoes_sinc,
                    key="filtro_ano_sinc"
                )
        
        with col_sinc_filtro2:
            if 'Mês' in df_uso.columns:
                meses_sinc = sorted(df_uso['Mês'].dropna().unique().astype(int))
                meses_opcoes_sinc = ['Todos os Meses'] + [str(m) for m in meses_sinc]
                mes_sinc = st.selectbox(
                    "📆 Filtrar por Mês:",
                    options=meses_opcoes_sinc,
                    key="filtro_mes_sinc"
                )
        
        df_sinc = df_uso.copy()
        
        if ano_sinc != 'Todos os Anos':
            df_sinc = df_sinc[df_sinc['Ano'] == int(ano_sinc)]
        
        if mes_sinc != 'Todos os Meses':
            df_sinc = df_sinc[df_sinc['Mês'] == int(mes_sinc)]
        
        if 'Status' in df_sinc.columns and 'Criado' in df_sinc.columns:
            df_sincronizados = df_sinc[df_sinc['Status'] == 'Sincronizado'].copy()
            
            if not df_sincronizados.empty:
                df_sincronizados['Data'] = df_sincronizados['Criado'].dt.date
                
                sincronizados_por_dia = df_sincronizados.groupby('Data').size().reset_index()
                sincronizados_por_dia.columns = ['Data', 'Quantidade']
                sincronizados_por_dia = sincronizados_por_dia.sort_values('Data')
                
                titulo_sinc = 'Evolução Diária de Chamados Sincronizados'
                if ano_sinc != 'Todos os Anos':
                    titulo_sinc += f' - {ano_sinc}'
                if mes_sinc != 'Todos os Meses':
                    meses_nomes = MESES_COMPLETOS
                    titulo_sinc += f' - {meses_nomes[int(mes_sinc)]}'
                
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
                    title=titulo_sinc,
                    xaxis_title='Data',
                    yaxis_title='Número de Chamados Sincronizados',
                    plot_bgcolor='white',
                    height=500,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    margin=dict(t=50, b=50, l=50, r=50),
                    xaxis=dict(
                        gridcolor='rgba(0,0,0,0.05)',
                        showgrid=True
                    ),
                    yaxis=dict(
                        gridcolor='rgba(0,0,0,0.05)',
                        rangemode='tozero'
                    )
                )
                
                st.plotly_chart(fig_dia, use_container_width=True)
    
    with tab4:
        st.markdown('<div class="section-title-exec">🏆 PERFORMANCE DOS SREs</div>', unsafe_allow_html=True)
        
        if 'SRE' in df_uso.columns and 'Status' in df_uso.columns and 'Revisões' in df_uso.columns:
            col_filtro1, col_filtro2 = st.columns(2)
            
            with col_filtro1:
                if 'Ano' in df_uso.columns:
                    anos_sre = sorted(df_uso['Ano'].dropna().unique().astype(int))
                    anos_opcoes_sre = ['Todos'] + list(anos_sre)
                    ano_sre = st.selectbox(
                        "📅 Filtrar por Ano:",
                        options=anos_opcoes_sre,
                        key="filtro_ano_sre"
                    )
            
            with col_filtro2:
                if 'Mês' in df_uso.columns:
                    meses_sre = sorted(df_uso['Mês'].dropna().unique().astype(int))
                    meses_opcoes_sre = ['Todos'] + [str(m) for m in meses_sre]
                    mes_sre = st.selectbox(
                        "📆 Filtrar por Mês:",
                        options=meses_opcoes_sre,
                        key="filtro_mes_sre"
                    )
            
            df_sre = df_uso.copy()
            
            if 'Ano' in df_sre.columns and ano_sre != 'Todos':
                df_sre = df_sre[df_sre['Ano'] == int(ano_sre)]
            
            if 'Mês' in df_sre.columns and mes_sre != 'Todos':
                df_sre = df_sre[df_sre['Mês'] == int(mes_sre)]
            
            df_sincronizados = df_sre[df_sre['Status'] == 'Sincronizado'].copy()
            
            if not df_sincronizados.empty and 'SRE' in df_sincronizados.columns:
                st.markdown("### 📈 Sincronizados por SRE")
                
                sinc_por_sre = df_sincronizados.groupby('SRE').size().reset_index()
                sinc_por_sre.columns = ['SRE', 'Sincronizados']
                sinc_por_sre = sinc_por_sre.sort_values('Sincronizados', ascending=False)
                
                sinc_por_sre['SRE_Nome'] = sinc_por_sre['SRE'].apply(substituir_nome_sre)
                
                sinc_por_sre_nome = sinc_por_sre.groupby('SRE_Nome')['Sincronizados'].sum().reset_index()
                sinc_por_sre_nome = sinc_por_sre_nome.sort_values('Sincronizados', ascending=False)
                
                fig_sinc_bar = go.Figure()
                
                max_sinc = sinc_por_sre_nome['Sincronizados'].max()
                min_sinc = sinc_por_sre_nome['Sincronizados'].min()
                
                colors = []
                for valor in sinc_por_sre_nome['Sincronizados']:
                    if max_sinc == min_sinc:
                        colors.append('#1e3799')
                    else:
                        normalized = (valor - min_sinc) / (max_sinc - min_sinc)
                        red = int(30 * normalized + 74 * (1 - normalized))
                        green = int(55 * normalized + 105 * (1 - normalized))
                        blue = int(153 * normalized + 189 * (1 - normalized))
                        colors.append(f'rgb({red}, {green}, {blue})')
                
                fig_sinc_bar.add_trace(go.Bar(
                    x=sinc_por_sre_nome['SRE_Nome'].head(15),
                    y=sinc_por_sre_nome['Sincronizados'].head(15),
                    name='Sincronizados',
                    text=sinc_por_sre_nome['Sincronizados'].head(15),
                    textposition='outside',
                    marker_color=colors[:15],
                    marker_line_color='#0c2461',
                    marker_line_width=1.5,
                    opacity=0.8
                ))
                
                titulo_grafico = 'Sincronizados por SRE'
                if ano_sre != 'Todos' or mes_sre != 'Todos':
                    titulo_grafico += ' - Filtrado'
                    if ano_sre != 'Todos':
                        titulo_grafico += f' ({ano_sre}'
                    if mes_sre != 'Todos':
                        if ano_sre != 'Todos':
                            titulo_grafico += f' - {MESES_COMPLETOS[int(mes_sre)]})'
                        else:
                            titulo_grafico += f' ({MESES_COMPLETOS[int(mes_sre)]})'
                
                fig_sinc_bar.update_layout(
                    title=titulo_grafico,
                    xaxis_title='SRE',
                    yaxis_title='Número de Sincronizados',
                    plot_bgcolor='white',
                    height=500,
                    showlegend=False,
                    margin=dict(t=50, b=100, l=50, r=50),
                    xaxis=dict(
                        tickangle=45,
                        gridcolor='rgba(0,0,0,0.05)',
                        categoryorder='total descending'
                    ),
                    yaxis=dict(
                        gridcolor='rgba(0,0,0,0.05)',
                        rangemode='tozero'
                    )
                )
                
                st.plotly_chart(fig_sinc_bar, use_container_width=True)
                
                col_top1, col_top2, col_top3 = st.columns(3)
                
                if len(sinc_por_sre_nome) >= 1:
                    with col_top1:
                        sre1 = sinc_por_sre_nome.iloc[0]
                        st.metric("🥇 1º Lugar Sincronizados", 
                                 f"{sre1['SRE_Nome']}", 
                                 f"{sre1['Sincronizados']} sinc.")
                
                if len(sinc_por_sre_nome) >= 2:
                    with col_top2:
                        sre2 = sinc_por_sre_nome.iloc[1]
                        st.metric("🥈 2º Lugar Sincronizados", 
                                 f"{sre2['SRE_Nome']}", 
                                 f"{sre2['Sincronizados']} sinc.")
                
                if len(sinc_por_sre_nome) >= 3:
                    with col_top3:
                        sre3 = sinc_por_sre_nome.iloc[2]
                        st.metric("🥉 3º Lugar Sincronizados", 
                                 f"{sre3['SRE_Nome']}", 
                                 f"{sre3['Sincronizados']} sinc.")
                
                st.markdown("### 📋 Performance Detalhada dos SREs")
                
                sres_metrics = []
                sres_list = df_sre['SRE'].dropna().unique()
                
                for sre in sres_list:
                    df_sre_data = df_sre[df_sre['SRE'] == sre].copy()
                    
                    if len(df_sre_data) > 0:
                        total_cards = len(df_sre_data)
                        sincronizados = len(df_sre_data[df_sre_data['Status'] == 'Sincronizado'])
                        
                        if 'Revisões' in df_sre_data.columns:
                            cards_retorno = len(df_sre_data[df_sre_data['Revisões'] > 0])
                        else:
                            cards_retorno = 0
                        
                        nome_sre_display = substituir_nome_sre(sre)
                        
                        sres_metrics.append({
                            'SRE': nome_sre_display,
                            'Total_Cards': total_cards,
                            'Sincronizados': sincronizados,
                            'Cards_Retorno': cards_retorno
                        })
                
                if sres_metrics:
                    df_sres_metrics = pd.DataFrame(sres_metrics)
                    df_sres_metrics = df_sres_metrics.groupby('SRE').agg({
                        'Total_Cards': 'sum',
                        'Sincronizados': 'sum',
                        'Cards_Retorno': 'sum'
                    }).reset_index()
                    
                    df_sres_metrics = df_sres_metrics.sort_values('Sincronizados', ascending=False)
                    
                    st.dataframe(
                        df_sres_metrics,
                        use_container_width=True,
                        column_config={
                            "SRE": st.column_config.TextColumn("SRE"),
                            "Total_Cards": st.column_config.NumberColumn("Total Cards", format="%d"),
                            "Sincronizados": st.column_config.NumberColumn("Sincronizados", format="%d"),
                            "Cards_Retorno": st.column_config.NumberColumn("Cards Retorno", format="%d")
                        }
                    )
    
    # ANÁLISES MELHORADAS
    st.markdown("---")
    st.markdown('<div class="section-title-exec">🔍 ANÁLISES AVANÇADAS</div>', unsafe_allow_html=True)
    
    tab_extra1, tab_extra2, tab_extra3 = st.tabs([
        "🚀 Performance de Desenvolvedores",
        "📈 Análise de Sazonalidade", 
        "⚡ Diagnóstico de Erros"
    ])
    
    with tab_extra1:
        if 'Responsável_Formatado' in df_uso.columns and 'Revisões' in df_uso.columns and 'Status' in df_uso.columns:
            col_filtro_perf1, col_filtro_perf2, col_filtro_perf3 = st.columns(3)
            
            with col_filtro_perf1:
                if 'Ano' in df_uso.columns:
                    anos_perf = sorted(df_uso['Ano'].dropna().unique().astype(int))
                    anos_opcoes_perf = ['Todos os Anos'] + list(anos_perf)
                    ano_perf = st.selectbox(
                        "📅 Filtrar por Ano:",
                        options=anos_opcoes_perf,
                        key="filtro_ano_perf"
                    )
            
            with col_filtro_perf2:
                if 'Mês' in df_uso.columns:
                    meses_perf = sorted(df_uso['Mês'].dropna().unique().astype(int))
                    meses_opcoes_perf = ['Todos os Meses'] + [str(m) for m in meses_perf]
                    mes_perf = st.selectbox(
                        "📆 Filtrar por Mês:",
                        options=meses_opcoes_perf,
                        key="filtro_mes_perf"
                    )
            
            with col_filtro_perf3:
                ordenar_por = st.selectbox(
                    "Ordenar por:",
                    options=["Score de Qualidade", "Total de Chamados", "Eficiência", "Produtividade"],
                    index=0
                )
            
            df_perf = df_uso.copy()
            
            if ano_perf != 'Todos os Anos':
                df_perf = df_perf[df_perf['Ano'] == int(ano_perf)]
            
            if mes_perf != 'Todos os Meses':
                df_perf = df_perf[df_perf['Mês'] == int(mes_perf)]
            
            dev_metrics = []
            devs = df_perf['Responsável_Formatado'].unique()
            
            for dev in devs:
                dev_data = df_perf[df_perf['Responsável_Formatado'] == dev]
                total_chamados = len(dev_data)
                
                if total_chamados > 0:
                    sem_revisao = len(dev_data[dev_data['Revisões'] == 0])
                    score_qualidade = (sem_revisao / total_chamados * 100) if total_chamados > 0 else 0
                    
                    sincronizados = len(dev_data[dev_data['Status'] == 'Sincronizado'])
                    eficiencia = (sincronizados / total_chamados * 100) if total_chamados > 0 else 0
                    
                    if 'Criado' in dev_data.columns:
                        meses_ativos = dev_data['Criado'].dt.to_period('M').nunique()
                        produtividade = total_chamados / meses_ativos if meses_ativos > 0 else 0
                    else:
                        produtividade = 0
                    
                    if score_qualidade >= 80 and produtividade >= 5:
                        classificacao = "🟢 Alto"
                    elif score_qualidade >= 60:
                        classificacao = "🟡 Médio"
                    else:
                        classificacao = "🔴 Baixo"
                    
                    dev_metrics.append({
                        'Desenvolvedor': dev,
                        'Total Chamados': total_chamados,
                        'Sem Revisão': sem_revisao,
                        'Score Qualidade': round(score_qualidade, 1),
                        'Sincronizados': sincronizados,
                        'Eficiência': round(eficiencia, 1),
                        'Produtividade': round(produtividade, 1),
                        'Classificação': classificacao
                    })
            
            if dev_metrics:
                df_dev_metrics = pd.DataFrame(dev_metrics)
                
                if ordenar_por == "Score de Qualidade":
                    df_dev_metrics = df_dev_metrics.sort_values('Score Qualidade', ascending=False)
                elif ordenar_por == "Total de Chamados":
                    df_dev_metrics = df_dev_metrics.sort_values('Total Chamados', ascending=False)
                elif ordenar_por == "Eficiência":
                    df_dev_metrics = df_dev_metrics.sort_values('Eficiência', ascending=False)
                elif ordenar_por == "Produtividade":
                    df_dev_metrics = df_dev_metrics.sort_values('Produtividade', ascending=False)
                
                st.markdown("### 🎯 Matriz de Performance - Desenvolvedores")
                
                with st.expander("📊 **Como é calculada a Matriz de Performance?**", expanded=False):
                    st.markdown("""
                    **Fórmulas de Cálculo:**
                    1. **Eficiência** = Total de Cards / Número de Meses Ativos
                    2. **Qualidade** = (Cards sem Revisão / Total de Cards) × 100
                    3. **Score** = (Qualidade × 0.5) + (Eficiência × 5 × 0.3) + ((Total_Cards / Total_Geral) × 100 × 0.2)
                    """)
                
                matriz_df = criar_matriz_performance_dev(df_perf)
                
                if not matriz_df.empty:
                    matriz_filtrada = matriz_df.copy()
                    
                    if not matriz_filtrada.empty:
                        media_eficiencia = matriz_filtrada['Eficiencia'].mean()
                        media_qualidade = matriz_filtrada['Qualidade'].mean()
                        
                        def classificar_quadrante(row):
                            if row['Eficiencia'] >= media_eficiencia and row['Qualidade'] >= media_qualidade:
                                return "⭐ Estrelas"
                            elif row['Eficiencia'] >= media_eficiencia and row['Qualidade'] < media_qualidade:
                                return "⚡ Eficientes"
                            elif row['Eficiencia'] < media_eficiencia and row['Qualidade'] >= media_qualidade:
                                return "🎯 Cuidadosos"
                            else:
                                return "🔄 Necessita Apoio"
                        
                        matriz_filtrada['Quadrante'] = matriz_filtrada.apply(classificar_quadrante, axis=1)
                        
                        num_devs = len(matriz_filtrada)
                        colors_scatter = []
                        for i in range(num_devs):
                            pos_normalizada = i / max(num_devs - 1, 1)
                            red = int(220 * pos_normalizada + 40 * (1 - pos_normalizada))
                            green = int(53 * pos_normalizada + 167 * (1 - pos_normalizada))
                            blue = int(69 * pos_normalizada + 69 * (1 - pos_normalizada))
                            colors_scatter.append(f'rgb({red}, {green}, {blue})')
                        
                        fig_matriz = px.scatter(
                            matriz_filtrada,
                            x='Eficiencia',
                            y='Qualidade',
                            size='Score',
                            color=colors_scatter,
                            hover_name='Desenvolvedor',
                            title='Matriz de Performance: Eficiência vs Qualidade',
                            labels={
                                'Eficiencia': 'Eficiência (Cards/Mês)',
                                'Qualidade': 'Qualidade (% Aprovação sem Revisão)',
                                'Score': 'Score Performance'
                            },
                            size_max=30
                        )
                        
                        fig_matriz.update_traces(showlegend=False)
                        
                        fig_matriz.add_shape(
                            type="line",
                            x0=media_eficiencia,
                            y0=matriz_filtrada['Qualidade'].min(),
                            x1=media_eficiencia,
                            y1=matriz_filtrada['Qualidade'].max(),
                            line=dict(color="gray", width=1, dash="dash")
                        )
                        
                        fig_matriz.add_shape(
                            type="line",
                            x0=matriz_filtrada['Eficiencia'].min(),
                            y0=media_qualidade,
                            x1=matriz_filtrada['Eficiencia'].max(),
                            y1=media_qualidade,
                            line=dict(color="gray", width=1, dash="dash")
                        )
                        
                        fig_matriz.add_annotation(
                            x=media_eficiencia + (matriz_filtrada['Eficiencia'].max() - media_eficiencia) * 0.5,
                            y=media_qualidade + (matriz_filtrada['Qualidade'].max() - media_qualidade) * 0.5,
                            text="⭐ Estrelas",
                            showarrow=False,
                            font=dict(size=12, color="#28a745")
                        )
                        
                        fig_matriz.add_annotation(
                            x=media_eficiencia + (matriz_filtrada['Eficiencia'].max() - media_eficiencia) * 0.5,
                            y=media_qualidade - (media_qualidade - matriz_filtrada['Qualidade'].min()) * 0.5,
                            text="⚡ Eficientes",
                            showarrow=False,
                            font=dict(size=12, color="#ffc107")
                        )
                        
                        fig_matriz.add_annotation(
                            x=media_eficiencia - (media_eficiencia - matriz_filtrada['Eficiencia'].min()) * 0.5,
                            y=media_qualidade + (matriz_filtrada['Qualidade'].max() - media_qualidade) * 0.5,
                            text="🎯 Cuidadosos",
                            showarrow=False,
                            font=dict(size=12, color="#007bff")
                        )
                        
                        fig_matriz.add_annotation(
                            x=media_eficiencia - (media_eficiencia - matriz_filtrada['Eficiencia'].min()) * 0.5,
                            y=media_qualidade - (media_qualidade - matriz_filtrada['Qualidade'].min()) * 0.5,
                            text="🔄 Necessita Apoio",
                            showarrow=False,
                            font=dict(size=12, color="#dc3545")
                        )
                        
                        fig_matriz.update_layout(
                            height=500,
                            xaxis_title="Eficiência (Cards por Mês)",
                            yaxis_title="Qualidade (% de Aprovação sem Revisão)",
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig_matriz, use_container_width=True)
                        
                        st.markdown("#### 📋 Classificação por Quadrante")
                        
                        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
                        
                        quadrantes_count = matriz_filtrada['Quadrante'].value_counts()
                        
                        if '⭐ Estrelas' in quadrantes_count:
                            with col_q1:
                                count = quadrantes_count['⭐ Estrelas']
                                st.markdown(f"""
                                <div class="matrix-quadrant quadrant-stars">
                                    ⭐ Estrelas<br>
                                    <span style="font-size: 1.5rem;">{count}</span> DEVs
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if '⚡ Eficientes' in quadrantes_count:
                            with col_q2:
                                count = quadrantes_count['⚡ Eficientes']
                                st.markdown(f"""
                                <div class="matrix-quadrant quadrant-efficient">
                                    ⚡ Eficientes<br>
                                    <span style="font-size: 1.5rem;">{count}</span> DEVs
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if '🎯 Cuidadosos' in quadrantes_count:
                            with col_q3:
                                count = quadrantes_count['🎯 Cuidadosos']
                                st.markdown(f"""
                                <div class="matrix-quadrant quadrant-careful">
                                    🎯 Cuidadosos<br>
                                    <span style="font-size: 1.5rem;">{count}</span> DEVs
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if '🔄 Necessita Apoio' in quadrantes_count:
                            with col_q4:
                                count = quadrantes_count['🔄 Necessita Apoio']
                                st.markdown(f"""
                                <div class="matrix-quadrant quadrant-needs-help">
                                    🔄 Necessita Apoio<br>
                                    <span style="font-size: 1.5rem;">{count}</span> DEVs
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.markdown("### 💡 Recomendações Personalizadas")
                        
                        devs_recom = sorted(df_perf['Responsável_Formatado'].dropna().unique())
                        
                        if devs_recom:
                            dev_recom_selecionado = st.selectbox(
                                "Selecione o Desenvolvedor para recomendações:",
                                options=devs_recom,
                                key="dev_recomendacoes"
                            )
                            
                            recomendacoes = gerar_recomendacoes_dev(df_perf, dev_recom_selecionado)
                            
                            if recomendacoes:
                                with st.expander(f"📋 Ver Recomendações para {dev_recom_selecionado}", expanded=False):
                                    for rec in recomendacoes:
                                        if rec['prioridade'] == 'ALTA':
                                            cor_card = "warning-card"
                                            emoji = "🔴"
                                        elif rec['prioridade'] == 'MÉDIA':
                                            cor_card = "info-card"
                                            emoji = "🟡"
                                        else:
                                            cor_card = "performance-card"
                                            emoji = "🟢"
                                        
                                        st.markdown(f"""
                                        <div class="{cor_card} card-base" style="margin-bottom: 15px;">
                                            <div style="display: flex; align-items: start; gap: 10px;">
                                                <span style="font-size: 1.5rem;">{emoji}</span>
                                                <div>
                                                    <h4 style="margin: 0;">{rec['titulo']}</h4>
                                                    <p style="margin: 5px 0; color: #6c757d;">{rec['descricao']}</p>
                                                    <p style="margin: 0; font-weight: 600;">Ação sugerida: {rec['acao']}</p>
                                                </div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    if st.button("📋 Ver Plano de Ação Completo", key="btn_plano_acao"):
                                        st.markdown("#### 🚀 Plano de Ação Sugerido")
                                        acoes = [
                                            "1. Implementar checklist padronizado antes do envio",
                                            "2. Realizar code review com desenvolvedores experientes",
                                            "3. Estabelecer metas de qualidade por desenvolvedor",
                                            "4. Criar banco de conhecimento com erros comuns",
                                            "5. Implementar sistema de feedback contínuo com SREs"
                                        ]
                                        
                                        for acao in acoes:
                                            st.markdown(f"""
                                            <div style="padding: 10px; margin-bottom: 5px; background: #f8f9fa; border-radius: 5px;">
                                                {acao}
                                            </div>
                                            """, unsafe_allow_html=True)
                            else:
                                st.success(f"✅ {dev_recom_selecionado} está com excelente performance!")
                
                st.markdown(f"### 🏆 Top 10 Desenvolvedores ({ordenar_por})")
                
                if ordenar_por == "Score de Qualidade":
                    top10_score = df_dev_metrics.head(10)
                    
                    fig_score = px.bar(
                        top10_score,
                        y='Desenvolvedor',
                        x='Score Qualidade',
                        orientation='h',
                        title='Top 10 - Score de Qualidade',
                        text='Score Qualidade',
                        color='Score Qualidade',
                        color_continuous_scale='RdYlGn',
                        range_color=[0, 100]
                    )
                    
                    fig_score.update_traces(
                        texttemplate='%{text:.1f}%',
                        textposition='outside',
                        marker_line_color='black',
                        marker_line_width=0.5
                    )
                    
                    fig_score.update_layout(
                        height=500,
                        plot_bgcolor='white',
                        yaxis={'categoryorder': 'total ascending'},
                        xaxis_title="Score de Qualidade (%)",
                        yaxis_title="Desenvolvedor",
                        xaxis_range=[0, 100]
                    )
                    
                    st.plotly_chart(fig_score, use_container_width=True)
                    
                else:
                    top10_other = df_dev_metrics.head(10)
                    
                    if ordenar_por == "Total de Chamados":
                        col_ordenada = 'Total Chamados'
                        color_scale = 'Blues'
                        titulo = 'Top 10 - Total de Chamados'
                    elif ordenar_por == "Eficiência":
                        col_ordenada = 'Eficiência'
                        color_scale = 'Greens'
                        titulo = 'Top 10 - Eficiência'
                    else:
                        col_ordenada = 'Produtividade'
                        color_scale = 'Purples'
                        titulo = 'Top 10 - Produtividade'
                    
                    fig_other = px.bar(
                        top10_other,
                        x='Desenvolvedor',
                        y=col_ordenada,
                        title=titulo,
                        text=col_ordenada,
                        color=col_ordenada,
                        color_continuous_scale=color_scale
                    )
                    
                    if ordenar_por in ["Score de Qualidade", "Eficiência"]:
                        fig_other.update_traces(texttemplate='%{text:.1f}%')
                    else:
                        fig_other.update_traces(texttemplate='%{text:.1f}')
                    
                    fig_other.update_traces(
                        textposition='outside',
                        marker_line_color='black',
                        marker_line_width=0.5
                    )
                    
                    fig_other.update_layout(
                        height=500,
                        plot_bgcolor='white',
                        xaxis_title="Desenvolvedor",
                        yaxis_title=ordenar_por,
                        xaxis_tickangle=45
                    )
                    
                    st.plotly_chart(fig_other, use_container_width=True)
                
                st.markdown("### 📋 Performance Detalhada")
                st.dataframe(
                    df_dev_metrics,
                    use_container_width=True,
                    height=400,
                    column_config={
                        "Desenvolvedor": st.column_config.TextColumn("Desenvolvedor", width="medium"),
                        "Total Chamados": st.column_config.NumberColumn("Total", format="%d"),
                        "Sem Revisão": st.column_config.NumberColumn("Sem Rev.", format="%d"),
                        "Score Qualidade": st.column_config.NumberColumn("Score %", format="%.1f%%"),
                        "Sincronizados": st.column_config.NumberColumn("Sinc.", format="%d"),
                        "Eficiência": st.column_config.NumberColumn("Efic. %", format="%.1f%%"),
                        "Produtividade": st.column_config.Number_config.NumberColumn("Prod./Mês", format="%.1f"),
                        "Classificação": st.column_config.TextColumn("Classif.")
                    }
                )
            else:
                st.info("Nenhum desenvolvedor encontrado com os critérios selecionados.")
    
    with tab_extra2:
        with st.expander("ℹ️ **SOBRE ESTA ANÁLISE**", expanded=False):
            st.markdown("""
            **Análise de Sazonalidade e Padrões Temporais**
            """)
        
        if 'Criado' in df_uso.columns and 'Status' in df_uso.columns:
            col_saz_filtro1, col_saz_filtro2, col_saz_filtro3 = st.columns(3)
            
            with col_saz_filtro1:
                anos_saz = sorted(df_uso['Ano'].dropna().unique().astype(int))
                anos_opcoes_saz = ['Todos os Anos'] + list(anos_saz)
                ano_saz = st.selectbox(
                    "Selecionar Ano:",
                    options=anos_opcoes_saz,
                    index=len(anos_opcoes_saz)-1,
                    key="ano_saz"
                )
            
            with col_saz_filtro2:
                if ano_saz != 'Todos os Anos':
                    meses_ano = df_uso[df_uso['Ano'] == int(ano_saz)]['Mês'].unique()
                    meses_opcoes = ['Todos os Meses'] + sorted([str(int(m)) for m in meses_ano])
                    mes_saz = st.selectbox(
                        "Selecionar Mês:",
                        options=meses_opcoes,
                        key="mes_saz"
                    )
                else:
                    mes_saz = 'Todos os Meses'
            
            with col_saz_filtro3:
                tipo_analise = st.selectbox(
                    "Tipo de Análise:",
                    options=["Demandas Totais", "Apenas Sincronizados", "Comparativo"],
                    index=0
                )
            
            df_saz = df_uso.copy()
            
            if ano_saz != 'Todos os Anos':
                df_saz = df_saz[df_saz['Ano'] == int(ano_saz)]
            
            if mes_saz != 'Todos os Meses':
                df_saz = df_saz[df_saz['Mês'] == int(mes_saz)]
            
            st.markdown("### 📅 Padrões por Dia da Semana")
            
            df_saz['Dia_Semana'] = df_saz['Criado'].dt.day_name()
            df_saz['Dia_Semana_PT'] = df_saz['Dia_Semana'].map(DIAS_MAPPING)
            
            col_dia1, col_dia2 = st.columns(2)
            
            with col_dia1:
                demanda_dia = df_saz['Dia_Semana_PT'].value_counts().reindex(DIAS_SEMANA_PT).reset_index()
                demanda_dia.columns = ['Dia', 'Total_Demandas']
                
                sinc_dia = df_saz[df_saz['Status'] == 'Sincronizado']['Dia_Semana_PT'].value_counts().reindex(DIAS_SEMANA_PT).reset_index()
                sinc_dia.columns = ['Dia', 'Sincronizados']
                
                dados_dia = pd.merge(demanda_dia, sinc_dia, on='Dia', how='left').fillna(0)
                dados_dia['Taxa_Sinc'] = (dados_dia['Sincronizados'] / dados_dia['Total_Demandas'] * 100).round(1)
                
                fig_dias = go.Figure()
                
                fig_dias.add_trace(go.Bar(
                    x=dados_dia['Dia'],
                    y=dados_dia['Total_Demandas'],
                    name='Total Demandas',
                    marker_color='#1e3799',
                    text=dados_dia['Total_Demandas'],
                    textposition='auto'
                ))
                
                fig_dias.add_trace(go.Bar(
                    x=dados_dia['Dia'],
                    y=dados_dia['Sincronizados'],
                    name='Sincronizados',
                    marker_color='#28a745',
                    text=dados_dia['Sincronizados'],
                    textposition='auto'
                ))
                
                fig_dias.add_trace(go.Scatter(
                    x=dados_dia['Dia'],
                    y=dados_dia['Taxa_Sinc'],
                    name='Taxa Sinc (%)',
                    yaxis='y2',
                    mode='lines+markers',
                    line=dict(color='#dc3545', width=3),
                    marker=dict(size=8)
                ))
                
                fig_dias.update_layout(
                    title='Demandas e Sincronizações por Dia da Semana',
                    barmode='group',
                    yaxis=dict(title='Quantidade'),
                    yaxis2=dict(
                        title='Taxa Sinc (%)',
                        overlaying='y',
                        side='right',
                        range=[0, 100]
                    ),
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig_dias, use_container_width=True)
            
            with col_dia2:
                st.markdown("### 🕐 Demandas por Hora do Dia")
                
                col_hora_filtro1, col_hora_filtro2 = st.columns(2)
                
                with col_hora_filtro1:
                    anos_hora = sorted(df_uso['Ano'].dropna().unique().astype(int))
                    anos_opcoes_hora = ['Todos os Anos'] + list(anos_hora)
                    ano_hora = st.selectbox(
                        "Ano para análise horária:",
                        options=anos_opcoes_hora,
                        index=len(anos_opcoes_hora)-1,
                        key="ano_hora"
                    )
                
                with col_hora_filtro2:
                    if ano_hora != 'Todos os Anos':
                        meses_hora = df_uso[df_uso['Ano'] == int(ano_hora)]['Mês'].unique()
                        meses_opcoes_hora = ['Todos os Meses'] + sorted([str(int(m)) for m in meses_hora])
                        mes_hora = st.selectbox(
                            "Mês para análise horária:",
                            options=meses_opcoes_hora,
                            key="mes_hora"
                        )
                    else:
                        mes_hora = 'Todos os Meses'
                
                df_hora = df_uso.copy()
                
                if ano_hora != 'Todos os Anos':
                    df_hora = df_hora[df_hora['Ano'] == int(ano_hora)]
                
                if mes_hora != 'Todos os Meses':
                    df_hora = df_hora[df_hora['Mês'] == int(mes_hora)]
                
                subtitulo_hora = "Análise por Hora"
                if ano_hora != 'Todos os Anos':
                    subtitulo_hora += f" - {ano_hora}"
                if mes_hora != 'Todos os Meses':
                    subtitulo_hora += f" - {MESES_COMPLETOS[int(mes_hora)]}"
                
                st.markdown(f"**Período:** {subtitulo_hora}")
                
                df_hora['Hora'] = df_hora['Criado'].dt.hour
                
                demanda_hora = df_hora['Hora'].value_counts().sort_index().reset_index()
                demanda_hora.columns = ['Hora', 'Total_Demandas']
                
                sinc_hora = df_hora[df_hora['Status'] == 'Sincronizado']['Hora'].value_counts().sort_index().reset_index()
                sinc_hora.columns = ['Hora', 'Sincronizados']
                
                dados_hora = pd.merge(demanda_hora, sinc_hora, on='Hora', how='left').fillna(0)
                dados_hora['Taxa_Sinc'] = (dados_hora['Sincronizados'] / dados_hora['Total_Demandas'] * 100).where(dados_hora['Total_Demandas'] > 0, 0).round(1)
                
                fig_horas = go.Figure()
                
                fig_horas.add_trace(go.Scatter(
                    x=dados_hora['Hora'],
                    y=dados_hora['Total_Demandas'],
                    name='Total Demandas',
                    mode='lines+markers',
                    line=dict(color='#1e3799', width=3),
                    marker=dict(size=8)
                ))
                
                fig_horas.add_trace(go.Scatter(
                    x=dados_hora['Hora'],
                    y=dados_hora['Sincronizados'],
                    name='Sincronizados',
                    mode='lines+markers',
                    line=dict(color='#28a745', width=3),
                    marker=dict(size=8)
                ))
                
                if not dados_hora.empty:
                    pico_demanda = dados_hora.loc[dados_hora['Total_Demandas'].idxmax()]
                    pico_sinc = dados_hora.loc[dados_hora['Sincronizados'].idxmax()]
                    
                    hora_pico_demanda = f"{int(pico_demanda['Hora'])}:00h"
                    hora_pico_sinc = f"{int(pico_sinc['Hora'])}:00h"
                    
                    fig_horas.add_annotation(
                        x=pico_demanda['Hora'],
                        y=pico_demanda['Total_Demandas'],
                        text=f"Pico Demandas: {int(pico_demanda['Total_Demandas'])}<br>{hora_pico_demanda}",
                        showarrow=True,
                        arrowhead=2,
                        ax=0,
                        ay=-40,
                        bgcolor="white",
                        bordercolor="black"
                    )
                    
                    fig_horas.add_annotation(
                        x=pico_sinc['Hora'],
                        y=pico_sinc['Sincronizados'],
                        text=f"Pico Sinc: {int(pico_sinc['Sincronizados'])}<br>{hora_pico_sinc}",
                        showarrow=True,
                        arrowhead=2,
                        ax=0,
                        ay=40,
                        bgcolor="white",
                        bordercolor="green"
                    )
                
                fig_horas.update_layout(
                    title=f'Demandas por Hora do Dia - {subtitulo_hora}',
                    xaxis_title='Hora do Dia',
                    yaxis_title='Quantidade',
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig_horas, use_container_width=True)
                
                if not dados_hora.empty:
                    col_hora_stats1, col_hora_stats2, col_hora_stats3 = st.columns(3)
                    
                    with col_hora_stats1:
                        hora_pico_demanda = dados_hora.loc[dados_hora['Total_Demandas'].idxmax()]
                        hora_formatada = f"{int(hora_pico_demanda['Hora'])}:00h"
                        st.metric("🕐 Pico de Demandas", 
                                 hora_formatada, 
                                 f"{int(hora_pico_demanda['Total_Demandas'])} demandas")
                    
                    with col_hora_stats2:
                        hora_pico_sinc = dados_hora.loc[dados_hora['Sincronizados'].idxmax()]
                        hora_sinc_formatada = f"{int(hora_pico_sinc['Hora'])}:00h"
                        st.metric("✅ Pico de Sincronizações", 
                                 hora_sinc_formatada, 
                                 f"{int(hora_pico_sinc['Sincronizados'])} sinc.")
                    
                    with col_hora_stats3:
                        melhor_taxa_hora = dados_hora.loc[dados_hora['Taxa_Sinc'].idxmax()]
                        hora_taxa_formatada = f"{int(melhor_taxa_hora['Hora'])}:00h"
                        st.metric("🏆 Melhor Taxa Sinc.", 
                                 hora_taxa_formatada, 
                                 f"{melhor_taxa_hora['Taxa_Sinc']}%")
            
            st.markdown("### 📈 Sazonalidade Mensal")
            
            col_saz_mes1, col_saz_mes2 = st.columns(2)
            
            with col_saz_mes1:
                anos_saz_mes = sorted(df_uso['Ano'].dropna().unique().astype(int))
                anos_opcoes_saz_mes = ['Todos os Anos'] + list(anos_saz_mes)
                ano_saz_mes = st.selectbox(
                    "Selecionar Ano para análise mensal:",
                    options=anos_opcoes_saz_mes,
                    index=len(anos_opcoes_saz_mes)-1,
                    key="ano_saz_mes"
                )
            
            with col_saz_mes2:
                if ano_saz_mes != 'Todos os Anos':
                    st.markdown(f"**Ano selecionado:** {ano_saz_mes}")
                else:
                    st.markdown("**Todos os anos**")
            
            if ano_saz_mes != 'Todos os Anos':
                df_saz_mes = df_uso[df_uso['Ano'] == int(ano_saz_mes)].copy()
            else:
                df_saz_mes = df_uso.copy()
            
            if not df_saz_mes.empty:
                if 'Nome_Mês' in df_saz_mes.columns:
                    df_saz_mes['Mês_Abrev'] = df_saz_mes['Nome_Mês']
                else:
                    df_saz_mes['Mês_Abrev'] = df_saz_mes['Criado'].dt.month.map(MESES_ABREVIADOS)
                
                demanda_mes = df_saz_mes.groupby('Mês_Abrev').size().reset_index()
                demanda_mes.columns = ['Mês', 'Total']
                
                demanda_mes = demanda_mes.set_index('Mês').reindex(ORDEM_MESES).reset_index()
                demanda_mes['Total'] = demanda_mes['Total'].fillna(0).astype(int)
                
                sinc_mes = df_saz_mes[df_saz_mes['Status'] == 'Sincronizado'].groupby('Mês_Abrev').size().reset_index()
                sinc_mes.columns = ['Mês', 'Sincronizados']
                
                sinc_mes = sinc_mes.set_index('Mês').reindex(ORDEM_MESES).reset_index()
                sinc_mes['Sincronizados'] = sinc_mes['Sincronizados'].fillna(0).astype(int)
                
                dados_mes = pd.merge(demanda_mes, sinc_mes, on='Mês', how='left').fillna(0)
                dados_mes['Taxa_Sinc'] = (dados_mes['Sincronizados'] / dados_mes['Total'] * 100).where(dados_mes['Total'] > 0, 0).round(1)
                
                titulo_grafico = f'Distribuição Mensal'
                if ano_saz_mes != 'Todos os Anos':
                    titulo_grafico += f' - {ano_saz_mes}'
                
                fig_mes_saz = go.Figure()
                
                fig_mes_saz.add_trace(go.Bar(
                    x=dados_mes['Mês'],
                    y=dados_mes['Total'],
                    name='Total Demandas',
                    marker_color='#1e3799',
                    text=dados_mes['Total'],
                    textposition='auto'
                ))
                
                fig_mes_saz.add_trace(go.Bar(
                    x=dados_mes['Mês'],
                    y=dados_mes['Sincronizados'],
                    name='Sincronizados',
                    marker_color='#28a745',
                    text=dados_mes['Sincronizados'],
                    textposition='auto'
                ))
                
                fig_mes_saz.add_trace(go.Scatter(
                    x=dados_mes['Mês'],
                    y=dados_mes['Taxa_Sinc'],
                    name='Taxa Sinc (%)',
                    yaxis='y2',
                    mode='lines+markers',
                    line=dict(color='#dc3545', width=3),
                    marker=dict(size=8)
                ))
                
                fig_mes_saz.update_layout(
                    title=titulo_grafico,
                    barmode='group',
                    yaxis=dict(title='Quantidade'),
                    yaxis2=dict(
                        title='Taxa Sinc (%)',
                        overlaying='y',
                        side='right',
                        range=[0, 100]
                    ),
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig_mes_saz, use_container_width=True)
                
                col_pico1, col_pico2, col_pico3 = st.columns(3)
                
                with col_pico1:
                    mes_maior_demanda = dados_mes.loc[dados_mes['Total'].idxmax()]
                    st.metric("📈 Mês com mais demandas", 
                             f"{MESES_COMPLETOS.get(list(MESES_ABREVIADOS.keys())[list(MESES_ABREVIADOS.values()).index(mes_maior_demanda['Mês'])], mes_maior_demanda['Mês'])}: {int(mes_maior_demanda['Total'])}")
                
                with col_pico2:
                    mes_maior_sinc = dados_mes.loc[dados_mes['Sincronizados'].idxmax()]
                    st.metric("✅ Mês com mais sincronizações", 
                             f"{MESES_COMPLETOS.get(list(MESES_ABREVIADOS.keys())[list(MESES_ABREVIADOS.values()).index(mes_maior_sinc['Mês'])], mes_maior_sinc['Mês'])}: {int(mes_maior_sinc['Sincronizados'])}")
                
                with col_pico3:
                    melhor_taxa = dados_mes.loc[dados_mes['Taxa_Sinc'].idxmax()]
                    st.metric("🏆 Melhor taxa de sincronização", 
                             f"{MESES_COMPLETOS.get(list(MESES_ABREVIADOS.keys())[list(MESES_ABREVIADOS.values()).index(melhor_taxa['Mês'])], melhor_taxa['Mês'])}: {melhor_taxa['Taxa_Sinc']}%")
    
    with tab_extra3:
        with st.expander("ℹ️ **SOBRE ESTA ANÁLISE**", expanded=False):
            st.markdown("""
            **Análise Avançada de Erros**
            """)
        
        if 'Tipo_Chamado' in df_uso.columns:
            col_diag1, col_diag2, col_diag3 = st.columns(3)
            
            with col_diag1:
                anos_diag = sorted(df_uso['Ano'].dropna().unique().astype(int))
                anos_opcoes_diag = ['Todos os Anos'] + list(anos_diag)
                ano_diag = st.selectbox(
                    "Selecionar Ano:",
                    options=anos_opcoes_diag,
                    index=len(anos_opcoes_diag)-1,
                    key="ano_diag"
                )
            
            with col_diag2:
                if ano_diag != 'Todos os Anos':
                    meses_diag = df_uso[df_uso['Ano'] == int(ano_diag)]['Mês'].unique()
                    meses_opcoes_diag = ['Todos os Meses'] + sorted([str(int(m)) for m in meses_diag])
                    mes_diag = st.selectbox(
                        "Selecionar Mês:",
                        options=meses_opcoes_diag,
                        key="mes_diag"
                    )
                else:
                    mes_diag = 'Todos os Meses'
            
            with col_diag3:
                tipo_analise_diag = st.selectbox(
                    "Foco da Análise:",
                    options=["Tipos de Erro", "Tendências Temporais", "Impacto nos SREs", "Recomendações"],
                    index=0
                )
            
            df_diag = df_uso.copy()
            
            if ano_diag != 'Todos os Anos':
                df_diag = df_diag[df_diag['Ano'] == int(ano_diag)]
            
            if mes_diag != 'Todos os Meses':
                df_diag = df_diag[df_diag['Mês'] == int(mes_diag)]
            
            if tipo_analise_diag == "Tipos de Erro":
                st.markdown("### 🔍 Análise de Tipos de Erro")
                
                tipos_erro = df_diag['Tipo_Chamado'].value_counts().reset_index()
                tipos_erro.columns = ['Tipo', 'Frequência']
                tipos_erro['Percentual'] = (tipos_erro['Frequência'] / len(df_diag) * 100).round(1)
                
                col_tipo1, col_tipo2 = st.columns([2, 1])
                
                with col_tipo1:
                    fig_pizza = px.pie(
                        tipos_erro.head(10),
                        values='Frequência',
                        names='Tipo',
                        title='Distribuição dos 10 Tipos Mais Frequentes',
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.RdBu
                    )
                    
                    fig_pizza.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hoverinfo='label+percent+value'
                    )
                    
                    st.plotly_chart(fig_pizza, use_container_width=True)
                
                with col_tipo2:
                    st.markdown("### 📊 Top 5 Tipos")
                    
                    for idx, row in tipos_erro.head(5).iterrows():
                        st.markdown(f"""
                        <div class="{'warning-card' if row['Percentual'] > 10 else 'info-card'} card-base" style="margin-bottom: 10px;">
                            <strong>{row['Tipo']}</strong><br>
                            <small>Frequência: {row['Frequência']}</small><br>
                            <small>Percentual: {row['Percentual']}%</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                if 'Revisões' in df_diag.columns:
                    st.markdown("### ⚠️ Análise de Severidade")
                    
                    severidade = df_diag.groupby('Tipo_Chamado').agg({
                        'Revisões': ['mean', 'max', 'sum'],
                        'Chamado': 'count'
                    }).round(2)
                    
                    severidade.columns = ['Média_Revisões', 'Max_Revisões', 'Total_Revisões', 'Contagem']
                    severidade = severidade.sort_values('Média_Revisões', ascending=False)
                    
                    severidade['Severidade'] = pd.qcut(
                        severidade['Média_Revisões'],
                        q=3,
                        labels=['Baixa', 'Média', 'Alta']
                    )
                    
                    st.dataframe(
                        severidade.head(10),
                        use_container_width=True,
                        column_config={
                            "Média_Revisões": st.column_config.NumberColumn("Média Rev.", format="%.1f"),
                            "Max_Revisões": st.column_config.NumberColumn("Máx. Rev.", format="%d"),
                            "Total_Revisões": st.column_config.NumberColumn("Total Rev.", format="%d"),
                            "Contagem": st.column_config.NumberColumn("Qtd Chamados", format="%d"),
                            "Severidade": st.column_config.TextColumn("Nível Severidade")
                        }
                    )
            
            elif tipo_analise_diag == "Tendências Temporales":
                st.markdown("### 📈 Tendências Temporais de Erros")
                
                if 'Criado' in df_diag.columns:
                    df_diag['Mes_Ano'] = df_diag['Criado'].dt.strftime('%Y-%m')
                    
                    evolucao = df_diag.groupby(['Mes_Ano', 'Tipo_Chamado']).size().reset_index()
                    evolucao.columns = ['Mês_Ano', 'Tipo', 'Quantidade']
                    
                    top_tipos = df_diag['Tipo_Chamado'].value_counts().head(5).index.tolist()
                    evol_top = evolucao[evolucao['Tipo'].isin(top_tipos)]
                    
                    fig_tendencia = px.line(
                        evol_top,
                        x='Mês_Ano',
                        y='Quantidade',
                        color='Tipo',
                        title='Evolução dos Tipos Mais Frequentes',
                        markers=True,
                        line_shape='spline'
                    )
                    
                    fig_tendencia.update_layout(
                        height=400,
                        xaxis_title="Mês/Ano",
                        yaxis_title="Quantidade de Ocorrências",
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_tendencia, use_container_width=True)
                    
                    st.markdown("### 🔍 Detecção de Tendências")
                    
                    tendencias = []
                    for tipo in top_tipos:
                        tipo_data = evol_top[evol_top['Tipo'] == tipo].sort_values('Mês_Ano')
                        if len(tipo_data) > 1:
                            crescimento = ((tipo_data['Quantidade'].iloc[-1] - tipo_data['Quantidade'].iloc[0]) / 
                                         tipo_data['Quantidade'].iloc[0] * 100)
                            
                            if crescimento > 20:
                                status = "📈 Crescimento Acelerado"
                                cor = "danger"
                            elif crescimento > 0:
                                status = "↗️ Crescimento Moderado"
                                cor = "warning"
                            elif crescimento < -20:
                                status = "📉 Redução Significativa"
                                cor = "success"
                            else:
                                status = "➡️ Estável"
                                cor = "info"
                            
                            tendencias.append({
                                'Tipo': tipo,
                                'Crescimento': f"{crescimento:.1f}%",
                                'Status': status,
                                'Tendência': cor
                            })
                    
                    if tendencias:
                        df_tendencias = pd.DataFrame(tendencias)
                        st.dataframe(
                            df_tendencias,
                            use_container_width=True,
                            column_config={
                                "Tipo": st.column_config.TextColumn("Tipo de Erro"),
                                "Crescimento": st.column_config.TextColumn("Variação"),
                                "Status": st.column_config.TextColumn("Análise"),
                                "Tendência": st.column_config.TextColumn("Tendência")
                            }
                        )
            
            elif tipo_analise_diag == "Impacto nos SREs":
                st.markdown("### 👥 Impacto nos SREs")
                
                if 'SRE' in df_diag.columns and 'Revisões' in df_diag.columns:
                    impacto_sre = df_diag.groupby('SRE').agg({
                        'Tipo_Chamado': lambda x: x.value_counts().index[0] if len(x) > 0 else 'N/A',
                        'Revisões': ['mean', 'sum'],
                        'Chamado': 'count'
                    }).round(2)
                    
                    impacto_sre.columns = ['Tipo_Mais_Comum', 'Média_Revisões', 'Total_Revisões', 'Qtd_Chamados']
                    impacto_sre = impacto_sre.sort_values('Total_Revisões', ascending=False)
                    
                    col_impacto1, col_impacto2 = st.columns(2)
                    
                    with col_impacto1:
                        fig_impacto = px.bar(
                            impacto_sre.head(10),
                            x=impacto_sre.head(10).index,
                            y='Total_Revisões',
                            title='Total de Revisões por SRE',
                            color='Média_Revisões',
                            color_continuous_scale='Reds',
                            text='Total_Revisões'
                        )
                        
                        fig_impacto.update_layout(
                            height=400,
                            xaxis_title="SRE",
                            yaxis_title="Total de Revisões"
                        )
                        
                        st.plotly_chart(fig_impacto, use_container_width=True)
                    
                    with col_impacto2:
                        st.markdown("### 🎯 Foco de Melhoria")
                        
                        sre_atencao = impacto_sre[
                            (impacto_sre['Média_Revisões'] > impacto_sre['Média_Revisões'].median()) &
                            (impacto_sre['Qtd_Chamados'] > 5)
                        ]
                        
                        if not sre_atencao.empty:
                            for idx, row in sre_atencao.head(3).iterrows():
                                st.markdown(f"""
                                <div class="warning-card card-base">
                                    <strong>⚠️ {idx}</strong><br>
                                    <small>Tipo mais comum: {row['Tipo_Mais_Comum']}</small><br>
                                    <small>Média revisões: {row['Média_Revisões']}</small><br>
                                    <small>Total revisões: {int(row['Total_Revisões'])}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        sre_melhor = impacto_sre[
                            (impacto_sre['Média_Revisões'] < impacto_sre['Média_Revisões'].quantile(0.25)) &
                            (impacto_sre['Qtd_Chamados'] > 5)
                        ]
                        
                        if not sre_melhor.empty:
                            for idx, row in sre_melhor.head(3).iterrows():
                                st.markdown(f"""
                                <div class="performance-card card-base">
                                    <strong>✅ {idx}</strong><br>
                                    <small>Tipo mais comum: {row['Tipo_Mais_Comum']}</small><br>
                                    <small>Média revisões: {row['Média_Revisões']}</small><br>
                                    <small>Total revisões: {int(row['Total_Revisões'])}</small>
                                </div>
                                """, unsafe_allow_html=True)
            
            elif tipo_analise_diag == "Recomendações":
                st.markdown("### 💡 Recomendações Inteligentes")
                
                recomendacoes = []
                
                tipos_frequentes = df_diag['Tipo_Chamado'].value_counts().head(3)
                for tipo, count in tipos_frequentes.items():
                    if count > len(df_diag) * 0.1:
                        recomendacoes.append({
                            'Prioridade': '🔴 ALTA',
                            'Recomendação': f'Investigar causa raiz do tipo "{tipo}"',
                            'Justificativa': f'Responsável por {count} ocorrências ({count/len(df_diag)*100:.1f}% do total)'
                        })
                
                if 'Criado' in df_diag.columns:
                    df_diag['Dia_Semana'] = df_diag['Criado'].dt.day_name()
                    dia_pico = df_diag['Dia_Semana'].value_counts().index[0]
                    
                    recomendacoes.append({
                        'Prioridade': '🟡 MÉDIA',
                        'Recomendação': f'Reforçar equipe às {dia_pico}s',
                        'Justificativa': f'Dia com maior volume de chamados'
                    })
                
                if 'Revisões' in df_diag.columns:
                    media_revisoes = df_diag['Revisões'].mean()
                    if media_revisoes > 2:
                        recomendacoes.append({
                            'Prioridade': '🔴 ALTA',
                            'Recomendação': 'Implementar revisão de código mais rigorosa',
                            'Justificativa': f'Média de {media_revisoes:.1f} revisões por chamado'
                        })
                
                if 'SRE' in df_diag.columns:
                    sre_performance = df_diag.groupby('SRE')['Revisões'].mean()
                    if len(sre_performance) > 0:
                        sre_maior_revisao = sre_performance.idxmax()
                        maior_media = sre_performance.max()
                        
                        if maior_media > 3:
                            recomendacoes.append({
                                'Prioridade': '🟡 MÉDIA',
                                'Recomendação': f'Capacitação específica para {sre_maior_revisao}',
                                'Justificativa': f'Média de {maior_media:.1f} revisões por chamado'
                            })
                
                if recomendacoes:
                    df_recomendacoes = pd.DataFrame(recomendacoes)
                    
                    for idx, row in df_recomendacoes.iterrows():
                        st.markdown(f"""
                        <div class="{ 'warning-card' if 'ALTA' in row['Prioridade'] else 'info-card' if 'MÉDIA' in row['Prioridade'] else 'performance-card'} card-base" 
                                   style="margin-bottom: 15px; padding: 15px;">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div>
                                    <strong style="font-size: 1.1rem;">{row['Prioridade']} - {row['Recomendação']}</strong><br>
                                    <small style="color: #6c757d;">{row['Justificativa']}</small>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("### 🚀 Plano de Ação Sugerido")
                    
                    acoes = [
                        "1. Priorizar investigação dos tipos de erro mais frequentes",
                        "2. Implementar treinamento específico baseado nas análises",
                        "3. Criar checklist de qualidade para reduzir revisões",
                        "4. Estabelecer métricas de acompanhamento mensal",
                        "5. Realizar reuniões de análise de causas raiz semanais"
                    ]
                    
                    for acao in acoes:
                        st.markdown(f"""
                        <div style="padding: 10px; margin-bottom: 8px; background: #f8f9fa; border-radius: 5px; border-left: 3px solid #1e3799;">
                            {acao}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Não foram identificadas recomendações específicas com os filtros atuais.")
    
    # TOP 10 RESPONSÁVEIS
    st.markdown("---")
    col_top, col_dist = st.columns([2, 1])
    
    with col_top:
        st.markdown('<div class="section-title-exec">👥 TOP 10 RESPONSÁVEIS</div>', unsafe_allow_html=True)
        
        if 'Responsável_Formatado' in df_uso.columns:
            top_responsaveis = df_uso['Responsável_Formatado'].value_counts().head(10).reset_index()
            top_responsaveis.columns = ['Responsável', 'Demandas']
            
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
            
            fig_top.update_layout(
                height=500,
                plot_bgcolor='white',
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis_title="Número de Demandas",
                yaxis_title=""
            )
            
            st.plotly_chart(fig_top, use_container_width=True)
    
    with col_dist:
        st.markdown('<div class="section-title-exec">📊 DISTRIBUIÇÃO POR TIPO</div>', unsafe_allow_html=True)
        
        if 'Tipo_Chamado' in df_uso.columns:
            tipos_chamado = df_uso['Tipo_Chamado'].value_counts().reset_index()
            tipos_chamado.columns = ['Tipo', 'Quantidade']
            
            tipos_chamado = tipos_chamado.sort_values('Quantidade', ascending=True)
            
            fig_tipos = px.bar(
                tipos_chamado,
                x='Quantidade',
                y='Tipo',
                orientation='h',
                title='',
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
            
            fig_tipos.update_layout(
                height=500,
                plot_bgcolor='white',
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis_title="Quantidade",
                yaxis_title=""
            )
            
            st.plotly_chart(fig_tipos, use_container_width=True)
    
    # ÚLTIMAS DEMANDAS REGISTRADAS
    st.markdown("---")
    st.markdown('<div class="section-title-exec">🕒 ÚLTIMAS DEMANDAS REGISTRADAS</div>', unsafe_allow_html=True)
    
    if 'Criado' in df_uso.columns:
        filtro_chamado_principal = st.text_input(
            "🔎 Buscar chamado específico:",
            placeholder="Digite o número do chamado...",
            key="filtro_chamado_principal"
        )
        
        col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
        
        with col_filtro1:
            qtd_demandas = st.slider(
                "Número de demandas:",
                min_value=5,
                max_value=50,
                value=15,
                step=5,
                key="slider_demandas"
            )
        
        with col_filtro2:
            ordenar_por = st.selectbox(
                "Ordenar por:",
                options=['Data (Mais Recente)', 'Data (Mais Antiga)', 'Revisões (Maior)', 'Revisões (Menor)'],
                key="select_ordenar"
            )
        
        with col_filtro3:
            mostrar_colunas = st.multiselect(
                "Colunas a mostrar:",
                options=['Chamado', 'Tipo_Chamado', 'Responsável', 'Status', 'Prioridade', 
                        'Revisões', 'Empresa', 'SRE', 'Data', 'Responsável_Formatado'],
                default=['Chamado', 'Tipo_Chamado', 'Responsável_Formatado', 'Status', 'Data'],
                key="select_colunas"
            )
        
        with col_filtro4:
            filtro_chamado_tabela = st.text_input(
                "Filtro adicional:",
                placeholder="Ex: 12345",
                key="input_filtro_chamado"
            )
        
        ultimas_demandas = df_uso.copy()
        
        if filtro_chamado_principal:
            ultimas_demandas = ultimas_demandas[
                ultimas_demandas['Chamado'].astype(str).str.contains(filtro_chamado_principal, na=False)
            ]
        
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
        
        if 'Responsável' in mostrar_colunas and 'Responsável' in ultimas_demandas.columns:
            display_data['Responsável'] = ultimas_demandas['Responsável']
        
        if 'Responsável_Formatado' in mostrar_colunas and 'Responsável_Formatado' in ultimas_demandas.columns:
            display_data['Responsável Formatado'] = ultimas_demandas['Responsável_Formatado']
        
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
            st.dataframe(
                display_data,
                use_container_width=True,
                height=400
            )
            
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
            st.info("Nenhum resultado encontrado com os filtros aplicados.")

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
        Versão 5.5 | Sistema de Performance SRE | Última atualização: {ultima_atualizacao} (Brasília)
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Finalizar com limpeza
gc.collect()
