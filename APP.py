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
        'latitude': -19.5,
        'longitude': -44.5
    },
    'EPB': {
        'sigla': 'PB',
        'estado': 'Paraíba',
        'regiao': 'Nordeste',
        'nome_completo': 'Energisa Paraíba',
        'latitude': -7.2,
        'longitude': -36.8
    },
    'ESE': {
        'sigla': 'SE',
        'estado': 'Sergipe',
        'regiao': 'Nordeste',
        'nome_completo': 'Energisa Sergipe',
        'latitude': -10.9,
        'longitude': -37.1
    },
    'ESS': {
        'sigla': 'SP',
        'estado': 'São Paulo',
        'regiao': 'Sudeste',
        'nome_completo': 'Energisa Sul/Sudeste',
        'latitude': -23.5,
        'longitude': -46.6
    },
    'EMS': {
        'sigla': 'MS',
        'estado': 'Mato Grosso do Sul',
        'regiao': 'Centro-Oeste',
        'nome_completo': 'Energisa Mato Grosso do Sul',
        'latitude': -20.5,
        'longitude': -54.6
    },
    'EMT': {
        'sigla': 'MT',
        'estado': 'Mato Grosso',
        'regiao': 'Centro-Oeste',
        'nome_completo': 'Energisa Mato Grosso',
        'latitude': -12.5,
        'longitude': -55.0
    },
    'ETO': {
        'sigla': 'TO',
        'estado': 'Tocantins',
        'regiao': 'Norte',
        'nome_completo': 'Energisa Tocantins',
        'latitude': -10.2,
        'longitude': -48.3
    },
    'ERO': {
        'sigla': 'RO',
        'estado': 'Rondônia',
        'regiao': 'Norte',
        'nome_completo': 'Energisa Rondônia',
        'latitude': -10.8,
        'longitude': -63.5
    },
    'EAC': {
        'sigla': 'AC',
        'estado': 'Acre',
        'regiao': 'Norte',
        'nome_completo': 'Energisa Acre',
        'latitude': -9.0,
        'longitude': -70.0
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
# FUNÇÕES DO MAPA ATUALIZADAS
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
    
    for empresa in sinc_por_empresa['Empresa']:
        if empresa in MAPEAMENTO_EMPRESAS:
            info = MAPEAMENTO_EMPRESAS[empresa]
            qtd = sinc_por_empresa[sinc_por_empresa['Empresa'] == empresa]['Sincronismos'].values[0]
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
    
    # Adicionar empresas com zero sincronismos se estiverem selecionadas
    if empresas_selecionadas and 'Todas' not in empresas_selecionadas:
        for empresa in empresas_selecionadas:
            if empresa in MAPEAMENTO_EMPRESAS and empresa not in sinc_por_empresa['Empresa'].values:
                info = MAPEAMENTO_EMPRESAS[empresa]
                dados_mapa.append({
                    'sigla': info['sigla'],
                    'estado': info['estado'],
                    'regiao': info['regiao'],
                    'empresa': empresa,
                    'empresa_nome': info['nome_completo'],
                    'sincronismos': 0,
                    'latitude': info['latitude'],
                    'longitude': info['longitude']
                })
    
    return pd.DataFrame(dados_mapa), total_sinc

def criar_mapa_coropletico(df_mapa):
    """Cria o mapa coroplético (por estados) com cores invertidas e linhas de divisão"""
    if df_mapa.empty:
        return None
    
    # Criar o mapa com escala de cores invertida (vermelho para maior, verde para menor)
    fig = px.choropleth(
        df_mapa,
        locations='sigla',
        locationmode="USA-states",
        color='sincronismos',
        hover_name='estado',
        hover_data={
            'empresa_nome': True,
            'sincronismos': True,
            'regiao': True
        },
        # Escala invertida: vermelho (maior) -> laranja -> verde (menor)
        color_continuous_scale=[
            [0.0, "#2E7D32"],      # Verde escuro (menor)
            [0.33, "#F57C00"],     # Laranja (médio)
            [0.66, "#C62828"],     # Vermelho escuro (alto)
            [1.0, "#8B0000"]       # Vermelho mais intenso (máximo)
        ],
        title="<b>Mapa de Sincronizações por Estado</b>",
        labels={'sincronismos': 'Nº de Sincronizações'}
    )
    
    # Personalizar o popup
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                      "Empresa: %{customdata[0]}<br>" +
                      "Sincronizações: <b>%{customdata[1]}</b><br>" +
                      "Região: %{customdata[2]}<extra></extra>",
        # Adicionar bordas mais visíveis
        marker_line_width=1.5,
        marker_line_color='black'
    )
    
    # Configurar o mapa com linhas de divisão de estados mais visíveis
    fig.update_geos(
        fitbounds="locations",
        visible=True,
        projection_type="mercator",
        # Configurar linhas de divisão
        showcountries=False,
        showcoastlines=True,
        coastlinecolor="black",
        coastlinewidth=1,
        showland=True,
        landcolor='rgb(240, 240, 240)',
        showlakes=True,
        lakecolor='rgb(200, 220, 240)',
        showocean=True,
        oceancolor='rgb(200, 220, 240)',
        showframe=True,
        framecolor='black',
        framewidth=1,
        # LINHAS DOS ESTADOS
        showsubunits=True,
        subunitcolor='black',
        subunitwidth=1.5,
        # Ajustar zoom para focar no Brasil
        lonaxis_range=[-75, -35],
        lataxis_range=[-35, 5]
    )
    
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title="Sincronizações",
            thicknessmode="pixels",
            thickness=25,
            lenmode="pixels",
            len=350,
            yanchor="middle",
            y=0.5,
            tickfont=dict(size=12),
            title_font=dict(size=12)
        ),
        geo=dict(
            bgcolor='rgb(220, 240, 250)',
            resolution=110
        )
    )
    
    return fig

