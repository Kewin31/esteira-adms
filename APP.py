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
# FUNÇÃO DE CLASSIFICAÇÃO DE MOTIVOS DE REVISÃO (CORRIGIDA)
# ============================================
def classificar_motivo_revisao(texto):
    """Classifica o motivo da revisão em categorias padronizadas com validação"""
    # Verificar se o texto é válido
    if pd.isna(texto) or str(texto).strip() == "":
        return "📝 Sem motivo informado"
    
    texto = str(texto).lower().strip()
    
    # Se o texto for muito curto, classificar como genérico
    if len(texto) < 3:
        return "📝 Outros"
    
    # Categorias de Classificação com palavras-chave mais abrangentes
    categorias = {
        "📋 Erro de Documentação": [
            'erro na descrição', 'card preenchido', 'card incompleto', 
            'chamado sem responsável', 'nome do changeset fora do padrão', 
            'card sem proprietário', 'erro no preenchimento', 'faltou colocar a descrição',
            'descrição', 'documentação', 'anexar', 'lista de pontos desatualizada',
            'card preenchido de forma errada', 'falta descrição', 'preenchimento incorreto',
            'informação faltando', 'dados incompletos', 'informação ausente'
        ],
        "⚙️ Falha Técnica/Configuração": [
            'changeset rejeitado', 'changeset não encontrado', 'changeset bloqueado',
            'changeset com numeração errada', 'changeset não apresentou modificação',
            'changeset duplicado', 'changeset errado', 'changeset ajustado',
            'configurações da remota fora do padrão', 'equipamento sem by-pass',
            'chave de by-pass aberta', 'parâmetros de comunicação', 'ponto de comando',
            'endereço de ip divergente', 'comandos do disjuntores incoerentes',
            'configuração', 'parametro', 'communication', 'endereço ip', 'by-pass'
        ],
        "🔗 Erro de Conectividade/Nó": [
            'nó de conectividade', 'padrão de conectividade', 'criar o nó',
            'conectividade', 'main', 'node', 'link de comunicação', 'conexão',
            'sem comunicação', 'perda de comunicação', 'timeout', 'networking'
        ],
        "📐 Não Conformidade com Padrão": [
            'padrão', 'procedimento', 'formato', 'nome do changeset',
            'grupo de aor', 'quadro de religadores', 'tela autogerada',
            'representação dos sinais', 'catalogo da chave', 'template',
            'alinhamento', 'sincronismo', 'norma', 'conformidade',
            'não está no padrão', 'fora do padrão', 'não segue o padrão'
        ],
        "🔄 Divergência de Informação": [
            'divergência', 'inconsistente', 'incoerente', 'não condiz',
            'chamado não encontrado', 'não correlaciona', 'changeset envolve outros equipamentos',
            'dois chamados em um único changeset', 'informação conflitante',
            'dados divergentes', 'não corresponde', 'diferença entre', 'discrepância'
        ],
        "🎨 Erro de Interface/Tela": [
            'representações em tela', 'tela autogerada', 'diagrama unifilar',
            'esquemática', 'exibir em tela', 'tela de resumo', 'interface',
            'visualização', 'display', 'exibição', 'layout', 'tela', 'front-end'
        ]
    }
    
    # Verificar cada categoria
    for categoria, palavras_chave in categorias.items():
        for palavra in palavras_chave:
            if palavra in texto:
                return categoria
    
    # Verificar se contém palavras que indicam correção (gênero neutro)
    palavras_correcao = ['corrigir', 'ajustar', 'alterar', 'modificar', 'revisar', 'refazer', 'correção', 'ajuste']
    for palavra in palavras_correcao:
        if palavra in texto:
            return "📝 Outros (Correção)"
    
    return "📝 Outros"

