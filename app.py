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
from plotly.subplots import make_subplots
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
    page_title="Esteira ADMS - Dashboard SRE",
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
    
    /* Novos estilos para análises SRE */
    .sre-score-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fcff 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .score-excelente { border-left-color: #28a745; }
    .score-bom { border-left-color: #17a2b8; }
    .score-regular { border-left-color: #ffc107; }
    .score-melhorar { border-left-color: #dc3545; }
    
    .matrix-cell {
        padding: 10px;
        text-align: center;
        border-radius: 5px;
        font-weight: 600;
    }
    
    .matrix-high { background-color: #d4edda; color: #155724; }
    .matrix-medium { background-color: #fff3cd; color: #856404; }
    .matrix-low { background-color: #f8d7da; color: #721c24; }
    
    /* Status colors */
    .status-sincronizado { color: #28a745; font-weight: bold; }
    .status-devrevisao { color: #dc3545; font-weight: bold; }
    .status-emvalidacao { color: #ffc107; font-weight: bold; }
    
    /* Timeline styles */
    .timeline-event {
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 6px;
        border-left: 4px solid;
    }
    
    .event-dev { border-left-color: #6f42c1; background-color: #f2e8ff; }
    .event-sre { border-left-color: #20c997; background-color: #e6f7f2; }
    .event-sinc { border-left-color: #007bff; background-color: #e7f1ff; }
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

# ============================================
# NOVAS FUNÇÕES PARA ANÁLISE SRE
# ============================================

def calcular_metricas_sre(df, sre_nome):
    """Calcula métricas de performance para um SRE específico"""
    
    # Filtrar dados do SRE
    df_sre = df[df['SRE'] == sre_nome].copy()
    
    if len(df_sre) == 0:
        return None
    
    # Métricas básicas
    total_cards = len(df_sre)
    cards_sincronizados = len(df_sre[df_sre['Status'] == 'Sincronizado'])
    
    # Calcular taxa de retorno (Status mudou de SRE para Dev Revisão)
    # Esta é uma estimativa baseada nas revisões
    taxa_retorno = 0
    if 'Revisões' in df_sre.columns:
        cards_com_revisoes = len(df_sre[df_sre['Revisões'] > 0])
        taxa_retorno = (cards_com_revisoes / total_cards * 100) if total_cards > 0 else 0
    
    # Calcular taxa de aprovação na primeira tentativa
    taxa_primeira_aprovacao = 100 - taxa_retorno
    
    # Calcular eficiência (cards por mês)
    if 'Criado' in df_sre.columns:
        meses_ativos = df_sre['Criado'].dt.to_period('M').nunique()
        eficiencia = total_cards / meses_ativos if meses_ativos > 0 else 0
    else:
        eficiencia = 0
    
    # Calcular score composto
    score = (
        (taxa_primeira_aprovacao * 0.4) +  # Qualidade (40%)
        (eficiencia * 2 * 0.3) +            # Eficiência (30%) - escalado
        (cards_sincronizados / max(total_cards, 1) * 100 * 0.3)  # Produtividade (30%)
    )
    
    return {
        'SRE': sre_nome,
        'Total_Cards': total_cards,
        'Cards_Sincronizados': cards_sincronizados,
        'Taxa_Retorno': round(taxa_retorno, 1),
        'Taxa_Primeira_Aprovacao': round(taxa_primeira_aprovacao, 1),
        'Eficiencia_Cards_Mes': round(eficiencia, 1),
        'Score_Performance': round(score, 1)
    }

def criar_matriz_performance(df_sres):
    """Cria matriz de performance (Eficiência vs Qualidade)"""
    
    # Preparar dados para a matriz
    matriz_data = []
    for sre in df_sres['SRE'].unique():
        metricas = calcular_metricas_sre(df_sres, sre)
        if metricas:
            matriz_data.append({
                'SRE': sre,
                'Eficiencia': metricas['Eficiencia_Cards_Mes'],
                'Qualidade': metricas['Taxa_Primeira_Aprovacao'],
                'Score': metricas['Score_Performance']
            })
    
    return pd.DataFrame(matriz_data)

def analisar_tendencia_temporal_sre(df, sre_nome):
    """Analisa tendência temporal das sincronizações do SRE"""
    
    df_sre = df[df['SRE'] == sre_nome].copy()
    
    if len(df_sre) == 0:
        return None
    
    # Agrupar por mês
    if 'Criado' in df_sre.columns:
        df_sre['Mes_Ano'] = df_sre['Criado'].dt.strftime('%Y-%m')
        
        # Cards sincronizados por mês
        sinc_mes = df_sre[df_sre['Status'] == 'Sincronizado'].groupby('Mes_Ano').size().reset_index()
        sinc_mes.columns = ['Mes_Ano', 'Sincronizados']
        
        # Total de cards por mês
        total_mes = df_sre.groupby('Mes_Ano').size().reset_index()
        total_mes.columns = ['Mes_Ano', 'Total']
        
        # Combinar dados
        dados_mes = pd.merge(total_mes, sinc_mes, on='Mes_Ano', how='left').fillna(0)
        dados_mes['Taxa_Sinc'] = (dados_mes['Sincronizados'] / dados_mes['Total'] * 100).round(1)
        
        return dados_mes.sort_values('Mes_Ano')
    
    return None

def gerar_recomendacoes_sre(metricas):
    """Gera recomendações personalizadas para o SRE"""
    
    recomendacoes = []
    
    if metricas['Taxa_Retorno'] > 20:
        recomendacoes.append({
            'Prioridade': 'ALTA',
            'Recomendação': 'Reduzir taxa de retorno',
            'Ação': 'Implementar checklist de validação mais rigoroso'
        })
    
    if metricas['Eficiencia_Cards_Mes'] < 10:
        recomendacoes.append({
            'Prioridade': 'MÉDIA',
            'Recomendação': 'Aumentar produtividade',
            'Ação': 'Otimizar processo de validação e usar templates'
        })
    
    if metricas['Score_Performance'] < 60:
        recomendacoes.append({
            'Prioridade': 'ALTA',
            'Recomendação': 'Melhorar performance geral',
            'Ação': 'Participar de sessões de pair validation'
        })
    
    if metricas['Taxa_Primeira_Aprovacao'] > 90:
        recomendacoes.append({
            'Prioridade': 'BAIXA',
            'Recomendação': 'Manter excelente performance',
            'Ação': 'Compartilhar best practices com a equipe'
        })
    
    return recomendacoes

# ============================================
# CONTINUAÇÃO DO CÓDIGO (mantenha as funções anteriores...
# encontrar_arquivo_dados(), verificar_atualizacao_arquivo(), 
# limpar_sessao_dados(), get_horario_brasilia(), etc.)
# ============================================

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
# SIDEBAR - FILTROS E CONTROLES
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
    
    # ... (resto do sidebar - mantém igual ao original)
    # [TODO: Manter todo o código do sidebar original aqui]

# ============================================
# CONTEÚDO PRINCIPAL
# ============================================

# HEADER
st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="color: white; margin: 0; font-size: 1.8rem; font-weight: 700;">📊 ESTEIRA ADMS - DASHBOARD SRE</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 1rem;">
            Sistema de Análise de Performance dos SREs
            </p>
        </div>
        <div style="text-align: right;">
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
            Fluxo: DEV → SRE → Aguardando Sinc
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 0.2rem 0 0 0; font-size: 0.85rem;">
            v6.0 | Análise Avançada de Performance
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
    # NOVA ABA: PERFORMANCE DOS SREs (ATUALIZADA)
    # ============================================
    st.markdown("---")
    
    # Criar abas principais
    tab_sre1, tab_sre2, tab_sre3, tab_sre4 = st.tabs([
        "🏆 Performance Geral", 
        "📈 Tendência Temporal", 
        "🎯 Matriz de Performance",
        "💡 Recomendações"
    ])
    
    with tab_sre1:
        st.markdown('<div class="section-title-exec">🏆 PERFORMANCE GERAL DOS SREs</div>', unsafe_allow_html=True)
        
        if 'SRE' in df.columns and 'Status' in df.columns:
            # Filtros para análise SRE
            col_filtro1, col_filtro2 = st.columns(2)
            
            with col_filtro1:
                # Filtrar por ano
                if 'Ano' in df.columns:
                    anos_sre = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_sre = ['Todos os Anos'] + list(anos_sre)
                    ano_sre = st.selectbox(
                        "📅 Filtrar por Ano:",
                        options=anos_opcoes_sre,
                        key="filtro_ano_sre_perf"
                    )
            
            with col_filtro2:
                # Filtrar por mês
                if 'Mês' in df.columns:
                    meses_sre = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_sre = ['Todos os Meses'] + [str(m) for m in meses_sre]
                    mes_sre = st.selectbox(
                        "📆 Filtrar por Mês:",
                        options=meses_opcoes_sre,
                        key="filtro_mes_sre_perf"
                    )
            
            # Aplicar filtros
            df_sre = df.copy()
            
            if 'Ano' in df_sre.columns and ano_sre != 'Todos os Anos':
                df_sre = df_sre[df_sre['Ano'] == int(ano_sre)]
            
            if 'Mês' in df_sre.columns and mes_sre != 'Todos os Meses':
                df_sre = df_sre[df_sre['Mês'] == int(mes_sre)]
            
            # Calcular métricas para todos os SREs
            sres_metricas = []
            sres = df_sre['SRE'].dropna().unique()
            
            for sre in sres:
                metricas = calcular_metricas_sre(df_sre, sre)
                if metricas:
                    sres_metricas.append(metricas)
            
            if sres_metricas:
                df_metricas = pd.DataFrame(sres_metricas)
                
                # Ordenar por Score
                df_metricas = df_metricas.sort_values('Score_Performance', ascending=False)
                
                # Exibir métricas principais
                st.markdown("### 📊 Métricas de Performance por SRE")
                
                # Criar cards para os top 3 SREs
                if len(df_metricas) >= 3:
                    col_top1, col_top2, col_top3 = st.columns(3)
                    
                    with col_top1:
                        top1 = df_metricas.iloc[0]
                        st.markdown(f"""
                        <div class="sre-score-card score-excelente">
                            <h4>🥇 {top1['SRE']}</h4>
                            <p><strong>Score:</strong> {top1['Score_Performance']}</p>
                            <p><strong>Taxa 1ª Aprovação:</strong> {top1['Taxa_Primeira_Aprovacao']}%</p>
                            <p><strong>Cards/Mês:</strong> {top1['Eficiencia_Cards_Mes']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_top2:
                        top2 = df_metricas.iloc[1]
                        st.markdown(f"""
                        <div class="sre-score-card score-bom">
                            <h4>🥈 {top2['SRE']}</h4>
                            <p><strong>Score:</strong> {top2['Score_Performance']}</p>
                            <p><strong>Taxa 1ª Aprovação:</strong> {top2['Taxa_Primeira_Aprovacao']}%</p>
                            <p><strong>Cards/Mês:</strong> {top2['Eficiencia_Cards_Mes']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_top3:
                        top3 = df_metricas.iloc[2]
                        st.markdown(f"""
                        <div class="sre-score-card score-regular">
                            <h4>🥉 {top3['SRE']}</h4>
                            <p><strong>Score:</strong> {top3['Score_Performance']}</p>
                            <p><strong>Taxa 1ª Aprovação:</strong> {top3['Taxa_Primeira_Aprovacao']}%</p>
                            <p><strong>Cards/Mês:</strong> {top3['Eficiencia_Cards_Mes']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Gráfico de barras para Taxa de Retorno
                st.markdown("### 📉 Taxa de Retorno por SRE")
                fig_retorno = px.bar(
                    df_metricas.sort_values('Taxa_Retorno'),
                    x='SRE',
                    y='Taxa_Retorno',
                    title='Taxa de Cards que Retornam para DEV (%)',
                    text='Taxa_Retorno',
                    color='Taxa_Retorno',
                    color_continuous_scale='RdYlGn_r',
                    range_color=[0, 100]
                )
                
                fig_retorno.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside',
                    marker_line_color='black',
                    marker_line_width=1
                )
                
                fig_retorno.update_layout(
                    height=400,
                    xaxis_title="SRE",
                    yaxis_title="Taxa de Retorno (%)",
                    yaxis_range=[0, 100]
                )
                
                st.plotly_chart(fig_retorno, use_container_width=True)
                
                # Tabela completa de métricas
                st.markdown("### 📋 Tabela de Performance Detalhada")
                
                # Adicionar classificação
                def classificar_score(score):
                    if score >= 80:
                        return "🟢 Excelente"
                    elif score >= 65:
                        return "🟡 Bom"
                    elif score >= 50:
                        return "🟠 Regular"
                    else:
                        return "🔴 Precisa Melhorar"
                
                df_metricas['Classificação'] = df_metricas['Score_Performance'].apply(classificar_score)
                
                st.dataframe(
                    df_metricas[['SRE', 'Total_Cards', 'Cards_Sincronizados', 
                                'Taxa_Retorno', 'Taxa_Primeira_Aprovacao', 
                                'Eficiencia_Cards_Mes', 'Score_Performance', 'Classificação']],
                    use_container_width=True,
                    column_config={
                        "SRE": "SRE",
                        "Total_Cards": "Total Cards",
                        "Cards_Sincronizados": "Sincronizados",
                        "Taxa_Retorno": st.column_config.NumberColumn("Taxa Retorno", format="%.1f%%"),
                        "Taxa_Primeira_Aprovacao": st.column_config.NumberColumn("1ª Aprovação", format="%.1f%%"),
                        "Eficiencia_Cards_Mes": st.column_config.NumberColumn("Cards/Mês", format="%.1f"),
                        "Score_Performance": st.column_config.NumberColumn("Score", format="%.1f"),
                        "Classificação": "Classificação"
                    }
                )
    
    with tab_sre2:
        st.markdown('<div class="section-title-exec">📈 TENDÊNCIA TEMPORAL - SINCRONIZAÇÕES POR MÊS</div>', unsafe_allow_html=True)
        
        if 'SRE' in df.columns and 'Status' in df.columns:
            # Seletor de SRE
            sres_disponiveis = sorted(df['SRE'].dropna().unique())
            
            if sres_disponiveis:
                col_sel1, col_sel2 = st.columns(2)
                
                with col_sel1:
                    sre_selecionado = st.selectbox(
                        "Selecione o SRE:",
                        options=sres_disponiveis,
                        key="sre_temporal"
                    )
                
                with col_sel2:
                    # Filtrar por ano
                    if 'Ano' in df.columns:
                        anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                        ano_temporal = st.selectbox(
                            "Ano para análise:",
                            options=['Todos'] + list(anos_disponiveis),
                            key="ano_temporal"
                        )
                
                # Aplicar filtro de ano
                df_temporal = df.copy()
                if ano_temporal != 'Todos' and 'Ano' in df_temporal.columns:
                    df_temporal = df_temporal[df_temporal['Ano'] == int(ano_temporal)]
                
                # Analisar tendência do SRE selecionado
                dados_temporal = analisar_tendencia_temporal_sre(df_temporal, sre_selecionado)
                
                if dados_temporal is not None and not dados_temporal.empty:
                    # Gráfico de linha para sincronizações por mês
                    fig_temporal = go.Figure()
                    
                    # Adicionar linha de sincronizações
                    fig_temporal.add_trace(go.Scatter(
                        x=dados_temporal['Mes_Ano'],
                        y=dados_temporal['Sincronizados'],
                        mode='lines+markers',
                        name='Sincronizações',
                        line=dict(color='#28a745', width=3),
                        marker=dict(size=8, color='#218838'),
                        text=dados_temporal['Sincronizados'],
                        textposition='top center'
                    ))
                    
                    # Adicionar linha de total de cards
                    fig_temporal.add_trace(go.Scatter(
                        x=dados_temporal['Mes_Ano'],
                        y=dados_temporal['Total'],
                        mode='lines+markers',
                        name='Total de Cards',
                        line=dict(color='#1e3799', width=2),
                        marker=dict(size=6, color='#0c2461'),
                        text=dados_temporal['Total'],
                        textposition='top center'
                    ))
                    
                    # Criar gráfico secundário para taxa de sincronização
                    fig_temporal.add_trace(go.Scatter(
                        x=dados_temporal['Mes_Ano'],
                        y=dados_temporal['Taxa_Sinc'],
                        name='Taxa Sinc (%)',
                        yaxis='y2',
                        mode='lines+markers',
                        line=dict(color='#dc3545', width=2, dash='dash'),
                        marker=dict(size=6, color='#dc3545')
                    ))
                    
                    fig_temporal.update_layout(
                        title=f'Tendência Temporal - {sre_selecionado}',
                        xaxis_title='Mês/Ano',
                        yaxis_title='Quantidade de Cards',
                        yaxis2=dict(
                            title='Taxa Sinc (%)',
                            overlaying='y',
                            side='right',
                            range=[0, 100]
                        ),
                        height=500,
                        showlegend=True,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_temporal, use_container_width=True)
                    
                    # Estatísticas da tendência
                    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                    
                    with col_stat1:
                        media_sinc = dados_temporal['Sincronizados'].mean()
                        st.metric("📊 Média Sinc/Mês", f"{media_sinc:.1f}")
                    
                    with col_stat2:
                        crescimento = ((dados_temporal['Sincronizados'].iloc[-1] - dados_temporal['Sincronizados'].iloc[0]) / 
                                     max(dados_temporal['Sincronizados'].iloc[0], 1) * 100)
                        st.metric("📈 Crescimento", f"{crescimento:.1f}%")
                    
                    with col_stat3:
                        melhor_mes = dados_temporal.loc[dados_temporal['Sincronizados'].idxmax()]
                        st.metric("🏆 Melhor Mês", f"{melhor_mes['Mes_Ano']}: {int(melhor_mes['Sincronizados'])}")
                    
                    with col_stat4:
                        media_taxa = dados_temporal['Taxa_Sinc'].mean()
                        st.metric("✅ Taxa Média", f"{media_taxa:.1f}%")
                    
                    # Análise de sazonalidade por dia da semana
                    st.markdown("### 📅 Análise por Dia da Semana")
                    
                    df_sre_dia = df_temporal[df_temporal['SRE'] == sre_selecionado].copy()
                    
                    if 'Criado' in df_sre_dia.columns:
                        # Mapear dias da semana
                        dias_semana = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        dias_portugues = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                        dia_mapping = dict(zip(dias_semana, dias_portugues))
                        
                        df_sre_dia['Dia_Semana'] = df_sre_dia['Criado'].dt.day_name()
                        df_sre_dia['Dia_Semana_PT'] = df_sre_dia['Dia_Semana'].map(dia_mapping)
                        
                        # Cards por dia da semana
                        cards_dia = df_sre_dia['Dia_Semana_PT'].value_counts().reindex(dias_portugues).reset_index()
                        cards_dia.columns = ['Dia', 'Quantidade']
                        
                        fig_dia = px.bar(
                            cards_dia,
                            x='Dia',
                            y='Quantidade',
                            title=f'Distribuição por Dia da Semana - {sre_selecionado}',
                            text='Quantidade',
                            color='Quantidade',
                            color_continuous_scale='Blues'
                        )
                        
                        fig_dia.update_traces(
                            texttemplate='%{text}',
                            textposition='outside'
                        )
                        
                        fig_dia.update_layout(height=400)
                        st.plotly_chart(fig_dia, use_container_width=True)
                else:
                    st.info(f"Não há dados suficientes para análise temporal do SRE {sre_selecionado}")
    
    with tab_sre3:
        st.markdown('<div class="section-title-exec">🎯 MATRIZ DE PERFORMANCE (EFICIÊNCIA vs QUALIDADE)</div>', unsafe_allow_html=True)
        
        if 'SRE' in df.columns:
            # Aplicar filtros para a matriz
            col_matriz1, col_matriz2 = st.columns(2)
            
            with col_matriz1:
                min_cards = st.slider(
                    "Mínimo de cards analisados:",
                    min_value=1,
                    max_value=50,
                    value=10,
                    help="Filtrar SREs com pelo menos X cards analisados"
                )
            
            with col_matriz2:
                # Filtrar por ano para matriz
                if 'Ano' in df.columns:
                    anos_matriz = sorted(df['Ano'].dropna().unique().astype(int))
                    ano_matriz = st.selectbox(
                        "Ano para matriz:",
                        options=['Todos'] + list(anos_matriz),
                        key="ano_matriz"
                    )
            
            # Aplicar filtros
            df_matriz = df.copy()
            if ano_matriz != 'Todos' and 'Ano' in df_matriz.columns:
                df_matriz = df_matriz[df_matriz['Ano'] == int(ano_matriz)]
            
            # Criar matriz de performance
            matriz_df = criar_matriz_performance(df_matriz)
            
            if not matriz_df.empty:
                # Filtrar por mínimo de cards
                sres_com_cards = []
                for sre in matriz_df['SRE']:
                    total_cards = len(df_matriz[df_matriz['SRE'] == sre])
                    if total_cards >= min_cards:
                        sres_com_cards.append(sre)
                
                matriz_df = matriz_df[matriz_df['SRE'].isin(sres_com_cards)]
                
                if not matriz_df.empty:
                    # Criar gráfico de dispersão para a matriz
                    fig_matriz = px.scatter(
                        matriz_df,
                        x='Eficiencia',
                        y='Qualidade',
                        size='Score',
                        color='Score',
                        hover_name='SRE',
                        title='Matriz de Performance: Eficiência vs Qualidade',
                        labels={
                            'Eficiencia': 'Eficiência (Cards/Mês)',
                            'Qualidade': 'Qualidade (% 1ª Aprovação)',
                            'Score': 'Score Performance'
                        },
                        color_continuous_scale='RdYlGn',
                        size_max=30
                    )
                    
                    # Adicionar quadrantes
                    media_eficiencia = matriz_df['Eficiencia'].mean()
                    media_qualidade = matriz_df['Qualidade'].mean()
                    
                    fig_matriz.add_shape(
                        type="line",
                        x0=media_eficiencia,
                        y0=matriz_df['Qualidade'].min(),
                        x1=media_eficiencia,
                        y1=matriz_df['Qualidade'].max(),
                        line=dict(color="gray", width=1, dash="dash")
                    )
                    
                    fig_matriz.add_shape(
                        type="line",
                        x0=matriz_df['Eficiencia'].min(),
                        y0=media_qualidade,
                        x1=matriz_df['Eficiencia'].max(),
                        y1=media_qualidade,
                        line=dict(color="gray", width=1, dash="dash")
                    )
                    
                    # Adicionar anotações dos quadrantes
                    fig_matriz.add_annotation(
                        x=matriz_df['Eficiencia'].max() * 0.8,
                        y=matriz_df['Qualidade'].max() * 0.9,
                        text="⭐ Estrelas<br>(Alta Eficiência, Alta Qualidade)",
                        showarrow=False,
                        font=dict(size=10, color="green"),
                        bgcolor="rgba(255,255,255,0.8)"
                    )
                    
                    fig_matriz.add_annotation(
                        x=matriz_df['Eficiencia'].max() * 0.8,
                        y=matriz_df['Qualidade'].min() * 1.1,
                        text="⚡ Eficientes<br>(Alta Eficiência, Baixa Qualidade)",
                        showarrow=False,
                        font=dict(size=10, color="orange"),
                        bgcolor="rgba(255,255,255,0.8)"
                    )
                    
                    fig_matriz.add_annotation(
                        x=matriz_df['Eficiencia'].min() * 1.1,
                        y=matriz_df['Qualidade'].max() * 0.9,
                        text="🎯 Cuidadosos<br>(Baixa Eficiência, Alta Qualidade)",
                        showarrow=False,
                        font=dict(size=10, color="blue"),
                        bgcolor="rgba(255,255,255,0.8)"
                    )
                    
                    fig_matriz.add_annotation(
                        x=matriz_df['Eficiencia'].min() * 1.1,
                        y=matriz_df['Qualidade'].min() * 1.1,
                        text="🔄 Necessita Apoio<br>(Baixa Eficiência, Baixa Qualidade)",
                        showarrow=False,
                        font=dict(size=10, color="red"),
                        bgcolor="rgba(255,255,255,0.8)"
                    )
                    
                    fig_matriz.update_layout(
                        height=600,
                        xaxis_title="Eficiência (Cards Validados por Mês)",
                        yaxis_title="Qualidade (% de Aprovação na 1ª Validação)",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_matriz, use_container_width=True)
                    
                    # Tabela de classificação por quadrante
                    st.markdown("### 📋 Classificação por Quadrante")
                    
                    # Classificar SREs por quadrante
                    def classificar_quadrante(row):
                        if row['Eficiencia'] >= media_eficiencia and row['Qualidade'] >= media_qualidade:
                            return "⭐ Estrelas"
                        elif row['Eficiencia'] >= media_eficiencia and row['Qualidade'] < media_qualidade:
                            return "⚡ Eficientes"
                        elif row['Eficiencia'] < media_eficiencia and row['Qualidade'] >= media_qualidade:
                            return "🎯 Cuidadosos"
                        else:
                            return "🔄 Necessita Apoio"
                    
                    matriz_df['Quadrante'] = matriz_df.apply(classificar_quadrante, axis=1)
                    
                    # Exibir tabela
                    st.dataframe(
                        matriz_df[['SRE', 'Eficiencia', 'Qualidade', 'Score', 'Quadrante']].sort_values('Score', ascending=False),
                        use_container_width=True,
                        column_config={
                            "SRE": "SRE",
                            "Eficiencia": st.column_config.NumberColumn("Eficiência", format="%.1f"),
                            "Qualidade": st.column_config.NumberColumn("Qualidade", format="%.1f%%"),
                            "Score": st.column_config.NumberColumn("Score", format="%.1f"),
                            "Quadrante": "Classificação"
                        }
                    )
                    
                    # Estatísticas por quadrante
                    st.markdown("### 📊 Estatísticas por Quadrante")
                    
                    stats_quadrantes = matriz_df.groupby('Quadrante').agg({
                        'SRE': 'count',
                        'Eficiencia': 'mean',
                        'Qualidade': 'mean',
                        'Score': 'mean'
                    }).round(1)
                    
                    stats_quadrantes.columns = ['Qtd SREs', 'Média Eficiência', 'Média Qualidade', 'Média Score']
                    
                    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
                    
                    quadrantes_stats = stats_quadrantes.to_dict('index')
                    
                    if '⭐ Estrelas' in quadrantes_stats:
                        with col_q1:
                            st.metric("⭐ Estrelas", 
                                     f"{quadrantes_stats['⭐ Estrelas']['Qtd SREs']} SREs",
                                     f"Score: {quadrantes_stats['⭐ Estrelas']['Média Score']}")
                    
                    if '⚡ Eficientes' in quadrantes_stats:
                        with col_q2:
                            st.metric("⚡ Eficientes", 
                                     f"{quadrantes_stats['⚡ Eficientes']['Qtd SREs']} SREs",
                                     f"Score: {quadrantes_stats['⚡ Eficientes']['Média Score']}")
                    
                    if '🎯 Cuidadosos' in quadrantes_stats:
                        with col_q3:
                            st.metric("🎯 Cuidadosos", 
                                     f"{quadrantes_stats['🎯 Cuidadosos']['Qtd SREs']} SREs",
                                     f"Score: {quadrantes_stats['🎯 Cuidadosos']['Média Score']}")
                    
                    if '🔄 Necessita Apoio' in quadrantes_stats:
                        with col_q4:
                            st.metric("🔄 Necessita Apoio", 
                                     f"{quadrantes_stats['🔄 Necessita Apoio']['Qtd SREs']} SREs",
                                     f"Score: {quadrantes_stats['🔄 Necessita Apoio']['Média Score']}")
                else:
                    st.info("Nenhum SRE encontrado com os critérios selecionados.")
    
    with tab_sre4:
        st.markdown('<div class="section-title-exec">💡 RECOMENDAÇÕES PERSONALIZADAS POR SRE</div>', unsafe_allow_html=True)
        
        if 'SRE' in df.columns:
            # Seletor de SRE para recomendações
            sres_recom = sorted(df['SRE'].dropna().unique())
            
            if sres_recom:
                sre_recom_selecionado = st.selectbox(
                    "Selecione o SRE para recomendações:",
                    options=sres_recom,
                    key="sre_recomendacoes"
                )
                
                # Calcular métricas do SRE selecionado
                metricas_sre = calcular_metricas_sre(df, sre_recom_selecionado)
                
                if metricas_sre:
                    # Exibir métricas do SRE
                    col_met1, col_met2, col_met3, col_met4 = st.columns(4)
                    
                    with col_met1:
                        st.metric("📊 Total Cards", metricas_sre['Total_Cards'])
                    
                    with col_met2:
                        st.metric("✅ Cards Sincronizados", metricas_sre['Cards_Sincronizados'])
                    
                    with col_met3:
                        st.metric("🔄 Taxa de Retorno", f"{metricas_sre['Taxa_Retorno']}%")
                    
                    with col_met4:
                        # Classificar score
                        score_class = ""
                        if metricas_sre['Score_Performance'] >= 80:
                            score_class = "🟢 Excelente"
                        elif metricas_sre['Score_Performance'] >= 65:
                            score_class = "🟡 Bom"
                        elif metricas_sre['Score_Performance'] >= 50:
                            score_class = "🟠 Regular"
                        else:
                            score_class = "🔴 Precisa Melhorar"
                        
                        st.metric("🏆 Score Performance", 
                                 f"{metricas_sre['Score_Performance']}",
                                 score_class)
                    
                    # Gerar recomendações
                    recomendacoes = gerar_recomendacoes_sre(metricas_sre)
                    
                    if recomendacoes:
                        st.markdown("### 🎯 Recomendações Específicas")
                        
                        for rec in recomendacoes:
                            if rec['Prioridade'] == 'ALTA':
                                cor_card = "warning-card"
                                emoji = "🔴"
                            elif rec['Prioridade'] == 'MÉDIA':
                                cor_card = "info-card"
                                emoji = "🟡"
                            else:
                                cor_card = "performance-card"
                                emoji = "🟢"
                            
                            st.markdown(f"""
                            <div class="{cor_card}" style="margin-bottom: 15px;">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span style="font-size: 1.5rem;">{emoji}</span>
                                    <div>
                                        <h4 style="margin: 0;">{rec['Recomendação']}</h4>
                                        <p style="margin: 5px 0 0 0; color: #6c757d;">
                                        <strong>Ação sugerida:</strong> {rec['Ação']}
                                        </p>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Plano de ação geral
                        st.markdown("### 📋 Plano de Ação Sugerido")
                        
                        acoes_gerais = [
                            "1. **Review periódico:** Realizar análise semanal das métricas",
                            "2. **Pair validation:** Sessões de validação em par com SREs de referência",
                            "3. **Checklist padronizado:** Implementar checklist de validação",
                            "4. **Feedback contínuo:** Reuniões de feedback com desenvolvedores",
                            "5. **Capacitação:** Treinamentos específicos baseados nas necessidades identificadas"
                        ]
                        
                        for acao in acoes_gerais:
                            st.markdown(f"""
                            <div style="padding: 10px; margin-bottom: 8px; background: #f8f9fa; border-radius: 5px;">
                                {acao}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Comparativo com média da equipe
                        st.markdown("### 📊 Comparativo com a Equipe")
                        
                        # Calcular médias da equipe
                        todos_sres = df['SRE'].dropna().unique()
                        metricas_equipe = []
                        
                        for sre in todos_sres:
                            met = calcular_metricas_sre(df, sre)
                            if met:
                                metricas_equipe.append(met)
                        
                        if metricas_equipe:
                            df_equipe = pd.DataFrame(metricas_equipe)
                            
                            # Comparar com médias
                            col_comp1, col_comp2, col_comp3 = st.columns(3)
                            
                            with col_comp1:
                                media_retorno = df_equipe['Taxa_Retorno'].mean()
                                diff_retorno = metricas_sre['Taxa_Retorno'] - media_retorno
                                st.metric("🔄 Taxa de Retorno vs Média", 
                                         f"{metricas_sre['Taxa_Retorno']}%",
                                         f"{diff_retorno:+.1f}%")
                            
                            with col_comp2:
                                media_eficiencia = df_equipe['Eficiencia_Cards_Mes'].mean()
                                diff_eficiencia = metricas_sre['Eficiencia_Cards_Mes'] - media_eficiencia
                                st.metric("⚡ Eficiência vs Média", 
                                         f"{metricas_sre['Eficiencia_Cards_Mes']:.1f}",
                                         f"{diff_eficiencia:+.1f}")
                            
                            with col_comp3:
                                media_score = df_equipe['Score_Performance'].mean()
                                diff_score = metricas_sre['Score_Performance'] - media_score
                                st.metric("🏆 Score vs Média", 
                                         f"{metricas_sre['Score_Performance']:.1f}",
                                         f"{diff_score:+.1f}")
                    else:
                        st.success("🎉 Este SRE está com excelente performance! Não há recomendações específicas no momento.")
                else:
                    st.info(f"Não há dados suficientes para gerar recomendações para o SRE {sre_recom_selecionado}")

else:
    # TELA INICIAL
    st.markdown("""
    <div style="text-align: center; padding: 4rem; background: #f8f9fa; border-radius: 10px; border: 2px dashed #dee2e6;">
        <h3 style="color: #495057;">📊 Esteira ADMS - Dashboard SRE</h3>
        <p style="color: #6c757d; margin-bottom: 2rem;">
            Sistema de análise de performance dos SREs - Análise Avançada
        </p>
        <div style="margin-top: 2rem; padding: 2rem; background: white; border-radius: 8px; display: inline-block;">
            <h4 style="color: #1e3799;">📋 Para começar:</h4>
            <p>1. <strong>Use a barra lateral esquerda</strong> para carregar os dados</p>
            <p>2. <strong>Acesse a aba "Performance dos SREs"</strong> para análises detalhadas</p>
            <p>3. <strong>Explore as 4 novas visualizações</strong> implementadas</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")
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
        Versão 6.0 | Análise Avançada de Performance SRE | Última atualização: {ultima_atualizacao} (Brasília)
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
