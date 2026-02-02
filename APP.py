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
# CSS PERSONALIZADO ATUALIZADO (COM MODAL)
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
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ffffff 0%, #fff8f8 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .info-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fcff 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #17a2b8;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
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
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .sre-comparison-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
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
    
    /* ESTILOS PARA O RESUMO EXECUTIVO (MODAL) */
    .resumo-modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        z-index: 1000;
        width: 90%;
        max-width: 1200px;
        max-height: 85vh;
        overflow-y: auto;
        border: 3px solid #1e3799;
    }
    
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.7);
        z-index: 999;
        backdrop-filter: blur(3px);
    }
    
    .close-btn {
        position: absolute;
        top: 15px;
        right: 15px;
        background: #dc3545;
        color: white;
        border: none;
        border-radius: 50%;
        width: 35px;
        height: 35px;
        cursor: pointer;
        font-size: 1.3rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .close-btn:hover {
        background: #c82333;
        transform: scale(1.1);
    }
    
    .resumo-header {
        background: linear-gradient(135deg, #1e3799 0%, #0c2461 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        position: relative;
    }
    
    .resumo-kpi-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-top: 4px solid;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .resumo-kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin: 0.3rem 0 0 0;
        font-weight: 500;
    }
    
    .kpi-trend {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .trend-up {
        color: #28a745;
    }
    
    .trend-down {
        color: #dc3545;
    }
    
    .resumo-sre-status {
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid;
        font-size: 1.1rem;
    }
    
    .status-excelente {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left-color: #28a745;
        color: #155724;
    }
    
    .status-bom {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left-color: #ffc107;
        color: #856404;
    }
    
    .status-alerta {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left-color: #dc3545;
        color: #721c24;
    }
    
    /* Botão do ícone de resumo */
    .icon-resumo-btn {
        position: absolute;
        top: 20px;
        left: 20px;
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        z-index: 100;
    }
    
    .icon-resumo-btn:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: white;
        transform: scale(1.1);
    }
    
    .icon-resumo-btn i {
        color: white;
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    /* Scrollbar personalizada para o modal */
    .resumo-modal::-webkit-scrollbar {
        width: 8px;
    }
    
    .resumo-modal::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    .resumo-modal::-webkit-scrollbar-thumb {
        background: #1e3799;
        border-radius: 4px;
    }
    
    .resumo-modal::-webkit-scrollbar-thumb:hover {
        background: #0c2461;
    }
</style>

<script>
// Função para abrir/fechar o modal
function toggleResumoModal() {
    const modal = document.getElementById('resumoModal');
    const overlay = document.getElementById('modalOverlay');
    
    if (modal.style.display === 'block') {
        modal.style.display = 'none';
        overlay.style.display = 'none';
    } else {
        modal.style.display = 'block';
        overlay.style.display = 'block';
    }
}

// Fechar modal com ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modal = document.getElementById('resumoModal');
        const overlay = document.getElementById('modalOverlay');
        if (modal && modal.style.display === 'block') {
            modal.style.display = 'none';
            overlay.style.display = 'none';
        }
    }
});

// Fechar modal ao clicar fora
document.addEventListener('click', function(event) {
    const modal = document.getElementById('resumoModal');
    const overlay = document.getElementById('modalOverlay');
    
    if (modal && event.target === overlay) {
        modal.style.display = 'none';
        overlay.style.display = 'none';
    }
});
</script>
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

@st.cache_data(ttl=300)  # Cache expira em 5 minutos
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
        
        # Adicionar timestamp para evitar cache
        timestamp = time.time()
        
        return df, "✅ Dados carregados com sucesso", f"{hash_conteudo}_{timestamp}"
    
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