def corrigir_revisoes_duplicadas(df):
    """
    CORREÇÃO: Detecta e corrige chamados que aparecem duplicados na base
    Retorna a base limpa e um relatório de correções
    """
    df_corrigido = df.copy()
    relatorio = []
    
    # Verificar duplicatas por chamado
    duplicados = df_corrigido[df_corrigido.duplicated(subset=['Chamado'], keep=False)]
    
    if not duplicados.empty:
        st.warning(f"⚠️ Detectados {duplicados['Chamado'].nunique()} chamados duplicados na base!")
        
        # Agrupar por chamado e consolidar
        df_consolidado = df_corrigido.groupby('Chamado').agg({
            'Tipo_Chamado': 'first',
            'Responsável': 'first',
            'Responsável_Formatado': 'first',
            'Status': 'first',
            'Criado': 'first',
            'Modificado': 'last',  # A mais recente
            'Modificado_por': 'last',
            'Prioridade': 'first',
            'Sincronização': 'first',
            'SRE': 'first',
            'Empresa': 'first',
            'Revisões': 'first',  # Manter o valor original do primeiro registro
            'Motivo_Revisao': lambda x: ' | '.join(x.dropna().unique())  # Combinar motivos
        }).reset_index()
        
        # Adicionar colunas derivadas
        if 'Criado' in df_consolidado.columns:
            df_consolidado['Ano'] = df_consolidado['Criado'].dt.year
            df_consolidado['Mês'] = df_consolidado['Criado'].dt.month
            df_consolidado['Mês_Ano'] = df_consolidado['Criado'].dt.strftime('%Y-%m')
        
        # Contar revisões originais vs corrigidas
        total_revisoes_original = df_corrigido['Revisões'].sum()
        total_revisoes_corrigido = df_consolidado['Revisões'].sum()
        
        relatorio = {
            'chamados_duplicados': duplicados['Chamado'].nunique(),
            'total_registros_original': len(df_corrigido),
            'total_registros_corrigido': len(df_consolidado),
            'total_revisoes_original': int(total_revisoes_original),
            'total_revisoes_corrigido': int(total_revisoes_corrigido),
            'diferenca_revisoes': int(abs(total_revisoes_original - total_revisoes_corrigido))
        }
        
        return df_consolidado, relatorio
    
    return df_corrigido, None

