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
# Cores principais
COR_VERDE_ESCURO = "#2E7D32"      # Verde escuro - principal
COR_AZUL_PETROLEO = "#028a9f"     # Azul petróleo - secundário
COR_AZUL_ESCURO = "#005973"       # Azul escuro - destaque
COR_LARANJA = "#F57C00"           # Laranja - alertas/positivo
COR_VERMELHO = "#C62828"          # Vermelho - erros/negativo

# Cores neutras
COR_CINZA_FUNDO = "#F8F9FA"       # Cinza muito claro para fundos
COR_CINZA_BORDA = "#E9ECEF"       # Cinza para bordas
COR_CINZA_TEXTO = "#6C757D"       # Cinza para textos secundários
COR_BRANCO = "#FFFFFF"            # Branco
COR_PRETO_SUAVE = "#212529"       # Preto suave para textos principais

# Cores para gráficos
CORES_GRADIENTE = [
    COR_VERDE_ESCURO,
    COR_AZUL_PETROLEO,
    COR_AZUL_ESCURO,
    COR_LARANJA,
    COR_VERMELHO,
    "#1E88E5"  # Azul adicional
]

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
# CSS PERSONALIZADO - NOVA PALETA
# ============================================
st.markdown(f"""
<style>
    /* Reset e estilos base */
    .stApp {{
        background-color: {COR_CINZA_FUNDO};
    }}
    
    /* Main header - estilo Monitoring Center */
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
    
    /* Títulos de seção */
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
    
    /* Informações da base */
    .info-base {{
        background: {COR_CINZA_FUNDO};
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {COR_VERDE_ESCURO};
        margin-bottom: 1.5rem;
    }}
    
    /* Rodapé */
    .footer {{
        text-align: center;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 2px solid {COR_CINZA_BORDA};
        color: {COR_CINZA_TEXTO};
        font-size: 0.85rem;
    }}
    
    /* Status cards */
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
    
    /* Cards de performance */
    .performance-card {{
        background: linear-gradient(135deg, {COR_BRANCO}, #F1F8E9);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {COR_VERDE_ESCURO};
        margin-bottom: 1rem;
    }}
    
    .warning-card {{
        background: linear-gradient(135deg, {COR_BRANCO}, #FFF3E0);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {COR_LARANJA};
        margin-bottom: 1rem;
    }}
    
    .alert-card {{
        background: linear-gradient(135deg, {COR_BRANCO}, #FFEBEE);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {COR_VERMELHO};
        margin-bottom: 1rem;
    }}
    
    .info-card {{
        background: linear-gradient(135deg, {COR_BRANCO}, #E0F7FA);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {COR_AZUL_PETROLEO};
        margin-bottom: 1rem;
    }}
    
    /* Botões */
    .stButton > button {{
        background: {COR_AZUL_ESCURO};
        color: {COR_BRANCO};
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        background: {COR_AZUL_PETROLEO};
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 89, 115, 0.3);
    }}
    
    /* Badges e tags */
    .badge-success {{
        background-color: {COR_VERDE_ESCURO};
        color: {COR_BRANCO};
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    
    .badge-warning {{
        background-color: {COR_LARANJA};
        color: {COR_BRANCO};
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    
    .badge-danger {{
        background-color: {COR_VERMELHO};
        color: {COR_BRANCO};
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    
    .badge-info {{
        background-color: {COR_AZUL_PETROLEO};
        color: {COR_BRANCO};
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    
    /* Quadrantes da matriz */
    .matrix-quadrant {{
        padding: 10px;
        border-radius: 8px;
        margin: 5px;
        font-weight: bold;
        text-align: center;
    }}
    
    .quadrant-stars {{
        background-color: #E8F5E9;
        color: {COR_VERDE_ESCURO};
        border: 2px solid {COR_VERDE_ESCURO};
    }}
    
    .quadrant-efficient {{
        background-color: #FFF3E0;
        color: {COR_LARANJA};
        border: 2px solid {COR_LARANJA};
    }}
    
    .quadrant-careful {{
        background-color: #E0F7FA;
        color: {COR_AZUL_PETROLEO};
        border: 2px solid {COR_AZUL_PETROLEO};
    }}
    
    .quadrant-needs-help {{
        background-color: #FFEBEE;
        color: {COR_VERMELHO};
        border: 2px solid {COR_VERMELHO};
    }}
    
    /* Tabelas */
    .dataframe {{
        border-collapse: collapse;
        width: 100%;
    }}
    
    .dataframe th {{
        background-color: {COR_AZUL_ESCURO};
        color: {COR_BRANCO};
        padding: 10px;
        text-align: left;
    }}
    
    .dataframe td {{
        padding: 8px;
        border-bottom: 1px solid {COR_CINZA_BORDA};
    }}
    
    .dataframe tr:hover {{
        background-color: {COR_CINZA_FUNDO};
    }}
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

def calcular_hash_arquivo(conteudo):
    """Calcula hash do conteúdo do arquivo para detectar mudanças"""
    return hashlib.md5(conteudo).hexdigest()

@st.cache_data(ttl=300)
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
            'Revisões': 'Revisões',
            'Motivo Revisão': 'Motivo_Revisao',
            'ChangeSet': 'ChangeSet'  # Adicionando a coluna ChangeSet
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
        timestamp = time.time()
        
        return df, "✅ Dados carregados com sucesso", f"{hash_conteudo}_{timestamp}"
    
    except Exception as e:
        return None, f"Erro: {str(e)}", None

def encontrar_arquivo_dados():
    """Tenta encontrar o arquivo de dados em vários caminhos possíveis"""
    if os.path.exists(CAMINHO_ARQUIVO_PRINCIPAL):
        return CAMINHO_ARQUIVO_PRINCIPAL
    
    for caminho in CAMINHOS_ALTERNATIVOS:
        if os.path.exists(caminho):
            return caminho
    
    return None

def verificar_atualizacao_arquivo():
    """Verifica se o arquivo foi modificado desde a última carga"""
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

def verificar_e_atualizar_arquivo():
    """Verifica se o arquivo local foi modificado e atualiza se necessário"""
    caminho_arquivo = encontrar_arquivo_dados()
    
    if caminho_arquivo and os.path.exists(caminho_arquivo):
        if 'ultima_modificacao' not in st.session_state:
            st.session_state.ultima_modificacao = os.path.getmtime(caminho_arquivo)
            return False
        
        modificacao_atual = os.path.getmtime(caminho_arquivo)
        
        if (modificacao_atual > st.session_state.ultima_modificacao and 
            st.session_state.df_original is not None):
            
            with open(caminho_arquivo, 'rb') as f:
                conteudo_atual = f.read()
            hash_atual = calcular_hash_arquivo(conteudo_atual)
            
            if 'file_hash' not in st.session_state or hash_atual != st.session_state.file_hash:
                st.session_state.ultima_modificacao = modificacao_atual
                return True
        
        st.session_state.ultima_modificacao = modificacao_atual
    
    return False

def limpar_sessao_dados():
    """Limpa todos os dados da sessão relacionados ao upload"""
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
# FUNÇÃO PARA FILTRAR POR SISTEMA (USANDO CHANGESET)
# ============================================
def filtrar_por_sistema(df, sistema_selecionado):
    """
    Filtra o DataFrame baseado no sistema de validação (ADMS/ELIPSE)
    Usando a coluna de ChangeSet
    """
    if sistema_selecionado == 'Todos':
        return df
    
    # Identificar a coluna de ChangeSet
    coluna_changeset = None
    for col in df.columns:
        if 'changeset' in col.lower() or 'change set' in col.lower():
            coluna_changeset = col
            break
    
    if coluna_changeset is None:
        st.warning("⚠️ Coluna de 'ChangeSet' não encontrada no arquivo.")
        return df
    
    df_filtrado = df.copy()
    
    # Normalizar os valores para comparação
    df_filtrado['ChangeSet_Norm'] = df_filtrado[coluna_changeset].astype(str).str.strip().str.upper()
    
    if sistema_selecionado == 'ELIPSE':
        # Para ELIPSE, filtra chamados com ChangeSet = 'ELIPSE'
        df_filtrado = df_filtrado[df_filtrado['ChangeSet_Norm'] == 'ELIPSE']
    elif sistema_selecionado == 'ADMS':
        # Para ADMS, filtra chamados com ChangeSet = 'TELEMETRY' ou 'MANUAL'
        df_filtrado = df_filtrado[
            df_filtrado['ChangeSet_Norm'].isin(['TELEMETRY', 'MANUAL'])
        ]
    
    # Remover coluna auxiliar
    df_filtrado = df_filtrado.drop('ChangeSet_Norm', axis=1)
    
    return df_filtrado

# ============================================
# FUNÇÃO PARA EXIBIR ESTATÍSTICAS COMPARATIVAS (COM TODOS OS GRÁFICOS)
# ============================================
def exibir_estatisticas_por_sistema(df):
    """Exibe estatísticas comparativas entre ADMS e ELIPSE com todos os gráficos"""
    
    # Identificar a coluna de ChangeSet
    coluna_changeset = None
    for col in df.columns:
        if 'changeset' in col.lower() or 'change set' in col.lower():
            coluna_changeset = col
            break
    
    if coluna_changeset is None:
        st.info("ℹ️ Coluna 'ChangeSet' não encontrada para análise comparativa.")
        
        # Mostrar colunas disponíveis para ajudar no debug
        st.markdown("### 📋 Colunas disponíveis no arquivo:")
        st.write(list(df.columns))
        
        # Tentar usar Tipo_Chamado como fallback
        if 'Tipo_Chamado' in df.columns:
            st.warning("⚠️ Usando 'Tipo_Chamado' como fallback para análise.")
            coluna_changeset = 'Tipo_Chamado'
        else:
            return
    
    # Normalizar para comparação
    df_temp = df.copy()
    df_temp['ChangeSet_Norm'] = df_temp[coluna_changeset].astype(str).str.strip().str.upper()
    
    # Separar dados por sistema
    df_elipse = df_temp[df_temp['ChangeSet_Norm'] == 'ELIPSE']
    df_adms = df_temp[df_temp['ChangeSet_Norm'].isin(['TELEMETRY', 'MANUAL'])]
    
    total_elipse = len(df_elipse)
    total_adms = len(df_adms)
    
    # Debug - mostrar quantos registros foram encontrados
    st.info(f"🔍 Encontrados: {total_elipse} registros ELIPSE e {total_adms} registros ADMS")
    
    st.markdown("### 📊 Comparativo ADMS vs ELIPSE")
    
    # MÉTRICAS PRINCIPAIS (CARDS)
    col_comp1, col_comp2, col_comp3, col_comp4 = st.columns(4)
    
    with col_comp1:
        st.metric("📋 ELIPSE", total_elipse, help="ChangeSet do tipo Elipse")
    
    with col_comp2:
        st.metric("📋 ADMS", total_adms, help="ChangeSet do tipo Telemetry e Manual")
    
    with col_comp3:
        sinc_elipse = len(df_elipse[df_elipse['Status'] == 'Sincronizado']) if 'Status' in df_elipse.columns else 0
        pct_elipse = (sinc_elipse / total_elipse * 100) if total_elipse > 0 else 0
        st.metric("✅ Sincronizados ELIPSE", sinc_elipse, f"{pct_elipse:.1f}%")
    
    with col_comp4:
        sinc_adms = len(df_adms[df_adms['Status'] == 'Sincronizado']) if 'Status' in df_adms.columns else 0
        pct_adms = (sinc_adms / total_adms * 100) if total_adms > 0 else 0
        st.metric("✅ Sincronizados ADMS", sinc_adms, f"{pct_adms:.1f}%")
    
    # Se não houver dados, mostrar alerta com valores disponíveis
    if total_elipse == 0 and total_adms == 0:
        st.warning(f"⚠️ Nenhum dado encontrado com os valores esperados na coluna '{coluna_changeset}'.")
        
        # Mostrar os valores disponíveis para ajudar no debug
        st.markdown(f"### 📋 Valores disponíveis na coluna '{coluna_changeset}':")
        valores_disponiveis = df[coluna_changeset].value_counts()
        st.dataframe(valores_disponiveis.reset_index().rename(columns={'index': 'ChangeSet', coluna_changeset: 'Quantidade'}))
        return
    
    # ============================================
    # GRÁFICO 1: DISTRIBUIÇÃO POR SISTEMA
    # ============================================
    st.markdown("### 📈 Distribuição por Sistema")
    
    dados_sistema = pd.DataFrame({
        'Sistema': ['ELIPSE', 'ADMS'],
        'Total': [total_elipse, total_adms],
        'Sincronizados': [sinc_elipse, sinc_adms],
        'Percentual_Sinc': [pct_elipse, pct_adms]
    })
    
    fig_comp = go.Figure()
    
    fig_comp.add_trace(go.Bar(
        x=dados_sistema['Sistema'],
        y=dados_sistema['Total'],
        name='Total',
        marker_color=COR_AZUL_ESCURO,
        text=dados_sistema['Total'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Total: %{y:,}<extra></extra>'
    ))
    
    fig_comp.add_trace(go.Bar(
        x=dados_sistema['Sistema'],
        y=dados_sistema['Sincronizados'],
        name='Sincronizados',
        marker_color=COR_VERDE_ESCURO,
        text=dados_sistema['Sincronizados'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Sincronizados: %{y:,}<extra></extra>'
    ))
    
    fig_comp.update_layout(
        title='Distribuição de Chamados por Tipo de ChangeSet',
        barmode='group',
        height=400,
        showlegend=True,
        plot_bgcolor=COR_BRANCO,
        yaxis=dict(gridcolor=COR_CINZA_BORDA, rangemode='tozero'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # ============================================
    # GRÁFICO 2: TAXA DE SUCESSO
    # ============================================
    st.markdown("### 🎯 Análise Comparativa")
    
    col_analise1, col_analise2 = st.columns(2)
    
    with col_analise1:
        st.markdown("**Taxa de Sucesso**")
        fig_taxa = go.Figure()
        
        fig_taxa.add_trace(go.Bar(
            x=dados_sistema['Sistema'],
            y=dados_sistema['Percentual_Sinc'],
            name='Taxa de Sucesso',
            marker_color=[COR_VERDE_ESCURO if pct >= 90 else COR_LARANJA for pct in dados_sistema['Percentual_Sinc']],
            text=[f"{pct:.1f}%" for pct in dados_sistema['Percentual_Sinc']],
            textposition='outside'
        ))
        
        fig_taxa.add_hline(y=90, line_dash="dash", line_color=COR_VERDE_ESCURO, annotation_text="🎯 Meta 90%")
        fig_taxa.add_hline(y=70, line_dash="dash", line_color=COR_LARANJA, annotation_text="⚠️ Alerta 70%")
        
        fig_taxa.update_layout(
            title='Taxa de Sincronização por Sistema',
            yaxis=dict(range=[0, 105], title='Percentual (%)', gridcolor=COR_CINZA_BORDA),
            height=300,
            showlegend=False,
            plot_bgcolor=COR_BRANCO
        )
        
        st.plotly_chart(fig_taxa, use_container_width=True)
    
    # ============================================
    # GRÁFICO 3: ANÁLISE DE REVISÕES
    # ============================================
    with col_analise2:
        if 'Revisões' in df.columns:
            st.markdown("**Revisões por Sistema**")
            
            revisoes_elipse = df_elipse['Revisões'].sum() if len(df_elipse) > 0 else 0
            revisoes_adms = df_adms['Revisões'].sum() if len(df_adms) > 0 else 0
            media_rev_elipse = df_elipse['Revisões'].mean() if len(df_elipse) > 0 else 0
            media_rev_adms = df_adms['Revisões'].mean() if len(df_adms) > 0 else 0
            
            dados_revisoes = pd.DataFrame({
                'Sistema': ['ELIPSE', 'ADMS'],
                'Total_Revisões': [revisoes_elipse, revisoes_adms],
                'Média_Revisões': [media_rev_elipse, media_rev_adms]
            })
            
            fig_rev = go.Figure()
            
            fig_rev.add_trace(go.Bar(
                x=dados_revisoes['Sistema'],
                y=dados_revisoes['Total_Revisões'],
                name='Total Revisões',
                marker_color=COR_LARANJA,
                text=dados_revisoes['Total_Revisões'],
                textposition='outside'
            ))
            
            fig_rev.add_trace(go.Scatter(
                x=dados_revisoes['Sistema'],
                y=dados_revisoes['Média_Revisões'],
                name='Média Revisões',
                yaxis='y2',
                mode='lines+markers+text',
                line=dict(color=COR_VERMELHO, width=3),
                marker=dict(size=10, color=COR_VERMELHO),
                text=[f"{m:.1f}" for m in dados_revisoes['Média_Revisões']],
                textposition='top center'
            ))
            
            fig_rev.update_layout(
                title='Análise de Revisões por Sistema',
                yaxis=dict(title='Total Revisões', gridcolor=COR_CINZA_BORDA),
                yaxis2=dict(
                    title='Média Revisões',
                    overlaying='y',
                    side='right',
                    gridcolor='rgba(0,0,0,0)'
                ),
                height=300,
                showlegend=True,
                plot_bgcolor=COR_BRANCO,
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )
            
            st.plotly_chart(fig_rev, use_container_width=True)
    
    # ============================================
    # GRÁFICO 4: EVOLUÇÃO MENSAL (opcional)
    # ============================================
    if 'Criado' in df.columns and (total_elipse > 0 or total_adms > 0):
        st.markdown("### 📈 Evolução Mensal dos Sistemas")
        
        # Preparar dados de evolução mensal
        df_elipse['Mês_Ano'] = df_elipse['Criado'].dt.strftime('%Y-%m')
        df_adms['Mês_Ano'] = df_adms['Criado'].dt.strftime('%Y-%m')
        
        evol_elipse = df_elipse.groupby('Mês_Ano').size().reset_index()
        evol_elipse.columns = ['Mês_Ano', 'ELIPSE']
        
        evol_adms = df_adms.groupby('Mês_Ano').size().reset_index()
        evol_adms.columns = ['Mês_Ano', 'ADMS']
        
        evol_total = pd.merge(evol_elipse, evol_adms, on='Mês_Ano', how='outer').fillna(0)
        evol_total = evol_total.sort_values('Mês_Ano')
        
        fig_evol = go.Figure()
        
        fig_evol.add_trace(go.Scatter(
            x=evol_total['Mês_Ano'],
            y=evol_total['ELIPSE'],
            name='ELIPSE',
            mode='lines+markers',
            line=dict(color=COR_AZUL_ESCURO, width=3),
            marker=dict(size=8, color=COR_AZUL_ESCURO)
        ))
        
        fig_evol.add_trace(go.Scatter(
            x=evol_total['Mês_Ano'],
            y=evol_total['ADMS'],
            name='ADMS',
            mode='lines+markers',
            line=dict(color=COR_VERDE_ESCURO, width=3),
            marker=dict(size=8, color=COR_VERDE_ESCURO)
        ))
        
        fig_evol.update_layout(
            title='Evolução Mensal de Chamados por Sistema',
            xaxis_title='Mês/Ano',
            yaxis_title='Quantidade de Chamados',
            height=350,
            showlegend=True,
            plot_bgcolor=COR_BRANCO,
            yaxis=dict(gridcolor=COR_CINZA_BORDA)
        )
        
        st.plotly_chart(fig_evol, use_container_width=True)
    
    # ============================================
    # TABELA DETALHADA
    # ============================================
    with st.expander("📋 Ver Detalhamento por Sistema", expanded=False):
        # Preparar dados detalhados
        detalhes = []
        
        for sistema in ['ELIPSE', 'ADMS']:
            if sistema == 'ELIPSE':
                df_sistema = df_elipse
            else:
                df_sistema = df_adms
            
            if len(df_sistema) > 0:
                total = len(df_sistema)
                sinc = len(df_sistema[df_sistema['Status'] == 'Sincronizado']) if 'Status' in df_sistema.columns else 0
                pct_sinc = (sinc / total * 100) if total > 0 else 0
                
                if 'Revisões' in df_sistema.columns:
                    total_rev = df_sistema['Revisões'].sum()
                    media_rev = df_sistema['Revisões'].mean()
                else:
                    total_rev = 0
                    media_rev = 0
                
                if 'Responsável_Formatado' in df_sistema.columns:
                    top_resp = df_sistema['Responsável_Formatado'].value_counts().index[0] if len(df_sistema) > 0 else 'N/A'
                else:
                    top_resp = 'N/A'
                
                detalhes.append({
                    'Sistema': sistema,
                    'Total Chamados': total,
                    'Sincronizados': sinc,
                    '% Sucesso': f"{pct_sinc:.1f}%",
                    'Total Revisões': int(total_rev),
                    'Média Revisões': f"{media_rev:.2f}",
                    'Top Responsável': top_resp
                })
        
        if detalhes:
            df_detalhes = pd.DataFrame(detalhes)
            st.dataframe(
                df_detalhes,
                use_container_width=True,
                column_config={
                    "Sistema": st.column_config.TextColumn("Sistema", width="small"),
                    "Total Chamados": st.column_config.NumberColumn("Total", format="%d"),
                    "Sincronizados": st.column_config.NumberColumn("Sinc.", format="%d"),
                    "% Sucesso": st.column_config.TextColumn("% Sucesso"),
                    "Total Revisões": st.column_config.NumberColumn("Total Rev.", format="%d"),
                    "Média Revisões": st.column_config.TextColumn("Média Rev."),
                    "Top Responsável": st.column_config.TextColumn("Top Responsável")
                }
            )

# ============================================
# FUNÇÃO DE DEBUG - VERIFICAR CHANGESET
# ============================================
def debug_changeset(df):
    """Função para debug - mostra informações sobre ChangeSet"""
    st.markdown("### 🔍 Debug - Informações sobre ChangeSet")
    
    # Identificar coluna de ChangeSet
    coluna_changeset = None
    for col in df.columns:
        if 'changeset' in col.lower() or 'change set' in col.lower():
            coluna_changeset = col
            break
    
    if coluna_changeset is None:
        st.error("❌ Coluna de 'ChangeSet' não encontrada!")
        st.markdown("### 📋 Colunas disponíveis no arquivo:")
        st.write(list(df.columns))
        return
    
    st.success(f"✅ Coluna de ChangeSet identificada: **'{coluna_changeset}'**")
    
    # Mostrar valores únicos
    st.markdown(f"### 📊 Valores únicos na coluna '{coluna_changeset}':")
    valores = df[coluna_changeset].value_counts()
    st.dataframe(valores.reset_index().rename(columns={'index': 'ChangeSet', coluna_changeset: 'Quantidade'}))
    
    # Mostrar amostra dos dados
    st.markdown("### 📋 Amostra dos dados (primeiras 10 linhas):")
    colunas_mostrar = ['Chamado', coluna_changeset, 'Status']
    colunas_existentes = [col for col in colunas_mostrar if col in df.columns]
    st.dataframe(df[colunas_existentes].head(10))

# ============================================
# FUNÇÃO DE CLASSIFICAÇÃO DE MOTIVOS DE REVISÃO
# ============================================
def classificar_motivo_revisao(texto):
    """Classifica o motivo da revisão em categorias padronizadas"""
    if pd.isna(texto) or texto == "" or texto.strip() == "":
        return "📝 Sem motivo informado"
    
    texto = str(texto).lower()
    
    # Categorias de Classificação
    categorias = {
        "📋 Erro de Documentação": [
            'erro na descrição', 'card preenchido', 'card incompleto', 'chamado sem responsável',
            'nome do changeset fora do padrão', 'card sem proprietário', 'erro no preenchimento',
            'faltou colocar a descrição', 'descrição', 'documentação', 'anexar',
            'lista de pontos desatualizada', 'card preenchido de forma errada'
        ],
        "⚙️ Falha Técnica/Configuração": [
            'changeset rejeitado', 'changeset não encontrado', 'changeset bloqueado',
            'changeset com numeração errada', 'changeset não apresentou modificação',
            'changeset duplicado', 'changeset errado', 'changeset ajustado',
            'configurações da remota fora do padrão', 'equipamento sem by-pass',
            'chave de by-pass aberta', 'parâmetros de comunicação', 'ponto de comando',
            'endereço de ip divergente', 'comandos do disjuntores incoerentes'
        ],
        "🔗 Erro de Conectividade/Nó": [
            'nó de conectividade', 'padrão de conectividade', 'criar o nó',
            'conectividade', 'main', 'node', 'link de comunicação'
        ],
        "📐 Não Conformidade com Padrão": [
            'padrão', 'procedimento', 'formato', 'nome do changeset',
            'grupo de aor', 'quadro de religadores', 'tela autogerada',
            'representação dos sinais', 'catalogo da chave', 'template',
            'alinhamento', 'sincronismo'
        ],
        "🔄 Divergência de Informação": [
            'divergência', 'inconsistente', 'incoerente', 'não condiz',
            'chamado não encontrado', 'não correlaciona', 'changeset envolve outros equipamentos',
            'dois chamados em um único changeset'
        ],
        "🎨 Erro de Interface/Tela": [
            'representações em tela', 'tela autogerada', 'diagrama unifilar',
            'esquemática', 'exibir em tela', 'tela de resumo'
        ]
    }
    
    for categoria, palavras_chave in categorias.items():
        for palavra in palavras_chave:
            if palavra in texto:
                return categoria
    
    return "📝 Outros"

# ============================================
# FUNÇÕES DO MAPA - PROCESSAMENTO DE DADOS
# ============================================
def processar_dados_mapa(df, empresas_selecionadas=None, ano_filtro=None, mes_filtro=None):
    """Processa os dados para gerar as métricas do mapa"""
    
    # Filtrar apenas sincronizados
    df_sinc = df[df['Status'] == 'Sincronizado'].copy()
    
    # Aplicar filtros de data
    if ano_filtro and ano_filtro != 'Todos':
        df_sinc = df_sinc[df_sinc['Ano'] == int(ano_filtro)]
    
    if mes_filtro and mes_filtro != 'Todos':
        df_sinc = df_sinc[df_sinc['Mês'] == int(mes_filtro)]
    
    # Filtrar empresas selecionadas
    if empresas_selecionadas and 'Todas' not in empresas_selecionadas:
        df_sinc = df_sinc[df_sinc['Empresa'].isin(empresas_selecionadas)]
    
    # Contar sincronismos por empresa
    sinc_por_empresa = df_sinc['Empresa'].value_counts().reset_index()
    sinc_por_empresa.columns = ['Empresa', 'Sincronismos']
    
    # Preparar dados para o mapa
    dados_mapa = []
    total_sinc = 0
    
    for empresa, info in MAPEAMENTO_EMPRESAS.items():
        mask = sinc_por_empresa['Empresa'] == empresa
        qtd = int(sinc_por_empresa[mask]['Sincronismos'].values[0]) if mask.any() else 0
        
        if empresas_selecionadas and 'Todas' not in empresas_selecionadas:
            if empresa not in empresas_selecionadas:
                continue
        
        dados_mapa.append({
            'sigla': info['sigla'],
            'estado': info['estado'],
            'regiao': info['regiao'],
            'empresa': empresa,
            'empresa_nome': info['nome_completo'],
            'sincronismos': qtd,
            'latitude': info['latitude'],
            'longitude': info['longitude']
        })
        total_sinc += qtd
    
    return pd.DataFrame(dados_mapa), total_sinc

# ============================================
# FUNÇÕES DO MAPA FOLIUM
# ============================================
def cor_gradiente_folium(valor, min_val, max_val):
    """
    Retorna cor em hex interpolando entre azul petróleo e vermelho.
    Valores mais ALTOS → mais VERMELHO
    Valores mais BAIXOS → mais AZUL PETRÓLEO
    """
    if max_val == min_val:
        return COR_AZUL_PETROLEO

    t = (valor - min_val) / (max_val - min_val)  # normaliza 0..1

    # Cores base
    cor_baixo = (0x02, 0x8a, 0x9f)   # #028a9f  azul petróleo
    cor_medio = (0xF5, 0x7C, 0x00)   # #F57C00  laranja
    cor_alto  = (0xC6, 0x28, 0x28)   # #C62828  vermelho

    if t < 0.5:
        tt = t / 0.5
        r = int(cor_baixo[0] + tt * (cor_medio[0] - cor_baixo[0]))
        g = int(cor_baixo[1] + tt * (cor_medio[1] - cor_baixo[1]))
        b = int(cor_baixo[2] + tt * (cor_medio[2] - cor_baixo[2]))
    else:
        tt = (t - 0.5) / 0.5
        r = int(cor_medio[0] + tt * (cor_alto[0] - cor_medio[0]))
        g = int(cor_medio[1] + tt * (cor_alto[1] - cor_medio[1]))
        b = int(cor_medio[2] + tt * (cor_alto[2] - cor_medio[2]))

    return f"#{r:02X}{g:02X}{b:02X}"


def criar_mapa_folium(df_mapa):
    """
    Cria mapa Folium interativo centrado no Brasil com:
    - Bolhas proporcionais ao volume
    - Gradiente correto azul → laranja → vermelho
    - Labels com sigla + número DENTRO da bolha
    - Tooltip rico com todas as informações
    - Legenda visual
    """
    try:
        import folium
    except ImportError:
        st.error("⚠️ Biblioteca 'folium' não instalada. Execute: pip install folium")
        return None
    
    if df_mapa.empty:
        return None

    df_bolhas = df_mapa[df_mapa['sincronismos'] > 0].copy()

    # Mapa base centrado no Brasil
    m = folium.Map(
        location=[-14.5, -51.5],
        zoom_start=4,
        tiles=None,
        prefer_canvas=True
    )

    # Tile elegante (CartoDB Positron)
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name='CartoDB Positron',
        max_zoom=19,
        subdomains='abcd'
    ).add_to(m)

    if df_bolhas.empty:
        return m

    max_sinc = df_bolhas['sincronismos'].max()
    min_sinc = df_bolhas['sincronismos'].min()
    total = df_bolhas['sincronismos'].sum()

    # Escala de raio: mínimo 20px, máximo 70px
    R_MIN, R_MAX = 20, 70

    def raio(v):
        if max_sinc == min_sinc:
            return (R_MIN + R_MAX) / 2
        return R_MIN + (v - min_sinc) / (max_sinc - min_sinc) * (R_MAX - R_MIN)

    # Ranking para badge
    df_bolhas_sorted = df_bolhas.sort_values('sincronismos', ascending=False).reset_index(drop=True)
    rank_map = {row['empresa']: i + 1 for i, row in df_bolhas_sorted.iterrows()}

    for _, row in df_bolhas.iterrows():
        cor = cor_gradiente_folium(row['sincronismos'], min_sinc, max_sinc)
        r = raio(row['sincronismos'])
        rank = rank_map[row['empresa']]
        pct = row['sincronismos'] / total * 100 if total > 0 else 0
        medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, f'#{rank}')

        # Tooltip rico
        tooltip_html = f"""
        <div style="
            font-family: 'Segoe UI', sans-serif;
            min-width: 220px;
            padding: 4px;
        ">
            <div style="
                background: {COR_AZUL_ESCURO};
                color: white;
                padding: 10px 14px;
                border-radius: 8px 8px 0 0;
                font-weight: 700;
                font-size: 14px;
            ">{medal} {row['empresa_nome']}</div>
            <div style="
                background: white;
                border: 1px solid #ddd;
                border-top: none;
                border-radius: 0 0 8px 8px;
                padding: 12px 14px;
            ">
                <table style="width:100%; border-collapse:collapse; font-size:13px;">
                    <tr><td style="color:{COR_CINZA_TEXTO}; padding:4px 0;">Código</td>
                        <td style="font-weight:700; text-align:right;">{row['empresa']}</td>
                    </tr>
                    <tr><td style="color:{COR_CINZA_TEXTO}; padding:4px 0;">Estado</td>
                        <td style="font-weight:700; text-align:right;">{row['estado']} ({row['sigla']})</td>
                    </tr>
                    <tr><td style="color:{COR_CINZA_TEXTO}; padding:4px 0;">Região</td>
                        <td style="font-weight:700; text-align:right;">{row['regiao']}</td>
                    </tr>
                    <tr style="border-top:1px solid #eee;">
                        <td style="color:{COR_CINZA_TEXTO}; padding:8px 0 4px;">Sincronizações</td>
                        <td style="font-weight:800; font-size:18px; color:{cor}; text-align:right;">
                            {row['sincronismos']:,}
                        </td>
                    </tr>
                    <tr><td style="color:{COR_CINZA_TEXTO}; padding:4px 0;">% do Total</td>
                        <td style="font-weight:600; text-align:right; color:{COR_AZUL_PETROLEO};">{pct:.1f}%</td>
                    </tr>
                    <tr><td style="color:{COR_CINZA_TEXTO}; padding:4px 0;">Ranking</td>
                        <td style="font-weight:600; text-align:right;">{medal} {rank}º lugar</td>
                    </tr>
                </table>
            </div>
        </div>
        """

        # Círculo colorido (bolha)
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=r,
            color=COR_BRANCO,
            weight=3,
            fill=True,
            fill_color=cor,
            fill_opacity=0.85,
            tooltip=folium.Tooltip(tooltip_html, sticky=True),
        ).add_to(m)

        # Label DENTRO da bolha
        font_size_sigla = max(10, min(16, int(r * 0.4)))
        font_size_num = max(9, min(14, int(r * 0.32)))
        
        label_html = f"""
        <div style="
            font-family: 'Segoe UI', 'Arial', sans-serif;
            text-align: center;
            font-weight: 800;
            line-height: 1.2;
            white-space: nowrap;
        ">
            <div style="
                font-size: {font_size_sigla}px;
                color: white;
                text-shadow: 0 1px 2px rgba(0,0,0,0.7);
                letter-spacing: 0.3px;
            ">{row['empresa']}</div>
            <div style="
                font-size: {font_size_num}px;
                color: white;
                text-shadow: 0 1px 2px rgba(0,0,0,0.6);
                font-weight: 600;
            ">{row['sincronismos']}</div>
        </div>
        """

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            icon=folium.DivIcon(
                html=label_html,
                icon_size=(int(r * 1.8), int(r * 1.8)),
                icon_anchor=(int(r * 0.9), int(r * 0.9)),
            )
        ).add_to(m)

    # Legenda de gradiente
    legenda_html = f"""
    <div style="
        position: fixed;
        bottom: 30px;
        left: 20px;
        z-index: 9999;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        padding: 14px 20px;
        font-family: 'Segoe UI', sans-serif;
        min-width: 210px;
        border: 1px solid {COR_CINZA_BORDA};
    ">
        <div style="font-weight:800; font-size:13px; color:{COR_PRETO_SUAVE}; margin-bottom:12px; letter-spacing:0.5px;">
            📊 VOLUME DE SINCRONIZAÇÕES
        </div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            <div style="
                width: 140px; height: 12px; border-radius: 6px;
                background: linear-gradient(to right, {COR_AZUL_PETROLEO}, {COR_LARANJA}, {COR_VERMELHO});
                border: 1px solid #ddd;
            "></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:10px; color:{COR_CINZA_TEXTO}; margin-bottom:12px;">
            <span>⬅️ Menor volume</span>
            <span>Maior volume ➡️</span>
        </div>
        <div style="border-top:1px solid {COR_CINZA_BORDA}; padding-top:10px; font-size:10px; color:{COR_CINZA_TEXTO};">
            <div>🔍 Passe o mouse sobre uma bolha</div>
            <div>para ver os detalhes completos</div>
        </div>
    </div>
    """

    m.get_root().html.add_child(folium.Element(legenda_html))

    # Painel de top 3
    if len(df_bolhas_sorted) >= 1:
        top3_rows = df_bolhas_sorted.head(3)
        top3_html_items = ""
        medals = ['🥇', '🥈', '🥉']

        for i, (_, row) in enumerate(top3_rows.iterrows()):
            pct_t = row['sincronismos'] / total * 100 if total > 0 else 0
            cor_top = cor_gradiente_folium(row['sincronismos'], min_sinc, max_sinc)
            top3_html_items += f"""
            <div style="
                display:flex; align-items:center; gap:10px;
                padding: 8px 0;
                border-bottom: 1px solid {COR_CINZA_BORDA};
            ">
                <span style="font-size:18px;">{medals[i]}</span>
                <div style="flex:1;">
                    <div style="font-weight:700; font-size:12px; color:{COR_PRETO_SUAVE};">{row['empresa_nome'][:25]}</div>
                    <div style="font-size:10px; color:{COR_CINZA_TEXTO};">{row['estado']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-weight:800; font-size:14px; color:{cor_top};">{row['sincronismos']:,}</div>
                    <div style="font-size:9px; color:{COR_CINZA_TEXTO};">{pct_t:.1f}%</div>
                </div>
            </div>
            """

        painel_html = f"""
        <div style="
            position: fixed;
            top: 90px;
            right: 20px;
            z-index: 9999;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            padding: 14px 18px;
            font-family: 'Segoe UI', sans-serif;
            min-width: 240px;
            border: 1px solid {COR_CINZA_BORDA};
        ">
            <div style="font-weight:800; font-size:13px; color:{COR_PRETO_SUAVE}; margin-bottom:10px; letter-spacing:0.5px;">
                🏆 TOP EMPRESAS
            </div>
            {top3_html_items}
            <div style="padding-top:10px; font-size:11px; color:{COR_CINZA_TEXTO}; text-align:center; border-top:1px solid {COR_CINZA_BORDA}; margin-top:5px;">
                <strong style="color:{COR_AZUL_ESCURO};">Total: {total:,}</strong> sincronizações
            </div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(painel_html))

    return m


def criar_grafico_barras(df_mapa):
    """Cria gráfico de barras comparativo com barras de progresso coloridas"""
    if df_mapa.empty:
        return None
    
    df_barras = df_mapa.sort_values('sincronismos', ascending=False).reset_index(drop=True)
    total = df_barras['sincronismos'].sum()
    
    fig = go.Figure()
    
    # Cores baseadas no valor
    max_val = df_barras['sincronismos'].max()
    min_val = df_barras['sincronismos'].min()
    
    for idx, row in df_barras.iterrows():
        if max_val == min_val:
            cor = COR_AZUL_PETROLEO
        else:
            normalized = (row['sincronismos'] - min_val) / (max_val - min_val)
            # Gradiente: azul petróleo -> laranja -> vermelho
            if normalized < 0.5:
                tt = normalized / 0.5
                r = int(2 + tt * (245 - 2))
                g = int(138 + tt * (124 - 138))
                b = int(159 + tt * (0 - 159))
            else:
                tt = (normalized - 0.5) / 0.5
                r = int(245 + tt * (198 - 245))
                g = int(124 + tt * (40 - 124))
                b = int(0 + tt * (40 - 0))
            cor = f'rgb({r}, {g}, {b})'
        
        percentual = (row['sincronismos'] / total * 100) if total > 0 else 0
        
        # Adicionar barra
        fig.add_trace(go.Bar(
            x=[row['sincronismos']],
            y=[f"{row['empresa']} - {row['empresa_nome'][:20]}"],
            orientation='h',
            text=[f"{row['sincronismos']:,} ({percentual:.1f}%)"],
            textposition='outside',
            marker_color=cor,
            marker_line_color=COR_AZUL_ESCURO,
            marker_line_width=1,
            hovertemplate=f"<b>{row['empresa_nome']}</b><br>" +
                          f"Sincronizações: {row['sincronismos']:,}<br>" +
                          f"Percentual: {percentual:.1f}%<br>" +
                          f"Estado: {row['estado']}<br>" +
                          f"Região: {row['regiao']}<extra></extra>",
            name=row['empresa']
        ))
    
    fig.update_layout(
        title=dict(
            text="<b>RANKING </b>",
            font=dict(size=16, color=COR_AZUL_ESCURO),
            x=0.5
        ),
        xaxis_title="Número de Sincronizações",
        yaxis_title="",
        height=450,
        showlegend=False,
        plot_bgcolor=COR_BRANCO,
        xaxis=dict(
            gridcolor=COR_CINZA_BORDA,
            tickformat="d",
            title_font=dict(size=12)
        ),
        yaxis=dict(
            gridcolor=COR_CINZA_BORDA,
            tickfont=dict(size=11),
            categoryorder='total ascending'
        ),
        margin=dict(l=20, r=80, t=60, b=20),
        hovermode='closest'
    )
    
    return fig

# ============================================
# CONTINUAÇÃO DO CÓDIGO - SIDEBAR E DASHBOARD
# ============================================

# O restante do código (Sidebar, Tabs, etc.) continua igual ao original,
# mas com a adição do filtro "Sistema" e da nova aba "ADMS vs ELIPSE"

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
    
    if 'df_original' not in st.session_state:
        st.session_state.df_original = None
        st.session_state.df_filtrado = None
        st.session_state.arquivo_atual = None
        st.session_state.file_hash = None
        st.session_state.uploaded_file_name = None
        st.session_state.ultima_atualizacao = None
    
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
            
            # ============================================
            # NOVO FILTRO DE SISTEMA NA SIDEBAR
            # ============================================
            with st.container():
                st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
                st.markdown("**🎯 Sistema**")
                
                # Novo filtro para sistema de validação
                sistema_selecionado = st.selectbox(
                    "Selecionar Sistema:",
                    options=['Todos', 'ADMS', 'ELIPSE'],
                    key="filtro_sistema",
                    help="Filtra os chamados por sistema de validação baseado no ChangeSet"
                )
                
                st.session_state.sistema_selecionado = sistema_selecionado
                
                # Exibir informações sobre o filtro atual
                if sistema_selecionado == 'ADMS':
                    st.info("🔹 **ADMS**: ChangeSet 'Telemetry' e 'Manual'")
                elif sistema_selecionado == 'ELIPSE':
                    st.info("🔹 **ELIPSE**: ChangeSet 'Elipse'")
                else:
                    st.info("🔹 **Todos**: Exibindo todos os chamados")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**🔄 Controles de Atualização**")
        
        if st.session_state.df_original is not None:
            arquivo_atual = st.session_state.arquivo_atual
            
            if arquivo_atual and isinstance(arquivo_atual, str) and os.path.exists(arquivo_atual):
                tamanho_kb = os.path.getsize(arquivo_atual) / 1024
                ultima_mod = datetime.fromtimestamp(os.path.getmtime(arquivo_atual))
                
                st.markdown(f"""
                <div style="background: {COR_CINZA_FUNDO}; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem;">
                    <p style="margin: 0 0 0.3rem 0; font-weight: 600;">📄 Arquivo atual:</p>
                    <p style="margin: 0; font-size: 0.85rem; color: {COR_PRETO_SUAVE};">{os.path.basename(arquivo_atual)}</p>
                    <p style="margin: 0.3rem 0 0 0; font-size: 0.75rem; color: {COR_CINZA_TEXTO};">
                    📏 {tamanho_kb:.1f} KB | 📅 {ultima_mod.strftime('%d/%m/%Y %H:%M')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if verificar_e_atualizar_arquivo():
                    st.warning("⚠️ O arquivo local foi modificado! Clique em 'Recarregar Local' para atualizar.")
            
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
        
        st.markdown("**📤 Importar Dados**")
        
        if st.session_state.df_original is not None:
            ultima_atualizacao = st.session_state.get('ultima_atualizacao', get_horario_brasilia())
            st.markdown(f"""
            <div class="status-success">
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
            
            file_details = {
                "Nome": uploaded_file.name,
                "Tamanho": f"{uploaded_file.size / 1024:.1f} KB"
            }
            
            st.write("📄 Detalhes do arquivo:")
            st.json(file_details)
            
            if st.button("📥 Processar Arquivo", use_container_width=True, type="primary", key="btn_processar"):
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
                        
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {status}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
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
# HEADER - ESTILO GRADIENTE AZUL PETRÓLEO
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
                📊 ESTEIRA ADMS
            </h1>
            <p style="
                color: rgba(255,255,255,0.9);
                margin: 0.3rem 0 0 0;
                font-size: 0.85rem;
                font-weight: 400;
            ">
                Acompanhamento de Demandas - ADMS & ELIPSE
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
                v6.0 | Sistema de Performance
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
# APLICAÇÃO DO FILTRO DE SISTEMA
# ============================================
if st.session_state.df_original is not None:
    # Aplicar filtros existentes...
    df_filtrado = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    # Aplicar filtro de sistema
    if 'sistema_selecionado' in st.session_state:
        sistema_selecionado = st.session_state.sistema_selecionado
        df_filtrado_sistema = filtrar_por_sistema(df_filtrado, sistema_selecionado)
        st.session_state.df_filtrado_sistema = df_filtrado_sistema
    else:
        st.session_state.df_filtrado_sistema = df_filtrado

# ============================================
# EXIBIR DASHBOARD SE HOUVER DADOS
# ============================================
if st.session_state.df_original is not None:
    # Usar o DataFrame filtrado por sistema para as abas
    df_para_analise = st.session_state.df_filtrado_sistema if st.session_state.df_filtrado_sistema is not None else st.session_state.df_filtrado
    if df_para_analise is None:
        df_para_analise = st.session_state.df_original
    
    # ============================================
    # CRIAR TABS PRINCIPAIS
    # ============================================
    tab_principal, tab_mapa, tab_motivos, tab_ipe, tab_comparativo = st.tabs(["📊 Dashboard Principal", "🗺️ Mapa de Sincronizações", "🔍 Motivos de Revisão", "📈 SRE Performance (KPI IPE)", "📊 ADMS vs ELIPSE"])
    
    with tab_principal:
        st.markdown("## 📊 Informações da Base de Dados")
        
        # Adicionar informação do sistema filtrado
        sistema_atual = st.session_state.get('sistema_selecionado', 'Todos')
        
        if 'Criado' in df_para_analise.columns and not df_para_analise.empty:
            data_min = df_para_analise['Criado'].min()
            data_max = df_para_analise['Criado'].max()
            
            st.markdown(f"""
            <div class="info-base">
                <p style="margin: 0; font-weight: 600;">📅 Base atualizada em: {get_horario_brasilia()}</p>
                <p style="margin: 0.3rem 0 0 0; color: {COR_CINZA_TEXTO};">
                Período coberto: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')} | 
                Total de registros: {len(df_para_analise):,} | 
                Sistema: <strong>{sistema_atual}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("## 📈 INDICADORES PRINCIPAIS")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_atual = len(df_para_analise)
            st.markdown(criar_card_indicador_simples(
                total_atual, 
                "Total de Demandas", 
                "📋"
            ), unsafe_allow_html=True)
        
        with col2:
            if 'Status' in df_para_analise.columns:
                sincronizados = len(df_para_analise[df_para_analise['Status'] == 'Sincronizado'])
                st.markdown(criar_card_indicador_simples(
                    sincronizados,
                    "Sincronizados",
                    "✅"
                ), unsafe_allow_html=True)
        
        with col3:
            if 'Revisões' in df_para_analise.columns:
                total_revisoes = int(df_para_analise['Revisões'].sum())
                st.markdown(criar_card_indicador_simples(
                    total_revisoes,
                    "Total de Revisões",
                    "📝"
                ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Nota: As abas internas (Evolução, Revisões, etc.) continuam funcionando 
        # com o dataframe filtrado por sistema
        
        st.info("ℹ️ As análises detalhadas de evolução, revisões e performance dos SREs estão disponíveis nas abas abaixo, aplicando o filtro de sistema selecionado.")
    
    with tab_mapa:
        st.markdown("## 🗺️ Mapa de Sincronizações por Empresa")
        
        # Filtros para o mapa
        col_mapa_filtro1, col_mapa_filtro2, col_mapa_filtro3 = st.columns(3)
        
        with col_mapa_filtro1:
            empresas_disponiveis = df_para_analise['Empresa'].dropna().unique()
            empresas_opcoes = ['Todas'] + sorted([e for e in empresas_disponiveis if e in MAPEAMENTO_EMPRESAS])
            
            empresas_selecionadas_mapa = st.multiselect(
                "🏢 Empresas",
                options=empresas_opcoes,
                default=['Todas'],
                key="mapa_empresas_folium"
            )
        
        with col_mapa_filtro2:
            if 'Ano' in df_para_analise.columns:
                anos_disponiveis_mapa = sorted(df_para_analise['Ano'].dropna().unique().astype(int))
                anos_opcoes_mapa = ['Todos'] + list(anos_disponiveis_mapa)
                ano_filtro_mapa = st.selectbox(
                    "📅 Ano",
                    options=anos_opcoes_mapa,
                    index=0,
                    key="mapa_ano_folium"
                )
            else:
                ano_filtro_mapa = 'Todos'
        
        with col_mapa_filtro3:
            if 'Mês' in df_para_analise.columns and ano_filtro_mapa != 'Todos':
                df_ano_mapa = df_para_analise[df_para_analise['Ano'] == int(ano_filtro_mapa)]
                meses_disponiveis_mapa = sorted(df_ano_mapa['Mês'].dropna().unique().astype(int))
                meses_opcoes_mapa = ['Todos'] + [f"{m:02d}" for m in meses_disponiveis_mapa]
                mes_filtro_mapa = st.selectbox(
                    "📆 Mês",
                    options=meses_opcoes_mapa,
                    index=0,
                    key="mapa_mes_folium"
                )
            else:
                mes_filtro_mapa = 'Todos'
        
        # Processar dados para o mapa
        df_mapa, total_sinc_filtrado = processar_dados_mapa(
            df_para_analise,
            empresas_selecionadas=empresas_selecionadas_mapa,
            ano_filtro=ano_filtro_mapa,
            mes_filtro=mes_filtro_mapa
        )
        
        # Métricas do mapa
        col_metrica1, col_metrica2, col_metrica3, col_metrica4 = st.columns(4)
        
        with col_metrica1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_sinc_filtrado:,}</div>
                <div class="metric-label">Total Sincronizações</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_metrica2:
            empresas_ativas = len(df_mapa[df_mapa['sincronismos'] > 0])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{empresas_ativas}</div>
                <div class="metric-label">Empresas com Sinc.</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_metrica3:
            if not df_mapa.empty:
                media_sinc = df_mapa['sincronismos'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{media_sinc:.1f}</div>
                    <div class="metric-label">Média por Empresa</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">0</div>
                    <div class="metric-label">Média por Empresa</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col_metrica4:
            if not df_mapa.empty and df_mapa['sincronismos'].max() > 0:
                max_sinc = df_mapa['sincronismos'].max()
                empresa_max = df_mapa[df_mapa['sincronismos'] == max_sinc]['empresa_nome'].values[0]
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{max_sinc:,}</div>
                    <div class="metric-label">🏆 Maior: {empresa_max[:20]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">0</div>
                    <div class="metric-label">Maior Sincronização</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Mapa Folium
        st.markdown('<div class="section-title">📍 MAPA DE BOLHAS </div>', unsafe_allow_html=True)
        
        m = criar_mapa_folium(df_mapa)
        if m:
            mapa_html = m._repr_html_()
            
            wrapper = f"""
            <div style="
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0,89,115,0.12);
                border: 1px solid {COR_CINZA_BORDA};
                margin-bottom: 20px;
            ">
                {mapa_html}
            </div>
            """
            st.components.v1.html(wrapper, height=620)
        else:
            st.info("ℹ️ Nenhuma empresa com sincronizações para exibir no mapa.")
        
        # Ranking de barras
        st.markdown('<div class="section-title">🏆 RANKING DE SINCRONIZAÇÕES POR EMPRESA</div>', unsafe_allow_html=True)
        
        fig_barras = criar_grafico_barras(df_mapa)
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True, config={'displayModeBar': True})
        
        # Tabela detalhada
        with st.expander("📋 Ver Detalhes por Empresa", expanded=False):
            if not df_mapa.empty:
                tabela_detalhes = df_mapa[['empresa_nome', 'sigla', 'estado', 'regiao', 'sincronismos']].copy()
                tabela_detalhes.columns = ['Empresa', 'UF', 'Estado', 'Região', 'Sincronizações']
                tabela_detalhes = tabela_detalhes.sort_values('Sincronizações', ascending=False).reset_index(drop=True)
                
                total_geral = tabela_detalhes['Sincronizações'].sum()
                
                posicoes = []
                for i in range(len(tabela_detalhes)):
                    if i == 0:
                        posicoes.append("🥇")
                    elif i == 1:
                        posicoes.append("🥈")
                    elif i == 2:
                        posicoes.append("🥉")
                    else:
                        posicoes.append(f"{i+1}º")
                tabela_detalhes.insert(0, 'Posição', posicoes)
                
                tabela_detalhes['% Total'] = (tabela_detalhes['Sincronizações'] / total_geral * 100).round(1) if total_geral > 0 else 0
                
                tabela_detalhes['Empresa (UF)'] = tabela_detalhes.apply(
                    lambda x: f"{x['Empresa']} ({x['UF']})", axis=1
                )
                
                df_exibir = tabela_detalhes[['Posição', 'Empresa (UF)', 'Estado', 'Região', 'Sincronizações', '% Total']].copy()
                
                column_config = {
                    "Posição": st.column_config.TextColumn("Posição", width="small"),
                    "Empresa (UF)": st.column_config.TextColumn("Empresa", width="large"),
                    "Estado": st.column_config.TextColumn("Estado", width="medium"),
                    "Região": st.column_config.TextColumn("Região", width="medium"),
                    "Sincronizações": st.column_config.NumberColumn("Sinc.", format="%d", width="small"),
                    "% Total": st.column_config.NumberColumn("% Total", format="%.1f%%", width="small")
                }
                
                st.dataframe(
                    df_exibir,
                    use_container_width=True,
                    column_config=column_config,
                    height=400
                )
                
                csv = tabela_detalhes[['Empresa', 'UF', 'Estado', 'Região', 'Sincronizações', '% Total']].to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Exportar dados para CSV",
                    data=csv,
                    file_name=f"sincronismos_empresas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    with tab_motivos:
        st.markdown("## 🔍 ANÁLISE DE MOTIVOS DE REVISÃO")
        st.markdown("_Principais causas de retrabalho e oportunidades de melhoria_")
        
        if 'Motivo_Revisao' not in df_para_analise.columns:
            st.warning("⚠️ Coluna 'Motivo Revisão' não encontrada no arquivo de dados.")
        else:
            st.info("ℹ️ A análise de motivos de revisão está aplicando o filtro de sistema selecionado.")
            
            # Versão simplificada da análise de motivos
            df_com_revisao = df_para_analise[df_para_analise['Revisões'] > 0].copy()
            df_com_motivo = df_com_revisao[df_com_revisao['Motivo_Revisao'].notna() & (df_com_revisao['Motivo_Revisao'].str.strip() != '')].copy()
            
            total_com_revisao = len(df_com_revisao)
            total_com_motivo_informado = len(df_com_motivo)
            
            st.markdown("### 📊 Resumo Executivo")
            
            col_metric1, col_metric2, col_metric3 = st.columns(3)
            
            with col_metric1:
                st.metric("📋 Total com Revisão", total_com_revisao)
            
            with col_metric2:
                st.metric("📝 Motivos Informados", total_com_motivo_informado)
            
            with col_metric3:
                pct_informado = (total_com_motivo_informado / total_com_revisao * 100) if total_com_revisao > 0 else 0
                st.metric("📊 Taxa de Informação", f"{pct_informado:.1f}%")
            
            if df_com_motivo.empty:
                st.info("ℹ️ Nenhum motivo de revisão registrado com os filtros selecionados.")
            else:
                # Classificar motivos
                df_com_motivo['Categoria'] = df_com_motivo['Motivo_Revisao'].apply(classificar_motivo_revisao)
                
                # Distribuição por categoria
                st.markdown("### 📊 Distribuição por Categoria")
                
                categoria_counts = df_com_motivo['Categoria'].value_counts().reset_index()
                categoria_counts.columns = ['Categoria', 'Quantidade']
                categoria_counts['Percentual'] = (categoria_counts['Quantidade'] / len(df_com_motivo) * 100).round(1)
                
                fig_cat = px.pie(
                    categoria_counts,
                    values='Quantidade',
                    names='Categoria',
                    title='Distribuição por Categoria de Motivo',
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_cat.update_layout(height=400)
                st.plotly_chart(fig_cat, use_container_width=True)
                
                # Top motivos
                st.markdown("### 🎯 Top Motivos Mais Recorrentes")
                
                motivos_counts = df_com_motivo['Motivo_Revisao'].value_counts().head(10).reset_index()
                motivos_counts.columns = ['Motivo', 'Quantidade']
                
                fig_motivos = go.Figure()
                fig_motivos.add_trace(go.Bar(
                    x=motivos_counts['Motivo'],
                    y=motivos_counts['Quantidade'],
                    text=motivos_counts['Quantidade'],
                    textposition='outside',
                    marker_color=COR_AZUL_PETROLEO
                ))
                fig_motivos.update_layout(
                    title='Top 10 Motivos de Revisão',
                    xaxis_title='Motivo',
                    yaxis_title='Quantidade',
                    height=400,
                    xaxis=dict(tickangle=45)
                )
                st.plotly_chart(fig_motivos, use_container_width=True)
    
    with tab_ipe:
        st.markdown(f'<div class="section-title">🎯 KPI IPE - ÍNDICE DE PERFORMANCE DO ESPECIALISTA</div>', unsafe_allow_html=True)
        
        if 'SRE' in df_para_analise.columns and 'Status' in df_para_analise.columns:
            st.info("ℹ️ Análise de IPE aplicando o filtro de sistema selecionado.")
            
            # Versão simplificada do IPE
            df_sre = df_para_analise[df_para_analise['Status'] == 'Sincronizado'].copy()
            
            if not df_sre.empty:
                sinc_por_sre = df_sre['SRE'].value_counts().reset_index()
                sinc_por_sre.columns = ['SRE', 'Sincronizados']
                
                st.markdown("### 📊 Sincronizações por SRE")
                
                fig_sre = px.bar(
                    sinc_por_sre,
                    x='SRE',
                    y='Sincronizados',
                    title='Sincronizações por SRE',
                    text='Sincronizados',
                    color='Sincronizados',
                    color_continuous_scale='Blues'
                )
                fig_sre.update_layout(height=400)
                st.plotly_chart(fig_sre, use_container_width=True)
                
                st.dataframe(sinc_por_sre, use_container_width=True)
            else:
                st.info("ℹ️ Nenhum dado sincronizado encontrado com os filtros selecionados.")
        else:
            st.warning("⚠️ Colunas necessárias não encontradas para análise de IPE.")
    
    # ============================================
    # NOVA ABA: ADMS vs ELIPSE
    # ============================================
    with tab_comparativo:
        st.markdown(f'<div class="section-title">📊 ANÁLISE COMPARATIVA ADMS vs ELIPSE</div>', unsafe_allow_html=True)
        
        # Debug - Mostrar informações sobre ChangeSet
        with st.expander("🔍 Debug - Verificar ChangeSet", expanded=False):
            debug_changeset(df_para_analise)
        
        # Chamar a função de estatísticas comparativas com todos os gráficos
        exibir_estatisticas_por_sistema(df_para_analise)

else:
    st.markdown(f"""
    <div style="text-align: center; padding: 4rem; background: {COR_CINZA_FUNDO}; border-radius: 12px; border: 2px dashed {COR_CINZA_BORDA};">
        <h3 style="color: {COR_PRETO_SUAVE};">📊 Esteira ADMS Dashboard</h3>
        <p style="color: {COR_CINZA_TEXTO}; margin-bottom: 2rem;">
            Sistema de análise e monitoramento de chamados - ADMS & ELIPSE
        </p>
        <div style="margin-top: 2rem; padding: 2rem; background: {COR_BRANCO}; border-radius: 8px; display: inline-block;">
            <h4 style="color: {COR_AZUL_ESCURO};">📋 Para começar:</h4>
            <p>1. <strong>Use a barra lateral esquerda</strong> para fazer upload do arquivo CSV</p>
            <p>2. <strong>Use a seção "Importar Dados"</strong> no final da barra lateral</p>
            <p>3. <strong>Ou coloque um arquivo CSV</strong> no mesmo diretório do app</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
        Versão 6.0 | Sistema de Performance ADMS/ELIPSE | Última atualização: {ultima_atualizacao} (Brasília)
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
