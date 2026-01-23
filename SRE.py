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
# CONFIGURAÇÕES DE SESSÃO
# ============================================
if 'show_upload_manager' not in st.session_state:
    st.session_state.show_upload_manager = False

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
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
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
    
    /* Upload Manager Styles */
    .upload-manager-header {
        background: linear-gradient(135deg, #1e3799 0%, #0c2461 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
    }
    
    .file-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e3799;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .file-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    .status-box {
        padding: 0.5rem;
        border-radius: 6px;
        font-size: 0.85rem;
        margin: 0.2rem 0;
    }
    
    .status-success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-info {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    
    .status-warning {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .drop-zone {
        border: 2px dashed #1e3799;
        border-radius: 10px;
        padding: 3rem;
        text-align: center;
        background: #f8f9fa;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .drop-zone:hover {
        background: #e9ecef;
        border-color: #0c2461;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES AUXILIARES PRINCIPAIS
# ============================================
def get_horario_brasilia():
    """Retorna o horário atual de Brasília"""
    try:
        tz = timezone('America/Sao_Paulo')
        return datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    except:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

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
    if isinstance(conteudo, bytes):
        return hashlib.md5(conteudo).hexdigest()
    else:
        return hashlib.md5(conteudo.encode('utf-8')).hexdigest()

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
    
    # Limpar cache
    st.cache_data.clear()

# ============================================
# DATA MANAGER (Funções de processamento otimizadas)
# ============================================
@st.cache_data(ttl=3600, show_spinner="Processando dados...")
def carregar_e_processar_dados(file_content, filename):
    """Função otimizada para carregar e processar dados"""
    try:
        # Detectar tipo de arquivo
        if filename.endswith('.csv'):
            # Tentar diferentes encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    if isinstance(file_content, bytes):
                        content_str = file_content.decode(encoding)
                    else:
                        content_str = file_content
                    break
                except:
                    continue
            else:
                if isinstance(file_content, bytes):
                    content_str = file_content.decode('utf-8-sig', errors='ignore')
                else:
                    content_str = file_content
            
            # Ler CSV
            df = pd.read_csv(io.StringIO(content_str), quotechar='"', on_bad_lines='skip')
            
        elif filename.endswith(('.xlsx', '.xls')):
            # Salvar temporariamente para ler com pandas
            temp_path = f"temp_{filename}"
            if isinstance(file_content, bytes):
                with open(temp_path, 'wb') as f:
                    f.write(file_content)
            else:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
            
            # Ler Excel
            df = pd.read_excel(temp_path, engine='openpyxl' if filename.endswith('.xlsx') else 'xlrd')
            
            # Remover arquivo temporário
            os.remove(temp_path)
        else:
            return None, f"Formato não suportado: {filename}"
        
        # Processamento básico
        df = processar_dataframe_basico(df)
        
        return df, "✅ Dados carregados com sucesso"
        
    except Exception as e:
        return None, f"❌ Erro: {str(e)}"

def processar_dataframe_basico(df):
    """Processamento básico do dataframe"""
    # Renomear colunas para padrão
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
        df['Nome_Mês'] = df['Criado'].dt.month.map({
            1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
            5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
            9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
        })
    
    # Converter revisões
    if 'Revisões' in df.columns:
        df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
    
    return df

def encontrar_arquivo_dados():
    """Tenta encontrar o arquivo de dados em vários caminhos possíveis"""
    caminhos = [
        "esteira_demandas.csv",
        "data/esteira_demandas.csv",
        "dados/esteira_demandas.csv",
        "base_dados.csv",
        "demandas.csv"
    ]
    
    for caminho in caminhos:
        if os.path.exists(caminho):
            return caminho
    
    return None

# ============================================
# UPLOAD MANAGER (Interface simplificada)
# ============================================
def show_upload_manager():
    """Mostra gerenciador completo de upload"""
    st.markdown("---")
    
    # Container principal
    with st.container():
        col_header, col_close = st.columns([4, 1])
        
        with col_header:
            st.markdown("### 📁 Gerenciador de Arquivos")
            st.caption("Carregue e gerencie múltiplas fontes de dados")
        
        with col_close:
            if st.button("✖️ Fechar", use_container_width=True, type="secondary"):
                if 'show_upload_manager' in st.session_state:
                    del st.session_state.show_upload_manager
                st.rerun()
    
    # Métodos de carregamento
    tab_local, tab_upload, tab_history = st.tabs([
        "📂 Local", 
        "⬆️ Upload", 
        "📊 Histórico"
    ])
    
    with tab_local:
        show_local_file_loader()
    
    with tab_upload:
        show_file_uploader()
    
    with tab_history:
        show_file_history()

def show_local_file_loader():
    """Carrega arquivos locais de forma otimizada"""
    st.markdown("#### 📂 Arquivos Locais")
    
    # Verificar quais arquivos existem
    existing_files = []
    caminhos = [
        "esteira_demandas.csv",
        "data/esteira_demandas.csv",
        "dados/demandas.csv",
        "base_dados.csv"
    ]
    
    for path in caminhos:
        if os.path.exists(path):
            stats = os.stat(path)
            file_info = {
                'filename': os.path.basename(path),
                'path': path,
                'size_kb': stats.st_size / 1024,
                'last_modified': datetime.fromtimestamp(stats.st_mtime),
                'created': datetime.fromtimestamp(stats.st_ctime)
            }
            existing_files.append(file_info)
    
    if existing_files:
        for info in existing_files:
            col_file, col_size, col_action = st.columns([3, 1, 1])
            
            with col_file:
                st.markdown(f"**{info['filename']}**")
                st.caption(f"Atualizado: {info['last_modified'].strftime('%d/%m/%Y %H:%M')}")
            
            with col_size:
                st.markdown(f"**{info['size_kb']:.1f} KB**")
            
            with col_action:
                if st.button("📥 Carregar", key=f"load_{info['path']}", use_container_width=True):
                    with st.spinner(f"Carregando {info['filename']}..."):
                        load_local_file(info['path'])
        
        st.markdown("---")
    
    # Upload manual de novo arquivo
    st.markdown("#### 📤 Enviar novo arquivo local")
    uploaded_file = st.file_uploader(
        "Selecione um arquivo CSV ou Excel",
        type=['csv', 'xlsx', 'xls'],
        key="local_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        col_info, col_action = st.columns([3, 1])
        
        with col_info:
            st.success(f"✅ Pronto: **{uploaded_file.name}**")
            st.caption(f"Tamanho: {uploaded_file.size / 1024:.1f} KB")
        
        with col_action:
            if st.button("✅ Processar", type="primary", use_container_width=True):
                with st.spinner("Processando arquivo..."):
                    process_uploaded_file(uploaded_file)

def show_file_uploader():
    """Interface principal de upload"""
    st.markdown("#### ⬆️ Upload Direto")
    
    # Área de upload
    uploaded_file = st.file_uploader(
        "Arraste e solte ou clique para selecionar",
        type=['csv', 'xlsx', 'xls'],
        key="main_uploader",
        help="Formatos suportados: CSV, Excel (.xlsx, .xls)",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # Preview rápido
        col_preview, col_info = st.columns([2, 1])
        
        with col_preview:
            st.success(f"✅ Arquivo pronto: **{uploaded_file.name}**")
            
            # Pré-visualização rápida
            try:
                if uploaded_file.name.endswith('.csv'):
                    preview_df = pd.read_csv(uploaded_file, nrows=5)
                else:
                    # Voltar ao início do arquivo
                    uploaded_file.seek(0)
                    preview_df = pd.read_excel(uploaded_file, nrows=5, engine='openpyxl')
                
                with st.expander("📋 Pré-visualização (5 primeiras linhas)"):
                    st.dataframe(preview_df, use_container_width=True)
                
                # Voltar ao início novamente para processamento
                uploaded_file.seek(0)
            except Exception as e:
                st.warning(f"Não foi possível mostrar pré-visualização: {str(e)}")
        
        with col_info:
            st.metric("Tamanho", f"{uploaded_file.size / 1024:.1f} KB")
            st.metric("Tipo", uploaded_file.type.split('/')[-1].upper())
        
        # Botão de processamento
        if st.button("🚀 Processar e Carregar Dados", 
                    type="primary",
                    use_container_width=True):
            with st.spinner("Processando dados..."):
                process_uploaded_file(uploaded_file)

def show_file_history():
    """Mostra histórico de arquivos carregados"""
    if 'loaded_files_history' not in st.session_state:
        st.session_state.loaded_files_history = []
    
    st.markdown("#### 📊 Histórico de Arquivos")
    
    if st.session_state.loaded_files_history:
        for i, file_info in enumerate(reversed(st.session_state.loaded_files_history[-5:])):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{file_info['name']}**")
                    st.caption(f"Carregado: {file_info['timestamp']}")
                
                with col2:
                    st.caption(f"Registros: {file_info['records']:,}")
                    st.caption(f"Hash: {file_info['hash'][:8]}...")
                
                with col3:
                    if st.button("↻", key=f"reload_{i}", 
                                help=f"Recarregar {file_info['name']}",
                                use_container_width=True):
                        # Para recarregar, você pode implementar a lógica aqui
                        st.info("Funcionalidade de recarregamento em desenvolvimento")
    else:
        st.info("Nenhum arquivo carregado recentemente.")

def load_local_file(filepath):
    """Carrega arquivo local"""
    try:
        with open(filepath, 'rb') as f:
            file_content = f.read()
            filename = os.path.basename(filepath)
            
            # Processar arquivo
            df, message = carregar_e_processar_dados(file_content, filename)
            
            if df is not None:
                # Calcular hash
                file_hash = calcular_hash_arquivo(file_content)
                
                # Atualizar session state
                st.session_state.df_original = df
                st.session_state.df_filtrado = df.copy()
                st.session_state.file_hash = file_hash
                st.session_state.uploaded_file_name = filename
                st.session_state.arquivo_atual = filepath
                st.session_state.ultima_atualizacao = get_horario_brasilia()
                
                # Adicionar ao histórico
                add_to_history(filename, len(df), file_hash)
                
                st.success(f"✅ {message} - {len(df):,} registros carregados")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {message}")
                
    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo: {str(e)}")

def process_uploaded_file(uploaded_file):
    """Processa arquivo enviado"""
    try:
        file_content = uploaded_file.getvalue()
        filename = uploaded_file.name
        
        # Verificar se é o mesmo arquivo
        current_hash = calcular_hash_arquivo(file_content)
        
        if ('file_hash' in st.session_state and 
            current_hash == st.session_state.file_hash):
            st.info("ℹ️ Este arquivo já está carregado.")
            return
        
        # Processar arquivo
        df, message = carregar_e_processar_dados(file_content, filename)
        
        if df is not None:
            # Atualizar session state
            st.session_state.df_original = df
            st.session_state.df_filtrado = df.copy()
            st.session_state.file_hash = current_hash
            st.session_state.uploaded_file_name = filename
            st.session_state.arquivo_atual = filename
            st.session_state.ultima_atualizacao = get_horario_brasilia()
            
            # Adicionar ao histórico
            add_to_history(filename, len(df), current_hash)
            
            st.success(f"✅ {message} - {len(df):,} registros carregados")
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"❌ {message}")
            
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {str(e)}")

def add_to_history(filename, records, file_hash):
    """Adiciona arquivo ao histórico"""
    if 'loaded_files_history' not in st.session_state:
        st.session_state.loaded_files_history = []
    
    history_entry = {
        'name': filename,
        'records': records,
        'hash': file_hash,
        'timestamp': get_horario_brasilia()
    }
    
    st.session_state.loaded_files_history.append(history_entry)
    
    # Manter apenas últimos 10 registros
    if len(st.session_state.loaded_files_history) > 10:
        st.session_state.loaded_files_history = st.session_state.loaded_files_history[-10:]

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
# SIDEBAR - REORGANIZADA E SIMPLIFICADA
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
    
    # CARREGAMENTO AUTOMÁTICO INICIAL (se não houver dados)
    if st.session_state.df_original is None:
        # Tentar carregar arquivo padrão
        caminho_padrao = encontrar_arquivo_dados()
        if caminho_padrao:
            with st.spinner('Carregando dados iniciais...'):
                try:
                    with open(caminho_padrao, 'rb') as f:
                        file_content = f.read()
                        filename = os.path.basename(caminho_padrao)
                    
                    df_local, message = carregar_e_processar_dados(file_content, filename)
                    
                    if df_local is not None:
                        # Calcular hash
                        file_hash = calcular_hash_arquivo(file_content)
                        
                        # Atualizar session state
                        st.session_state.df_original = df_local
                        st.session_state.df_filtrado = df_local.copy()
                        st.session_state.arquivo_atual = caminho_padrao
                        st.session_state.file_hash = file_hash
                        st.session_state.ultima_atualizacao = get_horario_brasilia()
                        
                        # Adicionar ao histórico
                        add_to_history(filename, len(df_local), file_hash)
                        
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao carregar arquivo inicial: {str(e)}")
    
    # SEÇÃO DE FILTROS (apenas se houver dados)
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
    
    # SEÇÃO DE GERENCIAMENTO DE DADOS (sempre visível)
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**📊 Gerenciar Dados**")
        
        # Status atual
        if st.session_state.df_original is not None:
            st.success("✅ Dados carregados")
            st.caption(f"Registros: {len(st.session_state.df_original):,}")
            
            if st.session_state.ultima_atualizacao:
                st.caption(f"Atualizado: {st.session_state.ultima_atualizacao}")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔄 Recarregar", 
                           use_container_width=True,
                           help="Recarrega os dados atuais"):
                    if st.session_state.arquivo_atual:
                        if os.path.exists(st.session_state.arquivo_atual):
                            with st.spinner("Recarregando dados..."):
                                load_local_file(st.session_state.arquivo_atual)
                        else:
                            st.error("Arquivo não encontrado!")
                    else:
                        st.warning("Nenhum arquivo para recarregar")
            
            with col_btn2:
                if st.button("🗑️ Limpar", 
                           use_container_width=True,
                           type="secondary",
                           help="Remove todos os dados"):
                    limpar_sessao_dados()
                    st.success("Dados limpos!")
                    time.sleep(1)
                    st.rerun()
        
        # Botão para abrir interface de upload completa
        if st.button("📁 Gerenciar Arquivos", 
                    use_container_width=True,
                    type="primary"):
            st.session_state.show_upload_manager = True
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# VERIFICAR SE PRECISA MOSTRAR UPLOAD MANAGER
# ============================================
if st.session_state.get('show_upload_manager', False):
    show_upload_manager()
    st.stop()

# ============================================
# CONTEÚDO PRINCIPAL
# ============================================

# HEADER ATUALIZADO
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
    # INFORMAÇÕES DA BASE DE DADOS
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
    # INDICADORES PRINCIPAIS SIMPLES
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
    # ABAS PRINCIPAIS
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
        # Cabeçalho com seletor de ano
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
        
        # FILTROS PARA ANÁLISE DE REVISÕES
        col_rev_filtro1, col_rev_filtro2 = st.columns(2)
        
        with col_rev_filtro1:
            # Filtrar por ano
            if 'Ano' in df.columns:
                anos_rev = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_rev = ['Todos os Anos'] + list(anos_rev)
                ano_rev = st.selectbox(
                    "📅 Filtrar por Ano:",
                    options=anos_opcoes_rev,
                    key="filtro_ano_revisoes"
                )
        
        with col_rev_filtro2:
            # Filtrar por mês
            if 'Mês' in df.columns:
                meses_rev = sorted(df['Mês'].dropna().unique().astype(int))
                meses_opcoes_rev = ['Todos os Meses'] + [str(m) for m in meses_rev]
                mes_rev = st.selectbox(
                    "📆 Filtrar por Mês:",
                    options=meses_opcoes_rev,
                    key="filtro_mes_revisoes"
                )
        
        # Aplicar filtros
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
                
                # Criar gráfico de barras
                fig_revisoes = go.Figure()
                
                # Criar escala de cores
                max_revisoes = revisoes_por_responsavel['Total_Revisões'].max()
                min_revisoes = revisoes_por_responsavel['Total_Revisões'].min()
                
                # Calcular cores baseadas no valor
                colors = []
                for valor in revisoes_por_responsavel['Total_Revisões']:
                    if max_revisoes == min_revisoes:
                        colors.append('#e74c3c')
                    else:
                        normalized = (valor - min_revisoes) / (max_revisoes - min_revisoes)
                        red = int(231 * normalized + 40 * (1 - normalized))
                        green = int(76 * normalized + 167 * (1 - normalized))
                        blue = int(60 * normalized + 69 * (1 - normalized))
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
                    title=titulo_rev,
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
        
        # FILTROS PARA SINCRONIZAÇÃO POR DIA
        col_sinc_filtro1, col_sinc_filtro2 = st.columns(2)
        
        with col_sinc_filtro1:
            # Filtrar por ano
            if 'Ano' in df.columns:
                anos_sinc = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_sinc = ['Todos os Anos'] + list(anos_sinc)
                ano_sinc = st.selectbox(
                    "📅 Filtrar por Ano:",
                    options=anos_opcoes_sinc,
                    key="filtro_ano_sinc"
                )
        
        with col_sinc_filtro2:
            # Filtrar por mês
            if 'Mês' in df.columns:
                meses_sinc = sorted(df['Mês'].dropna().unique().astype(int))
                meses_opcoes_sinc = ['Todos os Meses'] + [str(m) for m in meses_sinc]
                mes_sinc = st.selectbox(
                    "📆 Filtrar por Mês:",
                    options=meses_opcoes_sinc,
                    key="filtro_mes_sinc"
                )
        
        # Aplicar filtros
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
                titulo_sinc = 'Evolução Diária de Chamados Sincronizados'
                if ano_sinc != 'Todos os Anos':
                    titulo_sinc += f' - {ano_sinc}'
                if mes_sinc != 'Todos os Meses':
                    meses_nomes = {
                        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                    }
                    titulo_sinc += f' - {meses_nomes[int(mes_sinc)]}'
                
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
                    mode='lines',
                    name='Média Móvel (7 dias)',
                    line=dict(color='#dc3545', width=2, dash='dash')
                ))
                
                fig_dia.update_layout(
                    title=titulo_sinc,
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
            
            # Função para substituir e-mail pelo nome correto
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
            
            # Filtrar apenas chamados sincronizados para análise SRE
            df_sincronizados = df_sre[df_sre['Status'] == 'Sincronizado'].copy()
            
            if not df_sincronizados.empty and 'SRE' in df_sincronizados.columns:
                # SINCRONIZADOS POR SRE
                st.markdown("### 📈 Sincronizados por SRE")
                
                # Calcular sincronizados por SRE
                sinc_por_sre = df_sincronizados.groupby('SRE').size().reset_index()
                sinc_por_sre.columns = ['SRE', 'Sincronizados']
                sinc_por_sre = sinc_por_sre.sort_values('Sincronizados', ascending=False)
                
                # Aplicar a substituição de nomes
                sinc_por_sre['SRE_Nome'] = sinc_por_sre['SRE'].apply(substituir_nome_sre)
                
                # Agrupar por nome
                sinc_por_sre_nome = sinc_por_sre.groupby('SRE_Nome')['Sincronizados'].sum().reset_index()
                sinc_por_sre_nome = sinc_por_sre_nome.sort_values('Sincronizados', ascending=False)
                
                # Criar gráfico de barras
                fig_sinc_bar = go.Figure()
                
                # Cores do maior para o menor
                max_sinc = sinc_por_sre_nome['Sincronizados'].max()
                min_sinc = sinc_por_sre_nome['Sincronizados'].min()
                
                colors = []
                for valor in sinc_por_sre_nome['Sincronizados']:
                    if max_sinc == min_sinc:
                        colors.append('#1e3799')
                    else:
                        normalized = (valor - min_sinc) / (max_sinc - min_sinc)
                        red = int(30 * normalized + 74 * (1 - normalized))
                        green = int(55 * normalized + 105 * (1 - normalized))
                        blue = int(153 * normalized + 189 * (1 - normalized))
                        colors.append(f'rgb({red}, {green}, {blue})')
                
                fig_sinc_bar.add_trace(go.Bar(
                    x=sinc_por_sre_nome['SRE_Nome'].head(15),
                    y=sinc_por_sre_nome['Sincronizados'].head(15),
                    name='Sincronizados',
                    text=sinc_por_sre_nome['Sincronizados'].head(15),
                    textposition='outside',
                    marker_color=colors[:15],
                    marker_line_color='#0c2461',
                    marker_line_width=1.5,
                    opacity=0.8
                ))
                
                # Criar título dinâmico
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
                
                # Top 3 SREs
                col_top1, col_top2, col_top3 = st.columns(3)
                
                if len(sinc_por_sre_nome) >= 1:
                    with col_top1:
                        sre1 = sinc_por_sre_nome.iloc[0]
                        st.metric("🥇 1º Lugar Sincronizados", 
                                 f"{sre1['SRE_Nome']}", 
                                 f"{sre1['Sincronizados']} sinc.")
                
                if len(sinc_por_sre_nome) >= 2:
                    with col_top2:
                        sre2 = sinc_por_sre_nome.iloc[1]
                        st.metric("🥈 2º Lugar Sincronizados", 
                                 f"{sre2['SRE_Nome']}", 
                                 f"{sre2['Sincronizados']} sinc.")
                
                if len(sinc_por_sre_nome) >= 3:
                    with col_top3:
                        sre3 = sinc_por_sre_nome.iloc[2]
                        st.metric("🥉 3º Lugar Sincronizados", 
                                 f"{sre3['SRE_Nome']}", 
                                 f"{sre3['Sincronizados']} sinc.")
                
                # Tabela completa
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
                        
                        # Substituir e-mail pelo nome correto
                        nome_sre_display = substituir_nome_sre(sre)
                        
                        sres_metrics.append({
                            'SRE': nome_sre_display,
                            'Total_Cards': total_cards,
                            'Sincronizados': sincronizados,
                            'Cards_Retorno': cards_retorno
                        })
                
                if sres_metrics:
                    df_sres_metrics = pd.DataFrame(sres_metrics)
                    # Agrupar por nome
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
    
    # ============================================
    # ANÁLISES MELHORADAS
    # ============================================
    st.markdown("---")
    st.markdown('<div class="section-title-exec">🔍 ANÁLISES AVANÇADAS</div>', unsafe_allow_html=True)
    
    # Criar abas para as análises adicionais
    tab_extra1, tab_extra2, tab_extra3 = st.tabs([
        "🚀 Performance de Desenvolvedores",
        "📈 Análise de Sazonalidade", 
        "⚡ Diagnóstico de Erros"
    ])
    
    # ABA 1: PERFORMANCE DE DESENVOLVEDORES
    with tab_extra1:
        if 'Responsável_Formatado' in df.columns and 'Revisões' in df.columns and 'Status' in df.columns:
            # Filtros para performance
            col_filtro_perf1, col_filtro_perf2, col_filtro_perf3 = st.columns(3)
            
            with col_filtro_perf1:
                # Filtrar por ano
                if 'Ano' in df.columns:
                    anos_perf = sorted(df['Ano'].dropna().unique().astype(int))
                    anos_opcoes_perf = ['Todos os Anos'] + list(anos_perf)
                    ano_perf = st.selectbox(
                        "📅 Filtrar por Ano:",
                        options=anos_opcoes_perf,
                        key="filtro_ano_perf"
                    )
            
            with col_filtro_perf2:
                # Filtrar por mês
                if 'Mês' in df.columns:
                    meses_perf = sorted(df['Mês'].dropna().unique().astype(int))
                    meses_opcoes_perf = ['Todos os Meses'] + [str(m) for m in meses_perf]
                    mes_perf = st.selectbox(
                        "📆 Filtrar por Mês:",
                        options=meses_opcoes_perf,
                        key="filtro_mes_perf"
                    )
            
            with col_filtro_perf3:
                ordenar_por = st.selectbox(
                    "Ordenar por:",
                    options=["Score de Qualidade", "Total de Chamados", "Eficiência", "Produtividade"],
                    index=0
                )
            
            # Filtrar dados conforme período selecionado
            df_perf = df.copy()
            
            if ano_perf != 'Todos os Anos':
                df_perf = df_perf[df_perf['Ano'] == int(ano_perf)]
            
            if mes_perf != 'Todos os Meses':
                df_perf = df_perf[df_perf['Mês'] == int(mes_perf)]
            
            # Calcular métricas por desenvolvedor
            dev_metrics = []
            devs = df_perf['Responsável_Formatado'].unique()
            
            for dev in devs:
                dev_data = df_perf[df_perf['Responsável_Formatado'] == dev]
                total_chamados = len(dev_data)
                
                if total_chamados > 0:
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
                
                # MATRIZ DE PERFORMANCE PARA DEVS
                st.markdown("### 🎯 Matriz de Performance - Desenvolvedores")
                
                # Criar matriz de performance
                matriz_df = criar_matriz_performance_dev(df_perf)
                
                if not matriz_df.empty:
                    # Calcular médias para quadrantes
                    media_eficiencia = matriz_df['Eficiencia'].mean()
                    media_qualidade = matriz_df['Qualidade'].mean()
                    
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
                    
                    matriz_df['Quadrante'] = matriz_df.apply(classificar_quadrante, axis=1)
                    
                    # Gráfico de dispersão
                    fig_matriz = px.scatter(
                        matriz_df,
                        x='Eficiencia',
                        y='Qualidade',
                        size='Score',
                        color='Quadrante',
                        hover_name='Desenvolvedor',
                        title='Matriz de Performance: Eficiência vs Qualidade',
                        labels={
                            'Eficiencia': 'Eficiência (Cards/Mês)',
                            'Qualidade': 'Qualidade (% Aprovação sem Revisão)',
                            'Score': 'Score Performance'
                        },
                        size_max=30
                    )
                    
                    # Adicionar linhas de média
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
                    
                    fig_matriz.update_layout(
                        height=500,
                        xaxis_title="Eficiência (Cards por Mês)",
                        yaxis_title="Qualidade (% de Aprovação sem Revisão)",
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_matriz, use_container_width=True)
                    
                    # Tabela de classificação
                    st.markdown("#### 📋 Classificação por Quadrante")
                    
                    quadrantes_count = matriz_df['Quadrante'].value_counts()
                    
                    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
                    
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
                
                # Mostrar top 10
                st.markdown(f"### 🏆 Top 10 Desenvolvedores ({ordenar_por})")
                
                # Gráfico de barras horizontais para Score de Qualidade
                if ordenar_por == "Score de Qualidade":
                    top10_score = df_dev_metrics.head(10)
                    
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
                
                # Tabela completa
                st.markdown("### 📋 Performance Detalhada")
                st.dataframe(
                    df_dev_metrics,
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
    
    # ABA 2: ANÁLISE DE SAZONALIDADE
    with tab_extra2:
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
    
    # ABA 3: DIAGNÓSTICO DE ERROS
    with tab_extra3:
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
    # ÚLTIMAS DEMANDAS REGISTRADAS
    # ============================================
    st.markdown("---")
    st.markdown('<div class="section-title_exec">🕒 ÚLTIMAS DEMANDAS REGISTRADAS</div>', unsafe_allow_html=True)
    
    if 'Criado' in df.columns:
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
            # Colunas a mostrar
            mostrar_colunas = st.multiselect(
                "Colunas a mostrar:",
                options=['Chamado', 'Tipo_Chamado', 'Responsável', 'Status', 'Prioridade', 
                        'Revisões', 'Empresa', 'SRE', 'Data', 'Responsável_Formatado'],
                default=['Chamado', 'Tipo_Chamado', 'Responsável_Formatado', 'Status', 'Data'],
                key="select_colunas"
            )
        
        with col_filtro4:
            # Filtro de busca por chamado
            filtro_chamado_tabela = st.text_input(
                "Filtro adicional:",
                placeholder="Ex: 12345",
                key="input_filtro_chamado"
            )
        
        # Aplicar ordenação
        ultimas_demandas = df.copy()
        
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
    # ============================================
    # TELA INICIAL MELHORADA
    # ============================================
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("""
        <div style="padding: 2rem; background: #f8f9fa; border-radius: 10px;">
            <h2 style="color: #1e3799;">📊 Bem-vindo ao Esteira ADMS</h2>
            <p style="color: #495057; margin-bottom: 1.5rem;">
            Sistema avançado de análise e monitoramento de chamados
            </p>
            
            <div style="background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
                <h4 style="color: #28a745;">🚀 Para começar:</h4>
                <ol style="color: #6c757d;">
                    <li style="margin-bottom: 0.5rem;">Use a barra lateral para <strong>gerenciar arquivos</strong></li>
                    <li style="margin-bottom: 0.5rem;">Faça upload de um arquivo CSV ou Excel</li>
                    <li style="margin-bottom: 0.5rem;">Explore as análises disponíveis</li>
                </ol>
            </div>
            
            <div style="background: #e8f4fd; padding: 1rem; border-radius: 8px;">
                <h5 style="color: #1e3799;">📋 Formatos suportados:</h5>
                <ul style="color: #495057;">
                    <li>CSV (com colunas padrão)</li>
                    <li>Excel (.xlsx, .xls)</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📈</div>
            <h4 style="color: #495057;">Estatísticas do Sistema</h4>
            
            <div style="background: white; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <p style="color: #6c757d; margin: 0;">
                <strong>Versão:</strong> 5.5<br>
                <strong>Atualização:</strong> {get_horario_brasilia()}<br>
                <strong>Status:</strong> Pronto para uso
                </p>
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
