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
warnings.filterwarnings('ignore')

# ============================================
# VARIÁVEIS GLOBAIS DE CONFIGURAÇÃO
# ============================================
# CONFIGURE AQUI O CAMINHO DO SEU ARQUIVO
CAMINHO_ARQUIVO_PRINCIPAL = "esteira_demandas.csv"  # ← ALTERE AQUI!
# Possíveis caminhos alternativos
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
# CSS PERSONALIZADO ATUALIZADO
# ============================================
st.markdown("""
<style>
    /* Estilos gerais */
    .main-header {
        background: linear-gradient(135deg, #0c2461 0%, #1e3799 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .metric-card-exec {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .metric-card-exec:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
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
    
    .metric-delta-positive {
        color: #28a745;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .metric-delta-negative {
        color: #dc3545;
        font-size: 0.85rem;
        font-weight: 600;
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
    
    /* Informações da base */
    .info-base {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e3799;
        margin-bottom: 1.5rem;
    }
    
    /* Rodapé */
    .footer-exec {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 2px solid #e9ecef;
        color: #6c757d;
        font-size: 0.9rem;
    }
    
    /* Status de SRE */
    .sre-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e3799;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    
    .sre-rank {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e3799;
        margin-right: 0.5rem;
    }
    
    .sre-name {
        font-weight: 600;
        color: #495057;
    }
    
    .sre-stats {
        color: #6c757d;
        font-size: 0.85rem;
    }
    
    /* Novos estilos para análises melhoradas */
    .performance-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fff9 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ffffff 0%, #fff8f8 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .info-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fcff 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #17a2b8;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .trend-up {
        color: #28a745;
        font-weight: bold;
    }
    
    .trend-down {
        color: #dc3545;
        font-weight: bold;
    }
    
    .trend-neutral {
        color: #6c757d;
        font-weight: bold;
    }
    
    /* Estilos para o dashboard comparativo dos SREs */
    .sre-comparison-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .sre-comparison-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .sre-performance-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
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
    
    /* Novos estilos para análise SRE */
    .sre-metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fcff 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1e3799;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05)
    }
    
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
    
    # Se for e-mail, extrair nome
    if '@' in nome_str:
        partes = nome_str.split('@')[0]
        # Remover números e separadores
        for separador in ['.', '_', '-']:
            if separador in partes:
                partes = partes.replace(separador, ' ')
        
        # Capitalizar e formatar
        palavras = [p.capitalize() for p in partes.split() if not p.isdigit()]
        nome_formatado = ' '.join(palavras)
        
        # Corrigir conectivos
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
    
    # Se já for nome, apenas formatar
    return nome_str.title()

def criar_card_indicador_simples(valor, label, icone="📊"):
    """Cria card de indicador SIMPLES - sem delta"""
    # Verificar se o valor é numérico para formatar com vírgula
    if isinstance(valor, (int, float)):
        valor_formatado = f"{valor:,}"
    else:
        valor_formatado = str(valor)
    
    return f'''
    <div class="metric-card-exec">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <span style="font-size: 1.5rem;">{icone}</span>
            <div style="flex-grow: 1;">
                <div class="metric-value">{valor_formatado}</div>
                <div class="metric-label">{label}</div>
            </div>
        </div>
    </div>
    '''

def calcular_hash_arquivo(conteudo):
    """Calcula hash do conteúdo do arquivo para detectar mudanças"""
    return hashlib.md5(conteudo).hexdigest()

@st.cache_data
def carregar_dados(uploaded_file=None, caminho_arquivo=None):
    """Carrega e processa os dados"""
    try:
        if uploaded_file:
            # Ler conteúdo como bytes para hash
            conteudo_bytes = uploaded_file.getvalue()
            conteudo = conteudo_bytes.decode('utf-8-sig')
        elif caminho_arquivo and os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8-sig') as f:
                conteudo = f.read()
            conteudo_bytes = conteudo.encode('utf-8')
        else:
            return None, "Nenhum arquivo fornecido", None
        
        lines = conteudo.split('\n')
        
        # Encontrar cabeçalho
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
        
        # Ler dados
        data_str = '\n'.join(lines[header_line:])
        df = pd.read_csv(io.StringIO(data_str), quotechar='"')
        
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
        
        # Formatar nomes dos responsáveis
        if 'Responsável' in df.columns:
            df['Responsável_Formatado'] = df['Responsável'].apply(formatar_nome_responsavel)
        
        # Converter datas
        date_columns = ['Criado', 'Modificado']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Extrair informações temporais
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
        
        # Converter revisões
        if 'Revisões' in df.columns:
            df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
        
        # Calcular hash do conteúdo
        hash_conteudo = calcular_hash_arquivo(conteudo_bytes)
        
        return df, "✅ Dados carregados com sucesso", hash_conteudo
    
    except Exception as e:
        return None, f"Erro: {str(e)}", None

def encontrar_arquivo_dados():
    """Tenta encontrar o arquivo de dados em vários caminhos possíveis"""
    # Tentar primeiro o caminho principal
    if os.path.exists(CAMINHO_ARQUIVO_PRINCIPAL):
        return CAMINHO_ARQUIVO_PRINCIPAL
    
    # Tentar caminhos alternativos
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

def limpar_sessao_dados():
    """Limpa todos os dados da sessão relacionados ao upload"""
    keys_to_clear = [
        'df_original', 'df_filtrado', 'arquivo_atual',
        'ultima_modificacao', 'file_hash', 'uploaded_file_name',
        'ultima_atualizacao'  # Adicionado para tracking de tempo
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
# NOVAS FUNÇÕES PARA ANÁLISE SRE MELHORADA
# ============================================

def calcular_taxa_retorno_sre(df, sre_nome):
    """Calcula taxa de retorno específica para um SRE"""
    # Filtrar cards do SRE
    df_sre = df[df['SRE'] == sre_nome].copy()
    
    if len(df_sre) == 0:
        return 0, 0, 0
    
    total_cards = len(df_sre)
    
    # Estimar cards que retornaram para DEV (baseado em revisões > 0)
    if 'Revisões' in df_sre.columns:
        cards_com_revisoes = len(df_sre[df_sre['Revisões'] > 0])
        taxa_retorno = (cards_com_revisoes / total_cards * 100) if total_cards > 0 else 0
    else:
        taxa_retorno = 0
        cards_com_revisoes = 0
    
    # Cards sincronizados (aprovados)
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
        
        # Calcular eficiência (cards por mês)
        if 'Criado' in df_dev.columns:
            meses_ativos = df_dev['Criado'].dt.to_period('M').nunique()
            eficiencia = total_cards / max(meses_ativos, 1)
        else:
            eficiencia = total_cards
        
        # Calcular qualidade (taxa de aprovação sem revisão)
        if 'Revisões' in df_dev.columns:
            cards_sem_revisao = len(df_dev[df_dev['Revisões'] == 0])
            qualidade = (cards_sem_revisao / total_cards * 100) if total_cards > 0 else 0
        else:
            qualidade = 100
        
        # Calcular score composto
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
    
    # Agrupar por mês
    df_sre['Mes_Ano'] = df_sre['Criado'].dt.strftime('%Y-%m')
    
    # Sincronizados por mês
    sinc_mes = df_sre[df_sre['Status'] == 'Sincronizado'].groupby('Mes_Ano').size().reset_index()
    sinc_mes.columns = ['Mes_Ano', 'Sincronizados']
    
    # Total por mês
    total_mes = df_sre.groupby('Mes_Ano').size().reset_index()
    total_mes.columns = ['Mes_Ano', 'Total']
    
    # Combinar
    dados_mes = pd.merge(total_mes, sinc_mes, on='Mes_Ano', how='left').fillna(0)
    
    # Ordenar por data
    dados_mes = dados_mes.sort_values('Mes_Ano')
    
    return dados_mes

def gerar_recomendacoes_dev(df, dev_nome):
    """Gera recomendações personalizadas para um Desenvolvedor"""
    # Calcular métricas do Desenvolvedor
    df_dev = df[df['Responsável_Formatado'] == dev_nome].copy()
    
    if len(df_dev) == 0:
        return []
    
    total_cards = len(df_dev)
    
    # Calcular métricas de qualidade
    if 'Revisões' in df_dev.columns:
        cards_sem_revisao = len(df_dev[df_dev['Revisões'] == 0])
        qualidade = (cards_sem_revisao / total_cards * 100) if total_cards > 0 else 0
    else:
        qualidade = 100
    
    # Calcular eficiência
    if 'Criado' in df_dev.columns:
        meses_ativos = df_dev['Criado'].dt.to_period('M').nunique()
        eficiencia = total_cards / max(meses_ativos, 1)
    else:
        eficiencia = total_cards
    
    # Gerar recomendações baseadas nas métricas
    recomendacoes = []
    
    if qualidade < 70:
        recomendacoes.append({
            'prioridade': 'ALTA',
            'titulo': 'Melhorar qualidade do código',
            'descricao': f'Taxa de aprovação sem revisão: {qualidade:.1f}% (abaixo de 70%)',
            'acao': 'Implementar testes mais rigorosos antes do envio'
        })
    
    if eficiencia < 3:
        recomendacoes.append({
            'prioridade': 'MÉDIA',
            'titulo': 'Aumentar produtividade',
            'descricao': f'Eficiência atual: {eficiencia:.1f} cards/mês',
            'acao': 'Otimizar processo de desenvolvimento'
        })
    
    if 'Status' in df_dev.columns:
        cards_sincronizados = len(df_dev[df_dev['Status'] == 'Sincronizado'])
        if cards_sincronizados < total_cards * 0.6:
            recomendacoes.append({
                'prioridade': 'ALTA',
                'titulo': 'Melhorar taxa de sincronização',
                'descricao': f'Apenas {cards_sincronizados}/{total_cards} cards sincronizados',
                'acao': 'Revisar critérios antes do envio para SRE'
            })
    
    if qualidade > 90 and eficiencia > 8:
        recomendacoes.append({
            'prioridade': 'BAIXA',
            'titulo': 'Manter excelente performance',
            'descricao': 'Excelente equilíbrio entre qualidade e eficiência',
            'acao': 'Compartilhar melhores práticas com a equipe'
        })
    
    return recomendacoes

# ============================================
# SIDEBAR - FILTROS E CONTROLES (REORGANIZADO)
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
    
    # Inicializar session state
    if 'df_original' not in st.session_state:
        st.session_state.df_original = None
        st.session_state.df_filtrado = None
        st.session_state.arquivo_atual = None
        st.session_state.file_hash = None
        st.session_state.uploaded_file_name = None
        st.session_state.ultima_atualizacao = None
    
    # FILTROS APENAS SE HOUVER DADOS
    if st.session_state.df_original is not None:
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**🔍 Filtros de Análise**")
            
            df = st.session_state.df_original.copy()
            
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
                        df = df[df['Ano'] == int(ano_selecionado)]
            
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
                        df = df[df['Mês'] == int(mes_selecionado)]
            
            # FILTRO POR RESPONSÁVEL
            if 'Responsável_Formatado' in df.columns:
                responsaveis = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
                responsavel_selecionado = st.selectbox(
                    "👤 Responsável",
                    options=responsaveis,
                    key="filtro_responsavel"
                )
                if responsavel_selecionado != 'Todos':
                    df = df[df['Responsável_Formatado'] == responsavel_selecionado]
            
            # BUSCA POR CHAMADO
            busca_chamado = st.text_input(
                "🔎 Buscar Chamado",
                placeholder="Digite número do chamado...",
                key="busca_chamado"
            )
            if busca_chamado:
                df = df[df['Chamado'].astype(str).str.contains(busca_chamado, na=False)]
            
            # FILTRO POR STATUS
            if 'Status' in df.columns:
                status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox(
                    "📊 Status",
                    options=status_opcoes,
                    key="filtro_status"
                )
                if status_selecionado != 'Todos':
                    df = df[df['Status'] == status_selecionado]
            
            # FILTRO POR TIPO
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos'] + sorted(df['Tipo_Chamado'].dropna().unique())
                tipo_selecionado = st.selectbox(
                    "📝 Tipo de Chamado",
                    options=tipos,
                    key="filtro_tipo"
                )
                if tipo_selecionado != 'Todos':
                    df = df[df['Tipo_Chamado'] == tipo_selecionado]
            
            # FILTRO POR EMPRESA
            if 'Empresa' in df.columns:
                empresas = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                empresa_selecionada = st.selectbox(
                    "🏢 Empresa",
                    options=empresas,
                    key="filtro_empresa"
                )
                if empresa_selecionada != 'Todas':
                    df = df[df['Empresa'] == empresa_selecionada]
            
            # FILTRO POR SRE
            if 'SRE' in df.columns:
                sres = ['Todos'] + sorted(df['SRE'].dropna().unique())
                sre_selecionado = st.selectbox(
                    "🔧 SRE Responsável",
                    options=sres,
                    key="filtro_sre"
                )
                if sre_selecionado != 'Todos':
                    df = df[df['SRE'] == sre_selecionado]
            
            # Atualizar dados filtrados
            st.session_state.df_filtrado = df
            
            st.markdown(f"**📈 Registros filtrados:** {len(df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # CONTROLES DE ATUALIZAÇÃO (SEMPRE VISÍVEL)
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**🔄 Controles de Atualização**")
        
        # Verificar se há dados carregados
        if st.session_state.df_original is not None:
            arquivo_atual = st.session_state.arquivo_atual
            
            if arquivo_atual and isinstance(arquivo_atual, str) and os.path.exists(arquivo_atual):
                # Informações do arquivo
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
                
                # Verificar se o arquivo foi modificado
                if verificar_atualizacao_arquivo():
                    st.warning("⚠️ O arquivo local foi modificado!")
            
            # Botões de ação
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
                                # Limpar cache desta função
                                carregar_dados.clear()
                                
                                # Recarregar dados
                                df_atualizado, status, hash_conteudo = carregar_dados(caminho_arquivo=caminho_atual)
                                
                                if df_atualizado is not None:
                                    st.session_state.df_original = df_atualizado
                                    st.session_state.df_filtrado = df_atualizado.copy()
                                    st.session_state.arquivo_atual = caminho_atual
                                    st.session_state.file_hash = hash_conteudo
                                    st.session_state.ultima_atualizacao = get_horario_brasilia()
                                    
                                    # Atualizar timestamp da última modificação
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
                    
                    # Limpar cache
                    st.cache_data.clear()
                    
                    # Limpar session state
                    limpar_sessao_dados()
                    
                    st.success("✅ Dados e cache limpos!")
                    time.sleep(1)
                    st.rerun()
            
            st.markdown("---")
        
        # UPLOAD DE ARQUIVO (MOVIDO PARA O FINAL)
        st.markdown("**📤 Importar Dados**")
        
        # Mostrar status atual
        if st.session_state.df_original is not None:
            ultima_atualizacao = st.session_state.get('ultima_atualizacao', get_horario_brasilia())
            st.markdown(f"""
            <div class="status-box status-success">
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
        
        # Se um arquivo foi enviado
        if uploaded_file is not None:
            # Verificar se é um arquivo diferente do atual
            current_hash = calcular_hash_arquivo(uploaded_file.getvalue())
            
            if ('file_hash' not in st.session_state or 
                current_hash != st.session_state.file_hash or
                uploaded_file.name != st.session_state.uploaded_file_name):
                
                with st.spinner('Processando novo arquivo...'):
                    # Salvar temporariamente
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Carregar dados
                    df_novo, status, hash_conteudo = carregar_dados(caminho_arquivo=temp_path)
                    os.remove(temp_path)
                    
                    if df_novo is not None:
                        # Atualizar session state
                        st.session_state.df_original = df_novo
                        st.session_state.df_filtrado = df_novo.copy()
                        st.session_state.arquivo_atual = uploaded_file.name
                        st.session_state.file_hash = hash_conteudo
                        st.session_state.uploaded_file_name = uploaded_file.name
                        st.session_state.ultima_atualizacao = get_horario_brasilia()
                        
                        # Limpar filtros
                        if 'filtros_aplicados' in st.session_state:
                            del st.session_state.filtros_aplicados
                        
                        st.success(f"✅ {len(df_novo):,} registros carregados!")
                        
                        # Forçar recarregamento da página
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
                    # Registrar data da última modificação
                    if os.path.exists(caminho_encontrado):
                        st.session_state.ultima_modificacao = os.path.getmtime(caminho_encontrado)
                    st.rerun()
                else:
                    st.error(f"❌ {status}")

# ============================================
# CONTEÚDO PRINCIPAL
# ============================================

# HEADER ATUALIZADO (removida a data completamente)
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
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    # ============================================
    # INFORMAÇÕES DA BASE DE DADOS (SIMPLIFICADO)
    # ============================================
    st.markdown("## 📊 Informações da Base de Dados")
    
    if 'Criado' in df.columns and not df.empty:
        data_min = df['Criado'].min()
        data_max = df['Criado'].max()
        
        st.markdown(f"""
        <div class="info-base">
            <p style="margin: 0; font-weight: 600;">📅 Base atualizada em: {get_horario_brasilia()}</p>
            <p style="margin: 0.3rem 0 0 0; color: #6c757d;">
            Período coberto: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')} | 
            Total de registros: {len(df):,}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # INDICADORES PRINCIPAIS SIMPLES (APENAS 3)
    # ============================================
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
    
    # ============================================
    # ABAS PRINCIPAIS (ORIGINAIS)
    # ============================================
    st.markdown("---")
    
    # Definir 4 abas principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Evolução de Demandas", 
        "📊 Análise de Revisões", 
        "📈 Sincronizados por Dia",
        "🏆 Performance dos SREs"
    ])
    
    with tab1:
        # Cabeçalho com seletor de ano no lado direito
        col_titulo, col_seletor = st.columns([3, 1])
        
        with col_titulo:
            st.markdown('<div class="section-title-exec">📅 EVOLUÇÃO DE DEMANDAS POR MÊS</div>', unsafe_allow_html=True)
        
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
            # Filtrar dados para o ano selecionado
            df_ano = df[df['Ano'] == ano_selecionado].copy()
            
            if not df_ano.empty:
                # Ordem dos meses abreviados
                ordem_meses_abreviados = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                                         'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                
                # Criar dataframe com todos os meses do ano
                todos_meses = pd.DataFrame({
                    'Mês_Num': range(1, 13),
                    'Nome_Mês': ordem_meses_abreviados
                })
                
                # Agrupar por mês
                demandas_por_mes = df_ano.groupby('Mês_Num').size().reset_index()
                demandas_por_mes.columns = ['Mês_Num', 'Quantidade']
                
                # Juntar com todos os meses para garantir 12 meses
                demandas_completas = pd.merge(todos_meses, demandas_por_mes, on='Mês_Num', how='left')
                demandas_completas['Quantidade'] = demandas_completas['Quantidade'].fillna(0).astype(int)
                
                # Criar gráfico de linha
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
                        ticktext=ordem_meses_abreviados
                    ),
                    yaxis=dict(
                        gridcolor='rgba(0,0,0,0.05)',
                        rangemode='tozero'
                    )
                )
                
                # Adicionar valor total
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
                
                # Estatísticas mensais
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
        
        # ADICIONADO: Filtros de ano e mês para análise de revisões
        col_filtro_rev1, col_filtro_rev2 = st.columns(2)
        
        with col_filtro_rev1:
            if 'Ano' in df.columns:
                anos_rev = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_rev = ['Todos os Anos'] + list(anos_rev)
                ano_rev = st.selectbox(
                    "📅 Ano:",
                    options=anos_opcoes_rev,
                    index=len(anos_opcoes_rev)-1,
                    key="filtro_ano_rev"
                )
        
        with col_filtro_rev2:
            if 'Mês' in df.columns:
                meses_rev = sorted(df['Mês'].dropna().unique().astype(int))
                meses_opcoes_rev = ['Todos os Meses'] + [str(m) for m in meses_rev]
                mes_rev = st.selectbox(
                    "📆 Mês:",
                    options=meses_opcoes_rev,
                    key="filtro_mes_rev"
                )
        
        # Filtrar dados conforme ano e mês selecionados
        df_rev = df.copy()
        
        if ano_rev != 'Todos os Anos':
            df_rev = df_rev[df_rev['Ano'] == int(ano_rev)]
        
        if mes_rev != 'Todos os Meses':
            df_rev = df_rev[df_rev['Mês'] == int(mes_rev)]
        
        if 'Revisões' in df_rev.columns and 'Responsável_Formatado' in df_rev.columns:
            # Filtrar apenas responsáveis com revisões
            df_com_revisoes = df_rev[df_rev['Revisões'] > 0].copy()
            
            if not df_com_revisoes.empty:
                # Agrupar por responsável
                revisoes_por_responsavel = df_com_revisoes.groupby('Responsável_Formatado').agg({
                    'Revisões': 'sum',
                    'Chamado': 'count'
                }).reset_index()
                
                revisoes_por_responsavel.columns = ['Responsável', 'Total_Revisões', 'Chamados_Com_Revisão']
                revisoes_por_responsavel = revisoes_por_responsavel.sort_values('Total_Revisões', ascending=False)
                
                # Criar título dinâmico
                titulo_periodo = ""
                if ano_rev != 'Todos os Anos':
                    titulo_periodo = f" em {ano_rev}"
                if mes_rev != 'Todos os Meses':
                    meses_nomes = {
                        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                    }
                    titulo_periodo += f" - {meses_nomes[int(mes_rev)]}"
                
                # Criar gráfico de barras com cores vermelho (maior) para verde (menor)
                fig_revisoes = go.Figure()
                
                # Criar escala de cores personalizada (vermelho para maiores, verde para menores)
                max_revisoes = revisoes_por_responsavel['Total_Revisões'].max()
                min_revisoes = revisoes_por_responsavel['Total_Revisões'].min()
                
                # Calcular cores baseadas no valor (vermelho para maior, verde para menor)
                colors = []
                for valor in revisoes_por_responsavel['Total_Revisões']:
                    if max_revisoes == min_revisoes:
                        colors.append('#e74c3c')  # Vermelho se todos forem iguais
                    else:
                        # Normalizar entre 0 e 1
                        normalized = (valor - min_revisoes) / (max_revisoes - min_revisoes)
                        # Interpolar entre vermelho (#e74c3c) e verde (#28a745)
                        # Quanto maior o valor, mais vermelho; quanto menor, mais verde
                        red = int(231 * normalized + 40 * (1 - normalized))  # 231->40
                        green = int(76 * normalized + 167 * (1 - normalized))  # 76->167
                        blue = int(60 * normalized + 69 * (1 - normalized))  # 60->69
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
                    title=f'Top 15 Responsáveis com Mais Revisões{titulo_periodo}',
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
        
        # ADICIONADO: Filtros de ano e mês para sincronizados por dia
        col_filtro_sinc1, col_filtro_sinc2 = st.columns(2)
        
        with col_filtro_sinc1:
            if 'Ano' in df.columns:
                anos_sinc = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_sinc = ['Todos os Anos'] + list(anos_sinc)
                ano_sinc = st.selectbox(
                    "📅 Ano:",
                    options=anos_opcoes_sinc,
                    index=len(anos_opcoes_sinc)-1,
                    key="filtro_ano_sinc"
                )
        
        with col_filtro_sinc2:
            if 'Mês' in df.columns:
                meses_sinc = sorted(df['Mês'].dropna().unique().astype(int))
                meses_opcoes_sinc = ['Todos os Meses'] + [str(m) for m in meses_sinc]
                mes_sinc = st.selectbox(
                    "📆 Mês:",
                    options=meses_opcoes_sinc,
                    key="filtro_mes_sinc"
                )
        
        # Filtrar dados conforme ano e mês selecionados
        df_sinc = df.copy()
        
        if ano_sinc != 'Todos os Anos':
            df_sinc = df_sinc[df_sinc['Ano'] == int(ano_sinc)]
        
        if mes_sinc != 'Todos os Meses':
            df_sinc = df_sinc[df_sinc['Mês'] == int(mes_sinc)]
        
        if 'Status' in df_sinc.columns and 'Criado' in df_sinc.columns:
            # Filtrar apenas chamados sincronizados
            df_sincronizados = df_sinc[df_sinc['Status'] == 'Sincronizado'].copy()
            
            if not df_sincronizados.empty:
                # Extrair data sem hora
                df_sincronizados['Data'] = df_sincronizados['Criado'].dt.date
                
                # Agrupar por data
                sincronizados_por_dia = df_sincronizados.groupby('Data').size().reset_index()
                sincronizados_por_dia.columns = ['Data', 'Quantidade']
                
                # Ordenar por data
                sincronizados_por_dia = sincronizados_por_dia.sort_values('Data')
                
                # Criar título dinâmico
                titulo_periodo = ""
                if ano_sinc != 'Todos os Anos':
                    titulo_periodo = f" em {ano_sinc}"
                if mes_sinc != 'Todos os Meses':
                    meses_nomes = {
                        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                    }
                    titulo_periodo += f" - {meses_nomes[int(mes_sinc)]}"
                
                # Criar gráfico de linha com área
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
                
                # Adicionar média móvel de 7 dias
                sincronizados_por_dia['Media_Movel'] = sincronizados_por_dia['Quantidade'].rolling(window=7, min_periods=1).mean()
                
                fig_dia.add_trace(go.Scatter(
                    x=sincronizados_por_dia['Data'],
                    y=sincronizados_por_dia['Media_Movel'],
                    name='Média Móvel (7 dias)',
                    line=dict(color='#dc3545', width=2, dash='dash')
                ))
                
                fig_dia.update_layout(
                    title=f'Evolução Diária de Chamados Sincronizados{titulo_periodo}',
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
        
        if 'SRE' in df.columns and 'Status' in df.columns and 'Revisões' in df.columns:
            # Filtros específicos para esta aba
            col_filtro1, col_filtro2 = st.columns(2)
            
            with col_filtro1:
                # Filtrar por ano
                if 'Ano' in df.columns:
                    anos_sre = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_sre = ['Todos'] + list(anos_sre)
                    ano_sre = st.selectbox(
                        "📅 Filtrar por Ano:",
                        options=anos_opcoes_sre,
                        key="filtro_ano_sre"
                    )
            
            with col_filtro2:
                # Filtrar por mês
                if 'Mês' in df.columns:
                    meses_sre = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_sre = ['Todos'] + [str(m) for m in meses_sre]
                    mes_sre = st.selectbox(
                        "📆 Filtrar por Mês:",
                        options=meses_opcoes_sre,
                        key="filtro_mes_sre"
                    )
            
            # Aplicar filtros
            df_sre = df.copy()
            
            if 'Ano' in df_sre.columns and ano_sre != 'Todos':
                df_sre = df_sre[df_sre['Ano'] == int(ano_sre)]
            
            if 'Mês' in df_sre.columns and mes_sre != 'Todos':
                df_sre = df_sre[df_sre['Mês'] == int(mes_sre)]
            
            # Filtrar apenas chamados sincronizados para análise SRE
            df_sincronizados = df_sre[df_sre['Status'] == 'Sincronizado'].copy()
            
            if not df_sincronizados.empty and 'SRE' in df_sincronizados.columns:
                # ============================================
                # 1. SINCRONIZADOS POR SRE (GRÁFICO DE BARRAS)
                # ============================================
                st.markdown("### 📈 Sincronizados por SRE")
                
                # Criar coluna com nomes formatados (remover emails)
                df_sincronizados['SRE_Formatado'] = df_sincronizados['SRE'].apply(lambda x: formatar_nome_responsavel(x) if pd.notna(x) else x)
                
                # Calcular sincronizados por SRE (usando nomes formatados)
                sinc_por_sre = df_sincronizados.groupby('SRE_Formatado').size().reset_index()
                sinc_por_sre.columns = ['SRE', 'Sincronizados']
                sinc_por_sre = sinc_por_sre.sort_values('Sincronizados', ascending=False)
                
                # Criar layout com gráfico e ranking lado a lado
                col_grafico, col_ranking = st.columns([3, 1])
                
                with col_grafico:
                    # Criar gráfico de barras
                    fig_sinc_bar = go.Figure()
                    
                    # Cores do maior para o menor (azul escuro para azul claro)
                    max_sinc = sinc_por_sre['Sincronizados'].max()
                    min_sinc = sinc_por_sre['Sincronizados'].min()
                    
                    colors = []
                    for valor in sinc_por_sre['Sincronizados']:
                        if max_sinc == min_sinc:
                            colors.append('#1e3799')  # Azul escuro se todos forem iguais
                        else:
                            normalized = (valor - min_sinc) / (max_sinc - min_sinc)
                            # Interpolar entre azul escuro (#1e3799) e azul claro (#4a69bd)
                            red = int(30 * normalized + 74 * (1 - normalized))
                            green = int(55 * normalized + 105 * (1 - normalized))
                            blue = int(153 * normalized + 189 * (1 - normalized))
                            colors.append(f'rgb({red}, {green}, {blue})')
                    
                    fig_sinc_bar.add_trace(go.Bar(
                        x=sinc_por_sre['SRE'].head(15),
                        y=sinc_por_sre['Sincronizados'].head(15),
                        name='Sincronizados',
                        text=sinc_por_sre['Sincronizados'].head(15),
                        textposition='outside',
                        marker_color=colors[:15],
                        marker_line_color='#0c2461',
                        marker_line_width=1.5,
                        opacity=0.8
                    ))
                    
                    fig_sinc_bar.update_layout(
                        title=f'Sincronizados por SRE',
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
                
                with col_ranking:
                    # Ranking dos SREs - CORRIGIDO
                    st.markdown("### 🏆 Ranking SREs")
                    
                    # Calcular ranking baseado em sincronizados
                    sre_ranking = sinc_por_sre.copy()
                    sre_ranking = sre_ranking.sort_values('Sincronizados', ascending=False).reset_index(drop=True)
                    
                    # Construir HTML completo para o ranking
                    ranking_html = '''
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border: 1px solid #dee2e6; margin-bottom: 1rem;">
                        <div style="text-align: center; font-weight: bold; color: #1e3799; margin-bottom: 0.5rem;">🏆 CLASSIFICAÇÃO</div>
                    '''
                    
                    # Medalhas e cores (apenas 4 primeiras)
                    medalhas = ['🥇', '🥈', '🥉', '4️⃣']
                    cores_bg = ['#e8f4f8', '#f0f0f0', '#f8f0e8', '#f8f9fa']
                    cores_borda = ['#1e3799', '#495057', '#856404', '#6c757d']
                    
                    # Mostrar apenas 4 SREs
                    num_sres = min(len(sre_ranking), 4)
                    
                    for i in range(num_sres):
                        sre = sre_ranking.iloc[i]
                        medalha = medalhas[i] if i < len(medalhas) else f"{i+1}️⃣"
                        
                        ranking_html += f'''
                        <div style="margin-bottom: 0.5rem; padding: 0.5rem; background: {cores_bg[i]}; 
                                    border-radius: 5px; border-left: 4px solid {cores_borda[i]};">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span style="font-weight: bold; color: #1e3799; font-size: 0.9rem;">{medalha} {sre['SRE']}</span>
                                </div>
                                <div>
                                    <span style="background: white; padding: 0.2rem 0.5rem; border-radius: 10px; 
                                                font-weight: bold; color: {cores_borda[i]}; font-size: 0.85rem;">
                                        {sre['Sincronizados']} sinc
                                    </span>
                                </div>
                            </div>
                        </div>
                        '''
                    
                    ranking_html += '</div>'
                    
                    # Exibir o ranking
                    st.markdown(ranking_html, unsafe_allow_html=True)
                    
                    # Adicionar estatísticas
                    if not sre_ranking.empty:
                        total_sinc = sre_ranking['Sincronizados'].sum()
                        media_sinc = sre_ranking['Sincronizados'].mean()
                        
                        stats_html = f"""
                        <div style="background: white; padding: 0.8rem; border-radius: 8px; border: 1px solid #dee2e6; margin-top: 1rem;">
                            <div style="font-size: 0.85rem; color: #495057;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                                    <span>📊 Total Sincronizados:</span>
                                    <span style="font-weight: bold;">{int(total_sinc)}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                                    <span>📈 Média por SRE:</span>
                                    <span style="font-weight: bold;">{media_sinc:.1f}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between;">
                                    <span>👥 SREs Ativos:</span>
                                    <span style="font-weight: bold;">{len(sre_ranking)}</span>
                                </div>
                            </div>
                        </div>
                        """
                        st.markdown(stats_html, unsafe_allow_html=True)
                
                # Tabela de Performance dos SREs - LIMITADA AO NÚMERO REAL DE SREs
                st.markdown("### 📋 Performance Detalhada dos SREs")
                
                # Calcular métricas adicionais
                sres_metrics = []
                sres_list = df_sre['SRE'].dropna().unique()
                
                for sre in sres_list:
                    df_sre_data = df_sre[df_sre['SRE'] == sre].copy()
                    
                    if len(df_sre_data) > 0:
                        total_cards = len(df_sre_data)
                        sincronizados = len(df_sre_data[df_sre_data['Status'] == 'Sincronizado'])
                        
                        # Cards que retornaram (revisões > 0)
                        if 'Revisões' in df_sre_data.columns:
                            cards_retorno = len(df_sre_data[df_sre_data['Revisões'] > 0])
                        else:
                            cards_retorno = 0
                        
                        # Taxa de retorno
                        taxa_retorno = (cards_retorno / total_cards * 100) if total_cards > 0 else 0
                        
                        # Taxa de sincronização
                        taxa_sinc = (sincronizados / total_cards * 100) if total_cards > 0 else 0
                        
                        # Usar nome formatado
                        sre_formatado = formatar_nome_responsavel(sre)
                        
                        sres_metrics.append({
                            'SRE': sre_formatado,
                            'Total Cards': total_cards,
                            'Sincronizados': sincronizados,
                            'Taxa Sinc. (%)': round(taxa_sinc, 1),
                            'Cards Retorno': cards_retorno,
                            'Taxa Retorno (%)': round(taxa_retorno, 1),
                            'Performance': '✅ Excelente' if taxa_sinc > 90 and taxa_retorno < 10 else 
                                          '🟡 Boa' if taxa_sinc > 70 else 
                                          '🟠 Regular' if taxa_sinc > 50 else 
                                          '🔴 Necessita Atenção'
                        })
                
                if sres_metrics:
                    df_sres_metrics = pd.DataFrame(sres_metrics)
                    df_sres_metrics = df_sres_metrics.sort_values('Sincronizados', ascending=False)
                    
                    # Mostrar apenas os SREs existentes (sem limite fixo de 10)
                    num_sres = len(df_sres_metrics)
                    
                    # Calcular altura dinâmica da tabela
                    altura_tabela = max(150, num_sres * 50 + 50)  # 50px por linha + cabeçalho
                    
                    # Formatar a tabela
                    styled_df = df_sres_metrics.style.format({
                        'Total Cards': '{:,}',
                        'Sincronizados': '{:,}',
                        'Taxa Sinc. (%)': '{:.1f}%',
                        'Cards Retorno': '{:,}',
                        'Taxa Retorno (%)': '{:.1f}%'
                    })
                    
                    st.dataframe(
                        styled_df,
                        use_container_width=True,
                        height=altura_tabela,
                        column_config={
                            "SRE": st.column_config.TextColumn("SRE", width="medium"),
                            "Total Cards": st.column_config.NumberColumn("Total", width="small"),
                            "Sincronizados": st.column_config.NumberColumn("Sinc.", width="small"),
                            "Taxa Sinc. (%)": st.column_config.NumberColumn("Taxa Sinc.", width="small", help="% de cards sincronizados"),
                            "Cards Retorno": st.column_config.NumberColumn("Retorno", width="small", help="Cards que retornaram"),
                            "Taxa Retorno (%)": st.column_config.NumberColumn("Taxa Ret.", width="small", help="% de cards que retornaram"),
                            "Performance": st.column_config.TextColumn("Performance", width="medium")
                        }
                    )
                    
                    # Adicionar estatísticas resumidas
                    if num_sres > 0:
                        col_sum1, col_sum2, col_sum3 = st.columns(3)
                        
                        with col_sum1:
                            st.metric("👥 SREs Ativos", num_sres)
                        
                        with col_sum2:
                            total_sinc = df_sres_metrics['Sincronizados'].sum()
                            st.metric("✅ Total Sincronizado", f"{total_sinc:,}")
                        
                        with col_sum3:
                            avg_sync_rate = df_sres_metrics['Taxa Sinc. (%)'].mean()
                            st.metric("📈 Taxa Média Sinc.", f"{avg_sync_rate:.1f}%")
    
    # ============================================
    # ANÁLISES MELHORADAS (COM NOVAS FUNCIONALIDADES)
    # ============================================
    st.markdown("---")
    st.markdown('<div class="section-title-exec">🔍 ANÁLISES AVANÇADAS</div>', unsafe_allow_html=True)
    
    # Criar abas para as análises adicionais
    tab_extra1, tab_extra2, tab_extra3 = st.tabs([
        "🚀 Performance de Desenvolvedores",
        "📈 Análise de Sazonalidade", 
        "⚡ Diagnóstico de Erros"
    ])
    
    # ABA 1: PERFORMANCE DE DESENVOLVEDORES - MELHORADA E DINÂMICA
    with tab_extra1:
        # APAGADO: Container expansível "SOBRE ESTA ANÁLISE"
        
        if 'Responsável_Formatado' in df.columns and 'Revisões' in df.columns and 'Status' in df.columns:
            # Filtros para performance - REMOVIDO "Mínimo de chamados" e ADICIONADO Ano e Mês
            col_filtro_perf1, col_filtro_perf2, col_filtro_perf3 = st.columns(3)
            
            with col_filtro_perf1:
                # REMOVIDO: filtro de mínimo de chamados
                # ADICIONADO: Filtro por ano
                if 'Ano' in df.columns:
                    anos_perf = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_perf = ['Todos os Anos'] + list(anos_perf)
                    ano_perf = st.selectbox(
                        "📅 Ano:",
                        options=anos_opcoes_perf,
                        index=len(anos_opcoes_perf)-1,
                        key="filtro_ano_perf"
                    )
            
            with col_filtro_perf2:
                # ADICIONADO: Filtro por mês
                if 'Mês' in df.columns:
                    meses_perf = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_perf = ['Todos os Meses'] + [str(m) for m in meses_perf]
                    mes_perf = st.selectbox(
                        "📆 Mês:",
                        options=meses_opcoes_perf,
                        key="filtro_mes_perf"
                    )
            
            with col_filtro_perf3:
                ordenar_por = st.selectbox(
                    "Ordenar por:",
                    options=["Score de Qualidade", "Total de Chamados", "Eficiência", "Produtividade"],
                    index=0,
                    key="ordenar_perf"
                )
            
            # Filtrar dados conforme ano e mês selecionados
            df_perf = df.copy()
            
            # Aplicar filtro de ano
            if ano_perf != 'Todos os Anos':
                df_perf = df_perf[df_perf['Ano'] == int(ano_perf)]
            
            # Aplicar filtro de mês
            if mes_perf != 'Todos os Meses':
                df_perf = df_perf[df_perf['Mês'] == int(mes_perf)]
            
            # ADICIONADO: Filtrar para excluir Bruna, Pierry e Kewin (SREs)
            sres_excluir = ['Bruna', 'Pierry', 'Kewin']
            
            # Aplicar filtro para excluir SREs (considerando diferentes variações dos nomes)
            devs_permitidos = []
            for dev in df_perf['Responsável_Formatado'].unique():
                if pd.isna(dev):
                    continue
                dev_str = str(dev).lower()
                # Verificar se o nome não contém nenhum dos nomes dos SREs
                if all(sre.lower() not in dev_str for sre in sres_excluir):
                    devs_permitidos.append(dev)
            
            df_perf = df_perf[df_perf['Responsável_Formatado'].isin(devs_permitidos)]
            
            # Calcular métricas por desenvolvedor
            dev_metrics = []
            devs = df_perf['Responsável_Formatado'].unique()
            
            for dev in devs:
                if pd.isna(dev):
                    continue
                    
                dev_data = df_perf[df_perf['Responsável_Formatado'] == dev]
                total_chamados = len(dev_data)
                
                # REMOVIDO: if total_chamados >= min_chamados: (agora mostra todos)
                # Chamados sem revisão
                sem_revisao = len(dev_data[dev_data['Revisões'] == 0])
                score_qualidade = (sem_revisao / total_chamados * 100) if total_chamados > 0 else 0
                
                # Eficiência (sincronizados)
                sincronizados = len(dev_data[dev_data['Status'] == 'Sincronizado'])
                eficiencia = (sincronizados / total_chamados * 100) if total_chamados > 0 else 0
                
                # Produtividade (chamados por mês)
                if 'Criado' in dev_data.columns:
                    meses_ativos = dev_data['Criado'].dt.to_period('M').nunique()
                    produtividade = total_chamados / meses_ativos if meses_ativos > 0 else 0
                else:
                    produtividade = 0
                
                # Classificação
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
                # Converter para DataFrame
                df_dev_metrics = pd.DataFrame(dev_metrics)
                
                # Ordenar
                if ordenar_por == "Score de Qualidade":
                    df_dev_metrics = df_dev_metrics.sort_values('Score Qualidade', ascending=False)
                elif ordenar_por == "Total de Chamados":
                    df_dev_metrics = df_dev_metrics.sort_values('Total Chamados', ascending=False)
                elif ordenar_por == "Eficiência":
                    df_dev_metrics = df_dev_metrics.sort_values('Eficiência', ascending=False)
                elif ordenar_por == "Produtividade":
                    df_dev_metrics = df_dev_metrics.sort_values('Produtividade', ascending=False)
                
                # ============================================
                # MATRIZ DE PERFORMANCE PARA DEVS - COM FILTRO ANO/MÊS
                # ============================================
                st.markdown("### 🎯 Matriz de Performance - Desenvolvedores")
                
                # Container expansível para explicação da métrica
                with st.expander("📊 **Como é calculada a Matriz de Performance?**", expanded=False):
                    st.markdown("""
                    **Fórmulas de Cálculo:**
                    
                    1. **Eficiência** = Total de Cards / Número de Meses Ativos
                    - Mede a produtividade mensal do desenvolvedor
                    
                    2. **Qualidade** = (Cards sem Revisão / Total de Cards) × 100
                    - Mede a taxa de aprovação na primeira tentativa
                    
                    3. **Score** = (Qualidade × 0.5) + (Eficiência × 5 × 0.3) + ((Total_Cards / Total_Geral) × 100 × 0.2)
                    - Score composto que balanceia qualidade, eficiência e volume
                    
                    **Classificação por Quadrantes:**
                    - **⭐ Estrelas**: Alta eficiência + Alta qualidade
                    - **⚡ Eficientes**: Alta eficiência + Qualidade média/baixa
                    - **🎯 Cuidadosos**: Baixa eficiência + Alta qualidade
                    - **🔄 Necessita Apoio**: Baixa eficiência + Baixa qualidade
                    """)
                
                # ADICIONADO: Filtros para a Matriz de Performance
                col_matriz1, col_matriz2 = st.columns(2)
                
                with col_matriz1:
                    if 'Ano' in df.columns:
                        anos_matriz = sorted(df['Ano'].dropna().unique().astype(int))
                        anos_opcoes_matriz = ['Todos os Anos'] + list(anos_matriz)
                        ano_matriz = st.selectbox(
                            "📅 Ano para Matriz:",
                            options=anos_opcoes_matriz,
                            index=len(anos_opcoes_matriz)-1,
                            key="filtro_ano_matriz"
                        )
                
                with col_matriz2:
                    if 'Mês' in df.columns:
                        meses_matriz = sorted(df['Mês'].dropna().unique().astype(int))
                        meses_opcoes_matriz = ['Todos os Meses'] + [str(m) for m in meses_matriz]
                        mes_matriz = st.selectbox(
                            "📆 Mês para Matriz:",
                            options=meses_opcoes_matriz,
                            key="filtro_mes_matriz"
                        )
                
                # Filtrar dados para a matriz
                df_matriz = df.copy()
                
                if ano_matriz != 'Todos os Anos':
                    df_matriz = df_matriz[df_matriz['Ano'] == int(ano_matriz)]
                
                if mes_matriz != 'Todos os Meses':
                    df_matriz = df_matriz[df_matriz['Mês'] == int(mes_matriz)]
                
                # Filtrar para excluir SREs também na matriz
                devs_matriz_permitidos = []
                for dev in df_matriz['Responsável_Formatado'].unique():
                    if pd.isna(dev):
                        continue
                    dev_str = str(dev).lower()
                    if all(sre.lower() not in dev_str for sre in sres_excluir):
                        devs_matriz_permitidos.append(dev)
                
                df_matriz = df_matriz[df_matriz['Responsável_Formatado'].isin(devs_matriz_permitidos)]
                
                # Criar matriz de performance
                matriz_df = criar_matriz_performance_dev(df_matriz)
                
                if not matriz_df.empty:
                    # REMOVIDO: filtro por mínimo de cards
                    matriz_filtrada = matriz_df.copy()
                    
                    if not matriz_filtrada.empty:
                        # Calcular médias para quadrantes
                        media_eficiencia = matriz_filtrada['Eficiencia'].mean()
                        media_qualidade = matriz_filtrada['Qualidade'].mean()
                        
                        # Classificar em quadrantes
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
                        
                        # Determinar cores: verde para melhor qualidade, vermelho para pior
                        # Ordenar por qualidade para atribuir cores
                        matriz_filtrada = matriz_filtrada.sort_values('Qualidade', ascending=False)
                        
                        # Atribuir cores baseadas na posição na classificação de qualidade
                        num_devs = len(matriz_filtrada)
                        colors_scatter = []
                        for i in range(num_devs):
                            # Normalizar posição (0 = melhor qualidade, 1 = pior qualidade)
                            pos_normalizada = i / max(num_devs - 1, 1)
                            # Interpolar entre verde (#28a745) e vermelho (#dc3545)
                            red = int(220 * pos_normalizada + 40 * (1 - pos_normalizada))
                            green = int(53 * pos_normalizada + 167 * (1 - pos_normalizada))
                            blue = int(69 * pos_normalizada + 69 * (1 - pos_normalizada))
                            colors_scatter.append(f'rgb({red}, {green}, {blue})')
                        
                        # Criar título dinâmico para matriz
                        titulo_matriz = "Matriz de Performance: Eficiência vs Qualidade"
                        if ano_matriz != 'Todos os Anos':
                            titulo_matriz += f" - {ano_matriz}"
                        if mes_matriz != 'Todos os Meses':
                            meses_nomes = {
                                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                            }
                            titulo_matriz += f" - {meses_nomes[int(mes_matriz)]}"
                        
                        # Gráfico de dispersão com cores personalizadas
                        fig_matriz = px.scatter(
                            matriz_filtrada,
                            x='Eficiencia',
                            y='Qualidade',
                            size='Score',
                            color=colors_scatter,  # Usar lista de cores personalizadas
                            hover_name='Desenvolvedor',
                            title=titulo_matriz,
                            labels={
                                'Eficiencia': 'Eficiência (Cards/Mês)',
                                'Qualidade': 'Qualidade (% Aprovação sem Revisão)',
                                'Score': 'Score Performance'
                            },
                            size_max=30
                        )
                        
                        # Remover legenda de cores (não é necessária com cores personalizadas)
                        fig_matriz.update_traces(showlegend=False)
                        
                        # Adicionar linhas de média
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
                        
                        # Adicionar anotações para os quadrantes
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
                        
                        # Tabela de classificação por quadrante
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
                        
                        # ============================================
                        # RECOMENDAÇÕES PERSONALIZADAS PARA DEVS (MINIMIZADO)
                        # ============================================
                        st.markdown("### 💡 Recomendações Personalizadas")
                        
                        # Seletor de Desenvolvedor para recomendações
                        devs_recom = sorted([d for d in df_perf['Responsável_Formatado'].dropna().unique() if d in devs_permitidos])
                        
                        if devs_recom:
                            dev_recom_selecionado = st.selectbox(
                                "Selecione o Desenvolvedor para recomendações:",
                                options=devs_recom,
                                key="dev_recomendacoes"
                            )
                            
                            # Gerar recomendações
                            recomendacoes = gerar_recomendacoes_dev(df_perf, dev_recom_selecionado)
                            
                            if recomendacoes:
                                # Container colapsável para as recomendações
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
                                        <div class="{cor_card}" style="margin-bottom: 15px;">
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
                                    
                                    # Botão para expandir plano de ação
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
                                st.success(f"✅ {dev_recom_selecionado} está com excelente performance! Não há recomendações específicas no momento.")
                
                # Mostrar top 10 - EXCLUINDO SREs
                st.markdown(f"### 🏆 Top 10 Desenvolvedores ({ordenar_por})")
                
                # Filtrar desenvolvedores para excluir SREs
                df_dev_metrics_filtrado = df_dev_metrics.copy()
                df_dev_metrics_filtrado = df_dev_metrics_filtrado[~df_dev_metrics_filtrado['Desenvolvedor'].str.contains('|'.join(sres_excluir), case=False, na=False)]
                
                # Gráfico de barras horizontais para Score de Qualidade
                if ordenar_por == "Score de Qualidade":
                    top10_score = df_dev_metrics_filtrado.head(10)
                    
                    if not top10_score.empty:
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
                    # Para outras ordenações, usar gráfico de barras
                    top10_other = df_dev_metrics_filtrado.head(10)
                    
                    if not top10_other.empty:
                        if ordenar_por == "Total de Chamados":
                            col_ordenada = 'Total Chamados'
                            color_scale = 'Blues'
                            titulo = 'Top 10 - Total de Chamados'
                        elif ordenar_por == "Eficiência":
                            col_ordenada = 'Eficiência'
                            color_scale = 'Greens'
                            titulo = 'Top 10 - Eficiência'
                        else:  # Produtividade
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
                
                # Tabela completa - EXCLUINDO SREs
                st.markdown("### 📋 Performance Detalhada")
                
                # Filtrar para excluir SREs na tabela também
                df_dev_metrics_final = df_dev_metrics_filtrado.copy()
                
                st.dataframe(
                    df_dev_metrics_final,
                    use_container_width=True,
                    height=400,
                    column_config={
                        "Desenvolvedor": st.column_config.TextColumn("Desenvolvedor", width="medium"),
                        "Total Chamados": st.column_config.NumberColumn("Total", format="%d"),
                        "Sem Revisão": st.column_config.NumberColumn("Sem Rev.", format="%d"),
                        "Score Qualidade": st.column_config.NumberColumn("Score %", format="%.1f%%"),
                        "Sincronizados": st.column_config.NumberColumn("Sinc.", format="%d"),
                        "Eficiência": st.column_config.NumberColumn("Efic. %", format="%.1f%%"),
                        "Produtividade": st.column_config.NumberColumn("Prod./Mês", format="%.1f"),
                        "Classificação": st.column_config.TextColumn("Classif.")
                    }
                )
            else:
                st.info("Nenhum desenvolvedor encontrado com os critérios selecionados.")
    
    # ABA 2: ANÁLISE DE SAZONALIDADE - MELHORADA COM FILTROS
    with tab_extra2:
        with st.expander("ℹ️ **SOBRE ESTA ANÁLISE**", expanded=False):
            st.markdown("""
            **Análise de Sazonalidade e Padrões Temporais:**
            
            Esta análise identifica padrões no fluxo de demandas ao longo do tempo:
            
            **📅 Padrões por Dia da Semana:**
            - Identifica quais dias têm mais/menos demandas
            - Mostra taxa de sincronização por dia
            - Útil para planningo de recursos
            
            **🕐 Demandas por Hora do Dia:**
            - Identifica horários de pico de criação de chamados
            - Mostra horários com maior taxa de sincronização
            - Filtros por ano e mês disponíveis
            
            **📈 Sazonalidade Mensal:**
            - Distribuição de demandas ao longo dos meses
            - Identifica meses com maior volume
            - Mostra taxa de sincronização mensal
            - Inclui todos os 12 meses (Janeiro a Dezembro)
            
            **📊 Tipos de Gráficos:**
            - Gráficos de barras para comparação
            - Gráficos de linha para tendências
            - Taxas de sincronização sobrepostas
            
            **🎯 Objetivo:**
            Otimizar alocação de recursos e identificar padrões para melhorar eficiência.
            """)
        
        if 'Criado' in df.columns and 'Status' in df.columns:
            # Filtros para sazonalidade
            col_saz_filtro1, col_saz_filtro2, col_saz_filtro3 = st.columns(3)
            
            with col_saz_filtro1:
                anos_saz = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_saz = ['Todos os Anos'] + list(anos_saz)
                ano_saz = st.selectbox(
                    "Selecionar Ano:",
                    options=anos_opcoes_saz,
                    index=len(anos_opcoes_saz)-1,
                    key="ano_saz"
                )
            
            with col_saz_filtro2:
                if ano_saz != 'Todos os Anos':
                    meses_ano = df[df['Ano'] == int(ano_saz)]['Mês'].unique()
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
            
            # Aplicar filtros
            df_saz = df.copy()
            
            if ano_saz != 'Todos os Anos':
                df_saz = df_saz[df_saz['Ano'] == int(ano_saz)]
            
            if mes_saz != 'Todos os Meses':
                df_saz = df_saz[df_saz['Mês'] == int(mes_saz)]
            
            # Análise por dia da semana
            st.markdown("### 📅 Padrões por Dia da Semana")
            
            # Mapear dias da semana
            dias_semana = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dias_portugues = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            dia_mapping = dict(zip(dias_semana, dias_portugues))
            
            df_saz['Dia_Semana'] = df_saz['Criado'].dt.day_name()
            df_saz['Dia_Semana_PT'] = df_saz['Dia_Semana'].map(dia_mapping)
            
            col_dia1, col_dia2 = st.columns(2)
            
            with col_dia1:
                # Total por dia da semana
                demanda_dia = df_saz['Dia_Semana_PT'].value_counts().reindex(dias_portugues).reset_index()
                demanda_dia.columns = ['Dia', 'Total_Demandas']
                
                # Sincronizados por dia
                sinc_dia = df_saz[df_saz['Status'] == 'Sincronizado']['Dia_Semana_PT'].value_counts().reindex(dias_portugues).reset_index()
                sinc_dia.columns = ['Dia', 'Sincronizados']
                
                # Combinar dados
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
                # ============================================
                # DEMANDAS POR HORA DO DIA - COM FILTROS DE ANO E MÊS
                # ============================================
                st.markdown("### 🕐 Demandas por Hora do Dia")
                
                # Filtros específicos para análise por hora
                col_hora_filtro1, col_hora_filtro2 = st.columns(2)
                
                with col_hora_filtro1:
                    anos_hora = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_hora = ['Todos os Anos'] + list(anos_hora)
                    ano_hora = st.selectbox(
                        "Ano para análise horária:",
                        options=anos_opcoes_hora,
                        index=len(anos_opcoes_hora)-1,
                        key="ano_hora"
                    )
                
                with col_hora_filtro2:
                    if ano_hora != 'Todos os Anos':
                        meses_hora = df[df['Ano'] == int(ano_hora)]['Mês'].unique()
                        meses_opcoes_hora = ['Todos os Meses'] + sorted([str(int(m)) for m in meses_hora])
                        mes_hora = st.selectbox(
                            "Mês para análise horária:",
                            options=meses_opcoes_hora,
                            key="mes_hora"
                        )
                    else:
                        mes_hora = 'Todos os Meses'
                
                # Aplicar filtros para análise por hora
                df_hora = df.copy()
                
                if ano_hora != 'Todos os Anos':
                    df_hora = df_hora[df_hora['Ano'] == int(ano_hora)]
                
                if mes_hora != 'Todos os Meses':
                    df_hora = df_hora[df_hora['Mês'] == int(mes_hora)]
                
                # Criar subtítulo dinâmico
                subtitulo_hora = "Análise por Hora"
                if ano_hora != 'Todos os Anos':
                    subtitulo_hora += f" - {ano_hora}"
                if mes_hora != 'Todos os Meses':
                    meses_nomes = {
                        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                    }
                    subtitulo_hora += f" - {meses_nomes[int(mes_hora)]}"
                
                st.markdown(f"**Período:** {subtitulo_hora}")
                
                # Extrair hora
                df_hora['Hora'] = df_hora['Criado'].dt.hour
                
                # Total por hora
                demanda_hora = df_hora['Hora'].value_counts().sort_index().reset_index()
                demanda_hora.columns = ['Hora', 'Total_Demandas']
                
                # Sincronizados por hora
                sinc_hora = df_hora[df_hora['Status'] == 'Sincronizado']['Hora'].value_counts().sort_index().reset_index()
                sinc_hora.columns = ['Hora', 'Sincronizados']
                
                # Combinar dados
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
                
                # Corrigir as anotações para mostrar a hora formatada corretamente
                if not dados_hora.empty:
                    pico_demanda = dados_hora.loc[dados_hora['Total_Demandas'].idxmax()]
                    pico_sinc = dados_hora.loc[dados_hora['Sincronizados'].idxmax()]
                    
                    # Formatar hora para 2 dígitos (00, 01, 02, ..., 23)
                    hora_demanda_fmt = f"{int(pico_demanda['Hora']):02d}"
                    hora_sinc_fmt = f"{int(pico_sinc['Hora']):02d}"
                    
                    # Adicionar anotações para picos
                    fig_horas.add_annotation(
                        x=pico_demanda['Hora'],
                        y=pico_demanda['Total_Demandas'],
                        text=f"Pico Demandas: {int(pico_demanda['Total_Demandas'])}<br>{hora_demanda_fmt}:00h",
                        showarrow=True,
                        arrowhead=2,
                        ax=0,
                        ay=-40,
                        bgcolor="white",
                        bordercolor="black",
                        font=dict(size=10)
                    )
                    
                    fig_horas.add_annotation(
                        x=pico_sinc['Hora'],
                        y=pico_sinc['Sincronizados'],
                        text=f"Pico Sinc: {int(pico_sinc['Sincronizados'])}<br>{hora_sinc_fmt}:00h",
                        showarrow=True,
                        arrowhead=2,
                        ax=0,
                        ay=40,
                        bgcolor="white",
                        bordercolor="green",
                        font=dict(size=10)
                    )
                
                fig_horas.update_layout(
                    title=f'Demandas por Hora do Dia - {subtitulo_hora}',
                    xaxis_title='Hora do Dia',
                    yaxis_title='Quantidade',
                    height=400,
                    showlegend=True,
                    xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(0, 24)),
                        ticktext=[f"{h:02d}:00" for h in range(0, 24)],
                        tickangle=45
                    )
                )
                
                st.plotly_chart(fig_horas, use_container_width=True)
                
                # Estatísticas de pico com horas formatadas
                if not dados_hora.empty:
                    col_hora_stats1, col_hora_stats2, col_hora_stats3 = st.columns(3)
                    
                    with col_hora_stats1:
                        hora_pico_demanda = dados_hora.loc[dados_hora['Total_Demandas'].idxmax()]
                        hora_fmt_demanda = f"{int(hora_pico_demanda['Hora']):02d}:00h"
                        st.metric("🕐 Pico de Demandas", 
                                 hora_fmt_demanda, 
                                 f"{int(hora_pico_demanda['Total_Demandas'])} demandas")
                    
                    with col_hora_stats2:
                        hora_pico_sinc = dados_hora.loc[dados_hora['Sincronizados'].idxmax()]
                        hora_fmt_sinc = f"{int(hora_pico_sinc['Hora']):02d}:00h"
                        st.metric("✅ Pico de Sincronizações", 
                                 hora_fmt_sinc, 
                                 f"{int(hora_pico_sinc['Sincronizados'])} sinc.")
                    
                    with col_hora_stats3:
                        melhor_taxa_hora = dados_hora.loc[dados_hora['Taxa_Sinc'].idxmax()]
                        hora_fmt_taxa = f"{int(melhor_taxa_hora['Hora']):02d}:00h"
                        st.metric("🏆 Melhor Taxa Sinc.", 
                                 hora_fmt_taxa, 
                                 f"{melhor_taxa_hora['Taxa_Sinc']}%")
            
            # ============================================
            # SAZONALIDADE MENSAL - CORRIGIDA PARA MOSTRAR DEZEMBRO
            # ============================================
            st.markdown("### 📈 Sazonalidade Mensal")
            
            # Filtro simples para sazonalidade mensal
            col_saz_mes1, col_saz_mes2 = st.columns(2)
            
            with col_saz_mes1:
                anos_saz_mes = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_saz_mes = ['Todos os Anos'] + list(anos_saz_mes)
                ano_saz_mes = st.selectbox(
                    "Selecionar Ano para análise mensal:",
                    options=anos_opcoes_saz_mes,
                    index=len(anos_opcoes_saz_mes)-1,
                    key="ano_saz_mes"
                )
            
            with col_saz_mes2:
                # Apenas mostra o ano selecionado
                if ano_saz_mes != 'Todos os Anos':
                    st.markdown(f"**Ano selecionado:** {ano_saz_mes}")
                else:
                    st.markdown("**Todos os anos**")
            
            # Aplicar filtro para análise mensal
            if ano_saz_mes != 'Todos os Anos':
                df_saz_mes = df[df['Ano'] == int(ano_saz_mes)].copy()
            else:
                df_saz_mes = df.copy()
            
            if not df_saz_mes.empty:
                # Ordem dos meses abreviados em português (incluindo Dezembro)
                meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                meses_nomes_completos = {
                    'Jan': 'Janeiro', 'Fev': 'Fevereiro', 'Mar': 'Março', 'Abr': 'Abril',
                    'Mai': 'Maio', 'Jun': 'Junho', 'Jul': 'Julho', 'Ago': 'Agosto',
                    'Set': 'Setembro', 'Out': 'Outubro', 'Nov': 'Novembro', 'Dez': 'Dezembro'
                }
                
                # Usar o mês abreviado já criado na função carregar_dados
                if 'Nome_Mês' in df_saz_mes.columns:
                    # Garantir que estamos usando a abreviação correta
                    df_saz_mes['Mês_Abrev'] = df_saz_mes['Nome_Mês']
                else:
                    # Se não existir, criar a partir da data
                    df_saz_mes['Mês_Abrev'] = df_saz_mes['Criado'].dt.month.map({
                        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
                        5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
                        9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
                    })
                
                # Dados mensais para o ano selecionado
                demanda_mes = df_saz_mes.groupby('Mês_Abrev').size().reset_index()
                demanda_mes.columns = ['Mês', 'Total']
                
                # Reindex para garantir todos os 12 meses aparecem
                demanda_mes = demanda_mes.set_index('Mês').reindex(meses_ordem).reset_index()
                demanda_mes['Total'] = demanda_mes['Total'].fillna(0).astype(int)
                
                sinc_mes = df_saz_mes[df_saz_mes['Status'] == 'Sincronizado'].groupby('Mês_Abrev').size().reset_index()
                sinc_mes.columns = ['Mês', 'Sincronizados']
                
                # Reindex para garantir todos os 12 meses aparecem
                sinc_mes = sinc_mes.set_index('Mês').reindex(meses_ordem).reset_index()
                sinc_mes['Sincronizados'] = sinc_mes['Sincronizados'].fillna(0).astype(int)
                
                dados_mes = pd.merge(demanda_mes, sinc_mes, on='Mês', how='left').fillna(0)
                dados_mes['Taxa_Sinc'] = (dados_mes['Sincronizados'] / dados_mes['Total'] * 100).where(dados_mes['Total'] > 0, 0).round(1)
                
                # Criar título dinâmico
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
                
                # Estatísticas de pico
                col_pico1, col_pico2, col_pico3 = st.columns(3)
                
                with col_pico1:
                    mes_maior_demanda = dados_mes.loc[dados_mes['Total'].idxmax()]
                    st.metric("📈 Mês com mais demandas", 
                             f"{meses_nomes_completos.get(mes_maior_demanda['Mês'], mes_maior_demanda['Mês'])}: {int(mes_maior_demanda['Total'])}")
                
                with col_pico2:
                    mes_maior_sinc = dados_mes.loc[dados_mes['Sincronizados'].idxmax()]
                    st.metric("✅ Mês com mais sincronizações", 
                             f"{meses_nomes_completos.get(mes_maior_sinc['Mês'], mes_maior_sinc['Mês'])}: {int(mes_maior_sinc['Sincronizados'])}")
                
                with col_pico3:
                    melhor_taxa = dados_mes.loc[dados_mes['Taxa_Sinc'].idxmax()]
                    st.metric("🏆 Melhor taxa de sincronização", 
                             f"{meses_nomes_completos.get(melhor_taxa['Mês'], melhor_taxa['Mês'])}: {melhor_taxa['Taxa_Sinc']}%")
    
    # ABA 3: DIAGNÓSTICO DE ERROS - SURPREENDENTE
    with tab_extra3:
        with st.expander("ℹ️ **SOBRE ESTA ANÁLISE**", expanded=False):
            st.markdown("""
            **Análise Avançada de Erros:**
            - 🔍 **Identificação de padrões recorrentes**
            - 📊 **Análise de causas raiz**
            - ⚡ **Recomendações automáticas**
            - 🎯 **Foco em prevenção**
            """)
        
        if 'Tipo_Chamado' in df.columns:
            # Filtros para diagnóstico
            col_diag1, col_diag2, col_diag3 = st.columns(3)
            
            with col_diag1:
                anos_diag = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_diag = ['Todos os Anos'] + list(anos_diag)
                ano_diag = st.selectbox(
                    "Selecionar Ano:",
                    options=anos_opcoes_diag,
                    index=len(anos_opcoes_diag)-1,
                    key="ano_diag"
                )
            
            with col_diag2:
                if ano_diag != 'Todos os Anos':
                    meses_diag = df[df['Ano'] == int(ano_diag)]['Mês'].unique()
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
            
            # Aplicar filtros
            df_diag = df.copy()
            
            if ano_diag != 'Todos os Anos':
                df_diag = df_diag[df_diag['Ano'] == int(ano_diag)]
            
            if mes_diag != 'Todos os Meses':
                df_diag = df_diag[df_diag['Mês'] == int(mes_diag)]
            
            # Análise principal baseada na seleção
            if tipo_analise_diag == "Tipos de Erro":
                st.markdown("### 🔍 Análise de Tipos de Erro")
                
                # Distribuição por tipo
                tipos_erro = df_diag['Tipo_Chamado'].value_counts().resetindex()
                tipos_erro.columns = ['Tipo', 'Frequência']
                tipos_erro['Percentual'] = (tipos_erro['Frequência'] / len(df_diag) * 100).round(1)
                
                col_tipo1, col_tipo2 = st.columns([2, 1])
                
                with col_tipo1:
                    # Gráfico de pizza
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
                        <div class="{'warning-card' if row['Percentual'] > 10 else 'info-card'}" style="margin-bottom: 10px;">
                            <strong>{row['Tipo']}</strong><br>
                            <small>Frequência: {row['Frequência']}</small><br>
                            <small>Percentual: {row['Percentual']}%</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Análise de severidade (baseada em revisões)
                if 'Revisões' in df_diag.columns:
                    st.markdown("### ⚠️ Análise de Severidade")
                    
                    severidade = df_diag.groupby('Tipo_Chamado').agg({
                        'Revisões': ['mean', 'max', 'sum'],
                        'Chamado': 'count'
                    }).round(2)
                    
                    severidade.columns = ['Média_Revisões', 'Max_Revisões', 'Total_Revisões', 'Contagem']
                    severidade = severidade.sort_values('Média_Revisões', ascending=False)
                    
                    # Identificar tipos problemáticos
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
            
            elif tipo_analise_diag == "Tendências Temporais":
                st.markdown("### 📈 Tendências Temporais de Erros")
                
                if 'Criado' in df_diag.columns:
                    # Agrupar por mês
                    df_diag['Mes_Ano'] = df_diag['Criado'].dt.strftime('%Y-%m')
                    
                    evolucao = df_diag.groupby(['Mes_Ano', 'Tipo_Chamado']).size().resetindex()
                    evolucao.columns = ['Mês_Ano', 'Tipo', 'Quantidade']
                    
                    # Top 5 tipos para análise
                    top_tipos = df_diag['Tipo_Chamado'].value_counts().head(5).index.tolist()
                    evol_top = evolucao[evolucao['Tipo'].isin(top_tipos)]
                    
                    # Gráfico de linha
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
                    
                    # Detecção de tendências
                    st.markdown("### 🔍 Detecção de Tendências")
                    
                    # Calcular crescimento para cada tipo
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
                    # Análise por SRE
                    impacto_sre = df_diag.groupby('SRE').agg({
                        'Tipo_Chamado': lambda x: x.value_counts().index[0] if len(x) > 0 else 'N/A',
                        'Revisões': ['mean', 'sum'],
                        'Chamado': 'count'
                    }).round(2)
                    
                    impacto_sre.columns = ['Tipo_Mais_Comum', 'Média_Revisões', 'Total_Revisões', 'Qtd_Chamados']
                    impacto_sre = impacto_sre.sort_values('Total_Revisões', ascending=False)
                    
                    col_impacto1, col_impacto2 = st.columns(2)
                    
                    with col_impacto1:
                        # Gráfico de impacto
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
                        
                        # Identificar SREs que precisam de atenção
                        sre_atencao = impacto_sre[
                            (impacto_sre['Média_Revisões'] > impacto_sre['Média_Revisões'].median()) &
                            (impacto_sre['Qtd_Chamados'] > 5)
                        ]
                        
                        if not sre_atencao.empty:
                            for idx, row in sre_atencao.head(3).iterrows():
                                st.markdown(f"""
                                <div class="warning-card">
                                    <strong>⚠️ {idx}</strong><br>
                                    <small>Tipo mais comum: {row['Tipo_Mais_Comum']}</small><br>
                                    <small>Média revisões: {row['Média_Revisões']}</small><br>
                                    <small>Total revisões: {int(row['Total_Revisões'])}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # SREs com melhor performance
                        sre_melhor = impacto_sre[
                            (impacto_sre['Média_Revisões'] < impacto_sre['Média_Revisões'].quantile(0.25)) &
                            (impacto_sre['Qtd_Chamados'] > 5)
                        ]
                        
                        if not sre_melhor.empty:
                            for idx, row in sre_melhor.head(3).iterrows():
                                st.markdown(f"""
                                <div class="performance-card">
                                    <strong>✅ {idx}</strong><br>
                                    <small>Tipo mais comum: {row['Tipo_Mais_Comum']}</small><br>
                                    <small>Média revisões: {row['Média_Revisões']}</small><br>
                                    <small>Total revisões: {int(row['Total_Revisões'])}</small>
                                </div>
                                """, unsafe_allow_html=True)
            
            elif tipo_analise_diag == "Recomendações":
                st.markdown("### 💡 Recomendações Inteligentes")
                
                # Gerar recomendações baseadas nos dados
                recomendacoes = []
                
                # 1. Análise de tipos frequentes
                tipos_frequentes = df_diag['Tipo_Chamado'].value_counts().head(3)
                for tipo, count in tipos_frequentes.items():
                    if count > len(df_diag) * 0.1:  # Mais de 10% do total
                        recomendacoes.append({
                            'Prioridade': '🔴 ALTA',
                            'Recomendação': f'Investigar causa raiz do tipo "{tipo}"',
                            'Justificativa': f'Responsável por {count} ocorrências ({count/len(df_diag)*100:.1f}% do total)'
                        })
                
                # 2. Análise temporal
                if 'Criado' in df_diag.columns:
                    df_diag['Dia_Semana'] = df_diag['Criado'].dt.day_name()
                    dia_pico = df_diag['Dia_Semana'].value_counts().index[0]
                    
                    recomendacoes.append({
                        'Prioridade': '🟡 MÉDIA',
                        'Recomendação': f'Reforçar equipe às {dia_pico}s',
                        'Justificativa': f'Dia com maior volume de chamados'
                    })
                
                # 3. Análise de revisões
                if 'Revisões' in df_diag.columns:
                    media_revisoes = df_diag['Revisões'].mean()
                    if media_revisoes > 2:
                        recomendacoes.append({
                            'Prioridade': '🔴 ALTA',
                            'Recomendação': 'Implementar revisão de código mais rigorosa',
                            'Justificativa': f'Média de {media_revisoes:.1f} revisões por chamado'
                        })
                
                # 4. Análise de SRE
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
                
                # Exibir recomendações
                if recomendacoes:
                    df_recomendacoes = pd.DataFrame(recomendacoes)
                    
                    for idx, row in df_recomendacoes.iterrows():
                        st.markdown(f"""
                        <div class="{ 'warning-card' if 'ALTA' in row['Prioridade'] else 'info-card' if 'MÉDIA' in row['Prioridade'] else 'performance-card'}" 
                                   style="margin-bottom: 15px; padding: 15px;">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div>
                                    <strong style="font-size: 1.1rem;">{row['Prioridade']} - {row['Recomendação']}</strong><br>
                                    <small style="color: #6c757d;">{row['Justificativa']}</small>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Ações sugeridas
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
    
    # ============================================
    # TOP 10 RESPONSÁVEIS
    # ============================================
    st.markdown("---")
    col_top, col_dist = st.columns([2, 1])
    
    with col_top:
        st.markdown('<div class="section-title-exec">👥 TOP 10 RESPONSÁVEIS</div>', unsafe_allow_html=True)
        
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
        
        if 'Tipo_Chamado' in df.columns:
            # Agrupar por tipo de chamado
            tipos_chamado = df['Tipo_Chamado'].value_counts().reset_index()
            tipos_chamado.columns = ['Tipo', 'Quantidade']
            
            # Ordenar por quantidade
            tipos_chamado = tipos_chamado.sort_values('Quantidade', ascending=True)
            
            # Criar gráfico de barras horizontais
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
    
    # ============================================
    # ÚLTIMAS DEMANDAS REGISTRADAS COM FILTROS (ORIGINAL)
    # ============================================
    st.markdown("---")
    st.markdown('<div class="section-title-exec">🕒 ÚLTIMAS DEMANDAS REGISTRADAS</div>', unsafe_allow_html=True)
    
    if 'Criado' in df.columns:
        # FILTRO DE BUSCA POR CHAMADO ESPECÍFICO - MANTIDO
        filtro_chamado_principal = st.text_input(
            "🔎 Buscar chamado específico:",
            placeholder="Digite o número do chamado...",
            key="filtro_chamado_principal"
        )
        
        # Filtros para a tabela
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
            # Mantendo todas as colunas originais
            mostrar_colunas = st.multiselect(
                "Colunas a mostrar:",
                options=['Chamado', 'Tipo_Chamado', 'Responsável', 'Status', 'Prioridade', 
                        'Revisões', 'Empresa', 'SRE', 'Data', 'Responsável_Formatado'],
                default=['Chamado', 'Tipo_Chamado', 'Responsável_Formatado', 'Status', 'Data'],
                key="select_colunas"
            )
        
        with col_filtro4:
            # Filtro de busca por chamado específico (adicional ao filtro principal)
            filtro_chamado_tabela = st.text_input(
                "Filtro adicional:",
                placeholder="Ex: 12345",
                key="input_filtro_chamado"
            )
        
        # Aplicar ordenação
        ultimas_demandas = df.copy()
        
        # Aplicar filtro principal de busca por chamado
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
        
        # Aplicar filtro de busca por chamado adicional
        if filtro_chamado_tabela:
            ultimas_demandas = ultimas_demandas[
                ultimas_demandas['Chamado'].astype(str).str.contains(filtro_chamado_tabela, na=False)
            ]
        
        # Limitar quantidade
        ultimas_demandas = ultimas_demandas.head(qtd_demandas)
        
        # Preparar dados para exibição
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
            
            # Botão de exportação
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
# RODAPÉ COM HORÁRIO DE ATUALIZAÇÃO
# ============================================
st.markdown("---")

# Obter horário da última atualização
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
