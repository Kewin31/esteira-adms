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
# PALETA DE CORES - EXECUTIVA
# ============================================
# Cores principais - mais sóbrias e profissionais
COR_AZUL_ESCURO = "#1a2a3a"       # Azul escuro - principal corporativo
COR_AZUL_MEDIO = "#2c5282"        # Azul médio - secundário
COR_AZUL_CLARO = "#4a7fb5"        # Azul claro - destaques
COR_VERDE_CORPORATIVO = "#276749" # Verde corporativo
COR_LARANJA_SUAVE = "#c05621"     # Laranja suave
COR_VERMELHO_SUAVE = "#9b2c2c"    # Vermelho suave
COR_CINZA_ESCURO = "#2d3748"      # Cinza escuro
COR_CINZA_MEDIO = "#4a5568"       # Cinza médio
COR_CINZA_CLARO = "#718096"       # Cinza claro

# Cores neutras
COR_FUNDO = "#f7fafc"             # Fundo claro
COR_BRANCO = "#ffffff"            # Branco
COR_BORDA = "#e2e8f0"             # Bordas
COR_TEXTO_PRINCIPAL = "#1a202c"   # Texto principal
COR_TEXTO_SECUNDARIO = "#4a5568"  # Texto secundário

# Cores para gráficos - mais suaves
CORES_GRADIENTE = [
    COR_AZUL_ESCURO,
    COR_AZUL_MEDIO,
    COR_AZUL_CLARO,
    COR_VERDE_CORPORATIVO,
    COR_LARANJA_SUAVE,
    "#5a67d8"
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
# CSS PERSONALIZADO - ESTILO EXECUTIVO
# ============================================
st.markdown(f"""
<style>
    /* Reset e estilos base */
    .stApp {{
        background-color: {COR_FUNDO};
    }}
    
    /* Main header - executivo */
    .main-header {{
        background: {COR_BRANCO};
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid {COR_BORDA};
        border-radius: 0;
    }}
    
    /* Cards de métricas - mais compactos */
    .metric-card {{
        background: {COR_BRANCO};
        padding: 0.8rem 1rem;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
        border: 1px solid {COR_BORDA};
        margin-bottom: 0.8rem;
        transition: none;
    }}
    
    .metric-card:hover {{
        border-color: {COR_AZUL_CLARO};
    }}
    
    .metric-value {{
        font-size: 1.4rem;
        font-weight: 600;
        color: {COR_AZUL_ESCURO};
        margin: 0;
        line-height: 1.2;
    }}
    
    .metric-label {{
        font-size: 0.7rem;
        color: {COR_CINZA_CLARO};
        margin: 0.3rem 0 0 0;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }}
    
    /* Títulos de seção - mais discretos */
    .section-title {{
        color: {COR_AZUL_ESCURO};
        border-left: 3px solid {COR_AZUL_MEDIO};
        padding-left: 0.8rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {COR_BRANCO};
        border-right: 1px solid {COR_BORDA};
    }}
    
    .sidebar-section {{
        background: {COR_FUNDO};
        padding: 0.8rem;
        border-radius: 6px;
        margin-bottom: 0.8rem;
        border: 1px solid {COR_BORDA};
        font-size: 0.8rem;
    }}
    
    /* Informações da base */
    .info-base {{
        background: {COR_FUNDO};
        padding: 0.8rem;
        border-radius: 6px;
        border-left: 3px solid {COR_AZUL_MEDIO};
        margin-bottom: 1rem;
        font-size: 0.8rem;
    }}
    
    /* Rodapé */
    .footer {{
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid {COR_BORDA};
        color: {COR_CINZA_CLARO};
        font-size: 0.7rem;
    }}
    
    /* Status cards */
    .status-success {{
        background: #f0fff4;
        border-left: 3px solid {COR_VERDE_CORPORATIVO};
        padding: 0.5rem;
        border-radius: 6px;
        font-size: 0.8rem;
    }}
    
    .status-warning {{
        background: #fffbeb;
        border-left: 3px solid {COR_LARANJA_SUAVE};
        padding: 0.5rem;
        border-radius: 6px;
        font-size: 0.8rem;
    }}
    
    .status-danger {{
        background: #fff5f5;
        border-left: 3px solid {COR_VERMELHO_SUAVE};
        padding: 0.5rem;
        border-radius: 6px;
        font-size: 0.8rem;
    }}
    
    /* Botões */
    .stButton > button {{
        background: {COR_AZUL_ESCURO};
        color: {COR_BRANCO};
        border: none;
        border-radius: 4px;
        padding: 0.4rem 0.8rem;
        font-weight: 500;
        font-size: 0.8rem;
        transition: all 0.2s ease;
    }}
    
    .stButton > button:hover {{
        background: {COR_AZUL_MEDIO};
        box-shadow: 0 2px 6px rgba(26, 42, 58, 0.2);
    }}
    
    /* Badges */
    .badge-success {{
        background-color: {COR_VERDE_CORPORATIVO};
        color: {COR_BRANCO};
        padding: 0.15rem 0.6rem;
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 600;
    }}
    
    .badge-warning {{
        background-color: {COR_LARANJA_SUAVE};
        color: {COR_BRANCO};
        padding: 0.15rem 0.6rem;
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 600;
    }}
    
    .badge-danger {{
        background-color: {COR_VERMELHO_SUAVE};
        color: {COR_BRANCO};
        padding: 0.15rem 0.6rem;
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 600;
    }}
    
    .badge-info {{
        background-color: {COR_AZUL_MEDIO};
        color: {COR_BRANCO};
        padding: 0.15rem 0.6rem;
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 600;
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

def criar_card_indicador_simples(valor, label, icone="▎"):
    """Cria card de indicador SIMPLES - sem delta - com ícones mais discretos"""
    if isinstance(valor, (int, float)):
        valor_formatado = f"{valor:,}"
    else:
        valor_formatado = str(valor)
    
    return f'''
    <div class="metric-card">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.2rem; color: {COR_AZUL_MEDIO}; opacity: 0.7;">{icone}</span>
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
            'Motivo Revisão': 'Motivo_Revisao'
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
    """Cria popup modal com indicadores principais - versão executiva"""
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
        texto_principal = f"SRE validou {cards_validados} cards sem retorno de erro"
        subtexto = f"Performance excepcional em {nome_mes_pt} - 100% de aprovação direta"
        cor_destaque = COR_VERDE_CORPORATIVO
    elif taxa_erro <= 5:
        texto_principal = f"SRE validou {cards_validados} cards com {cards_com_erro} ajustes"
        subtexto = f"Alta qualidade em {nome_mes_pt} - Taxa de erro: {taxa_erro:.1f}%"
        cor_destaque = COR_AZUL_MEDIO
    else:
        texto_principal = f"SRE validou {cards_validados} cards, {cards_com_erro} com retorno"
        subtexto = f"Análise de {nome_mes_pt} - {taxa_sucesso:.1f}% de taxa de sucesso"
        cor_destaque = COR_LARANJA_SUAVE
    
    popup_html = f'''
    <div id="popupOverlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(0, 0, 0, 0.5); z-index: 10000; display: flex; 
                justify-content: center; align-items: center;">
        <div style="background: {COR_BRANCO}; width: 90%; max-width: 850px; max-height: 85vh;
                    border-radius: 8px; padding: 0; overflow: hidden; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            
            <div style="background: {COR_AZUL_ESCURO}; padding: 1rem 1.5rem; color: {COR_BRANCO};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="margin: 0; font-size: 1.1rem; font-weight: 600; letter-spacing: 0.5px;">
                            RELATÓRIO EXECUTIVO
                        </h2>
                        <p style="margin: 0.2rem 0 0 0; opacity: 0.8; font-size: 0.8rem;">
                            {nome_mes_pt} {ano_atual} | Resumo de Performance
                        </p>
                    </div>
                    <button onclick="document.getElementById('popupOverlay').style.display='none'" 
                            style="background: rgba(255,255,255,0.1); color: {COR_BRANCO}; 
                                   border: none; width: 32px; height: 32px; 
                                   border-radius: 50%; font-size: 1.2rem; 
                                   cursor: pointer;">×</button>
                </div>
            </div>
            
            <div style="padding: 1.5rem;">
                <div style="background: {cor_destaque}08; padding: 1rem; border-radius: 6px; 
                            border-left: 3px solid {cor_destaque}; margin-bottom: 1.5rem;">
                    <p style="color: {COR_TEXTO_PRINCIPAL}; margin: 0 0 0.3rem 0; font-size: 0.9rem; font-weight: 600;">
                        {texto_principal}
                    </p>
                    <p style="color: {COR_CINZA_CLARO}; margin: 0; font-size: 0.8rem;">{subtexto}</p>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; margin-bottom: 1.5rem;">
                    <div style="background: {COR_FUNDO}; padding: 0.8rem; border-radius: 6px; border-top: 2px solid {COR_AZUL_ESCURO};">
                        <div style="font-size: 1.2rem; font-weight: 600; color: {COR_AZUL_ESCURO};">
                            {total_cards_mes}
                        </div>
                        <div style="font-size: 0.65rem; color: {COR_CINZA_CLARO}; text-transform: uppercase; letter-spacing: 0.3px;">
                            Total de Cards
                        </div>
                    </div>
                    
                    <div style="background: {COR_FUNDO}; padding: 0.8rem; border-radius: 6px; border-top: 2px solid {COR_VERDE_CORPORATIVO};">
                        <div style="font-size: 1.2rem; font-weight: 600; color: {COR_VERDE_CORPORATIVO};">
                            {cards_validados}
                        </div>
                        <div style="font-size: 0.65rem; color: {COR_CINZA_CLARO}; text-transform: uppercase; letter-spacing: 0.3px;">
                            Validados
                        </div>
                        <div style="font-size: 0.6rem; color: {COR_CINZA_CLARO}; margin-top: 0.2rem;">
                            {variacao:+.1f}% vs mês anterior
                        </div>
                    </div>
                    
                    <div style="background: {COR_FUNDO}; padding: 0.8rem; border-radius: 6px; border-top: 2px solid {COR_AZUL_MEDIO};">
                        <div style="font-size: 1.2rem; font-weight: 600; color: {COR_AZUL_MEDIO};">
                            {cards_sem_erro}
                        </div>
                        <div style="font-size: 0.65rem; color: {COR_CINZA_CLARO}; text-transform: uppercase; letter-spacing: 0.3px;">
                            Sem retorno
                        </div>
                    </div>
                    
                    <div style="background: {COR_FUNDO}; padding: 0.8rem; border-radius: 6px; border-top: 2px solid {COR_VERMELHO_SUAVE if cards_com_erro > 0 else COR_CINZA_CLARO};">
                        <div style="font-size: 1.2rem; font-weight: 600; color: {COR_VERMELHO_SUAVE if cards_com_erro > 0 else COR_CINZA_CLARO};">
                            {cards_com_erro}
                        </div>
                        <div style="font-size: 0.65rem; color: {COR_CINZA_CLARO}; text-transform: uppercase; letter-spacing: 0.3px;">
                            Com retorno
                        </div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1rem;">
                    <div style="background: {COR_FUNDO}; padding: 0.8rem; border-radius: 6px;">
                        <h4 style="color: {COR_TEXTO_PRINCIPAL}; margin: 0 0 0.8rem 0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.3px;">
                            Evolução Mensal
                        </h4>
                        <div style="height: 120px; display: flex; align-items: end; gap: 30px;">
                            <div style="text-align: center; flex: 1;">
                                <div style="background: {COR_CINZA_CLARO}; height: {max(10, min(80, cards_validados_anterior/3))}px; 
                                            border-radius: 3px 3px 0 0; width: 40px; margin: 0 auto;"></div>
                                <div style="margin-top: 6px; font-size: 0.65rem; color: {COR_CINZA_CLARO};">
                                    {mes_anterior:02d}/{ano_anterior}
                                </div>
                                <div style="font-weight: 600; font-size: 0.75rem; color: {COR_TEXTO_PRINCIPAL};">{cards_validados_anterior}</div>
                            </div>
                            <div style="text-align: center; flex: 1;">
                                <div style="background: {COR_VERDE_CORPORATIVO}; height: {max(10, min(80, cards_validados/3))}px; 
                                            border-radius: 3px 3px 0 0; width: 40px; margin: 0 auto;"></div>
                                <div style="margin-top: 6px; font-size: 0.65rem; color: {COR_CINZA_CLARO};">
                                    {mes_atual:02d}/{ano_atual}
                                </div>
                                <div style="font-weight: 600; font-size: 0.75rem; color: {COR_TEXTO_PRINCIPAL};">{cards_validados}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: #fffbeb; padding: 0.8rem; border-radius: 6px; border-left: 3px solid {COR_LARANJA_SUAVE};">
                        <h4 style="color: {COR_LARANJA_SUAVE}; margin: 0 0 0.6rem 0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.3px;">
                            Insights
                        </h4>
                        <ul style="color: {COR_CINZA_CLARO}; padding-left: 1rem; margin: 0; font-size: 0.75rem; list-style-type: none;">
                            <li style="margin-bottom: 0.3rem;">
                                {f"Recorde de validações" if variacao > 20 else "Performance consistente"}
                            </li>
                            <li style="margin-bottom: 0.3rem;">
                                {f"Qualidade excepcional" if cards_com_erro == 0 else f"{cards_sem_erro} cards perfeitos"}
                            </li>
                            <li>
                                {f"Meta: {taxa_sucesso:.0f}% de sucesso" if taxa_sucesso >= 90 else f"Oportunidade: melhorar {100-taxa_sucesso:.0f}%"}
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div style="background: {COR_FUNDO}; padding: 0.8rem 1.5rem; border-top: 1px solid {COR_BORDA};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <p style="color: {COR_CINZA_CLARO}; margin: 0; font-size: 0.65rem;">
                        Atualizado em {hoje.strftime('%d/%m/%Y %H:%M')}
                    </p>
                    <button onclick="document.getElementById('popupOverlay').style.display='none'"
                            style="background: {COR_AZUL_ESCURO}; color: {COR_BRANCO}; border: none; 
                                   padding: 0.4rem 1rem; border-radius: 4px; 
                                   cursor: pointer; font-weight: 500; font-size: 0.8rem;">
                        Fechar
                    </button>
                </div>
            </div>
        </div>
    </div>
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
    Retorna cor em hex interpolando entre azul médio e vermelho suave.
    """
    if max_val == min_val:
        return COR_AZUL_MEDIO

    t = (valor - min_val) / (max_val - min_val)

    cor_baixo = (44, 82, 130)    # #2c5282
    cor_medio = (192, 86, 33)    # #c05621
    cor_alto  = (155, 44, 44)    # #9b2c2c

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
    """Cria mapa Folium interativo - versão executiva"""
    try:
        import folium
    except ImportError:
        st.error("Biblioteca 'folium' não instalada")
        return None
    
    if df_mapa.empty:
        return None

    df_bolhas = df_mapa[df_mapa['sincronismos'] > 0].copy()

    m = folium.Map(
        location=[-14.5, -51.5],
        zoom_start=4,
        tiles=None,
        prefer_canvas=True
    )

    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='OpenStreetMap contributors & CARTO',
        name='CartoDB Positron',
        max_zoom=19,
        subdomains='abcd'
    ).add_to(m)

    if df_bolhas.empty:
        return m

    max_sinc = df_bolhas['sincronismos'].max()
    min_sinc = df_bolhas['sincronismos'].min()
    total = df_bolhas['sincronismos'].sum()

    R_MIN, R_MAX = 15, 55

    def raio(v):
        if max_sinc == min_sinc:
            return (R_MIN + R_MAX) / 2
        return R_MIN + (v - min_sinc) / (max_sinc - min_sinc) * (R_MAX - R_MIN)

    for _, row in df_bolhas.iterrows():
        cor = cor_gradiente_folium(row['sincronismos'], min_sinc, max_sinc)
        r = raio(row['sincronismos'])
        pct = row['sincronismos'] / total * 100 if total > 0 else 0

        tooltip_html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; padding: 8px; min-width: 180px;">
            <div style="font-weight: 700; font-size: 13px; color: {COR_AZUL_ESCURO};">
                {row['empresa_nome']}
            </div>
            <div style="margin-top: 4px; font-size: 11px; color: {COR_CINZA_CLARO};">
                {row['estado']} ({row['sigla']}) • {row['regiao']}
            </div>
            <div style="border-top: 1px solid {COR_BORDA}; margin: 6px 0; padding-top: 6px;">
                <span style="font-weight: 700; font-size: 18px; color: {cor};">{row['sincronismos']:,}</span>
                <span style="font-size: 11px; color: {COR_CINZA_CLARO};"> sincronizações</span>
            </div>
            <div style="font-size: 11px; color: {COR_CINZA_CLARO};">
                {pct:.1f}% do total
            </div>
        </div>
        """

        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=r,
            color=COR_BRANCO,
            weight=2,
            fill=True,
            fill_color=cor,
            fill_opacity=0.85,
            tooltip=folium.Tooltip(tooltip_html, sticky=True),
        ).add_to(m)

        # Label dentro da bolha
        font_size_sigla = max(8, min(13, int(r * 0.4)))
        font_size_num = max(7, min(11, int(r * 0.32)))
        
        label_html = f"""
        <div style="
            font-family: 'Segoe UI', sans-serif;
            text-align: center;
            font-weight: 700;
            line-height: 1.2;
            white-space: nowrap;
        ">
            <div style="
                font-size: {font_size_sigla}px;
                color: white;
                text-shadow: 0 1px 2px rgba(0,0,0,0.5);
            ">{row['empresa']}</div>
            <div style="
                font-size: {font_size_num}px;
                color: white;
                text-shadow: 0 1px 2px rgba(0,0,0,0.4);
                font-weight: 600;
            ">{row['sincronismos']}</div>
        </div>
        """

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            icon=folium.DivIcon(
                html=label_html,
                icon_size=(int(r * 1.6), int(r * 1.6)),
                icon_anchor=(int(r * 0.8), int(r * 0.8)),
            )
        ).add_to(m)

    # Legenda simplificada
    legenda_html = f"""
    <div style="
        position: fixed;
        bottom: 20px;
        left: 15px;
        z-index: 9999;
        background: white;
        border-radius: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        padding: 10px 14px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 10px;
        border: 1px solid {COR_BORDA};
    ">
        <div style="font-weight: 600; color: {COR_AZUL_ESCURO}; margin-bottom: 6px; font-size: 9px; text-transform: uppercase; letter-spacing: 0.3px;">
            Volume de Sincronizações
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
            <div style="width: 100px; height: 8px; border-radius: 4px;
                        background: linear-gradient(to right, {COR_AZUL_MEDIO}, {COR_LARANJA_SUAVE}, {COR_VERMELHO_SUAVE});
                        border: 1px solid {COR_BORDA};"></div>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top: 4px; color: {COR_CINZA_CLARO};">
            <span>Menor</span>
            <span>Maior</span>
        </div>
    </div>
    """

    m.get_root().html.add_child(folium.Element(legenda_html))

    return m


def criar_grafico_barras(df_mapa):
    """Cria gráfico de barras comparativo - versão executiva"""
    if df_mapa.empty:
        return None
    
    df_barras = df_mapa.sort_values('sincronismos', ascending=False).reset_index(drop=True)
    total = df_barras['sincronismos'].sum()
    
    fig = go.Figure()
    
    max_val = df_barras['sincronismos'].max()
    min_val = df_barras['sincronismos'].min()
    
    for idx, row in df_barras.iterrows():
        if max_val == min_val:
            cor = COR_AZUL_MEDIO
        else:
            normalized = (row['sincronismos'] - min_val) / (max_val - min_val)
            if normalized < 0.5:
                tt = normalized / 0.5
                r = int(44 + tt * (192 - 44))
                g = int(82 + tt * (86 - 82))
                b = int(130 + tt * (33 - 130))
            else:
                tt = (normalized - 0.5) / 0.5
                r = int(192 + tt * (155 - 192))
                g = int(86 + tt * (44 - 86))
                b = int(33 + tt * (44 - 33))
            cor = f'rgb({r}, {g}, {b})'
        
        percentual = (row['sincronismos'] / total * 100) if total > 0 else 0
        
        fig.add_trace(go.Bar(
            x=[row['sincronismos']],
            y=[f"{row['empresa']}"],
            orientation='h',
            text=[f"{row['sincronismos']:,}"],
            textposition='outside',
            marker_color=cor,
            marker_line_color=COR_AZUL_ESCURO,
            marker_line_width=0.5,
            hovertemplate=f"<b>{row['empresa_nome']}</b><br>" +
                          f"Sincronizações: {row['sincronismos']:,}<br>" +
                          f"Percentual: {percentual:.1f}%<br>" +
                          f"Estado: {row['estado']}<br>" +
                          f"Região: {row['regiao']}<extra></extra>",
            name=row['empresa']
        ))
    
    fig.update_layout(
        title=dict(
            text="Ranking de Sincronizações",
            font=dict(size=12, color=COR_AZUL_ESCURO),
            x=0.5
        ),
        xaxis_title="Número de Sincronizações",
        yaxis_title="",
        height=350,
        showlegend=False,
        plot_bgcolor=COR_BRANCO,
        xaxis=dict(
            gridcolor=COR_BORDA,
            tickformat="d",
            title_font=dict(size=10)
        ),
        yaxis=dict(
            gridcolor=COR_BORDA,
            tickfont=dict(size=10),
            categoryorder='total ascending'
        ),
        margin=dict(l=10, r=60, t=40, b=10),
        hovermode='closest'
    )
    
    return fig


# ============================================
# SIDEBAR - FILTROS E CONTROLES
# ============================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 0.8rem 0;">
        <h4 style="color: {COR_AZUL_ESCURO}; margin: 0; font-size: 1rem;">Painel de Controle</h4>
        <p style="color: {COR_CINZA_CLARO}; margin: 0; font-size: 0.7rem;">Filtros e Configurações</p>
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
            st.markdown("**Filtros de Análise**")
            
            df = st.session_state.df_original.copy()
            
            if 'Ano' in df.columns:
                anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                if anos_disponiveis:
                    anos_opcoes = ['Todos os Anos'] + list(anos_disponiveis)
                    ano_selecionado = st.selectbox(
                        "Ano",
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
                        "Mês",
                        options=meses_opcoes,
                        key="filtro_mes"
                    )
                    if mes_selecionado != 'Todos os Meses':
                        df = df[df['Mês'] == int(mes_selecionado)]
            
            if 'Responsável_Formatado' in df.columns:
                responsaveis = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
                responsavel_selecionado = st.selectbox(
                    "Responsável",
                    options=responsaveis,
                    key="filtro_responsavel"
                )
                if responsavel_selecionado != 'Todos':
                    df = df[df['Responsável_Formatado'] == responsavel_selecionado]
            
            busca_chamado = st.text_input(
                "Buscar Chamado",
                placeholder="Número do chamado...",
                key="busca_chamado"
            )
            if busca_chamado:
                df = df[df['Chamado'].astype(str).str.contains(busca_chamado, na=False)]
            
            if 'Status' in df.columns:
                status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox(
                    "Status",
                    options=status_opcoes,
                    key="filtro_status"
                )
                if status_selecionado != 'Todos':
                    df = df[df['Status'] == status_selecionado]
            
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos'] + sorted(df['Tipo_Chamado'].dropna().unique())
                tipo_selecionado = st.selectbox(
                    "Tipo de Chamado",
                    options=tipos,
                    key="filtro_tipo"
                )
                if tipo_selecionado != 'Todos':
                    df = df[df['Tipo_Chamado'] == tipo_selecionado]
            
            if 'Empresa' in df.columns:
                empresas = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                empresa_selecionada = st.selectbox(
                    "Empresa",
                    options=empresas,
                    key="filtro_empresa"
                )
                if empresa_selecionada != 'Todas':
                    df = df[df['Empresa'] == empresa_selecionada]
            
            if 'SRE' in df.columns:
                sres = ['Todos'] + sorted(df['SRE'].dropna().unique())
                sre_selecionado = st.selectbox(
                    "SRE Responsável",
                    options=sres,
                    key="filtro_sre"
                )
                if sre_selecionado != 'Todos':
                    df = df[df['SRE'] == sre_selecionado]
            
            st.session_state.df_filtrado = df
            
            st.markdown(f"**Registros filtrados:** {len(df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**Controles**")
        
        if st.session_state.df_original is not None:
            arquivo_atual = st.session_state.arquivo_atual
            
            if arquivo_atual and isinstance(arquivo_atual, str) and os.path.exists(arquivo_atual):
                tamanho_kb = os.path.getsize(arquivo_atual) / 1024
                ultima_mod = datetime.fromtimestamp(os.path.getmtime(arquivo_atual))
                
                st.markdown(f"""
                <div style="background: {COR_FUNDO}; padding: 0.5rem; border-radius: 6px; margin-bottom: 0.8rem; font-size: 0.75rem;">
                    <p style="margin: 0 0 0.2rem 0; font-weight: 600;">Arquivo atual:</p>
                    <p style="margin: 0; color: {COR_TEXTO_PRINCIPAL};">{os.path.basename(arquivo_atual)}</p>
                    <p style="margin: 0.2rem 0 0 0; color: {COR_CINZA_CLARO};">
                    {tamanho_kb:.1f} KB • {ultima_mod.strftime('%d/%m/%Y %H:%M')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if verificar_e_atualizar_arquivo():
                    st.warning("Arquivo local modificado!")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("Recarregar", use_container_width=True, key="btn_recarregar"):
                    
                    caminho_atual = encontrar_arquivo_dados()
                    
                    if caminho_atual and os.path.exists(caminho_atual):
                        with st.spinner('Recarregando...'):
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
                                    
                                    st.success(f"Dados atualizados! {len(df_atualizado):,} registros")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"Erro: {status}")
                            except Exception as e:
                                st.error(f"Erro: {str(e)}")
                    else:
                        st.error("Arquivo local não encontrado.")
            
            with col_btn2:
                if st.button("Limpar", use_container_width=True, key="btn_limpar"):
                    
                    st.cache_data.clear()
                    
                    limpar_sessao_dados()
                    
                    st.success("Dados limpos!")
                    time.sleep(1)
                    st.rerun()
            
            st.markdown("---")
        
        st.markdown("**Importar Dados**")
        
        if st.session_state.df_original is not None:
            ultima_atualizacao = st.session_state.get('ultima_atualizacao', get_horario_brasilia())
            st.markdown(f"""
            <div class="status-success">
                <small>Registros: {len(st.session_state.df_original):,}</small><br>
                <small>Atualizado: {ultima_atualizacao}</small>
            </div>
            """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Selecione um arquivo CSV",
            type=['csv'],
            key="file_uploader",
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
            
            if st.button("Processar", use_container_width=True, key="btn_processar"):
                with st.spinner('Processando...'):
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
                        
                        st.success(f"{len(df_novo):,} registros carregados!")
                        
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"{status}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.df_original is None:
        caminho_encontrado = encontrar_arquivo_dados()
        
        if caminho_encontrado:
            with st.spinner('Carregando dados...'):
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
                    st.error(f"{status}")

# ============================================
# HEADER - ESTILO EXECUTIVO
# ============================================
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
        <div>
            <h1 style="
                color: {COR_AZUL_ESCURO};
                margin: 0;
                font-size: 1.3rem;
                font-weight: 600;
                letter-spacing: -0.3px;
            ">
                ESTEIRA ADMS
            </h1>
            <p style="
                color: {COR_CINZA_CLARO};
                margin: 0.2rem 0 0 0;
                font-size: 0.75rem;
                font-weight: 400;
            ">
                Acompanhamento de Demandas - Energisa Group
            </p>
        </div>
        <div style="text-align: right;">
            <p style="
                color: {COR_CINZA_CLARO};
                margin: 0;
                font-size: 0.7rem;
                font-weight: 500;
            ">
                v5.5
            </p>
            <p style="
                color: {COR_CINZA_CLARO};
                margin: 0.2rem 0 0 0;
                font-size: 0.65rem;
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
    
    col_btn_manchete, col_espaco = st.columns([1, 11])
    
    with col_btn_manchete:
        if st.button("Ver Relatório", 
                    help="Clique para ver os principais indicadores",
                    type="secondary",
                    use_container_width=True,
                    key="btn_manchete"):
            st.session_state.show_popup = True

if st.session_state.df_original is not None:
    if verificar_e_atualizar_arquivo():
        st.info("Arquivo local foi atualizado!")

if st.session_state.df_original is not None and st.session_state.show_popup:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    with st.expander("RELATÓRIO EXECUTIVO", expanded=True):
        
        st.markdown("### Resumo de Performance")
        st.markdown("---")
        
        st.markdown("#### Período de Análise")
        
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
                "Selecione o período:",
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
                        options=['Selecionar...'] + list(anos_disponiveis),
                        key="popup_ano"
                    )
                else:
                    ano_especifico = 'Selecionar...'
            else:
                ano_especifico = 'Selecionar...'
        
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
            periodo_titulo = "Todo o Período"
            
        elif ano_especifico != 'Selecionar...':
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
        
        st.markdown(f"#### Destaque: {periodo_titulo}")
        
        if total_cards == 0:
            st.error(f"Nenhum dado disponível para {periodo_titulo.lower()}")
        elif com_erro == 0 and validados > 0:
            st.success(f"SRE validou {validados} cards sem retorno de erro")
            st.info("Performance excepcional - 100% de aprovação direta")
        elif taxa_erro <= 5:
            st.warning(f"SRE validou {validados} cards com {com_erro} ajustes")
            st.info(f"Taxa de erro: {taxa_erro:.1f}%")
        else:
            st.warning(f"SRE validou {validados} cards, {com_erro} com retorno")
            st.info(f"Taxa de sucesso: {taxa_sucesso:.1f}% | {sem_erro} cards perfeitos")
        
        st.markdown("---")
        
        if not df_anterior.empty and total_cards_anterior > 0:
            st.markdown("#### Comparação com Período Anterior")
            
            periodos = [periodo_anterior_titulo, periodo_titulo]
            cards_totais = [total_cards_anterior, total_cards]
            cards_validados = [validados_anterior, validados]
            taxa_sucesso_vals = [taxa_sucesso_anterior, taxa_sucesso]
            
            fig_comparativo = go.Figure()
            
            fig_comparativo.add_trace(go.Bar(
                x=periodos,
                y=cards_totais,
                name='Total Cards',
                marker_color=COR_AZUL_MEDIO,
                text=cards_totais,
                textposition='outside',
                textfont=dict(size=9),
                width=0.35
            ))
            
            fig_comparativo.add_trace(go.Bar(
                x=periodos,
                y=cards_validados,
                name='Validados',
                marker_color=COR_VERDE_CORPORATIVO,
                text=cards_validados,
                textposition='outside',
                textfont=dict(size=9),
                width=0.35
            ))
            
            fig_comparativo.add_trace(go.Scatter(
                x=periodos,
                y=taxa_sucesso_vals,
                name='Taxa Sucesso',
                yaxis='y2',
                mode='lines+markers+text',
                line=dict(color=COR_LARANJA_SUAVE, width=2),
                marker=dict(size=6, color=COR_LARANJA_SUAVE),
                text=[f"{v:.1f}%" for v in taxa_sucesso_vals],
                textposition='top center',
                textfont=dict(size=8)
            ))
            
            fig_comparativo.update_layout(
                title=dict(
                    text='Comparativo de Performance',
                    font=dict(size=11)
                ),
                barmode='group',
                yaxis=dict(
                    title=dict(text='Quantidade', font=dict(size=9)),
                    gridcolor='rgba(0,0,0,0.05)',
                    rangemode='tozero'
                ),
                yaxis2=dict(
                    title=dict(text='Taxa Sucesso (%)', font=dict(size=9)),
                    overlaying='y',
                    side='right',
                    range=[0, max(100, max(taxa_sucesso_vals) * 1.1)],
                    gridcolor='rgba(0,0,0,0.02)'
                ),
                height=250,
                showlegend=True,
                plot_bgcolor=COR_BRANCO,
                margin=dict(l=40, r=40, t=40, b=30),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=8)
                ),
                xaxis=dict(tickfont=dict(size=9))
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
            
            st.markdown("#### Variação")
            
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
        
        st.markdown("#### Indicadores")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Cards", 
                total_cards,
                delta=None
            )
        
        with col2:
            st.metric(
                "Validados", 
                validados,
                f"{taxa_sucesso:.1f}%"
            )
        
        with col3:
            st.metric(
                "Sem Erro", 
                sem_erro,
                f"{(sem_erro/validados*100) if validados>0 else 0:.1f}%" if validados > 0 else "0%"
            )
        
        with col4:
            st.metric(
                "Com Erro", 
                com_erro,
                f"{taxa_erro:.1f}%" if validados > 0 else "0%"
            )
        
        st.markdown("---")
        st.markdown("#### Análise")
        
        if total_cards > 0:
            if 'Criado' in df_filtrado_periodo.columns and len(df_filtrado_periodo) > 0:
                dias_unicos = df_filtrado_periodo['Criado'].dt.date.nunique()
                media_diaria = total_cards / dias_unicos if dias_unicos > 0 else 0
                
                col_analise1, col_analise2, col_analise3 = st.columns(3)
                
                with col_analise1:
                    st.metric("Dias com atividade", dias_unicos)
                
                with col_analise2:
                    st.metric("Média diária", f"{media_diaria:.1f}")
                
                with col_analise3:
                    if 'Revisões' in df_filtrado_periodo.columns:
                        media_revisoes = df_filtrado_periodo['Revisões'].mean()
                        st.metric("Média revisões/card", f"{media_revisoes:.1f}")
                    else:
                        st.metric("Revisões", "N/A")
            
            st.markdown("#### Classificação")
            
            if taxa_sucesso >= 95:
                st.success("""
                **Excelente**
                - Meta de qualidade superada (>95%)
                - Processos altamente eficientes
                - Manter padrões atuais
                """)
            elif taxa_sucesso >= 85:
                st.info("""
                **Bom Desempenho**
                - Dentro dos padrões esperados (85-94%)
                - Processos consistentes
                - Pequenos ajustes pontuais
                """)
            elif taxa_sucesso >= 70:
                st.warning("""
                **Oportunidade de Melhoria**
                - Abaixo do ideal (70-84%)
                - Identificar causas principais
                """)
            else:
                st.error("""
                **Atenção Necessária**
                - Performance crítica (<70%)
                - Revisão urgente dos fluxos
                """)
        else:
            st.info(f"Nenhum dado disponível para análise em: {periodo_titulo}")
        
        st.markdown("---")
        
        st.markdown(f"""
        <div style="background: {COR_FUNDO}; padding: 0.8rem; border-radius: 6px; border: 1px solid {COR_BORDA};">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                <div>
                    <p style="margin: 0; color: {COR_TEXTO_PRINCIPAL}; font-weight: 600; font-size: 0.75rem;">Ações</p>
                    <p style="margin: 0.2rem 0 0 0; color: {COR_CINZA_CLARO}; font-size: 0.7rem;">
                    Exporte ou feche o relatório
                    </p>
                </div>
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                    <button onclick="document.getElementById('exportBtn').click()" 
                            style="background: {COR_VERDE_CORPORATIVO}; color: {COR_BRANCO}; border: none; 
                                   padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer; 
                                   font-weight: 500; font-size: 0.75rem;">
                        Exportar
                    </button>
                    <button onclick="document.getElementById('closeBtn').click()" 
                            style="background: {COR_CINZA_CLARO}; color: {COR_BRANCO}; border: none; 
                                   padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer; 
                                   font-weight: 500; font-size: 0.75rem;">
                        Fechar
                    </button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_exportar, col_fechar = st.columns(2)
        
        with col_exportar:
            if st.button("Exportar PDF", 
                        type="primary", 
                        use_container_width=True,
                        key="btn_exportar_pdf_final"):
                st.info("PDF - Em desenvolvimento")
        
        with col_fechar:
            if st.button("Fechar", 
                        type="secondary",
                        use_container_width=True,
                        key="btn_fechar_final"):
                st.session_state.show_popup = False
                st.rerun()
        
        st.markdown(f"""
        <div style="background: {COR_FUNDO}; padding: 0.5rem; border-radius: 4px; margin-top: 0.8rem; font-size: 0.65rem;">
            <strong>Período:</strong> {periodo_titulo}<br>
            <strong>Atualizado:</strong> {hoje.strftime('%d/%m/%Y %H:%M')}<br>
            <strong>Base:</strong> {len(df):,} registros
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
    tab_principal, tab_mapa, tab_ipe, tab_estatistica = st.tabs(["Principal", "Mapa", "KPI", "Análise"])
    
    with tab_principal:
        st.markdown("### Base de Dados")
        
        if 'Criado' in df.columns and not df.empty:
            data_min = df['Criado'].min()
            data_max = df['Criado'].max()
            
            st.markdown(f"""
            <div class="info-base">
                <p style="margin: 0; font-weight: 600;">Base atualizada em: {get_horario_brasilia()}</p>
                <p style="margin: 0.2rem 0 0 0; color: {COR_CINZA_CLARO};">
                Período: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')} • 
                Total: {len(df):,} registros
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### Indicadores")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_atual = len(df)
            st.markdown(criar_card_indicador_simples(
                total_atual, 
                "Total de Demandas", 
                "▎"
            ), unsafe_allow_html=True)
        
        with col2:
            if 'Status' in df.columns:
                sincronizados = len(df[df['Status'] == 'Sincronizado'])
                st.markdown(criar_card_indicador_simples(
                    sincronizados,
                    "Sincronizados",
                    "▎"
                ), unsafe_allow_html=True)
        
        with col3:
            if 'Revisões' in df.columns:
                total_revisoes = int(df['Revisões'].sum())
                st.markdown(criar_card_indicador_simples(
                    total_revisoes,
                    "Total de Revisões",
                    "▎"
                ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "Evolução", 
            "Revisões", 
            "Sincronizações",
            "SRE"
        ])
        
        with tab1:
            st.markdown(f'<div class="section-title">Evolução Mensal</div>', unsafe_allow_html=True)
            
            col_titulo, col_seletor = st.columns([3, 1])
            
            with col_seletor:
                if 'Ano' in df.columns:
                    anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                    if anos_disponiveis:
                        ano_selecionado = st.selectbox(
                            "Ano:",
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
                        line=dict(color=COR_AZUL_ESCURO, width=2),
                        marker=dict(size=6, color=COR_AZUL_MEDIO),
                        text=demandas_completas['Quantidade'],
                        textposition='top center',
                        textfont=dict(size=8, color=COR_AZUL_ESCURO)
                    ))
                    
                    fig_mes.update_layout(
                        title=f"Demandas em {ano_selecionado}",
                        xaxis_title="Mês",
                        yaxis_title="Número de Demandas",
                        plot_bgcolor=COR_BRANCO,
                        height=350,
                        showlegend=False,
                        margin=dict(t=40, b=40, l=40, r=40),
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
                        text=f"Total: {total_ano:,} demandas",
                        showarrow=False,
                        font=dict(size=9, color=COR_AZUL_ESCURO, weight="bold"),
                        bgcolor="rgba(255,255,255,0.9)",
                        bordercolor=COR_AZUL_ESCURO,
                        borderwidth=1,
                        borderpad=4
                    )
                    
                    st.plotly_chart(fig_mes, use_container_width=True)
                    
                    col_stats1, col_stats2, col_stats3 = st.columns(3)
                    with col_stats1:
                        mes_max = demandas_completas.loc[demandas_completas['Quantidade'].idxmax()]
                        st.metric("Mês com mais demandas", f"{mes_max['Nome_Mês']}: {int(mes_max['Quantidade']):,}")
                    
                    with col_stats2:
                        mes_min = demandas_completas.loc[demandas_completas['Quantidade'].idxmin()]
                        st.metric("Mês com menos demandas", f"{mes_min['Nome_Mês']}: {int(mes_min['Quantidade']):,}")
                    
                    with col_stats3:
                        media_mensal = int(demandas_completas['Quantidade'].mean())
                        st.metric("Média mensal", f"{media_mensal:,}")
        
        with tab2:
            st.markdown(f'<div class="section-title">Revisões por Responsável</div>', unsafe_allow_html=True)
            
            col_rev_filtro1, col_rev_filtro2 = st.columns(2)
            
            with col_rev_filtro1:
                if 'Ano' in df.columns:
                    anos_rev = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_rev = ['Todos os Anos'] + list(anos_rev)
                    ano_rev = st.selectbox(
                        "Ano:",
                        options=anos_opcoes_rev,
                        key="filtro_ano_revisoes"
                    )
            
            with col_rev_filtro2:
                if 'Mês' in df.columns:
                    meses_rev = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_rev = ['Todos os Meses'] + [str(m) for m in meses_rev]
                    mes_rev = st.selectbox(
                        "Mês:",
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
                    
                    titulo_rev = 'Top 15 Responsáveis com Mais Revisões'
                    if ano_rev != 'Todos os Anos':
                        titulo_rev += f' - {ano_rev}'
                    if mes_rev != 'Todos os Meses':
                        meses_nomes = {
                            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                        }
                        titulo_rev += f' - {meses_nomes[int(mes_rev)]}'
                    
                    fig_revisoes = go.Figure()
                    
                    max_revisoes = revisoes_por_responsavel['Total_Revisões'].max()
                    min_revisoes = revisoes_por_responsavel['Total_Revisões'].min()
                    
                    colors = []
                    for valor in revisoes_por_responsavel['Total_Revisões']:
                        if max_revisoes == min_revisoes:
                            colors.append(COR_VERMELHO_SUAVE)
                        else:
                            normalized = (valor - min_revisoes) / (max_revisoes - min_revisoes)
                            red = int(155 * normalized + 44 * (1 - normalized))
                            green = int(44 * normalized + 82 * (1 - normalized))
                            blue = int(44 * normalized + 130 * (1 - normalized))
                            colors.append(f'rgb({red}, {green}, {blue})')
                    
                    fig_revisoes.add_trace(go.Bar(
                        x=revisoes_por_responsavel['Responsável'].head(15),
                        y=revisoes_por_responsavel['Total_Revisões'].head(15),
                        name='Total de Revisões',
                        text=revisoes_por_responsavel['Total_Revisões'].head(15),
                        textposition='outside',
                        marker_color=colors[:15],
                        marker_line_color=COR_TEXTO_PRINCIPAL,
                        marker_line_width=1,
                        opacity=0.8
                    ))
                    
                    fig_revisoes.update_layout(
                        title=titulo_rev,
                        xaxis_title='Responsável',
                        yaxis_title='Total de Revisões',
                        plot_bgcolor=COR_BRANCO,
                        height=400,
                        showlegend=False,
                        margin=dict(t=40, b=80, l=40, r=40),
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
            st.markdown(f'<div class="section-title">Sincronizações por Dia</div>', unsafe_allow_html=True)
            
            col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
            
            with col_filtro1:
                if 'Ano' in df.columns:
                    anos_sinc = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_sinc = ['Todos os Anos'] + list(anos_sinc)
                    ano_sinc = st.selectbox(
                        "Ano:",
                        options=anos_opcoes_sinc,
                        key="filtro_ano_sinc"
                    )
            
            with col_filtro2:
                if 'Mês' in df.columns:
                    meses_sinc = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_sinc = ['Todos os Meses'] + [str(m) for m in meses_sinc]
                    mes_sinc = st.selectbox(
                        "Mês:",
                        options=meses_opcoes_sinc,
                        key="filtro_mes_sinc"
                    )
            
            with col_filtro3:
                if 'SRE' in df.columns:
                    sres_sinc = ['Todos os SREs'] + sorted(df['SRE'].dropna().unique())
                    sre_sinc = st.selectbox(
                        "SRE:",
                        options=sres_sinc,
                        key="filtro_sre_sinc"
                    )
            
            with col_filtro4:
                if 'Empresa' in df.columns:
                    empresas_sinc = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                    empresa_sinc = st.selectbox(
                        "Empresa:",
                        options=empresas_sinc,
                        key="filtro_empresa_sinc"
                    )
            
            df_sinc = df.copy()
            
            if ano_sinc != 'Todos os Anos':
                df_sinc = df_sinc[df_sinc['Ano'] == int(ano_sinc)]
            
            if mes_sinc != 'Todos os Meses':
                df_sinc = df_sinc[df_sinc['Mês'] == int(mes_sinc)]
            
            if sre_sinc != 'Todos os SREs':
                df_sinc = df_sinc[df_sinc['SRE'] == sre_sinc]
            
            if empresa_sinc != 'Todas':
                df_sinc = df_sinc[df_sinc['Empresa'] == empresa_sinc]
            
            if 'Status' in df_sinc.columns and 'Criado' in df_sinc.columns:
                df_sincronizados = df_sinc[df_sinc['Status'] == 'Sincronizado'].copy()
                
                if not df_sincronizados.empty:
                    df_sincronizados['Data'] = df_sincronizados['Criado'].dt.date
                    
                    sincronizados_por_dia = df_sincronizados.groupby('Data').size().reset_index()
                    sincronizados_por_dia.columns = ['Data', 'Quantidade']
                    sincronizados_por_dia = sincronizados_por_dia.sort_values('Data')
                    
                    st.markdown("#### Indicadores")
                    
                    total_sincronizados = int(sincronizados_por_dia['Quantidade'].sum())
                    media_diaria = sincronizados_por_dia['Quantidade'].mean()
                    max_dia = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmax()]
                    min_dia = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmin()]
                    dias_trabalhados = len(sincronizados_por_dia)
                    
                    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
                    
                    with col_kpi1:
                        st.metric("Total Sincronizado", f"{total_sincronizados:,}")
                    
                    with col_kpi2:
                        st.metric("Média Diária", f"{media_diaria:.1f}")
                    
                    with col_kpi3:
                        st.metric("Melhor Dia", f"{int(max_dia['Quantidade']):,}")
                    
                    with col_kpi4:
                        st.metric("Dias Ativos", f"{dias_trabalhados}")
                    
                    st.markdown("#### Evolução Diária")
                    
                    if len(sincronizados_por_dia) > 30:
                        sinc_por_dia_recente = sincronizados_por_dia.tail(30)
                    else:
                        sinc_por_dia_recente = sincronizados_por_dia.copy()
                    
                    sinc_por_dia_recente['Data_Formatada'] = sinc_por_dia_recente['Data'].apply(lambda x: x.strftime('%d/%m'))
                    
                    fig_dias = go.Figure()
                    
                    max_quant = sinc_por_dia_recente['Quantidade'].max()
                    min_quant = sinc_por_dia_recente['Quantidade'].min()
                    
                    colors = []
                    for valor in sinc_por_dia_recente['Quantidade']:
                        if max_quant == min_quant:
                            colors.append(COR_AZUL_ESCURO)
                        else:
                            normalized = (valor - min_quant) / (max_quant - min_quant)
                            red = int(0 * normalized + 26 * (1 - normalized))
                            green = int(89 * normalized + 42 * (1 - normalized))
                            blue = int(115 * normalized + 58 * (1 - normalized))
                            colors.append(f'rgb({red}, {green}, {blue})')
                    
                    fig_dias.add_trace(go.Bar(
                        x=sinc_por_dia_recente['Data_Formatada'],
                        y=sinc_por_dia_recente['Quantidade'],
                        name='Sincronizações',
                        text=sinc_por_dia_recente['Quantidade'],
                        textposition='outside',
                        marker_color=colors,
                        marker_line_color=COR_AZUL_MEDIO,
                        marker_line_width=1,
                        opacity=0.8
                    ))
                    
                    fig_dias.update_layout(
                        title='Sincronizações por Dia (Últimos 30 dias)' if len(sincronizados_por_dia) > 30 else 'Sincronizações por Dia',
                        xaxis_title='Data (Dia/Mês)',
                        yaxis_title='Quantidade',
                        height=350,
                        plot_bgcolor=COR_BRANCO,
                        showlegend=False,
                        margin=dict(t=40, b=40, l=40, r=40),
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
                    
                    col_dia1, col_dia2, col_dia3 = st.columns(3)
                    
                    with col_dia1:
                        dia_max = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmax()]
                        st.metric("Melhor Dia", 
                                 dia_max['Data'].strftime('%d/%m/%Y'), 
                                 f"{int(dia_max['Quantidade'])} sinc.")
                    
                    with col_dia2:
                        dia_min = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmin()]
                        st.metric("Pior Dia", 
                                 dia_min['Data'].strftime('%d/%m/%Y'), 
                                 f"{int(dia_min['Quantidade'])} sinc.")
                    
                    with col_dia3:
                        media_dia_total = sincronizados_por_dia['Quantidade'].mean()
                        st.metric("Média por Dia", 
                                 f"{media_dia_total:.1f}")
        
        with tab4:
            st.markdown(f'<div class="section-title">Performance dos SREs</div>', unsafe_allow_html=True)
            
            if 'SRE' in df.columns and 'Status' in df.columns and 'Revisões' in df.columns:
                col_filtro1, col_filtro2 = st.columns(2)
                
                with col_filtro1:
                    if 'Ano' in df.columns:
                        anos_sre = sorted(df['Ano'].dropna().unique().astype(int))
                        anos_opcoes_sre = ['Todos'] + list(anos_sre)
                        ano_sre = st.selectbox(
                            "Ano:",
                            options=anos_opcoes_sre,
                            key="filtro_ano_sre"
                        )
                
                with col_filtro2:
                    if 'Mês' in df.columns:
                        meses_sre = sorted(df['Mês'].dropna().unique().astype(int))
                        meses_opcoes_sre = ['Todos'] + [str(m) for m in meses_sre]
                        mes_sre = st.selectbox(
                            "Mês:",
                            options=meses_opcoes_sre,
                            key="filtro_mes_sre"
                        )
                
                df_sre = df.copy()
                
                if 'Ano' in df_sre.columns and ano_sre != 'Todos':
                    df_sre = df_sre[df_sre['Ano'] == int(ano_sre)]
                
                if 'Mês' in df_sre.columns and mes_sre != 'Todos':
                    df_sre = df_sre[df_sre['Mês'] == int(mes_sre)]
                
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
                
                df_sincronizados = df_sre[df_sre['Status'] == 'Sincronizado'].copy()
                
                if not df_sincronizados.empty and 'SRE' in df_sincronizados.columns:
                    st.markdown("#### Sincronizados por SRE")
                    
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
                            colors.append(COR_AZUL_ESCURO)
                        else:
                            normalized = (valor - min_sinc) / (max_sinc - min_sinc)
                            red = int(0 * normalized + 26 * (1 - normalized))
                            green = int(89 * normalized + 42 * (1 - normalized))
                            blue = int(115 * normalized + 58 * (1 - normalized))
                            colors.append(f'rgb({red}, {green}, {blue})')
                    
                    fig_sinc_bar.add_trace(go.Bar(
                        x=sinc_por_sre_nome['SRE_Nome'].head(15),
                        y=sinc_por_sre_nome['Sincronizados'].head(15),
                        name='Sincronizados',
                        text=sinc_por_sre_nome['Sincronizados'].head(15),
                        textposition='outside',
                        marker_color=colors[:15],
                        marker_line_color=COR_AZUL_MEDIO,
                        marker_line_width=1,
                        opacity=0.8
                    ))
                    
                    titulo_grafico = 'Sincronizados por SRE'
                    if ano_sre != 'Todos' or mes_sre != 'Todos':
                        titulo_grafico += ' - Filtrado'
                        if ano_sre != 'Todos':
                            titulo_grafico += f' ({ano_sre}'
                        if mes_sre != 'Todos':
                            meses_nomes = {
                                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                            }
                            if ano_sre != 'Todos':
                                titulo_grafico += f' - {meses_nomes[int(mes_sre)]})'
                            else:
                                titulo_grafico += f' ({meses_nomes[int(mes_sre)]})'
                    
                    fig_sinc_bar.update_layout(
                        title=titulo_grafico,
                        xaxis_title='SRE',
                        yaxis_title='Número de Sincronizados',
                        plot_bgcolor=COR_BRANCO,
                        height=400,
                        showlegend=False,
                        margin=dict(t=40, b=80, l=40, r=40),
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
                            st.metric("1º Lugar", 
                                     f"{sre1['SRE_Nome']}", 
                                     f"{sre1['Sincronizados']} sinc.")
                    
                    if len(sinc_por_sre_nome) >= 2:
                        with col_top2:
                            sre2 = sinc_por_sre_nome.iloc[1]
                            st.metric("2º Lugar", 
                                     f"{sre2['SRE_Nome']}", 
                                     f"{sre2['Sincronizados']} sinc.")
                    
                    if len(sinc_por_sre_nome) >= 3:
                        with col_top3:
                            sre3 = sinc_por_sre_nome.iloc[2]
                            st.metric("3º Lugar", 
                                     f"{sre3['SRE_Nome']}", 
                                     f"{sre3['Sincronizados']} sinc.")
                    
                    st.markdown("#### Detalhado")
                    
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
    
    with tab_mapa:
        st.markdown("### Mapa de Sincronizações")
        
        # Filtros para o mapa
        col_mapa_filtro1, col_mapa_filtro2, col_mapa_filtro3 = st.columns(3)
        
        with col_mapa_filtro1:
            empresas_disponiveis = df['Empresa'].dropna().unique()
            empresas_opcoes = ['Todas'] + sorted([e for e in empresas_disponiveis if e in MAPEAMENTO_EMPRESAS])
            
            empresas_selecionadas_mapa = st.multiselect(
                "Empresas",
                options=empresas_opcoes,
                default=['Todas'],
                key="mapa_empresas_folium"
            )
        
        with col_mapa_filtro2:
            if 'Ano' in df.columns:
                anos_disponiveis_mapa = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_mapa = ['Todos'] + list(anos_disponiveis_mapa)
                ano_filtro_mapa = st.selectbox(
                    "Ano",
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
                    "Mês",
                    options=meses_opcoes_mapa,
                    index=0,
                    key="mapa_mes_folium"
                )
            else:
                mes_filtro_mapa = 'Todos'
        
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
                <div class="metric-label">Empresas Ativas</div>
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
                    <div class="metric-label">Maior: {empresa_max[:20]}</div>
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
        st.markdown('<div class="section-title">Mapa de Bolhas</div>', unsafe_allow_html=True)
        
        m = criar_mapa_folium(df_mapa)
        if m:
            mapa_html = m._repr_html_()
            
            wrapper = f"""
            <div style="
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                border: 1px solid {COR_BORDA};
                margin-bottom: 15px;
            ">
                {mapa_html}
            </div>
            """
            st.components.v1.html(wrapper, height=520)
        else:
            st.info("Nenhuma empresa com sincronizações para exibir.")
        
        # Ranking de barras
        st.markdown('<div class="section-title">Ranking de Sincronizações</div>', unsafe_allow_html=True)
        
        fig_barras = criar_grafico_barras(df_mapa)
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True, config={'displayModeBar': True})
        
        # Tabela detalhada
        with st.expander("Detalhes por Empresa", expanded=False):
            if not df_mapa.empty:
                tabela_detalhes = df_mapa[['empresa_nome', 'sigla', 'estado', 'regiao', 'sincronismos']].copy()
                tabela_detalhes.columns = ['Empresa', 'UF', 'Estado', 'Região', 'Sincronizações']
                tabela_detalhes = tabela_detalhes.sort_values('Sincronizações', ascending=False).reset_index(drop=True)
                
                total_geral = tabela_detalhes['Sincronizações'].sum()
                
                posicoes = []
                for i in range(len(tabela_detalhes)):
                    if i == 0:
                        posicoes.append("1º")
                    elif i == 1:
                        posicoes.append("2º")
                    elif i == 2:
                        posicoes.append("3º")
                    else:
                        posicoes.append(f"{i+1}º")
                tabela_detalhes.insert(0, 'Posição', posicoes)
                
                tabela_detalhes['% Total'] = (tabela_detalhes['Sincronizações'] / total_geral * 100).round(1) if total_geral > 0 else 0
                
                tabela_detalhes['Empresa (UF)'] = tabela_detalhes.apply(
                    lambda x: f"{x['Empresa']} ({x['UF']})", axis=1
                )
                
                df_exibir = tabela_detalhes[['Posição', 'Empresa (UF)', 'Estado', 'Região', 'Sincronizações', '% Total']].copy()
                
                column_config = {
                    "Posição": st.column_config.TextColumn("Pos.", width="small"),
                    "Empresa (UF)": st.column_config.TextColumn("Empresa", width="large"),
                    "Estado": st.column_config.TextColumn("Estado", width="medium"),
                    "Região": st.column_config.TextColumn("Região", width="medium"),
                    "Sincronizações": st.column_config.NumberColumn("Sinc.", format="%d", width="small"),
                    "% Total": st.column_config.NumberColumn("%", format="%.1f%%", width="small")
                }
                
                st.dataframe(
                    df_exibir,
                    use_container_width=True,
                    column_config=column_config,
                    height=350
                )
                
                csv = tabela_detalhes[['Empresa', 'UF', 'Estado', 'Região', 'Sincronizações', '% Total']].to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="Exportar CSV",
                    data=csv,
                    file_name=f"sincronismos_empresas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # Legenda
        with st.expander("Sobre o Mapa", expanded=False):
            st.markdown(f"""
            **Escala de Cores**
            
            - **Azul** → Menor volume de sincronizações
            - **Laranja** → Volume médio
            - **Vermelho** → Maior volume
            
            **Interação**
            - Passe o mouse sobre as bolhas para ver detalhes
            - O tamanho da bolha é proporcional ao volume
            - O texto dentro mostra a sigla e o número
            """)
    
    # ============================================
    # KPI IPE
    # ============================================
    with tab_ipe:
        st.markdown(f'<div class="section-title">Índice de Performance (IPE)</div>', unsafe_allow_html=True)
        
        if 'SRE' in df.columns and 'Status' in df.columns and 'Retorno Cliente' in df.columns:
            
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
            st.markdown("#### Período")
            col_filtro_ipe1, col_filtro_ipe2 = st.columns(2)
            
            with col_filtro_ipe1:
                if 'Ano' in df.columns:
                    anos_ipe = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_ipe = ['Todos'] + list(anos_ipe)
                    ano_ipe = st.selectbox("Ano:", options=anos_opcoes_ipe, key="filtro_ano_ipe")
                else:
                    ano_ipe = 'Todos'
            
            with col_filtro_ipe2:
                if 'Mês' in df.columns:
                    meses_map = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
                    meses_disponiveis = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_ipe = [meses_map[m] for m in meses_disponiveis]
                    meses_selecionados_nomes = st.multiselect("Mês(es):", options=meses_opcoes_ipe, default=meses_opcoes_ipe, key="filtro_meses_ipe")
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
            st.markdown("#### Performance - Período Selecionado")
            cards_total_periodo = len(df_ipe)
            total_sres_periodo = df_ipe['SRE'].nunique()
            
            sres_metrics = []
            for sre in df_ipe['SRE'].dropna().unique():
                df_sre_data = df_ipe[df_ipe['SRE'] == sre]
                if len(df_sre_data) > 0:
                    cd = len(df_sre_data)
                    ca = len(df_sre_data[df_sre_data['Status'] == 'Sincronizado'])
                    cr = len(df_sre_data[df_sre_data['Retorno Cliente'].apply(is_retorno_sim)])
                    
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
            
            st.markdown("---")
            
            # IPE Acumulado por Mês
            st.markdown("#### IPE Acumulado")
            st.caption("Evolução do IPE acumulado mês a mês")
            
            if 'Criado' in df_ipe.columns and len(df_ipe) > 0:
                df_ipe['Periodo'] = df_ipe['Criado'].dt.strftime('%Y-%m')
                df_ipe['Nome_Mes_Completo'] = df_ipe['Criado'].dt.month.map({1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'})
                meses_ordenados = sorted(df_ipe['Periodo'].unique())
                
                acumulados = []
                for periodo in meses_ordenados:
                    df_ate = df_ipe[df_ipe['Periodo'] <= periodo]
                    
                    cd_acum = len(df_ate)
                    ca_acum = len(df_ate[df_ate['Status'] == 'Sincronizado'])
                    cr_acum = len(df_ate[df_ate['Retorno Cliente'].apply(is_retorno_sim)])
                    na_acum = df_ate['SRE'].nunique()
                    
                    ipe_acum = calcular_ipe(ca_acum, cr_acum, cd_acum, cd_acum, na_acum)
                    
                    df_ate_sorted = df_ate.sort_values('Criado')
                    ultimo_mes_completo = df_ate_sorted['Nome_Mes_Completo'].iloc[-1] if len(df_ate_sorted) > 0 else periodo
                    
                    acumulados.append({
                        'Mês': ultimo_mes_completo,
                        'CD_Acum': cd_acum,
                        'CA_Acum': ca_acum,
                        'CR_Acum': cr_acum,
                        'NA_Acum': na_acum,
                        'IPE Acumulado (%)': round(ipe_acum * 100, 2)
                    })
                
                if acumulados:
                    df_acum = pd.DataFrame(acumulados)
                    
                    # Gráfico de linha
                    fig_linha = go.Figure()
                    fig_linha.add_trace(go.Scatter(
                        x=df_acum['Mês'], 
                        y=df_acum['IPE Acumulado (%)'], 
                        mode='lines+markers+text', 
                        line=dict(color=COR_AZUL_ESCURO, width=2), 
                        marker=dict(size=8, color=COR_AZUL_MEDIO), 
                        text=df_acum['IPE Acumulado (%)'].apply(lambda x: f'{x:.1f}%'), 
                        textposition='top center', 
                        name='IPE Acumulado',
                        hovertemplate='<b>%{x}</b><br>IPE: %{y:.1f}%<br>CD: %{customdata[0]:,}<br>CA: %{customdata[1]:,}<br>CR: %{customdata[2]:,}<br>SREs: %{customdata[3]}<extra></extra>',
                        customdata=df_acum[['CD_Acum', 'CA_Acum', 'CR_Acum', 'NA_Acum']].values
                    ))
                    fig_linha.add_hline(y=95, line_dash="dash", line_color=COR_AZUL_MEDIO, annotation_text="Meta 95%")
                    fig_linha.add_hline(y=100, line_dash="dot", line_color=COR_CINZA_CLARO, annotation_text="Limite")
                    fig_linha.add_trace(go.Scatter(x=df_acum['Mês'], y=df_acum['IPE Acumulado (%)'], fill='tozeroy', fillcolor='rgba(44, 82, 130, 0.08)', line=dict(width=0), showlegend=False, hoverinfo='skip'))
                    fig_linha.update_layout(title='Evolução do IPE Acumulado', xaxis_title='Mês', yaxis_title='IPE (%)', yaxis=dict(range=[0, 105]), height=350, plot_bgcolor=COR_BRANCO)
                    st.plotly_chart(fig_linha, use_container_width=True)
                    
                    # Cards resumo
                    ultimo = df_acum.iloc[-1]
                    primeiro = df_acum.iloc[0]
                    st.markdown("#### Resumo do Período")
                    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                    with col_r1: st.metric("Período", f"{primeiro['Mês']} - {ultimo['Mês']}")
                    with col_r2: st.metric("Total Cards", f"{ultimo['CD_Acum']:,}")
                    with col_r3: st.metric("IPE Acumulado", f"{ultimo['IPE Acumulado (%)']:.2f}%", delta=f"{ultimo['IPE Acumulado (%)'] - 95:+.2f} pp", delta_color="normal" if ultimo['IPE Acumulado (%)'] >= 95 else "inverse")
                    with col_r4: st.metric("SREs Ativos", f"{ultimo['NA_Acum']}")
                    
                    # Tabela
                    with st.expander("Tabela de Acumulados", expanded=False):
                        st.dataframe(df_acum, use_container_width=True, column_config={"IPE Acumulado (%)": st.column_config.ProgressColumn("IPE %", format="%.2f%%", min_value=0, max_value=100)})
                        csv_acum = df_acum.to_csv(index=False).encode('utf-8-sig')
                        st.download_button("Exportar CSV", data=csv_acum, file_name=f"ipe_acumulado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)
            
            # Explicação
            with st.expander("Entenda o IPE"):
                st.markdown("""
                **Fórmula:** `IPE = (CA - CR) / (CD + |((CT/CD)/NA) - 1|)`
                
                - **CA** = Cards Analisados (Sincronizados)
                - **CR** = Cards Reabertos (Retorno Cliente = Sim)
                - **CD** = Cards Demandados (Total do período)
                - **CT** = Cards Total (Total geral)
                - **NA** = Número de Atendentes (SREs únicos)
                
                **Meta: 95% | Limite: 100%**
                """)
        else:
            st.warning("Colunas necessárias não encontradas.")
    
    # ============================================
    # ANÁLISE ESTATÍSTICA
    # ============================================
    with tab_estatistica:
        st.markdown("### Análise Estatística")
        st.caption("Distribuição, percentis e tendência de sincronizações")
        
        # Filtros
        col_filtro_est1, col_filtro_est2, col_filtro_est3 = st.columns(3)
        
        with col_filtro_est1:
            if 'Ano' in df.columns:
                anos_est = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_est = ['Todos os Anos'] + list(anos_est)
                ano_est = st.selectbox(
                    "Ano",
                    options=anos_opcoes_est,
                    key="filtro_ano_est",
                    index=0
                )
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
                
                mes_est = st.selectbox(
                    "Mês",
                    options=meses_opcoes_est,
                    key="filtro_mes_est",
                    index=0
                )
            else:
                mes_est = 'Todos os Meses'
        
        with col_filtro_est3:
            percentil_param = st.number_input(
                "Percentil de Referência (%)",
                min_value=50,
                max_value=99,
                value=75,
                step=5,
                key="percentil_param",
                help="Percentil utilizado para análise de tendência"
            )
        
        # Aplicar filtros
        df_est = df.copy()
        if ano_est != 'Todos os Anos':
            df_est = df_est[df_est['Ano'] == int(ano_est)]
        if mes_est != 'Todos os Meses':
            df_est = df_est[df_est['Mês'] == int(mes_est)]
        
        # Filtrar apenas sincronizados
        df_sinc_est = df_est[df_est['Status'] == 'Sincronizado'].copy()
        
        if df_sinc_est.empty:
            st.warning("Nenhum dado sincronizado encontrado.")
        else:
            
            # Medidas separatrizes
            st.markdown("---")
            st.markdown("#### Distribuição e Percentis")
            st.caption(f"Percentil de Referência: {percentil_param}%")
            
            if 'Criado' in df_sinc_est.columns:
                df_sinc_est['Data'] = df_sinc_est['Criado'].dt.date
                sinc_por_dia_est = df_sinc_est.groupby('Data').size().reset_index()
                sinc_por_dia_est.columns = ['Data', 'Quantidade']
                
                if not sinc_por_dia_est.empty:
                    valores = sinc_por_dia_est['Quantidade']
                    
                    # Calcular medidas
                    mediana = valores.median()
                    q1 = valores.quantile(0.25)
                    q3 = valores.quantile(0.75)
                    p10 = valores.quantile(0.10)
                    p90 = valores.quantile(0.90)
                    p_selecionado = valores.quantile(percentil_param/100)
                    
                    # Gráfico - Distribuição
                    fig_sep = go.Figure()
                    
                    fig_sep.add_trace(go.Histogram(
                        x=valores,
                        nbinsx=20,
                        name='Frequência',
                        marker_color='rgba(44, 82, 130, 0.4)',
                        marker_line_color=COR_AZUL_ESCURO,
                        marker_line_width=1,
                        hovertemplate='Intervalo: %{x}<br>Frequência: %{y}<extra></extra>'
                    ))
                    
                    fig_sep.add_vline(x=mediana, line_dash="dash", line_color=COR_VERDE_CORPORATIVO, 
                                      annotation_text=f"P50: {mediana:.0f}", annotation_position="top")
                    fig_sep.add_vline(x=q1, line_dash="dot", line_color=COR_AZUL_MEDIO,
                                      annotation_text=f"Q1: {q1:.0f}", annotation_position="top")
                    fig_sep.add_vline(x=q3, line_dash="dot", line_color=COR_AZUL_MEDIO,
                                      annotation_text=f"Q3: {q3:.0f}", annotation_position="top")
                    fig_sep.add_vline(x=p10, line_dash="dot", line_color=COR_CINZA_CLARO,
                                      annotation_text=f"P10: {p10:.0f}", annotation_position="bottom")
                    fig_sep.add_vline(x=p90, line_dash="dot", line_color=COR_CINZA_CLARO,
                                      annotation_text=f"P90: {p90:.0f}", annotation_position="bottom")
                    fig_sep.add_vline(x=p_selecionado, line_dash="dash", line_color=COR_LARANJA_SUAVE, line_width=2,
                                      annotation_text=f"P{percentil_param}: {p_selecionado:.0f}", annotation_position="bottom")
                    
                    fig_sep.update_layout(
                        title=f'Distribuição Diária',
                        xaxis_title='Sincronizações por Dia',
                        yaxis_title='Frequência',
                        height=350,
                        plot_bgcolor=COR_BRANCO,
                        showlegend=False,
                        barmode='overlay'
                    )
                    
                    st.plotly_chart(fig_sep, use_container_width=True)
                    
                    # Cards
                    col_sep1, col_sep2, col_sep3, col_sep4, col_sep5 = st.columns(5)
                    
                    with col_sep1:
                        st.metric("P10", f"{p10:.0f}")
                    with col_sep2:
                        st.metric("Q1 (P25)", f"{q1:.0f}")
                    with col_sep3:
                        st.metric("Mediana (P50)", f"{mediana:.0f}")
                    with col_sep4:
                        st.metric("Q3 (P75)", f"{q3:.0f}")
                    with col_sep5:
                        st.metric(f"P{percentil_param}", f"{p_selecionado:.0f}")
            
            # Análise de tendência
            st.markdown("---")
            st.markdown("#### Tendência de Percentis")
            st.caption(f"Evolução dos percentis - Referência: {percentil_param}%")
            
            if 'Criado' in df_sinc_est.columns:
                df_sinc_est['Mes_Ano'] = df_sinc_est['Criado'].dt.strftime('%Y-%m')
                df_sinc_est['Nome_Mes_Ano'] = df_sinc_est['Criado'].dt.strftime('%b/%Y')
                
                meses_unicos = sorted(df_sinc_est['Mes_Ano'].unique())
                
                dados_tendencia = []
                for mes in meses_unicos:
                    df_mes = df_sinc_est[df_sinc_est['Mes_Ano'] == mes]
                    if not df_mes.empty:
                        valores_mes = df_mes.groupby('Data').size()
                        if not valores_mes.empty:
                            dados_tendencia.append({
                                'Mês': mes,
                                'Mês_Label': df_mes['Nome_Mes_Ano'].iloc[0],
                                'P25': valores_mes.quantile(0.25),
                                'P50': valores_mes.quantile(0.50),
                                f'P{percentil_param}': valores_mes.quantile(percentil_param/100),
                                'P90': valores_mes.quantile(0.90),
                                'Média': valores_mes.mean(),
                                'Total': len(df_mes)
                            })
                
                if dados_tendencia:
                    df_tendencia = pd.DataFrame(dados_tendencia)
                    
                    # Gráfico de tendência
                    fig_tendencia = go.Figure()
                    
                    # P{percentil_param}
                    fig_tendencia.add_trace(go.Scatter(
                        x=df_tendencia['Mês_Label'],
                        y=df_tendencia[f'P{percentil_param}'],
                        mode='lines+markers',
                        name=f'P{percentil_param}',
                        line=dict(color=COR_LARANJA_SUAVE, width=2),
                        marker=dict(size=8, color=COR_LARANJA_SUAVE)
                    ))
                    
                    # P50
                    fig_tendencia.add_trace(go.Scatter(
                        x=df_tendencia['Mês_Label'],
                        y=df_tendencia['P50'],
                        mode='lines+markers',
                        name='P50 (Mediana)',
                        line=dict(color=COR_AZUL_ESCURO, width=2),
                        marker=dict(size=6, color=COR_AZUL_ESCURO)
                    ))
                    
                    # Média
                    fig_tendencia.add_trace(go.Scatter(
                        x=df_tendencia['Mês_Label'],
                        y=df_tendencia['Média'],
                        mode='lines+markers',
                        name='Média',
                        line=dict(color=COR_VERDE_CORPORATIVO, width=2, dash='dash'),
                        marker=dict(size=6, color=COR_VERDE_CORPORATIVO)
                    ))
                    
                    # Área P25-P90
                    fig_tendencia.add_trace(go.Scatter(
                        x=df_tendencia['Mês_Label'],
                        y=df_tendencia['P90'],
                        mode='lines',
                        name='Faixa P25-P90',
                        line=dict(width=0),
                        showlegend=False
                    ))
                    
                    fig_tendencia.add_trace(go.Scatter(
                        x=df_tendencia['Mês_Label'],
                        y=df_tendencia['P25'],
                        mode='lines',
                        fill='tonexty',
                        fillcolor='rgba(44, 82, 130, 0.15)',
                        line=dict(width=0),
                        name='Faixa P25-P90'
                    ))
                    
                    fig_tendencia.update_layout(
                        title='Evolução dos Percentis Diários',
                        xaxis_title='Mês',
                        yaxis_title='Sincronizações por Dia',
                        height=350,
                        plot_bgcolor=COR_BRANCO,
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=8)
                        )
                    )
                    
                    st.plotly_chart(fig_tendencia, use_container_width=True)
                    
                    # Análise da tendência
                    st.markdown("#### Resumo da Tendência")
                    
                    if len(df_tendencia) > 1:
                        primeiro = df_tendencia.iloc[0]
                        ultimo = df_tendencia.iloc[-1]
                        
                        col_tend1, col_tend2, col_tend3 = st.columns(3)
                        
                        with col_tend1:
                            variacao_p50 = ((ultimo['P50'] - primeiro['P50']) / primeiro['P50'] * 100) if primeiro['P50'] > 0 else 0
                            st.metric(
                                "Mediana (P50)",
                                f"{ultimo['P50']:.0f}",
                                delta=f"{variacao_p50:+.1f}%",
                                delta_color="normal" if variacao_p50 >= 0 else "inverse"
                            )
                        
                        with col_tend2:
                            variacao_p_param = ((ultimo[f'P{percentil_param}'] - primeiro[f'P{percentil_param}']) / primeiro[f'P{percentil_param}'] * 100) if primeiro[f'P{percentil_param}'] > 0 else 0
                            st.metric(
                                f"P{percentil_param}",
                                f"{ultimo[f'P{percentil_param}']:.0f}",
                                delta=f"{variacao_p_param:+.1f}%",
                                delta_color="normal" if variacao_p_param >= 0 else "inverse"
                            )
                        
                        with col_tend3:
                            variacao_media = ((ultimo['Média'] - primeiro['Média']) / primeiro['Média'] * 100) if primeiro['Média'] > 0 else 0
                            st.metric(
                                "Média",
                                f"{ultimo['Média']:.1f}",
                                delta=f"{variacao_media:+.1f}%",
                                delta_color="normal" if variacao_media >= 0 else "inverse"
                            )
                        
                        if variacao_p50 > 10:
                            st.success(f"Tendência POSITIVA - Mediana cresceu {variacao_p50:.1f}%")
                        elif variacao_p50 > 0:
                            st.info(f"Leve crescimento - Mediana cresceu {variacao_p50:.1f}%")
                        elif variacao_p50 > -10:
                            st.warning(f"Estável - Mediana variou {variacao_p50:.1f}%")
                        else:
                            st.error(f"Tendência NEGATIVA - Mediana caiu {abs(variacao_p50):.1f}%")
                    
                    # Tabela
                    with st.expander("Tabela de Tendência", expanded=False):
                        st.dataframe(
                            df_tendencia,
                            use_container_width=True,
                            column_config={
                                "Mês_Label": st.column_config.TextColumn("Mês"),
                                "P25": st.column_config.NumberColumn("P25", format="%.1f"),
                                "P50": st.column_config.NumberColumn("P50", format="%.1f"),
                                f"P{percentil_param}": st.column_config.NumberColumn(f"P{percentil_param}", format="%.1f"),
                                "P90": st.column_config.NumberColumn("P90", format="%.1f"),
                                "Média": st.column_config.NumberColumn("Média", format="%.1f"),
                                "Total": st.column_config.NumberColumn("Total", format="%d")
                            }
                        )
            
            # Exportar dados
            st.markdown("---")
            st.markdown("#### Exportar Dados")
            
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                if 'df_tendencia' in locals() and not df_tendencia.empty:
                    csv_tendencia = df_tendencia.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="Exportar Tendência",
                        data=csv_tendencia,
                        file_name=f"tendencia_percentis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col_export2:
                if 'sinc_por_dia_est' in locals() and not sinc_por_dia_est.empty:
                    csv_sinc = sinc_por_dia_est.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="Exportar Sincronizações",
                        data=csv_sinc,
                        file_name=f"sincronizacoes_diarias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

else:
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem; background: {COR_FUNDO}; border-radius: 8px; border: 1px dashed {COR_BORDA};">
        <h3 style="color: {COR_TEXTO_PRINCIPAL};">Esteira ADMS Dashboard</h3>
        <p style="color: {COR_CINZA_CLARO}; margin-bottom: 1.5rem;">
            Sistema de análise e monitoramento de chamados
        </p>
        <div style="margin-top: 1.5rem; padding: 1.5rem; background: {COR_BRANCO}; border-radius: 6px; display: inline-block; text-align: left;">
            <h4 style="color: {COR_AZUL_ESCURO};">Para começar:</h4>
            <p>1. Use a barra lateral para fazer upload do arquivo CSV</p>
            <p>2. Ou coloque um arquivo CSV no mesmo diretório</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

ultima_atualizacao = st.session_state.get('ultima_atualizacao', get_horario_brasilia())

st.markdown(f"""
<div class="footer">
    <div style="margin-bottom: 0.5rem;">
        <p style="margin: 0; color: {COR_TEXTO_PRINCIPAL}; font-weight: 500; font-size: 0.75rem;">
        Desenvolvido por: Kewin Marcel Ramirez Ferreira | GEAT
        </p>
        <p style="margin: 0.2rem 0 0 0; color: {COR_CINZA_CLARO}; font-size: 0.7rem;">
        📧 kewin.ferreira@energisa.com.br
        </p>
    </div>
    <div>
        <p style="margin: 0; color: {COR_CINZA_CLARO}; font-size: 0.65rem;">
        © 2024 Esteira ADMS Dashboard | Energisa Group
        </p>
        <p style="margin: 0.1rem 0 0 0; color: {COR_CINZA_CLARO}; font-size: 0.6rem;">
        v5.5 | Última atualização: {ultima_atualizacao}
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
