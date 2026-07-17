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
            'ChangeSet': 'ChangeSet'
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

def criar_popup_indicadores(df):
    """Cria popup modal com indicadores principais"""
    hoje = datetime.now()
    mes_atual = hoje.month
    ano_atual = hoje.year
    nome_mes = hoje.strftime('%B').capitalize()
    
    meses_pt = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
        'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
        'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
        'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    }
    nome_mes_pt = meses_pt.get(nome_mes, nome_mes)
    
    df_mes = df[(df['Criado'].dt.month == mes_atual) & 
                (df['Criado'].dt.year == ano_atual)].copy()
    
    total_cards_mes = len(df_mes)
    cards_validados = len(df_mes[df_mes['Status'] == 'Sincronizado'])
    cards_com_erro = len(df_mes[df_mes['Revisões'] > 0])
    cards_sem_erro = cards_validados - cards_com_erro
    
    taxa_sucesso = (cards_validados / total_cards_mes * 100) if total_cards_mes > 0 else 0
    taxa_erro = (cards_com_erro / cards_validados * 100) if cards_validados > 0 else 0
    
    mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
    ano_anterior = ano_atual if mes_atual > 1 else ano_atual - 1
    
    df_mes_anterior = df[(df['Criado'].dt.month == mes_anterior) & 
                         (df['Criado'].dt.year == ano_anterior)].copy()
    
    cards_validados_anterior = len(df_mes_anterior[df_mes_anterior['Status'] == 'Sincronizado'])
    
    if cards_validados_anterior > 0:
        variacao = ((cards_validados - cards_validados_anterior) / cards_validados_anterior * 100)
    else:
        variacao = 0
    
    if cards_com_erro == 0:
        texto_principal = f"✅ **SRE VALIDOU {cards_validados} CARDS SEM RETORNO DE ERRO!**"
        subtexto = f"Performance excepcional em {nome_mes_pt} - 100% de aprovação direta"
        emoji_titulo = "🎯"
        cor_destaque = COR_VERDE_ESCURO
    elif taxa_erro <= 5:
        texto_principal = f"⚡ **SRE VALIDOU {cards_validados} CARDS COM APENAS {cards_com_erro} AJUSTES**"
        subtexto = f"Alta qualidade no mês de {nome_mes_pt} - Taxa de erro de apenas {taxa_erro:.1f}%"
        emoji_titulo = "🚀"
        cor_destaque = COR_AZUL_PETROLEO
    else:
        texto_principal = f"📊 **SRE VALIDOU {cards_validados} CARDS, {cards_com_erro} COM RETORNO**"
        subtexto = f"Análise de {nome_mes_pt} - {taxa_sucesso:.1f}% de taxa de sucesso"
        emoji_titulo = "📈"
        cor_destaque = COR_LARANJA
    
    popup_html = f'''
    <div id="popupOverlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(0, 0, 0, 0.7); z-index: 10000; display: flex; 
                justify-content: center; align-items: center; backdrop-filter: blur(3px);">
        <div style="background: {COR_BRANCO}; width: 90%; max-width: 900px; max-height: 90vh;
                    border-radius: 12px; padding: 0; overflow: hidden; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.3); animation: slideIn 0.3s ease-out;">
            
            <div style="background: linear-gradient(135deg, {COR_AZUL_ESCURO}, {COR_AZUL_PETROLEO}); 
                        padding: 1.5rem 2rem; color: {COR_BRANCO};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="margin: 0; font-size: 1.6rem;">{emoji_titulo} MANCHETE DO MÊS</h2>
                        <p style="margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">
                        {nome_mes_pt} {ano_atual} | Resumo Executivo
                        </p>
                    </div>
                    <button onclick="document.getElementById('popupOverlay').style.display='none'" 
                            style="background: rgba(255,255,255,0.2); color: {COR_BRANCO}; 
                                   border: none; width: 36px; height: 36px; 
                                   border-radius: 50%; font-size: 1.3rem; 
                                   cursor: pointer;">×</button>
                </div>
            </div>
            
            <div style="padding: 2rem;">
                <div style="background: {cor_destaque}10; padding: 1.5rem; border-radius: 8px; 
                            border-left: 4px solid {cor_destaque}; margin-bottom: 2rem;">
                    <h3 style="color: {COR_PRETO_SUAVE}; margin: 0 0 0.5rem 0; font-size: 1.1rem;">{texto_principal}</h3>
                    <p style="color: {COR_CINZA_TEXTO}; margin: 0; font-size: 0.9rem;">{subtexto}</p>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 2rem;">
                    <div style="background: {COR_CINZA_FUNDO}; padding: 1.2rem; border-radius: 8px; border-top: 3px solid {COR_AZUL_ESCURO};">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="background: {COR_AZUL_ESCURO}; color: {COR_BRANCO}; width: 45px; height: 45px; 
                                        border-radius: 8px; display: flex; align-items: center; 
                                        justify-content: center; font-size: 1.3rem;">📋</div>
                            <div>
                                <div style="font-size: 1.8rem; font-weight: 700; color: {COR_AZUL_ESCURO};">
                                    {total_cards_mes}
                                </div>
                                <div style="color: {COR_CINZA_TEXTO}; font-size: 0.8rem;">TOTAL DE CARDS</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: {COR_CINZA_FUNDO}; padding: 1.2rem; border-radius: 8px; border-top: 3px solid {COR_VERDE_ESCURO};">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="background: {COR_VERDE_ESCURO}; color: {COR_BRANCO}; width: 45px; height: 45px; 
                                        border-radius: 8px; display: flex; align-items: center; 
                                        justify-content: center; font-size: 1.3rem;">✅</div>
                            <div>
                                <div style="font-size: 1.8rem; font-weight: 700; color: {COR_VERDE_ESCURO};">
                                    {cards_validados}
                                </div>
                                <div style="color: {COR_CINZA_TEXTO}; font-size: 0.8rem;">VALIDADOS PELO SRE</div>
                            </div>
                        </div>
                        <p style="color: {COR_CINZA_TEXTO}; margin: 0.5rem 0 0 0; font-size: 0.75rem;">
                        {variacao:+.1f}% vs mês anterior
                        </p>
                    </div>
                    
                    <div style="background: {COR_CINZA_FUNDO}; padding: 1.2rem; border-radius: 8px; border-top: 3px solid {COR_AZUL_PETROLEO};">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="background: {COR_AZUL_PETROLEO}; color: {COR_BRANCO}; width: 45px; height: 45px; 
                                        border-radius: 8px; display: flex; align-items: center; 
                                        justify-content: center; font-size: 1.3rem;">🎯</div>
                            <div>
                                <div style="font-size: 1.8rem; font-weight: 700; color: {COR_AZUL_PETROLEO};">
                                    {cards_sem_erro}
                                </div>
                                <div style="color: {COR_CINZA_TEXTO}; font-size: 0.8rem;">SEM RETORNO DE ERRO</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: {COR_CINZA_FUNDO}; padding: 1.2rem; border-radius: 8px; border-top: 3px solid {COR_VERMELHO if cards_com_erro > 0 else COR_CINZA_TEXTO};">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="background: {COR_VERMELHO if cards_com_erro > 0 else COR_CINZA_TEXTO}; 
                                        color: {COR_BRANCO}; width: 45px; height: 45px; 
                                        border-radius: 8px; display: flex; align-items: center; 
                                        justify-content: center; font-size: 1.3rem;">{'⚠️' if cards_com_erro > 0 else '✅'}</div>
                            <div>
                                <div style="font-size: 1.8rem; font-weight: 700; 
                                            color: {COR_VERMELHO if cards_com_erro > 0 else COR_CINZA_TEXTO}">
                                    {cards_com_erro}
                                </div>
                                <div style="color: {COR_CINZA_TEXTO}; font-size: 0.8rem;">COM RETORNO DE ERRO</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1rem;">
                    <div style="background: {COR_CINZA_FUNDO}; padding: 1rem; border-radius: 8px;">
                        <h4 style="color: {COR_PRETO_SUAVE}; margin: 0 0 1rem 0;">📈 EVOLUÇÃO MENSAL</h4>
                        <div style="height: 180px; display: flex; align-items: end; gap: 20px;">
                            <div style="text-align: center; flex: 1;">
                                <div style="background: {COR_CINZA_TEXTO}; height: {max(10, min(100, cards_validados_anterior/5))}px; 
                                            border-radius: 4px 4px 0 0;"></div>
                                <div style="margin-top: 8px; font-size: 0.8rem; color: {COR_CINZA_TEXTO};">
                                    {mes_anterior:02d}/{ano_anterior}
                                </div>
                                <div style="font-weight: bold; color: {COR_PRETO_SUAVE};">{cards_validados_anterior}</div>
                            </div>
                            <div style="text-align: center; flex: 1;">
                                <div style="background: {COR_VERDE_ESCURO}; height: {max(10, min(100, cards_validados/5))}px; 
                                            border-radius: 4px 4px 0 0;"></div>
                                <div style="margin-top: 8px; font-size: 0.8rem; color: {COR_CINZA_TEXTO};">
                                    {mes_atual:02d}/{ano_atual}
                                </div>
                                <div style="font-weight: bold; color: {COR_PRETO_SUAVE};">{cards_validados}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: #FFF8E1; padding: 1rem; border-radius: 8px; border-left: 4px solid {COR_LARANJA};">
                        <h4 style="color: {COR_LARANJA}; margin: 0 0 0.8rem 0;">💡 INSIGHTS</h4>
                        <ul style="color: {COR_CINZA_TEXTO}; padding-left: 1.2rem; margin: 0; font-size: 0.85rem;">
                            <li style="margin-bottom: 0.5rem;">
                                {f"🎉 Recorde de validações!" if variacao > 20 else "📊 Performance consistente"}
                            </li>
                            <li style="margin-bottom: 0.5rem;">
                                {f"✅ Qualidade excepcional" if cards_com_erro == 0 else f"🎯 {cards_sem_erro} cards perfeitos"}
                            </li>
                            <li>
                                {f"🚀 Meta atingida: {taxa_sucesso:.0f}% de sucesso" if taxa_sucesso >= 90 else f"📈 Oportunidade: melhorar {100-taxa_sucesso:.0f}%"}
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div style="background: {COR_CINZA_FUNDO}; padding: 1rem 2rem; border-top: 1px solid {COR_CINZA_BORDA};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <p style="color: {COR_CINZA_TEXTO}; margin: 0; font-size: 0.8rem;">
                    📅 Atualizado em {hoje.strftime('%d/%m/%Y %H:%M')}
                    </p>
                    <button onclick="document.getElementById('popupOverlay').style.display='none'"
                            style="background: {COR_AZUL_ESCURO}; color: {COR_BRANCO}; border: none; 
                                   padding: 0.5rem 1.2rem; border-radius: 6px; 
                                   cursor: pointer; font-weight: 500;">
                        Fechar
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <style>
    @keyframes slideIn {{
        from {{ transform: translateY(-30px); opacity: 0; }}
        to {{ transform: translateY(0); opacity: 1; }}
    }}
    </style>
    '''
    
    return popup_html