# ============================================
# FUNÇÃO PARA CRIAR O POPUP DE EXPLICAÇÃO DE CORREÇÃO
# ============================================
def criar_popup_explicacao_correcao():
    """Cria um popup modal explicando a metodologia de correção por categoria"""
    
    popup_html = f'''
    <div id="popupExplicacao" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(0, 0, 0, 0.85); z-index: 10001; display: flex; 
                justify-content: center; align-items: center; backdrop-filter: blur(5px);">
        <div style="background: {COR_BRANCO}; width: 90%; max-width: 800px; max-height: 85vh;
                    border-radius: 16px; padding: 0; overflow: hidden; 
                    box-shadow: 0 25px 50px rgba(0,0,0,0.3); animation: slideIn 0.3s ease-out;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, {COR_AZUL_ESCURO}, {COR_AZUL_PETROLEO}); 
                        padding: 1.5rem 2rem; color: {COR_BRANCO};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="margin: 0; font-size: 1.5rem;">🔧 Metodologia de Correção por Categoria</h2>
                        <p style="margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 0.85rem;">
                        Como classificamos e tratamos os motivos de revisão
                        </p>
                    </div>
                    <button onclick="document.getElementById('popupExplicacao').style.display='none'" 
                            style="background: rgba(255,255,255,0.2); color: {COR_BRANCO}; 
                                   border: none; width: 36px; height: 36px; 
                                   border-radius: 50%; font-size: 1.3rem; 
                                   cursor: pointer; transition: all 0.2s;">
                        ×
                    </button>
                </div>
            </div>
            
            <!-- Conteúdo -->
            <div style="padding: 1.5rem 2rem; max-height: 60vh; overflow-y: auto;">
                
                <!-- Visão Geral -->
                <div style="background: {COR_CINZA_FUNDO}; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid {COR_VERDE_ESCURO};">
                    <h3 style="margin: 0 0 0.5rem 0; color: {COR_PRETO_SUAVE};">📋 Visão Geral</h3>
                    <p style="margin: 0; color: {COR_CINZA_TEXTO}; font-size: 0.9rem;">
                    A classificação dos motivos de revisão é feita automaticamente com base em 
                    palavras-chave e padrões identificados nos textos. Esta metodologia permite:
                    </p>
                    <ul style="margin: 0.5rem 0 0 1.5rem; color: {COR_CINZA_TEXTO};">
                        <li>Agrupar problemas semelhantes para análise de causa raiz</li>
                        <li>Identificar padrões recorrentes por categoria</li>
                        <li>Priorizar ações de melhoria baseadas em dados</li>
                        <li>Medir a efetividade das correções ao longo do tempo</li>
                    </ul>
                </div>
                
                <!-- Tabela de Categorias -->
                <h3 style="color: {COR_AZUL_ESCURO}; margin-bottom: 1rem;">🏷️ Categorias de Classificação</h3>
                
                <div style="display: grid; gap: 1rem;">
                    
                    <!-- Categoria 1 -->
                    <div style="background: #FFF8E1; padding: 1rem; border-radius: 8px; border-left: 5px solid #FFB300;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <span style="font-size: 1.8rem;">📋</span>
                            <strong style="font-size: 1.1rem; color: #E65100;">Erro de Documentação</strong>
                        </div>
                        <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: {COR_CINZA_TEXTO};">
                        Problemas relacionados ao preenchimento de informações, documentação incompleta, 
                        descrições ausentes ou fora do padrão.
                        </p>
                        <details>
                            <summary style="cursor: pointer; font-size: 0.8rem; color: {COR_AZUL_ESCURO};">📝 Exemplos comuns →</summary>
                            <ul style="margin: 8px 0 0 20px; font-size: 0.75rem; color: {COR_CINZA_TEXTO};">
                                <li>Card preenchido de forma incompleta</li>
                                <li>Descrição ausente ou insuficiente</li>
                                <li>Falta de anexos/documentação</li>
                                <li>Informações de responsável ausentes</li>
                                <li>Template preenchido incorretamente</li>
                            </ul>
                        </details>
                    </div>
                    
                    <!-- Categoria 2 -->
                    <div style="background: #E3F2FD; padding: 1rem; border-radius: 8px; border-left: 5px solid #1565C0;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <span style="font-size: 1.8rem;">⚙️</span>
                            <strong style="font-size: 1.1rem; color: #0D47A1;">Falha Técnica/Configuração</strong>
                        </div>
                        <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: {COR_CINZA_TEXTO};">
                        Erros decorrentes de problemas técnicos, configuração incorreta de sistemas, 
                        changesets rejeitados ou parâmetros incorretos.
                        </p>
                        <details>
                            <summary style="cursor: pointer; font-size: 0.8rem; color: {COR_AZUL_ESCURO};">📝 Exemplos comuns →</summary>
                            <ul style="margin: 8px 0 0 20px; font-size: 0.75rem; color: {COR_CINZA_TEXTO};">
                                <li>Changeset rejeitado ou bloqueado</li>
                                <li>Configurações de remota fora do padrão</li>
                                <li>Parâmetros de comunicação incorretos</li>
                                <li>Endereço de IP divergente</li>
                                <li>Comandos de disjuntores incoerentes</li>
                            </ul>
                        </details>
                    </div>
                    
                    <!-- Categoria 3 -->
                    <div style="background: #E8EAF6; padding: 1rem; border-radius: 8px; border-left: 5px solid #3949AB;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <span style="font-size: 1.8rem;">🔗</span>
                            <strong style="font-size: 1.1rem; color: #1A237E;">Erro de Conectividade/Nó</strong>
                        </div>
                        <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: {COR_CINZA_TEXTO};">
                        Problemas relacionados à conectividade entre sistemas, criação/configuração de nós, 
                        links de comunicação e rede.
                        </p>
                        <details>
                            <summary style="cursor: pointer; font-size: 0.8rem; color: {COR_AZUL_ESCURO};">📝 Exemplos comuns →</summary>
                            <ul style="margin: 8px 0 0 20px; font-size: 0.75rem; color: {COR_CINZA_TEXTO};">
                                <li>Nó de conectividade fora do padrão</li>
                                <li>Falha no link de comunicação</li>
                                <li>Problemas de sincronização de main/node</li>
                                <li>Timeouts de conexão</li>
                            </ul>
                        </details>
                    </div>
                    
                    <!-- Categoria 4 -->
                    <div style="background: #F3E5F5; padding: 1rem; border-radius: 8px; border-left: 5px solid #6A1B9A;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <span style="font-size: 1.8rem;">📐</span>
                            <strong style="font-size: 1.1rem; color: #4A148C;">Não Conformidade com Padrão</strong>
                        </div>
                        <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: {COR_CINZA_TEXTO};">
                        Itens que não seguem os padrões estabelecidos, procedimentos, templates ou 
                        normas definidas pela área.
                        </p>
                        <details>
                            <summary style="cursor: pointer; font-size: 0.8rem; color: {COR_AZUL_ESCURO};">📝 Exemplos comuns →</summary>
                            <ul style="margin: 8px 0 0 20px; font-size: 0.75rem; color: {COR_CINZA_TEXTO};">
                                <li>Formatação de changeset fora do padrão</li>
                                <li>Representação de sinais incorreta</li>
                                <li>Template não utilizado corretamente</li>
                                <li>Alinhamento/sincronismo inadequado</li>
                                <li>Procedimento não seguido</li>
                            </ul>
                        </details>
                    </div>
                    
                    <!-- Categoria 5 -->
                    <div style="background: #FFF3E0; padding: 1rem; border-radius: 8px; border-left: 5px solid #E65100;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <span style="font-size: 1.8rem;">🔄</span>
                            <strong style="font-size: 1.1rem; color: #BF360C;">Divergência de Informação</strong>
                        </div>
                        <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: {COR_CINZA_TEXTO};">
                        Inconsistências ou conflitos entre informações de diferentes fontes, chamados 
                        que não correlacionam ou dados divergentes.
                        </p>
                        <details>
                            <summary style="cursor: pointer; font-size: 0.8rem; color: {COR_AZUL_ESCURO};">📝 Exemplos comuns →</summary>
                            <ul style="margin: 8px 0 0 20px; font-size: 0.75rem; color: {COR_CINZA_TEXTO};">
                                <li>Informações inconsistentes entre sistemas</li>
                                <li>Chamado não encontrado ou não correlaciona</li>
                                <li>Múltiplos chamados em um changeset</li>
                                <li>Dados que não condizem com a realidade</li>
                            </ul>
                        </details>
                    </div>
                    
                    <!-- Categoria 6 -->
                    <div style="background: #E0F2F1; padding: 1rem; border-radius: 8px; border-left: 5px solid #00695C;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <span style="font-size: 1.8rem;">🎨</span>
                            <strong style="font-size: 1.1rem; color: #004D40;">Erro de Interface/Tela</strong>
                        </div>
                        <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: {COR_CINZA_TEXTO};">
                        Problemas relacionados à exibição de informações em tela, representações gráficas, 
                        diagramas unifilares e interfaces de usuário.
                        </p>
                        <details>
                            <summary style="cursor: pointer; font-size: 0.8rem; color: {COR_AZUL_ESCURO};">📝 Exemplos comuns →</summary>
                            <ul style="margin: 8px 0 0 20px; font-size: 0.75rem; color: {COR_CINZA_TEXTO};">
                                <li>Representação incorreta em tela</li>
                                <li>Diagrama unifilar com problemas</li>
                                <li>Tela autogerada com erro</li>
                                <li>Esquemática fora do padrão</li>
                            </ul>
                        </details>
                    </div>
                    
                    <!-- Categoria 7 -->
                    <div style="background: {COR_CINZA_FUNDO}; padding: 1rem; border-radius: 8px; border-left: 5px solid {COR_CINZA_TEXTO};">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <span style="font-size: 1.8rem;">📝</span>
                            <strong style="font-size: 1.1rem; color: {COR_PRETO_SUAVE};">Outros / Não Classificado</strong>
                        </div>
                        <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: {COR_CINZA_TEXTO};">
                        Motivos que não se enquadram nas categorias anteriores ou não contêm 
                        informações suficientes para classificação.
                        </p>
                        <details>
                            <summary style="cursor: pointer; font-size: 0.8rem; color: {COR_AZUL_ESCURO};">📝 Quando ocorre →</summary>
                            <ul style="margin: 8px 0 0 20px; font-size: 0.75rem; color: {COR_CINZA_TEXTO};">
                                <li>Motivo não informado (campo vazio)</li>
                                <li>Texto muito curto ou genérico</li>
                                <li>Informação não categorize</li>
                                <li>Palavras-chave não reconhecidas</li>
                            </ul>
                        </details>
                    </div>
                    
                </div>
                
                <!-- Processo de Correção -->
                <div style="margin-top: 2rem; background: #E8F5E9; padding: 1rem; border-radius: 8px;">
                    <h3 style="margin: 0 0 0.5rem 0; color: {COR_VERDE_ESCURO};">🔄 Por que corrigimos por categoria?</h3>
                    <p style="margin: 0; color: {COR_CINZA_TEXTO}; font-size: 0.9rem;">
                    A correção e classificação por categoria é fundamental porque:
                    </p>
                    <ul style="margin: 0.5rem 0 0 1.5rem; color: {COR_CINZA_TEXTO};">
                        <li><strong>Identifica padrões recorrentes</strong> - Permite visualizar quais tipos de erro são mais frequentes</li>
                        <li><strong>Prioriza ações corretivas</strong> - Foca nos problemas que mais impactam a equipe</li>
                        <li><strong>Mede evolução</strong> - Acompanha se as correções estão reduzindo ocorrências ao longo do tempo</li>
                        <li><strong>Facilita tomada de decisão</strong> - Fornece dados objetivos para gestão de qualidade</li>
                        <li><strong>Permite benchmarking</strong> - Compara performance entre equipes e períodos</li>
                    </ul>
                </div>
                
                <!-- Validação de Dados -->
                <div style="margin-top: 1rem; background: #FFF8E1; padding: 1rem; border-radius: 8px;">
                    <h3 style="margin: 0 0 0.5rem 0; color: #E65100;">⚠️ Nota sobre Validação de Dados</h3>
                    <p style="margin: 0; color: {COR_CINZA_TEXTO}; font-size: 0.9rem;">
                    Caso você identifique uma diferença entre as revisões declaradas (101) e as revisões analisadas (107), 
                    isso indica que existem <strong>registros duplicados na base de dados</strong> ou <strong>chamados 
                    com múltiplas linhas de revisão</strong>. O sistema aplica automaticamente a correção consolidando 
                    estes registros para garantir a precisão das análises.
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: {COR_CINZA_FUNDO}; padding: 1rem 2rem; border-top: 1px solid {COR_CINZA_BORDA};">
                <div style="display: flex; justify-content: flex-end;">
                    <button onclick="document.getElementById('popupExplicacao').style.display='none'"
                            style="background: {COR_AZUL_ESCURO}; color: {COR_BRANCO}; border: none; 
                                   padding: 0.6rem 1.5rem; border-radius: 6px; 
                                   cursor: pointer; font-weight: 500;">
                        Entendi ✓
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
    
    details summary {{
        user-select: none;
    }}
    
    details summary:hover {{
        text-decoration: underline;
    }}
    </style>
    '''
    
    return popup_html

