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

CORES_GRADIENTE = [
    COR_VERDE_ESCURO,
    COR_AZUL_PETROLEO,
    COR_AZUL_ESCURO,
    COR_LARANJA,
    COR_VERMELHO,
    "#1E88E5"
]

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
    page_icon="📊",
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
    .dataframe {{ border-collapse: collapse; width: 100%; }}
    .dataframe th {{ background-color: {COR_AZUL_ESCURO}; color: {COR_BRANCO}; padding: 10px; text-align: left; }}
    .dataframe td {{ padding: 8px; border-bottom: 1px solid {COR_CINZA_BORDA}; }}
    .dataframe tr:hover {{ background-color: {COR_CINZA_FUNDO}; }}
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

def criar_card_indicador_simples(valor, label, icone="📊"):
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
    return hashlib.md5(conteudo).hexdigest()

# ============================================
# FUNÇÃO PRINCIPAL DE CARREGAMENTO DE DADOS
# ============================================
@st.cache_data(ttl=300)
def carregar_dados(uploaded_file=None, caminho_arquivo=None):
    """Carrega e processa os dados - Adaptado para o formato do arquivo ADMS.
    Suporta 'Revisões', 'Qtd. Revisões' e variações, criando Revisões_Total (soma das duas)."""
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
        df = pd.read_csv(io.StringIO(data_str), quotechar='"')

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
                df[col] = pd.to_datetime(df[col], errors='coerce')

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

        hash_conteudo = calcular_hash_arquivo(conteudo_bytes)
        timestamp = time.time()

        return df, "✅ Dados carregados com sucesso", f"{hash_conteudo}_{timestamp}"

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

def verificar_atualizacao_arquivo():
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
    keys_to_clear = ['df_original', 'df_filtrado', 'arquivo_atual',
                     'ultima_modificacao', 'file_hash', 'uploaded_file_name',
                     'ultima_atualizacao']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def get_horario_brasilia():
    try:
        tz = timezone('America/Sao_Paulo')
        return datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    except:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

def criar_popup_indicadores(df):
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
    cards_com_erro = len(df_mes[df_mes['Revisões_Total'] > 0])
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
    df_sre = df[df['SRE'] == sre_nome].copy()
    if len(df_sre) == 0:
        return 0, 0, 0
    total_cards = len(df_sre)
    if 'Revisões_Total' in df_sre.columns:
        cards_com_revisoes = len(df_sre[df_sre['Revisões_Total'] > 0])
        taxa_retorno = (cards_com_revisoes / total_cards * 100) if total_cards > 0 else 0
    else:
        taxa_retorno = 0
        cards_com_revisoes = 0
    cards_sincronizados = len(df_sre[df_sre['Status'] == 'Sincronizado'])
    return taxa_retorno, cards_com_revisoes, cards_sincronizados

