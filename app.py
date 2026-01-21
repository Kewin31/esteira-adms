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

# HEADER
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
            Última atualização: {}
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 0.2rem 0 0 0; font-size: 0.85rem;">
            v5.4 | Sistema de Performance SRE
            </p>
        </div>
    </div>
</div>
""".format(datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)

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
    # ABAS PARA DIFERENTES VISUALIZAÇÕES (APENAS 3)
    # ============================================
    st.markdown("---")
    
    # Definir apenas 3 abas
    tab1, tab2, tab3 = st.tabs([
        "📅 Evolução de Demandas", 
        "📊 Análise de Revisões", 
        "🏆 Performance dos SREs"  # Terceira aba agora é Performance dos SREs
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
        
        if 'Revisões' in df.columns and 'Responsável_Formatado' in df.columns:
            # Filtrar apenas responsáveis com revisões
            df_com_revisoes = df[df['Revisões'] > 0].copy()
            
            if not df_com_revisoes.empty:
                # Agrupar por responsável
                revisoes_por_responsavel = df_com_revisoes.groupby('Responsável_Formatado').agg({
                    'Revisões': 'sum',
                    'Chamado': 'count'
                }).reset_index()
                
                revisoes_por_responsavel.columns = ['Responsável', 'Total_Revisões', 'Chamados_Com_Revisão']
                revisoes_por_responsavel = revisoes_por_responsavel.sort_values('Total_Revisões', ascending=False)
                
                # Criar gráfico de barras
                fig_revisoes = go.Figure()
                
                fig_revisoes.add_trace(go.Bar(
                    x=revisoes_por_responsavel['Responsável'].head(15),
                    y=revisoes_por_responsavel['Total_Revisões'].head(15),
                    name='Total de Revisões',
                    text=revisoes_por_responsavel['Total_Revisões'].head(15),
                    textposition='outside',
                    marker_color='#e74c3c',
                    marker_line_color='#c0392b',
                    marker_line_width=1.5,
                    opacity=0.8
                ))
                
                fig_revisoes.update_layout(
                    title='Top 15 Responsáveis com Mais Revisões',
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
    
    # ABA 3: PERFORMANCE DOS SREs
    with tab3:
        st.markdown('<div class="section-title-exec">🏆 PERFORMANCE DOS SREs</div>', unsafe_allow_html=True)
        
        if 'SRE' in df.columns and 'Status' in df.columns:
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
                # 1. Ranking dos SREs que mais sincronizaram
                st.markdown("### 🥇 Ranking de Sincronizações por SRE")
                
                sincronizacoes_por_sre = df_sincronizados['SRE'].value_counts().reset_index()
                sincronizacoes_por_sre.columns = ['SRE', 'Sincronizações']
                sincronizacoes_por_sre = sincronizacoes_por_sre.sort_values('Sincronizações', ascending=False)
                
                # Criar título dinâmico
                titulo_sinc = "Top 10 SREs com Mais Sincronizações"
                if ano_sre != 'Todos':
                    titulo_sinc += f" - {ano_sre}"
                if mes_sre != 'Todos':
                    titulo_sinc += f"/{mes_sre}"
                
                # Criar gráfico de barras
                fig_sinc_sre = px.bar(
                    sincronizacoes_por_sre.head(10),
                    x='SRE',
                    y='Sincronizações',
                    title=titulo_sinc,
                    text='Sincronizações',
                    color='Sincronizações',
                    color_continuous_scale='Greens'
                )
                
                fig_sinc_sre.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    marker_line_color='#218838',
                    marker_line_width=1.5
                )
                
                fig_sinc_sre.update_layout(
                    height=400,
                    plot_bgcolor='white',
                    xaxis_title="SRE",
                    yaxis_title="Número de Sincronizações",
                    margin=dict(t=50, b=50, l=50, r=50)
                )
                
                st.plotly_chart(fig_sinc_sre, use_container_width=True)
                
                # 2. Dashboard comparativo dos SREs
                st.markdown("### 📊 Dashboard Comparativo dos SREs")
                
                # Explicação da métrica de eficiência
                with st.expander("ℹ️ **Sobre a métrica de eficiência**", expanded=False):
                    st.markdown("""
                    #### 📈 **Como calculamos a eficiência do SRE:**
                    
                    **Fórmula:** 
                    ```
                    Eficiência = (Revisões / Sincronizações) × 100
                    ```
                    
                    **Interpretação:**
                    - **Eficiência ALTA** → SRE encontra muitos erros (faz muitas revisões por sincronização)
                    - **Eficiência BAIXA** → SRE encontra poucos erros (faz poucas revisões por sincronização)
                    
                    **Por que isso importa:**
                    1. **Qualidade**: SREs que fazem mais revisões estão encontrando mais problemas
                    2. **Prevenção**: Revisões evitam que erros cheguem em produção
                    3. **Excelência**: SREs eficientes garantem entregas mais confiáveis
                    
                    **Exemplo prático:**
                    - SRE A: 100 sincronizações, 25 revisões → Eficiência = 25%
                    - SRE B: 100 sincronizações, 10 revisões → Eficiência = 10%
                    - **SRE A é 2.5× mais eficiente** que SRE B!
                    """)
                
                col_comp1, col_comp2 = st.columns(2)
                
                with col_comp1:
                    # Tabela de performance
                    performance_sre = pd.DataFrame()
                    
                    # Sincronizações
                    performance_sre['SRE'] = sincronizacoes_por_sre['SRE']
                    performance_sre['Sincronizações'] = sincronizacoes_por_sre['Sincronizações']
                    
                    # Revisões por SRE
                    if 'Revisões' in df_sincronizados.columns:
                        revisoes_por_sre = df_sincronizados.groupby('SRE')['Revisões'].sum().reset_index()
                        revisoes_por_sre.columns = ['SRE', 'Revisões']
                        performance_sre = pd.merge(
                            performance_sre, 
                            revisoes_por_sre, 
                            on='SRE', 
                            how='left'
                        )
                        performance_sre['Revisões'] = performance_sre['Revisões'].fillna(0)
                    
                    # Calcular eficiência como Revisões/Sincronizações
                    if 'Revisões' in performance_sre.columns:
                        performance_sre['Eficiência'] = performance_sre.apply(
                            lambda x: (x['Revisões'] / x['Sincronizações'] * 100) 
                            if x['Sincronizações'] > 0 else 0,
                            axis=1
                        )
                        performance_sre['Eficiência'] = performance_sre['Eficiência'].round(2)
                    
                    # Ordenar por eficiência (maior é melhor)
                    performance_sre = performance_sre.sort_values('Eficiência', ascending=False)
                    
                    # Criar DataFrame para exibição com tooltips
                    display_performance = performance_sre.head(15).copy()
                    
                    # Adicionar ranking
                    display_performance['Ranking'] = range(1, len(display_performance) + 1)
                    
                    st.dataframe(
                        display_performance[['Ranking', 'SRE', 'Sincronizações', 'Revisões', 'Eficiência']],
                        use_container_width=True,
                        height=400,
                        column_config={
                            "Ranking": st.column_config.NumberColumn(
                                "#",
                                width="small",
                                help="Posição no ranking de eficiência"
                            ),
                            "SRE": st.column_config.TextColumn(
                                "SRE",
                                width="medium"
                            ),
                            "Sincronizações": st.column_config.NumberColumn(
                                "Sincronizações",
                                help="Número de chamados sincronizados pelo SRE",
                                format="%d"
                            ),
                            "Revisões": st.column_config.NumberColumn(
                                "Revisões",
                                help="Total de revisões feitas pelo SRE (quanto mais, melhor)",
                                format="%d"
                            ),
                            "Eficiência": st.column_config.NumberColumn(
                                "Eficiência (%)",
                                help="Cálculo: (Revisões / Sincronizações) × 100%\\n\\n"
                                     "📊 **Interpretação:**\\n"
                                     "• ALTA (>20%): Excelente detecção de erros\\n"
                                     "• MÉDIA (10-20%): Boa revisão\\n"
                                     "• BAIXA (<10%): Pode melhorar na detecção\\n\\n"
                                     "🔍 **Quanto MAIOR, MELHOR!**",
                                format="%.2f%%",
                                width="small"
                            )
                        }
                    )
                
                with col_comp2:
                    # Gráfico de eficiência
                    if len(performance_sre) > 0:
                        st.markdown("#### 📈 Ranking de Eficiência (Top 10)")
                        
                        top10_eficiencia = performance_sre.head(10).copy()
                        
                        fig_eficiencia = go.Figure()
                        
                        fig_eficiencia.add_trace(go.Bar(
                            x=top10_eficiencia['SRE'],
                            y=top10_eficiencia['Eficiência'],
                            name='Eficiência',
                            text=[f"{v:.1f}%" for v in top10_eficiencia['Eficiência']],
                            textposition='outside',
                            marker_color='#1e3799',
                            marker_line_color='#0c2461',
                            marker_line_width=1.5,
                            opacity=0.8,
                            hovertemplate="<b>%{x}</b><br>"
                                        "Eficiência: %{y:.2f}%<br>"
                                        "Sincronizações: %{customdata[0]}<br>"
                                        "Revisões: %{customdata[1]}<br>"
                                        "<extra></extra>",
                            customdata=top10_eficiencia[['Sincronizações', 'Revisões']].values
                        ))
                        
                        # Adicionar linha de média
                        media_eficiencia = top10_eficiencia['Eficiência'].mean()
                        fig_eficiencia.add_hline(
                            y=media_eficiencia,
                            line_dash="dash",
                            line_color="red",
                            annotation_text=f"Média: {media_eficiencia:.1f}%",
                            annotation_position="top right"
                        )
                        
                        # Adicionar zonas de classificação
                        fig_eficiencia.add_hrect(
                            y0=20, y1=100,
                            fillcolor="rgba(144, 238, 144, 0.2)",
                            line_width=0,
                            annotation_text="Excelente (>20%)",
                            annotation_position="top left"
                        )
                        
                        fig_eficiencia.add_hrect(
                            y0=10, y1=20,
                            fillcolor="rgba(255, 255, 224, 0.2)",
                            line_width=0,
                            annotation_text="Bom (10-20%)"
                        )
                        
                        fig_eficiencia.add_hrect(
                            y0=0, y1=10,
                            fillcolor="rgba(255, 182, 193, 0.2)",
                            line_width=0,
                            annotation_text="Pode melhorar (<10%)",
                            annotation_position="bottom left"
                        )
                        
                        fig_eficiencia.update_layout(
                            title="Eficiência dos SREs (Revisões por Sincronização)",
                            xaxis_title="SRE",
                            yaxis_title="Eficiência (%)",
                            plot_bgcolor='white',
                            height=400,
                            showlegend=False,
                            margin=dict(t=50, b=50, l=50, r=50),
                            yaxis=dict(range=[0, min(100, top10_eficiencia['Eficiência'].max() * 1.2)])
                        )
                        
                        st.plotly_chart(fig_eficiencia, use_container_width=True)
                    
                    # Métricas gerais
                    st.markdown("#### 📊 Métricas Gerais")
                    
                    total_sres = len(sincronizacoes_por_sre)
                    media_sinc = sincronizacoes_por_sre['Sincronizações'].mean()
                    
                    col_met1, col_met2 = st.columns(2)
                    with col_met1:
                        st.metric("Total de SREs", f"{total_sres}")
                    
                    with col_met2:
                        st.metric("Média de Sincronizações", f"{media_sinc:.1f}")
                    
                    if 'Revisões' in performance_sre.columns:
                        total_revisoes_sre = performance_sre['Revisões'].sum()
                        media_revisoes = performance_sre['Revisões'].mean()
                        
                        st.metric("Total de Revisões (SREs)", f"{int(total_revisoes_sre)}")
                        st.metric("Média de Revisões por SRE", f"{media_revisoes:.1f}")
                
                # 3. Evolução temporal do SRE líder em eficiência
                st.markdown("### 📈 Evolução Temporal do SRE Líder (Eficiência)")
                
                if not performance_sre.empty:
                    sre_lider_eficiencia = performance_sre.iloc[0]['SRE']
                    eficiencia_lider = performance_sre.iloc[0]['Eficiência']
                    
                    # Filtros para a evolução temporal
                    col_evol1, col_evol2, col_evol3 = st.columns(3)
                    
                    with col_evol1:
                        # Seletor de período
                        periodo_selecionado = st.selectbox(
                            "Período:",
                            options=['Diário', 'Mensal', 'Anual'],
                            key="periodo_evolucao"
                        )
                    
                    with col_evol2:
                        # Seletor de ano para filtro
                        if 'Ano' in df_sincronizados.columns:
                            anos_lider = sorted(df_sincronizados['Ano'].dropna().unique().astype(int))
                            ano_lider = st.selectbox(
                                "Ano:",
                                options=['Todos'] + list(anos_lider),
                                key="ano_lider"
                            )
                    
                    with col_evol3:
                        # Seletor de SRE (pode escolher outro além do líder)
                        sres_disponiveis = sorted(df_sincronizados['SRE'].dropna().unique())
                        sre_selecionado = st.selectbox(
                            "Selecionar SRE:",
                            options=[sre_lider_eficiencia] + [s for s in sres_disponiveis if s != sre_lider_eficiencia],
                            key="sre_selecionado"
                        )
                    
                    # Filtrar dados para o SRE selecionado
                    df_sre_selecionado = df_sincronizados[df_sincronizados['SRE'] == sre_selecionado].copy()
                    
                    if 'Ano' in df_sre_selecionado.columns and ano_lider != 'Todos':
                        df_sre_selecionado = df_sre_selecionado[df_sre_selecionado['Ano'] == int(ano_lider)]
                    
                    if not df_sre_selecionado.empty:
                        if periodo_selecionado == 'Diário':
                            # Agrupar por dia
                            df_sre_selecionado['Data'] = df_sre_selecionado['Criado'].dt.date
                            evolucao_sre = df_sre_selecionado.groupby('Data').agg({
                                'Revisões': 'sum'
                            }).reset_index()
                            evolucao_sre['Sincronizações'] = 1
                            evolucao_sre = evolucao_sre.groupby('Data').sum().reset_index()
                            eixo_x = 'Data'
                            titulo_evol = f"Evolução Diária de {sre_selecionado}"
                        
                        elif periodo_selecionado == 'Mensal':
                            # Agrupar por mês/ano
                            df_sre_selecionado['Ano_Mês'] = df_sre_selecionado['Criado'].dt.strftime('%Y-%m')
                            evolucao_sre = df_sre_selecionado.groupby('Ano_Mês').agg({
                                'Revisões': 'sum'
                            }).reset_index()
                            evolucao_sre['Sincronizações'] = df_sre_selecionado.groupby('Ano_Mês').size().values
                            eixo_x = 'Ano_Mês'
                            titulo_evol = f"Evolução Mensal de {sre_selecionado}"
                        
                        else:  # Anual
                            # Agrupar por ano
                            evolucao_sre = df_sre_selecionado.groupby('Ano').agg({
                                'Revisões': 'sum'
                            }).reset_index()
                            evolucao_sre['Sincronizações'] = df_sre_selecionado.groupby('Ano').size().values
                            eixo_x = 'Ano'
                            titulo_evol = f"Evolução Anual de {sre_selecionado}"
                        
                        # Calcular eficiência por período
                        evolucao_sre['Eficiência'] = (evolucao_sre['Revisões'] / evolucao_sre['Sincronizações'] * 100).round(2)
                        evolucao_sre = evolucao_sre.sort_values(eixo_x)
                        
                        # Criar gráfico de linha duplo
                        fig_evol_sre = go.Figure()
                        
                        # Adicionar linha de eficiência
                        fig_evol_sre.add_trace(go.Scatter(
                            x=evolucao_sre[eixo_x],
                            y=evolucao_sre['Eficiência'],
                            mode='lines+markers',
                            name='Eficiência (%)',
                            line=dict(color='#1e3799', width=3),
                            marker=dict(size=10, color='#0c2461'),
                            yaxis='y',
                            text=evolucao_sre['Eficiência'],
                            hovertemplate="<b>%{x}</b><br>Eficiência: %{y:.2f}%<br>Sincronizações: %{customdata[0]}<br>Revisões: %{customdata[1]}<extra></extra>",
                            customdata=evolucao_sre[['Sincronizações', 'Revisões']].values
                        ))
                        
                        # Adicionar barras para sincronizações (eixo secundário)
                        fig_evol_sre.add_trace(go.Bar(
                            x=evolucao_sre[eixo_x],
                            y=evolucao_sre['Sincronizações'],
                            name='Sincronizações',
                            marker_color='rgba(40, 167, 69, 0.3)',
                            yaxis='y2',
                            opacity=0.6
                        ))
                        
                        fig_evol_sre.update_layout(
                            title=f"{titulo_evol} - Eficiência vs Sincronizações",
                            xaxis_title="Período",
                            yaxis_title="Eficiência (%)",
                            yaxis2=dict(
                                title="Sincronizações",
                                overlaying='y',
                                side='right',
                                showgrid=False
                            ),
                            plot_bgcolor='white',
                            height=400,
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            ),
                            margin=dict(t=50, b=50, l=50, r=50)
                        )
                        
                        st.plotly_chart(fig_evol_sre, use_container_width=True)
                        
                        # Estatísticas da evolução
                        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                        
                        with col_stat1:
                            eficiencia_media = evolucao_sre['Eficiência'].mean()
                            st.metric("Eficiência média", f"{eficiencia_media:.1f}%")
                        
                        with col_stat2:
                            max_eficiencia = evolucao_sre['Eficiência'].max()
                            periodo_max = evolucao_sre.loc[evolucao_sre['Eficiência'].idxmax(), eixo_x]
                            st.metric("Melhor período", f"{periodo_max}: {max_eficiencia:.1f}%")
                        
                        with col_stat3:
                            total_sinc = evolucao_sre['Sincronizações'].sum()
                            st.metric("Total sincronizações", f"{total_sinc}")
                        
                        with col_stat4:
                            total_rev = evolucao_sre['Revisões'].sum()
                            st.metric("Total revisões", f"{total_rev}")
            else:
                st.info("ℹ️ Nenhum dado de sincronização disponível para análise dos SREs.")
        else:
            st.warning("⚠️ Coluna 'SRE' não encontrada nos dados.")
    
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
                title='',
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
    # ÚLTIMAS DEMANDAS REGISTRADAS COM FILTROS
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
            mostrar_colunas = st.multiselect(
                "Colunas a mostrar:",
                options=['Chamado', 'Tipo_Chamado', 'Responsável', 'Status', 'Prioridade', 'Revisões', 'Empresa', 'SRE', 'Data'],
                default=['Chamado', 'Tipo_Chamado', 'Responsável', 'Status', 'Data'],
                key="select_colunas"
            )
        
        with col_filtro4:
            # Filtro de busca por chamado específico
            filtro_chamado_tabela = st.text_input(
                "Filtrar por chamado:",
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
        
        # Aplicar filtro de busca por chamado
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
        
        if 'Responsável' in mostrar_colunas and 'Responsável_Formatado' in ultimas_demandas.columns:
            display_data['Responsável'] = ultimas_demandas['Responsável_Formatado']
        
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
        Versão 5.4 | Sistema de Performance SRE | Última atualização: {ultima_atualizacao} (Brasília)
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