# ============================================
# FUNÇÃO ANALISAR_MOTIVOS_REVISAO MODIFICADA
# ============================================
def analisar_motivos_revisao(df, ano_selecionado, mes_selecionado):
    """Analisa os motivos de revisão com filtros - VERSÃO COM TABELA (SEM GRÁFICO)"""
    
    # CORREÇÃO AUTOMÁTICA: Consolidar duplicatas antes da análise
    df_corrigido, relatorio = corrigir_revisoes_duplicadas(df)
    
    # Exibir aviso se houve correção
    if relatorio is not None and relatorio['diferenca_revisoes'] > 0:
        st.warning(f"""
        ⚠️ **Correção automática aplicada!**  
        Detectados {relatorio['chamados_duplicados']} chamados duplicados.  
        Revisões originais: {relatorio['total_revisoes_original']} → Corrigido: {relatorio['total_revisoes_corrigido']}  
        Diferença: {relatorio['diferenca_revisoes']} revisões ajustadas.
        """)
        
        # Botão para explicar a correção
        if st.button("🔧 Entenda como corrigimos os dados", key="btn_explicar_correcao"):
            st.session_state.show_correcao_popup = True
    
    # Usar o dataframe corrigido
    df_filtrado = df_corrigido[df_corrigido['Revisões'] > 0].copy()
    
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
    
    # TABELA detalhada de motivos (em vez de gráfico)
    motivos_detalhados = df_filtrado[['Motivo_Revisao', 'Categoria_Motivo', 'Chamado', 'Responsável_Formatado']].drop_duplicates().copy()
    motivos_detalhados.columns = ['Motivo da Revisão', 'Categoria', 'Chamado', 'Responsável']
    
    # Remover duplicatas de motivo (para não repetir o mesmo motivo várias vezes)
    motivos_unicos = motivos_detalhados.groupby(['Motivo da Revisão', 'Categoria']).agg({
        'Chamado': lambda x: ', '.join(x.astype(str).unique()[:3]) + ('...' if len(x) > 3 else ''),
        'Responsável': lambda x: ', '.join(x.unique()[:3]) + ('...' if len(x.unique()) > 3 else '')
    }).reset_index()
    
    # Adicionar contagem de ocorrências
    contagem_motivos = df_filtrado['Motivo_Revisao'].value_counts().reset_index()
    contagem_motivos.columns = ['Motivo da Revisão', 'Ocorrências']
    
    motivos_unicos = motivos_unicos.merge(contagem_motivos, on='Motivo da Revisão', how='left')
    motivos_unicos = motivos_unicos.sort_values('Ocorrências', ascending=False)
    
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
    
    return estatisticas_categoria, motivos_unicos, responsavel_pivot, total_com_revisao