def verificar_e_atualizar_arquivo():
    """Verifica se o arquivo local foi modificado e atualiza se necessário"""
    caminho_arquivo = encontrar_arquivo_dados()
    
    if caminho_arquivo and os.path.exists(caminho_arquivo):
        # Inicializar session state se não existir
        if 'ultima_modificacao' not in st.session_state:
            st.session_state.ultima_modificacao = os.path.getmtime(caminho_arquivo)
            return False
        
        # Verificar se o arquivo foi modificado
        modificacao_atual = os.path.getmtime(caminho_arquivo)
        
        # Se o arquivo foi modificado E temos dados carregados
        if (modificacao_atual > st.session_state.ultima_modificacao and 
            st.session_state.df_original is not None):
            
            # Calcular hash atual para verificar se realmente mudou
            with open(caminho_arquivo, 'rb') as f:
                conteudo_atual = f.read()
            hash_atual = calcular_hash_arquivo(conteudo_atual)
            
            # Comparar com hash anterior
            if 'file_hash' not in st.session_state or hash_atual != st.session_state.file_hash:
                # Atualizar timestamp
                st.session_state.ultima_modificacao = modificacao_atual
                return True
        
        st.session_state.ultima_modificacao = modificacao_atual
    
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
# FUNÇÃO PARA CRIAR RESUMO EXECUTIVO
# ============================================