def criar_mapa_bolhas(df_mapa):
    """Cria um mapa de bolhas (scatter geo) com cores invertidas e linhas de divisão"""
    if df_mapa.empty:
        return None
    
    # Filtrar apenas empresas com sincronismos > 0 para as bolhas
    df_bolhas = df_mapa[df_mapa['sincronismos'] > 0].copy()
    
    if df_bolhas.empty:
        return None
    
    # Criar escala de cores invertida (vermelho para maior, verde para menor)
    fig = px.scatter_geo(
        df_bolhas,
        lat='latitude',
        lon='longitude',
        size='sincronismos',
        hover_name='estado',
        text='empresa',
        color='sincronismos',
        color_continuous_scale=[
            [0.0, "#2E7D32"],      # Verde escuro (menor)
            [0.5, "#F57C00"],      # Laranja (médio)
            [1.0, "#8B0000"]       # Vermelho intenso (maior)
        ],
        size_max=60,
        title="<b>Mapa de Bolhas - Volume de Sincronizações</b>",
        labels={'sincronismos': 'Nº de Sincronizações'}
    )
    
    # Personalizar o popup
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                      "Empresa: %{text}<br>" +
                      "Sincronizações: <b>%{marker.size}</b><br>" +
                      "<extra></extra>",
        marker=dict(
            line=dict(width=1.5, color='black'),
            opacity=0.8
        )
    )
    
    # Configurar o mapa com linhas de divisão
    fig.update_geos(
        projection_type="natural earth",
        showcountries=False,
        showcoastlines=True,
        coastlinecolor="black",
        coastlinewidth=1,
        showsubunits=True,
        subunitcolor='black',
        subunitwidth=1.5,
        showland=True,
        landcolor='rgb(240, 240, 240)',
        showlakes=True,
        lakecolor='rgb(200, 220, 240)',
        showocean=True,
        oceancolor='rgb(200, 220, 240)',
        showframe=True,
        framecolor='black',
        framewidth=1,
        lonaxis_range=[-75, -35],
        lataxis_range=[-35, 5]
    )
    
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title="Sincronizações",
            thicknessmode="pixels",
            thickness=25,
            title_font=dict(size=12)
        )
    )
    
    return fig

def criar_grafico_barras(df_mapa):
    """Cria gráfico de barras comparativo com cores invertidas"""
    if df_mapa.empty:
        return None
    
    df_barras = df_mapa.sort_values('sincronismos', ascending=True)
    
    fig = go.Figure()
    
    # Cores invertidas: maior valor = vermelho, menor = verde
    cores = []
    max_val = df_barras['sincronismos'].max() if len(df_barras) > 0 else 0
    
    for val in df_barras['sincronismos']:
        if val == 0:
            cores.append(COR_CINZA_TEXTO)
        elif val < max_val * 0.25:
            cores.append("#2E7D32")    # Verde (baixo)
        elif val < max_val * 0.6:
            cores.append("#F57C00")    # Laranja (médio)
        else:
            cores.append("#C62828")    # Vermelho (alto)
    
    fig.add_trace(go.Bar(
        x=df_barras['sincronismos'],
        y=df_barras['empresa_nome'],
        orientation='h',
        text=df_barras['sincronismos'],
        textposition='outside',
        marker_color=cores,
        marker_line_color='black',
        marker_line_width=1,
        hovertemplate="Empresa: %{y}<br>Sincronizações: %{x}<extra></extra>"
    ))
    
    fig.update_layout(
        title="<b>Ranking de Sincronizações por Empresa</b>",
        xaxis_title="Número de Sincronizações",
        yaxis_title="",
        height=450,
        showlegend=False,
        plot_bgcolor=COR_BRANCO,
        xaxis=dict(gridcolor=COR_CINZA_BORDA, title_font=dict(size=12)),
        yaxis=dict(gridcolor=COR_CINZA_BORDA, tickfont=dict(size=11))
    )
    
    return fig