def analisar_tendencia_mensal_sre(df, sre_nome):
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
        st.error("⚠️ Biblioteca 'folium' não instalada. Execute: pip install folium")
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
        medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, f'#{rank}')
        tooltip_html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; min-width: 220px; padding: 4px;">
            <div style="background: {COR_AZUL_ESCURO}; color: white; padding: 10px 14px;
                border-radius: 8px 8px 0 0; font-weight: 700; font-size: 14px;">
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
                        <td style="font-weight:600; text-align:right;">{medal} {rank}º lugar</td></tr>
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
        padding: 14px 20px; font-family: 'Segoe UI', sans-serif; min-width: 210px;
        border: 1px solid {COR_CINZA_BORDA};">
        <div style="font-weight:800; font-size:13px; color:{COR_PRETO_SUAVE}; margin-bottom:12px; letter-spacing:0.5px;">
            📊 VOLUME DE SINCRONIZAÇÕES</div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            <div style="width: 140px; height: 12px; border-radius: 6px;
                background: linear-gradient(to right, {COR_AZUL_PETROLEO}, {COR_LARANJA}, {COR_VERMELHO});
                border: 1px solid #ddd;"></div></div>
        <div style="display:flex; justify-content:space-between; font-size:10px; color:{COR_CINZA_TEXTO}; margin-bottom:12px;">
            <span>⬅️ Menor volume</span><span>Maior volume ➡️</span></div>
        <div style="border-top:1px solid {COR_CINZA_BORDA}; padding-top:10px; font-size:10px; color:{COR_CINZA_TEXTO};">
            <div>🔍 Passe o mouse sobre uma bolha</div><div>para ver os detalhes completos</div></div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legenda_html))
    if len(df_bolhas_sorted) >= 1:
        top3_rows = df_bolhas_sorted.head(3)
        top3_html_items = ""
        medals = ['🥇', '🥈', '🥉']
        for i, (_, row) in enumerate(top3_rows.iterrows()):
            pct_t = row['sincronismos'] / total * 100 if total > 0 else 0
            cor_top = cor_gradiente_folium(row['sincronismos'], min_sinc, max_sinc)
            top3_html_items += f"""
            <div style="display:flex; align-items:center; gap:10px; padding: 8px 0;
                border-bottom: 1px solid {COR_CINZA_BORDA};">
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
        <div style="position: fixed; top: 90px; right: 20px; z-index: 9999;
            background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            padding: 14px 18px; font-family: 'Segoe UI', sans-serif; min-width: 240px;
            border: 1px solid {COR_CINZA_BORDA};">
            <div style="font-weight:800; font-size:13px; color:{COR_PRETO_SUAVE}; margin-bottom:10px; letter-spacing:0.5px;">
                🏆 TOP EMPRESAS</div>
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
            orientation='h', text=[f"{row['sincronismos']:,} ({percentual:.1f}%)"],
            textposition='outside', marker_color=cor,
            marker_line_color=COR_AZUL_ESCURO, marker_line_width=1,
            hovertemplate=f"<b>{row['empresa_nome']}</b><br>" +
                          f"Sincronizações: {row['sincronismos']:,}<br>" +
                          f"Percentual: {percentual:.1f}%<br>" +
                          f"Estado: {row['estado']}<br>" +
                          f"Região: {row['regiao']}<extra></extra>",
            name=row['empresa']
        ))
    fig.update_layout(
        title=dict(text="<b>RANKING </b>", font=dict(size=16, color=COR_AZUL_ESCURO), x=0.5),
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
                    ano_selecionado = st.selectbox("📅 Ano", options=anos_opcoes, key="filtro_ano")
                    if ano_selecionado != 'Todos os Anos':
                        df = df[df['Ano'] == int(ano_selecionado)]
            if 'Mês' in df.columns:
                meses_disponiveis = sorted(df['Mês'].dropna().unique().astype(int))
                if meses_disponiveis:
                    meses_opcoes = ['Todos os Meses'] + [str(m) for m in meses_disponiveis]
                    mes_selecionado = st.selectbox("📆 Mês", options=meses_opcoes, key="filtro_mes")
                    if mes_selecionado != 'Todos os Meses':
                        df = df[df['Mês'] == int(mes_selecionado)]
            if 'Responsável_Formatado' in df.columns:
                responsaveis = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
                responsavel_selecionado = st.selectbox("👤 Responsável", options=responsaveis, key="filtro_responsavel")
                if responsavel_selecionado != 'Todos':
                    df = df[df['Responsável_Formatado'] == responsavel_selecionado]
            busca_chamado = st.text_input("🔎 Buscar Chamado", placeholder="Digite número do chamado...", key="busca_chamado")
            if busca_chamado:
                df = df[df['Chamado'].astype(str).str.contains(busca_chamado, na=False)]
            if 'Status' in df.columns:
                status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox("📊 Status", options=status_opcoes, key="filtro_status")
                if status_selecionado != 'Todos':
                    df = df[df['Status'] == status_selecionado]
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos'] + sorted(df['Tipo_Chamado'].dropna().unique())
                tipo_selecionado = st.selectbox("📝 Tipo de Chamado", options=tipos, key="filtro_tipo")
                if tipo_selecionado != 'Todos':
                    df = df[df['Tipo_Chamado'] == tipo_selecionado]
            if 'Empresa' in df.columns:
                empresas = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                empresa_selecionada = st.selectbox("🏢 Empresa", options=empresas, key="filtro_empresa")
                if empresa_selecionada != 'Todas':
                    df = df[df['Empresa'] == empresa_selecionada]
            if 'SRE' in df.columns:
                sres = ['Todos'] + sorted(df['SRE'].dropna().unique())
                sre_selecionado = st.selectbox("🔧 SRE Responsável", options=sres, key="filtro_sre")
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
                if st.button("🔄 Recarregar Local", use_container_width=True, type="primary",
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
                if st.button("🗑️ Limpar Tudo", use_container_width=True, type="secondary",
                           help="Limpa todos os dados e cache", key="btn_limpar"):
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
        uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=['csv'],
                                         key="file_uploader",
                                         help="Faça upload de um novo arquivo CSV para substituir os dados atuais",
                                         label_visibility="collapsed")
        if uploaded_file is not None:
            current_hash = calcular_hash_arquivo(uploaded_file.getvalue())
            file_details = {"Nome": uploaded_file.name, "Tamanho": f"{uploaded_file.size / 1024:.1f} KB"}
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
            <h1 style="color: {COR_BRANCO}; margin: 0; font-size: 1.6rem; font-weight: 600;
                letter-spacing: -0.3px; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                📊 ESTEIRA SRE (Site Reliability Engineering)
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
                v5.5 | Sistema de Performance SRE
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 0.3rem 0 0 0; font-size: 0.7rem; font-weight: 500;">
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
        if st.button("📰 **VER MANCHETE**", help="Clique para ver os principais indicadores do mês",
                    type="secondary", use_container_width=True, key="btn_manchete"):
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
                                                  key="popup_ano")
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
        com_erro = len(df_filtrado_periodo[df_filtrado_periodo['Revisões_Total'] > 0])
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
            com_erro_anterior = len(df_anterior[df_anterior['Revisões_Total'] > 0])
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
            fig_comparativo.add_trace(go.Bar(x=periodos, y=cards_totais, name='Total Cards',
                                             marker_color=COR_AZUL_ESCURO, text=cards_totais,
                                             textposition='outside', textfont=dict(size=10), width=0.35))
            fig_comparativo.add_trace(go.Bar(x=periodos, y=cards_validados, name='Validados',
                                             marker_color=COR_VERDE_ESCURO, text=cards_validados,
                                             textposition='outside', textfont=dict(size=10), width=0.35))
            fig_comparativo.add_trace(go.Scatter(x=periodos, y=taxa_sucesso_vals, name='Taxa Sucesso',
                                                 yaxis='y2', mode='lines+markers+text',
                                                 line=dict(color=COR_LARANJA, width=2),
                                                 marker=dict(size=8, color=COR_LARANJA),
                                                 text=[f"{v:.1f}%" for v in taxa_sucesso_vals],
                                                 textposition='top center', textfont=dict(size=9)))
            fig_comparativo.update_layout(
                title=dict(text='Comparativo: Período Atual vs Anterior', font=dict(size=14)),
                barmode='group',
                yaxis=dict(title=dict(text='Quantidade', font=dict(size=11)),
                           gridcolor='rgba(0,0,0,0.05)', rangemode='tozero'),
                yaxis2=dict(title=dict(text='Taxa Sucesso (%)', font=dict(size=11)),
                            overlaying='y', side='right',
                            range=[0, max(100, max(taxa_sucesso_vals) * 1.1)],
                            gridcolor='rgba(0,0,0,0.02)'),
                height=300, showlegend=True, plot_bgcolor=COR_BRANCO,
                margin=dict(l=50, r=50, t=50, b=50),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=10)),
                xaxis=dict(tickfont=dict(size=10))
            )
            fig_comparativo.update_traces(marker_line_width=0.5, selector=dict(type='bar'))
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
                st.metric(label="Total Cards", value=f"{total_cards:,}", delta=f"{variacao_total:+.1f}%",
                          delta_color="normal" if variacao_total >= 0 else "inverse",
                          help=f"Anterior: {total_cards_anterior:,}")
            with col_var2:
                st.metric(label="Validados", value=f"{validados:,}", delta=f"{variacao_validados:+.1f}%",
                          delta_color="normal" if variacao_validados >= 0 else "inverse",
                          help=f"Anterior: {validados_anterior:,}")
            with col_var3:
                st.metric(label="Taxa Sucesso", value=f"{taxa_sucesso:.1f}%", delta=f"{variacao_taxa:+.1f}pp",
                          delta_color="normal" if variacao_taxa >= 0 else "inverse",
                          help=f"Anterior: {taxa_sucesso_anterior:.1f}%")
            st.markdown("---")
        st.markdown("#### 📊 INDICADORES PRINCIPAIS")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📋 Total Cards", total_cards, delta=None, help="Total de cards no período")
        with col2:
            st.metric("✅ Validados", validados, f"{taxa_sucesso:.1f}%",
                      delta_color="normal" if taxa_sucesso >= 90 else "off",
                      help="Cards sincronizados (aprovados)")
        with col3:
            st.metric("🎯 Sem Erro", sem_erro,
                      f"{(sem_erro/validados*100) if validados>0 else 0:.1f}%" if validados > 0 else "0%",
                      help="Aprovação direta na primeira validação")
        with col4:
            st.metric("⚠️ Com Erro", com_erro, f"{taxa_erro:.1f}%" if validados > 0 else "0%",
                      delta_color="inverse", help="Cards que retornaram para ajuste")
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
                    if 'Revisões_Total' in df_filtrado_periodo.columns:
                        media_revisoes = df_filtrado_periodo['Revisões_Total'].mean()
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
            if st.button("📥 **EXPORTAR PDF**", type="primary", use_container_width=True,
                        help="Gerar relatório completo em formato PDF", key="btn_exportar_pdf_final"):
                st.info("""
                📄 **Funcionalidade de PDF em desenvolvimento...**
                Para uma implementação completa, você pode usar:
                - `fpdf` ou `reportlab` para gerar PDFs
                - `weasyprint` para converter HTML para PDF
                - `pdfkit` (requer wkhtmltopdf)
                """)
        with col_fechar:
            if st.button("✕ **FECHAR**", type="secondary", use_container_width=True, key="btn_fechar_final"):
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
    tab_principal, tab_mapa, tab_ipe, tab_estatistica = st.tabs(["📊 Principal", "🗺️ Mapa", "📈 KPI", "📈 Análise Estatística"])
    with tab_principal:
        st.markdown("## 📊 Base de Dados")
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
            st.markdown(criar_card_indicador_simples(total_atual, "Total de Demandas", "📋"), unsafe_allow_html=True)
        with col2:
            if 'Status' in df.columns:
                sincronizados = len(df[df['Status'] == 'Sincronizado'])
                st.markdown(criar_card_indicador_simples(sincronizados, "Sincronizados", "✅"), unsafe_allow_html=True)
        with col3:
            if 'Revisões_Total' in df.columns:
                total_revisoes = int(df['Revisões_Total'].sum())
                st.markdown(criar_card_indicador_simples(total_revisoes, "Total de Revisões", "📝"), unsafe_allow_html=True)
        st.markdown("---")
        tab1, tab2, tab3, tab4 = st.tabs([
            "📅 Evolução de Demandas",
            "📊 Análise de Revisões",
            "📈 Sincronização Diária",
            "🏆 Análise Avançada SRE"
        ])
        with tab1:
            col_titulo, col_seletor = st.columns([3, 1])
            with col_titulo:
                st.markdown(f'<div class="section-title">📅 EVOLUÇÃO DE DEMANDAS POR MÊS</div>', unsafe_allow_html=True)
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
                    demandas_completas = pd.merge(todos_meses, demandas_por_mes, on='Mês_Num', how='left')
                    demandas_completas['Quantidade'] = demandas_completas['Quantidade'].fillna(0).astype(int)
                    fig_mes = go.Figure()
                    fig_mes.add_trace(go.Scatter(
                        x=demandas_completas['Nome_Mês'], y=demandas_completas['Quantidade'],
                        mode='lines+markers+text', name='Demandas',
                        line=dict(color=COR_AZUL_ESCURO, width=3),
                        marker=dict(size=10, color=COR_AZUL_PETROLEO),
                        text=demandas_completas['Quantidade'], textposition='top center',
                        textfont=dict(size=12, color=COR_AZUL_ESCURO)
                    ))
                    fig_mes.update_layout(
                        title=f"Demandas em {ano_selecionado}", xaxis_title="Mês",
                        yaxis_title="Número de Demandas", plot_bgcolor=COR_BRANCO,
                        height=450, showlegend=False, margin=dict(t=50, b=50, l=50, r=50),
                        xaxis=dict(gridcolor='rgba(0,0,0,0.05)', tickmode='array',
                                   tickvals=list(range(12)), ticktext=ordem_meses_abreviados),
                        yaxis=dict(gridcolor='rgba(0,0,0,0.05)', rangemode='tozero')
                    )
                    total_ano = int(demandas_completas['Quantidade'].sum())
                    fig_mes.add_annotation(
                        x=0.5, y=0.95, xref="paper", yref="paper",
                        text=f"Total no ano: {total_ano:,} demandas", showarrow=False,
                        font=dict(size=12, color=COR_AZUL_ESCURO, weight="bold"),
                        bgcolor="rgba(255,255,255,0.9)", bordercolor=COR_AZUL_ESCURO,
                        borderwidth=1, borderpad=4
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
                    ano_rev = st.selectbox("📅 Filtrar por Ano:", options=anos_opcoes_rev, key="filtro_ano_revisoes")
            with col_rev_filtro2:
                if 'Mês' in df.columns:
                    meses_rev = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_rev = ['Todos os Meses'] + [str(m) for m in meses_rev]
                    mes_rev = st.selectbox("📆 Filtrar por Mês:", options=meses_opcoes_rev, key="filtro_mes_revisoes")
            df_rev = df.copy()
            if ano_rev != 'Todos os Anos':
                df_rev = df_rev[df_rev['Ano'] == int(ano_rev)]
            if mes_rev != 'Todos os Meses':
                df_rev = df_rev[df_rev['Mês'] == int(mes_rev)]
            if 'Revisões_Total' in df_rev.columns and 'Responsável_Formatado' in df_rev.columns:
                df_com_revisoes = df_rev[df_rev['Revisões_Total'] > 0].copy()
                if not df_com_revisoes.empty:
                    revisoes_por_responsavel = df_com_revisoes.groupby('Responsável_Formatado').agg({
                        'Revisões_Total': 'sum', 'Chamado': 'count'
                    }).reset_index()
                    revisoes_por_responsavel.columns = ['Responsável', 'Total_Revisões', 'Chamados_Com_Revisão']
                    revisoes_por_responsavel = revisoes_por_responsavel.sort_values('Total_Revisões', ascending=False)
                    titulo_rev = 'Top 15 Responsáveis com Mais Revisões'
                    if ano_rev != 'Todos os Anos':
                        titulo_rev += f' - {ano_rev}'
                    if mes_rev != 'Todos os Meses':
                        meses_nomes = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                                       5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                                       9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
                        titulo_rev += f' - {meses_nomes[int(mes_rev)]}'
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
                        textposition='outside', marker_color=colors[:15],
                        marker_line_color=COR_PRETO_SUAVE, marker_line_width=1.5, opacity=0.8
                    ))
                    fig_revisoes.update_layout(
                        title=titulo_rev, xaxis_title='Responsável', yaxis_title='Total de Revisões',
                        plot_bgcolor=COR_BRANCO, height=500, showlegend=False,
                        margin=dict(t=50, b=100, l=50, r=50),
                        xaxis=dict(tickangle=45, gridcolor='rgba(0,0,0,0.05)'),
                        yaxis=dict(gridcolor='rgba(0,0,0,0.05)')
                    )
                    st.plotly_chart(fig_revisoes, use_container_width=True)
        with tab3:
            st.markdown(f'<div class="section-title">📈 CHAMADOS SINCRONIZADOS POR DIA - ANÁLISE COMPLETA</div>', unsafe_allow_html=True)
            col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
            with col_filtro1:
                if 'Ano' in df.columns:
                    anos_sinc = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_sinc = ['Todos os Anos'] + list(anos_sinc)
                    ano_sinc = st.selectbox("📅 Ano:", options=anos_opcoes_sinc, key="filtro_ano_sinc")
            with col_filtro2:
                if 'Mês' in df.columns:
                    meses_sinc = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_sinc = ['Todos os Meses'] + [str(m) for m in meses_sinc]
                    mes_sinc = st.selectbox("📆 Mês:", options=meses_opcoes_sinc, key="filtro_mes_sinc")
            with col_filtro3:
                if 'SRE' in df.columns:
                    sres_sinc = ['Todos os SREs'] + sorted(df['SRE'].dropna().unique())
                    sre_sinc = st.selectbox("🔧 SRE:", options=sres_sinc, key="filtro_sre_sinc")
            with col_filtro4:
                if 'Empresa' in df.columns:
                    empresas_sinc = ['Todas Empresas'] + sorted(df['Empresa'].dropna().unique())
                    empresa_sinc = st.selectbox("🏢 Empresa:", options=empresas_sinc, key="filtro_empresa_sinc")
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
                df_sincronizados = df_sinc[df_sinc['Status'] == 'Sincronizado'].copy()
                if not df_sincronizados.empty:
                    df_sincronizados['Data'] = df_sincronizados['Criado'].dt.date
                    df_sincronizados['Ano_Mes'] = df_sincronizados['Criado'].dt.strftime('%Y-%m')
                    df_sincronizados['Dia_Semana'] = df_sincronizados['Criado'].dt.day_name()
                    df_sincronizados['Semana_Ano'] = df_sincronizados['Criado'].dt.isocalendar().week
                    df_sincronizados['Dia_Mes'] = df_sincronizados['Criado'].dt.day
                    dias_semana_map = {'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
                                       'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
                    df_sincronizados['Dia_Semana_PT'] = df_sincronizados['Dia_Semana'].map(dias_semana_map)
                    df_sincronizados = df_sincronizados.sort_values('Criado')
                    sincronizados_por_dia = df_sincronizados.groupby('Data').size().reset_index()
                    sincronizados_por_dia.columns = ['Data', 'Quantidade']
                    sincronizados_por_dia = sincronizados_por_dia.sort_values('Data')
                    st.markdown("### 📊 Indicadores Principais")
                    total_sincronizados = int(sincronizados_por_dia['Quantidade'].sum())
                    media_diaria = sincronizados_por_dia['Quantidade'].mean()
                    max_dia = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmax()]
                    min_dia = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmin()]
                    dias_com_zero = len(sincronizados_por_dia[sincronizados_por_dia['Quantidade'] == 0])
                    dias_trabalhados = len(sincronizados_por_dia)
                    variacao = 0
                    if len(sincronizados_por_dia) > 1:
                        primeiro_valor = sincronizados_por_dia['Quantidade'].iloc[0]
                        ultimo_valor = sincronizados_por_dia['Quantidade'].iloc[-1]
                        if primeiro_valor > 0:
                            variacao = ((ultimo_valor - primeiro_valor) / primeiro_valor) * 100
                    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
                    with col_kpi1:
                        st.metric("✅ Total Sincronizado", f"{total_sincronizados:,}",
                                  f"{variacao:+.1f}%" if variacao != 0 else None,
                                  delta_color="normal" if variacao >= 0 else "inverse")
                    with col_kpi2:
                        st.metric("📊 Média Diária", f"{media_diaria:.1f}", f"Dias: {dias_trabalhados}")
                    with col_kpi3:
                        st.metric("📈 Dia com Mais Sinc.", f"{int(max_dia['Quantidade']):,}", f"{max_dia['Data'].strftime('%d/%m')}")
                    with col_kpi4:
                        st.metric("⚠️ Dias sem Sinc.", f"{dias_com_zero}",
                                  f"{min_dia['Data'].strftime('%d/%m')}: {int(min_dia['Quantidade']):,}")
                    with st.expander("📋 Visualização Detalhada por Dia", expanded=False):
                        sincronizados_por_dia['Dia_Semana'] = sincronizados_por_dia['Data'].apply(lambda x: x.strftime('%A'))
                        sincronizados_por_dia['Dia_Semana_PT'] = sincronizados_por_dia['Dia_Semana'].map(dias_semana_map)
                        sincronizados_por_dia['Diferenca'] = sincronizados_por_dia['Quantidade'].diff()
                        sincronizados_por_dia['Variacao_%'] = (sincronizados_por_dia['Diferenca'] / sincronizados_por_dia['Quantidade'].shift(1) * 100).round(1)
                        sincronizados_por_dia['Media_Movel_7'] = sincronizados_por_dia['Quantidade'].rolling(window=7, min_periods=1).mean().round(1)
                        tabela_detalhada = sincronizados_por_dia.copy()
                        tabela_detalhada['Data_Formatada'] = tabela_detalhada['Data'].apply(lambda x: x.strftime('%d/%m/%Y'))
                        tabela_detalhada = tabela_detalhada.sort_values('Data', ascending=False)
                        colunas_exibir = ['Data_Formatada', 'Dia_Semana_PT', 'Quantidade',
                                          'Diferenca', 'Variacao_%', 'Media_Movel_7']
                        st.dataframe(tabela_detalhada[colunas_exibir], use_container_width=True,
                                     column_config={
                                         "Data_Formatada": st.column_config.TextColumn("Data"),
                                         "Dia_Semana_PT": st.column_config.TextColumn("Dia Semana"),
                                         "Quantidade": st.column_config.NumberColumn("Sinc. do Dia", format="%d"),
                                         "Diferenca": st.column_config.NumberColumn("Δ vs Dia Anterior", format="%+d"),
                                         "Variacao_%": st.column_config.NumberColumn("Variação %", format="%+.1f%%"),
                                         "Media_Movel_7": st.column_config.NumberColumn("Média 7 dias", format="%.1f")
                                     })
                    st.markdown("### 📅 Sincronizações por Dia")
                    anos_disponiveis = sorted(df_sincronizados['Criado'].dt.year.unique())
                    df_semanal_real = df_sincronizados.copy()
                    if 2026 not in anos_disponiveis:
                        df_semanal_real = df_semanal_real[df_semanal_real['Criado'].dt.year != 2026]
                    df_semanal_real['Data_Formatada'] = df_semanal_real['Criado'].dt.strftime('%d/%m/%Y')
                    sinc_por_dia = df_semanal_real.groupby('Data').size().reset_index()
                    sinc_por_dia.columns = ['Data', 'Quantidade']
                    sinc_por_dia = sinc_por_dia.sort_values('Data')
                    if len(sinc_por_dia) > 30:
                        sinc_por_dia_recente = sinc_por_dia.tail(30)
                    else:
                        sinc_por_dia_recente = sinc_por_dia.copy()
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
                            red = int(0 * normalized + 0 * (1 - normalized))
                            green = int(89 * normalized + 89 * (1 - normalized))
                            blue = int(115 * normalized + 115 * (1 - normalized))
                            colors.append(f'rgb({red}, {green}, {blue})')
                    fig_dias.add_trace(go.Bar(
                        x=sinc_por_dia_recente['Data_Formatada'], y=sinc_por_dia_recente['Quantidade'],
                        name='Sincronizações', text=sinc_por_dia_recente['Quantidade'],
                        textposition='outside', marker_color=colors,
                        marker_line_color=COR_AZUL_PETROLEO, marker_line_width=1.5, opacity=0.8
                    ))
                    fig_dias.update_layout(
                        title='Sincronizações por Dia (Período Recente)' if len(sinc_por_dia) > 30 else 'Sincronizações por Dia',
                        xaxis_title='Data (Dia/Mês)', yaxis_title='Quantidade de Sincronizações',
                        height=400, plot_bgcolor=COR_BRANCO, showlegend=False,
                        margin=dict(t=50, b=50, l=50, r=50),
                        xaxis=dict(gridcolor='rgba(0,0,0,0.05)', tickangle=45),
                        yaxis=dict(gridcolor='rgba(0,0,0,0.05)', rangemode='tozero')
                    )
                    st.plotly_chart(fig_dias, use_container_width=True)
                    col_dia1, col_dia2, col_dia3 = st.columns(3)
                    with col_dia1:
                        dia_max = sinc_por_dia.loc[sinc_por_dia['Quantidade'].idxmax()]
                        st.metric("📈 Melhor Dia", dia_max['Data'].strftime('%d/%m/%Y'), f"{int(dia_max['Quantidade'])} sinc.")
                    with col_dia2:
                        dia_min = sinc_por_dia.loc[sinc_por_dia['Quantidade'].idxmin()]
                        st.metric("📉 Pior Dia", dia_min['Data'].strftime('%d/%m/%Y'), f"{int(dia_min['Quantidade'])} sinc.")
                    with col_dia3:
                        media_dia_total = sinc_por_dia['Quantidade'].mean()
                        st.metric("📊 Média por Dia", f"{media_dia_total:.1f}")
                    st.markdown("### 👥 Sincronizações por SRE")
                    if 'SRE' in df_sincronizados.columns:
                        sre_por_dia = df_sincronizados.groupby(['Data', 'SRE']).size().reset_index()
                        sre_por_dia.columns = ['Data', 'SRE', 'Quantidade']
                        pivot_sre = sre_por_dia.pivot_table(index='Data', columns='SRE',
                                                            values='Quantidade', aggfunc='sum', fill_value=0).reset_index()
                        fig_sre = go.Figure()
                        for sre in pivot_sre.columns[1:]:
                            fig_sre.add_trace(go.Bar(
                                x=pivot_sre['Data'], y=pivot_sre[sre], name=sre,
                                hovertemplate='Data: %{x|%d/%m/%Y}<br>SRE: ' + sre + '<br>Quantidade: %{y}<extra></extra>'
                            ))
                        fig_sre.update_layout(
                            title='Sincronizações por SRE (Stacked)', barmode='stack', height=400,
                            xaxis_title="Data", yaxis_title="Quantidade de Sincronizações",
                            xaxis=dict(tickformat='%d/%m', tickangle=45),
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        st.plotly_chart(fig_sre, use_container_width=True)
                    st.markdown("### 📝 Sincronizações por Tipo de Chamado")
                    if 'Tipo_Chamado' in df_sincronizados.columns:
                        col_tipo1, col_tipo2 = st.columns([2, 1])
                        with col_tipo1:
                            tipo_por_dia = df_sincronizados.groupby(['Data', 'Tipo_Chamado']).size().reset_index()
                            tipo_por_dia.columns = ['Data', 'Tipo', 'Quantidade']
                            pivot_tipo = tipo_por_dia.pivot_table(index='Data', columns='Tipo',
                                                                  values='Quantidade', aggfunc='sum', fill_value=0).reset_index()
                            fig_tipo = go.Figure()
                            top_tipos = df_sincronizados['Tipo_Chamado'].value_counts().head(5).index.tolist()
                            for tipo in top_tipos:
                                if tipo in pivot_tipo.columns:
                                    fig_tipo.add_trace(go.Scatter(
                                        x=pivot_tipo['Data'], y=pivot_tipo[tipo],
                                        mode='lines+markers', name=tipo,
                                        hovertemplate='Data: %{x|%d/%m/%Y}<br>Tipo: ' + tipo + '<br>Quantidade: %{y}<extra></extra>'
                                    ))
                            fig_tipo.update_layout(
                                title='Evolução dos 5 Tipos Mais Frequentes', height=350,
                                xaxis_title="Data", yaxis_title="Quantidade",
                                xaxis=dict(tickformat='%d/%m', tickangle=45), showlegend=True
                            )
                            st.plotly_chart(fig_tipo, use_container_width=True)
                        with col_tipo2:
                            tipo_dist = df_sincronizados['Tipo_Chamado'].value_counts().reset_index()
                            tipo_dist.columns = ['Tipo', 'Quantidade']
                            tipo_dist['Percentual'] = (tipo_dist['Quantidade'] / total_sincronizados * 100).round(1)
                            st.markdown("**📊 Distribuição por Tipo:**")
                            for idx, row in tipo_dist.head(5).iterrows():
                                st.markdown(f"""
                                <div style="padding: 8px; margin-bottom: 5px; background: {COR_CINZA_FUNDO}; border-radius: 5px;">
                                    <strong>{row['Tipo']}</strong><br>
                                    <small>{row['Quantidade']} ({row['Percentual']}%)</small>
                                </div>
                                """, unsafe_allow_html=True)
                    st.markdown("### 🏢 Sincronizações por Empresa")
                    if 'Empresa' in df_sincronizados.columns:
                        col_empresa1, col_empresa2 = 