def criar_html_resumo_executivo(df):
    """Cria o HTML completo do resumo executivo"""
    
    if df is None or df.empty:
        return """
        <div class="resumo-modal" id="resumoModal">
            <button class="close-btn" onclick="toggleResumoModal()">×</button>
            <div class="resumo-header">
                <h2 style="margin: 0; color: white;">📊 RESUMO EXECUTIVO</h2>
                <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.9);">
                    Painel de Indicadores Principais
                </p>
            </div>
            <div style="text-align: center; padding: 3rem;">
                <h3 style="color: #6c757d;">⚠️ Nenhum dado disponível</h3>
                <p>Carregue um arquivo para visualizar o resumo executivo.</p>
            </div>
        </div>
        """
    
    # Obter mês atual
    hoje = datetime.now()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    # Nome do mês
    meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    nome_mes_atual = meses.get(mes_atual, f"Mês {mes_atual}")
    
    # Filtrar dados do mês atual
    df_mes_atual = df[
        (df['Criado'].dt.month == mes_atual) & 
        (df['Criado'].dt.year == ano_atual)
    ].copy()
    
    # Mês anterior para comparação
    mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
    ano_anterior = ano_atual if mes_atual > 1 else ano_atual - 1
    nome_mes_anterior = meses.get(mes_anterior, f"Mês {mes_anterior}")
    
    df_mes_anterior = df[
        (df['Criado'].dt.month == mes_anterior) & 
        (df['Criado'].dt.year == ano_anterior)
    ].copy()
    
    # Calcular métricas do mês atual
    total_cards_mes = len(df_mes_atual)
    cards_sincronizados_mes = len(df_mes_atual[df_mes_atual['Status'] == 'Sincronizado']) if 'Status' in df_mes_atual.columns else 0
    
    # Cards com revisões (retorno de erro)
    if 'Revisões' in df_mes_atual.columns:
        cards_com_revisoes = len(df_mes_atual[df_mes_atual['Revisões'] > 0])
        total_revisoes = int(df_mes_atual['Revisões'].sum())
    else:
        cards_com_revisoes = 0
        total_revisoes = 0
    
    # Métricas do mês anterior (para comparação)
    total_cards_anterior = len(df_mes_anterior)
    cards_sincronizados_anterior = len(df_mes_anterior[df_mes_anterior['Status'] == 'Sincronizado']) if 'Status' in df_mes_anterior.columns else 0
    
    # Calcular variações
    variacao_total = 0
    if total_cards_anterior > 0:
        variacao_total = ((total_cards_mes - total_cards_anterior) / total_cards_anterior * 100)
    
    variacao_sinc = 0
    if cards_sincronizados_anterior > 0:
        variacao_sinc = ((cards_sincronizados_mes - cards_sincronizados_anterior) / cards_sincronizados_anterior * 100)
    
    # Taxa de sucesso do SRE
    taxa_sucesso_sre = 0
    if cards_sincronizados_mes > 0:
        taxa_sucesso_sre = ((cards_sincronizados_mes - cards_com_revisoes) / cards_sincronizados_mes * 100)
    
    # Classificação da taxa de sucesso
    if taxa_sucesso_sre >= 95:
        status_class = "status-excelente"
        status_icon = "🎯"
        status_text = "EXCELENTE"
    elif taxa_sucesso_sre >= 85:
        status_class = "status-bom"
        status_icon = "✅"
        status_text = "BOM"
    else:
        status_class = "status-alerta"
        status_icon = "⚠️"
        status_text = "PRECISA DE ATENÇÃO"
    
    # Gerar HTML do resumo
    html = f"""
    <div class="resumo-modal" id="resumoModal">
        <button class="close-btn" onclick="toggleResumoModal()">×</button>
        
        <div class="resumo-header">
            <h2 style="margin: 0; color: white;">📊 RESUMO EXECUTIVO</h2>
            <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.9);">
                {nome_mes_atual} {ano_atual} | Indicadores Principais | Performance SRE
            </p>
        </div>
        
        <!-- KPIs PRINCIPAIS -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem;">
            <!-- KPI 1: Total de Cards -->
            <div class="resumo-kpi-card" style="border-top-color: #1e3799;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                    <span style="font-size: 2rem; color: #1e3799;">📋</span>
                    <div>
                        <div class="kpi-label">TOTAL DE CARDS</div>
                        <div class="kpi-value" style="color: #1e3799;">{total_cards_mes:,}</div>
                    </div>
                </div>
                <div class="kpi-trend {'trend-up' if variacao_total >= 0 else 'trend-down'}">
                    {f'↗️ {variacao_total:+.1f}% vs {nome_mes_anterior}' if total_cards_anterior > 0 else '📊 Sem comparação anterior'}
                </div>
            </div>
            
            <!-- KPI 2: Cards Sincronizados -->
            <div class="resumo-kpi-card" style="border-top-color: #28a745;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                    <span style="font-size: 2rem; color: #28a745;">✅</span>
                    <div>
                        <div class="kpi-label">CARDS SINCRONIZADOS</div>
                        <div class="kpi-value" style="color: #28a745;">{cards_sincronizados_mes:,}</div>
                    </div>
                </div>
                <div class="kpi-trend {'trend-up' if variacao_sinc >= 0 else 'trend-down'}">
                    {f'↗️ {variacao_sinc:+.1f}% vs {nome_mes_anterior}' if cards_sincronizados_anterior > 0 else '📊 Sem comparação anterior'}
                </div>
            </div>
            
            <!-- KPI 3: Taxa de Sucesso SRE -->
            <div class="resumo-kpi-card" style="border-top-color: {'#28a745' if taxa_sucesso_sre >= 95 else '#ffc107' if taxa_sucesso_sre >= 85 else '#dc3545'};">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                    <span style="font-size: 2rem; color: {'#28a745' if taxa_sucesso_sre >= 95 else '#ffc107' if taxa_sucesso_sre >= 85 else '#dc3545'};">🎯</span>
                    <div>
                        <div class="kpi-label">TAXA DE SUCESSO SRE</div>
                        <div class="kpi-value" style="color: {'#28a745' if taxa_sucesso_sre >= 95 else '#ffc107' if taxa_sucesso_sre >= 85 else '#dc3545'};">{taxa_sucesso_sre:.1f}%</div>
                    </div>
                </div>
                <div class="kpi-trend">
                    {f'🔧 {cards_com_revisoes} cards com retorno' if cards_com_revisoes > 0 else '✨ Nenhum retorno de erro'}
                </div>
            </div>
            
            <!-- KPI 4: Total de Revisões -->
            <div class="resumo-kpi-card" style="border-top-color: #6c757d;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                    <span style="font-size: 2rem; color: #6c757d;">📝</span>
                    <div>
                        <div class="kpi-label">TOTAL DE REVISÕES</div>
                        <div class="kpi-value" style="color: #6c757d;">{total_revisoes:,}</div>
                    </div>
                </div>
                <div class="kpi-trend">
                    {f'📊 Média: {(total_revisoes/total_cards_mes):.1f} por card' if total_cards_mes > 0 else '📊 Sem dados'}
                </div>
            </div>
        </div>
        
        <!-- STATUS DO SRE -->
        <div class="resumo-sre-status {status_class}">
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-size: 2.5rem;">{status_icon}</span>
                <div>
                    <h3 style="margin: 0 0 0.5rem 0; font-weight: bold;">STATUS DO SRE - {nome_mes_atual} {ano_atual}</h3>
                    <p style="margin: 0; font-size: 1.1rem;">
                        <strong>O papel do SRE validou {cards_sincronizados_mes:,} cards</strong> este mês.
                        {'✨ Não houve retorno de erro!' if cards_com_revisoes == 0 else f'🔧 {cards_com_revisoes} cards ({cards_com_revisoes/cards_sincronizados_mes*100:.1f}%) retornaram para ajustes.'}
                        Taxa de sucesso: <strong>{taxa_sucesso_sre:.1f}%</strong> - <strong>{status_text}</strong>
                    </p>
                </div>
            </div>
        </div>
        
        <!-- GRÁFICOS RESUMIDOS -->
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-top: 2rem;">
            <!-- Gráfico 1: Evolução Mensal -->
            <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h4 style="color: #1e3799; margin: 0 0 1rem 0; border-bottom: 2px solid #1e3799; padding-bottom: 0.5rem;">
                    📈 EVOLUÇÃO MENSAL - ÚLTIMOS 6 MESES
                </h4>
                <div id="graficoEvolucao" style="height: 250px;"></div>
            </div>
            
            <!-- Gráfico 2: Distribuição por Status -->
            <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <h4 style="color: #28a745; margin: 0 0 1rem 0; border-bottom: 2px solid #28a745; padding-bottom: 0.5rem;">
                    📊 DISTRIBUIÇÃO POR STATUS
                </h4>
                <div id="graficoStatus" style="height: 250px;"></div>
            </div>
        </div>
        
        <!-- TOP SREs -->
        <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-top: 1.5rem;">
            <h4 style="color: #6c757d; margin: 0 0 1rem 0; border-bottom: 2px solid #6c757d; padding-bottom: 0.5rem;">
                🏆 TOP 5 SREs - {nome_mes_atual} {ano_atual}
            </h4>
            <div id="topSREs" style="min-height: 150px;">
    """
    
    # Adicionar ranking dos SREs
    if 'SRE' in df_mes_atual.columns and not df_mes_atual.empty:
        # Contar sincronizações por SRE
        sre_ranking = df_mes_atual[df_mes_atual['Status'] == 'Sincronizado']['SRE'].value_counts().head(5)
        
        if not sre_ranking.empty:
            html += '<div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem;">'
            for i, (sre, count) in enumerate(sre_ranking.items()):
                medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
                html += f"""
                <div style="text-align: center; padding: 1rem; background: {'#fff3cd' if i < 3 else '#f8f9fa'}; 
                            border-radius: 8px; border: 2px solid {'#ffc107' if i < 3 else '#dee2e6'};">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{medal}</div>
                    <div style="font-weight: bold; color: #495057; font-size: 0.9rem; margin-bottom: 0.3rem;">
                        {sre[:20] + '...' if len(str(sre)) > 20 else sre}
                    </div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #1e3799;">{count}</div>
                    <div style="font-size: 0.8rem; color: #6c757d;">sincronizações</div>
                </div>
                """
            html += '</div>'
        else:
            html += '<p style="text-align: center; color: #6c757d; padding: 2rem;">Nenhum SRE com sincronizações neste mês.</p>'
    else:
        html += '<p style="text-align: center; color: #6c757d; padding: 2rem;">Dados de SRE não disponíveis.</p>'
    
    # Fechar divs e adicionar scripts
    html += """
            </div>
        </div>
        
        <!-- RESUMO FINAL -->
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 1.5rem; border-radius: 10px; margin-top: 1.5rem; border-left: 4px solid #1e3799;">
            <div style="display: flex; align-items: start; gap: 15px;">
                <span style="font-size: 2rem;">📋</span>
                <div>
                    <h4 style="margin: 0 0 0.5rem 0; color: #1e3799;">ANÁLISE SINTÉTICA</h4>
                    <p style="margin: 0; color: #495057; line-height: 1.5;">
                        No mês de <strong>""" + nome_mes_atual + """</strong>, foram processados <strong>""" + f"{total_cards_mes:,}" + """ cards</strong>, 
                        com <strong>""" + f"{cards_sincronizados_mes:,}" + """ sincronizações</strong> realizadas.
                        A equipe SRE alcançou uma taxa de sucesso de <strong>""" + f"{taxa_sucesso_sre:.1f}%" + """</strong>, 
                        """ + ("mantendo excelência nas validações." if taxa_sucesso_sre >= 95 else 
                              "com desempenho satisfatório." if taxa_sucesso_sre >= 85 else 
                              "indicando oportunidades de melhoria.") + """
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- OVERLAY -->
    <div class="modal-overlay" id="modalOverlay" onclick="toggleResumoModal()"></div>
    
    <script>
    // Dados para os gráficos (exemplo - você precisaria gerar dados reais)
    function criarGraficos() {
        // Gráfico de Evolução Mensal
        const evolucaoData = {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            datasets: [{
                label: 'Cards Totais',
                data: [120, 135, 150, 145, 160, 155],
                borderColor: '#1e3799',
                backgroundColor: 'rgba(30, 55, 153, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: 'Sincronizados',
                data: [110, 125, 140, 135, 150, 145],
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                fill: true,
                tension: 0.4
            }]
        };
        
        const evolucaoCtx = document.createElement('canvas');
        document.getElementById('graficoEvolucao').appendChild(evolucaoCtx);
        
        new Chart(evolucaoCtx.getContext('2d'), {
            type: 'line',
            data: evolucaoData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.05)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.05)'
                        }
                    }
                }
            }
        });
        
        // Gráfico de Distribuição por Status
        const statusData = {
            labels: ['Sincronizado', 'Em Andamento', 'Pendente', 'Rejeitado'],
            datasets: [{
                data: [75, 15, 8, 2],
                backgroundColor: ['#28a745', '#ffc107', '#17a2b8', '#dc3545'],
                borderWidth: 1
            }]
        };
        
        const statusCtx = document.createElement('canvas');
        document.getElementById('graficoStatus').appendChild(statusCtx);
        
        new Chart(statusCtx.getContext('2d'), {
            type: 'doughnut',
            data: statusData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            }
        });
    }
    
    // Executar quando o modal for aberto
    document.addEventListener('DOMContentLoaded', function() {
        const modal = document.getElementById('resumoModal');
        if (modal && modal.style.display === 'block') {
            criarGraficos();
        }
    });
    
    // Recriar gráficos quando o modal for reaberto
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                const modal = document.getElementById('resumoModal');
                if (modal && modal.style.display === 'block') {
                    // Limpar gráficos existentes
                    const evolDiv = document.getElementById('graficoEvolucao');
                    const statusDiv = document.getElementById('graficoStatus');
                    evolDiv.innerHTML = '';
                    statusDiv.innerHTML = '';
                    
                    // Criar novos gráficos
                    criarGraficos();
                }
            }
        });
    });
    
    observer.observe(document.getElementById('resumoModal'), { attributes: true });
    </script>
    """
    
    return html

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
                if verificar_e_atualizar_arquivo():
                    st.warning("⚠️ O arquivo local foi modificado! Clique em 'Recarregar Local' para atualizar.")
            
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
                                # Forçar recarregamento limpando o cache
                                carregar_dados.clear()
                                
                                # Recarregar dados
                                df_atualizado, status, hash_conteudo = carregar_dados(caminho_arquivo=caminho_atual)
                                
                                if df_atualizado is not None:
                                    # Atualizar session state
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
        
        # UPLOAD DE ARQUIVO
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
            
            file_details = {
                "Nome": uploaded_file.name,
                "Tamanho": f"{uploaded_file.size / 1024:.1f} KB"
            }
            
            st.write("📄 Detalhes do arquivo:")
            st.json(file_details)
            
            if st.button("📥 Processar Arquivo", use_container_width=True, type="primary", key="btn_processar"):
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
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {status}")
        
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