def calcular_taxa_retorno_sre(df, sre_nome):
    """Calcula taxa de retorno específica para um SRE"""
    df_sre = df[df['SRE'] == sre_nome].copy()
    
    if len(df_sre) == 0:
        return 0, 0, 0
    
    total_cards = len(df_sre)
    
    if 'Revisões' in df_sre.columns:
        cards_com_revisoes = len(df_sre[df_sre['Revisões'] > 0])
        taxa_retorno = (cards_com_revisoes / total_cards * 100) if total_cards > 0 else 0
    else:
        taxa_retorno = 0
        cards_com_revisoes = 0
    
    cards_sincronizados = len(df_sre[df_sre['Status'] == 'Sincronizado'])
    
    return taxa_retorno, cards_com_revisoes, cards_sincronizados

def criar_matriz_performance_dev(df):
    """Cria matriz de performance (Eficiência vs Qualidade) para Desenvolvedores"""
    devs = df['Responsável_Formatado'].dropna().unique()
    matriz_data = []
    
    for dev in devs:
        df_dev = df[df['Responsável_Formatado'] == dev].copy()
        
        if len(df_dev) == 0:
            continue
        
        total_cards = len(df_dev)
        
        if 'Criado' in df_dev.columns:
            meses_ativos = df_dev['Criado'].dt.to_period('M').nunique()
            eficiencia = total_cards / max(meses_ativos, 1)
        else:
            eficiencia = total_cards
        
        if 'Revisões' in df_dev.columns:
            cards_sem_revisao = len(df_dev[df_dev['Revisões'] == 0])
            qualidade = (cards_sem_revisao / total_cards * 100) if total_cards > 0 else 0
        else:
            qualidade = 100
        
        score = (qualidade * 0.5) + (eficiencia * 5 * 0.3) + ((total_cards / max(len(df), 1)) * 100 * 0.2)
        
        matriz_data.append({
            'Desenvolvedor': dev,
            'Eficiencia': round(eficiencia, 1),
            'Qualidade': round(qualidade, 1),
            'Score': round(score, 1),
            'Total_Cards': total_cards
        })
    
    return pd.DataFrame(matriz_data)

def analisar_tendencia_mensal_sre(df, sre_nome):
    """Analisa tendência mensal de sincronizações de um SRE"""
    df_sre = df[df['SRE'] == sre_nome].copy()
    
    if len(df_sre) == 0 or 'Criado' not in df_sre.columns:
        return None
    
    df_sre['Mes_Ano'] = df_sre['Criado'].dt.strftime('%Y-%m')
    
    sinc_mes = df_sre[df_sre['Status'] == 'Sincronizado'].groupby('Mes_Ano').size().reset_index()
    sinc_mes.columns = ['Mes_Ano', 'Sincronizados']
    
    total_mes = df_sre.groupby('Mes_Ano').size().reset_index()
    total_mes.columns = ['Mes_Ano', 'Total']
    
    dados_mes = pd.merge(total_mes, sinc_mes, on='Mes_Ano', how='left').fillna(0)
    
    dados_mes = dados_mes.sort_values('Mes_Ano')
    
    return dados_mes

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

