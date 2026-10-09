import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, timedelta
import io
import os
import time
import hashlib
import warnings
from pytz import timezone
import streamlit.components.v1 as components
warnings.filterwarnings('ignore')

TZ_BR = timezone('America/Sao_Paulo')

# Remove a setinha dos deltas informativos (ex.: "99% do total") quando o Streamlit suporta;
# em versões antigas o parâmetro é simplesmente ignorado
import inspect as _inspect
DELTA_SEM_SETA = {'delta_arrow': 'off'} if 'delta_arrow' in _inspect.signature(st.metric).parameters else {}


def agora():
    """Data/hora de Brasília (sem fuso, para comparar com as datas do CSV).
    Evita que o 'mês atual' vire errado quando o servidor está em UTC."""
    return datetime.now(TZ_BR).replace(tzinfo=None)

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

CORES_GRADIENTE = [
    COR_VERDE_ESCURO,
    COR_AZUL_PETROLEO,
    COR_AZUL_ESCURO,
    COR_LARANJA,
    COR_VERMELHO,
    "#1E88E5"
]

# Escalas contínuas da paleta (substituem 'Blues' e 'Viridis', que fugiam da identidade visual)
ESCALA_AZUL = [[0, "#CFE8EC"], [0.5, COR_AZUL_PETROLEO], [1, COR_AZUL_ESCURO]]

# Nomes de exibição dos SREs (antes repetido em dois lugares do código)
APELIDOS_SRE = [
    (("kewin", "ferreira"), "Kewin Marcel"),
    (("pierry", "perez"), "Pierry Perez"),
    (("bruna", "maciel"), "Bruna Maciel"),
    (("ramiza", "irineu"), "Ramiza Irineu"),
]

# ============================================
# ÍCONES (SVG no estilo Lucide — embutidos, funcionam sem internet)
# Nos widgets nativos do Streamlit (abas, botões, alertas) usamos :material/...:
# ============================================
ICONES = {
    'grafico': '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    'check': '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    'lista': '<rect width="8" height="4" x="8" y="2" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/>',
    'revisao': '<path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>',
    'atividade': '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    'mapa': '<polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" x2="9" y1="3" y2="18"/><line x1="15" x2="15" y1="6" y2="21"/>',
    'premio': '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>',
    'calendario': '<rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/>',
    'ajustes': '<line x1="4" x2="4" y1="21" y2="14"/><line x1="4" x2="4" y1="10" y2="3"/><line x1="12" x2="12" y1="21" y2="12"/><line x1="12" x2="12" y1="8" y2="3"/><line x1="20" x2="20" y1="21" y2="16"/><line x1="20" x2="20" y1="12" y2="3"/><line x1="2" x2="6" y1="14" y2="14"/><line x1="10" x2="14" y1="8" y2="8"/><line x1="18" x2="22" y1="16" y2="16"/>',
    'alvo': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    'subida': '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    'alerta': '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/>',
    'equipe': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    'relogio': '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    'empresa': '<rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/>',
    'jornal': '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/>',
    'info': '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/>',
    'ideia': '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    'email': '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    'arquivo': '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/>',
    'base': '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
    'medidor': '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
    'pino': '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    'paleta': '<circle cx="13.5" cy="6.5" r=".5"/><circle cx="17.5" cy="10.5" r=".5"/><circle cx="8.5" cy="7.5" r=".5"/><circle cx="6.5" cy="12.5" r=".5"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>',
}