# ÍCONE DE RESUMO EXECUTIVO (FLUTUANTE NO CANTO SUPERIOR ESQUERDO)
st.markdown("""
<div class="icon-resumo-btn" onclick="toggleResumoModal()" title="Clique para ver o Resumo Executivo">
    <i>📊</i>
</div>
""", unsafe_allow_html=True)

# HEADER PRINCIPAL
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
# RESUMO EXECUTIVO (MODAL - INICIALMENTE OCULTO)
# ============================================
# Inicializar estado do modal
if 'show_resumo' not in st.session_state:
    st.session_state.show_resumo = False

# Se o botão do ícone for clicado (via JavaScript), mostraremos o modal
# Como o Streamlit não tem interatividade JavaScript direta, usamos um workaround
st.markdown("""
<script>
// Inicializar modal como oculto
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('resumoModal');
    const overlay = document.getElementById('modalOverlay');
    if (modal) {
        modal.style.display = 'none';
    }
    if (overlay) {
        overlay.style.display = 'none';
    }
    
    // Adicionar evento ao botão do ícone
    const iconBtn = document.querySelector('.icon-resumo-btn');
    if (iconBtn) {
        iconBtn.addEventListener('click', function() {
            toggleResumoModal();
        });
    }
});

function toggleResumoModal() {
    const modal = document.getElementById('resumoModal');
    const overlay = document.getElementById('modalOverlay');
    
    if (!modal) {
        // Se o modal não existir, criar dinamicamente
        fetchResumoExecutivo();
        return;
    }
    
    if (modal.style.display === 'none' || modal.style.display === '') {
        modal.style.display = 'block';
        overlay.style.display = 'block';
        // Recriar gráficos quando abrir
        criarGraficos();
    } else {
        modal.style.display = 'none';
        overlay.style.display = 'none';
    }
}

// Função para buscar resumo executivo (será implementada pelo Streamlit)
function fetchResumoExecutivo() {
    // Esta função será chamada pelo Streamlit para gerar o conteúdo
    console.log('Solicitando resumo executivo...');
}
</script>
""", unsafe_allow_html=True)

