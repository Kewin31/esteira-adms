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

# Lista de siglas de empresas válidas
EMPRESAS_VALIDAS = set(MAPEAMENTO_EMPRESAS.keys())

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

# ============================================
# FUNÇÃO PRINCIPAL DE CARREGAMENTO DE DADOS
# ============================================
@st.cache_data(ttl=300)
def carregar_dados(uploaded_file=None, caminho_arquivo=None):
    """Carrega e processa os dados - Adaptado para o formato do arquivo ADMS"""
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
        
        # Busca pelo cabeçalho
        header_line = None
        for i, line in enumerate(lines):
            line_clean = line.strip().strip('\ufeff')
            if '"Chamado"' in line_clean and '"Tipo Chamado"' in line_clean:
                header_line = i
                break
        
        if header_line is None:
            for i, line in enumerate(lines):
                line_clean = line.strip().strip('\ufeff')
                if '"Chamado"' in line_clean:
                    header_line = i
                    break
        
        if header_line is None:
            return None, "Formato de arquivo inválido - cabeçalho não encontrado", None
        
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
        
        for old, new in col_mapping.items():
            if old in df.columns:
                df = df.rename(columns={old: new})
        
        # Processamento de datas
        date_columns = ['Criado', 'Modificado', 'Vencimento']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Criação de colunas de data
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
        
        # Processamento do responsável
        if 'Responsável' in df.columns:
            df['Responsável_Formatado'] = df['Responsável'].apply(formatar_nome_responsavel)
        
        # Processamento de revisões
        if 'Revisões' in df.columns:
            df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
        
        # Processamento de empresa - FILTRA APENAS EMPRESAS VÁLIDAS
        if 'Empresa' in df.columns:
            df['Empresa'] = df['Empresa'].astype(str).str.strip()
            # Remove empresas que não estão no mapeamento
            df = df[df['Empresa'].isin(EMPRESAS_VALIDAS)]
        
        if 'Sincronização' in df.columns:
            df['Sincronização'] = df['Sincronização'].astype(str).str.strip()
        
        hash_conteudo = calcular_hash_arquivo(conteudo_bytes)
        timestamp = time.time()
        
        return df, "✅ Dados carregados com sucesso", f"{hash_conteudo}_{timestamp}"
    
    except Exception as e:
        import traceback
        traceback.print_exc()
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
# FUNÇÕES DO MAPA - PROCESSAMENTO DE DADOS
# ============================================
def processar_dados_mapa(df, empresas_selecionadas=None, ano_filtro=None, mes_filtro=None):
    """Processa os dados para gerar as métricas do mapa"""
    
    df_sinc = df[df['Status'] == 'Sincronizado'].copy()
    
    if ano_filtro and ano_filtro != 'Todos':
        df_sinc = df_sinc[df_sinc['Ano'] == int(ano_filtro)]
    
    if mes_filtro and mes_filtro != 'Todos':
        df_sinc = df_sinc[df_sinc['Mês'] == int(mes_filtro)]
    
    if empresas_selecionadas and 'Todas' not in empresas_selecionadas:
        df_sinc = df_sinc[df_sinc['Empresa'].isin(empresas_selecionadas)]
    
    sinc_por_empresa = df_sinc['Empresa'].value_counts().reset_index()
    sinc_por_empresa.columns = ['Empresa', 'Sincronismos']
    
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
# FUNÇÃO DO MAPA FOLIUM - CORRIGIDA (SEM API KEY)
# ============================================
def cor_gradiente_folium(valor, min_val, max_val):
    """Retorna cor em hex interpolando entre azul petróleo e vermelho"""
    if max_val == min_val:
        return COR_AZUL_PETROLEO

    t = (valor - min_val) / (max_val - min_val)

    cor_baixo = (0x02, 0x8a, 0x9f)
    cor_medio = (0xF5, 0x7C, 0x00)
    cor_alto  = (0xC6, 0x28, 0x28)

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
    Cria mapa Folium interativo centrado no Brasil com tiles gratuitos (sem API Key)
    """
    try:
        import folium
    except ImportError:
        st.error("⚠️ Biblioteca 'folium' não instalada. Execute: pip install folium")
        return None
    
    if df_mapa.empty:
        return None

    df_bolhas = df_mapa[df_mapa['sincronismos'] > 0].copy()

    # Mapa base usando OpenStreetMap - GRATUITO e SEM API KEY
    m = folium.Map(
        location=[-14.5, -51.5],
        zoom_start=4,
        tiles='OpenStreetMap',
        control_scale=True
    )

    if df_bolhas.empty:
        return m

    max_sinc = df_bolhas['sincronismos'].max()
    min_sinc = df_bolhas['sincronismos'].min()
    total = df_bolhas['sincronismos'].sum()

    R_MIN, R_MAX = 20, 70

    def raio(v):
        if max_sinc == min_sinc:
            return (R_MIN + R_MAX) / 2
        return R_MIN + (v - min_sinc) / (max_sinc - min_sinc) * (R_MAX - R_MIN)

    df_bolhas_sorted = df_bolhas.sort_values('sincronismos', ascending=False).reset_index(drop=True)
    rank_map = {row['empresa']: i + 1 for i, row in df_bolhas_sorted.iterrows()}

    for _, row in df_bolhas.iterrows():
        cor = cor_gradiente_folium(row['sincronismos'], min_sinc, max_sinc)
        r = raio(row['sincronismos'])
        rank = rank_map[row['empresa']]
        pct = row['sincronismos'] / total * 100 if total > 0 else 0
        medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, f'#{rank}')

        tooltip_html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; min-width: 220px; padding: 4px;">
            <div style="background: {COR_AZUL_ESCURO}; color: white; padding: 10px 14px; border-radius: 8px 8px 0 0; font-weight: 700; font-size: 14px;">
                {medal} {row['empresa_nome']}
            </div>
            <div style="background: white; border: 1px solid #ddd; border-top: none; border-radius: 0 0 8px 8px; padding: 12px 14px;">
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

        font_size_sigla = max(10, min(16, int(r * 0.4)))
        font_size_num = max(9, min(14, int(r * 0.32)))
        
        label_html = f"""
        <div style="font-family: 'Segoe UI', 'Arial', sans-serif; text-align: center; font-weight: 800; line-height: 1.2; white-space: nowrap;">
            <div style="font-size: {font_size_sigla}px; color: white; text-shadow: 0 1px 2px rgba(0,0,0,0.7); letter-spacing: 0.3px;">
                {row['empresa']}
            </div>
            <div style="font-size: {font_size_num}px; color: white; text-shadow: 0 1px 2px rgba(0,0,0,0.6); font-weight: 600;">
                {row['sincronismos']}
            </div>
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

    # Legenda
    legenda_html = f"""
    <div style="position: fixed; bottom: 30px; left: 20px; z-index: 9999; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); padding: 14px 20px; font-family: 'Segoe UI', sans-serif; min-width: 210px; border: 1px solid {COR_CINZA_BORDA};">
        <div style="font-weight:800; font-size:13px; color:{COR_PRETO_SUAVE}; margin-bottom:12px; letter-spacing:0.5px;">
            📊 VOLUME DE SINCRONIZAÇÕES
        </div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            <div style="width: 140px; height: 12px; border-radius: 6px; background: linear-gradient(to right, {COR_AZUL_PETROLEO}, {COR_LARANJA}, {COR_VERMELHO}); border: 1px solid #ddd;"></div>
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

    # Painel Top 3
    if len(df_bolhas_sorted) >= 1:
        top3_rows = df_bolhas_sorted.head(3)
        top3_html_items = ""
        medals = ['🥇', '🥈', '🥉']

        for i, (_, row) in enumerate(top3_rows.iterrows()):
            pct_t = row['sincronismos'] / total * 100 if total > 0 else 0
            cor_top = cor_gradiente_folium(row['sincronismos'], min_sinc, max_sinc)
            top3_html_items += f"""
            <div style="display:flex; align-items:center; gap:10px; padding: 8px 0; border-bottom: 1px solid {COR_CINZA_BORDA};">
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
        <div style="position: fixed; top: 90px; right: 20px; z-index: 9999; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); padding: 14px 18px; font-family: 'Segoe UI', sans-serif; min-width: 240px; border: 1px solid {COR_CINZA_BORDA};">
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
    
    max_val = df_barras['sincronismos'].max()
    min_val = df_barras['sincronismos'].min()
    
    for idx, row in df_barras.iterrows():
        if max_val == min_val:
            cor = COR_AZUL_PETROLEO
        else:
            normalized = (row['sincronismos'] - min_val) / (max_val - min_val)
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
            text="<b>RANKING DE SINCRONIZAÇÕES POR EMPRESA</b>",
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