def icone(nome, tamanho=20, cor="currentColor", espessura=2):
    """Ícone SVG inline para usar dentro dos blocos HTML (cards, títulos, rodapé)."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" '
            f'viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="{espessura}" '
            f'stroke-linecap="round" stroke-linejoin="round" '
            f'style="vertical-align:-0.18em; flex-shrink:0;">{ICONES[nome]}</svg>')


CORES_PODIO = {1: "#D4A017", 2: "#9AA5B1", 3: "#B87333"}


def selo_posicao(pos, tamanho=26):
    """Selo circular numerado (substitui as medalhas em emoji): ouro, prata, bronze e cinza."""
    cor = CORES_PODIO.get(pos, COR_CINZA_TEXTO)
    return (f'<span style="display:inline-flex; align-items:center; justify-content:center; '
            f'width:{tamanho}px; height:{tamanho}px; border-radius:50%; background:{cor}; '
            f'color:#fff; font-weight:700; font-size:{int(tamanho * 0.46)}px; flex-shrink:0;">{pos}º</span>')


MESES_NOMES = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
               7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
MESES_ABREV = {k: v[:3] for k, v in MESES_NOMES.items()}

# ============================================
# TEMA PADRÃO DOS GRÁFICOS (aplicado a todos)
# ============================================
pio.templates["energisa"] = go.layout.Template(layout=dict(
    font=dict(family="Inter, 'Segoe UI', sans-serif", size=12, color=COR_PRETO_SUAVE),
    colorway=[COR_AZUL_ESCURO, COR_VERDE_ESCURO, COR_LARANJA, COR_AZUL_PETROLEO,
              "#7E57C2", "#1E88E5", "#8D6E63", COR_VERMELHO],
    plot_bgcolor=COR_BRANCO, paper_bgcolor=COR_BRANCO,
    title=dict(font=dict(size=15, color=COR_AZUL_ESCURO)),
    xaxis=dict(gridcolor="#F1F3F5", linecolor=COR_CINZA_BORDA, zeroline=False, automargin=True),
    yaxis=dict(gridcolor="#F1F3F5", linecolor=COR_CINZA_BORDA, zeroline=False, automargin=True),
    hoverlabel=dict(bgcolor=COR_BRANCO, bordercolor=COR_CINZA_BORDA, font_size=12),
    legend=dict(bgcolor="rgba(255,255,255,0)"),
    separators=",.",
))
pio.templates.default = "plotly_white+energisa"

# ============================================
# MAPEAMENTO COMPLETO DAS EMPRESAS
# ============================================
MAPEAMENTO_EMPRESAS = {
    'EMR': {'sigla': 'MG', 'estado': 'Minas Gerais', 'regiao': 'Sudeste',
            'nome_completo': 'Energisa Minas Gerais', 'latitude': -19.9167, 'longitude': -43.9345},
    'EPB': {'sigla': 'PB', 'estado': 'Paraíba', 'regiao': 'Nordeste',
            'nome_completo': 'Energisa Paraíba', 'latitude': -7.1195, 'longitude': -36.7240},
    'ESE': {'sigla': 'SE', 'estado': 'Sergipe', 'regiao': 'Nordeste',
            'nome_completo': 'Energisa Sergipe', 'latitude': -10.9472, 'longitude': -37.0731},
    'ESS': {'sigla': 'SP', 'estado': 'São Paulo', 'regiao': 'Sudeste',
            'nome_completo': 'Energisa Sul/Sudeste', 'latitude': -23.5505, 'longitude': -46.6333},
    'EMS': {'sigla': 'MS', 'estado': 'Mato Grosso do Sul', 'regiao': 'Centro-Oeste',
            'nome_completo': 'Energisa Mato Grosso do Sul', 'latitude': -20.4697, 'longitude': -54.6201},
    'EMT': {'sigla': 'MT', 'estado': 'Mato Grosso', 'regiao': 'Centro-Oeste',
            'nome_completo': 'Energisa Mato Grosso', 'latitude': -12.6819, 'longitude': -56.9211},
    'ETO': {'sigla': 'TO', 'estado': 'Tocantins', 'regiao': 'Norte',
            'nome_completo': 'Energisa Tocantins', 'latitude': -10.1753, 'longitude': -48.2982},
    'ERO': {'sigla': 'RO', 'estado': 'Rondônia', 'regiao': 'Norte',
            'nome_completo': 'Energisa Rondônia', 'latitude': -10.9161, 'longitude': -61.8298},
    'EAC': {'sigla': 'AC', 'estado': 'Acre', 'regiao': 'Norte',
            'nome_completo': 'Energisa Acre', 'latitude': -9.0238, 'longitude': -70.8120}
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
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO - NOVA PALETA
# ============================================
st.markdown(f"""
<style>
    .stApp {{ background-color: {COR_CINZA_FUNDO}; }}
    .main-header-monitoring {{
        background: {COR_CINZA_FUNDO}; padding: 1.2rem 2rem; margin-bottom: 1.5rem;
        border-bottom: 4px solid {COR_AZUL_ESCURO}; border-radius: 0;
    }}
    .metric-card {{
        background: {COR_BRANCO}; padding: 1.2rem; border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); border: 1px solid {COR_CINZA_BORDA};
        margin-bottom: 1rem; transition: all 0.3s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 89, 115, 0.1);
        border-color: {COR_AZUL_PETROLEO};
    }}
    .metric-value {{ font-size: 2rem; font-weight: 700; color: {COR_AZUL_ESCURO}; margin: 0; line-height: 1.2; }}
    .metric-label {{ font-size: 0.85rem; color: {COR_CINZA_TEXTO}; margin: 0.5rem 0 0 0; font-weight: 500; }}
    .section-title {{
        color: {COR_AZUL_ESCURO}; border-left: 4px solid {COR_VERDE_ESCURO};
        padding-left: 1rem; margin-bottom: 1.5rem; font-size: 1.2rem;
        font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
    }}
    [data-testid="stSidebar"] {{ background: {COR_BRANCO}; border-right: 1px solid {COR_CINZA_BORDA}; }}
    .sidebar-section {{
        background: {COR_CINZA_FUNDO}; padding: 1rem; border-radius: 8px;
        margin-bottom: 1rem; border: 1px solid {COR_CINZA_BORDA};
    }}
    .info-base {{
        background: {COR_CINZA_FUNDO}; padding: 1rem; border-radius: 8px;
        border-left: 4px solid {COR_VERDE_ESCURO}; margin-bottom: 1.5rem;
    }}
    .footer {{
        text-align: center; margin-top: 3rem; padding-top: 1.5rem;
        border-top: 2px solid {COR_CINZA_BORDA}; color: {COR_CINZA_TEXTO}; font-size: 0.85rem;
    }}
    .status-success {{
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        border-left: 4px solid {COR_VERDE_ESCURO}; padding: 0.75rem; border-radius: 8px;
    }}
    .status-warning {{
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
        border-left: 4px solid {COR_LARANJA}; padding: 0.75rem; border-radius: 8px;
    }}
    .status-danger {{
        background: linear-gradient(135deg, #FFEBEE, #FFCDD2);
        border-left: 4px solid {COR_VERMELHO}; padding: 0.75rem; border-radius: 8px;
    }}
    .performance-card {{
        background: linear-gradient(135deg, {COR_BRANCO}, #F1F8E9); padding: 1rem;
        border-radius: 8px; border-left: 4px solid {COR_VERDE_ESCURO}; margin-bottom: 1rem;
    }}
    .warning-card {{
        background: linear-gradient(135deg, {COR_BRANCO}, #FFF3E0); padding: 1rem;
        border-radius: 8px; border-left: 4px solid {COR_LARANJA}; margin-bottom: 1rem;
    }}
    .alert-card {{
        background: linear-gradient(135deg, {COR_BRANCO}, #FFEBEE); padding: 1rem;
        border-radius: 8px; border-left: 4px solid {COR_VERMELHO}; margin-bottom: 1rem;
    }}
    .info-card {{
        background: linear-gradient(135deg, {COR_BRANCO}, #E0F7FA); padding: 1rem;
        border-radius: 8px; border-left: 4px solid {COR_AZUL_PETROLEO}; margin-bottom: 1rem;
    }}
    .stButton > button {{
        background: {COR_AZUL_ESCURO}; color: {COR_BRANCO}; border: none;
        border-radius: 6px; padding: 0.5rem 1rem; font-weight: 500; transition: all 0.3s ease;
    }}
    .stButton > button:hover {{
        background: {COR_AZUL_PETROLEO}; transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 89, 115, 0.3);
    }}
    .badge-success {{ background-color: {COR_VERDE_ESCURO}; color: {COR_BRANCO}; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }}
    .badge-warning {{ background-color: {COR_LARANJA}; color: {COR_BRANCO}; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }}
    .badge-danger {{ background-color: {COR_VERMELHO}; color: {COR_BRANCO}; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }}
    .badge-info {{ background-color: {COR_AZUL_PETROLEO}; color: {COR_BRANCO}; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }}
    .matrix-quadrant {{ padding: 10px; border-radius: 8px; margin: 5px; font-weight: bold; text-align: center; }}
    .quadrant-stars {{ background-color: #E8F5E9; color: {COR_VERDE_ESCURO}; border: 2px solid {COR_VERDE_ESCURO}; }}
    .quadrant-efficient {{ background-color: #FFF3E0; color: {COR_LARANJA}; border: 2px solid {COR_LARANJA}; }}
    .quadrant-careful {{ background-color: #E0F7FA; color: {COR_AZUL_PETROLEO}; border: 2px solid {COR_AZUL_PETROLEO}; }}
    .quadrant-needs-help {{ background-color: #FFEBEE; color: {COR_VERMELHO}; border: 2px solid {COR_VERMELHO}; }}
    /* Cards nativos do Streamlit (st.metric) no mesmo estilo dos .metric-card */
    [data-testid="stMetric"] {{
        background: {COR_BRANCO}; padding: 0.9rem 1rem; border-radius: 8px;
        border: 1px solid {COR_CINZA_BORDA}; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;
    }}
    [data-testid="stMetric"]:hover {{ border-color: {COR_AZUL_PETROLEO}; box-shadow: 0 4px 12px rgba(0, 89, 115, 0.1); }}
    [data-testid="stMetricValue"] {{ color: {COR_AZUL_ESCURO}; font-weight: 700; }}
    [data-testid="stMetricLabel"] p {{ color: {COR_CINZA_TEXTO}; font-weight: 600; }}
    /* Botões primários e secundários na paleta (o padrão do Streamlit é vermelho) */
    button[kind="primary"], [data-testid="stBaseButton-primary"] {{
        background: {COR_AZUL_ESCURO} !important; border-color: {COR_AZUL_ESCURO} !important; color: {COR_BRANCO} !important;
    }}
    button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {{
        background: {COR_AZUL_PETROLEO} !important; border-color: {COR_AZUL_PETROLEO} !important;
    }}
    button[kind="secondary"], [data-testid="stBaseButton-secondary"] {{
        border-color: {COR_CINZA_BORDA} !important; color: {COR_AZUL_ESCURO} !important;
    }}
    button[kind="secondary"]:hover, [data-testid="stBaseButton-secondary"]:hover {{
        border-color: {COR_AZUL_PETROLEO} !important; color: {COR_AZUL_PETROLEO} !important;
    }}
    /* Abas */
    .stTabs [data-baseweb="tab-list"] {{ gap: 0.4rem; }}
    .stTabs [data-baseweb="tab"] {{ font-weight: 600; }}
    .stTabs [aria-selected="true"] {{ color: {COR_AZUL_ESCURO}; }}
    /* Gráficos com moldura de card */
    [data-testid="stPlotlyChart"] {{
        background: {COR_BRANCO}; border: 1px solid {COR_CINZA_BORDA}; border-radius: 8px; padding: 6px;
    }}
    /* Expanders */
    [data-testid="stExpander"] {{ background: {COR_BRANCO}; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def formatar_nome_responsavel(nome):
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
        correcoes = {' Da ': ' da ', ' De ': ' de ', ' Do ': ' do ', ' Das ': ' das ', ' Dos ': ' dos ', ' E ': ' e '}
        for errado, correto in correcoes.items():
            nome_formatado = nome_formatado.replace(errado, correto)
        return nome_formatado
    return nome_str.title()

def substituir_nome_sre(sre_nome):
    """Nome de exibição do SRE (única definição — antes existia duplicada em duas abas)."""
    if pd.isna(sre_nome):
        return "Não informado"
    sre_nome_str = str(sre_nome).lower()
    for chaves, apelido in APELIDOS_SRE:
        if any(c in sre_nome_str for c in chaves):
            return apelido
    return sre_nome

def is_retorno_sim(valor):
    if pd.isna(valor):
        return False
    return str(valor).strip().upper() in ['SIM', 'S', 'YES', 'Y', '1', 'TRUE']

def converter_datas(serie):
    """Converte as datas detectando o formato do arquivo.
    - ISO (2026-03-04) é lido direto
    - dd/mm/aaaa (padrão brasileiro) é o padrão quando há dúvida
    - mm/dd/aaaa só é usado se o 2º número passar de 12 em alguma linha
    Antes, pd.to_datetime sem dayfirst lia 03/04 como 4 de março."""
    texto = serie.astype(str).str.strip()
    amostra = texto[~texto.isin(['', 'nan', 'NaT', 'None'])].head(1000)
    if amostra.empty:
        return pd.to_datetime(serie, errors='coerce')
    if amostra.str.match(r'^\d{4}-\d{1,2}-\d{1,2}').mean() > 0.5:
        return pd.to_datetime(texto, errors='coerce', format='mixed')
    partes = amostra.str.extract(r'^(\d{1,2})[/.\-](\d{1,2})[/.\-]\d{2,4}')
    primeiro = pd.to_numeric(partes[0], errors='coerce')
    segundo = pd.to_numeric(partes[1], errors='coerce')
    dayfirst = not ((segundo > 12).any() and not (primeiro > 12).any())
    return pd.to_datetime(texto, errors='coerce', dayfirst=dayfirst, format='mixed')

def serie_diaria(datas):
    """Contagem por dia INCLUINDO os dias úteis sem nenhum registro (valor 0).
    Antes, o groupby só gerava os dias com registro, então 'Dias sem Sinc.' era sempre 0
    e médias/percentis ficavam inflados."""
    datas = pd.to_datetime(pd.Series(datas)).dropna().dt.normalize()
    if datas.empty:
        return pd.Series(dtype=int)
    contagem = datas.value_counts().sort_index()
    indice = pd.bdate_range(contagem.index.min(), contagem.index.max()).union(contagem.index)
    return contagem.reindex(indice, fill_value=0).astype(int)

def gradiente_azul(valores):
    """Cores do azul-petróleo claro (menor) ao azul-escuro (maior).
    Substitui o gradiente antigo, que ia de rgb(0,89,115) para rgb(0,89,115) (cor única)."""
    valores = list(valores)
    if not valores:
        return []
    mn, mx = min(valores), max(valores)
    claro, escuro = (0x7F, 0xC4, 0xD0), (0x00, 0x59, 0x73)
    cores = []
    for v in valores:
        t = 0.5 if mx == mn else (v - mn) / (mx - mn)
        r, g, b = (int(claro[i] + t * (escuro[i] - claro[i])) for i in range(3))
        cores.append(f'rgb({r}, {g}, {b})')
    return cores

def fmt_milhar(valor):
    return f"{int(valor):,}".replace(",", ".")

def criar_card_indicador_simples(valor, label, icone_nome="grafico", subtitulo=None, cor=None):
    cor = cor or COR_AZUL_ESCURO
    if isinstance(valor, (int, float)):
        valor_formatado = fmt_milhar(valor)
    else:
        valor_formatado = str(valor)
    simbolo = icone(icone_nome, 24, cor) if icone_nome in ICONES else icone_nome
    sub = (f'<div style="font-size:0.75rem; color:{COR_CINZA_TEXTO}; margin-top:0.2rem;">{subtitulo}</div>'
           if subtitulo else '')
    # HTML numa linha só: linhas em branco/indentadas fazem o Markdown do Streamlit
    # transformar o resto do card em bloco de código (o "</div>" que aparecia na tela)
    return (f'<div class="metric-card" style="border-left: 4px solid {cor};">'
            f'<div style="display: flex; align-items: center; gap: 14px;">'
            f'<div style="background: {cor}14; width: 48px; height: 48px; border-radius: 12px; '
            f'display: flex; align-items: center; justify-content: center; flex-shrink: 0;">{simbolo}</div>'
            f'<div>'
            f'<div class="metric-value" style="color:{cor};">{valor_formatado}</div>'
            f'<div class="metric-label">{label}</div>'
            f'{sub}'
            f'</div></div></div>')

def quebrar_rotulo(texto, largura=18):
    """Quebra rótulos longos em linhas (<br>) para caber no eixo dos gráficos."""
    palavras, linhas, atual = str(texto).split(), [], ""
    for p in palavras:
        if atual and len(atual) + 1 + len(p) > largura:
            linhas.append(atual)
            atual = p
        else:
            atual = f"{atual} {p}".strip()
    if atual:
        linhas.append(atual)
    return "<br>".join(linhas[:3]) + ("…" if len(linhas) > 3 else "")


def motivo_preenchido(serie):
    """True onde há motivo informado. Funciona no pandas 2 (vazio vira 'nan' como texto)
    e no pandas 3 (vazio continua NaN mesmo depois de .astype(str))."""
    texto = serie.astype(str).str.strip()
    return serie.notna() & ~texto.isin(['', 'nan', 'NaN', 'None', '<NA>', 'NaT'])


def explodir_motivos(df_base):
    """Uma linha por (card, motivo). Aceita vários motivos no mesmo card separados por ';'
    (inclusive o formato ';#' das listas do SharePoint) e padroniza maiúsculas/espaços."""
    if 'Motivo_Revisao' not in df_base.columns or df_base.empty:
        return df_base.iloc[0:0].assign(Motivo=pd.Series(dtype=str))
    texto = df_base['Motivo_Revisao'].astype(str).str.strip()
    preenchido = motivo_preenchido(df_base['Motivo_Revisao'])
    ex = df_base.loc[preenchido].copy()
    if ex.empty:
        return ex.assign(Motivo=pd.Series(dtype=str))
    ex['Motivo'] = texto[preenchido].str.replace(';#', ';', regex=False).str.split(';')
    # reset_index: o explode repete o índice, o que desalinha agrupamentos em algumas versões do pandas
    ex = ex.explode('Motivo').reset_index(drop=True)
    ex['Motivo'] = ex['Motivo'].astype(str).str.strip(' #').str.replace(r'\s+', ' ', regex=True)
    ex = ex[ex['Motivo'].notna() & ~ex['Motivo'].isin(['', 'nan', 'None'])].reset_index(drop=True)
    # "Fase errada" e "fase  errada" viram o mesmo motivo (mostra a grafia mais usada)
    ex['_chave_motivo'] = ex['Motivo'].str.lower()
    grafia = ex.groupby('_chave_motivo')['Motivo'].agg(lambda s: s.value_counts().index[0])
    ex['Motivo'] = ex['_chave_motivo'].map(grafia)
    return ex.drop(columns='_chave_motivo')


def titulo_secao(texto, icone_nome):
    """Título de seção (barra verde) com ícone SVG no lugar do emoji."""
    return (f'<div class="section-title" style="display:flex; align-items:center; gap:10px;">'
            f'{icone(icone_nome, 20, COR_AZUL_ESCURO)}<span>{texto}</span></div>')

def calcular_hash_arquivo(conteudo):
    return hashlib.md5(conteudo).hexdigest()

# ============================================
# FUNÇÃO PRINCIPAL DE CARREGAMENTO DE DADOS
# ============================================
@st.cache_data(ttl=300)
def carregar_dados(uploaded_file=None, caminho_arquivo=None, conteudo_bytes=None):
    """Carrega e processa os dados - Adaptado para o formato do arquivo ADMS.
    Suporta 'Revisões', 'Qtd. Revisões' e variações, criando Revisões_Total (soma das duas)."""
    try:
        if conteudo_bytes is not None:
            try:
                conteudo = conteudo_bytes.decode('utf-8-sig')
            except UnicodeDecodeError:
                conteudo = conteudo_bytes.decode('latin-1')
        elif uploaded_file:
            conteudo_bytes = uploaded_file.getvalue()
            conteudo = conteudo_bytes.decode('utf-8-sig')
        elif caminho_arquivo and os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8-sig') as f:
                conteudo = f.read()
            conteudo_bytes = conteudo.encode('utf-8')
        else:
            return None, "Nenhum arquivo fornecido", None

        lines = conteudo.split('\n')

        # BUSCA FLEXÍVEL PELO CABEÇALHO
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
        df = pd.read_csv(io.StringIO(data_str), quotechar='"', dtype={'Chamado': str})

        # Remove espaços extras dos nomes das colunas
        df.columns = [str(c).strip() for c in df.columns]

        # ============================================
        # MAPEAMENTO DE COLUNAS
        # ============================================
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
            'Motivo Revisão': 'Motivo_Revisao',
            'Motivo Revisao': 'Motivo_Revisao',
            'Retorno Cliente': 'Retorno_Cliente',
            'Vencimento': 'Vencimento',
            'ChangeSet': 'ChangeSet',
            'ID': 'ID',
        }

        rename_dict = {}
        for old, new in col_mapping.items():
            if old in df.columns and new not in df.columns:
                rename_dict[old] = new
        if rename_dict:
            df = df.rename(columns=rename_dict)

        # ============================================
        # TRATAMENTO DAS COLUNAS DE REVISÕES
        # ============================================
        # Padroniza os nomes das colunas de revisões (mantém as duas originais)
        variacoes_revisoes = ['Revisões', 'Revisoes', 'Revisão', 'Revisao']
        variacoes_qtd = ['Qtd. Revisões', 'Qtd. Revisoes', 'Qtd.Revisões', 'Qtd.Revisoes',
                         'Qtd Revisões', 'Qtd Revisoes']

        # Renomeia variações de "Revisões" para o padrão 'Revisões'
        for v in variacoes_revisoes:
            if v in df.columns and v != 'Revisões' and 'Revisões' not in df.columns:
                df = df.rename(columns={v: 'Revisões'})

        # Renomeia variações de "Qtd. Revisões" para o padrão 'Qtd. Revisões'
        for v in variacoes_qtd:
            if v in df.columns and v != 'Qtd. Revisões' and 'Qtd. Revisões' not in df.columns:
                df = df.rename(columns={v: 'Qtd. Revisões'})

        # Garante que ambas existam
        if 'Revisões' not in df.columns:
            df['Revisões'] = 0
        if 'Qtd. Revisões' not in df.columns:
            df['Qtd. Revisões'] = 0

        # Converte para numérico
        df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
        df['Qtd. Revisões'] = pd.to_numeric(df['Qtd. Revisões'], errors='coerce').fillna(0).astype(int)

        # CRIA COLUNA CONSOLIDADA
        df['Revisões_Total'] = df['Revisões'] + df['Qtd. Revisões']

        # ============================================
        # PROCESSAMENTO DE DATAS
        # ============================================
        date_columns = ['Criado', 'Modificado', 'Vencimento']
        for col in date_columns:
            if col in df.columns:
                df[col] = converter_datas(df[col])

        # CRIAÇÃO DE COLUNAS DE DATA
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

        # PROCESSAMENTO DO RESPONSÁVEL
        if 'Responsável' in df.columns:
            df['Responsável_Formatado'] = df['Responsável'].apply(formatar_nome_responsavel)

        # PROCESSAMENTO DE EMPRESA
        if 'Empresa' in df.columns:
            df['Empresa'] = df['Empresa'].astype(str).str.strip()

        # PROCESSAMENTO DE SINCRONIZAÇÃO
        if 'Sincronização' in df.columns:
            df['Sincronização'] = df['Sincronização'].astype(str).str.strip()

        # COLUNAS PRÉ-CALCULADAS (usadas em várias abas; evita .apply dentro de loops)
        if 'Status' in df.columns:
            df['Status'] = df['Status'].astype('string').str.strip()
            df['Sinc'] = df['Status'].eq('Sincronizado').fillna(False).astype(bool)
        else:
            df['Sinc'] = False
        df['Com_Revisao'] = df['Revisões_Total'] > 0
        if 'Retorno_Cliente' in df.columns:
            df['Reaberto'] = df['Retorno_Cliente'].apply(is_retorno_sim)
        if 'SRE' in df.columns:
            df['SRE_Nome'] = df['SRE'].apply(substituir_nome_sre)
        if 'Criado' in df.columns:
            df['Data'] = df['Criado'].dt.normalize()
            df['Mês_Label'] = df['Mês'].map(MESES_ABREV) + '/' + df['Criado'].dt.strftime('%y')

        # Hash só do conteúdo (antes incluía o timestamp e nunca batia na comparação)
        hash_conteudo = calcular_hash_arquivo(conteudo.encode('utf-8'))

        return df, "Dados carregados com sucesso", hash_conteudo

    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"Erro: {str(e)}", None

def encontrar_arquivo_dados():
    if os.path.exists(CAMINHO_ARQUIVO_PRINCIPAL):
        return CAMINHO_ARQUIVO_PRINCIPAL
    for caminho in CAMINHOS_ALTERNATIVOS:
        if os.path.exists(caminho):
            return caminho
    return None

def verificar_e_atualizar_arquivo():
    """True enquanto o CSV local tiver conteúdo diferente do que está carregado.
    Corrigido: o hash agora é calculado do mesmo jeito nos dois lados, e o aviso
    não 'some' na segunda chamada da mesma execução."""
    if st.session_state.get('arquivo_mudou'):
        return True
    caminho_arquivo = encontrar_arquivo_dados()
    if not (caminho_arquivo and os.path.exists(caminho_arquivo)):
        return False
    modificacao_atual = os.path.getmtime(caminho_arquivo)
    if 'ultima_modificacao' not in st.session_state:
        st.session_state.ultima_modificacao = modificacao_atual
        return False
    if modificacao_atual > st.session_state.ultima_modificacao and st.session_state.df_original is not None:
        st.session_state.ultima_modificacao = modificacao_atual
        with open(caminho_arquivo, 'r', encoding='utf-8-sig') as f:
            hash_atual = calcular_hash_arquivo(f.read().encode('utf-8'))
        if hash_atual != st.session_state.get('file_hash'):
            st.session_state.arquivo_mudou = True
            return True
    return False

def limpar_sessao_dados():
    keys_to_clear = ['df_original', 'df_filtrado', 'arquivo_atual',
                     'ultima_modificacao', 'file_hash', 'uploaded_file_name',
                     'ultima_atualizacao', 'arquivo_mudou']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def get_horario_brasilia():
    return agora().strftime('%d/%m/%Y %H:%M:%S')

# ============================================
# FUNÇÕES DO MAPA
# ============================================
def processar_dados_mapa(df, empresas_selecionadas=None, ano_filtro=None, mes_filtro=None):
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
            'sigla': info['sigla'], 'estado': info['estado'], 'regiao': info['regiao'],
            'empresa': empresa, 'empresa_nome': info['nome_completo'],
            'sincronismos': qtd, 'latitude': info['latitude'], 'longitude': info['longitude']
        })
        total_sinc += qtd
    return pd.DataFrame(dados_mapa), total_sinc

def cor_gradiente_folium(valor, min_val, max_val):
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
    try:
        import folium
    except ImportError:
        st.error("Biblioteca 'folium' não instalada. Execute: pip install folium", icon=":material/error:")
        return None
    if df_mapa.empty:
        return None
    df_bolhas = df_mapa[df_mapa['sincronismos'] > 0].copy()
    m = folium.Map(location=[-14.5, -51.5], zoom_start=4, tiles=None, prefer_canvas=True)
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name='CartoDB Positron', max_zoom=19, subdomains='abcd'
    ).add_to(m)
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
        medal = selo_posicao(rank, 22)
        tooltip_html = f"""
        <div style="font-family: 'Inter', 'Segoe UI', sans-serif; min-width: 220px; padding: 4px;">
            <div style="background: {COR_AZUL_ESCURO}; color: white; padding: 10px 14px;
                border-radius: 8px 8px 0 0; font-weight: 700; font-size: 14px;
                display:flex; align-items:center; gap:8px;">
                {medal} {row['empresa_nome']}</div>
            <div style="background: white; border: 1px solid #ddd; border-top: none;
                border-radius: 0 0 8px 8px; padding: 12px 14px;">
                <table style="width:100%; border-collapse:collapse; font-size:13px;">
                    <tr><td style="color:{COR_CINZA_TEXTO}; padding:4px 0;">Código</td>
                        <td style="font-weight:700; text-align:right;">{row['empresa']}</td></tr>
                    <tr><td style="color:{COR_CINZA_TEXTO}; padding:4px 0;">Estado</td>
                        <td style="font-weight:700; text-align:right;">{row['estado']} ({row['sigla']})</td></tr>
                    <tr><td style="color:{COR_CINZA_TEXTO}; padding:4px 0;">Região</td>
                        <td style="font-weight:700; text-align:right;">{row['regiao']}</td></tr>
                    <tr style="border-top:1px solid #eee;">
                        <td style="color:{COR_CINZA_TEXTO}; padding:8px 0 4px;">Sincronizações</td>
                        <td style="font-weight:800; font-size:18px; color:{cor}; text-align:right;">
                            {row['sincronismos']:,}</td></tr>
                    <tr><td style="color:{COR_CINZA_TEXTO}; padding:4px 0;">% do Total</td>
                        <td style="font-weight:600; text-align:right; color:{COR_AZUL_PETROLEO};">{pct:.1f}%</td></tr>
                    <tr><td style="color:{COR_CINZA_TEXTO}; padding:4px 0;">Ranking</td>
                        <td style="font-weight:600; text-align:right;">{rank}º lugar</td></tr>
                </table>
            </div>
        </div>
        """
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']], radius=r,
            color=COR_BRANCO, weight=3, fill=True, fill_color=cor,
            fill_opacity=0.85, tooltip=folium.Tooltip(tooltip_html, sticky=True),
        ).add_to(m)
        font_size_sigla = max(10, min(16, int(r * 0.4)))
        font_size_num = max(9, min(14, int(r * 0.32)))
        label_html = f"""
        <div style="font-family: 'Segoe UI', 'Arial', sans-serif; text-align: center;
            font-weight: 800; line-height: 1.2; white-space: nowrap;">
            <div style="font-size: {font_size_sigla}px; color: white;
                text-shadow: 0 1px 2px rgba(0,0,0,0.7); letter-spacing: 0.3px;">{row['empresa']}</div>
            <div style="font-size: {font_size_num}px; color: white;
                text-shadow: 0 1px 2px rgba(0,0,0,0.6); font-weight: 600;">{row['sincronismos']}</div>
        </div>
        """
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            icon=folium.DivIcon(html=label_html,
                icon_size=(int(r * 1.8), int(r * 1.8)),
                icon_anchor=(int(r * 0.9), int(r * 0.9)),)
        ).add_to(m)
    legenda_html = f"""
    <div style="position: fixed; bottom: 30px; left: 20px; z-index: 9999;
        background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        padding: 14px 20px; font-family: 'Inter', 'Segoe UI', sans-serif; min-width: 210px;
        border: 1px solid {COR_CINZA_BORDA};">
        <div style="font-weight:800; font-size:13px; color:{COR_PRETO_SUAVE}; margin-bottom:12px; letter-spacing:0.5px;">
            <span style="display:inline-flex; align-items:center; gap:6px;">{icone('grafico', 15, COR_AZUL_ESCURO)} VOLUME DE SINCRONIZAÇÕES</span></div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            <div style="width: 140px; height: 12px; border-radius: 6px;
                background: linear-gradient(to right, {COR_AZUL_PETROLEO}, {COR_LARANJA}, {COR_VERMELHO});
                border: 1px solid #ddd;"></div></div>
        <div style="display:flex; justify-content:space-between; font-size:10px; color:{COR_CINZA_TEXTO}; margin-bottom:12px;">
            <span>Menor volume</span><span>Maior volume</span></div>
        <div style="border-top:1px solid {COR_CINZA_BORDA}; padding-top:10px; font-size:10px; color:{COR_CINZA_TEXTO};">
            <div style="display:flex; gap:6px; align-items:flex-start;">{icone('info', 13, COR_CINZA_TEXTO)}
            <span>Passe o mouse sobre uma bolha<br>para ver os detalhes completos</span></div></div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legenda_html))
    if len(df_bolhas_sorted) >= 1:
        top3_rows = df_bolhas_sorted.head(3)
        top3_html_items = ""
        for i, (_, row) in enumerate(top3_rows.iterrows()):
            pct_t = row['sincronismos'] / total * 100 if total > 0 else 0
            cor_top = cor_gradiente_folium(row['sincronismos'], min_sinc, max_sinc)
            top3_html_items += f"""
            <div style="display:flex; align-items:center; gap:10px; padding: 8px 0;
                border-bottom: 1px solid {COR_CINZA_BORDA};">
                {selo_posicao(i + 1, 24)}
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
        <div style="position: fixed; top: 90px; right: 20px; z-index: 9999;
            background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            padding: 14px 18px; font-family: 'Inter', 'Segoe UI', sans-serif; min-width: 240px;
            border: 1px solid {COR_CINZA_BORDA};">
            <div style="font-weight:800; font-size:13px; color:{COR_PRETO_SUAVE}; margin-bottom:10px; letter-spacing:0.5px;">
                <span style="display:inline-flex; align-items:center; gap:6px;">{icone('premio', 15, COR_AZUL_ESCURO)} TOP EMPRESAS</span></div>
            {top3_html_items}
            <div style="padding-top:10px; font-size:11px; color:{COR_CINZA_TEXTO}; text-align:center; border-top:1px solid {COR_CINZA_BORDA}; margin-top:5px;">
                <strong style="color:{COR_AZUL_ESCURO};">Total: {total:,}</strong> sincronizações</div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(painel_html))
    return m

def criar_grafico_barras(df_mapa):
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
                r = int(2 + tt * (245 - 2)); g = int(138 + tt * (124 - 138)); b = int(159 + tt * (0 - 159))
            else:
                tt = (normalized - 0.5) / 0.5
                r = int(245 + tt * (198 - 245)); g = int(124 + tt * (40 - 124)); b = int(0 + tt * (40 - 0))
            cor = f'rgb({r}, {g}, {b})'
        percentual = (row['sincronismos'] / total * 100) if total > 0 else 0
        fig.add_trace(go.Bar(
            x=[row['sincronismos']], y=[f"{row['empresa']} - {row['empresa_nome'][:20]}"],
            orientation='h', text=[f"{fmt_milhar(row['sincronismos'])}  ·  " + f"{percentual:.1f}%".replace('.', ',')],
            textposition='outside', cliponaxis=False, marker_color=cor,
            marker_line_width=0,
            hovertemplate=f"<b>{row['empresa_nome']}</b><br>" +
                          f"Sincronizações: {row['sincronismos']:,}<br>" +
                          f"Percentual: {percentual:.1f}%<br>" +
                          f"Estado: {row['estado']}<br>" +
                          f"Região: {row['regiao']}<extra></extra>",
            name=row['empresa']
        ))
    fig.update_layout(
        title=dict(text="<b>Ranking de sincronizações</b>", font=dict(size=15, color=COR_AZUL_ESCURO), x=0.01),
        xaxis_title="Número de Sincronizações", yaxis_title="", height=450, showlegend=False,
        plot_bgcolor=COR_BRANCO,
        xaxis=dict(gridcolor=COR_CINZA_BORDA, tickformat="d", title_font=dict(size=12)),
        yaxis=dict(gridcolor=COR_CINZA_BORDA, tickfont=dict(size=11), categoryorder='total ascending'),
        margin=dict(l=20, r=80, t=60, b=20), hovermode='closest'
    )
    return fig

# ============================================
# SIDEBAR - FILTROS E CONTROLES
# ============================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 0.6rem 0 0.2rem 0;">
        <h3 style="color: {COR_AZUL_ESCURO}; margin: 0; display:inline-flex; align-items:center; gap:8px;">
            {icone('ajustes', 22, COR_AZUL_ESCURO)} Painel de Controle</h3>
        <p style="color: {COR_CINZA_TEXTO}; margin: 0.2rem 0 0 0; font-size: 0.85rem;">Filtros e Configurações</p>
    </div>
    """, unsafe_allow_html=True)
    if 'df_original' not in st.session_state:
        st.session_state.df_original = None
        st.session_state.df_filtrado = None
        st.session_state.arquivo_atual = None
        st.session_state.file_hash = None
        st.session_state.uploaded_file_name = None
        st.session_state.ultima_atualizacao = None
    if st.session_state.df_original is not None:
        with st.container(border=True):
            st.markdown("**:material/filter_alt: Filtros de Análise**")
            df = st.session_state.df_original.copy()
            if 'Ano' in df.columns:
                anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                if anos_disponiveis:
                    anos_opcoes = ['Todos os Anos'] + list(anos_disponiveis)
                    ano_selecionado = st.selectbox(":material/calendar_month: Ano", options=anos_opcoes, key="filtro_ano")
                    if ano_selecionado != 'Todos os Anos':
                        df = df[df['Ano'] == int(ano_selecionado)]
            if 'Mês' in df.columns:
                meses_disponiveis = sorted(df['Mês'].dropna().unique().astype(int))
                if meses_disponiveis:
                    meses_opcoes = ['Todos os Meses'] + [str(m) for m in meses_disponiveis]
                    mes_selecionado = st.selectbox(
                        ":material/date_range: Mês", options=meses_opcoes, key="filtro_mes",
                        format_func=lambda m: m if m == 'Todos os Meses' else MESES_NOMES[int(m)])
                    if mes_selecionado != 'Todos os Meses':
                        df = df[df['Mês'] == int(mes_selecionado)]
            if 'Responsável_Formatado' in df.columns:
                responsaveis = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
                responsavel_selecionado = st.selectbox(":material/person: Responsável", options=responsaveis, key="filtro_responsavel")
                if responsavel_selecionado != 'Todos':
                    df = df[df['Responsável_Formatado'] == responsavel_selecionado]
            busca_chamado = st.text_input(":material/search: Buscar Chamado", placeholder="Digite número do chamado...", key="busca_chamado")
            if busca_chamado:
                df = df[df['Chamado'].astype(str).str.contains(busca_chamado.strip(), na=False, regex=False)]
            if 'Status' in df.columns:
                status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox(":material/flag: Status", options=status_opcoes, key="filtro_status")
                if status_selecionado != 'Todos':
                    df = df[df['Status'] == status_selecionado]
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos'] + sorted(df['Tipo_Chamado'].dropna().unique())
                tipo_selecionado = st.selectbox(":material/category: Tipo de Chamado", options=tipos, key="filtro_tipo")
                if tipo_selecionado != 'Todos':
                    df = df[df['Tipo_Chamado'] == tipo_selecionado]
            if 'Empresa' in df.columns:
                empresas = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                empresa_selecionada = st.selectbox(":material/apartment: Empresa", options=empresas, key="filtro_empresa")
                if empresa_selecionada != 'Todas':
                    df = df[df['Empresa'] == empresa_selecionada]
            if 'SRE' in df.columns:
                sres = ['Todos'] + sorted(df['SRE'].dropna().unique())
                sre_selecionado = st.selectbox(
                    ":material/engineering: SRE Responsável", options=sres, key="filtro_sre",
                    format_func=lambda v: v if v == 'Todos' else substituir_nome_sre(v))
                if sre_selecionado != 'Todos':
                    df = df[df['SRE'] == sre_selecionado]
            st.session_state.df_filtrado = df
            st.markdown(f"**:material/database: Registros filtrados:** {fmt_milhar(len(df))}")
    with st.container(border=True):
        st.markdown("**:material/sync: Controles de Atualização**")
        if st.session_state.df_original is not None:
            arquivo_atual = st.session_state.arquivo_atual
            if arquivo_atual and isinstance(arquivo_atual, str) and os.path.exists(arquivo_atual):
                tamanho_kb = os.path.getsize(arquivo_atual) / 1024
                ultima_mod = datetime.fromtimestamp(os.path.getmtime(arquivo_atual))
                st.markdown(f"""
                <div style="background: {COR_CINZA_FUNDO}; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem;
                            border: 1px solid {COR_CINZA_BORDA};">
                    <p style="margin: 0 0 0.3rem 0; font-weight: 600; display:flex; align-items:center; gap:6px;">
                        {icone('arquivo', 16, COR_AZUL_ESCURO)} Arquivo atual:</p>
                    <p style="margin: 0; font-size: 0.85rem; color: {COR_PRETO_SUAVE};">{os.path.basename(arquivo_atual)}</p>
                    <p style="margin: 0.3rem 0 0 0; font-size: 0.75rem; color: {COR_CINZA_TEXTO}; display:flex; align-items:center; gap:4px; flex-wrap:wrap;">
                    {icone('base', 12, COR_CINZA_TEXTO)} {tamanho_kb:.1f} KB &nbsp;|&nbsp; {icone('calendario', 12, COR_CINZA_TEXTO)} {ultima_mod.strftime('%d/%m/%Y %H:%M')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                if verificar_e_atualizar_arquivo():
                    st.warning("O arquivo local foi modificado! Clique em 'Recarregar Local' para atualizar.",
                               icon=":material/warning:")
            col_btn1, col_btn2 = st.container(), st.container()
            with col_btn1:
                if st.button("Recarregar Local", icon=":material/refresh:", use_container_width=True, type="primary",
                           help="Recarrega os dados do arquivo local", key="btn_recarregar"):
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
                                    st.session_state.arquivo_mudou = False
                                    st.success(f"Dados atualizados! {fmt_milhar(len(df_atualizado))} registros",
                                               icon=":material/check_circle:")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"Erro ao recarregar: {status}", icon=":material/error:")
                            except Exception as e:
                                st.error(f"Erro: {str(e)}", icon=":material/error:")
                    else:
                        st.error("Arquivo local não encontrado.", icon=":material/error:")
            with col_btn2:
                if st.button("Limpar Tudo", icon=":material/delete:", use_container_width=True, type="secondary",
                           help="Limpa todos os dados e cache", key="btn_limpar"):
                    st.cache_data.clear()
                    limpar_sessao_dados()
                    st.success("Dados e cache limpos!", icon=":material/check_circle:")
                    time.sleep(1)
                    st.rerun()
            st.markdown("---")
        st.markdown("**:material/upload_file: Importar Dados**")
        if st.session_state.df_original is not None:
            ultima_atualizacao = st.session_state.get('ultima_atualizacao') or get_horario_brasilia()
            st.markdown(f"""
            <div class="status-success">
                <strong style="display:inline-flex; align-items:center; gap:6px;">
                    {icone('check', 15, COR_VERDE_ESCURO)} Status atual:</strong><br>
                <small>Registros: {fmt_milhar(len(st.session_state.df_original))}</small><br>
                <small>Atualizado: {ultima_atualizacao}</small>
            </div>
            """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=['csv'],
                                         key="file_uploader",
                                         help="Faça upload de um novo arquivo CSV para substituir os dados atuais",
                                         label_visibility="collapsed")
        if uploaded_file is not None:
            file_details = {"Nome": uploaded_file.name, "Tamanho": f"{uploaded_file.size / 1024:.1f} KB"}
            st.write(":material/description: Detalhes do arquivo:")
            st.json(file_details)
            if st.button("Processar Arquivo", icon=":material/upload:", use_container_width=True, type="primary",
                         key="btn_processar"):
                with st.spinner('Processando novo arquivo...'):
                    # Lê direto da memória (antes gravava um temp_*.csv na pasta do app,
                    # o que podia dar conflito com dois usuários ao mesmo tempo)
                    df_novo, status, hash_conteudo = carregar_dados(conteudo_bytes=uploaded_file.getvalue())
                    if df_novo is not None:
                        st.session_state.df_original = df_novo
                        st.session_state.df_filtrado = df_novo.copy()
                        st.session_state.arquivo_atual = uploaded_file.name
                        st.session_state.file_hash = hash_conteudo
                        st.session_state.uploaded_file_name = uploaded_file.name
                        st.session_state.ultima_atualizacao = get_horario_brasilia()
                        st.session_state.arquivo_mudou = False
                        if 'filtros_aplicados' in st.session_state:
                            del st.session_state.filtros_aplicados
                        st.success(f"{fmt_milhar(len(df_novo))} registros carregados!", icon=":material/check_circle:")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(status, icon=":material/error:")
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
                    st.error(status, icon=":material/error:")

# ============================================
# HEADER - ESTILO GRADIENTE AZUL PETRÓLEO
# ============================================
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {COR_AZUL_PETROLEO} 0%, {COR_AZUL_ESCURO} 100%);
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(2, 138, 159, 0.3);
">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
        <div>
            <h1 style="color: {COR_BRANCO}; margin: 0; font-size: 1.6rem; font-weight: 600;
                letter-spacing: -0.3px; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                <span style="display:inline-flex; align-items:center; gap:10px;">{icone('atividade', 28, COR_BRANCO, 2.4)} ESTEIRA SRE (Site Reliability Engineering)</span>
            </h1>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 0.85rem; font-weight: 400;">
                Acompanhamento das validações da EAC | EMR | EMS | EMT | EPB | ERO | ESE | ESS | ETO
            </p>
        </div>
        <div style="text-align: right;">
            <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 0.85rem; font-weight: 500;">
                Dashboard de Performance
            </p>
            <p style="color: rgba(255,255,255,0.8); margin: 0.2rem 0 0 0; font-size: 0.75rem;">
                v5.6 | Sistema de Performance SRE
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 0.3rem 0 0 0; font-size: 0.7rem; font-weight: 500;">
                {agora().strftime('%d/%m/%Y')}
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
        if st.button("**VER MANCHETE**", icon=":material/newspaper:", help="Clique para ver os principais indicadores do mês",
                    type="secondary", use_container_width=True, key="btn_manchete"):
            st.session_state.show_popup = True

if st.session_state.df_original is not None:
    if verificar_e_atualizar_arquivo():
        st.info("O arquivo local foi atualizado! Clique em 'Recarregar Local' na barra lateral para atualizar os dados.",
                icon=":material/notifications_active:")

def indicadores_periodo(dfp):
    """Indicadores da Manchete. 'Com erro' agora conta só cards SINCRONIZADOS com revisão
    (antes contava todos, e 'Sem erro = validados - com erro' podia dar negativo)."""
    total = len(dfp)
    if total == 0:
        return dict(total=0, validados=0, com_erro=0, sem_erro=0, taxa_sucesso=0.0, taxa_erro=0.0)
    validados = int(dfp['Sinc'].sum())
    com_erro = int((dfp['Sinc'] & dfp['Com_Revisao']).sum())
    return dict(total=total, validados=validados, com_erro=com_erro, sem_erro=validados - com_erro,
                taxa_sucesso=validados / total * 100,
                taxa_erro=(com_erro / validados * 100) if validados > 0 else 0.0)


def grafico_gauge(valor, titulo="Taxa de sucesso"):
    """Medidor da taxa de sucesso com as faixas da classificação de performance."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=valor,
        number=dict(suffix="%", valueformat=".1f", font=dict(size=34, color=COR_AZUL_ESCURO)),
        gauge=dict(
            axis=dict(range=[0, 100], ticksuffix="%", tickfont=dict(size=10)),
            bar=dict(color=COR_AZUL_ESCURO, thickness=0.3),
            bgcolor=COR_BRANCO, borderwidth=0,
            steps=[dict(range=[0, 70], color="#FDECEA"), dict(range=[70, 85], color="#FFF3E0"),
                   dict(range=[85, 95], color="#E0F2F5"), dict(range=[95, 100], color="#E8F5E9")],
            threshold=dict(line=dict(color=COR_VERDE_ESCURO, width=3), thickness=0.85, value=95),
        ),
        title=dict(text=f"{titulo} · meta 95%", font=dict(size=13, color=COR_CINZA_TEXTO)),
    ))
    fig.update_layout(height=250, margin=dict(t=50, b=15, l=35, r=35))
    return fig


if st.session_state.df_original is not None and st.session_state.show_popup:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    with st.expander("**MANCHETE - INDICADORES PRINCIPAIS**", expanded=True, icon=":material/newspaper:"):
        st.markdown("### :material/newspaper: MANCHETE - RELATÓRIO")
        st.markdown("---")
        st.markdown("#### :material/calendar_month: SELECIONE O PERÍODO")
        col_periodo1, col_periodo2 = st.columns(2)
        with col_periodo1:
            periodo_opcoes = ["Mês Atual", "Últimos 30 dias", "Últimos 90 dias",
                              "Este Ano", "Ano Passado", "Todo o Período"]
            periodo_selecionado = st.selectbox("Período de análise:", options=periodo_opcoes,
                                               index=0, key="popup_periodo")
        with col_periodo2:
            if 'Ano' in df.columns:
                anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                if anos_disponiveis:
                    ano_especifico = st.selectbox("Ou selecione um ano:",
                                                  options=['Selecionar ano...'] + list(anos_disponiveis),
                                                  key="popup_ano",
                                                  help="Quando um ano é escolhido aqui, ele tem prioridade sobre o período ao lado")
                else:
                    ano_especifico = 'Selecionar ano...'
            else:
                ano_especifico = 'Selecionar ano...'
        hoje = agora()
        hoje_d = pd.Timestamp(hoje).normalize()
        amanha = hoje_d + timedelta(days=1)
        df_filtrado_periodo = df.copy()
        df_anterior = df.iloc[0:0]
        periodo_titulo = ""
        periodo_anterior_titulo = ""

        def entre(ini, fim):
            return df[(df['Criado'] >= ini) & (df['Criado'] < fim)].copy()

        # Corrigido: antes o "ano específico" nunca era aplicado (ficava num elif inalcançável)
        if ano_especifico != 'Selecionar ano...':
            ano_esc = int(ano_especifico)
            df_filtrado_periodo = df[df['Criado'].dt.year == ano_esc].copy()
            df_anterior = df[df['Criado'].dt.year == ano_esc - 1].copy()
            periodo_titulo = f"Ano {ano_esc}"
            periodo_anterior_titulo = f"Ano {ano_esc - 1}"
        elif periodo_selecionado == "Mês Atual":
            ini_mes = hoje_d.replace(day=1)
            ini_ant = (ini_mes - timedelta(days=1)).replace(day=1)
            fim_ant = min(ini_ant + timedelta(days=hoje_d.day), ini_mes)
            df_filtrado_periodo = entre(ini_mes, amanha)
            # Compara com o MESMO trecho do mês anterior (dia 1 até o mesmo dia),
            # para o mês em andamento não parecer sempre pior que o anterior completo
            df_anterior = entre(ini_ant, fim_ant)
            periodo_titulo = f"Mês Atual ({hoje.month:02d}/{hoje.year})"
            periodo_anterior_titulo = f"{ini_ant.month:02d}/{ini_ant.year} até dia {hoje_d.day}"
        elif periodo_selecionado in ("Últimos 30 dias", "Últimos 90 dias"):
            n = 30 if "30" in periodo_selecionado else 90
            ini = amanha - timedelta(days=n)
            df_filtrado_periodo = entre(ini, amanha)
            df_anterior = entre(ini - timedelta(days=n), ini)
            periodo_titulo = periodo_selecionado
            periodo_anterior_titulo = f"{n} dias anteriores"
        elif periodo_selecionado == "Este Ano":
            ano_atual = hoje.year
            df_filtrado_periodo = df[df['Criado'].dt.year == ano_atual].copy()
            ini_ant = pd.Timestamp(ano_atual - 1, 1, 1)
            df_anterior = entre(ini_ant, ini_ant + (hoje_d - pd.Timestamp(ano_atual, 1, 1)) + timedelta(days=1))
            periodo_titulo = f"Este Ano ({ano_atual})"
            periodo_anterior_titulo = f"{ano_atual - 1} (mesmo trecho)"
        elif periodo_selecionado == "Ano Passado":
            ano_passado = hoje.year - 1
            df_filtrado_periodo = df[df['Criado'].dt.year == ano_passado].copy()
            df_anterior = df[df['Criado'].dt.year == ano_passado - 1].copy()
            periodo_titulo = f"Ano Passado ({ano_passado})"
            periodo_anterior_titulo = f"Ano {ano_passado - 1}"
        elif periodo_selecionado == "Todo o Período":
            periodo_titulo = "Todo o Período Disponível"

        atual_ind = indicadores_periodo(df_filtrado_periodo)
        ant_ind = indicadores_periodo(df_anterior)
        total_cards = atual_ind['total']
        validados = atual_ind['validados']
        com_erro = atual_ind['com_erro']
        sem_erro = atual_ind['sem_erro']
        taxa_sucesso = atual_ind['taxa_sucesso']
        taxa_erro = atual_ind['taxa_erro']
        total_cards_anterior = ant_ind['total']
        validados_anterior = ant_ind['validados']
        com_erro_anterior = ant_ind['com_erro']
        taxa_sucesso_anterior = ant_ind['taxa_sucesso']

        st.markdown(f"#### :material/target: DESTAQUE DO PERÍODO: {periodo_titulo}")
        if total_cards == 0:
            st.error(f"**NENHUM DADO DISPONÍVEL** para {periodo_titulo.lower()}", icon=":material/error:")
        elif com_erro == 0 and validados > 0:
            st.success(f"**SRE VALIDOU {validados} CARDS SEM RETORNO DE ERRO!**", icon=":material/verified:")
            st.info(f"Performance excepcional - 100% de aprovação direta", icon=":material/workspace_premium:")
        elif taxa_erro <= 5:
            st.warning(f"**SRE VALIDOU {validados} CARDS COM APENAS {com_erro} AJUSTES**", icon=":material/bolt:")
            st.info(f"Alta qualidade - Taxa de erro: {taxa_erro:.1f}%".replace('.', ','), icon=":material/insights:")
        else:
            st.warning(f"**SRE VALIDOU {validados} CARDS, {com_erro} COM RETORNO**", icon=":material/assignment_return:")
            st.info(f"Taxa de sucesso: {taxa_sucesso:.1f}% | {sem_erro} cards perfeitos".replace('.', ','),
                    icon=":material/insights:")
        st.markdown("---")
        if total_cards_anterior > 0:
            st.markdown("#### :material/compare_arrows: COMPARAÇÃO COM PERÍODO ANTERIOR")
            periodos = [periodo_anterior_titulo, periodo_titulo]
            cards_totais = [total_cards_anterior, total_cards]
            cards_validados = [validados_anterior, validados]
            cards_retorno = [com_erro_anterior, com_erro]
            taxa_sucesso_vals = [taxa_sucesso_anterior, taxa_sucesso]
            fig_comparativo = go.Figure()
            fig_comparativo.add_trace(go.Bar(x=periodos, y=cards_totais, name='Total Cards',
                                             marker_color="#B9DDE3", text=cards_totais,
                                             textposition='outside', cliponaxis=False))
            fig_comparativo.add_trace(go.Bar(x=periodos, y=cards_validados, name='Validados',
                                             marker_color=COR_AZUL_ESCURO, text=cards_validados,
                                             textposition='outside', cliponaxis=False))
            fig_comparativo.add_trace(go.Bar(x=periodos, y=cards_retorno, name='Com retorno',
                                             marker_color=COR_LARANJA, text=cards_retorno,
                                             textposition='outside', cliponaxis=False))
            fig_comparativo.add_trace(go.Scatter(x=periodos, y=taxa_sucesso_vals, name='Taxa Sucesso',
                                                 yaxis='y2', mode='lines+markers+text',
                                                 line=dict(color=COR_VERDE_ESCURO, width=2.5, dash='dot'),
                                                 marker=dict(size=10, color=COR_VERDE_ESCURO,
                                                             line=dict(color=COR_BRANCO, width=2)),
                                                 text=[f"{v:.1f}%" for v in taxa_sucesso_vals],
                                                 textposition='top center', textfont=dict(size=11, color=COR_VERDE_ESCURO)))
            fig_comparativo.update_layout(
                title=dict(text='Comparativo: Período Atual vs Anterior'),
                barmode='group', bargap=0.3, bargroupgap=0.08,
                yaxis=dict(title=dict(text='Quantidade', font=dict(size=11)), rangemode='tozero'),
                yaxis2=dict(title=dict(text='Taxa Sucesso (%)', font=dict(size=11)),
                            overlaying='y', side='right', showgrid=False,
                            range=[0, max(115, max(taxa_sucesso_vals) * 1.15)], ticksuffix='%'),
                height=340, showlegend=True,
                margin=dict(l=50, r=50, t=50, b=80),
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, font=dict(size=11)),
                hovermode='x unified'
            )
            st.plotly_chart(fig_comparativo, use_container_width=True, config={'displayModeBar': False})
            variacao_total = ((total_cards - total_cards_anterior) / total_cards_anterior * 100)
            variacao_validados = ((validados - validados_anterior) / validados_anterior * 100) if validados_anterior > 0 else 0
            variacao_taxa = taxa_sucesso - taxa_sucesso_anterior
            st.markdown("##### :material/percent: VARIAÇÃO PERCENTUAL")
            col_var1, col_var2, col_var3 = st.columns(3)
            # Corrigido: delta_color "inverse" em valores negativos deixava a QUEDA verde.
            # "normal" já colore sozinho: subida verde, queda vermelha.
            with col_var1:
                st.metric(label=":material/assignment: Total Cards", value=fmt_milhar(total_cards),
                          delta=f"{variacao_total:+.1f}%", delta_color="normal",
                          help=f"Anterior ({periodo_anterior_titulo}): {fmt_milhar(total_cards_anterior)}")
            with col_var2:
                st.metric(label=":material/task_alt: Validados", value=fmt_milhar(validados),
                          delta=f"{variacao_validados:+.1f}%", delta_color="normal",
                          help=f"Anterior ({periodo_anterior_titulo}): {fmt_milhar(validados_anterior)}")
            with col_var3:
                st.metric(label=":material/speed: Taxa Sucesso", value=f"{taxa_sucesso:.1f}%",
                          delta=f"{variacao_taxa:+.1f}pp", delta_color="normal",
                          help=f"Anterior ({periodo_anterior_titulo}): {taxa_sucesso_anterior:.1f}%")
            st.markdown("---")
        st.markdown("#### :material/monitoring: INDICADORES PRINCIPAIS")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(":material/assignment: Total Cards", fmt_milhar(total_cards), delta=None,
                      help="Total de cards no período")
        with col2:
            st.metric(":material/task_alt: Validados", fmt_milhar(validados), f"{taxa_sucesso:.1f}% do total",
                      delta_color="off", **DELTA_SEM_SETA,
                      help="Cards sincronizados (aprovados)")
        with col3:
            st.metric(":material/verified: Sem Erro", fmt_milhar(sem_erro),
                      f"{(sem_erro / validados * 100) if validados > 0 else 0:.1f}% dos validados",
                      delta_color="off", **DELTA_SEM_SETA,
                      help="Sincronizados aprovados na primeira validação")
        with col4:
            st.metric(":material/report: Com Erro", fmt_milhar(com_erro),
                      f"{taxa_erro:.1f}% dos validados", delta_color="off", **DELTA_SEM_SETA,
                      help="Sincronizados que retornaram para ajuste")
        st.markdown("---")
        st.markdown("#### :material/analytics: ANÁLISE DETALHADA")
        if total_cards > 0:
            if 'Criado' in df_filtrado_periodo.columns and len(df_filtrado_periodo) > 0:
                dias_unicos = df_filtrado_periodo['Criado'].dt.date.nunique()
                media_diaria = total_cards / dias_unicos if dias_unicos > 0 else 0
                col_analise1, col_analise2, col_analise3 = st.columns(3)
                with col_analise1:
                    st.metric(":material/event_available: Dias com atividade", dias_unicos)
                with col_analise2:
                    st.metric(":material/bar_chart: Média diária", f"{media_diaria:.1f}".replace('.', ','))
                with col_analise3:
                    if 'Revisões_Total' in df_filtrado_periodo.columns:
                        media_revisoes = df_filtrado_periodo['Revisões_Total'].mean()
                        st.metric(":material/edit_note: Média revisões/card", f"{media_revisoes:.2f}".replace('.', ','))
                    else:
                        st.metric(":material/edit_note: Revisões", "N/A")
            st.markdown("##### :material/emoji_events: CLASSIFICAÇÃO DE PERFORMANCE")
            col_gauge, col_class = st.columns([1, 1.3])
            with col_gauge:
                st.plotly_chart(grafico_gauge(taxa_sucesso), use_container_width=True, config={'displayModeBar': False})
            with col_class:
                if taxa_sucesso >= 95:
                    st.success("""
                    **EXCELENTE**
                    - Meta de qualidade superada (>95%)
                    - Processos altamente eficientes
                    - Recomendação: Manter padrões atuais
                    """, icon=":material/star:")
                elif taxa_sucesso >= 85:
                    st.info("""
                    **BOM DESEMPENHO**
                    - Dentro dos padrões esperados (85-94%)
                    - Processos consistentes
                    - Recomendação: Pequenos ajustes pontuais
                    """, icon=":material/thumb_up:")
                elif taxa_sucesso >= 70:
                    st.warning("""
                    **OPORTUNIDADE DE MELHORIA**
                    - Abaixo do ideal (70-84%)
                    - Processos precisam de revisão
                    - Recomendação: Identificar causas principais
                    """, icon=":material/trending_up:")
                else:
                    st.error("""
                    **ATENÇÃO NECESSÁRIA**
                    - Performance crítica (<70%)
                    - Processos ineficientes
                    - Recomendação: Revisão urgente dos fluxos
                    """, icon=":material/priority_high:")
        else:
            st.info(f"Nenhum dado disponível para análise no período: {periodo_titulo}", icon=":material/info:")
        st.markdown("---")
        st.markdown(f"""
        <div style="background: {COR_CINZA_FUNDO}; padding: 1.2rem; border-radius: 8px; border: 1px solid {COR_CINZA_BORDA};">
            <p style="margin: 0; color: {COR_PRETO_SUAVE}; font-weight: 600;">Ações disponíveis</p>
            <p style="margin: 0.3rem 0 0 0; color: {COR_CINZA_TEXTO}; font-size: 0.85rem;">
            Exporte o relatório completo ou feche a manchete
            </p>
        </div>
        """, unsafe_allow_html=True)
        col_exportar, col_fechar = st.columns(2)
        with col_exportar:
            if st.button("**EXPORTAR PDF**", icon=":material/picture_as_pdf:", type="primary", use_container_width=True,
                        help="Gerar relatório completo em formato PDF", key="btn_exportar_pdf_final"):
                st.info("""
                **Funcionalidade de PDF em desenvolvimento...**
                Para uma implementação completa, você pode usar:
                - `fpdf` ou `reportlab` para gerar PDFs
                - `weasyprint` para converter HTML para PDF
                - `pdfkit` (requer wkhtmltopdf)
                """, icon=":material/construction:")
        with col_fechar:
            if st.button("**FECHAR**", icon=":material/close:", type="secondary", use_container_width=True,
                         key="btn_fechar_final"):
                st.session_state.show_popup = False
                st.rerun()
        st.markdown(f"""
        <div style="background: {COR_CINZA_FUNDO}; padding: 0.8rem; border-radius: 6px; margin-top: 1rem;
                    display:flex; flex-direction:column; gap:4px; font-size:0.85rem;">
            <span style="display:flex; align-items:center; gap:6px;">{icone('calendario', 14, COR_CINZA_TEXTO)} <strong>Período analisado:</strong> {periodo_titulo}</span>
            <span style="display:flex; align-items:center; gap:6px;">{icone('relogio', 14, COR_CINZA_TEXTO)} <strong>Atualizado em:</strong> {hoje.strftime('%d/%m/%Y %H:%M')}</span>
            <span style="display:flex; align-items:center; gap:6px;">{icone('base', 14, COR_CINZA_TEXTO)} <strong>Base de dados:</strong> {fmt_milhar(len(df))} registros totais</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# EXIBIR DASHBOARD SE HOUVER DADOS
# ============================================
if st.session_state.df_original is not None:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    tab_principal, tab_mapa, tab_ipe, tab_estatistica = st.tabs([
        ":material/dashboard: Principal", ":material/map: Mapa",
        ":material/target: KPI", ":material/query_stats: Análise Estatística"])
    with tab_principal:
        st.markdown("## :material/database: Base de Dados")
        if 'Criado' in df.columns and not df.empty:
            data_min = df['Criado'].min()
            data_max = df['Criado'].max()
            st.markdown(f"""
            <div class="info-base">
                <p style="margin: 0; font-weight: 600; display:flex; align-items:center; gap:8px;">
                    {icone('calendario', 18, COR_VERDE_ESCURO)} Base atualizada em: {get_horario_brasilia()}</p>
                <p style="margin: 0.3rem 0 0 0; color: {COR_CINZA_TEXTO};">
                Período coberto: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')} |
                Total de registros: {fmt_milhar(len(df))}
                </p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("## :material/monitoring: INDICADORES PRINCIPAIS")
        col1, col2, col3 = st.columns(3)
        total_atual = len(df)
        with col1:
            st.markdown(criar_card_indicador_simples(total_atual, "Total de Demandas", "lista",
                                                     subtitulo="cards no recorte atual"), unsafe_allow_html=True)
        with col2:
            if 'Status' in df.columns:
                sincronizados = int(df['Sinc'].sum())
                pct_sinc = f"{(sincronizados / total_atual * 100) if total_atual else 0:.1f}".replace('.', ',')
                st.markdown(criar_card_indicador_simples(sincronizados, "Sincronizados", "check",
                                                         subtitulo=f"{pct_sinc}% das demandas", cor=COR_VERDE_ESCURO),
                            unsafe_allow_html=True)
        with col3:
            if 'Revisões_Total' in df.columns:
                total_revisoes = int(df['Revisões_Total'].sum())
                cards_com_rev = int(df['Com_Revisao'].sum())
                st.markdown(criar_card_indicador_simples(total_revisoes, "Total de Revisões", "revisao",
                                                         subtitulo=f"em {fmt_milhar(cards_com_rev)} cards", cor=COR_LARANJA),
                            unsafe_allow_html=True)
        st.markdown("---")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            ":material/calendar_month: Evolução de Demandas",
            ":material/rate_review: Análise de Revisões",
            ":material/show_chart: Sincronização Diária",
            ":material/emoji_events: Análise Avançada SRE",
            ":material/fact_check: Motivos de Revisão"
        ])
        with tab1:
            col_titulo, col_seletor = st.columns([3, 1])
            anos_disponiveis = []
            with col_titulo:
                st.markdown(titulo_secao("EVOLUÇÃO DE DEMANDAS POR MÊS", "calendario"), unsafe_allow_html=True)
            with col_seletor:
                if 'Ano' in df.columns:
                    anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                    if anos_disponiveis:
                        ano_selecionado = st.selectbox("Selecionar Ano:", options=anos_disponiveis,
                                                       index=len(anos_disponiveis)-1,
                                                       label_visibility="collapsed", key="ano_evolucao")
            if 'Ano' in df.columns and 'Nome_Mês' in df.columns and anos_disponiveis:
                df_ano = df[df['Ano'] == ano_selecionado].copy()
                if not df_ano.empty:
                    ordem_meses_abreviados = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                                             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                    todos_meses = pd.DataFrame({'Mês_Num': range(1, 13), 'Nome_Mês': ordem_meses_abreviados})
                    demandas_por_mes = df_ano.groupby('Mês_Num').size().reset_index()
                    demandas_por_mes.columns = ['Mês_Num', 'Quantidade']
                    sinc_por_mes = df_ano[df_ano['Sinc']].groupby('Mês_Num').size().rename('Sincronizados').reset_index()
                    demandas_completas = pd.merge(todos_meses, demandas_por_mes, on='Mês_Num', how='left')
                    demandas_completas = pd.merge(demandas_completas, sinc_por_mes, on='Mês_Num', how='left')
                    demandas_completas[['Quantidade', 'Sincronizados']] = (
                        demandas_completas[['Quantidade', 'Sincronizados']].fillna(0).astype(int))
                    # Meses que ainda não chegaram (ano corrente) ficam sem ponto, em vez de cair a zero
                    if ano_selecionado == agora().year:
                        futuros = demandas_completas['Mês_Num'] > agora().month
                        demandas_completas[['Quantidade', 'Sincronizados']] = (
                            demandas_completas[['Quantidade', 'Sincronizados']].astype(float).mask(
                                futuros.values.reshape(-1, 1).repeat(2, axis=1)))
                    fig_mes = go.Figure()
                    fig_mes.add_trace(go.Scatter(
                        x=demandas_completas['Nome_Mês'], y=demandas_completas['Quantidade'],
                        mode='lines+markers+text', name='Demandas', line_shape='spline',
                        line=dict(color=COR_AZUL_ESCURO, width=3),
                        fill='tozeroy', fillcolor='rgba(0, 89, 115, 0.08)',
                        marker=dict(size=9, color=COR_AZUL_ESCURO, line=dict(color=COR_BRANCO, width=2)),
                        text=demandas_completas['Quantidade'].map(lambda v: '' if pd.isna(v) else int(v)),
                        textposition='top center',
                        textfont=dict(size=12, color=COR_AZUL_ESCURO),
                        hovertemplate='%{x}: %{y} demandas<extra></extra>'
                    ))
                    fig_mes.add_trace(go.Scatter(
                        x=demandas_completas['Nome_Mês'], y=demandas_completas['Sincronizados'],
                        mode='lines+markers', name='Sincronizados', line_shape='spline',
                        line=dict(color=COR_VERDE_ESCURO, width=2, dash='dot'),
                        marker=dict(size=7, color=COR_VERDE_ESCURO),
                        hovertemplate='%{x}: %{y} sincronizados<extra></extra>'
                    ))
                    fig_mes.update_layout(
                        title=f"Demandas em {ano_selecionado}", xaxis_title="Mês",
                        yaxis_title="Número de Demandas",
                        height=450, showlegend=True, margin=dict(t=70, b=50, l=50, r=30),
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                        xaxis=dict(showgrid=False, categoryorder='array', categoryarray=ordem_meses_abreviados),
                        yaxis=dict(rangemode='tozero'),
                        hovermode='x unified'
                    )
                    total_ano = int(demandas_completas['Quantidade'].fillna(0).sum())
                    fig_mes.add_annotation(
                        x=0.01, y=1.0, xref="paper", yref="paper", xanchor='left', yanchor='bottom',
                        text=f"Total no ano: <b>{fmt_milhar(total_ano)}</b> demandas", showarrow=False,
                        font=dict(size=12, color=COR_AZUL_ESCURO),
                        bgcolor="rgba(2,138,159,0.08)", borderpad=6
                    )
                    st.plotly_chart(fig_mes, use_container_width=True)
                    col_stats1, col_stats2, col_stats3 = st.columns(3)
                    meses_com_dado = demandas_completas[demandas_completas['Quantidade'].fillna(0) > 0]
                    with col_stats1:
                        mes_max = demandas_completas.loc[demandas_completas['Quantidade'].idxmax()]
                        st.metric(":material/trending_up: Mês com mais demandas", f"{mes_max['Nome_Mês']}: {fmt_milhar(mes_max['Quantidade'])}")
                    with col_stats2:
                        # Considera só meses que já têm dados (antes meses futuros zerados viravam o "mínimo")
                        base_min = meses_com_dado if not meses_com_dado.empty else demandas_completas
                        mes_min = base_min.loc[base_min['Quantidade'].idxmin()]
                        st.metric(":material/trending_down: Mês com menos demandas", f"{mes_min['Nome_Mês']}: {fmt_milhar(mes_min['Quantidade'])}")
                    with col_stats3:
                        media_mensal = int(round(meses_com_dado['Quantidade'].mean())) if not meses_com_dado.empty else 0
                        st.metric(":material/functions: Média mensal", fmt_milhar(media_mensal),
                                  help="Média dos meses com registro no ano selecionado")
        with tab2:
            st.markdown(titulo_secao("REVISÕES POR RESPONSÁVEL", "revisao"), unsafe_allow_html=True)
            col_rev_filtro1, col_rev_filtro2 = st.columns(2)
            ano_rev, mes_rev = 'Todos os Anos', 'Todos os Meses'
            with col_rev_filtro1:
                if 'Ano' in df.columns:
                    anos_rev = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_rev = ['Todos os Anos'] + list(anos_rev)
                    ano_rev = st.selectbox(":material/calendar_month: Filtrar por Ano:", options=anos_opcoes_rev, key="filtro_ano_revisoes")
            with col_rev_filtro2:
                if 'Mês' in df.columns:
                    meses_rev = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_rev = ['Todos os Meses'] + [str(m) for m in meses_rev]
                    mes_rev = st.selectbox(":material/date_range: Filtrar por Mês:", options=meses_opcoes_rev, key="filtro_mes_revisoes",
                                           format_func=lambda m: m if m == 'Todos os Meses' else MESES_NOMES[int(m)])
            df_rev = df.copy()
            if ano_rev != 'Todos os Anos':
                df_rev = df_rev[df_rev['Ano'] == int(ano_rev)]
            if mes_rev != 'Todos os Meses':
                df_rev = df_rev[df_rev['Mês'] == int(mes_rev)]
            if 'Revisões_Total' in df_rev.columns and 'Responsável_Formatado' in df_rev.columns:
                df_com_revisoes = df_rev[df_rev['Revisões_Total'] > 0].copy()
                if df_com_revisoes.empty:
                    st.success("Nenhuma revisão registrada no período selecionado.", icon=":material/verified:")
                else:
                    revisoes_por_responsavel = df_com_revisoes.groupby('Responsável_Formatado').agg({
                        'Revisões_Total': 'sum', 'Chamado': 'count'
                    }).reset_index()
                    revisoes_por_responsavel.columns = ['Responsável', 'Total_Revisões', 'Chamados_Com_Revisão']
                    revisoes_por_responsavel = revisoes_por_responsavel.sort_values('Total_Revisões', ascending=False)
                    titulo_rev = 'Top 15 Responsáveis com Mais Revisões'
                    if ano_rev != 'Todos os Anos':
                        titulo_rev += f' - {ano_rev}'
                    if mes_rev != 'Todos os Meses':
                        titulo_rev += f' - {MESES_NOMES[int(mes_rev)]}'
                    top15 = revisoes_por_responsavel.head(15).iloc[::-1]  # maior no topo (barras horizontais)
                    max_revisoes = top15['Total_Revisões'].max()
                    min_revisoes = top15['Total_Revisões'].min()
                    colors = []
                    for valor in top15['Total_Revisões']:
                        # Mesmo gradiente verde → vermelho de antes (menos → mais revisões)
                        if max_revisoes == min_revisoes:
                            colors.append(COR_VERMELHO)
                        else:
                            normalized = (valor - min_revisoes) / (max_revisoes - min_revisoes)
                            red = int(198 * normalized + 40 * (1 - normalized))
                            green = int(40 * normalized + 167 * (1 - normalized))
                            blue = int(40 * normalized + 69 * (1 - normalized))
                            colors.append(f'rgb({red}, {green}, {blue})')
                    fig_revisoes = go.Figure()
                    fig_revisoes.add_trace(go.Bar(
                        y=top15['Responsável'], x=top15['Total_Revisões'], orientation='h',
                        name='Total de Revisões',
                        text=top15['Total_Revisões'], textposition='outside', cliponaxis=False,
                        marker_color=colors, marker_line_width=0,
                        customdata=top15['Chamados_Com_Revisão'],
                        hovertemplate='<b>%{y}</b><br>%{x} revisões em %{customdata} chamados<extra></extra>'
                    ))
                    fig_revisoes.update_layout(
                        title=titulo_rev, xaxis_title='Total de Revisões', yaxis_title='',
                        height=max(380, 34 * len(top15) + 120), showlegend=False,
                        margin=dict(t=50, b=40, l=10, r=50),
                        xaxis=dict(rangemode='tozero'), yaxis=dict(showgrid=False)
                    )
                    st.plotly_chart(fig_revisoes, use_container_width=True)
                    col_rv1, col_rv2, col_rv3 = st.columns(3)
                    col_rv1.metric(":material/edit_note: Total de revisões", fmt_milhar(df_com_revisoes['Revisões_Total'].sum()))
                    col_rv2.metric(":material/assignment_late: Chamados com revisão", fmt_milhar(len(df_com_revisoes)),
                                   help=f"De {fmt_milhar(len(df_rev))} chamados no período")
                    col_rv3.metric(":material/person_alert: Responsável com mais revisões",
                                   revisoes_por_responsavel.iloc[0]['Responsável'],
                                   f"{int(revisoes_por_responsavel.iloc[0]['Total_Revisões'])} revisões",
                                   delta_color="off", **DELTA_SEM_SETA)
        with tab3:
            st.markdown(titulo_secao("CHAMADOS SINCRONIZADOS POR DIA - ANÁLISE COMPLETA", "subida"), unsafe_allow_html=True)
            col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
            ano_sinc, mes_sinc, sre_sinc, empresa_sinc = 'Todos os Anos', 'Todos os Meses', 'Todos os SREs', 'Todas Empresas'
            with col_filtro1:
                if 'Ano' in df.columns:
                    anos_sinc = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_sinc = ['Todos os Anos'] + list(anos_sinc)
                    ano_sinc = st.selectbox(":material/calendar_month: Ano:", options=anos_opcoes_sinc, key="filtro_ano_sinc")
            with col_filtro2:
                if 'Mês' in df.columns:
                    meses_sinc = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_sinc = ['Todos os Meses'] + [str(m) for m in meses_sinc]
                    mes_sinc = st.selectbox(":material/date_range: Mês:", options=meses_opcoes_sinc, key="filtro_mes_sinc",
                                            format_func=lambda m: m if m == 'Todos os Meses' else MESES_NOMES[int(m)])
            with col_filtro3:
                if 'SRE' in df.columns:
                    sres_sinc = ['Todos os SREs'] + sorted(df['SRE'].dropna().unique())
                    sre_sinc = st.selectbox(":material/engineering: SRE:", options=sres_sinc, key="filtro_sre_sinc",
                                            format_func=lambda v: v if v == 'Todos os SREs' else substituir_nome_sre(v))
            with col_filtro4:
                if 'Empresa' in df.columns:
                    empresas_sinc = ['Todas Empresas'] + sorted(df['Empresa'].dropna().unique())
                    empresa_sinc = st.selectbox(":material/apartment: Empresa:", options=empresas_sinc, key="filtro_empresa_sinc")
            df_sinc = df.copy()
            if ano_sinc != 'Todos os Anos':
                df_sinc = df_sinc[df_sinc['Ano'] == int(ano_sinc)]
            if mes_sinc != 'Todos os Meses':
                df_sinc = df_sinc[df_sinc['Mês'] == int(mes_sinc)]
            if sre_sinc != 'Todos os SREs':
                df_sinc = df_sinc[df_sinc['SRE'] == sre_sinc]
            if empresa_sinc != 'Todas Empresas':
                df_sinc = df_sinc[df_sinc['Empresa'] == empresa_sinc]
            if 'Status' in df_sinc.columns and 'Criado' in df_sinc.columns:
                df_sincronizados = df_sinc[df_sinc['Sinc']].copy()
                if not df_sincronizados.empty:
                    df_sincronizados = df_sincronizados.sort_values('Criado')
                    dias_semana_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                    # Série diária COM os dias úteis zerados (corrige "Dias sem Sinc." sempre 0)
                    serie_sinc = serie_diaria(df_sincronizados['Data'])
                    sincronizados_por_dia = serie_sinc.rename_axis('Data').reset_index(name='Quantidade')
                    uteis = sincronizados_por_dia[sincronizados_por_dia['Data'].dt.dayofweek < 5]
                    st.markdown("### :material/monitoring: Indicadores Principais")
                    total_sincronizados = int(sincronizados_por_dia['Quantidade'].sum())
                    media_diaria = uteis['Quantidade'].mean() if not uteis.empty else sincronizados_por_dia['Quantidade'].mean()
                    max_dia = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmax()]
                    base_min = uteis if not uteis.empty else sincronizados_por_dia
                    min_dia = base_min.loc[base_min['Quantidade'].idxmin()]
                    dias_com_zero = int((uteis['Quantidade'] == 0).sum())
                    dias_trabalhados = int((sincronizados_por_dia['Quantidade'] > 0).sum())
                    # Variação: média dos últimos 7 dias úteis vs os 7 anteriores
                    # (antes comparava só o primeiro com o último dia, o que oscilava muito)
                    variacao = None
                    if len(uteis) >= 14:
                        recentes = uteis['Quantidade'].iloc[-7:].mean()
                        anteriores = uteis['Quantidade'].iloc[-14:-7].mean()
                        if anteriores > 0:
                            variacao = (recentes - anteriores) / anteriores * 100
                    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
                    with col_kpi1:
                        st.metric(":material/task_alt: Total Sincronizado", fmt_milhar(total_sincronizados),
                                  f"{variacao:+.1f}% (7 dias úteis)" if variacao is not None else None,
                                  delta_color="normal",
                                  help="Variação: média dos últimos 7 dias úteis vs os 7 anteriores")
                    with col_kpi2:
                        st.metric(":material/bar_chart: Média Diária", f"{media_diaria:.1f}".replace('.', ','),
                                  f"Dias com sinc.: {dias_trabalhados}", delta_color="off", **DELTA_SEM_SETA,
                                  help="Média por dia útil, contando os dias sem sincronização como zero")
                    with col_kpi3:
                        st.metric(":material/trending_up: Dia com Mais Sinc.", fmt_milhar(max_dia['Quantidade']),
                                  f"{max_dia['Data'].strftime('%d/%m')}", delta_color="off", **DELTA_SEM_SETA)
                    with col_kpi4:
                        st.metric(":material/event_busy: Dias sem Sinc.", f"{dias_com_zero}",
                                  f"Menor dia útil {min_dia['Data'].strftime('%d/%m')}: {int(min_dia['Quantidade'])}",
                                  delta_color="off", **DELTA_SEM_SETA, help=f"Dias úteis sem sincronização, de {len(uteis)} no intervalo")
                    with st.expander("Visualização Detalhada por Dia", expanded=False, icon=":material/table_view:"):
                        tabela_detalhada = sincronizados_por_dia.copy()
                        tabela_detalhada['Dia_Semana_PT'] = tabela_detalhada['Data'].dt.dayofweek.map(dict(enumerate(dias_semana_pt)))
                        tabela_detalhada['Diferenca'] = tabela_detalhada['Quantidade'].diff()
                        qtd_anterior = tabela_detalhada['Quantidade'].shift(1).astype(float)
                        # Dia anterior com 0 sincronizações fica sem variação % (evita divisão por zero)
                        tabela_detalhada['Variacao_%'] = (tabela_detalhada['Diferenca'].astype(float)
                                                          / qtd_anterior.where(qtd_anterior > 0) * 100).round(1)
                        tabela_detalhada['Media_Movel_7'] = tabela_detalhada['Quantidade'].rolling(window=7, min_periods=1).mean().round(1)
                        tabela_detalhada['Data_Formatada'] = tabela_detalhada['Data'].dt.strftime('%d/%m/%Y')
                        tabela_detalhada = tabela_detalhada.sort_values('Data', ascending=False)
                        colunas_exibir = ['Data_Formatada', 'Dia_Semana_PT', 'Quantidade',
                                          'Diferenca', 'Variacao_%', 'Media_Movel_7']
                        st.dataframe(tabela_detalhada[colunas_exibir], use_container_width=True, hide_index=True,
                                     column_config={
                                         "Data_Formatada": st.column_config.TextColumn("Data"),
                                         "Dia_Semana_PT": st.column_config.TextColumn("Dia Semana"),
                                         "Quantidade": st.column_config.ProgressColumn(
                                             "Sinc. do Dia", format="%d", min_value=0,
                                             max_value=int(max(1, tabela_detalhada['Quantidade'].max()))),
                                         "Diferenca": st.column_config.NumberColumn("Δ vs Dia Anterior", format="%+d"),
                                         "Variacao_%": st.column_config.NumberColumn("Variação %", format="%+.1f%%"),
                                         "Media_Movel_7": st.column_config.NumberColumn("Média 7 dias", format="%.1f")
                                     })
                    st.markdown("### :material/calendar_view_day: Sincronizações por Dia")
                    sinc_por_dia = sincronizados_por_dia.copy()
                    sinc_por_dia['Media_Movel_7'] = sinc_por_dia['Quantidade'].rolling(7, min_periods=1).mean()
                    sinc_por_dia_recente = sinc_por_dia.tail(30).copy() if len(sinc_por_dia) > 30 else sinc_por_dia.copy()
                    sinc_por_dia_recente['Data_Formatada'] = sinc_por_dia_recente['Data'].dt.strftime('%d/%m')
                    fig_dias = go.Figure()
                    fig_dias.add_trace(go.Bar(
                        x=sinc_por_dia_recente['Data_Formatada'], y=sinc_por_dia_recente['Quantidade'],
                        name='Sincronizações', text=sinc_por_dia_recente['Quantidade'],
                        textposition='outside', cliponaxis=False,
                        marker_color=gradiente_azul(sinc_por_dia_recente['Quantidade']), marker_line_width=0,
                        customdata=sinc_por_dia_recente['Data'].dt.dayofweek.map(dict(enumerate(dias_semana_pt))),
                        hovertemplate='%{x} (%{customdata}): <b>%{y}</b> sinc.<extra></extra>'
                    ))
                    fig_dias.add_trace(go.Scatter(
                        x=sinc_por_dia_recente['Data_Formatada'], y=sinc_por_dia_recente['Media_Movel_7'],
                        name='Média móvel 7 dias', mode='lines', line=dict(color=COR_LARANJA, width=2.5, shape='spline'),
                        hovertemplate='Média 7d: %{y:.1f}<extra></extra>'
                    ))
                    fig_dias.update_layout(
                        title='Sincronizações por Dia (Período Recente)' if len(sinc_por_dia) > 30 else 'Sincronizações por Dia',
                        xaxis_title='Data (Dia/Mês)', yaxis_title='Quantidade de Sincronizações',
                        height=420, showlegend=True,
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                        margin=dict(t=70, b=50, l=50, r=30),
                        xaxis=dict(showgrid=False, tickangle=-45, type='category'),
                        yaxis=dict(rangemode='tozero'), bargap=0.2
                    )
                    st.plotly_chart(fig_dias, use_container_width=True)
                    col_dia1, col_dia2, col_dia3 = st.columns(3)
                    with col_dia1:
                        dia_max = sinc_por_dia.loc[sinc_por_dia['Quantidade'].idxmax()]
                        st.metric(":material/trending_up: Melhor Dia", dia_max['Data'].strftime('%d/%m/%Y'),
                                  f"{int(dia_max['Quantidade'])} sinc.", delta_color="off", **DELTA_SEM_SETA)
                    with col_dia2:
                        dia_min = base_min.loc[base_min['Quantidade'].idxmin()]
                        st.metric(":material/trending_down: Pior Dia", dia_min['Data'].strftime('%d/%m/%Y'),
                                  f"{int(dia_min['Quantidade'])} sinc.", delta_color="off", **DELTA_SEM_SETA,
                                  help="Considera só dias úteis")
                    with col_dia3:
                        st.metric(":material/functions: Média por Dia", f"{media_diaria:.1f}".replace('.', ','),
                                  help="Média por dia útil (dias sem sincronização contam como zero)")

                    # NOVO: calendário (estilo GitHub) — mostra dias zerados e semanas fracas de relance
                    st.markdown("### :material/calendar_month: Calendário de Sincronizações")
                    contagem_cal = df_sincronizados['Data'].value_counts()
                    fim_cal = contagem_cal.index.max()
                    ini_cal = max(contagem_cal.index.min(), fim_cal - timedelta(weeks=26))
                    dias_cal = pd.date_range(ini_cal - timedelta(days=ini_cal.dayofweek), fim_cal)
                    cal = pd.DataFrame({'Data': dias_cal, 'Qtd': contagem_cal.reindex(dias_cal, fill_value=0).values})
                    cal['Semana'] = cal['Data'] - pd.to_timedelta(cal['Data'].dt.dayofweek, unit='D')
                    cal['Dia'] = cal['Data'].dt.dayofweek
                    z_cal = cal.pivot(index='Dia', columns='Semana', values='Qtd').reindex(range(7))
                    txt_cal = cal.assign(T=cal['Data'].dt.strftime('%d/%m/%Y')).pivot(
                        index='Dia', columns='Semana', values='T').reindex(range(7))
                    fig_cal = go.Figure(go.Heatmap(
                        z=z_cal.values, x=z_cal.columns, y=['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
                        customdata=txt_cal.values, colorscale=[[0, '#F1F3F5'], [0.01, '#CFE8EC'],
                                                               [0.5, COR_AZUL_PETROLEO], [1, COR_AZUL_ESCURO]],
                        xgap=3, ygap=3, showscale=False,
                        hovertemplate='%{customdata}: <b>%{z}</b> sinc.<extra></extra>'))
                    fig_cal.update_layout(title='Últimas 26 semanas · cada quadrado é um dia', height=280,
                                          margin=dict(t=50, b=30, l=40, r=20))
                    fig_cal.update_yaxes(autorange='reversed', showgrid=False)
                    fig_cal.update_xaxes(tickformat='%b/%y', dtick='M1', showgrid=False)
                    st.plotly_chart(fig_cal, use_container_width=True, config={'displayModeBar': False})

                    # Agrupamento dos gráficos de evolução (Dia é o padrão, igual à versão anterior)
                    agrupamento = st.radio(":material/tune: Agrupar evolução por:", ["Dia", "Semana", "Mês"],
                                           horizontal=True, key="agrupamento_sinc",
                                           help="Semana/Mês deixam as linhas menos ruidosas em períodos longos")
                    freq_agrup = {'Dia': 'D', 'Semana': 'W-MON', 'Mês': 'MS'}[agrupamento]
                    fmt_agrup = {'Dia': '%d/%m', 'Semana': '%d/%m', 'Mês': '%b/%y'}[agrupamento]

                    def evolucao(coluna):
                        if agrupamento == 'Dia':
                            chave = pd.Grouper(key='Data', freq='D')
                        else:
                            chave = pd.Grouper(key='Data', freq=freq_agrup, label='left', closed='left')
                        piv = df_sincronizados.groupby([chave, coluna]).size().unstack(fill_value=0)
                        return piv

                    st.markdown("### :material/groups: Sincronizações por SRE")
                    if 'SRE' in df_sincronizados.columns:
                        pivot_sre = evolucao('SRE_Nome')
                        fig_sre = go.Figure()
                        for sre in pivot_sre.columns:
                            fig_sre.add_trace(go.Bar(
                                x=pivot_sre.index, y=pivot_sre[sre], name=sre,
                                hovertemplate='%{x|%d/%m/%Y}<br>' + sre + ': <b>%{y}</b><extra></extra>'
                            ))
                        fig_sre.update_layout(
                            title='Sincronizações por SRE (Stacked)', barmode='stack', height=420,
                            xaxis_title="Data", yaxis_title="Quantidade de Sincronizações",
                            xaxis=dict(tickformat=fmt_agrup, showgrid=False), bargap=0.15,
                            showlegend=True, hovermode='x unified',
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            margin=dict(t=70)
                        )
                        st.plotly_chart(fig_sre, use_container_width=True)
                    st.markdown("### :material/category: Sincronizações por Tipo de Chamado")
                    if 'Tipo_Chamado' in df_sincronizados.columns:
                        col_tipo1, col_tipo2 = st.columns([2, 1])
                        with col_tipo1:
                            pivot_tipo = evolucao('Tipo_Chamado')
                            fig_tipo = go.Figure()
                            top_tipos = df_sincronizados['Tipo_Chamado'].value_counts().head(5).index.tolist()
                            for tipo in top_tipos:
                                if tipo in pivot_tipo.columns:
                                    fig_tipo.add_trace(go.Scatter(
                                        x=pivot_tipo.index, y=pivot_tipo[tipo],
                                        mode='lines+markers', name=tipo, line=dict(width=2.5, shape='spline'),
                                        marker=dict(size=6),
                                        hovertemplate='%{x|%d/%m/%Y}<br>' + str(tipo) + ': <b>%{y}</b><extra></extra>'
                                    ))
                            fig_tipo.update_layout(
                                title='Evolução dos 5 Tipos Mais Frequentes', height=380,
                                xaxis_title="Data", yaxis_title="Quantidade",
                                xaxis=dict(tickformat=fmt_agrup, showgrid=False), yaxis=dict(rangemode='tozero'),
                                showlegend=True, legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0),
                                margin=dict(t=70)
                            )
                            st.plotly_chart(fig_tipo, use_container_width=True)
                        with col_tipo2:
                            tipo_dist = df_sincronizados['Tipo_Chamado'].value_counts().reset_index()
                            tipo_dist.columns = ['Tipo', 'Quantidade']
                            tipo_dist['Percentual'] = (tipo_dist['Quantidade'] / total_sincronizados * 100).round(1)
                            st.markdown("**:material/donut_small: Distribuição por Tipo:**")
                            for idx, row in tipo_dist.head(5).iterrows():
                                pct_txt = f"{row['Percentual']:.1f}".replace('.', ',')
                                st.markdown(f"""
                                <div style="padding: 10px 12px; margin-bottom: 8px; background: {COR_BRANCO};
                                            border: 1px solid {COR_CINZA_BORDA}; border-radius: 8px;">
                                    <div style="display:flex; justify-content:space-between; align-items:baseline;">
                                        <strong style="font-size:0.88rem;">{row['Tipo']}</strong>
                                        <span style="font-weight:700; color:{COR_AZUL_ESCURO};">{fmt_milhar(row['Quantidade'])}</span>
                                    </div>
                                    <div style="background:{COR_CINZA_FUNDO}; height:6px; border-radius:3px; margin-top:6px;">
                                        <div style="background:{COR_AZUL_PETROLEO}; width:{row['Percentual']}%; height:6px; border-radius:3px;"></div>
                                    </div>
                                    <small style="color:{COR_CINZA_TEXTO};">{pct_txt}% do total</small>
                                </div>
                                """, unsafe_allow_html=True)
                    st.markdown("### :material/apartment: Sincronizações por Empresa")
                    if 'Empresa' in df_sincronizados.columns:
                        col_empresa1, col_empresa2 = st.columns([2, 1])
                        with col_empresa1:
                            pivot_empresa = evolucao('Empresa')
                            fig_empresa = go.Figure()
                            top_empresas = df_sincronizados['Empresa'].value_counts().head(5).index.tolist()
                            for empresa in top_empresas:
                                if empresa in pivot_empresa.columns:
                                    fig_empresa.add_trace(go.Scatter(
                                        x=pivot_empresa.index, y=pivot_empresa[empresa],
                                        mode='lines', name=empresa, stackgroup='one', line=dict(width=1),
                                        hovertemplate='%{x|%d/%m/%Y}<br>' + empresa + ': <b>%{y}</b><extra></extra>'
                                    ))
                            fig_empresa.update_layout(
                                title='Sincronizações por Empresa (Top 5) - Gráfico de Área Empilhado',
                                height=380, xaxis_title="Data", yaxis_title="Quantidade",
                                xaxis=dict(tickformat=fmt_agrup, showgrid=False), hovermode='x unified',
                                showlegend=True, legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0),
                                margin=dict(t=70)
                            )
                            st.plotly_chart(fig_empresa, use_container_width=True)
                        with col_empresa2:
                            empresa_rank = df_sincronizados['Empresa'].value_counts().reset_index()
                            empresa_rank.columns = ['Empresa', 'Quantidade']
                            empresa_rank['Percentual'] = (empresa_rank['Quantidade'] / total_sincronizados * 100).round(1)
                            st.markdown("**:material/leaderboard: Ranking Empresas:**")
                            for idx, row in empresa_rank.head(5).iterrows():
                                cor_borda = list(CORES_PODIO.values())[idx] if idx < 3 else COR_CINZA_BORDA
                                pct_txt = f"{row['Percentual']:.1f}".replace('.', ',')
                                nome_emp = MAPEAMENTO_EMPRESAS.get(row['Empresa'], {}).get('nome_completo', '')
                                st.markdown(f"""
                                <div style="padding: 10px 12px; margin-bottom: 8px; background: {COR_BRANCO};
                                            border: 1px solid {COR_CINZA_BORDA}; border-left: 4px solid {cor_borda};
                                            border-radius: 8px; display:flex; align-items:center; gap:10px;">
                                    {selo_posicao(idx + 1, 26)}
                                    <div style="flex:1; line-height:1.25;">
                                        <strong>{row['Empresa']}</strong><br>
                                        <small style="color:{COR_CINZA_TEXTO};">{nome_emp}</small>
                                    </div>
                                    <div style="text-align:right; line-height:1.25;">
                                        <strong style="color:{COR_AZUL_ESCURO};">{fmt_milhar(row['Quantidade'])}</strong><br>
                                        <small style="color:{COR_CINZA_TEXTO};">{pct_txt}%</small>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    st.warning("Nenhum chamado sincronizado encontrado com os filtros aplicados.", icon=":material/warning:")
            else:
                st.info("Selecione filtros para visualizar os dados de sincronização por dia.", icon=":material/info:")
        with tab4:
            st.markdown(titulo_secao("PERFORMANCE DOS SREs", "premio"), unsafe_allow_html=True)
            if 'SRE' in df.columns and 'Status' in df.columns and 'Revisões_Total' in df.columns:
                col_filtro1, col_filtro2 = st.columns(2)
                ano_sre, mes_sre = 'Todos', 'Todos'
                with col_filtro1:
                    if 'Ano' in df.columns:
                        anos_sre = sorted(df['Ano'].dropna().unique().astype(int))
                        anos_opcoes_sre = ['Todos'] + list(anos_sre)
                        ano_sre = st.selectbox(":material/calendar_month: Filtrar por Ano:", options=anos_opcoes_sre, key="filtro_ano_sre")
                with col_filtro2:
                    if 'Mês' in df.columns:
                        meses_sre = sorted(df['Mês'].dropna().unique().astype(int))
                        meses_opcoes_sre = ['Todos'] + [str(m) for m in meses_sre]
                        mes_sre = st.selectbox(":material/date_range: Filtrar por Mês:", options=meses_opcoes_sre, key="filtro_mes_sre",
                                               format_func=lambda m: m if m == 'Todos' else MESES_NOMES[int(m)])
                df_sre = df.copy()
                if 'Ano' in df_sre.columns and ano_sre != 'Todos':
                    df_sre = df_sre[df_sre['Ano'] == int(ano_sre)]
                if 'Mês' in df_sre.columns and mes_sre != 'Todos':
                    df_sre = df_sre[df_sre['Mês'] == int(mes_sre)]
                df_sincronizados = df_sre[df_sre['Sinc']].copy()
                if not df_sincronizados.empty and 'SRE' in df_sincronizados.columns:
                    st.markdown("### :material/bar_chart: Sincronizados por SRE")
                    sinc_por_sre_nome = (df_sincronizados.groupby('SRE_Nome').size()
                                         .reset_index(name='Sincronizados')
                                         .sort_values('Sincronizados', ascending=False))
                    total_sinc_sre = sinc_por_sre_nome['Sincronizados'].sum()
                    top_sre = sinc_por_sre_nome.head(15)
                    fig_sinc_bar = go.Figure()
                    fig_sinc_bar.add_trace(go.Bar(
                        x=top_sre['SRE_Nome'], y=top_sre['Sincronizados'],
                        name='Sincronizados',
                        text=[f"<b>{fmt_milhar(v)}</b>  ·  " + f"{v / total_sinc_sre * 100:.1f}%".replace('.', ',')
                              for v in top_sre['Sincronizados']],
                        textposition='outside', cliponaxis=False,
                        marker_color=gradiente_azul(top_sre['Sincronizados']), marker_line_width=0,
                        hovertemplate='<b>%{x}</b><br>%{y} sincronizados<extra></extra>'
                    ))
                    titulo_grafico = 'Sincronizados por SRE'
                    if ano_sre != 'Todos' or mes_sre != 'Todos':
                        titulo_grafico += ' - Filtrado'
                        if ano_sre != 'Todos':
                            titulo_grafico += f' ({ano_sre}'
                        if mes_sre != 'Todos':
                            if ano_sre != 'Todos':
                                titulo_grafico += f' - {MESES_NOMES[int(mes_sre)]})'
                            else:
                                titulo_grafico += f' ({MESES_NOMES[int(mes_sre)]})'
                        elif ano_sre != 'Todos':
                            titulo_grafico += ')'
                    fig_sinc_bar.update_layout(
                        title=titulo_grafico, xaxis_title='SRE', yaxis_title='Número de Sincronizados',
                        height=460, showlegend=False, bargap=0.35,
                        margin=dict(t=60, b=60, l=50, r=30),
                        xaxis=dict(showgrid=False, categoryorder='total descending'),
                        yaxis=dict(rangemode='tozero')
                    )
                    st.plotly_chart(fig_sinc_bar, use_container_width=True)
                    col_top1, col_top2, col_top3 = st.columns(3)
                    for posicao, coluna in enumerate([col_top1, col_top2, col_top3]):
                        if len(sinc_por_sre_nome) > posicao:
                            linha_sre = sinc_por_sre_nome.iloc[posicao]
                            pct_sre = f"{linha_sre['Sincronizados'] / total_sinc_sre * 100:.1f}".replace('.', ',')
                            with coluna:
                                st.markdown(f"""
                                <div class="metric-card" style="border-top: 4px solid {CORES_PODIO[posicao + 1]};">
                                    <div style="display:flex; align-items:center; gap:12px;">
                                        {selo_posicao(posicao + 1, 40)}
                                        <div>
                                            <div class="metric-label" style="margin:0;">{posicao + 1}º Lugar Sincronizados</div>
                                            <div style="font-size:1.25rem; font-weight:700; color:{COR_PRETO_SUAVE};">{linha_sre['SRE_Nome']}</div>
                                            <div style="font-size:0.85rem; color:{COR_AZUL_ESCURO}; font-weight:600;">
                                                {fmt_milhar(linha_sre['Sincronizados'])} sinc. · {pct_sre}% do total</div>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    st.markdown("### :material/table_chart: Performance Detalhada dos SREs")
                    df_sres_metrics = (df_sre.groupby('SRE_Nome')
                                       .agg(Total_Cards=('Sinc', 'size'), Sincronizados=('Sinc', 'sum'),
                                            Cards_Retorno=('Com_Revisao', 'sum'), Revisoes=('Revisões_Total', 'sum'))
                                       .reset_index().rename(columns={'SRE_Nome': 'SRE'}))
                    df_sres_metrics['Taxa_Retorno'] = (df_sres_metrics['Cards_Retorno'] /
                                                       df_sres_metrics['Total_Cards'] * 100).round(1)
                    df_sres_metrics['Participacao'] = (df_sres_metrics['Sincronizados'] /
                                                       max(df_sres_metrics['Sincronizados'].sum(), 1) * 100).round(1)
                    df_sres_metrics = df_sres_metrics.sort_values('Sincronizados', ascending=False)
                    st.dataframe(df_sres_metrics, use_container_width=True, hide_index=True,
                                 column_config={
                                     "SRE": st.column_config.TextColumn("SRE"),
                                     "Total_Cards": st.column_config.NumberColumn("Total Cards", format="%d"),
                                     "Sincronizados": st.column_config.NumberColumn("Sincronizados", format="%d"),
                                     "Cards_Retorno": st.column_config.NumberColumn("Cards Retorno", format="%d",
                                                                                    help="Cards com Revisões + Qtd. Revisões > 0"),
                                     "Revisoes": st.column_config.NumberColumn("Total Revisões", format="%d",
                                                                               help="Soma de Revisões + Qtd. Revisões"),
                                     "Taxa_Retorno": st.column_config.ProgressColumn("Taxa Retorno", format="%.1f%%",
                                                                                     min_value=0, max_value=100),
                                     "Participacao": st.column_config.ProgressColumn("Participação", format="%.1f%%",
                                                                                     min_value=0, max_value=100),
                                 })
                st.markdown("---")
                st.markdown(titulo_secao("ANÁLISE DE SAZONALIDADE", "calendario"), unsafe_allow_html=True)
                with st.expander("**SOBRE ESTA ANÁLISE**", expanded=False, icon=":material/info:"):
                    st.markdown("""
                    **Análise de Sazonalidade e Padrões Temporais:**
                    Esta análise identifica padrões no fluxo de demandas ao longo do tempo:
                    **:material/calendar_view_week: Padrões por Dia da Semana:**
                    - Identifica quais dias têm mais/menos demandas
                    - Mostra taxa de sincronização por dia
                    - Útil para planejamento de recursos
                    **:material/schedule: Demandas por Hora do Dia:**
                    - Identifica horários de pico de criação de chamados
                    - Mostra horários com maior taxa de sincronização
                    - Filtros por ano e mês disponíveis
                    **:material/calendar_month: Sazonalidade Mensal:**
                    - Distribuição de demandas ao longo dos meses
                    - Identifica meses com maior volume
                    - Mostra taxa de sincronização mensal
                    - Inclui todos os 12 meses (Janeiro a Dezembro)
                    **:material/bar_chart: Tipos de Gráficos:**
                    - Gráficos de barras para comparação
                    - Gráficos de linha para tendências
                    - Taxas de sincronização sobrepostas
                    - Mapa de calor dia da semana × hora
                    **:material/target: Objetivo:**
                    Otimizar alocação de recursos e identificar padrões para melhorar eficiência.
                    """)
                if 'Criado' in df.columns and 'Status' in df.columns:
                    col_saz_filtro1, col_saz_filtro2, col_saz_filtro3 = st.columns(3)
                    with col_saz_filtro1:
                        anos_saz = sorted(df['Ano'].dropna().unique().astype(int))
                        anos_opcoes_saz = ['Todos os Anos'] + list(anos_saz)
                        ano_saz = st.selectbox(":material/calendar_month: Selecionar Ano:", options=anos_opcoes_saz,
                                               index=len(anos_opcoes_saz)-1, key="ano_saz")
                    with col_saz_filtro2:
                        if ano_saz != 'Todos os Anos':
                            meses_ano = df[df['Ano'] == int(ano_saz)]['Mês'].unique()
                            meses_opcoes = ['Todos os Meses'] + sorted([str(int(m)) for m in meses_ano])
                            mes_saz = st.selectbox(":material/date_range: Selecionar Mês:", options=meses_opcoes, key="mes_saz",
                                                   format_func=lambda m: m if m == 'Todos os Meses' else MESES_NOMES[int(m)])
                        else:
                            mes_saz = 'Todos os Meses'
                    with col_saz_filtro3:
                        # Corrigido: este seletor não alterava nada nos gráficos. Agora controla as séries exibidas.
                        tipo_analise = st.selectbox(":material/stacked_bar_chart: Tipo de Análise:",
                                                    options=["Demandas Totais", "Apenas Sincronizados", "Comparativo"],
                                                    index=2, key="tipo_analise_saz")
                    mostrar_total = tipo_analise in ("Demandas Totais", "Comparativo")
                    mostrar_sinc = tipo_analise in ("Apenas Sincronizados", "Comparativo")
                    mostrar_taxa = tipo_analise == "Comparativo"
                    df_saz = df.copy()
                    if ano_saz != 'Todos os Anos':
                        df_saz = df_saz[df_saz['Ano'] == int(ano_saz)]
                    if mes_saz != 'Todos os Meses':
                        df_saz = df_saz[df_saz['Mês'] == int(mes_saz)]
                    st.markdown("### :material/calendar_view_week: Padrões por Dia da Semana")
                    dias_semana = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    dias_portugues = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                    dia_mapping = dict(zip(dias_semana, dias_portugues))
                    df_saz['Dia_Semana'] = df_saz['Criado'].dt.day_name()
                    df_saz['Dia_Semana_PT'] = df_saz['Dia_Semana'].map(dia_mapping)
                    col_dia1, col_dia2 = st.columns(2)
                    with col_dia1:
                        demanda_dia = df_saz['Dia_Semana_PT'].value_counts().reindex(dias_portugues).reset_index()
                        demanda_dia.columns = ['Dia', 'Total_Demandas']
                        sinc_dia = df_saz[df_saz['Status'] == 'Sincronizado']['Dia_Semana_PT'].value_counts().reindex(dias_portugues).reset_index()
                        sinc_dia.columns = ['Dia', 'Sincronizados']
                        dados_dia = pd.merge(demanda_dia, sinc_dia, on='Dia', how='left').fillna(0)
                        dados_dia['Taxa_Sinc'] = (dados_dia['Sincronizados'] / dados_dia['Total_Demandas'] * 100).round(1)
                        fig_dias = go.Figure()
                        if mostrar_total:
                            fig_dias.add_trace(go.Bar(x=dados_dia['Dia'], y=dados_dia['Total_Demandas'],
                                                      name='Total Demandas', marker_color=COR_AZUL_ESCURO,
                                                      text=dados_dia['Total_Demandas'].astype(int), textposition='outside',
                                                      cliponaxis=False))
                        if mostrar_sinc:
                            fig_dias.add_trace(go.Bar(x=dados_dia['Dia'], y=dados_dia['Sincronizados'],
                                                      name='Sincronizados', marker_color=COR_VERDE_ESCURO,
                                                      text=dados_dia['Sincronizados'].astype(int), textposition='outside',
                                                      cliponaxis=False))
                        if mostrar_taxa:
                            fig_dias.add_trace(go.Scatter(x=dados_dia['Dia'], y=dados_dia['Taxa_Sinc'],
                                                          name='Taxa Sinc (%)', yaxis='y2',
                                                          mode='lines+markers',
                                                          line=dict(color=COR_LARANJA, width=3, shape='spline'),
                                                          marker=dict(size=9, line=dict(color=COR_BRANCO, width=2)),
                                                          hovertemplate='%{x}: %{y:.1f}%<extra>Taxa Sinc</extra>'))
                        fig_dias.update_layout(
                            title='Demandas e Sincronizações por Dia da Semana', barmode='group', bargap=0.25,
                            yaxis=dict(title='Quantidade', range=[0, max(1, dados_dia['Total_Demandas'].max()) * 1.35]),
                            yaxis2=dict(title='Taxa Sinc (%)', overlaying='y', side='right', range=[0, 105],
                                        ticksuffix='%', showgrid=False),
                            xaxis=dict(showgrid=False),
                            height=420, showlegend=True, hovermode='x unified',
                            legend=dict(orientation='h', yanchor='top', y=-0.12, x=0),
                            margin=dict(t=60, b=70)
                        )
                        st.plotly_chart(fig_dias, use_container_width=True)
                    with col_dia2:
                        st.markdown("### :material/schedule: Demandas por Hora do Dia")
                        col_hora_filtro1, col_hora_filtro2 = st.columns(2)
                        with col_hora_filtro1:
                            anos_hora = sorted(df['Ano'].dropna().unique().astype(int))
                            anos_opcoes_hora = ['Todos os Anos'] + list(anos_hora)
                            ano_hora = st.selectbox("Ano para análise horária:", options=anos_opcoes_hora,
                                                    index=len(anos_opcoes_hora)-1, key="ano_hora")
                        with col_hora_filtro2:
                            if ano_hora != 'Todos os Anos':
                                meses_hora = df[df['Ano'] == int(ano_hora)]['Mês'].unique()
                                meses_opcoes_hora = ['Todos os Meses'] + sorted([str(int(m)) for m in meses_hora])
                                mes_hora = st.selectbox("Mês para análise horária:", options=meses_opcoes_hora, key="mes_hora",
                                                        format_func=lambda m: m if m == 'Todos os Meses' else MESES_NOMES[int(m)])
                            else:
                                mes_hora = 'Todos os Meses'
                        df_hora = df.copy()
                        if ano_hora != 'Todos os Anos':
                            df_hora = df_hora[df_hora['Ano'] == int(ano_hora)]
                        if mes_hora != 'Todos os Meses':
                            df_hora = df_hora[df_hora['Mês'] == int(mes_hora)]
                        subtitulo_hora = "Análise por Hora"
                        if ano_hora != 'Todos os Anos':
                            subtitulo_hora += f" - {ano_hora}"
                        if mes_hora != 'Todos os Meses':
                            subtitulo_hora += f" - {MESES_NOMES[int(mes_hora)]}"
                        st.markdown(f"**Período:** {subtitulo_hora}")
                        df_hora['Hora'] = df_hora['Criado'].dt.hour
                        demanda_hora = df_hora['Hora'].value_counts().sort_index().reset_index()
                        demanda_hora.columns = ['Hora', 'Total_Demandas']
                        sinc_hora = df_hora[df_hora['Status'] == 'Sincronizado']['Hora'].value_counts().sort_index().reset_index()
                        sinc_hora.columns = ['Hora', 'Sincronizados']
                        dados_hora = pd.merge(demanda_hora, sinc_hora, on='Hora', how='left').fillna(0)
                        dados_hora['Taxa_Sinc'] = (dados_hora['Sincronizados'] / dados_hora['Total_Demandas'] * 100).where(dados_hora['Total_Demandas'] > 0, 0).round(1)
                        fig_horas = go.Figure()
                        fig_horas.add_trace(go.Scatter(x=dados_hora['Hora'], y=dados_hora['Total_Demandas'],
                                                       name='Total Demandas', mode='lines+markers',
                                                       line=dict(color=COR_AZUL_ESCURO, width=3, shape='spline'),
                                                       fill='tozeroy', fillcolor='rgba(0, 89, 115, 0.08)',
                                                       marker=dict(size=8, line=dict(color=COR_BRANCO, width=2)),
                                                       hovertemplate='%{x}h: %{y} demandas<extra></extra>'))
                        fig_horas.add_trace(go.Scatter(x=dados_hora['Hora'], y=dados_hora['Sincronizados'],
                                                       name='Sincronizados', mode='lines+markers',
                                                       line=dict(color=COR_VERDE_ESCURO, width=3, shape='spline'),
                                                       marker=dict(size=8, line=dict(color=COR_BRANCO, width=2)),
                                                       hovertemplate='%{x}h: %{y} sincronizados<extra></extra>'))
                        if not dados_hora.empty:
                            pico_demanda = dados_hora.loc[dados_hora['Total_Demandas'].idxmax()]
                            pico_sinc = dados_hora.loc[dados_hora['Sincronizados'].idxmax()]
                            hora_pico_demanda = f"{int(pico_demanda['Hora'])}:00h"
                            hora_pico_sinc = f"{int(pico_sinc['Hora'])}:00h"
                            fig_horas.add_annotation(x=pico_demanda['Hora'], y=pico_demanda['Total_Demandas'],
                                                     text=f"Pico Demandas: {int(pico_demanda['Total_Demandas'])}<br>{hora_pico_demanda}",
                                                     showarrow=True, arrowhead=2, ax=0, ay=-40, arrowcolor=COR_AZUL_ESCURO,
                                                     bgcolor="white", bordercolor=COR_AZUL_ESCURO, borderpad=4,
                                                     font=dict(size=11, color=COR_AZUL_ESCURO))
                            fig_horas.add_annotation(x=pico_sinc['Hora'], y=pico_sinc['Sincronizados'],
                                                     text=f"Pico Sinc: {int(pico_sinc['Sincronizados'])}<br>{hora_pico_sinc}",
                                                     showarrow=True, arrowhead=2, ax=0, ay=40, arrowcolor=COR_VERDE_ESCURO,
                                                     bgcolor="white", bordercolor=COR_VERDE_ESCURO, borderpad=4,
                                                     font=dict(size=11, color=COR_VERDE_ESCURO))
                        fig_horas.update_layout(
                            title=f'Demandas por Hora do Dia - {subtitulo_hora}',
                            xaxis_title='Hora do Dia', yaxis_title='Quantidade',
                            xaxis=dict(dtick=1, ticksuffix='h', showgrid=False), yaxis=dict(rangemode='tozero'),
                            height=420, showlegend=True,
                            legend=dict(orientation='h', yanchor='top', y=-0.15, x=0),
                            margin=dict(t=60, b=80)
                        )
                        st.plotly_chart(fig_horas, use_container_width=True)
                        if not dados_hora.empty:
                            col_hora_stats1, col_hora_stats2, col_hora_stats3 = st.columns(3)
                            with col_hora_stats1:
                                hora_pico_demanda = dados_hora.loc[dados_hora['Total_Demandas'].idxmax()]
                                hora_formatada = f"{int(hora_pico_demanda['Hora'])}:00h"
                                st.metric(":material/schedule: Pico de Demandas", hora_formatada,
                                          f"{int(hora_pico_demanda['Total_Demandas'])} demandas")
                            with col_hora_stats2:
                                HORARIOS_SINCRONISMO = [8, 9, 10, 11, 12, 14, 15, 16]
                                dados_sinc_pico = dados_hora[dados_hora['Hora'].isin(HORARIOS_SINCRONISMO)].copy()
                                if not dados_sinc_pico.empty:
                                    hora_pico_sinc = dados_sinc_pico.loc[dados_sinc_pico['Sincronizados'].idxmax()]
                                    hora_sinc_formatada = f"{int(hora_pico_sinc['Hora'])}:00h"
                                    st.metric(":material/task_alt: Pico de Sincronizações", hora_sinc_formatada,
                                              f"{int(hora_pico_sinc['Sincronizados'])} sinc.")
                                else:
                                    hora_pico_sinc = dados_hora.loc[dados_hora['Sincronizados'].idxmax()]
                                    hora_sinc_formatada = f"{int(hora_pico_sinc['Hora'])}:00h"
                                    st.metric(":material/task_alt: Pico de Sincronizações", hora_sinc_formatada,
                                              f"{int(hora_pico_sinc['Sincronizados'])} sinc.",
                                              help="Pico calculado fora dos horários de sincronismo")
                            with col_hora_stats3:
                                HORARIOS_SINCRONISMO = [8, 9, 10, 11, 12, 14, 15, 16]
                                MINIMO_CHAMADOS = 2
                                dados_hora_validos = dados_hora[
                                    dados_hora['Hora'].isin(HORARIOS_SINCRONISMO) &
                                    (dados_hora['Total_Demandas'] >= MINIMO_CHAMADOS)
                                ]
                                if not dados_hora_validos.empty:
                                    melhor_taxa_hora = dados_hora_validos.loc[dados_hora_validos['Taxa_Sinc'].idxmax()]
                                    hora_taxa_formatada = f"{int(melhor_taxa_hora['Hora'])}:00h"
                                    st.metric(":material/emoji_events: Melhor Taxa Sinc.", hora_taxa_formatada,
                                              f"{melhor_taxa_hora['Taxa_Sinc']:.1f}%")
                                else:
                                    dados_fallback = dados_hora[dados_hora['Hora'].isin(HORARIOS_SINCRONISMO)]
                                    if not dados_fallback.empty:
                                        melhor_taxa_hora = dados_fallback.loc[dados_fallback['Taxa_Sinc'].idxmax()]
                                        hora_taxa_formatada = f"{int(melhor_taxa_hora['Hora'])}:00h"
                                        st.metric(":material/emoji_events: Melhor Taxa Sinc.", hora_taxa_formatada,
                                                  f"{melhor_taxa_hora['Taxa_Sinc']:.1f}%",
                                                  help="Taxa calculada com volume baixo de dados")
                                    else:
                                        st.metric(":material/emoji_events: Melhor Taxa Sinc.", "N/A",
                                                  "Sem dados nos horários 8-12,14-16h")
                    # NOVO: mapa de calor dia da semana × hora (respeita os filtros de ano/mês acima)
                    st.markdown("### :material/grid_on: Mapa de Calor · Dia da Semana × Hora")
                    if not df_saz.empty:
                        base_calor = df_saz[df_saz['Sinc']] if tipo_analise == "Apenas Sincronizados" else df_saz
                        mapa_calor = (base_calor.assign(DiaN=base_calor['Criado'].dt.dayofweek,
                                                        HoraN=base_calor['Criado'].dt.hour)
                                      .pivot_table(index='DiaN', columns='HoraN', values='Criado',
                                                   aggfunc='count', fill_value=0)
                                      .reindex(index=range(7), fill_value=0))
                        mapa_calor = mapa_calor.loc[mapa_calor.sum(axis=1) > 0]
                        if not mapa_calor.empty:
                            fig_calor = go.Figure(go.Heatmap(
                                z=mapa_calor.values, x=[f"{h}h" for h in mapa_calor.columns],
                                y=[dias_portugues[i] for i in mapa_calor.index],
                                colorscale=[[0, '#F1F8FA'], [0.35, '#8CCAD5'], [0.7, COR_AZUL_PETROLEO], [1, COR_AZUL_ESCURO]],
                                xgap=2, ygap=2, text=mapa_calor.values, texttemplate='%{text}',
                                textfont=dict(size=10),
                                colorbar=dict(title='Qtd', thickness=12),
                                hovertemplate='%{y}, %{x}: <b>%{z}</b><extra></extra>'))
                            fig_calor.update_layout(
                                title=('Sincronizados' if tipo_analise == "Apenas Sincronizados" else 'Demandas criadas')
                                      + ' por dia da semana e hora', height=340, margin=dict(t=50, b=40))
                            fig_calor.update_yaxes(autorange='reversed', showgrid=False)
                            fig_calor.update_xaxes(showgrid=False)
                            st.plotly_chart(fig_calor, use_container_width=True)
                    st.markdown("### :material/calendar_month: Sazonalidade Mensal")
                    col_saz_mes1, col_saz_mes2 = st.columns(2)
                    with col_saz_mes1:
                        anos_saz_mes = sorted(df['Ano'].dropna().unique().astype(int))
                        anos_opcoes_saz_mes = ['Todos os Anos'] + list(anos_saz_mes)
                        ano_saz_mes = st.selectbox(":material/calendar_month: Selecionar Ano para análise mensal:",
                                                   options=anos_opcoes_saz_mes,
                                                   index=len(anos_opcoes_saz_mes)-1, key="ano_saz_mes")
                    with col_saz_mes2:
                        if ano_saz_mes != 'Todos os Anos':
                            st.markdown(f"**Ano selecionado:** {ano_saz_mes}")
                        else:
                            st.markdown("**Todos os anos**")
                    if ano_saz_mes != 'Todos os Anos':
                        df_saz_mes = df[df['Ano'] == int(ano_saz_mes)].copy()
                    else:
                        df_saz_mes = df.copy()
                    if not df_saz_mes.empty:
                        meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                        meses_nomes_completos = {
                            'Jan': 'Janeiro', 'Fev': 'Fevereiro', 'Mar': 'Março', 'Abr': 'Abril',
                            'Mai': 'Maio', 'Jun': 'Junho', 'Jul': 'Julho', 'Ago': 'Agosto',
                            'Set': 'Setembro', 'Out': 'Outubro', 'Nov': 'Novembro', 'Dez': 'Dezembro'
                        }
                        if 'Nome_Mês' in df_saz_mes.columns:
                            df_saz_mes['Mês_Abrev'] = df_saz_mes['Nome_Mês']
                        else:
                            df_saz_mes['Mês_Abrev'] = df_saz_mes['Criado'].dt.month.map({
                                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
                                5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
                                9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
                            })
                        demanda_mes = df_saz_mes.groupby('Mês_Abrev').size().reset_index()
                        demanda_mes.columns = ['Mês', 'Total']
                        demanda_mes = demanda_mes.set_index('Mês').reindex(meses_ordem).reset_index()
                        demanda_mes['Total'] = demanda_mes['Total'].fillna(0).astype(int)
                        sinc_mes = df_saz_mes[df_saz_mes['Status'] == 'Sincronizado'].groupby('Mês_Abrev').size().reset_index()
                        sinc_mes.columns = ['Mês', 'Sincronizados']
                        sinc_mes = sinc_mes.set_index('Mês').reindex(meses_ordem).reset_index()
                        sinc_mes['Sincronizados'] = sinc_mes['Sincronizados'].fillna(0).astype(int)
                        dados_mes = pd.merge(demanda_mes, sinc_mes, on='Mês', how='left').fillna(0)
                        dados_mes['Taxa_Sinc'] = (dados_mes['Sincronizados'] / dados_mes['Total'] * 100).where(dados_mes['Total'] > 0, 0).round(1)
                        titulo_grafico = f'Distribuição Mensal'
                        if ano_saz_mes != 'Todos os Anos':
                            titulo_grafico += f' - {ano_saz_mes}'
                        fig_mes_saz = go.Figure()
                        if mostrar_total:
                            fig_mes_saz.add_trace(go.Bar(x=dados_mes['Mês'], y=dados_mes['Total'],
                                                         name='Total Demandas', marker_color=COR_AZUL_ESCURO,
                                                         text=dados_mes['Total'], textposition='outside', cliponaxis=False))
                        if mostrar_sinc:
                            fig_mes_saz.add_trace(go.Bar(x=dados_mes['Mês'], y=dados_mes['Sincronizados'],
                                                         name='Sincronizados', marker_color=COR_VERDE_ESCURO,
                                                         text=dados_mes['Sincronizados'], textposition='outside',
                                                         cliponaxis=False))
                        if mostrar_taxa:
                            dados_taxa = dados_mes[dados_mes['Total'] > 0]  # não desenha 0% em meses sem dados
                            fig_mes_saz.add_trace(go.Scatter(x=dados_taxa['Mês'], y=dados_taxa['Taxa_Sinc'],
                                                             name='Taxa Sinc (%)', yaxis='y2',
                                                             mode='lines+markers',
                                                             line=dict(color=COR_LARANJA, width=3, shape='spline'),
                                                             marker=dict(size=9, line=dict(color=COR_BRANCO, width=2)),
                                                             hovertemplate='%{x}: %{y:.1f}%<extra>Taxa Sinc</extra>'))
                        fig_mes_saz.update_layout(
                            title=titulo_grafico, barmode='group', bargap=0.25,
                            yaxis=dict(title='Quantidade', range=[0, max(1, dados_mes['Total'].max()) * 1.35]),
                            yaxis2=dict(title='Taxa Sinc (%)', overlaying='y', side='right', range=[0, 105],
                                        ticksuffix='%', showgrid=False),
                            xaxis=dict(showgrid=False, categoryorder='array', categoryarray=meses_ordem),
                            height=420, showlegend=True, hovermode='x unified',
                            legend=dict(orientation='h', yanchor='top', y=-0.12, x=0),
                            margin=dict(t=60, b=70)
                        )
                        st.plotly_chart(fig_mes_saz, use_container_width=True)
                        col_pico1, col_pico2, col_pico3 = st.columns(3)
                        with col_pico1:
                            mes_maior_demanda = dados_mes.loc[dados_mes['Total'].idxmax()]
                            st.metric(":material/trending_up: Mês com mais demandas",
                                      f"{meses_nomes_completos.get(mes_maior_demanda['Mês'], mes_maior_demanda['Mês'])}: {int(mes_maior_demanda['Total'])}")
                        with col_pico2:
                            mes_maior_sinc = dados_mes.loc[dados_mes['Sincronizados'].idxmax()]
                            st.metric(":material/task_alt: Mês com mais sincronizações",
                                      f"{meses_nomes_completos.get(mes_maior_sinc['Mês'], mes_maior_sinc['Mês'])}: {int(mes_maior_sinc['Sincronizados'])}")
                        with col_pico3:
                            melhor_taxa = dados_mes.loc[dados_mes['Taxa_Sinc'].idxmax()]
                            st.metric(":material/emoji_events: Melhor taxa de sincronização",
                                      f"{meses_nomes_completos.get(melhor_taxa['Mês'], melhor_taxa['Mês'])}: " + f"{melhor_taxa['Taxa_Sinc']:.1f}%".replace('.', ','))
                st.markdown("---")
                col_top, col_dist = st.columns([2, 1])
                with col_top:
                    st.markdown(titulo_secao("TOP 10 RESPONSÁVEIS", "equipe"), unsafe_allow_html=True)
                    if 'Responsável_Formatado' in df.columns:
                        top_responsaveis = df['Responsável_Formatado'].value_counts().head(10).reset_index()
                        top_responsaveis.columns = ['Responsável', 'Demandas']
                        fig_top = px.bar(top_responsaveis, x='Demandas', y='Responsável',
                                         orientation='h', text='Demandas', color='Demandas',
                                         color_continuous_scale=ESCALA_AZUL)
                        fig_top.update_traces(texttemplate='%{text}', textposition='outside', cliponaxis=False,
                                              marker_line_width=0,
                                              hovertemplate='<b>%{y}</b><br>%{x} demandas<extra></extra>')
                        fig_top.update_layout(height=500, showlegend=False, coloraxis_showscale=False, bargap=0.3,
                                              yaxis={'categoryorder': 'total ascending'},
                                              margin=dict(t=20, b=20, l=20, r=20),
                                              xaxis_title="Número de Demandas", yaxis_title="")
                        st.plotly_chart(fig_top, use_container_width=True)
                with col_dist:
                    st.markdown(titulo_secao("DISTRIBUIÇÃO POR TIPO", "grafico"), unsafe_allow_html=True)
                    if 'Tipo_Chamado' in df.columns:
                        tipos_chamado = df['Tipo_Chamado'].value_counts().reset_index()
                        tipos_chamado.columns = ['Tipo', 'Quantidade']
                        tipos_chamado = tipos_chamado.sort_values('Quantidade', ascending=True)
                        fig_tipos = px.bar(tipos_chamado, x='Quantidade', y='Tipo',
                                           orientation='h', title='', text='Quantidade',
                                           color='Quantidade', color_continuous_scale=ESCALA_AZUL)
                        fig_tipos.update_traces(texttemplate='%{text}', textposition='outside', cliponaxis=False,
                                                marker_line_width=0,
                                                hovertemplate='<b>%{y}</b><br>%{x} chamados<extra></extra>')
                        fig_tipos.update_layout(height=500, showlegend=False, coloraxis_showscale=False, bargap=0.3,
                                                yaxis={'categoryorder': 'total ascending'},
                                                margin=dict(t=20, b=20, l=20, r=20),
                                                xaxis_title="Quantidade", yaxis_title="")
                        st.plotly_chart(fig_tipos, use_container_width=True)
                st.markdown("---")
                st.markdown(titulo_secao("ÚLTIMAS DEMANDAS REGISTRADAS", "relogio"), unsafe_allow_html=True)
                if 'Criado' in df.columns:
                    filtro_chamado_principal = st.text_input(":material/search: Buscar chamado específico:",
                                                             placeholder="Digite o número do chamado...",
                                                             key="filtro_chamado_principal")
                    col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
                    with col_filtro1:
                        qtd_demandas = st.slider("Número de demandas:", min_value=5, max_value=50,
                                                 value=15, step=5, key="slider_demandas")
                    with col_filtro2:
                        ordenar_por = st.selectbox("Ordenar por:",
                                                   options=['Data (Mais Recente)', 'Data (Mais Antiga)',
                                                            'Revisões (Maior)', 'Revisões (Menor)'],
                                                   key="select_ordenar")
                    with col_filtro3:
                        mostrar_colunas = st.multiselect("Colunas a mostrar:",
                                                         options=['Chamado', 'Tipo_Chamado', 'Responsável', 'Status',
                                                                  'Prioridade', 'Revisões', 'Revisões_Total',
                                                                  'Qtd. Revisões', 'Empresa', 'SRE', 'Data',
                                                                  'Responsável_Formatado'],
                                                         default=['Chamado', 'Tipo_Chamado', 'Responsável_Formatado',
                                                                  'Status', 'Data'],
                                                         key="select_colunas")
                    with col_filtro4:
                        filtro_chamado_tabela = st.text_input("Filtro adicional:",
                                                              placeholder="Ex: 12345",
                                                              key="input_filtro_chamado")
                    ultimas_demandas = df.copy()
                    if filtro_chamado_principal:
                        ultimas_demandas = ultimas_demandas[
                            ultimas_demandas['Chamado'].astype(str).str.contains(filtro_chamado_principal, na=False)
                        ]
                    if ordenar_por == 'Data (Mais Recente)':
                        ultimas_demandas = ultimas_demandas.sort_values('Criado', ascending=False)
                    elif ordenar_por == 'Data (Mais Antiga)':
                        ultimas_demandas = ultimas_demandas.sort_values('Criado', ascending=True)
                    elif ordenar_por == 'Revisões (Maior)':
                        ultimas_demandas = ultimas_demandas.sort_values('Revisões_Total', ascending=False)
                    elif ordenar_por == 'Revisões (Menor)':
                        ultimas_demandas = ultimas_demandas.sort_values('Revisões_Total', ascending=True)
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
                    if 'Qtd. Revisões' in mostrar_colunas and 'Qtd. Revisões' in ultimas_demandas.columns:
                        display_data['Qtd. Revisões'] = ultimas_demandas['Qtd. Revisões']
                    if 'Revisões_Total' in mostrar_colunas and 'Revisões_Total' in ultimas_demandas.columns:
                        display_data['Revisões_Total'] = ultimas_demandas['Revisões_Total']
                    if 'Empresa' in mostrar_colunas and 'Empresa' in ultimas_demandas.columns:
                        display_data['Empresa'] = ultimas_demandas['Empresa']
                    if 'SRE' in mostrar_colunas and 'SRE' in ultimas_demandas.columns:
                        display_data['SRE'] = ultimas_demandas['SRE']
                    if 'Data' in mostrar_colunas and 'Criado' in ultimas_demandas.columns:
                        display_data['Data Criação'] = ultimas_demandas['Criado'].dt.strftime('%d/%m/%Y %H:%M')
                    if not display_data.empty:
                        st.dataframe(display_data, use_container_width=True, height=400, hide_index=True)
                        csv = display_data.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(label="Exportar esta tabela", icon=":material/download:", data=csv,
                                           file_name=f"ultimas_demandas_{agora().strftime('%Y%m%d_%H%M%S')}.csv",
                                           mime="text/csv", use_container_width=True, key="btn_exportar")
                    else:
                        st.info("Nenhum resultado encontrado com os filtros aplicados.", icon=":material/search_off:")
        with tab5:
            st.markdown(titulo_secao("MOTIVOS DE REVISÃO", "revisao"), unsafe_allow_html=True)
            if 'Motivo_Revisao' not in df.columns:
                st.info("A coluna 'Motivo Revisão' não foi encontrada no arquivo carregado.", icon=":material/info:")
            else:
                col_mf1, col_mf2, col_mf3, col_mf4 = st.columns(4)
                ano_mot, mes_mot, sre_mot, emp_mot = 'Todos os Anos', 'Todos os Meses', 'Todos os SREs', 'Todas Empresas'
                with col_mf1:
                    if 'Ano' in df.columns:
                        ano_mot = st.selectbox(":material/calendar_month: Ano:", key="filtro_ano_motivo",
                                               options=['Todos os Anos'] + sorted(df['Ano'].dropna().unique().astype(int)))
                with col_mf2:
                    if 'Mês' in df.columns:
                        ano_ref = df if ano_mot == 'Todos os Anos' else df[df['Ano'] == int(ano_mot)]
                        mes_mot = st.selectbox(":material/date_range: Mês:", key="filtro_mes_motivo",
                                               options=['Todos os Meses'] + [str(m) for m in sorted(ano_ref['Mês'].dropna().unique().astype(int))],
                                               format_func=lambda m: m if m == 'Todos os Meses' else MESES_NOMES[int(m)])
                with col_mf3:
                    if 'SRE_Nome' in df.columns:
                        sre_mot = st.selectbox(":material/engineering: SRE:", key="filtro_sre_motivo",
                                               options=['Todos os SREs'] + sorted(df['SRE_Nome'].dropna().unique()))
                with col_mf4:
                    if 'Empresa' in df.columns:
                        emp_mot = st.selectbox(":material/apartment: Empresa:", key="filtro_empresa_motivo",
                                               options=['Todas Empresas'] + sorted(df['Empresa'].dropna().unique()))
                df_mot = df.copy()
                if ano_mot != 'Todos os Anos':
                    df_mot = df_mot[df_mot['Ano'] == int(ano_mot)]
                if mes_mot != 'Todos os Meses':
                    df_mot = df_mot[df_mot['Mês'] == int(mes_mot)]
                if sre_mot != 'Todos os SREs':
                    df_mot = df_mot[df_mot['SRE_Nome'] == sre_mot]
                if emp_mot != 'Todas Empresas':
                    df_mot = df_mot[df_mot['Empresa'] == emp_mot]

                motivos_ex = explodir_motivos(df_mot)
                tem_motivo = motivo_preenchido(df_mot['Motivo_Revisao'])
                cards_revisao = df_mot[df_mot['Com_Revisao'] | tem_motivo]
                sem_motivo = int((df_mot['Com_Revisao'] & ~tem_motivo).sum())

                # ---- Indicadores
                col_mk1, col_mk2, col_mk3, col_mk4 = st.columns(4)
                with col_mk1:
                    st.markdown(criar_card_indicador_simples(
                        len(cards_revisao), "Cards com revisão", "revisao", cor=COR_LARANJA,
                        subtitulo=f"{fmt_milhar(int(tem_motivo.sum()))} com motivo informado"), unsafe_allow_html=True)
                with col_mk2:
                    st.markdown(criar_card_indicador_simples(
                        motivos_ex['Motivo'].nunique(), "Motivos distintos", "lista",
                        subtitulo="no período filtrado"), unsafe_allow_html=True)
                with col_mk3:
                    if not motivos_ex.empty:
                        top_mot = motivos_ex.groupby('Motivo')['Chamado'].nunique().sort_values(ascending=False)
                        pct_top = f"{top_mot.iloc[0] / motivos_ex['Chamado'].nunique() * 100:.1f}".replace('.', ',')
                        st.markdown(criar_card_indicador_simples(
                            int(top_mot.iloc[0]), "Principal motivo", "alvo", cor=COR_VERMELHO,
                            subtitulo=f"{top_mot.index[0][:38]} · {pct_top}% dos cards"), unsafe_allow_html=True)
                    else:
                        st.markdown(criar_card_indicador_simples("—", "Principal motivo", "alvo"), unsafe_allow_html=True)
                with col_mk4:
                    pct_sem = f"{(sem_motivo / max(int(df_mot['Com_Revisao'].sum()), 1)) * 100:.1f}".replace('.', ',')
                    st.markdown(criar_card_indicador_simples(
                        sem_motivo, "Revisões sem motivo", "alerta", cor=COR_CINZA_TEXTO,
                        subtitulo=f"{pct_sem}% dos cards com revisão"), unsafe_allow_html=True)

                if motivos_ex.empty:
                    st.info("Nenhum motivo de revisão registrado com os filtros selecionados.", icon=":material/info:")
                else:
                    medida = st.radio(":material/straighten: Medir por:",
                                      ["Cards", "Revisões (Revisões + Qtd. Revisões)"],
                                      horizontal=True, key="medida_motivo",
                                      help="Cards = quantos chamados citam o motivo. Revisões = soma de Revisões + Qtd. Revisões desses chamados.")
                    por_cards = medida == "Cards"
                    resumo_mot = (motivos_ex.groupby('Motivo')
                                  .agg(Cards=('Chamado', 'nunique'), Revisoes=('Revisões_Total', 'sum'),
                                       SREs=('SRE_Nome', 'nunique'), Empresas=('Empresa', 'nunique'),
                                       Ultimo=('Criado', 'max'))
                                  .reset_index())
                    col_valor = 'Cards' if por_cards else 'Revisoes'
                    resumo_mot = resumo_mot.sort_values([col_valor, 'Cards'], ascending=False).reset_index(drop=True)
                    total_valor = max(resumo_mot[col_valor].sum(), 1)
                    resumo_mot['Pct'] = (resumo_mot[col_valor] / total_valor * 100).round(1)
                    resumo_mot['Acumulado'] = resumo_mot['Pct'].cumsum().clip(upper=100).round(1)

                    # ---- Pareto (o que concentra 80% das revisões)
                    st.markdown("### :material/stacked_line_chart: Pareto dos Motivos")
                    limite_pareto = 12
                    pareto = resumo_mot.head(limite_pareto).copy()
                    if len(resumo_mot) > limite_pareto:
                        resto = resumo_mot.iloc[limite_pareto:]
                        pareto = pd.concat([pareto, pd.DataFrame([{
                            'Motivo': f'Demais ({len(resto)})', col_valor: resto[col_valor].sum(),
                            'Pct': resto['Pct'].sum().round(1), 'Acumulado': 100.0}])], ignore_index=True)
                    vitais = int((resumo_mot['Acumulado'] < 80).sum()) + 1
                    vitais = min(vitais, len(resumo_mot))
                    fig_pareto = go.Figure()
                    fig_pareto.add_trace(go.Bar(
                        x=[quebrar_rotulo(m) for m in pareto['Motivo']], y=pareto[col_valor],
                        name='Cards' if por_cards else 'Revisões',
                        marker_color=[COR_LARANJA if i < vitais else '#FFCC80' for i in range(len(pareto))],
                        text=[f"{fmt_milhar(v)}" for v in pareto[col_valor]], textposition='outside', cliponaxis=False,
                        customdata=pareto[['Motivo', 'Pct']].values,
                        hovertemplate='<b>%{customdata[0]}</b><br>%{y} · %{customdata[1]:.1f}% do total<extra></extra>'))
                    fig_pareto.add_trace(go.Scatter(
                        x=[quebrar_rotulo(m) for m in pareto['Motivo']], y=pareto['Acumulado'], yaxis='y2',
                        name='% acumulado', mode='lines+markers', line=dict(color=COR_AZUL_ESCURO, width=2.5),
                        marker=dict(size=8, line=dict(color=COR_BRANCO, width=2)),
                        hovertemplate='Acumulado: %{y:.1f}%<extra></extra>'))
                    fig_pareto.add_hline(y=80, yref='y2', line_dash='dash', line_color=COR_CINZA_TEXTO,
                                         annotation_text='80%', annotation_position='top right')
                    fig_pareto.update_layout(
                        title=f'{vitais} motivo(s) concentram ~80% das {"ocorrências" if por_cards else "revisões"}',
                        yaxis=dict(title='Cards' if por_cards else 'Revisões', rangemode='tozero',
                                   range=[0, pareto[col_valor].max() * 1.2]),
                        yaxis2=dict(title='% acumulado', overlaying='y', side='right', range=[0, 105],
                                    ticksuffix='%', showgrid=False),
                        xaxis=dict(showgrid=False, tickangle=0), height=460, bargap=0.3,
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                        margin=dict(t=70, b=90), hovermode='x unified')
                    st.plotly_chart(fig_pareto, use_container_width=True)
                    st.caption("Barras em laranja forte = motivos que, somados, chegam a ~80% do total "
                               "(onde atacar primeiro). Um card com mais de um motivo conta em cada um deles.")

                    # ---- Motivo × SRE e Motivo × Empresa
                    top_motivos = resumo_mot['Motivo'].head(10).tolist()
                    base_cruz = motivos_ex[motivos_ex['Motivo'].isin(top_motivos)]

                    def mapa_cruzado(coluna, titulo):
                        if por_cards:
                            piv = base_cruz.pivot_table(index='Motivo', columns=coluna, values='Chamado',
                                                        aggfunc='nunique', fill_value=0)
                        else:
                            piv = base_cruz.pivot_table(index='Motivo', columns=coluna, values='Revisões_Total',
                                                        aggfunc='sum', fill_value=0)
                        piv = piv.reindex(top_motivos).fillna(0)
                        piv = piv[piv.sum().sort_values(ascending=False).index]
                        fig = go.Figure(go.Heatmap(
                            z=piv.values, x=list(piv.columns), y=[quebrar_rotulo(m, 28) for m in piv.index],
                            colorscale=[[0, '#FFF8F0'], [0.4, '#FFCC80'], [0.75, COR_LARANJA], [1, '#B35900']],
                            xgap=2, ygap=2, text=piv.values.astype(int), texttemplate='%{text}',
                            textfont=dict(size=11), showscale=False,
                            customdata=[[m] * piv.shape[1] for m in piv.index],
                            hovertemplate='<b>%{customdata}</b><br>%{x}: %{z}<extra></extra>'))
                        fig.update_layout(title=titulo, height=max(320, 42 * len(piv) + 110),
                                          margin=dict(t=50, b=40, l=10, r=10))
                        fig.update_yaxes(autorange='reversed', showgrid=False)
                        fig.update_xaxes(showgrid=False, side='top')
                        return fig

                    st.markdown("### :material/grid_on: Onde cada motivo aparece")
                    col_cz1, col_cz2 = st.columns(2)
                    with col_cz1:
                        if 'SRE_Nome' in motivos_ex.columns:
                            st.plotly_chart(mapa_cruzado('SRE_Nome', 'Motivo × SRE (top 10 motivos)'),
                                            use_container_width=True)
                    with col_cz2:
                        if 'Empresa' in motivos_ex.columns:
                            st.plotly_chart(mapa_cruzado('Empresa', 'Motivo × Empresa (top 10 motivos)'),
                                            use_container_width=True)

                    # ---- Evolução mensal dos principais motivos
                    st.markdown("### :material/calendar_month: Evolução Mensal dos Motivos")
                    top5_mot = resumo_mot['Motivo'].head(5).tolist()
                    evo = motivos_ex.assign(Grupo=motivos_ex['Motivo'].where(motivos_ex['Motivo'].isin(top5_mot), 'Demais'))
                    if por_cards:
                        evo = evo.groupby(['Ano_Mês', 'Mês_Label', 'Grupo'])['Chamado'].nunique().reset_index(name='Valor')
                    else:
                        evo = evo.groupby(['Ano_Mês', 'Mês_Label', 'Grupo'])['Revisões_Total'].sum().reset_index(name='Valor')
                    evo = evo.sort_values('Ano_Mês')
                    ordem_meses_evo = evo.drop_duplicates('Ano_Mês')['Mês_Label'].tolist()
                    cores_mot = [COR_LARANJA, COR_AZUL_ESCURO, COR_VERDE_ESCURO, COR_AZUL_PETROLEO, '#7E57C2']
                    fig_evo = go.Figure()
                    for idx_g, grupo in enumerate(top5_mot + ['Demais']):
                        dados_g = evo[evo['Grupo'] == grupo]
                        if dados_g.empty:
                            continue
                        fig_evo.add_trace(go.Bar(
                            x=dados_g['Mês_Label'], y=dados_g['Valor'], name=grupo[:40],
                            marker_color=cores_mot[idx_g] if idx_g < len(top5_mot) else '#CED4DA',
                            hovertemplate='%{x}<br>' + grupo.replace('%', '%%')[:60] + ': <b>%{y}</b><extra></extra>'))
                    fig_evo.update_layout(
                        barmode='stack', height=420, bargap=0.25, hovermode='x unified',
                        title='Top 5 motivos por mês (demais agrupados)',
                        yaxis=dict(title='Cards' if por_cards else 'Revisões', rangemode='tozero'),
                        xaxis=dict(type='category', categoryorder='array', categoryarray=ordem_meses_evo, showgrid=False),
                        legend=dict(orientation='h', yanchor='top', y=-0.12, x=0), margin=dict(t=60, b=90))
                    st.plotly_chart(fig_evo, use_container_width=True)

                    # ---- Tabela completa + exportação
                    st.markdown("### :material/table_chart: Ranking Completo dos Motivos")
                    tabela_mot = resumo_mot.copy()
                    tabela_mot.insert(0, 'Posição', [f"{i + 1}º" for i in range(len(tabela_mot))])
                    tabela_mot['Ultimo'] = tabela_mot['Ultimo'].dt.strftime('%d/%m/%Y')
                    st.dataframe(
                        tabela_mot[['Posição', 'Motivo', 'Cards', 'Revisoes', 'Pct', 'Acumulado', 'SREs', 'Empresas', 'Ultimo']],
                        use_container_width=True, hide_index=True, height=min(420, 38 * len(tabela_mot) + 40),
                        column_config={
                            "Posição": st.column_config.TextColumn("Posição", width="small"),
                            "Motivo": st.column_config.TextColumn("Motivo", width="large"),
                            "Cards": st.column_config.NumberColumn("Cards", format="%d"),
                            "Revisoes": st.column_config.NumberColumn("Revisões", format="%d",
                                                                      help="Soma de Revisões + Qtd. Revisões"),
                            "Pct": st.column_config.ProgressColumn("% do total", format="%.1f%%", min_value=0, max_value=100),
                            "Acumulado": st.column_config.NumberColumn("% acumulado", format="%.1f%%"),
                            "SREs": st.column_config.NumberColumn("SREs", format="%d"),
                            "Empresas": st.column_config.NumberColumn("Empresas", format="%d"),
                            "Ultimo": st.column_config.TextColumn("Última ocorrência"),
                        })
                    st.download_button("Exportar motivos (CSV)", icon=":material/download:",
                                       data=tabela_mot.drop(columns='Posição').to_csv(index=False).encode('utf-8-sig'),
                                       file_name=f"motivos_revisao_{agora().strftime('%Y%m%d_%H%M%S')}.csv",
                                       mime="text/csv", use_container_width=True)

                    # ---- Chamados de um motivo
                    with st.expander("Ver chamados de um motivo", icon=":material/search:"):
                        motivo_escolhido = st.selectbox("Motivo:", resumo_mot['Motivo'].tolist(), key="motivo_detalhe")
                        det = motivos_ex[motivos_ex['Motivo'] == motivo_escolhido].drop_duplicates('Chamado')
                        det = det.sort_values('Criado', ascending=False)
                        colunas_det = {'Chamado': 'Chamado', 'Criado': 'Criado', 'SRE_Nome': 'SRE', 'Empresa': 'Empresa',
                                       'Responsável_Formatado': 'Responsável', 'Status': 'Status',
                                       'Revisões': 'Revisões', 'Qtd. Revisões': 'Qtd. Revisões',
                                       'Motivo_Revisao': 'Motivo (original)'}
                        colunas_det = {k: v for k, v in colunas_det.items() if k in det.columns}
                        det_exibir = det[list(colunas_det)].rename(columns=colunas_det)
                        if 'Criado' in det_exibir.columns:
                            det_exibir['Criado'] = det_exibir['Criado'].dt.strftime('%d/%m/%Y %H:%M')
                        st.caption(f"{fmt_milhar(len(det_exibir))} chamado(s) com este motivo")
                        st.dataframe(det_exibir, use_container_width=True, hide_index=True, height=360)
    with tab_mapa:
        st.markdown("## :material/map: Mapa de Sincronizações por Empresa")
        col_mapa_filtro1, col_mapa_filtro2, col_mapa_filtro3 = st.columns(3)
        with col_mapa_filtro1:
            empresas_disponiveis = df['Empresa'].dropna().unique()
            empresas_opcoes = ['Todas'] + sorted([e for e in empresas_disponiveis if e in MAPEAMENTO_EMPRESAS])
            empresas_selecionadas_mapa = st.multiselect(":material/apartment: Empresas", options=empresas_opcoes,
                                                        default=['Todas'], key="mapa_empresas_folium")
        with col_mapa_filtro2:
            if 'Ano' in df.columns:
                anos_disponiveis_mapa = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_mapa = ['Todos'] + list(anos_disponiveis_mapa)
                ano_filtro_mapa = st.selectbox(":material/calendar_month: Ano", options=anos_opcoes_mapa, index=0, key="mapa_ano_folium")
            else:
                ano_filtro_mapa = 'Todos'
        with col_mapa_filtro3:
            if 'Mês' in df.columns and ano_filtro_mapa != 'Todos':
                df_ano_mapa = df[df['Ano'] == int(ano_filtro_mapa)]
                meses_disponiveis_mapa = sorted(df_ano_mapa['Mês'].dropna().unique().astype(int))
                meses_opcoes_mapa = ['Todos'] + [f"{m:02d}" for m in meses_disponiveis_mapa]
                mes_filtro_mapa = st.selectbox(":material/date_range: Mês", options=meses_opcoes_mapa, index=0, key="mapa_mes_folium",
                                               format_func=lambda m: m if m == 'Todos' else MESES_NOMES[int(m)])
            else:
                mes_filtro_mapa = 'Todos'
        df_mapa, total_sinc_filtrado = processar_dados_mapa(
            df, empresas_selecionadas=empresas_selecionadas_mapa,
            ano_filtro=ano_filtro_mapa, mes_filtro=mes_filtro_mapa
        )
        col_metrica1, col_metrica2, col_metrica3, col_metrica4 = st.columns(4)
        empresas_ativas = len(df_mapa[df_mapa['sincronismos'] > 0]) if not df_mapa.empty else 0
        with col_metrica1:
            st.markdown(criar_card_indicador_simples(total_sinc_filtrado, "Total Sincronizações", "check",
                                                     cor=COR_VERDE_ESCURO), unsafe_allow_html=True)
        with col_metrica2:
            st.markdown(criar_card_indicador_simples(empresas_ativas, "Empresas com Sinc.", "empresa",
                                                     subtitulo=f"de {len(df_mapa)} mapeadas"), unsafe_allow_html=True)
        with col_metrica3:
            media_sinc = df_mapa['sincronismos'].mean() if not df_mapa.empty else 0
            st.markdown(criar_card_indicador_simples(f"{media_sinc:.1f}".replace('.', ','), "Média por Empresa",
                                                     "grafico", cor=COR_AZUL_PETROLEO), unsafe_allow_html=True)
        with col_metrica4:
            if not df_mapa.empty and df_mapa['sincronismos'].max() > 0:
                max_sinc = df_mapa['sincronismos'].max()
                empresa_max = df_mapa[df_mapa['sincronismos'] == max_sinc]['empresa_nome'].values[0]
                st.markdown(criar_card_indicador_simples(int(max_sinc), f"Maior: {empresa_max[:20]}", "premio",
                                                         cor=CORES_PODIO[1]), unsafe_allow_html=True)
            else:
                st.markdown(criar_card_indicador_simples(0, "Maior Sincronização", "premio"), unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(titulo_secao("MAPA DE BOLHAS", "pino"), unsafe_allow_html=True)
        m = criar_mapa_folium(df_mapa)
        if m:
            mapa_html = m._repr_html_()
            wrapper = f"""
            <div style="border-radius: 12px; overflow: hidden;
                box-shadow: 0 4px 20px rgba(0,89,115,0.12);
                border: 1px solid {COR_CINZA_BORDA}; margin-bottom: 20px;">
                {mapa_html}
            </div>
            """
            components.html(wrapper, height=620)
        else:
            st.info("Nenhuma empresa com sincronizações para exibir no mapa.", icon=":material/info:")
        st.markdown(titulo_secao("RANKING DE SINCRONIZAÇÕES POR EMPRESA", "premio"), unsafe_allow_html=True)
        fig_barras = criar_grafico_barras(df_mapa)
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True, config={'displayModeBar': True})
        with st.expander("Ver Detalhes por Empresa", expanded=False, icon=":material/table_view:"):
            if not df_mapa.empty:
                tabela_detalhes = df_mapa[['empresa_nome', 'sigla', 'estado', 'regiao', 'sincronismos']].copy()
                tabela_detalhes.columns = ['Empresa', 'UF', 'Estado', 'Região', 'Sincronizações']
                tabela_detalhes = tabela_detalhes.sort_values('Sincronizações', ascending=False).reset_index(drop=True)
                total_geral = tabela_detalhes['Sincronizações'].sum()
                posicoes = [f"{i + 1}º" for i in range(len(tabela_detalhes))]
                tabela_detalhes.insert(0, 'Posição', posicoes)
                tabela_detalhes['% Total'] = (tabela_detalhes['Sincronizações'] / total_geral * 100).round(1) if total_geral > 0 else 0
                tabela_detalhes['Empresa (UF)'] = tabela_detalhes.apply(
                    lambda x: f"{x['Empresa']} ({x['UF']})", axis=1)
                df_exibir = tabela_detalhes[['Posição', 'Empresa (UF)', 'Estado', 'Região', 'Sincronizações', '% Total']].copy()
                column_config = {
                    "Posição": st.column_config.TextColumn("Posição", width="small"),
                    "Empresa (UF)": st.column_config.TextColumn("Empresa", width="large"),
                    "Estado": st.column_config.TextColumn("Estado", width="medium"),
                    "Região": st.column_config.TextColumn("Região", width="medium"),
                    "Sincronizações": st.column_config.NumberColumn("Sinc.", format="%d", width="small"),
                    "% Total": st.column_config.ProgressColumn("% Total", format="%.1f%%", min_value=0,
                                                              max_value=100, width="medium")
                }
                st.dataframe(df_exibir, use_container_width=True, column_config=column_config, height=400, hide_index=True)
                csv = tabela_detalhes[['Empresa', 'UF', 'Estado', 'Região', 'Sincronizações', '% Total']].to_csv(index=False).encode('utf-8-sig')
                st.download_button(label="Exportar dados para CSV", icon=":material/download:", data=csv,
                                   file_name=f"sincronismos_empresas_{agora().strftime('%Y%m%d_%H%M%S')}.csv",
                                   mime="text/csv", use_container_width=True)
        with st.expander("Sobre as Cores do Mapa e Ranking", expanded=False, icon=":material/palette:"):
            st.markdown(f"""
            ### :material/palette: Escala de Cores
            <div style="display: flex; gap: 30px; margin: 15px 0;">
                <div><span style="display: inline-block; width: 30px; height: 20px; background: {COR_AZUL_PETROLEO}; border-radius: 4px; vertical-align: middle;"></span> <strong>Baixo volume</strong> - Até 33% do máximo</div>
                <div><span style="display: inline-block; width: 30px; height: 20px; background: {COR_LARANJA}; border-radius: 4px; vertical-align: middle;"></span> <strong>Médio volume</strong> - 33% a 66% do máximo</div>
                <div><span style="display: inline-block; width: 30px; height: 20px; background: {COR_VERMELHO}; border-radius: 4px; vertical-align: middle;"></span> <strong>Alto volume</strong> - Acima de 66% do máximo</div>
            </div>
            ### :material/location_on: Mapa de Bolhas
            - Quanto mais **<span style="color: {COR_VERMELHO};">vermelha</span>** a bolha, maior o número de sincronizações
            - Quanto mais **<span style="color: {COR_AZUL_PETROLEO};">azul</span>** a bolha, menor o número de sincronizações
            - O **tamanho** da bolha também é proporcional ao volume
            - O texto **dentro da bolha** mostra a sigla da empresa e o número de sincronizações
            - **Passe o mouse** sobre cada bolha para ver detalhes completos
            ### :material/leaderboard: Ranking
            - As **barras de progresso** mostram o percentual em relação ao total
            - A cor da barra segue o mesmo gradiente do mapa
            - Os três primeiros lugares recebem selos ouro, prata e bronze
            ### :material/apartment: Empresas Mapeadas
            | Empresa | Nome Completo | Estado |
            |---------|---------------|--------|
            | **EMR** | Energisa Minas Gerais | MG |
            | **EPB** | Energisa Paraíba | PB |
            | **ESE** | Energisa Sergipe | SE |
            | **ESS** | Energisa Sul/Sudeste | SP |
            | **EMS** | Energisa Mato Grosso do Sul | MS |
            | **EMT** | Energisa Mato Grosso | MT |
            | **ETO** | Energisa Tocantins | TO |
            | **ERO** | Energisa Rondônia | RO |
            | **EAC** | Energisa Acre | AC |
            """, unsafe_allow_html=True)
    with tab_ipe:
        st.markdown(titulo_secao("KPI IPE - ÍNDICE DE PERFORMANCE DO ESPECIALISTA", "alvo"), unsafe_allow_html=True)
        if 'SRE' in df.columns and 'Status' in df.columns and 'Retorno_Cliente' in df.columns:
            def calcular_ipe(ca, cr, cd, ct, na):
                # Fórmula mantida exatamente como na versão anterior
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
            st.markdown("### :material/filter_alt: Filtros de Período")
            col_filtro_ipe1, col_filtro_ipe2 = st.columns(2)
            with col_filtro_ipe1:
                if 'Ano' in df.columns:
                    anos_ipe = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_ipe = ['Todos'] + list(anos_ipe)
                    ano_ipe = st.selectbox(":material/calendar_month: Filtrar por Ano:", options=anos_opcoes_ipe, key="filtro_ano_ipe")
                else:
                    ano_ipe = 'Todos'
            with col_filtro_ipe2:
                if 'Mês' in df.columns:
                    meses_disponiveis = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_ipe = [MESES_NOMES[m] for m in meses_disponiveis]
                    meses_selecionados_nomes = st.multiselect(":material/date_range: Selecionar Mês(es):",
                                                              options=meses_opcoes_ipe,
                                                              default=meses_opcoes_ipe,
                                                              key="filtro_meses_ipe")
                    meses_invertido = {v: k for k, v in MESES_NOMES.items()}
                    meses_selecionados_numeros = [meses_invertido[m] for m in meses_selecionados_nomes] if meses_selecionados_nomes else []
                else:
                    meses_selecionados_numeros = []
            df_ipe = df.copy()
            if ano_ipe != 'Todos':
                df_ipe = df_ipe[df_ipe['Ano'] == int(ano_ipe)]
            if meses_selecionados_numeros:
                df_ipe = df_ipe[df_ipe['Mês'].isin(meses_selecionados_numeros)]
            st.markdown("### :material/table_chart: Performance Detalhada - Período Selecionado")
            cards_total_periodo = len(df_ipe)
            total_sres_periodo = df_ipe['SRE'].nunique()
            sres_metrics = []
            for sre in df_ipe['SRE'].dropna().unique():
                df_sre_data = df_ipe[df_ipe['SRE'] == sre]
                if len(df_sre_data) > 0:
                    cd = len(df_sre_data)
                    ca = int(df_sre_data['Sinc'].sum())
                    cr = int(df_sre_data['Reaberto'].sum())
                    ipe = calcular_ipe(ca, cr, cd, cards_total_periodo, total_sres_periodo)
                    sres_metrics.append({
                        'SRE': substituir_nome_sre(sre), 'Cards Demandados': cd,
                        'Cards Analisados': ca, 'Cards Reabertos': cr,
                        'IPE (%)': round(ipe * 100, 2),
                        'Status': 'Na meta' if ipe >= 0.95 else 'Abaixo da meta'
                    })
            if sres_metrics:
                df_sres = pd.DataFrame(sres_metrics).sort_values('IPE (%)', ascending=False)
                col_ipe_graf, col_ipe_tab = st.columns([1, 1.25])
                with col_ipe_graf:
                    # NOVO: IPE por SRE com a linha da meta
                    ordem_ipe = df_sres.sort_values('IPE (%)')
                    fig_ipe_sre = go.Figure(go.Bar(
                        x=ordem_ipe['IPE (%)'], y=ordem_ipe['SRE'], orientation='h',
                        marker_color=[COR_VERDE_ESCURO if v >= 95 else COR_LARANJA for v in ordem_ipe['IPE (%)']],
                        text=[f"{v:.1f}%".replace('.', ',') for v in ordem_ipe['IPE (%)']],
                        textposition='outside', cliponaxis=False,
                        hovertemplate='<b>%{y}</b><br>IPE: %{x:.2f}%<extra></extra>'))
                    fig_ipe_sre.add_vline(x=95, line_dash='dash', line_color=COR_VERDE_ESCURO,
                                          annotation_text='Meta 95%', annotation_position='top')
                    fig_ipe_sre.update_layout(title='IPE por SRE', height=max(280, 48 * len(ordem_ipe) + 110),
                                              xaxis=dict(range=[0, 110], ticksuffix='%'), yaxis=dict(showgrid=False),
                                              margin=dict(t=60, b=30, l=10, r=30), bargap=0.35)
                    st.plotly_chart(fig_ipe_sre, use_container_width=True)
                with col_ipe_tab:
                    st.dataframe(df_sres, use_container_width=True, hide_index=True, column_config={
                        "SRE": st.column_config.TextColumn("SRE", width="medium"),
                        "Cards Demandados": st.column_config.NumberColumn("Demandados", format="%d"),
                        "Cards Analisados": st.column_config.NumberColumn("Analisados", format="%d"),
                        "Cards Reabertos": st.column_config.NumberColumn("Reabertos", format="%d"),
                        "IPE (%)": st.column_config.ProgressColumn("IPE %", format="%.2f%%", min_value=0, max_value=100),
                        "Status": st.column_config.TextColumn("Status", width="small")
                    })
            st.markdown("---")
            st.markdown("### :material/show_chart: IPE Acumulado por Mês")
            st.caption("_Evolução do IPE acumulado mês a mês considerando TODO o período_")
            if 'Criado' in df_ipe.columns and len(df_ipe) > 0:
                df_ipe['Periodo'] = df_ipe['Criado'].dt.strftime('%Y-%m')
                meses_ordenados = sorted(df_ipe['Periodo'].unique())
                acumulados = []
                for periodo in meses_ordenados:
                    df_ate = df_ipe[df_ipe['Periodo'] <= periodo]
                    cd_acum = len(df_ate)
                    ca_acum = int(df_ate['Sinc'].sum())
                    cr_acum = int(df_ate['Reaberto'].sum())
                    na_acum = df_ate['SRE'].nunique()
                    ipe_acum = calcular_ipe(ca_acum, cr_acum, cd_acum, cd_acum, na_acum)
                    ano_p, mes_p = periodo.split('-')
                    acumulados.append({
                        # Corrigido: o rótulo agora inclui o ano (antes Janeiro/2025 e Janeiro/2026 se sobrepunham)
                        'Mês': f"{MESES_NOMES[int(mes_p)]}/{ano_p[2:]}", 'CD_Acum': cd_acum,
                        'CA_Acum': ca_acum, 'CR_Acum': cr_acum,
                        'NA_Acum': na_acum, 'IPE Acumulado (%)': round(ipe_acum * 100, 2)
                    })
                if acumulados:
                    df_acum = pd.DataFrame(acumulados)
                    fig_linha = go.Figure()
                    fig_linha.add_trace(go.Scatter(
                        x=df_acum['Mês'], y=df_acum['IPE Acumulado (%)'],
                        fill='tozeroy', fillcolor='rgba(2, 138, 159, 0.08)',
                        line=dict(width=0), showlegend=False, hoverinfo='skip'))
                    fig_linha.add_trace(go.Scatter(
                        x=df_acum['Mês'], y=df_acum['IPE Acumulado (%)'],
                        mode='lines+markers+text',
                        line=dict(color=COR_AZUL_ESCURO, width=3.5, shape='spline'),
                        marker=dict(size=11, color=[COR_VERDE_ESCURO if v >= 95 else COR_AZUL_PETROLEO
                                                    for v in df_acum['IPE Acumulado (%)']],
                                    line=dict(color=COR_BRANCO, width=2)),
                        text=df_acum['IPE Acumulado (%)'].apply(lambda x: f'{x:.1f}%'.replace('.', ',')),
                        textposition='top center', textfont=dict(size=11, color=COR_AZUL_ESCURO), name='IPE Acumulado',
                        hovertemplate='<b>%{x}</b><br>IPE: %{y:.1f}%<br>CD: %{customdata[0]:,}<br>CA: %{customdata[1]:,}<br>CR: %{customdata[2]:,}<br>SREs: %{customdata[3]}<extra></extra>',
                        customdata=df_acum[['CD_Acum', 'CA_Acum', 'CR_Acum', 'NA_Acum']].values
                    ))
                    fig_linha.add_hline(y=95, line_dash="dash", line_color=COR_VERDE_ESCURO, annotation_text="Meta 95%",
                                        annotation_position="bottom right", annotation_font=dict(color=COR_VERDE_ESCURO))
                    fig_linha.add_hline(y=100, line_dash="dot", line_color=COR_CINZA_TEXTO, annotation_text="Limite 100%",
                                        annotation_position="top right")
                    fig_linha.update_layout(title='Evolução do IPE Acumulado por Mês',
                                            xaxis_title='Mês', yaxis_title='IPE Acumulado (%)',
                                            xaxis=dict(type='category', showgrid=False,
                                                       range=[-0.6, len(df_acum) - 0.4]),
                                            yaxis=dict(range=[0, 108], ticksuffix='%'), height=480,
                                            showlegend=False, margin=dict(t=60, r=30))
                    st.plotly_chart(fig_linha, use_container_width=True)
                    ultimo = df_acum.iloc[-1]
                    primeiro = df_acum.iloc[0]
                    st.markdown("### :material/target: Resumo do Período Acumulado")
                    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                    with col_r1:
                        st.metric(":material/date_range: Período", f"{len(df_acum)} meses",
                                  f"{primeiro['Mês']} - {ultimo['Mês']}", delta_color="off", **DELTA_SEM_SETA)
                    with col_r2:
                        st.metric(":material/assignment: Total Cards", fmt_milhar(ultimo['CD_Acum']))
                    with col_r3:
                        # Corrigido: "inverse" com valor negativo deixava o "abaixo da meta" verde
                        st.metric(":material/target: IPE Acumulado", f"{ultimo['IPE Acumulado (%)']:.2f}%".replace('.', ','),
                                  delta=f"{ultimo['IPE Acumulado (%)'] - 95:+.2f} pp vs meta",
                                  delta_color="normal")
                    with col_r4:
                        st.metric(":material/groups: SREs Ativos", f"{ultimo['NA_Acum']}")
                    with st.expander("Ver Tabela de Acumulados Mensais", expanded=False, icon=":material/table_view:"):
                        st.dataframe(df_acum, use_container_width=True, hide_index=True,
                                     column_config={"IPE Acumulado (%)": st.column_config.ProgressColumn(
                                         "IPE %", format="%.2f%%", min_value=0, max_value=100)})
                        csv_acum = df_acum.to_csv(index=False).encode('utf-8-sig')
                        st.download_button("Exportar para CSV", icon=":material/download:", data=csv_acum,
                                           file_name=f"ipe_acumulado_{agora().strftime('%Y%m%d_%H%M%S')}.csv",
                                           mime="text/csv", use_container_width=True)
            with st.expander("Entenda o Cálculo do IPE", icon=":material/menu_book:"):
                st.markdown("""
                **Fórmula:** `IPE = (CA - CR) / (CD + |((CT/CD)/NA) - 1|)`
                - **CA** = Cards Analisados (Sincronizados)
                - **CR** = Cards Reabertos (Cards com **'Retorno Cliente = Sim'**)
                - **CD** = Cards Demandados (Total do período)
                - **CT** = Cards Total (Total geral)
                - **NA** = Número de Atendentes (SREs únicos)
                **Meta: 95% | Limite máximo: 100%**
                > **Importante:** Cards sem preenchimento na coluna 'Retorno Cliente' são considerados como **'Não'** (não contam como reabertos).
                """)
        else:
            st.warning("Colunas necessárias ('SRE', 'Status', 'Retorno_Cliente') não encontradas.", icon=":material/warning:")
    with tab_estatistica:
        st.markdown("## :material/query_stats: ANÁLISE ESTATÍSTICA")
        st.markdown("_Análise de distribuição, percentis e tendência de sincronizações_")
        col_filtro_est1, col_filtro_est2, col_filtro_est3 = st.columns(3)
        with col_filtro_est1:
            if 'Ano' in df.columns:
                anos_est = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_est = ['Todos os Anos'] + list(anos_est)
                ano_est = st.selectbox(":material/calendar_month: Ano", options=anos_opcoes_est, key="filtro_ano_est", index=0)
            else:
                ano_est = 'Todos os Anos'
        with col_filtro_est2:
            if 'Mês' in df.columns:
                if ano_est != 'Todos os Anos':
                    df_ano_est = df[df['Ano'] == int(ano_est)]
                    meses_est = sorted(df_ano_est['Mês'].dropna().unique().astype(int))
                else:
                    meses_est = sorted(df['Mês'].dropna().unique().astype(int))
                meses_opcoes_est = ['Todos os Meses'] + [f"{m:02d}" for m in meses_est]
                mes_est = st.selectbox(":material/date_range: Mês", options=meses_opcoes_est, key="filtro_mes_est", index=0,
                                       format_func=lambda m: m if m == 'Todos os Meses' else MESES_NOMES[int(m)])
            else:
                mes_est = 'Todos os Meses'
        with col_filtro_est3:
            percentil_param = st.number_input(":material/target: Percentil de Referência (%)",
                                              min_value=50, max_value=99, value=75, step=5,
                                              key="percentil_param",
                                              help="Percentil utilizado para análise de tendência")
        df_est = df.copy()
        if ano_est != 'Todos os Anos':
            df_est = df_est[df_est['Ano'] == int(ano_est)]
        if mes_est != 'Todos os Meses':
            df_est = df_est[df_est['Mês'] == int(mes_est)]
        df_sinc_est = df_est[df_est['Sinc']].copy()
        df_tendencia = pd.DataFrame()
        sinc_por_dia_est = pd.DataFrame()
        if df_sinc_est.empty:
            st.warning("Nenhum dado sincronizado encontrado com os filtros selecionados.", icon=":material/warning:")
        else:
            st.markdown("---")
            st.markdown("### :material/bar_chart: DISTRIBUIÇÃO E PERCENTIS")
            st.markdown(f"_Mediana, Quartis e Percentis - Percentil de Referência: {percentil_param}% · "
                        f"dias úteis sem sincronização contam como zero_")
            if 'Criado' in df_sinc_est.columns:
                # Corrigido: inclui os dias úteis sem sincronização (antes eram ignorados e inflavam os percentis)
                serie_est = serie_diaria(df_sinc_est['Data'])
                sinc_por_dia_est = serie_est.rename_axis('Data').reset_index(name='Quantidade')
                if not sinc_por_dia_est.empty:
                    valores = sinc_por_dia_est['Quantidade']
                    mediana = valores.median()
                    q1 = valores.quantile(0.25)
                    q3 = valores.quantile(0.75)
                    p10 = valores.quantile(0.10)
                    p90 = valores.quantile(0.90)
                    p_selecionado = valores.quantile(percentil_param/100)
                    # Contagens são inteiras: uma barra por valor, centrada no número (mais legível que o histograma)
                    frequencia = valores.value_counts().sort_index()
                    frequencia = frequencia.reindex(range(0, int(frequencia.index.max()) + 1), fill_value=0)
                    fig_sep = go.Figure()
                    fig_sep.add_trace(go.Bar(
                        x=frequencia.index, y=frequencia.values, name='Frequência',
                        marker_color='rgba(2, 138, 159, 0.45)',
                        marker_line_color=COR_AZUL_PETROLEO, marker_line_width=1,
                        hovertemplate='%{x} sincronizações no dia: <b>%{y}</b> dias<extra></extra>'
                    ))
                    linhas_ref = [(p10, f"P10: {p10:.0f}", COR_CINZA_TEXTO, "dot", "bottom left"),
                                  (q1, f"Q1: {q1:.0f}", COR_AZUL_PETROLEO, "dot", "top left"),
                                  (mediana, f"Mediana: {mediana:.0f}", COR_VERDE_ESCURO, "dash", "top"),
                                  (q3, f"Q3: {q3:.0f}", COR_AZUL_PETROLEO, "dot", "top right"),
                                  (p90, f"P90: {p90:.0f}", COR_CINZA_TEXTO, "dot", "bottom right")]
                    for valor_ref, rotulo, cor_ref, traco, posicao in linhas_ref:
                        fig_sep.add_vline(x=valor_ref, line_dash=traco, line_color=cor_ref,
                                          annotation_text=rotulo, annotation_position=posicao,
                                          annotation_font=dict(size=11, color=cor_ref))
                    fig_sep.add_vline(x=p_selecionado, line_dash="solid", line_color=COR_VERMELHO, line_width=3,
                                      annotation_text=f"P{percentil_param}: {p_selecionado:.0f}",
                                      annotation_position="top right",
                                      annotation_font=dict(size=12, color=COR_VERMELHO))
                    rotulo_mes_est = MESES_NOMES[int(mes_est)] if mes_est != "Todos os Meses" else ""
                    fig_sep.update_layout(
                        title=f'Distribuição de Sincronizações Diárias - {ano_est if ano_est != "Todos os Anos" else ""} {rotulo_mes_est}'.strip(' -'),
                        xaxis_title='Número de Sincronizações por Dia',
                        yaxis_title='Frequência (dias)', height=450,
                        showlegend=False, bargap=0.08,
                        xaxis=dict(dtick=1 if frequencia.index.max() <= 30 else None, showgrid=False),
                        margin=dict(t=70)
                    )
                    st.plotly_chart(fig_sep, use_container_width=True)
                    col_sep1, col_sep2, col_sep3, col_sep4, col_sep5 = st.columns(5)
                    with col_sep1:
                        st.metric(":material/vertical_align_bottom: P10", f"{p10:.0f}")
                    with col_sep2:
                        st.metric(":material/align_vertical_bottom: Q1 (P25)", f"{q1:.0f}")
                    with col_sep3:
                        st.metric(":material/align_vertical_center: Mediana (P50)", f"{mediana:.0f}")
                    with col_sep4:
                        st.metric(":material/align_vertical_top: Q3 (P75)", f"{q3:.0f}")
                    with col_sep5:
                        st.metric(f":material/target: P{percentil_param}", f"{p_selecionado:.0f}")
            st.markdown("---")
            st.markdown("### :material/timeline: ANÁLISE DE PERCENTIL PARA TENDÊNCIA")
            st.markdown(f"_Evolução dos percentis ao longo do tempo - Percentil de Referência: {percentil_param}%_")
            if 'Criado' in df_sinc_est.columns:
                df_sinc_est['Mes_Ano'] = df_sinc_est['Criado'].dt.strftime('%Y-%m')
                meses_unicos = sorted(df_sinc_est['Mes_Ano'].unique())
                dados_tendencia = []
                for mes in meses_unicos:
                    df_mes = df_sinc_est[df_sinc_est['Mes_Ano'] == mes]
                    if not df_mes.empty:
                        valores_mes = serie_diaria(df_mes['Data'])
                        if not valores_mes.empty:
                            ano_t, mes_t = mes.split('-')
                            dados_tendencia.append({
                                'Mês': mes,
                                'Mês_Label': f"{MESES_ABREV[int(mes_t)]}/{ano_t}",
                                'P25': valores_mes.quantile(0.25),
                                'P50': valores_mes.quantile(0.50),
                                f'P{percentil_param}': valores_mes.quantile(percentil_param/100),
                                'P90': valores_mes.quantile(0.90),
                                'Média': valores_mes.mean(),
                                'Total': len(df_mes)
                            })
                if dados_tendencia:
                    df_tendencia = pd.DataFrame(dados_tendencia)
                    st.markdown("#### :material/show_chart: Evolução dos Percentis")
                    fig_tendencia = go.Figure()
                    fig_tendencia.add_trace(go.Scatter(
                        x=df_tendencia['Mês_Label'], y=df_tendencia['P90'],
                        mode='lines', name='P25-P90 (Faixa)', line=dict(width=0), showlegend=False, hoverinfo='skip'
                    ))
                    fig_tendencia.add_trace(go.Scatter(
                        x=df_tendencia['Mês_Label'], y=df_tendencia['P25'],
                        mode='lines', fill='tonexty', fillcolor='rgba(2, 138, 159, 0.15)',
                        line=dict(width=0), name='Faixa P25–P90', hoverinfo='skip'
                    ))
                    fig_tendencia.add_trace(go.Scatter(
                        x=df_tendencia['Mês_Label'], y=df_tendencia[f'P{percentil_param}'],
                        mode='lines+markers', name=f'P{percentil_param}',
                        line=dict(color=COR_VERMELHO, width=3, shape='spline'),
                        marker=dict(size=9, color=COR_VERMELHO, line=dict(color=COR_BRANCO, width=2))
                    ))
                    fig_tendencia.add_trace(go.Scatter(
                        x=df_tendencia['Mês_Label'], y=df_tendencia['P50'],
                        mode='lines+markers', name='P50 (Mediana)',
                        line=dict(color=COR_AZUL_ESCURO, width=2.5, shape='spline'),
                        marker=dict(size=8, color=COR_AZUL_ESCURO, line=dict(color=COR_BRANCO, width=2))
                    ))
                    fig_tendencia.add_trace(go.Scatter(
                        x=df_tendencia['Mês_Label'], y=df_tendencia['Média'],
                        mode='lines+markers', name='Média',
                        line=dict(color=COR_VERDE_ESCURO, width=2, dash='dash', shape='spline'),
                        marker=dict(size=7, color=COR_VERDE_ESCURO)
                    ))
                    fig_tendencia.update_layout(
                        title=f'Evolução dos Percentis de Sincronizações Diárias',
                        xaxis_title='Mês', yaxis_title='Sincronizações por Dia',
                        xaxis=dict(type='category', showgrid=False), yaxis=dict(rangemode='tozero'),
                        height=450, hovermode='x unified', margin=dict(t=80),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig_tendencia, use_container_width=True)
                    st.markdown("#### :material/insights: Análise da Tendência")
                    # O mês corrente (incompleto) fica fora da comparação para não distorcer o resultado
                    tend_fechada = df_tendencia[df_tendencia['Mês'] < agora().strftime('%Y-%m')]
                    if len(tend_fechada) < 2:
                        tend_fechada = df_tendencia
                    if len(tend_fechada) > 1:
                        primeiro = tend_fechada.iloc[0]
                        ultimo = tend_fechada.iloc[-1]
                        col_tend1, col_tend2, col_tend3 = st.columns(3)
                        # Corrigido: delta_color "inverse" em queda deixava a seta verde
                        with col_tend1:
                            variacao_p50 = ((ultimo['P50'] - primeiro['P50']) / primeiro['P50'] * 100) if primeiro['P50'] > 0 else 0
                            st.metric(":material/align_vertical_center: Mediana (P50)", f"{ultimo['P50']:.0f}",
                                      delta=f"{variacao_p50:+.1f}%", delta_color="normal",
                                      help=f"{ultimo['Mês_Label']} vs {primeiro['Mês_Label']}")
                        with col_tend2:
                            variacao_p_param = ((ultimo[f'P{percentil_param}'] - primeiro[f'P{percentil_param}']) / primeiro[f'P{percentil_param}'] * 100) if primeiro[f'P{percentil_param}'] > 0 else 0
                            st.metric(f":material/target: P{percentil_param}", f"{ultimo[f'P{percentil_param}']:.0f}",
                                      delta=f"{variacao_p_param:+.1f}%", delta_color="normal",
                                      help=f"{ultimo['Mês_Label']} vs {primeiro['Mês_Label']}")
                        with col_tend3:
                            variacao_media = ((ultimo['Média'] - primeiro['Média']) / primeiro['Média'] * 100) if primeiro['Média'] > 0 else 0
                            st.metric(":material/functions: Média", f"{ultimo['Média']:.1f}".replace('.', ','),
                                      delta=f"{variacao_media:+.1f}%", delta_color="normal",
                                      help=f"{ultimo['Mês_Label']} vs {primeiro['Mês_Label']}")
                        st.markdown("#### :material/lightbulb: Resumo da Tendência")
                        periodo_txt = f"({primeiro['Mês_Label']} → {ultimo['Mês_Label']}, meses fechados)"
                        if variacao_p50 > 10:
                            st.success(f"**Tendência POSITIVA** - A mediana cresceu {variacao_p50:.1f}% no período analisado {periodo_txt}",
                                       icon=":material/trending_up:")
                        elif variacao_p50 > 0:
                            st.info(f"**Leve crescimento** - A mediana cresceu {variacao_p50:.1f}% no período {periodo_txt}",
                                    icon=":material/north_east:")
                        elif variacao_p50 > -10:
                            st.warning(f"**Estável** - A mediana variou {variacao_p50:.1f}% no período {periodo_txt}",
                                       icon=":material/trending_flat:")
                        else:
                            st.error(f"**Tendência NEGATIVA** - A mediana caiu {abs(variacao_p50):.1f}% no período {periodo_txt}",
                                     icon=":material/trending_down:")
                    with st.expander("Ver Tabela de Tendência Completa", expanded=False, icon=":material/table_view:"):
                        st.dataframe(df_tendencia, use_container_width=True, hide_index=True,
                                     column_config={
                                         "Mês_Label": st.column_config.TextColumn("Mês"),
                                         "P25": st.column_config.NumberColumn("P25", format="%.1f"),
                                         "P50": st.column_config.NumberColumn("P50", format="%.1f"),
                                         f"P{percentil_param}": st.column_config.NumberColumn(f"P{percentil_param}", format="%.1f"),
                                         "P90": st.column_config.NumberColumn("P90", format="%.1f"),
                                         "Média": st.column_config.NumberColumn("Média", format="%.1f"),
                                         "Total": st.column_config.NumberColumn("Total Chamados", format="%d")
                                     })
            st.markdown("---")
            st.markdown("### :material/download: Exportar Dados")
            col_export1, col_export2 = st.columns(2)
            with col_export1:
                if not df_tendencia.empty:
                    csv_tendencia = df_tendencia.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(label="Exportar Tendência de Percentis", icon=":material/download:",
                                       data=csv_tendencia,
                                       file_name=f"tendencia_percentis_{agora().strftime('%Y%m%d_%H%M%S')}.csv",
                                       mime="text/csv", use_container_width=True)
            with col_export2:
                if not sinc_por_dia_est.empty:
                    csv_sinc = (sinc_por_dia_est.assign(Data=sinc_por_dia_est['Data'].dt.strftime('%d/%m/%Y'))
                                .to_csv(index=False).encode('utf-8-sig'))
                    st.download_button(label="Exportar Sincronizações Diárias", icon=":material/download:",
                                       data=csv_sinc,
                                       file_name=f"sincronizacoes_diarias_{agora().strftime('%Y%m%d_%H%M%S')}.csv",
                                       mime="text/csv", use_container_width=True)
else:
    st.markdown(f"""
    <div style="text-align: center; padding: 4rem; background: {COR_CINZA_FUNDO}; border-radius: 12px; border: 2px dashed {COR_CINZA_BORDA};">
        <div style="margin-bottom: 0.6rem;">{icone('atividade', 46, COR_AZUL_PETROLEO, 1.8)}</div>
        <h3 style="color: {COR_PRETO_SUAVE};">Esteira ADMS Dashboard</h3>
        <p style="color: {COR_CINZA_TEXTO}; margin-bottom: 2rem;">
            Sistema de análise e monitoramento de chamados - Setor SRE
        </p>
        <div style="margin-top: 2rem; padding: 2rem; background: {COR_BRANCO}; border-radius: 8px; display: inline-block; text-align: left;">
            <h4 style="color: {COR_AZUL_ESCURO}; display:flex; align-items:center; gap:8px;">{icone('lista', 20, COR_AZUL_ESCURO)} Para começar:</h4>
            <p>1. <strong>Use a barra lateral esquerda</strong> para fazer upload do arquivo CSV</p>
            <p>2. <strong>Use a seção "Importar Dados"</strong> no final da barra lateral</p>
            <p>3. <strong>Ou coloque um arquivo CSV</strong> no mesmo diretório do app</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")
ultima_atualizacao = st.session_state.get('ultima_atualizacao') or get_horario_brasilia()
st.markdown(f"""
<div class="footer">
    <div style="margin-bottom: 0.8rem;">
        <p style="margin: 0; color: {COR_PRETO_SUAVE}; font-weight: 500;">
        Desenvolvido por: <span style="color: {COR_AZUL_ESCURO};">TIME SRE | GAUT</span>
        </p>
        <p style="margin: 0.3rem 0 0 0; color: {COR_CINZA_TEXTO}; font-size: 0.8rem; display:inline-flex; align-items:center; gap:6px;">
        {icone('email', 14, COR_CINZA_TEXTO)} Contato: <a href="mailto:kewin.ferreira@energisa.com.br" style="color: {COR_AZUL_ESCURO}; text-decoration: none;">kewin.ferreira@energisa.com.br</a>
        </p>
    </div>
    <div>
        <p style="margin: 0; color: {COR_CINZA_TEXTO}; font-size: 0.75rem;">
        © {agora().year} Esteira ADMS Dashboard | Sistema proprietário - Energisa Group
        </p>
        <p style="margin: 0.2rem 0 0 0; color: {COR_CINZA_TEXTO}; font-size: 0.7rem;">
        Versão 5.6 | Sistema de Performance SRE | Última atualização: {ultima_atualizacao} (Brasília)
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