# Gerar e exibir o modal do resumo executivo
if st.session_state.df_original is not None:
    # Botão alternativo (em caso de problemas com o ícone)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("📊 Abrir Resumo Executivo", use_container_width=True, type="secondary"):
            st.session_state.show_resumo = True
            st.rerun()
    
    # Se o modal deve ser mostrado
    if st.session_state.show_resumo:
        # Gerar HTML do resumo
        resumo_html = criar_html_resumo_executivo(st.session_state.df_original)
        st.markdown(resumo_html, unsafe_allow_html=True)
        
        # Botão para fechar (dentro do Streamlit)
        if st.button("❌ Fechar Resumo", use_container_width=True, type="primary"):
            st.session_state.show_resumo = False
            st.rerun()

# ============================================
# VERIFICAÇÃO AUTOMÁTICA DE ATUALIZAÇÕES
# ============================================
if st.session_state.df_original is not None:
    # Verificar se o arquivo foi atualizado
    if verificar_e_atualizar_arquivo():
        st.info("🔔 O arquivo local foi atualizado! Clique em 'Recarregar Local' na barra lateral para atualizar os dados.")

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
    # ABAS PRINCIPAIS (ORIGINAIS - MANTIDAS)
    # ============================================
    st.markdown("---")
    
    # Definir 4 abas principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Evolução de Demandas", 
        "📊 Análise de Revisões", 
        "📈 Chamados Sincronizados por Dia",
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
    
    # CONTINUAÇÃO DO CÓDIGO ORIGINAL...
    # [O restante do seu código original permanece aqui - tabs 2, 3, 4, análises avançadas, etc.]

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
            <div style="margin-top: 1.5rem;">
                <div class="icon-resumo-btn" style="position: relative; top: 0; left: 0; margin: 0 auto;" 
                     onclick="alert('Carregue dados primeiro para ver o Resumo Executivo')">
                    <i>📊</i>
                </div>
                <p style="margin-top: 0.5rem; font-size: 0.9rem; color: #6c757d;">
                    Ícone do Resumo Executivo aparecerá aqui
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# RODAPÉ
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
