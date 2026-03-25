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
import json
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
# CSS PERSONALIZADO
# ============================================
st.markdown(f"""
<style>
    .stApp {{
        background-color: {COR_CINZA_FUNDO};
    }}
    
    .main-header-monitoring {{
        background: {COR_CINZA_FUNDO};
        padding: 1.2rem 2rem;
        margin-bottom: 1.5rem;
        border-bottom: 4px solid {COR_AZUL_ESCURO};
        border-radius: 0;
    }}
    
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
    
    .footer {{
        text-align: center;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 2px solid {COR_CINZA_BORDA};
        color: {COR_CINZA_TEXTO};
        font-size: 0.85rem;
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

# ============================================
# FUNÇÕES DO MAPA
# ============================================

def criar_geojson_fallback():
    """Cria um GeoJSON simples como fallback com as coordenadas dos estados"""
    geojson_fallback = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # Dados aproximados dos estados (centroides)
    estados = {
        'AC': [-9.0, -70.0], 'AL': [-9.5, -36.5], 'AP': [1.0, -52.0], 'AM': [-3.0, -63.0],
        'BA': [-12.5, -41.5], 'CE': [-5.0, -39.0], 'DF': [-15.5, -47.5], 'ES': [-19.5, -40.5],
        'GO': [-16.0, -49.0], 'MA': [-5.0, -45.0], 'MT': [-12.5, -55.0], 'MS': [-20.5, -54.5],
        'MG': [-19.5, -44.5], 'PA': [-5.0, -53.0], 'PB': [-7.0, -36.5], 'PR': [-24.5, -51.5],
        'PE': [-8.5, -38.0], 'PI': [-7.0, -42.0], 'RJ': [-22.5, -43.0], 'RN': [-5.5, -36.0],
        'RS': [-30.0, -53.0], 'RO': [-10.5, -63.0], 'RR': [2.0, -62.0], 'SC': [-27.0, -50.5],
        'SP': [-23.5, -46.5], 'SE': [-10.5, -37.0], 'TO': [-10.0, -48.0]
    }
    
    for sigla, coords in estados.items():
        geojson_fallback['features'].append({
            "type": "Feature",
            "properties": {
                "sigla": sigla,
                "name": sigla
            },
            "geometry": {
                "type": "Point",
                "coordinates": [coords[1], coords[0]]
            }
        })
    
    return geojson_fallback

@st.cache_resource(ttl=86400)
def carregar_geojson_local():
    """Carrega o GeoJSON dos estados brasileiros com fallback"""
    try:
        caminho_geojson = "estados_brasil.geojson"
        
        if os.path.exists(caminho_geojson):
            with open(caminho_geojson, 'r', encoding='utf-8') as f:
                geojson = json.load(f)
            
            if 'features' in geojson and len(geojson['features']) > 0:
                primeira_feature = geojson['features'][0]
                if 'properties' in primeira_feature and 'sigla' in primeira_feature['properties']:
                    return geojson
                else:
                    st.warning("⚠️ GeoJSON não contém a propriedade 'sigla'. Usando fallback.")
                    return criar_geojson_fallback()
            else:
                st.warning("⚠️ GeoJSON vazio ou inválido. Usando fallback.")
                return criar_geojson_fallback()
        else:
            st.info(f"ℹ️ Arquivo '{caminho_geojson}' não encontrado. Usando visualização alternativa.")
            return criar_geojson_fallback()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar GeoJSON: {e}")
        return criar_geojson_fallback()

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

def criar_mapa_coropletico(df_mapa, geojson):
    """Cria o mapa coroplético usando GeoJSON"""
    if df_mapa.empty:
        return None
    
    if geojson is None:
        return criar_mapa_bolhas_alternativo(df_mapa)
    
    try:
        fig = px.choropleth(
            df_mapa,
            geojson=geojson,
            locations='sigla',
            color='sincronismos',
            featureidkey='properties.sigla',
            hover_name='estado',
            hover_data={
                'empresa_nome': True,
                'sincronismos': True,
                'regiao': True,
                'sigla': False
            },
            color_continuous_scale=[
                (0.0, "#FFE5E5"),
                (0.2, "#FFB3B3"),
                (0.4, "#FF8080"),
                (0.6, "#FF4D4D"),
                (0.8, "#E63946"),
                (1.0, "#C1121F")
            ],
            title="<b>Mapa de Sincronizações por Estado</b>",
            labels={'sincronismos': 'Nº de Sincronizações'}
        )
        
        fig.update_geos(
            fitbounds="locations",
            visible=False,
            projection_type="mercator"
        )
        
        fig.update_layout(
            height=600,
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            coloraxis_colorbar=dict(
                title="Sincronizações",
                thicknessmode="pixels",
                thickness=20,
                lenmode="pixels",
                len=300,
                yanchor="middle",
                y=0.5
            )
        )
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Erro ao criar mapa: {e}")
        return criar_mapa_bolhas_alternativo(df_mapa)

def criar_mapa_bolhas_alternativo(df_mapa):
    """Cria um mapa de bolhas como alternativa"""
    if df_mapa.empty:
        return None
    
    df_bolhas = df_mapa[df_mapa['sincronismos'] > 0].copy()
    
    if df_bolhas.empty:
        return None
    
    fig = px.scatter_geo(
        df_bolhas,
        lat='latitude',
        lon='longitude',
        size='sincronismos',
        hover_name='estado',
        text='sigla',
        color='sincronismos',
        color_continuous_scale='Reds',
        size_max=50,
        title="<b>Mapa de Bolhas - Volume de Sincronizações</b>",
        labels={'sincronismos': 'Nº de Sincronizações'}
    )
    
    fig.update_geos(
        projection_type="natural earth",
        center=dict(lon=-55, lat=-14),
        projection_scale=3,
        showcountries=True,
        countrycolor='rgba(0,0,0,0.4)',
        showsubunits=True,
        subunitcolor='rgba(0,0,0,0.6)',
        showland=True,
        landcolor='rgb(245, 245, 245)',
        showocean=True,
        oceancolor='rgba(200, 220, 240, 0.3)'
    )
    
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title="Sincronizações",
            thicknessmode="pixels",
            thickness=20
        )
    )
    
    return fig

def criar_grafico_barras(df_mapa):
    """Cria gráfico de barras comparativo"""
    if df_mapa.empty:
        return None
    
    df_barras = df_mapa.sort_values('sincronismos', ascending=True)
    
    fig = go.Figure()
    
    cores = []
    for val in df_barras['sincronismos']:
        if val == 0:
            cores.append('#FFE5E5')
        elif val < 10:
            cores.append('#FFB3B3')
        elif val < 30:
            cores.append('#FF8080')
        else:
            cores.append('#FF4D4D')
    
    fig.add_trace(go.Bar(
        x=df_barras['sincronismos'],
        y=df_barras['empresa_nome'],
        orientation='h',
        text=df_barras['sincronismos'],
        textposition='outside',
        marker_color=cores,
        marker_line_color='#FF1A1A',
        marker_line_width=1,
        hovertemplate="Empresa: %{y}<br>Sincronizações: %{x}<extra></extra>"
    ))
    
    fig.update_layout(
        title="<b>Ranking de Sincronizações por Empresa</b>",
        xaxis_title="Número de Sincronizações",
        yaxis_title="",
        height=400,
        showlegend=False,
        plot_bgcolor=COR_BRANCO,
        xaxis=dict(gridcolor=COR_CINZA_BORDA),
        yaxis=dict(gridcolor=COR_CINZA_BORDA)
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
# HEADER
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
            <h1 style="color: {COR_BRANCO}; margin: 0; font-size: 1.6rem; font-weight: 600;">
                📊 ESTEIRA ADMS
            </h1>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 0.85rem;">
                Acompanhamento de Demandas - EAC | EMR | EMS | EMT | EPB | ERO | ESE | ESS | ETO
            </p>
        </div>
        <div style="text-align: right;">
            <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 0.85rem;">
                Dashboard de Performance
            </p>
            <p style="color: rgba(255,255,255,0.8); margin: 0.2rem 0 0 0; font-size: 0.75rem;">
                v5.5 | Sistema de Performance SRE
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 0.3rem 0 0 0; font-size: 0.7rem;">
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
            st.markdown(criar_card_indicador_simples(total_atual, "Total de Demandas", "📋"), unsafe_allow_html=True)
        
        with col2:
            if 'Status' in df.columns:
                sincronizados = len(df[df['Status'] == 'Sincronizado'])
                st.markdown(criar_card_indicador_simples(sincronizados, "Sincronizados", "✅"), unsafe_allow_html=True)
        
        with col3:
            if 'Revisões' in df.columns:
                total_revisoes = int(df['Revisões'].sum())
                st.markdown(criar_card_indicador_simples(total_revisoes, "Total de Revisões", "📝"), unsafe_allow_html=True)
        
        st.markdown("---")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📅 Evolução de Demandas", 
            "📊 Análise de Revisões", 
            "📈 Chamados Sincronizados por Dia",
            "🏆 Performance dos SREs"
        ])
        
        with tab1:
            col_titulo, col_seletor = st.columns([3, 1])
            
            with col_titulo:
                st.markdown(f'<div class="section-title">📅 EVOLUÇÃO DE DEMANDAS POR MÊS</div>', unsafe_allow_html=True)
            
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
                        line=dict(color=COR_AZUL_ESCURO, width=3),
                        marker=dict(size=10, color=COR_AZUL_PETROLEO),
                        text=demandas_completas['Quantidade'],
                        textposition='top center'
                    ))
                    
                    fig_mes.update_layout(
                        title=f"Demandas em {ano_selecionado}",
                        xaxis_title="Mês",
                        yaxis_title="Número de Demandas",
                        plot_bgcolor=COR_BRANCO,
                        height=450,
                        showlegend=False,
                        xaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
                        yaxis=dict(gridcolor='rgba(0,0,0,0.05)', rangemode='tozero')
                    )
                    
                    total_ano = int(demandas_completas['Quantidade'].sum())
                    fig_mes.add_annotation(
                        x=0.5, y=0.95, xref="paper", yref="paper",
                        text=f"Total no ano: {total_ano:,} demandas",
                        showarrow=False,
                        font=dict(size=12, color=COR_AZUL_ESCURO)
                    )
                    
                    st.plotly_chart(fig_mes, use_container_width=True)
        
        with tab2:
            st.markdown(f'<div class="section-title">📊 REVISÕES POR RESPONSÁVEL</div>', unsafe_allow_html=True)
            
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
                        marker_color=COR_VERMELHO,
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
                        xaxis=dict(tickangle=45, gridcolor='rgba(0,0,0,0.05)'),
                        yaxis=dict(gridcolor='rgba(0,0,0,0.05)')
                    )
                    
                    st.plotly_chart(fig_revisoes, use_container_width=True)
        
        with tab3:
            st.markdown(f'<div class="section-title">📈 CHAMADOS SINCRONIZADOS POR DIA</div>', unsafe_allow_html=True)
            
            if 'Status' in df.columns and 'Criado' in df.columns:
                df_sincronizados = df[df['Status'] == 'Sincronizado'].copy()
                
                if not df_sincronizados.empty:
                    df_sincronizados['Data'] = df_sincronizados['Criado'].dt.date
                    sincronizados_por_dia = df_sincronizados.groupby('Data').size().reset_index()
                    sincronizados_por_dia.columns = ['Data', 'Quantidade']
                    sincronizados_por_dia = sincronizados_por_dia.sort_values('Data')
                    
                    st.markdown("### 📊 Indicadores Principais")
                    
                    total_sincronizados = int(sincronizados_por_dia['Quantidade'].sum())
                    media_diaria = sincronizados_por_dia['Quantidade'].mean()
                    max_dia = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmax()]
                    
                    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
                    
                    with col_kpi1:
                        st.metric("✅ Total Sincronizado", f"{total_sincronizados:,}")
                    
                    with col_kpi2:
                        st.metric("📊 Média Diária", f"{media_diaria:.1f}")
                    
                    with col_kpi3:
                        st.metric("📈 Dia com Mais Sinc.", f"{int(max_dia['Quantidade']):,}", f"{max_dia['Data'].strftime('%d/%m')}")
                    
                    sinc_por_dia_recente = sincronizados_por_dia.tail(30)
                    sinc_por_dia_recente['Data_Formatada'] = sinc_por_dia_recente['Data'].apply(lambda x: x.strftime('%d/%m'))
                    
                    fig_dias = go.Figure()
                    
                    fig_dias.add_trace(go.Bar(
                        x=sinc_por_dia_recente['Data_Formatada'],
                        y=sinc_por_dia_recente['Quantidade'],
                        name='Sincronizações',
                        text=sinc_por_dia_recente['Quantidade'],
                        textposition='outside',
                        marker_color=COR_VERDE_ESCURO,
                        marker_line_color=COR_AZUL_PETROLEO,
                        marker_line_width=1.5,
                        opacity=0.8
                    ))
                    
                    fig_dias.update_layout(
                        title='Sincronizações por Dia (Últimos 30 dias)',
                        xaxis_title='Data (Dia/Mês)',
                        yaxis_title='Quantidade de Sincronizações',
                        height=400,
                        plot_bgcolor=COR_BRANCO,
                        showlegend=False,
                        xaxis=dict(tickangle=45, gridcolor='rgba(0,0,0,0.05)'),
                        yaxis=dict(gridcolor='rgba(0,0,0,0.05)', rangemode='tozero')
                    )
                    
                    st.plotly_chart(fig_dias, use_container_width=True)
        
        with tab4:
            st.markdown(f'<div class="section-title">🏆 PERFORMANCE DOS SREs</div>', unsafe_allow_html=True)
            
            if 'SRE' in df.columns and 'Status' in df.columns:
                df_sincronizados = df[df['Status'] == 'Sincronizado'].copy()
                
                if not df_sincronizados.empty and 'SRE' in df_sincronizados.columns:
                    sinc_por_sre = df_sincronizados.groupby('SRE').size().reset_index()
                    sinc_por_sre.columns = ['SRE', 'Sincronizados']
                    sinc_por_sre = sinc_por_sre.sort_values('Sincronizados', ascending=False)
                    
                    fig_sinc_bar = go.Figure()
                    
                    fig_sinc_bar.add_trace(go.Bar(
                        x=sinc_por_sre['SRE'].head(10),
                        y=sinc_por_sre['Sincronizados'].head(10),
                        name='Sincronizados',
                        text=sinc_por_sre['Sincronizados'].head(10),
                        textposition='outside',
                        marker_color=COR_AZUL_ESCURO,
                        marker_line_color=COR_AZUL_PETROLEO,
                        marker_line_width=1.5,
                        opacity=0.8
                    ))
                    
                    fig_sinc_bar.update_layout(
                        title='Sincronizados por SRE',
                        xaxis_title='SRE',
                        yaxis_title='Número de Sincronizados',
                        plot_bgcolor=COR_BRANCO,
                        height=500,
                        showlegend=False,
                        xaxis=dict(tickangle=45, gridcolor='rgba(0,0,0,0.05)'),
                        yaxis=dict(gridcolor='rgba(0,0,0,0.05)', rangemode='tozero')
                    )
                    
                    st.plotly_chart(fig_sinc_bar, use_container_width=True)
    
    with tab_mapa:
        st.markdown("## 🗺️ Mapa de Sincronizações por Empresa")
        
        with st.spinner("Carregando mapa do Brasil..."):
            geojson = carregar_geojson_local()
        
        if geojson:
            st.success("✅ Mapa carregado com sucesso!")
        
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
        
        tipo_mapa = st.radio(
            "🗺️ Tipo de Visualização",
            options=["Coroplético (Estados)", "Bolhas (Pontos)"],
            index=0,
            horizontal=True,
            key="mapa_tipo"
        )
        
        df_mapa, total_sinc_filtrado = processar_dados_mapa(
            df,
            empresas_selecionadas=empresas_selecionadas_mapa,
            ano_filtro=ano_filtro_mapa,
            mes_filtro=mes_filtro_mapa
        )
        
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
        
        st.markdown("---")
        
        if tipo_mapa == "Coroplético (Estados)":
            st.markdown('<div class="section-title">🗺️ MAPA COROPLÉTICO - ESTADOS BRASILEIROS</div>', unsafe_allow_html=True)
            
            fig_coropletico = criar_mapa_coropletico(df_mapa, geojson)
            if fig_coropletico:
                st.plotly_chart(fig_coropletico, use_container_width=True, config={'displayModeBar': True})
                st.caption("📌 Mapa baseado em dados geoespaciais dos estados brasileiros")
        
        elif tipo_mapa == "Bolhas (Pontos)":
            st.markdown('<div class="section-title">📍 MAPA DE BOLHAS - COM DIVISAS DOS ESTADOS</div>', unsafe_allow_html=True)
            
            fig_bolhas = criar_mapa_bolhas_alternativo(df_mapa)
            if fig_bolhas:
                st.plotly_chart(fig_bolhas, use_container_width=True, config={'displayModeBar': True})
                st.caption("📌 As bolhas representam o volume de sincronizações por empresa")
        
        st.markdown('<div class="section-title" style="margin-top: 2rem;">📊 RANKING DE SINCRONIZAÇÕES</div>', unsafe_allow_html=True)
        
        fig_barras = criar_grafico_barras(df_mapa)
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True, config={'displayModeBar': True})
        
        with st.expander("📋 Ver Detalhes por Empresa", expanded=False):
            if not df_mapa.empty:
                tabela_detalhes = df_mapa[['empresa_nome', 'sigla', 'regiao', 'sincronismos']].copy()
                tabela_detalhes.columns = ['Empresa', 'UF', 'Região', 'Sincronizações']
                tabela_detalhes = tabela_detalhes.sort_values('Sincronizações', ascending=False)
                
                st.dataframe(tabela_detalhes, use_container_width=True)

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