def analisar_motivos_revisao(df, ano_selecionado, mes_selecionado):
    """Analisa os motivos de revisão com filtros"""
    df_filtrado = df[df['Revisões'] > 0].copy()
    
    if df_filtrado.empty:
        return None, None, None, None
    
    if 'Motivo_Revisao' not in df_filtrado.columns:
        return None, None, None, None
    
    # Aplicar filtros de data
    if ano_selecionado != 'Todos os Anos':
        df_filtrado = df_filtrado[df_filtrado['Ano'] == int(ano_selecionado)]
    
    if mes_selecionado != 'Todos os Meses':
        df_filtrado = df_filtrado[df_filtrado['Mês'] == int(mes_selecionado)]
    
    if df_filtrado.empty:
        return None, None, None, None
    
    # Classificar motivos
    df_filtrado['Categoria_Motivo'] = df_filtrado['Motivo_Revisao'].apply(classificar_motivo_revisao)
    
    # Remover linhas com texto vazio após classificação
    df_filtrado = df_filtrado[df_filtrado['Categoria_Motivo'] != "📝 Sem motivo informado"]
    
    if df_filtrado.empty:
        return None, None, None, None
    
    # Estatísticas por categoria
    estatisticas_categoria = df_filtrado.groupby('Categoria_Motivo').agg({
        'Chamado': 'count',
        'Revisões': 'sum'
    }).reset_index()
    estatisticas_categoria.columns = ['Categoria', 'Quantidade', 'Total_Revisões']
    estatisticas_categoria = estatisticas_categoria.sort_values('Quantidade', ascending=False)
    estatisticas_categoria['Percentual'] = (estatisticas_categoria['Quantidade'] / estatisticas_categoria['Quantidade'].sum() * 100).round(1)
    
    # Top motivos individuais
    motivos_contagem = df_filtrado['Motivo_Revisao'].value_counts().reset_index()
    motivos_contagem.columns = ['Motivo', 'Quantidade']
    motivos_contagem['Percentual'] = (motivos_contagem['Quantidade'] / motivos_contagem['Quantidade'].sum() * 100).round(1)
    motivos_contagem = motivos_contagem.head(15)
    
    # Análise por Responsável
    if 'Responsável_Formatado' in df_filtrado.columns:
        responsavel_categoria = df_filtrado.groupby(['Responsável_Formatado', 'Categoria_Motivo']).size().reset_index()
        responsavel_categoria.columns = ['Responsável', 'Categoria', 'Quantidade']
        
        responsavel_pivot = responsavel_categoria.pivot_table(
            index='Responsável', 
            columns='Categoria', 
            values='Quantidade', 
            fill_value=0
        ).reset_index()
    else:
        responsavel_pivot = None
    
    total_com_revisao = len(df_filtrado)
    
    return estatisticas_categoria, motivos_contagem, responsavel_pivot, total_com_revisao

# ============================================
# FUNÇÕES DO MAPA - PROCESSAMENTO DE DADOS
# ============================================
def processar_dados_mapa(df, empresas_selecionadas=None, ano_filtro=None, mes_filtro=None):
    """Processa os dados para gerar as métricas do mapa"""
    
    # Filtrar apenas sincronizados
    df_sinc = df[df['Status'] == 'Sincronizado'].copy()
    
    # REMOVER PROJETOS INTERNOS DAS CONTAGENS
    #if 'Tipo_Chamado' in df_sinc.columns:
        #df_sinc = df_sinc[df_sinc['Tipo_Chamado'] != 'Projetos Internos']
    
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
# FUNÇÕES PARA ANÁLISE ADMS vs ELIPSE
# ============================================
def classificar_origem_changeset(row):
    """
    Classifica a origem do chamado baseado no ChangeSet.
    ADMS: Telemetry e Manuals
    ELIPSE: Elipse
    """
    # Verificar se a coluna ChangeSet existe
    if 'ChangeSet' not in row.index:
        return 'Não Classificado'
    
    changeset = str(row['ChangeSet']).upper().strip()
    
    # Verificar se o valor é vazio ou NaN
    if pd.isna(changeset) or changeset == '' or changeset == 'NAN':
        return 'Não Classificado'
    
    # Classificação baseada no ChangeSet
    if 'TELEMETRY' in changeset:
        return 'ADMS - Telemetry'
    elif 'MANUALS' in changeset or 'MANUAL' in changeset:
        return 'ADMS - Manual'
    elif 'ELIPSE' in changeset:
        return 'ELIPSE'
    else:
        return 'Outros'

def analisar_adms_elipse(df, ano_filtro=None, mes_filtro=None, empresa_filtro=None, sre_filtro=None):
    """
    Analisa os chamados comparando ADMS (Telemetry e Manuals) vs ELIPSE
    Baseado no campo 'ChangeSet'
    """
    # Filtra apenas sincronizados
    df_analise = df[df['Status'] == 'Sincronizado'].copy()
    
    # Aplica filtros
    if ano_filtro and ano_filtro != 'Todos os Anos':
        df_analise = df_analise[df_analise['Ano'] == int(ano_filtro)]
    
    if mes_filtro and mes_filtro != 'Todos os Meses':
        df_analise = df_analise[df_analise['Mês'] == int(mes_filtro)]
    
    if empresa_filtro and empresa_filtro != 'Todas':
        df_analise = df_analise[df_analise['Empresa'] == empresa_filtro]
    
    if sre_filtro and sre_filtro != 'Todos':
        df_analise = df_analise[df_analise['SRE'] == sre_filtro]
    
    if df_analise.empty:
        return None
    
    # Verificar se a coluna ChangeSet existe
    if 'ChangeSet' not in df_analise.columns:
        return None
    
    # Classifica a origem baseada no ChangeSet
    df_analise['Origem'] = df_analise.apply(classificar_origem_changeset, axis=1)
    
    # Remove não classificados para análise focada
    df_classificados = df_analise[df_analise['Origem'] != 'Não Classificado']
    df_classificados = df_classificados[df_classificados['Origem'] != 'Outros']
    
    if df_classificados.empty:
        return None
    
    # Métricas gerais
    total_classificados = len(df_classificados)
    
    # Contagem por origem
    contagem_origem = df_classificados['Origem'].value_counts().reset_index()
    contagem_origem.columns = ['Origem', 'Quantidade']
    contagem_origem['Percentual'] = (contagem_origem['Quantidade'] / total_classificados * 100).round(1)
    
    # Análise por empresa
    empresa_origem = df_classificados.groupby(['Empresa', 'Origem']).size().reset_index()
    empresa_origem.columns = ['Empresa', 'Origem', 'Quantidade']
    
    # Análise por SRE
    sre_origem = df_classificados.groupby(['SRE', 'Origem']).size().reset_index()
    sre_origem.columns = ['SRE', 'Origem', 'Quantidade']
    
    # Análise temporal (por mês)
    df_classificados['Mês_Ano'] = df_classificados['Criado'].dt.strftime('%Y-%m')
    temporal_origem = df_classificados.groupby(['Mês_Ano', 'Origem']).size().reset_index()
    temporal_origem.columns = ['Mês_Ano', 'Origem', 'Quantidade']
    
    # Percentual de cada origem no total
    adms_telemetry = contagem_origem[contagem_origem['Origem'] == 'ADMS - Telemetry']['Quantidade'].sum() if 'ADMS - Telemetry' in contagem_origem['Origem'].values else 0
    adms_manual = contagem_origem[contagem_origem['Origem'] == 'ADMS - Manual']['Quantidade'].sum() if 'ADMS - Manual' in contagem_origem['Origem'].values else 0
    elipse = contagem_origem[contagem_origem['Origem'] == 'ELIPSE']['Quantidade'].sum() if 'ELIPSE' in contagem_origem['Origem'].values else 0
    
    total_adms = adms_telemetry + adms_manual
    
    return {
        'df_classificados': df_classificados,
        'contagem_origem': contagem_origem,
        'empresa_origem': empresa_origem,
        'sre_origem': sre_origem,
        'temporal_origem': temporal_origem,
        'total_classificados': total_classificados,
        'total_adms': total_adms,
        'total_elipse': elipse,
        'adms_telemetry': adms_telemetry,
        'adms_manual': adms_manual,
        'pct_adms': (total_adms / total_classificados * 100) if total_classificados > 0 else 0,
        'pct_elipse': (elipse / total_classificados * 100) if total_classificados > 0 else 0
    }

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
                📊 ESTEIRA SRE
            </h1>
            <p style="
                color: rgba(255,255,255,0.9);
                margin: 0.3rem 0 0 0;
                font-size: 0.85rem;
                font-weight: 400;
            ">
                Acompanhamento de Demandas - EAC | EMR | EMS | EMT | EPB | ERO | ESE | ESS | ETO
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
# BOTÕES MANCHETE
# ============================================
if st.session_state.df_original is not None:
    if 'show_popup' not in st.session_state:
        st.session_state.show_popup = False
    
    col_btn_manchete, col_espaco = st.columns([2, 10])
    
    with col_btn_manchete:
        if st.button("📰 **VER MANCHETE**", 
                    help="Clique para ver os principais indicadores do mês",
                    type="secondary",
                    use_container_width=True,
                    key="btn_manchete"):
            st.session_state.show_popup = True