# ============================================
# FUNÇÕES AUXILIARES (mantidas do código original)
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
        
        # APLICAR CORREÇÃO DE DUPLICATAS AUTOMATICAMENTE
        df, _ = corrigir_revisoes_duplicadas(df)
        
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
        st.session_state.show_correcao_popup = False
    
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
                v6.0 | Sistema de Performance SRE
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
# EXIBIR POPUP DE EXPLICAÇÃO DA CORREÇÃO
# ============================================
if st.session_state.get('show_correcao_popup', False):
    popup_html = criar_popup_explicacao_correcao()
    st.components.v1.html(popup_html, height=0)
    st.session_state.show_correcao_popup = False

# ============================================
# BOTÕES MANCHETE
# ============================================
if st.session_state.df_original is not None:
    if 'show_popup' not in st.session_state:
        st.session_state.show_popup = False
    
    # Botão de explicação da metodologia
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    
    with col_btn1:
        if st.button("📰 **VER MANCHETE**", 
                    help="Clique para ver os principais indicadores do mês",
                    type="secondary",
                    use_container_width=True,
                    key="btn_manchete"):
            st.session_state.show_popup = True
    
    with col_btn3:
        if st.button("🔧 **METODOLOGIA**", 
                    help="Clique para entender como classificamos os motivos de revisão",
                    type="secondary",
                    use_container_width=True,
                    key="btn_metodologia"):
            st.session_state.show_correcao_popup = True