if st.session_state.df_original is not None:
    if verificar_e_atualizar_arquivo():
        st.info("🔔 O arquivo local foi atualizado! Clique em 'Recarregar Local' na barra lateral para atualizar os dados.")

# ============================================
# EXIBIR DASHBOARD SE HOUVER DADOS
# ============================================
if st.session_state.df_original is not None:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    tab_principal, tab_mapa, tab_ipe, tab_estatistica = st.tabs(["📊 Principal", "🗺️ Mapa", "📈 KPI", "📈 Análise Estatística"])
    
    with tab_principal:
        st.markdown("## 📈 Key indicators")
        
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
        
        st.markdown("---")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📅 Evolução de Demandas", 
            "📊 Análise de Revisões", 
            "📈 Sincronização Diária",
            "🏆 Análise Avançada SRE"
        ])
        
        with tab1:
            st.markdown(f'<div class="section-title">📅 EVOLUÇÃO DE DEMANDAS POR MÊS</div>', unsafe_allow_html=True)
            
            if 'Ano' in df.columns and 'Nome_Mês' in df.columns:
                anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                if anos_disponiveis:
                    ano_selecionado = st.selectbox(
                        "Selecionar Ano:",
                        options=anos_disponiveis,
                        index=len(anos_disponiveis)-1,
                        key="ano_evolucao"
                    )
                    
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
                            line=dict(color=COR_AZUL_ESCURO, width=3),
                            marker=dict(size=10, color=COR_AZUL_PETROLEO),
                            text=demandas_completas['Quantidade'],
                            textposition='top center',
                            textfont=dict(size=12, color=COR_AZUL_ESCURO)
                        ))
                        
                        fig_mes.update_layout(
                            title=f"Demandas em {ano_selecionado}",
                            xaxis_title="Mês",
                            yaxis_title="Número de Demandas",
                            plot_bgcolor=COR_BRANCO,
                            height=450,
                            showlegend=False,
                            margin=dict(t=50, b=50, l=50, r=50),
                            xaxis=dict(
                                gridcolor='rgba(0,0,0,0.05)',
                                tickmode='array',
                                tickvals=list(range(12)),
                                ticktext=ordem_meses_abreviados
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
                            font=dict(size=12, color=COR_AZUL_ESCURO, weight="bold"),
                            bgcolor="rgba(255,255,255,0.9)",
                            bordercolor=COR_AZUL_ESCURO,
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
            st.markdown(f'<div class="section-title">📊 REVISÕES POR RESPONSÁVEL</div>', unsafe_allow_html=True)
            
            col_rev_filtro1, col_rev_filtro2 = st.columns(2)
            
            with col_rev_filtro1:
                if 'Ano' in df.columns:
                    anos_rev = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_rev = ['Todos os Anos'] + list(anos_rev)
                    ano_rev = st.selectbox(
                        "📅 Filtrar por Ano:",
                        options=anos_opcoes_rev,
                        key="filtro_ano_revisoes"
                    )
            
            with col_rev_filtro2:
                if 'Mês' in df.columns:
                    meses_rev = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_rev = ['Todos os Meses'] + [str(m) for m in meses_rev]
                    mes_rev = st.selectbox(
                        "📆 Filtrar por Mês:",
                        options=meses_opcoes_rev,
                        key="filtro_mes_revisoes"
                    )
            
            df_rev = df.copy()
            
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
                    
                    fig_revisoes = go.Figure()
                    
                    max_revisoes = revisoes_por_responsavel['Total_Revisões'].max()
                    min_revisoes = revisoes_por_responsavel['Total_Revisões'].min()
                    
                    colors = []
                    for valor in revisoes_por_responsavel['Total_Revisões']:
                        if max_revisoes == min_revisoes:
                            colors.append(COR_VERMELHO)
                        else:
                            normalized = (valor - min_revisoes) / (max_revisoes - min_revisoes)
                            red = int(198 * normalized + 40 * (1 - normalized))
                            green = int(40 * normalized + 167 * (1 - normalized))
                            blue = int(40 * normalized + 69 * (1 - normalized))
                            colors.append(f'rgb({red}, {green}, {blue})')
                    
                    fig_revisoes.add_trace(go.Bar(
                        x=revisoes_por_responsavel['Responsável'].head(15),
                        y=revisoes_por_responsavel['Total_Revisões'].head(15),
                        name='Total de Revisões',
                        text=revisoes_por_responsavel['Total_Revisões'].head(15),
                        textposition='outside',
                        marker_color=colors[:15],
                        marker_line_color=COR_PRETO_SUAVE,
                        marker_line_width=1.5,
                        opacity=0.8
                    ))
                    
                    fig_revisoes.update_layout(
                        title='Top 15 Responsáveis com Mais Revisões',
                        xaxis_title='Responsável',
                        yaxis_title='Total de Revisões',
                        plot_bgcolor=COR_BRANCO,
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
            st.markdown(f'<div class="section-title">📈 CHAMADOS SINCRONIZADOS POR DIA</div>', unsafe_allow_html=True)
            
            if 'Status' in df.columns and 'Criado' in df.columns:
                df_sincronizados = df[df['Status'] == 'Sincronizado'].copy()
                
                if not df_sincronizados.empty:
                    df_sincronizados['Data'] = df_sincronizados['Criado'].dt.date
                    sinc_por_dia = df_sincronizados.groupby('Data').size().reset_index()
                    sinc_por_dia.columns = ['Data', 'Quantidade']
                    sinc_por_dia = sinc_por_dia.sort_values('Data')
                    
                    # Métricas
                    total_sinc = int(sinc_por_dia['Quantidade'].sum())
                    media_diaria = sinc_por_dia['Quantidade'].mean()
                    
                    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
                    
                    with col_kpi1:
                        st.metric("✅ Total Sincronizado", f"{total_sinc:,}")
                    
                    with col_kpi2:
                        st.metric("📊 Média Diária", f"{media_diaria:.1f}")
                    
                    with col_kpi3:
                        dia_max = sinc_por_dia.loc[sinc_por_dia['Quantidade'].idxmax()]
                        st.metric("📈 Dia com Mais Sinc.", f"{int(dia_max['Quantidade'])}", f"{dia_max['Data'].strftime('%d/%m/%Y')}")
                    
                    # Gráfico
                    fig_dias = go.Figure()
                    
                    fig_dias.add_trace(go.Bar(
                        x=sinc_por_dia['Data'].apply(lambda x: x.strftime('%d/%m')),
                        y=sinc_por_dia['Quantidade'],
                        name='Sincronizações',
                        text=sinc_por_dia['Quantidade'],
                        textposition='outside',
                        marker_color=COR_AZUL_ESCURO,
                        marker_line_color=COR_AZUL_PETROLEO,
                        marker_line_width=1.5,
                        opacity=0.8
                    ))
                    
                    fig_dias.update_layout(
                        title='Sincronizações por Dia',
                        xaxis_title='Data (Dia/Mês)',
                        yaxis_title='Quantidade',
                        height=400,
                        plot_bgcolor=COR_BRANCO,
                        showlegend=False,
                        margin=dict(t=50, b=50, l=50, r=50),
                        xaxis=dict(
                            gridcolor='rgba(0,0,0,0.05)',
                            tickangle=45
                        ),
                        yaxis=dict(
                            gridcolor='rgba(0,0,0,0.05)',
                            rangemode='tozero'
                        )
                    )
                    
                    st.plotly_chart(fig_dias, use_container_width=True)
                else:
                    st.warning("⚠️ Nenhum chamado sincronizado encontrado.")
    
    with tab_mapa:
        st.markdown("## 🗺️ Mapa de Sincronizações por Empresa")
        
        col_mapa_filtro1, col_mapa_filtro2, col_mapa_filtro3 = st.columns(3)
        
        with col_mapa_filtro1:
            empresas_disponiveis = df['Empresa'].dropna().unique()
            empresas_opcoes = ['Todas'] + sorted([e for e in empresas_disponiveis if e in MAPEAMENTO_EMPRESAS])
            
            empresas_selecionadas_mapa = st.multiselect(
                "🏢 Empresas",
                options=empresas_opcoes,
                default=['Todas'],
                key="mapa_empresas_folium"
            )
        
        with col_mapa_filtro2:
            if 'Ano' in df.columns:
                anos_disponiveis_mapa = sorted(df['Ano'].dropna().unique().astype(int))
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
            if 'Mês' in df.columns and ano_filtro_mapa != 'Todos':
                df_ano_mapa = df[df['Ano'] == int(ano_filtro_mapa)]
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
        
        df_mapa, total_sinc_filtrado = processar_dados_mapa(
            df,
            empresas_selecionadas=empresas_selecionadas_mapa,
            ano_filtro=ano_filtro_mapa,
            mes_filtro=mes_filtro_mapa
        )
        
        # Métricas
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
        st.markdown('<div class="section-title">📍 MAPA DE BOLHAS</div>', unsafe_allow_html=True)
        
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
        
        # Ranking
        fig_barras = criar_grafico_barras(df_mapa)
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True, config={'displayModeBar': True})
        
        # Tabela detalhada
        with st.expander("📋 Ver Detalhes por Empresa", expanded=False):
            if not df_mapa.empty:
                tabela_detalhes = df_mapa[['empresa_nome', 'sigla', 'estado', 'regiao', 'sincronismos']].copy()
                tabela_detalhes.columns = ['Empresa', 'UF', 'Estado', 'Região', 'Sincronizações']
                tabela_detalhes = tabela_detalhes.sort_values('Sincronizações', ascending=False).reset_index(drop=True)
                
                st.dataframe(tabela_detalhes, use_container_width=True)
                
                csv = tabela_detalhes.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Exportar dados para CSV",
                    data=csv,
                    file_name=f"sincronismos_empresas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    # ============================================
    # ABA KPI IPE
    # ============================================
    with tab_ipe:
        st.markdown(f'<div class="section-title">🎯 KPI IPE - ÍNDICE DE PERFORMANCE DO ESPECIALISTA</div>', unsafe_allow_html=True)
        
        if 'SRE' in df.columns and 'Status' in df.columns and 'Retorno_Cliente' in df.columns:
            
            def is_retorno_sim(valor):
                if pd.isna(valor):
                    return False
                valor_str = str(valor).strip().upper()
                return valor_str in ['SIM', 'S', 'YES', 'Y', '1', 'TRUE']
            
            def calcular_ipe(ca, cr, cd, ct, na):
                if cd <= 0 or na <= 0:
                    return 0
                numerador = ca - cr
                termo1 = ct / cd
                termo2 = termo1 / na
                modulo = abs(termo2 - 1)
                denominador = cd + modulo
                if denominador <= 0:
                    return 0
                ipe = numerador / denominador
                return min(ipe, 1.0)
            
            def substituir_nome_sre(sre_nome):
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
            
            # Filtros
            st.markdown("### 📅 Filtros de Período")
            col_filtro_ipe1, col_filtro_ipe2 = st.columns(2)
            
            with col_filtro_ipe1:
                if 'Ano' in df.columns:
                    anos_ipe = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_ipe = ['Todos'] + list(anos_ipe)
                    ano_ipe = st.selectbox("📅 Filtrar por Ano:", options=anos_opcoes_ipe, key="filtro_ano_ipe")
                else:
                    ano_ipe = 'Todos'
            
            with col_filtro_ipe2:
                if 'Mês' in df.columns:
                    meses_map = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
                    meses_disponiveis = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_ipe = [meses_map[m] for m in meses_disponiveis]
                    meses_selecionados_nomes = st.multiselect("📆 Selecionar Mês(es):", options=meses_opcoes_ipe, default=meses_opcoes_ipe, key="filtro_meses_ipe")
                    meses_invertido = {v: k for k, v in meses_map.items()}
                    meses_selecionados_numeros = [meses_invertido[m] for m in meses_selecionados_nomes] if meses_selecionados_nomes else []
                else:
                    meses_selecionados_numeros = []
            
            # Aplica filtros
            df_ipe = df.copy()
            if ano_ipe != 'Todos':
                df_ipe = df_ipe[df_ipe['Ano'] == int(ano_ipe)]
            if meses_selecionados_numeros:
                df_ipe = df_ipe[df_ipe['Mês'].isin(meses_selecionados_numeros)]
            
            # Performance detalhada
            st.markdown("### 📊 Performance Detalhada - Período Selecionado")
            cards_total_periodo = len(df_ipe)
            total_sres_periodo = df_ipe['SRE'].nunique()
            
            sres_metrics = []
            for sre in df_ipe['SRE'].dropna().unique():
                df_sre_data = df_ipe[df_ipe['SRE'] == sre]
                if len(df_sre_data) > 0:
                    cd = len(df_sre_data)
                    ca = len(df_sre_data[df_sre_data['Status'] == 'Sincronizado'])
                    cr = len(df_sre_data[df_sre_data['Retorno_Cliente'].apply(is_retorno_sim)])
                    
                    ipe = calcular_ipe(ca, cr, cd, cards_total_periodo, total_sres_periodo)
                    sres_metrics.append({
                        'SRE': substituir_nome_sre(sre),
                        'Cards Demandados': cd,
                        'Cards Analisados': ca,
                        'Cards Reabertos': cr,
                        'IPE (%)': round(ipe * 100, 2),
                        'Status': '✅ Meta' if ipe >= 0.95 else '⚠️ Abaixo'
                    })
            
            if sres_metrics:
                df_sres = pd.DataFrame(sres_metrics).sort_values('IPE (%)', ascending=False)
                st.dataframe(df_sres, use_container_width=True, column_config={
                    "SRE": st.column_config.TextColumn("SRE", width="small"),
                    "Cards Demandados": st.column_config.NumberColumn("Demandados", format="%d"),
                    "Cards Analisados": st.column_config.NumberColumn("Analisados", format="%d"),
                    "Cards Reabertos": st.column_config.NumberColumn("Reabertos", format="%d"),
                    "IPE (%)": st.column_config.ProgressColumn("IPE %", format="%.2f%%", min_value=0, max_value=100),
                    "Status": st.column_config.TextColumn("Status", width="small")
                })
            
            # IPE Acumulado
            st.markdown("---")
            st.markdown("### 📈 IPE Acumulado por Mês")
            
            if 'Criado' in df_ipe.columns and len(df_ipe) > 0:
                df_ipe['Periodo'] = df_ipe['Criado'].dt.strftime('%Y-%m')
                df_ipe['Nome_Mes_Completo'] = df_ipe['Criado'].dt.month.map({1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'})
                meses_ordenados = sorted(df_ipe['Periodo'].unique())
                
                acumulados = []
                for periodo in meses_ordenados:
                    df_ate = df_ipe[df_ipe['Periodo'] <= periodo]
                    
                    cd_acum = len(df_ate)
                    ca_acum = len(df_ate[df_ate['Status'] == 'Sincronizado'])
                    cr_acum = len(df_ate[df_ate['Retorno_Cliente'].apply(is_retorno_sim)])
                    na_acum = df_ate['SRE'].nunique()
                    
                    ipe_acum = calcular_ipe(ca_acum, cr_acum, cd_acum, cd_acum, na_acum)
                    
                    df_ate_sorted = df_ate.sort_values('Criado')
                    ultimo_mes_completo = df_ate_sorted['Nome_Mes_Completo'].iloc[-1] if len(df_ate_sorted) > 0 else periodo
                    
                    acumulados.append({
                        'Mês': ultimo_mes_completo,
                        'IPE Acumulado (%)': round(ipe_acum * 100, 2)
                    })
                
                if acumulados:
                    df_acum = pd.DataFrame(acumulados)
                    
                    fig_linha = go.Figure()
                    fig_linha.add_trace(go.Scatter(
                        x=df_acum['Mês'], 
                        y=df_acum['IPE Acumulado (%)'], 
                        mode='lines+markers+text', 
                        line=dict(color=COR_AZUL_ESCURO, width=4), 
                        marker=dict(size=12, color=COR_AZUL_PETROLEO), 
                        text=df_acum['IPE Acumulado (%)'].apply(lambda x: f'{x:.1f}%'), 
                        textposition='top center', 
                        name='IPE Acumulado'
                    ))
                    fig_linha.add_hline(y=95, line_dash="dash", line_color=COR_AZUL_PETROLEO, annotation_text="🎯 Meta 95%")
                    fig_linha.add_hline(y=100, line_dash="dot", line_color=COR_CINZA_TEXTO, annotation_text="Limite 100%")
                    fig_linha.update_layout(title='📈 Evolução do IPE Acumulado por Mês', xaxis_title='Mês', yaxis_title='IPE Acumulado (%)', yaxis=dict(range=[0, 105]), height=500, plot_bgcolor=COR_BRANCO)
                    st.plotly_chart(fig_linha, use_container_width=True)
            
            # Explicação
            with st.expander("📖 Entenda o Cálculo do IPE"):
                st.markdown("""
                **Fórmula:** `IPE = (CA - CR) / (CD + |((CT/CD)/NA) - 1|)`
                
                - **CA** = Cards Analisados (Sincronizados)
                - **CR** = Cards Reabertos (Cards com **'Retorno Cliente = Sim'**)
                - **CD** = Cards Demandados (Total do período)
                - **CT** = Cards Total (Total geral)
                - **NA** = Número de Atendentes (SREs únicos)
                
                **Meta: 95% | Limite máximo: 100%**
                """)
        else:
            st.warning("⚠️ Colunas necessárias ('SRE', 'Status', 'Retorno_Cliente') não encontradas.")
    
    # ============================================
    # ABA ANÁLISE ESTATÍSTICA
    # ============================================
    with tab_estatistica:
        st.markdown("## 📈 ANÁLISE ESTATÍSTICA")
        st.markdown("_Análise de distribuição, percentis e tendência de sincronizações_")
        
        col_filtro_est1, col_filtro_est2, col_filtro_est3 = st.columns(3)
        
        with col_filtro_est1:
            if 'Ano' in df.columns:
                anos_est = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_est = ['Todos os Anos'] + list(anos_est)
                ano_est = st.selectbox("📅 Ano", options=anos_opcoes_est, key="filtro_ano_est", index=0)
            else:
                ano_est = 'Todos os Anos'
        
        with col_filtro_est2:
            if 'Mês' in df.columns:
                if ano_est != 'Todos os Anos':
                    df_ano_est = df[df['Ano'] == int(ano_est)]
                    meses_est = sorted(df_ano_est['Mês'].dropna().unique().astype(int))
                    meses_opcoes_est = ['Todos os Meses'] + [f"{m:02d}" for m in meses_est]
                else:
                    meses_est = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_est = ['Todos os Meses'] + [f"{m:02d}" for m in meses_est]
                mes_est = st.selectbox("📆 Mês", options=meses_opcoes_est, key="filtro_mes_est", index=0)
            else:
                mes_est = 'Todos os Meses'
        
        with col_filtro_est3:
            percentil_param = st.number_input(
                "🎯 Percentil de Referência (%)",
                min_value=50,
                max_value=99,
                value=75,
                step=5,
                key="percentil_param"
            )
        
        df_est = df.copy()
        if ano_est != 'Todos os Anos':
            df_est = df_est[df_est['Ano'] == int(ano_est)]
        if mes_est != 'Todos os Meses':
            df_est = df_est[df_est['Mês'] == int(mes_est)]
        
        df_sinc_est = df_est[df_est['Status'] == 'Sincronizado'].copy()
        
        if df_sinc_est.empty:
            st.warning("⚠️ Nenhum dado sincronizado encontrado com os filtros selecionados.")
        else:
            st.markdown("---")
            st.markdown("### 📊 DISTRIBUIÇÃO E PERCENTIS")
            
            if 'Criado' in df_sinc_est.columns:
                df_sinc_est['Data'] = df_sinc_est['Criado'].dt.date
                sinc_por_dia_est = df_sinc_est.groupby('Data').size().reset_index()
                sinc_por_dia_est.columns = ['Data', 'Quantidade']
                
                if not sinc_por_dia_est.empty:
                    valores = sinc_por_dia_est['Quantidade']
                    
                    mediana = valores.median()
                    q1 = valores.quantile(0.25)
                    q3 = valores.quantile(0.75)
                    p10 = valores.quantile(0.10)
                    p90 = valores.quantile(0.90)
                    p_selecionado = valores.quantile(percentil_param/100)
                    
                    fig_sep = go.Figure()
                    
                    fig_sep.add_trace(go.Histogram(
                        x=valores,
                        nbinsx=20,
                        name='Frequência',
                        marker_color='rgba(2, 138, 159, 0.5)',
                        marker_line_color=COR_AZUL_ESCURO,
                        marker_line_width=1
                    ))
                    
                    fig_sep.add_vline(x=mediana, line_dash="dash", line_color=COR_VERDE_ESCURO, 
                                      annotation_text=f"P50 (Mediana): {mediana:.0f}", annotation_position="top")
                    fig_sep.add_vline(x=q1, line_dash="dot", line_color=COR_AZUL_PETROLEO,
                                      annotation_text=f"Q1 (P25): {q1:.0f}", annotation_position="top")
                    fig_sep.add_vline(x=q3, line_dash="dot", line_color=COR_AZUL_PETROLEO,
                                      annotation_text=f"Q3 (P75): {q3:.0f}", annotation_position="top")
                    fig_sep.add_vline(x=p_selecionado, line_dash="dash", line_color=COR_VERMELHO, line_width=3,
                                      annotation_text=f"P{percentil_param}: {p_selecionado:.0f}", annotation_position="bottom")
                    
                    fig_sep.update_layout(
                        title=f'Distribuição de Sincronizações Diárias',
                        xaxis_title='Número de Sincronizações por Dia',
                        yaxis_title='Frequência',
                        height=450,
                        plot_bgcolor=COR_BRANCO,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_sep, use_container_width=True)
                    
                    col_sep1, col_sep2, col_sep3, col_sep4, col_sep5 = st.columns(5)
                    with col_sep1: st.metric("📊 P10", f"{p10:.0f}")
                    with col_sep2: st.metric("📊 Q1 (P25)", f"{q1:.0f}")
                    with col_sep3: st.metric("📊 Mediana (P50)", f"{mediana:.0f}")
                    with col_sep4: st.metric("📊 Q3 (P75)", f"{q3:.0f}")
                    with col_sep5: st.metric(f"🎯 P{percentil_param}", f"{p_selecionado:.0f}")

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

st.markdown("---")

ultima_atualizacao = st.session_state.get('ultima_atualizacao', get_horario_brasilia())

st.markdown(f"""
<div class="footer">
    <div style="margin-bottom: 0.8rem;">
        <p style="margin: 0; color: {COR_PRETO_SUAVE}; font-weight: 500;">
        Desenvolvido por: <span style="color: {COR_AZUL_ESCURO};">Time SRE | GAUT</span>
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