if st.session_state.df_original is not None:
    if verificar_e_atualizar_arquivo():
        st.info("🔔 O arquivo local foi atualizado! Clique em 'Recarregar Local' na barra lateral para atualizar os dados.")

if st.session_state.df_original is not None and st.session_state.show_popup:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    with st.expander("📰 MANCHETE - INDICADORES PRINCIPAIS", expanded=True):
        
        st.markdown("### 📰 MANCHETE - RELATÓRIO ")
        st.markdown("---")
        
        st.markdown("#### 📅 SELECIONE O PERÍODO")
        
        col_periodo1, col_periodo2 = st.columns(2)
        
        with col_periodo1:
            periodo_opcoes = [
                "Mês Atual",
                "Últimos 30 dias", 
                "Últimos 90 dias",
                "Este Ano",
                "Ano Passado",
                "Todo o Período"
            ]
            periodo_selecionado = st.selectbox(
                "Período de análise:",
                options=periodo_opcoes,
                index=0,
                key="popup_periodo"
            )
        
        with col_periodo2:
            if 'Ano' in df.columns:
                anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                if anos_disponiveis:
                    ano_especifico = st.selectbox(
                        "Ou selecione um ano:",
                        options=['Selecionar ano...'] + list(anos_disponiveis),
                        key="popup_ano"
                    )
                else:
                    ano_especifico = 'Selecionar ano...'
            else:
                ano_especifico = 'Selecionar ano...'
        
        hoje = datetime.now()
        df_filtrado_periodo = df.copy()
        periodo_titulo = ""
        
        if periodo_selecionado == "Mês Atual":
            mes_atual = hoje.month
            ano_atual = hoje.year
            df_filtrado_periodo = df[(df['Criado'].dt.month == mes_atual) & 
                                    (df['Criado'].dt.year == ano_atual)].copy()
            periodo_titulo = f"Mês Atual ({mes_atual:02d}/{ano_atual})"
            
        elif periodo_selecionado == "Últimos 30 dias":
            data_limite = hoje - timedelta(days=30)
            df_filtrado_periodo = df[df['Criado'] >= data_limite].copy()
            periodo_titulo = "Últimos 30 dias"
            
        elif periodo_selecionado == "Últimos 90 dias":
            data_limite = hoje - timedelta(days=90)
            df_filtrado_periodo = df[df['Criado'] >= data_limite].copy()
            periodo_titulo = "Últimos 90 dias"
            
        elif periodo_selecionado == "Este Ano":
            ano_atual = hoje.year
            df_filtrado_periodo = df[df['Criado'].dt.year == ano_atual].copy()
            periodo_titulo = f"Este Ano ({ano_atual})"
            
        elif periodo_selecionado == "Ano Passado":
            ano_passado = hoje.year - 1
            df_filtrado_periodo = df[df['Criado'].dt.year == ano_passado].copy()
            periodo_titulo = f"Ano Passado ({ano_passado})"
            
        elif periodo_selecionado == "Todo o Período":
            periodo_titulo = "Todo o Período Disponíve"
            
        elif ano_especifico != 'Selecionar ano...':
            df_filtrado_periodo = df[df['Criado'].dt.year == int(ano_especifico)].copy()
            periodo_titulo = f"Ano {ano_especifico}"
        
        total_cards = len(df_filtrado_periodo)
        validados = len(df_filtrado_periodo[df_filtrado_periodo['Status'] == 'Sincronizado'])
        com_erro = len(df_filtrado_periodo[df_filtrado_periodo['Revisões'] > 0])
        sem_erro = validados - com_erro
        
        taxa_sucesso = (validados / total_cards * 100) if total_cards > 0 else 0
        taxa_erro = (com_erro / validados * 100) if validados > 0 else 0
        
        df_anterior = pd.DataFrame()
        periodo_anterior_titulo = ""
        
        try:
            if periodo_selecionado == "Mês Atual":
                mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
                ano_anterior = ano_atual if mes_atual > 1 else ano_atual - 1
                df_anterior = df[(df['Criado'].dt.month == mes_anterior) & 
                                (df['Criado'].dt.year == ano_anterior)].copy()
                periodo_anterior_titulo = f"{mes_anterior:02d}/{ano_anterior}"
                
            elif periodo_selecionado == "Últimos 30 dias":
                data_inicio_anterior = hoje - timedelta(days=60)
                data_fim_anterior = hoje - timedelta(days=30)
                df_anterior = df[(df['Criado'] >= data_inicio_anterior) & 
                                (df['Criado'] < data_fim_anterior)].copy()
                periodo_anterior_titulo = "30 dias anteriores"
                
            elif periodo_selecionado == "Últimos 90 dias":
                data_inicio_anterior = hoje - timedelta(days=180)
                data_fim_anterior = hoje - timedelta(days=90)
                df_anterior = df[(df['Criado'] >= data_inicio_anterior) & 
                                (df['Criado'] < data_fim_anterior)].copy()
                periodo_anterior_titulo = "90 dias anteriores"
                
            elif periodo_selecionado == "Este Ano":
                ano_anterior = ano_atual - 1
                df_anterior = df[df['Criado'].dt.year == ano_anterior].copy()
                periodo_anterior_titulo = f"Ano {ano_anterior}"
                
            elif periodo_selecionado == "Ano Passado":
                ano_anterior_2 = ano_passado - 1
                df_anterior = df[df['Criado'].dt.year == ano_anterior_2].copy()
                periodo_anterior_titulo = f"Ano {ano_anterior_2}"
                
        except Exception as e:
            df_anterior = pd.DataFrame()
        
        if not df_anterior.empty:
            total_cards_anterior = len(df_anterior)
            validados_anterior = len(df_anterior[df_anterior['Status'] == 'Sincronizado'])
            com_erro_anterior = len(df_anterior[df_anterior['Revisões'] > 0])
            taxa_sucesso_anterior = (validados_anterior / total_cards_anterior * 100) if total_cards_anterior > 0 else 0
        else:
            total_cards_anterior = 0
            validados_anterior = 0
            com_erro_anterior = 0
            taxa_sucesso_anterior = 0
        
        st.markdown(f"#### 🎯 DESTAQUE DO PERÍODO: {periodo_titulo}")
        
        if total_cards == 0:
            st.error(f"⚠️ **NENHUM DADO DISPONÍVEL** para {periodo_titulo.lower()}")
        elif com_erro == 0 and validados > 0:
            st.success(f"**✅ SRE VALIDOU {validados} CARDS SEM RETORNO DE ERRO!**")
            st.info(f"Performance excepcional - 100% de aprovação direta")
        elif taxa_erro <= 5:
            st.warning(f"**⚡ SRE VALIDOU {validados} CARDS COM APENAS {com_erro} AJUSTES**")
            st.info(f"Alta qualidade - Taxa de erro: {taxa_erro:.1f}%")
        else:
            st.warning(f"**📊 SRE VALIDOU {validados} CARDS, {com_erro} COM RETORNO**")
            st.info(f"Taxa de sucesso: {taxa_sucesso:.1f}% | {sem_erro} cards perfeitos")
        
        st.markdown("---")
        
        if not df_anterior.empty and total_cards_anterior > 0:
            st.markdown("#### 📈 COMPARAÇÃO COM PERÍODO ANTERIOR")
            
            periodos = [periodo_anterior_titulo, periodo_titulo]
            cards_totais = [total_cards_anterior, total_cards]
            cards_validados = [validados_anterior, validados]
            taxa_sucesso_vals = [taxa_sucesso_anterior, taxa_sucesso]
            
            fig_comparativo = go.Figure()
            
            fig_comparativo.add_trace(go.Bar(
                x=periodos,
                y=cards_totais,
                name='Total Cards',
                marker_color=COR_AZUL_ESCURO,
                text=cards_totais,
                textposition='outside',
                textfont=dict(size=10),
                width=0.35
            ))
            
            fig_comparativo.add_trace(go.Bar(
                x=periodos,
                y=cards_validados,
                name='Validados',
                marker_color=COR_VERDE_ESCURO,
                text=cards_validados,
                textposition='outside',
                textfont=dict(size=10),
                width=0.35
            ))
            
            fig_comparativo.add_trace(go.Scatter(
                x=periodos,
                y=taxa_sucesso_vals,
                name='Taxa Sucesso',
                yaxis='y2',
                mode='lines+markers+text',
                line=dict(color=COR_LARANJA, width=2),
                marker=dict(size=8, color=COR_LARANJA),
                text=[f"{v:.1f}%" for v in taxa_sucesso_vals],
                textposition='top center',
                textfont=dict(size=9)
            ))
            
            fig_comparativo.update_layout(
                title=dict(
                    text='Comparativo: Período Atual vs Anterior',
                    font=dict(size=14)
                ),
                barmode='group',
                yaxis=dict(
                    title=dict(text='Quantidade', font=dict(size=11)),
                    gridcolor='rgba(0,0,0,0.05)',
                    rangemode='tozero'
                ),
                yaxis2=dict(
                    title=dict(text='Taxa Sucesso (%)', font=dict(size=11)),
                    overlaying='y',
                    side='right',
                    range=[0, max(100, max(taxa_sucesso_vals) * 1.1)],
                    gridcolor='rgba(0,0,0,0.02)'
                ),
                height=300,
                showlegend=True,
                plot_bgcolor=COR_BRANCO,
                margin=dict(l=50, r=50, t=50, b=50),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=10)
                ),
                xaxis=dict(tickfont=dict(size=10))
            )
            
            fig_comparativo.update_traces(
                marker_line_width=0.5,
                selector=dict(type='bar')
            )
            
            st.plotly_chart(fig_comparativo, use_container_width=True, config={'displayModeBar': False})
            
            if total_cards_anterior > 0:
                variacao_total = ((total_cards - total_cards_anterior) / total_cards_anterior * 100)
                variacao_validados = ((validados - validados_anterior) / validados_anterior * 100) if validados_anterior > 0 else 0
                variacao_taxa = taxa_sucesso - taxa_sucesso_anterior
            else:
                variacao_total = 100
                variacao_validados = 100 if validados > 0 else 0
                variacao_taxa = taxa_sucesso
            
            st.markdown("##### 📊 VARIAÇÃO PERCENTUAL")
            
            col_var1, col_var2, col_var3 = st.columns(3)
            
            with col_var1:
                st.metric(
                    label="Total Cards",
                    value=f"{total_cards:,}",
                    delta=f"{variacao_total:+.1f}%",
                    delta_color="normal" if variacao_total >= 0 else "inverse",
                    help=f"Anterior: {total_cards_anterior:,}"
                )
            
            with col_var2:
                st.metric(
                    label="Validados",
                    value=f"{validados:,}",
                    delta=f"{variacao_validados:+.1f}%",
                    delta_color="normal" if variacao_validados >= 0 else "inverse",
                    help=f"Anterior: {validados_anterior:,}"
                )
            
            with col_var3:
                st.metric(
                    label="Taxa Sucesso",
                    value=f"{taxa_sucesso:.1f}%",
                    delta=f"{variacao_taxa:+.1f}pp",
                    delta_color="normal" if variacao_taxa >= 0 else "inverse",
                    help=f"Anterior: {taxa_sucesso_anterior:.1f}%"
                )
            
            st.markdown("---")
        
        st.markdown("#### 📊 INDICADORES PRINCIPAIS")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📋 Total Cards", 
                total_cards,
                delta=None,
                help="Total de cards no período"
            )
        
        with col2:
            st.metric(
                "✅ Validados", 
                validados,
                f"{taxa_sucesso:.1f}%",
                delta_color="normal" if taxa_sucesso >= 90 else "off",
                help="Cards sincronizados (aprovados)"
            )
        
        with col3:
            st.metric(
                "🎯 Sem Erro", 
                sem_erro,
                f"{(sem_erro/validados*100) if validados>0 else 0:.1f}%" if validados > 0 else "0%",
                help="Aprovação direta na primeira validação"
            )
        
        with col4:
            st.metric(
                "⚠️ Com Erro", 
                com_erro,
                f"{taxa_erro:.1f}%" if validados > 0 else "0%",
                delta_color="inverse",
                help="Cards que retornaram para ajuste"
            )
        
        st.markdown("---")
        st.markdown("#### 📈 ANÁLISE DETALHADA")
        
        if total_cards > 0:
            if 'Criado' in df_filtrado_periodo.columns and len(df_filtrado_periodo) > 0:
                dias_unicos = df_filtrado_periodo['Criado'].dt.date.nunique()
                media_diaria = total_cards / dias_unicos if dias_unicos > 0 else 0
                
                col_analise1, col_analise2, col_analise3 = st.columns(3)
                
                with col_analise1:
                    st.metric("📅 Dias com atividade", dias_unicos)
                
                with col_analise2:
                    st.metric("📊 Média diária", f"{media_diaria:.1f}")
                
                with col_analise3:
                    if 'Revisões' in df_filtrado_periodo.columns:
                        media_revisoes = df_filtrado_periodo['Revisões'].mean()
                        st.metric("📝 Média revisões/card", f"{media_revisoes:.1f}")
                    else:
                        st.metric("📝 Revisões", "N/A")
            
            st.markdown("##### 🏆 CLASSIFICAÇÃO DE PERFORMANCE")
            
            if taxa_sucesso >= 95:
                st.success("""
                **⭐ EXCELENTE**
                - Meta de qualidade superada (>95%)
                - Processos altamente eficientes
                - Recomendação: Manter padrões atuais
                """)
            elif taxa_sucesso >= 85:
                st.info("""
                **👍 BOM DESEMPENHO**
                - Dentro dos padrões esperados (85-94%)
                - Processos consistentes
                - Recomendação: Pequenos ajustes pontuais
                """)
            elif taxa_sucesso >= 70:
                st.warning("""
                **⚠️ OPORTUNIDADE DE MELHORIA**
                - Abaixo do ideal (70-84%)
                - Processos precisam de revisão
                - Recomendação: Identificar causas principais
                """)
            else:
                st.error("""
                **🚨 ATENÇÃO NECESSÁRIA**
                - Performance crítica (<70%)
                - Processos ineficientes
                - Recomendação: Revisão urgente dos fluxos
                """)
        else:
            st.info(f"ℹ️ Nenhum dado disponível para análise no período: {periodo_titulo}")
        
        st.markdown("---")
        
        st.markdown(f"""
        <div style="background: {COR_CINZA_FUNDO}; padding: 1.2rem; border-radius: 8px; border: 1px solid {COR_CINZA_BORDA};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p style="margin: 0; color: {COR_PRETO_SUAVE}; font-weight: 600;">Ações disponíveis</p>
                    <p style="margin: 0.3rem 0 0 0; color: {COR_CINZA_TEXTO}; font-size: 0.85rem;">
                    Exporte o relatório completo ou feche a manchete
                    </p>
                </div>
                <div style="display: flex; gap: 0.8rem;">
                    <button onclick="document.getElementById('exportBtn').click()" 
                            style="background: {COR_VERDE_ESCURO}; color: {COR_BRANCO}; border: none; padding: 0.6rem 1.2rem; 
                                   border-radius: 6px; cursor: pointer; font-weight: 500;">
                        📥 Exportar PDF
                    </button>
                    <button onclick="document.getElementById('closeBtn').click()" 
                            style="background: {COR_CINZA_TEXTO}; color: {COR_BRANCO}; border: none; 
                                   padding: 0.6rem 1.2rem; border-radius: 6px; 
                                   cursor: pointer; font-weight: 500;">
                        ✕ Fechar
                    </button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_exportar, col_fechar = st.columns(2)
        
        with col_exportar:
            if st.button("📥 **EXPORTAR PDF**", 
                        type="primary", 
                        use_container_width=True,
                        help="Gerar relatório completo em formato PDF",
                        key="btn_exportar_pdf_final"):
                st.info("""
                📄 **Funcionalidade de PDF em desenvolvimento...**
                
                Para uma implementação completa, você pode usar:
                - `fpdf` ou `reportlab` para gerar PDFs
                - `weasyprint` para converter HTML para PDF
                - `pdfkit` (requer wkhtmltopdf)
                """)
        
        with col_fechar:
            if st.button("✕ **FECHAR**", 
                        type="secondary",
                        use_container_width=True,
                        key="btn_fechar_final"):
                st.session_state.show_popup = False
                st.rerun()
        
        st.markdown(f"""
        <div style="background: {COR_CINZA_FUNDO}; padding: 0.8rem; border-radius: 6px; margin-top: 1rem;">
            <small>📅 <strong>Período analisado:</strong> {periodo_titulo}</small><br>
            <small>🕒 <strong>Atualizado em:</strong> {hoje.strftime('%d/%m/%Y %H:%M')}</small><br>
            <small>📊 <strong>Base de dados:</strong> {len(df):,} registros totais</small>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# EXIBIR DASHBOARD SE HOUVER DADOS
# ============================================
if st.session_state.df_original is not None:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    # ============================================
    # CRIAR TABS PRINCIPAIS
    # ============================================
    tab_principal, tab_mapa, tab_motivos, tab_ipe, tab_adms_elipse = st.tabs(["📊 Dashboard Principal", "🗺️ Mapa de Sincronizações", "🔍 Motivos de Revisão", "📈 SRE Performance (KPI IPE)", "⚖️ ADMS vs ELIPSE"])
    
    with tab_principal:
        # ... (conteúdo do tab principal - igual ao original)
        st.markdown("## 📊 Informações da Base de Dados")
        
        if 'Criado' in df.columns and not df.empty:
            data_min = df['Criado'].min()
            data_max = df['Criado'].max()
            
            st.markdown(f"""
            <div class="info-base">
                <p style="margin: 0; font-weight: 600;">📅 Base atualizada em: {get_horario_brasilia()}</p>
                <p style="margin: 0.3rem 0 0 0; color: {COR_CINZA_TEXTO};">
                Período coberto: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')} | 
                Total de registros: {len(df):,}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
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
        
        st.markdown("---")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📅 Evolução de Demandas", 
            "📊 Análise de Revisões", 
            "📈 Chamados Sincronizados por Dia",
            "🏆 Performance dos SREs + Análise Avançada"
        ])
        
        with tab1:
            # ... (conteúdo do tab1 - igual ao original)
            st.markdown("📅 Evolução de Demandas")
            st.info("Conteúdo da tab1 - mantenha o código original aqui")
        
        with tab2:
            st.markdown("📊 Análise de Revisões")
            st.info("Conteúdo da tab2 - mantenha o código original aqui")
        
        with tab3:
            st.markdown("📈 Chamados Sincronizados por Dia")
            st.info("Conteúdo da tab3 - mantenha o código original aqui")
        
        with tab4:
            st.markdown("🏆 Performance dos SREs + Análise Avançada")
            st.info("Conteúdo da tab4 - mantenha o código original aqui")
    
    with tab_mapa:
        # ... (conteúdo do mapa - igual ao original)
        st.markdown("## 🗺️ Mapa de Sincronizações por Empresa")
        st.info("Conteúdo do mapa - mantenha o código original aqui")
    
    with tab_motivos:
        # ... (conteúdo dos motivos - igual ao original)
        st.markdown("## 🔍 ANÁLISE DE MOTIVOS DE REVISÃO")
        st.info("Conteúdo dos motivos - mantenha o código original aqui")
    
    with tab_ipe:
        # ... (conteúdo do IPE - igual ao original)
        st.markdown(f'<div class="section-title">🎯 KPI IPE - ÍNDICE DE PERFORMANCE DO ESPECIALISTA</div>', unsafe_allow_html=True)
        st.info("Conteúdo do IPE - mantenha o código original aqui")
    
    # ============================================
    # NOVA ABA: ADMS vs ELIPSE
    # ============================================
    with tab_adms_elipse:
        st.markdown(f'<div class="section-title">⚖️ ADMS vs ELIPSE - Comparativo de Sincronizações</div>', unsafe_allow_html=True)
        st.markdown("_Análise comparativa entre chamados sincronizados do ADMS (Telemetry e Manuals) e ELIPSE baseada no ChangeSet_")
        
        # Verificar se a coluna ChangeSet existe
        if 'ChangeSet' not in df.columns:
            st.warning("⚠️ Coluna 'ChangeSet' não encontrada. Não é possível realizar a análise ADMS vs ELIPSE.")
            st.info("""
            **Como resolver:**
            Certifique-se de que o arquivo CSV contém uma coluna chamada **'ChangeSet'** com os valores:
            - **Telemetry** → Classificado como ADMS - Telemetry
            - **Manuals** → Classificado como ADMS - Manual
            - **Elipse** → Classificado como ELIPSE
            """)
        else:
            # Filtros específicos para ADMS vs ELIPSE
            col_filtro_ae1, col_filtro_ae2, col_filtro_ae3, col_filtro_ae4 = st.columns(4)
            
            with col_filtro_ae1:
                if 'Ano' in df.columns:
                    anos_ae = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_ae = ['Todos os Anos'] + list(anos_ae)
                    ano_ae = st.selectbox(
                        "📅 Ano",
                        options=anos_opcoes_ae,
                        key="filtro_ano_ae"
                    )
                else:
                    ano_ae = 'Todos os Anos'
            
            with col_filtro_ae2:
                if 'Mês' in df.columns:
                    meses_ae = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_ae = ['Todos os Meses'] + [f"{m:02d}" for m in meses_ae]
                    mes_ae = st.selectbox(
                        "📆 Mês",
                        options=meses_opcoes_ae,
                        key="filtro_mes_ae"
                    )
                else:
                    mes_ae = 'Todos os Meses'
            
            with col_filtro_ae3:
                if 'Empresa' in df.columns:
                    empresas_ae = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                    empresa_ae = st.selectbox(
                        "🏢 Empresa",
                        options=empresas_ae,
                        key="filtro_empresa_ae"
                    )
                else:
                    empresa_ae = 'Todas'
            
            with col_filtro_ae4:
                if 'SRE' in df.columns:
                    sres_ae = ['Todos'] + sorted(df['SRE'].dropna().unique())
                    sre_ae = st.selectbox(
                        "🔧 SRE",
                        options=sres_ae,
                        key="filtro_sre_ae"
                    )
                else:
                    sre_ae = 'Todos'
            
            # Aplicar filtros
            df_ae = df.copy()
            
            if ano_ae != 'Todos os Anos':
                df_ae = df_ae[df_ae['Ano'] == int(ano_ae)]
            
            if mes_ae != 'Todos os Meses':
                df_ae = df_ae[df_ae['Mês'] == int(mes_ae)]
            
            if empresa_ae != 'Todas':
                df_ae = df_ae[df_ae['Empresa'] == empresa_ae]
            
            if sre_ae != 'Todos':
                df_ae = df_ae[df_ae['SRE'] == sre_ae]
            
            # Analisar dados
            resultados = analisar_adms_elipse(
                df_ae,
                ano_filtro=ano_ae,
                mes_filtro=mes_ae,
                empresa_filtro=empresa_ae,
                sre_filtro=sre_ae
            )
            
            # VERIFICAR SE RESULTADOS É VÁLIDO
            if resultados is None:
                st.warning("⚠️ Nenhum dado sincronizado encontrado com os filtros selecionados.")
                st.info("""
                **Possíveis causas:**
                - Não há chamados com status 'Sincronizado' no período selecionado
                - Os valores no campo 'ChangeSet' não correspondem a: Telemetry, Manuals ou Elipse
                - O campo 'ChangeSet' está vazio para os chamados sincronizados
                """)
            else:
                # Métricas principais
                st.markdown("### 📊 Métricas Gerais")
                
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                
                with col_m1:
                    st.metric(
                        "📋 Total Sincronizados",
                        f"{resultados['total_classificados']:,}",
                        help="Total de chamados sincronizados classificados como ADMS ou ELIPSE"
                    )
                
                with col_m2:
                    pct_adms = resultados['pct_adms']
                    st.metric(
                        "⚡ ADMS",
                        f"{resultados['total_adms']:,}",
                        f"{pct_adms:.1f}%",
                        delta_color="normal" if pct_adms >= 50 else "inverse"
                    )
                
                with col_m3:
                    pct_elipse = resultados['pct_elipse']
                    st.metric(
                        "🔷 ELIPSE",
                        f"{resultados['total_elipse']:,}",
                        f"{pct_elipse:.1f}%",
                        delta_color="normal" if pct_elipse >= 50 else "inverse"
                    )
                
                with col_m4:
                    if resultados['total_elipse'] > 0:
                        ratio = resultados['total_adms'] / resultados['total_elipse']
                        st.metric(
                            "📊 Proporção ADMS/ELIPSE",
                            f"{ratio:.2f}",
                            help="Razão entre chamados ADMS e ELIPSE"
                        )
                    else:
                        st.metric(
                            "📊 Proporção ADMS/ELIPSE",
                            "∞",
                            help="Sem chamados ELIPSE no período"
                        )
                
                st.markdown("---")
                
                # Gráfico de Distribuição
                st.markdown("### 📊 Distribuição de Sincronizações")
                
                col_ae1, col_ae2 = st.columns(2)
                
                with col_ae1:
                    # Gráfico de Pizza
                    fig_pizza_ae = px.pie(
                        resultados['contagem_origem'],
                        values='Quantidade',
                        names='Origem',
                        title='Distribuição por Origem',
                        hole=0.4,
                        color='Origem',
                        color_discrete_map={
                            'ADMS - Telemetry': COR_AZUL_PETROLEO,
                            'ADMS - Manual': COR_VERDE_ESCURO,
                            'ELIPSE': COR_LARANJA
                        }
                    )
                    fig_pizza_ae.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pizza_ae.update_layout(height=400)
                    st.plotly_chart(fig_pizza_ae, use_container_width=True)
                
                with col_ae2:
                    # Gráfico de Barras
                    fig_bar_ae = px.bar(
                        resultados['contagem_origem'],
                        x='Origem',
                        y='Quantidade',
                        text='Quantidade',
                        title='Quantidade por Origem',
                        color='Origem',
                        color_discrete_map={
                            'ADMS - Telemetry': COR_AZUL_PETROLEO,
                            'ADMS - Manual': COR_VERDE_ESCURO,
                            'ELIPSE': COR_LARANJA
                        }
                    )
                    fig_bar_ae.update_traces(textposition='outside')
                    fig_bar_ae.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_bar_ae, use_container_width=True)
                
                st.markdown("---")
                
                # Análise Temporal
                if not resultados['temporal_origem'].empty:
                    st.markdown("### 📈 Evolução Temporal por Origem")
                    
                    fig_temporal_ae = px.line(
                        resultados['temporal_origem'],
                        x='Mês_Ano',
                        y='Quantidade',
                        color='Origem',
                        markers=True,
                        title='Evolução das Sincronizações por Mês',
                        color_discrete_map={
                            'ADMS - Telemetry': COR_AZUL_PETROLEO,
                            'ADMS - Manual': COR_VERDE_ESCURO,
                            'ELIPSE': COR_LARANJA
                        }
                    )
                    fig_temporal_ae.update_layout(
                        height=400,
                        xaxis_title="Período",
                        yaxis_title="Quantidade",
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_temporal_ae, use_container_width=True)
                
                st.markdown("---")
                
                # Análise por Empresa
                if not resultados['empresa_origem'].empty:
                    st.markdown("### 🏢 Distribuição por Empresa")
                    
                    # Criar pivot para visualização
                    pivot_empresa = resultados['empresa_origem'].pivot_table(
                        index='Empresa',
                        columns='Origem',
                        values='Quantidade',
                        fill_value=0
                    ).reset_index()
                    
                    # Verificar se há colunas para ordenar
                    colunas_origem = [col for col in pivot_empresa.columns if col != 'Empresa']
                    if colunas_origem:
                        pivot_empresa['Total'] = pivot_empresa[colunas_origem].sum(axis=1)
                        pivot_empresa = pivot_empresa.sort_values('Total', ascending=False)
                    
                    fig_empresa_ae = go.Figure()
                    
                    cores = {
                        'ADMS - Telemetry': COR_AZUL_PETROLEO,
                        'ADMS - Manual': COR_VERDE_ESCURO,
                        'ELIPSE': COR_LARANJA
                    }
                    
                    for origem in ['ADMS - Telemetry', 'ADMS - Manual', 'ELIPSE']:
                        if origem in pivot_empresa.columns:
                            fig_empresa_ae.add_trace(go.Bar(
                                x=pivot_empresa['Empresa'],
                                y=pivot_empresa[origem],
                                name=origem,
                                marker_color=cores.get(origem, COR_CINZA_TEXTO),
                                hovertemplate='%{x}<br>' + origem + ': %{y}<extra></extra>'
                            ))
                    
                    if colunas_origem:
                        fig_empresa_ae.update_layout(
                            title='Sincronizações por Empresa e Origem',
                            barmode='stack',
                            height=400,
                            xaxis_title="Empresa",
                            yaxis_title="Quantidade",
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="center",
                                x=0.5
                            )
                        )
                        st.plotly_chart(fig_empresa_ae, use_container_width=True)
                    
                    # Tabela por empresa
                    with st.expander("📋 Ver Detalhes por Empresa", expanded=False):
                        st.dataframe(
                            pivot_empresa,
                            use_container_width=True,
                            column_config={
                                "Empresa": st.column_config.TextColumn("Empresa"),
                                "Total": st.column_config.NumberColumn("Total", format="%d"),
                            }
                        )
                
                st.markdown("---")
                
                # Análise por SRE
                if not resultados['sre_origem'].empty:
                    st.markdown("### 👥 Distribuição por SRE")
                    
                    # Criar pivot para visualização
                    pivot_sre = resultados['sre_origem'].pivot_table(
                        index='SRE',
                        columns='Origem',
                        values='Quantidade',
                        fill_value=0
                    ).reset_index()
                    
                    # Verificar se há colunas para ordenar
                    colunas_origem_sre = [col for col in pivot_sre.columns if col != 'SRE']
                    if colunas_origem_sre:
                        pivot_sre['Total'] = pivot_sre[colunas_origem_sre].sum(axis=1)
                        pivot_sre = pivot_sre.sort_values('Total', ascending=False)
                    
                    fig_sre_ae = go.Figure()
                    
                    for origem in ['ADMS - Telemetry', 'ADMS - Manual', 'ELIPSE']:
                        if origem in pivot_sre.columns:
                            fig_sre_ae.add_trace(go.Bar(
                                x=pivot_sre['SRE'],
                                y=pivot_sre[origem],
                                name=origem,
                                marker_color=cores.get(origem, COR_CINZA_TEXTO),
                                hovertemplate='%{x}<br>' + origem + ': %{y}<extra></extra>'
                            ))
                    
                    if colunas_origem_sre:
                        fig_sre_ae.update_layout(
                            title='Sincronizações por SRE e Origem',
                            barmode='stack',
                            height=400,
                            xaxis_title="SRE",
                            yaxis_title="Quantidade",
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="center",
                                x=0.5
                            )
                        )
                        st.plotly_chart(fig_sre_ae, use_container_width=True)
                    
                    # Tabela por SRE
                    with st.expander("📋 Ver Detalhes por SRE", expanded=False):
                        st.dataframe(
                            pivot_sre,
                            use_container_width=True,
                            column_config={
                                "SRE": st.column_config.TextColumn("SRE"),
                                "Total": st.column_config.NumberColumn("Total", format="%d"),
                            }
                        )
                
                st.markdown("---")
                
                # Tabela detalhada
                with st.expander("📋 Ver Detalhamento dos Chamados", expanded=False):
                    df_detalhe_ae = resultados['df_classificados'][['Chamado', 'ChangeSet', 'Origem', 'Empresa', 'SRE', 'Status', 'Criado']].copy()
                    df_detalhe_ae['Criado'] = df_detalhe_ae['Criado'].dt.strftime('%d/%m/%Y')
                    df_detalhe_ae = df_detalhe_ae.sort_values('Criado', ascending=False)
                    
                    st.dataframe(
                        df_detalhe_ae,
                        use_container_width=True,
                        height=400,
                        column_config={
                            "Chamado": st.column_config.TextColumn("Chamado"),
                            "ChangeSet": st.column_config.TextColumn("ChangeSet", width="medium"),
                            "Origem": st.column_config.TextColumn("Origem"),
                            "Empresa": st.column_config.TextColumn("Empresa"),
                            "SRE": st.column_config.TextColumn("SRE"),
                            "Status": st.column_config.TextColumn("Status"),
                            "Criado": st.column_config.TextColumn("Data")
                        }
                    )
                    
                    csv_detalhe_ae = df_detalhe_ae.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 Exportar detalhes para CSV",
                        data=csv_detalhe_ae,
                        file_name=f"detalhes_adms_elipse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                # Explicação
                with st.expander("📖 Entenda a Classificação ADMS vs ELIPSE"):
                    st.markdown("""
                    ### Como os Chamados são Classificados?
                    
                    A classificação é baseada no campo **'ChangeSet'**:
                    
                    | Origem | Valor no ChangeSet |
                    |--------|-------------------|
                    | **ADMS - Telemetry** | Contém a palavra **'TELEMETRY'** |
                    | **ADMS - Manual** | Contém a palavra **'MANUALS'** ou **'MANUAL'** |
                    | **ELIPSE** | Contém a palavra **'ELIPSE'** |
                    | **Outros** | Não se encaixa nas categorias acima |
                    
                    ### Análise Realizada
                    
                    - **Distribuição por Origem**: Proporção de chamados de cada fonte
                    - **Evolução Temporal**: Como a distribuição muda ao longo dos meses
                    - **Análise por Empresa**: Quais empresas têm mais chamados de cada origem
                    - **Análise por SRE**: Performance de cada SRE em diferentes origens
                    
                    ### Importância da Análise
                    
                    Esta análise ajuda a identificar:
                    - Qual fonte de chamados (ADMS ou ELIPSE) gera mais trabalho
                    - Se há desbalanceamento na distribuição de chamados
                    - Padrões de comportamento por empresa e SRE
                    - Oportunidades de otimização na alocação de recursos
                    """)

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