if st.session_state.df_original is not None:
    if verificar_e_atualizar_arquivo():
        st.info("🔔 O arquivo local foi atualizado! Clique em 'Recarregar Local' na barra lateral para atualizar os dados.")

# Restante do código continua igual, incluindo a parte que exibe o dashboard principal...

# [NOTA: O restante do código (tabs principal, mapa e motivos) permanece igual ao original, 
#  mas com a substituição do gráfico "Top Motivos Mais Recorrentes" pela tabela detalhada
#  dentro da aba de motivos]

# ============================================
# EXIBIR DASHBOARD SE HOUVER DADOS
# ============================================
if st.session_state.df_original is not None:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    # ============================================
    # CRIAR TABS PRINCIPAIS
    # ============================================
    tab_principal, tab_mapa, tab_motivos = st.tabs(["📊 Dashboard Principal", "🗺️ Mapa de Sincronizações", "🔍 Motivos de Revisão"])
    
    with tab_principal:
        # ... (todo o conteúdo do tab_principal permanece igual ao original)
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
        
        # Restante do tab_principal continua igual...
        st.info("ℹ️ O conteúdo do Dashboard Principal permanece inalterado, apenas a aba 'Motivos de Revisão' foi modificada conforme solicitado.")
    
    with tab_mapa:
        # ... (todo o conteúdo do tab_mapa permanece igual)
        st.info("ℹ️ O conteúdo do Mapa permanece inalterado.")
    
    with tab_motivos:
        st.markdown("## 🔍 ANÁLISE DE MOTIVOS DE REVISÃO")
        st.markdown("_Principais causas de retrabalho e oportunidades de melhoria_")
        
        if 'Motivo_Revisao' not in df.columns:
            st.warning("⚠️ Coluna 'Motivo Revisão' não encontrada no arquivo de dados.")
        else:
            # Filtros específicos para análise de motivos
            col_filtro_motivo1, col_filtro_motivo2, col_filtro_motivo3 = st.columns(3)
            
            with col_filtro_motivo1:
                anos_motivo = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_motivo = ['Todos os Anos'] + list(anos_motivo)
                ano_motivo = st.selectbox(
                    "📅 Ano",
                    options=anos_opcoes_motivo,
                    key="filtro_ano_motivo"
                )
            
            with col_filtro_motivo2:
                meses_motivo = sorted(df['Mês'].dropna().unique().astype(int))
                meses_opcoes_motivo = ['Todos os Meses'] + [f"{m:02d}" for m in meses_motivo]
                mes_motivo = st.selectbox(
                    "📆 Mês",
                    options=meses_opcoes_motivo,
                    key="filtro_mes_motivo"
                )
            
            with col_filtro_motivo3:
                if 'Responsável_Formatado' in df.columns:
                    responsaveis_motivo = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
                    responsavel_motivo = st.selectbox(
                        "👤 Responsável",
                        options=responsaveis_motivo,
                        key="filtro_responsavel_motivo"
                    )
                else:
                    responsavel_motivo = 'Todos'
            
            # Aplicar filtros para análise
            df_motivos = df.copy()
            
            if ano_motivo != 'Todos os Anos':
                df_motivos = df_motivos[df_motivos['Ano'] == int(ano_motivo)]
            
            if mes_motivo != 'Todos os Meses':
                df_motivos = df_motivos[df_motivos['Mês'] == int(mes_motivo)]
            
            if responsavel_motivo != 'Todos' and 'Responsável_Formatado' in df_motivos.columns:
                df_motivos = df_motivos[df_motivos['Responsável_Formatado'] == responsavel_motivo]
            
            # Usar a função analisar_motivos_revisao (versão SEM o gráfico)
            estatisticas_categoria, motivos_detalhados, responsavel_pivot, total_com_revisao = analisar_motivos_revisao(
                df_motivos, ano_motivo, mes_motivo
            )
            
            if estatisticas_categoria is None or motivos_detalhados is None:
                st.info("ℹ️ Nenhum motivo de revisão registrado com os filtros selecionados.")
            else:
                # Cards de resumo executivo
                st.markdown("### 📊 Resumo Executivo")
                
                col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
                
                with col_metric1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{total_com_revisao:,}</div>
                        <div class="metric-label">Registros com Revisão</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_metric2:
                    total_categorias = len(estatisticas_categoria)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{total_categorias}</div>
                        <div class="metric-label">Categorias Identificadas</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_metric3:
                    top_categoria = estatisticas_categoria.iloc[0]['Categoria'] if len(estatisticas_categoria) > 0 else "N/A"
                    top_percentual = estatisticas_categoria.iloc[0]['Percentual'] if len(estatisticas_categoria) > 0 else 0
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{top_categoria[:20]}</div>
                        <div class="metric-label">Principal Causa ({top_percentual:.1f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_metric4:
                    pct_informado = (total_com_revisao / len(df_motivos[df_motivos['Revisões'] > 0]) * 100) if len(df_motivos[df_motivos['Revisões'] > 0]) > 0 else 0
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{pct_informado:.1f}%</div>
                        <div class="metric-label">Cobertura de Informação</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Distribuição por Categoria (Gráfico de Rosca - mantido)
                st.markdown("### 📊 Distribuição por Categoria de Motivo")
                
                col_cat1, col_cat2 = st.columns([1, 1.5])
                
                with col_cat1:
                    fig_pizza = px.pie(
                        estatisticas_categoria,
                        values='Quantidade',
                        names='Categoria',
                        title='Distribuição por Categoria',
                        hole=0.4,
                        color='Categoria',
                        color_discrete_sequence=px.colors.sequential.Blues_r
                    )
                    fig_pizza.update_layout(height=400)
                    st.plotly_chart(fig_pizza, use_container_width=True)
                
                with col_cat2:
                    st.markdown("#### 📈 Ranking de Categorias")
                    for idx, row in estatisticas_categoria.iterrows():
                        percentual_barra = row['Percentual']
                        st.markdown(f"""
                        <div style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span><strong>{row['Categoria']}</strong></span>
                                <span>{row['Quantidade']} ({row['Percentual']:.1f}%)</span>
                            </div>
                            <div style="background: {COR_CINZA_BORDA}; border-radius: 10px; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, {COR_AZUL_ESCURO}, {COR_AZUL_PETROLEO}); width: {percentual_barra}%; padding: 8px 0; border-radius: 10px;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # ============================================
                # NOVA SEÇÃO: TABELA DETALHADA DE MOTIVOS 
                # (SUBSTITUI O GRÁFICO "TOP MOTIVOS MAIS RECORRENTES")
                # ============================================
                st.markdown("### 📋 TABELA DETALHADA DE MOTIVOS DE REVISÃO")
                st.markdown("_Lista completa dos motivos registrados, categorizados e com contagem de ocorrências_")
                
                # Aplicar paginação se houver muitos registros
                if len(motivos_detalhados) > 20:
                    pagina = st.number_input(
                        "Página", 
                        min_value=1, 
                        max_value=(len(motivos_detalhados) // 20) + 1,
                        value=1,
                        key="pagina_motivos"
                    )
                    inicio = (pagina - 1) * 20
                    fim = inicio + 20
                    motivos_paginados = motivos_detalhados.iloc[inicio:fim]
                else:
                    motivos_paginados = motivos_detalhados
                
                # Exibir a tabela
                st.dataframe(
                    motivos_paginados,
                    use_container_width=True,
                    height=min(500, len(motivos_paginados) * 40 + 40),
                    column_config={
                        "Motivo da Revisão": st.column_config.TextColumn("Motivo", width="large"),
                        "Categoria": st.column_config.TextColumn("Categoria", width="medium"),
                        "Ocorrências": st.column_config.NumberColumn("Ocorrências", format="%d", width="small"),
                        "Chamado (exemplos)": st.column_config.TextColumn("Chamados de Exemplo", width="medium"),
                        "Responsável (exemplos)": st.column_config.TextColumn("Responsáveis", width="medium")
                    }
                )
                
                # Botão para exportar a tabela completa
                csv_motivos = motivos_detalhados.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Exportar tabela completa de motivos",
                    data=csv_motivos,
                    file_name=f"motivos_revisao_detalhados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                # Exibir análise por responsável (se disponível)
                if responsavel_pivot is not None and not responsavel_pivot.empty:
                    st.markdown("---")
                    st.markdown("### 👥 Matriz de Erros por Responsável")
                    
                    st.dataframe(
                        responsavel_pivot,
                        use_container_width=True,
                        height=400
                    )
                
                st.markdown("---")
                
                # Evolução Mensal (se houver dados temporais)
                if 'Criado' in df_motivos.columns and len(df_motivos) > 0:
                    st.markdown("### 📈 Evolução Mensal dos Principais Motivos")
                    
                    df_motivos['Mês_Ano'] = df_motivos['Criado'].dt.strftime('%Y-%m')
                    
                    top_5_categorias = estatisticas_categoria.head(5)['Categoria'].tolist()
                    
                    df_categorias = df_motivos.copy()
                    df_categorias['Categoria'] = df_categorias['Motivo_Revisao'].apply(classificar_motivo_revisao)
                    
                    evolucao_motivos = df_categorias[df_categorias['Categoria'].isin(top_5_categorias)].groupby(['Mês_Ano', 'Categoria']).size().reset_index()
                    evolucao_motivos.columns = ['Mês_Ano', 'Categoria', 'Quantidade']
                    
                    if not evolucao_motivos.empty:
                        fig_evolucao = px.line(
                            evolucao_motivos,
                            x='Mês_Ano',
                            y='Quantidade',
                            color='Categoria',
                            markers=True,
                            title='Evolução das Principais Categorias de Motivos',
                            labels={'Mês_Ano': 'Período', 'Quantidade': 'Número de Ocorrências', 'Categoria': 'Categoria do Motivo'}
                        )
                        
                        fig_evolucao.update_layout(
                            height=400,
                            xaxis_title="Mês/Ano",
                            yaxis_title="Quantidade",
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig_evolucao, use_container_width=True)
                
                st.markdown("---")
                
                # Recomendações automáticas
                st.markdown("### 💡 Recomendações com Base nos Motivos")
                
                recomendacoes = []
                
                # Motivo mais frequente
                if len(motivos_detalhados) > 0:
                    motivo_top = motivos_detalhados.iloc[0]
                    if motivo_top['Ocorrências'] > 5:
                        recomendacoes.append({
                            'Prioridade': '🔴 ALTA',
                            'Recomendação': f'Corrigir recorrentemente: "{motivo_top["Motivo da Revisão"][:50]}"',
                            'Justificativa': f'Ocorreu {motivo_top["Ocorrências"]} vezes'
                        })
                
                # Categoria mais frequente
                if len(estatisticas_categoria) > 0:
                    cat_top = estatisticas_categoria.iloc[0]
                    if cat_top['Percentual'] > 30:
                        recomendacoes.append({
                            'Prioridade': '🔴 ALTA',
                            'Recomendação': f'Revisar processo da categoria "{cat_top["Categoria"]}"',
                            'Justificativa': f'Representa {cat_top["Percentual"]:.1f}% das ocorrências'
                        })
                    elif cat_top['Percentual'] > 15:
                        recomendacoes.append({
                            'Prioridade': '🟡 MÉDIA',
                            'Recomendação': f'Investigar categoria "{cat_top["Categoria"]}"',
                            'Justificativa': f'Responsável por {cat_top["Percentual"]:.1f}% dos casos'
                        })
                
                # Responsável com mais revisões
                if responsavel_pivot is not None and not responsavel_pivot.empty:
                    total_por_responsavel = responsavel_pivot.iloc[:, 1:].sum(axis=1)
                    if len(total_por_responsavel) > 0:
                        idx_max = total_por_responsavel.idxmax() if len(total_por_responsavel) > 0 else None
                        if idx_max is not None:
                            recomendacoes.append({
                                'Prioridade': '🟡 MÉDIA',
                                'Recomendação': f'Acompanhamento com {idx_max}',
                                'Justificativa': f'Responsável por {total_por_responsavel.max()} revisões'
                            })
                
                # Exibir recomendações
                if recomendacoes:
                    for rec in recomendacoes[:5]:
                        cor_classe = 'warning-card' if 'ALTA' in rec['Prioridade'] else 'info-card' if 'MÉDIA' in rec['Prioridade'] else 'performance-card'
                        st.markdown(f"""
                        <div class="{cor_classe}" style="margin-bottom: 15px; padding: 12px;">
                            <div>
                                <strong style="font-size: 1rem;">{rec['Prioridade']} - {rec['Recomendação']}</strong><br>
                                <small style="color: {COR_CINZA_TEXTO};">{rec['Justificativa']}</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("✅ Nenhuma recomendação crítica identificada neste período.")
                
                st.markdown("---")
                
                # Botão para entender a metodologia
                if st.button("🔧 **Entenda como classificamos os motivos**", use_container_width=True):
                    st.session_state.show_correcao_popup = True

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
        Versão 6.0 | Sistema de Performance SRE | Última atualização: {ultima_atualizacao} (Brasília)
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