def criar_mapa_comparativo(df_mapa):
    """Cria um mapa com visualização combinada (bolhas + cores) para melhor visualização"""
    if df_mapa.empty:
        return None
    
    # Criar figura base
    fig = go.Figure()
    
    # Adicionar bolhas para empresas com dados
    df_bolhas = df_mapa[df_mapa['sincronismos'] > 0].copy()
    
    if not df_bolhas.empty:
        # Definir cores baseadas no valor (vermelho = maior, verde = menor)
        max_val = df_bolhas['sincronismos'].max()
        min_val = df_bolhas['sincronismos'].min()
        
        sizes = []
        colors = []
        for val in df_bolhas['sincronismos']:
            if max_val == min_val:
                colors.append("#2E7D32")
                sizes.append(30)
            else:
                normalized = (val - min_val) / (max_val - min_val)
                if normalized > 0.7:
                    colors.append("#C62828")  # Vermelho
                    sizes.append(45 + normalized * 15)
                elif normalized > 0.4:
                    colors.append("#F57C00")  # Laranja
                    sizes.append(30 + normalized * 15)
                else:
                    colors.append("#2E7D32")  # Verde
                    sizes.append(20 + normalized * 10)
        
        fig.add_trace(go.Scattergeo(
            lon=df_bolhas['longitude'],
            lat=df_bolhas['latitude'],
            text=df_bolhas['empresa_nome'],
            mode='markers+text',
            marker=dict(
                size=sizes,
                color=colors,
                line=dict(width=1.5, color='black'),
                opacity=0.85,
                symbol='circle'
            ),
            textposition='top center',
            textfont=dict(size=10, color='black'),
            name='Sincronizações',
            hovertemplate='<b>%{text}</b><br>' +
                         'Sincronizações: %{marker.size:.0f}<br>' +
                         '<extra></extra>'
        ))
    
    # Adicionar camada de coroplético (cores nos estados)
    fig_choropleth = px.choropleth(
        df_mapa,
        locations='sigla',
        locationmode="USA-states",
        color='sincronismos',
        color_continuous_scale=[
            [0.0, "#2E7D32"],
            [0.33, "#F57C00"],
            [0.66, "#C62828"],
            [1.0, "#8B0000"]
        ]
    )
    
    # Combinar os traces
    for trace in fig_choropleth.data:
        fig.add_trace(trace)
    
    # Configurar o mapa com linhas de divisão completas
    fig.update_geos(
        projection_type="natural earth",
        showcountries=False,
        showcoastlines=True,
        coastlinecolor="black",
        coastlinewidth=1.2,
        showsubunits=True,
        subunitcolor='black',
        subunitwidth=1.8,
        showland=True,
        landcolor='rgb(245, 245, 245)',
        showlakes=True,
        lakecolor='rgb(200, 220, 240)',
        showocean=True,
        oceancolor='rgb(210, 230, 250)',
        showframe=True,
        framecolor='black',
        framewidth=1.5,
        lonaxis_range=[-75, -35],
        lataxis_range=[-35, 5],
        resolution=110
    )
    
    fig.update_layout(
        title=dict(
            text="<b>Mapa de Sincronizações - Visualização Completa</b>",
            font=dict(size=16),
            x=0.5
        ),
        height=650,
        margin={"r": 10, "t": 60, "l": 10, "b": 10},
        showlegend=False
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
                Acompanhamento de Demandas - EMS | EMR | ESS | ESE
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
    tab_principal, tab_mapa = st.tabs(["📊 Dashboard Principal", "🗺️ Mapa de Sincronizações"])
    
    with tab_principal:
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
        
        # Aqui você mantém todo o conteúdo do dashboard principal (tabs 1-4 e análises avançadas)
        # Como o código é muito extenso, mantenha o mesmo conteúdo que você tinha antes
        # Apenas mova todo o conteúdo do dashboard principal para dentro deste tab_principal
        
        st.markdown("---")
        st.markdown(f'<div class="section-title">👥 TOP 10 RESPONSÁVEIS</div>', unsafe_allow_html=True)
        
        if 'Responsável_Formatado' in df.columns:
            top_responsaveis = df['Responsável_Formatado'].value_counts().head(10).reset_index()
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
                marker_line_color=COR_AZUL_PETROLEO,
                marker_line_width=1.5,
                opacity=0.9
            )
            
            fig_top.update_layout(
                height=500,
                plot_bgcolor=COR_BRANCO,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis_title="Número de Demandas",
                yaxis_title=""
            )
            
            st.plotly_chart(fig_top, use_container_width=True)
        
        st.markdown("---")
        st.markdown(f'<div class="section-title">📊 DISTRIBUIÇÃO POR TIPO</div>', unsafe_allow_html=True)
        
        if 'Tipo_Chamado' in df.columns:
            tipos_chamado = df['Tipo_Chamado'].value_counts().reset_index()
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
                marker_line_color=COR_AZUL_ESCURO,
                marker_line_width=1,
                opacity=0.9
            )
            
            fig_tipos.update_layout(
                height=500,
                plot_bgcolor=COR_BRANCO,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis_title="Quantidade",
                yaxis_title=""
            )
            
            st.plotly_chart(fig_tipos, use_container_width=True)
        
        st.markdown("---")
        st.markdown(f'<div class="section-title">🕒 ÚLTIMAS DEMANDAS REGISTRADAS</div>', unsafe_allow_html=True)
        
        if 'Criado' in df.columns:
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
    
    with tab_mapa:
        st.markdown("## 🗺️ Mapa de Sincronizações por Empresa")
        
        # Filtros para o mapa
        col_mapa_filtro1, col_mapa_filtro2, col_mapa_filtro3 = st.columns(3)
        
        with col_mapa_filtro1:
            empresas_disponiveis = df['Empresa'].dropna().unique()
            empresas_opcoes = ['Todas'] + sorted([e for e in empresas_disponiveis if e in MAPEAMENTO_EMPRESAS])
            
            empresas_selecionadas_mapa = st.multiselect(
                "🏢 Empresas",
                options=empresas_opcoes,
                default=['Todas'],
                key="mapa_empresas"
            )
        
        with col_mapa_filtro2:
            if 'Ano' in df.columns:
                anos_disponiveis_mapa = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_mapa = ['Todos'] + list(anos_disponiveis_mapa)
                ano_filtro_mapa = st.selectbox(
                    "📅 Ano",
                    options=anos_opcoes_mapa,
                    index=0,
                    key="mapa_ano"
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
                    key="mapa_mes"
                )
            else:
                mes_filtro_mapa = 'Todos'
        
        # Tipo de visualização
        tipo_mapa = st.radio(
            "🗺️ Tipo de Visualização",
            options=["Coroplético (Estados)", "Bolhas (Pontos)", "Ambos", "Visualização Combinada"],
            index=0,
            horizontal=True,
            key="mapa_tipo"
        )
        
        # Processar dados para o mapa
        df_mapa, total_sinc_filtrado = processar_dados_mapa(
            df,
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
        
        # Informação sobre a escala de cores
        st.info("🎨 **Escala de Cores:** Quanto mais intenso o VERMELHO, maior o volume de sincronizações | Quanto mais VERDE, menor o volume")
        
        # Mapas
        if tipo_mapa == "Coroplético (Estados)":
            st.markdown('<div class="section-title">🗺️ MAPA COROPLÉTICO</div>', unsafe_allow_html=True)
            
            fig_coropletico = criar_mapa_coropletico(df_mapa)
            if fig_coropletico:
                st.plotly_chart(fig_coropletico, use_container_width=True, config={'displayModeBar': True})
            else:
                st.warning("⚠️ Não há dados suficientes para gerar o mapa coroplético.")
        
        elif tipo_mapa == "Bolhas (Pontos)":
            st.markdown('<div class="section-title">📍 MAPA DE BOLHAS</div>', unsafe_allow_html=True)
            
            fig_bolhas = criar_mapa_bolhas(df_mapa)
            if fig_bolhas:
                st.plotly_chart(fig_bolhas, use_container_width=True, config={'displayModeBar': True})
            else:
                st.info("ℹ️ Nenhuma empresa com sincronizações para exibir no mapa de bolhas.")
        
        elif tipo_mapa == "Ambos":
            st.markdown('<div class="section-title">🗺️ MAPA COROPLÉTICO</div>', unsafe_allow_html=True)
            
            fig_coropletico = criar_mapa_coropletico(df_mapa)
            if fig_coropletico:
                st.plotly_chart(fig_coropletico, use_container_width=True, config={'displayModeBar': True})
            else:
                st.warning("⚠️ Não há dados suficientes para gerar o mapa coroplético.")
            
            st.markdown('<div class="section-title" style="margin-top: 2rem;">📍 MAPA DE BOLHAS</div>', unsafe_allow_html=True)
            
            fig_bolhas = criar_mapa_bolhas(df_mapa)
            if fig_bolhas:
                st.plotly_chart(fig_bolhas, use_container_width=True, config={'displayModeBar': True})
            else:
                st.info("ℹ️ Nenhuma empresa com sincronizações para exibir no mapa de bolhas.")
        
        elif tipo_mapa == "Visualização Combinada":
            st.markdown('<div class="section-title">🗺️ VISUALIZAÇÃO COMBINADA</div>', unsafe_allow_html=True)
            
            fig_combinado = criar_mapa_comparativo(df_mapa)
            if fig_combinado:
                st.plotly_chart(fig_combinado, use_container_width=True, config={'displayModeBar': True})
            else:
                st.warning("⚠️ Não há dados suficientes para gerar a visualização combinada.")
        
        # Gráfico de barras (sempre exibido)
        st.markdown('<div class="section-title" style="margin-top: 2rem;">📊 RANKING DE SINCRONIZAÇÕES</div>', unsafe_allow_html=True)
        
        fig_barras = criar_grafico_barras(df_mapa)
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True, config={'displayModeBar': True})
        
        # Tabela detalhada
        with st.expander("📋 Ver Detalhes por Empresa", expanded=False):
            if not df_mapa.empty:
                tabela_detalhes = df_mapa[['empresa_nome', 'sigla', 'regiao', 'sincronismos']].copy()
                tabela_detalhes.columns = ['Empresa', 'UF', 'Região', 'Sincronizações']
                tabela_detalhes = tabela_detalhes.sort_values('Sincronizações', ascending=False)
                
                st.dataframe(
                    tabela_detalhes,
                    use_container_width=True,
                    column_config={
                        "Empresa": st.column_config.TextColumn("Empresa", width="large"),
                        "UF": st.column_config.TextColumn("UF", width="small"),
                        "Região": st.column_config.TextColumn("Região", width="medium"),
                        "Sincronizações": st.column_config.NumberColumn("Sinc.", format="%d")
                    }
                )
                
                csv = tabela_detalhes.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Exportar dados para CSV",
                    data=csv,
                    file_name=f"sincronismos_empresas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # Legenda
        with st.expander("ℹ️ Sobre o Mapa de Sincronizações", expanded=False):
            st.markdown("""
            **🗺️ Mapa de Sincronismos - Guia Rápido**
            
            Este mapa visualiza geograficamente os sincronismos por empresa da Energisa.
            
            **Escala de Cores:**
            - 🔴 **VERMELHO**: Alto volume de sincronizações (quanto mais intenso, maior o volume)
            - 🟠 **LARANJA**: Volume médio de sincronizações
            - 🟢 **VERDE**: Baixo volume de sincronizações
            
            **Tipos de Visualização:**
            - **Mapa Coroplético**: Cores nos estados representam o volume de sincronizações
            - **Mapa de Bolhas**: Círculos proporcionais ao volume, posicionados geograficamente
            - **Visualização Combinada**: Bolhas + cores para melhor compreensão
            
            **Linhas de Divisão:**
            - Linhas pretas representam as fronteiras entre os estados
            - Linhas mais grossas destacam as divisas principais
            
            **Filtros Disponíveis:**
            - Selecione empresas específicas para análise focada
            - Filtre por ano e mês para análise temporal
            
            **Empresas Mapeadas:**
            - **EMR** - Energisa Minas Gerais (MG)
            - **EPB** - Energisa Paraíba (PB)
            - **ESE** - Energisa Sergipe (SE)
            - **ESS** - Energisa Sul/Sudeste (SP)
            - **EMS** - Energisa Mato Grosso do Sul (MS)
            - **EMT** - Energisa Mato Grosso (MT)
            - **ETO** - Energisa Tocantins (TO)
            - **ERO** - Energisa Rondônia (RO)
            - **EAC** - Energisa Acre (AC)
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
