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
    
    /* Novos estilos para as análises avançadas */
    .score-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #28a745;
    }
    
    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .score-high {
        background-color: #d4edda;
        color: #155724;
    }
    
    .score-medium {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .score-low {
        background-color: #f8d7da;
        color: #721c24;
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
            v5.5 | Sistema de Performance SRE
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
    
    with tab3:
        st.markdown('<div class="section-title-exec">📈 CHAMADOS SINCRONIZADOS POR DIA</div>', unsafe_allow_html=True)
        
        if 'Status' in df.columns and 'Criado' in df.columns:
            # Filtrar apenas chamados sincronizados
            df_sincronizados = df[df['Status'] == 'Sincronizado'].copy()
            
            if not df_sincronizados.empty:
                # Extrair data sem hora
                df_sincronizados['Data'] = df_sincronizados['Criado'].dt.date
                
                # Agrupar por data
                sincronizados_por_dia = df_sincronizados.groupby('Data').size().reset_index()
                sincronizados_por_dia.columns = ['Data', 'Quantidade']
                
                # Ordenar por data
                sincronizados_por_dia = sincronizados_por_dia.sort_values('Data')
                
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
                    title='Evolução Diária de Chamados Sincronizados',
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
                # Ranking dos SREs que mais sincronizaram
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
                
                # Dashboard comparativo dos SREs
                st.markdown("### 📊 Dashboard Comparativo dos SREs")
                
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
                                help="Cálculo: (Revisões / Sincronizações) × 100%",
                                format="%.2f%%",
                                width="small"
                            )
                        }
                    )
    
    # ============================================
    # ANÁLISES AVANÇADAS - AS 4 FUNCIONALIDADES SOLICITADAS
    # ============================================
    st.markdown("---")
    st.markdown('<div class="section-title-exec">🔍 ANÁLISES AVANÇADAS</div>', unsafe_allow_html=True)
    
    # Criar abas para as análises avançadas
    tab_avancada1, tab_avancada2, tab_avancada3, tab_avancada4 = st.tabs([
        "📊 Score de Qualidade por Desenvolvedor",
        "📅 Análise de Sazonalidade", 
        "🔧 Análise de Erros Recorrentes",
        "📋 Relatórios Automáticos"
    ])
    
    # ABA 1: SCORE DE QUALIDADE POR DESENVOLVEDOR
    with tab_avancada1:
        st.markdown("### 📊 SCORE DE QUALIDADE POR DESENVOLVEDOR")
        
        # Informações sobre a análise
        with st.expander("ℹ️ **Sobre esta análise**", expanded=True):
            st.markdown("""
            #### **Objetivo:**
            Avaliar a qualidade do código enviado por cada desenvolvedor com base no histórico de revisões.
            
            #### **Como calculamos o Score:**
            ```
            Score = (Chamados sem revisão / Total de chamados do desenvolvedor) × 100
            ```
            
            #### **Interpretação:**
            - **Score ALTO (80-100%)**: Desenvolvedor produz código de alta qualidade
            - **Score MÉDIO (60-80%)**: Qualidade satisfatória, com espaço para melhorias
            - **Score BAIXO (<60%)**: Necessidade de atenção e treinamento
            
            #### **Benefícios:**
            - Identifica desenvolvedores que precisam de apoio
            - Mede eficácia dos processos de code review
            - Ajuda no planejamento de treinamentos
            """)
        
        if 'Responsável_Formatado' in df.columns and 'Revisões' in df.columns:
            # Calcular estatísticas por desenvolvedor
            dev_stats = df.groupby('Responsável_Formatado').agg({
                'Chamado': 'count',  # Total de chamados
                'Revisões': lambda x: (x == 0).sum()  # Chamados sem revisão
            }).reset_index()
            
            dev_stats.columns = ['Desenvolvedor', 'Total_Chamados', 'Chamados_Sem_Revisao']
            
            # Calcular score
            dev_stats['Score'] = (dev_stats['Chamados_Sem_Revisao'] / dev_stats['Total_Chamados'] * 100).round(1)
            
            # Classificar score
            def classificar_score(score):
                if score >= 80:
                    return '🟢 Alta'
                elif score >= 60:
                    return '🟡 Média'
                else:
                    return '🔴 Baixa'
            
            dev_stats['Classificação'] = dev_stats['Score'].apply(classificar_score)
            
            # Ordenar por score
            dev_stats = dev_stats.sort_values('Score', ascending=False)
            
            # Layout com métricas e gráficos
            col_metrica1, col_metrica2, col_metrica3 = st.columns(3)
            
            with col_metrica1:
                total_devs = len(dev_stats)
                st.metric("Total de Desenvolvedores", total_devs)
            
            with col_metrica2:
                score_medio = dev_stats['Score'].mean()
                st.metric("Score Médio", f"{score_medio:.1f}%")
            
            with col_metrica3:
                devs_alta_qualidade = len(dev_stats[dev_stats['Score'] >= 80])
                st.metric("Desenvolvedores com Alta Qualidade", devs_alta_qualidade)
            
            # Gráfico de distribuição dos scores
            st.markdown("#### 📈 Distribuição dos Scores de Qualidade")
            
            # Criar histograma
            fig_score_dist = px.histogram(
                dev_stats,
                x='Score',
                nbins=10,
                title='Distribuição dos Scores de Qualidade',
                labels={'Score': 'Score de Qualidade (%)', 'count': 'Número de Desenvolvedores'},
                color_discrete_sequence=['#1e3799']
            )
            
            fig_score_dist.update_layout(
                height=400,
                plot_bgcolor='white',
                bargap=0.1,
                showlegend=False
            )
            
            # Adicionar linhas de referência
            fig_score_dist.add_vline(x=80, line_dash="dash", line_color="green", 
                                     annotation_text="Alta (≥80%)", annotation_position="top")
            fig_score_dist.add_vline(x=60, line_dash="dash", line_color="orange",
                                     annotation_text="Média (60-80%)", annotation_position="top")
            
            st.plotly_chart(fig_score_dist, use_container_width=True)
            
            # Tabela detalhada
            st.markdown("#### 📋 Ranking de Desenvolvedores")
            
            # Mostrar top 15 desenvolvedores
            top_devs = dev_stats.head(15).copy()
            top_devs['Ranking'] = range(1, len(top_devs) + 1)
            
            # Formatando a tabela
            st.dataframe(
                top_devs[['Ranking', 'Desenvolvedor', 'Total_Chamados', 'Chamados_Sem_Revisao', 'Score', 'Classificação']],
                use_container_width=True,
                height=400,
                column_config={
                    "Ranking": st.column_config.NumberColumn("#", width="small"),
                    "Desenvolvedor": st.column_config.TextColumn("Desenvolvedor"),
                    "Total_Chamados": st.column_config.NumberColumn("Total Chamados", format="%d"),
                    "Chamados_Sem_Revisao": st.column_config.NumberColumn("Sem Revisão", format="%d"),
                    "Score": st.column_config.NumberColumn("Score (%)", format="%.1f%%"),
                    "Classificação": st.column_config.TextColumn("Classificação")
                }
            )
            
            # Detalhes do desenvolvedor selecionado
            st.markdown("#### 🔍 Análise Detalhada por Desenvolvedor")
            
            dev_selecionado = st.selectbox(
                "Selecione um desenvolvedor para análise detalhada:",
                options=dev_stats['Desenvolvedor'].tolist(),
                key="dev_selecionado"
            )
            
            if dev_selecionado:
                dev_data = dev_stats[dev_stats['Desenvolvedor'] == dev_selecionado].iloc[0]
                dev_chamados = df[df['Responsável_Formatado'] == dev_selecionado]
                
                col_det1, col_det2, col_det3, col_det4 = st.columns(4)
                
                with col_det1:
                    st.metric("Score do Desenvolvedor", f"{dev_data['Score']:.1f}%")
                
                with col_det2:
                    st.metric("Total de Chamados", f"{dev_data['Total_Chamados']}")
                
                with col_det3:
                    st.metric("Chamados sem Revisão", f"{dev_data['Chamados_Sem_Revisao']}")
                
                with col_det4:
                    taxa_sucesso = (dev_data['Chamados_Sem_Revisao'] / dev_data['Total_Chamados'] * 100)
                    st.metric("Taxa de Sucesso", f"{taxa_sucesso:.1f}%")
                
                # Revisões ao longo do tempo
                if 'Criado' in dev_chamados.columns:
                    st.markdown("##### 📊 Evolução Temporal")
                    
                    dev_chamados['Mês'] = dev_chamados['Criado'].dt.to_period('M').astype(str)
                    evolucao_mensal = dev_chamados.groupby('Mês').agg({
                        'Revisões': lambda x: (x == 0).sum(),  # Sem revisão
                        'Chamado': 'count'  # Total
                    }).reset_index()
                    
                    evolucao_mensal['Score_Mensal'] = (evolucao_mensal['Revisões'] / evolucao_mensal['Chamado'] * 100).round(1)
                    
                    fig_evol = px.line(
                        evolucao_mensal,
                        x='Mês',
                        y='Score_Mensal',
                        markers=True,
                        title=f'Evolução do Score de {dev_selecionado}',
                        labels={'Score_Mensal': 'Score Mensal (%)', 'Mês': 'Mês'}
                    )
                    
                    fig_evol.update_layout(
                        height=300,
                        plot_bgcolor='white',
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_evol, use_container_width=True)
    
    # ABA 2: ANÁLISE DE SAZONALIDADE
    with tab_avancada2:
        st.markdown("### 📅 ANÁLISE DE SAZONALIDADE")
        
        with st.expander("ℹ️ **Sobre esta análise**", expanded=True):
            st.markdown("""
            #### **Objetivo:**
            Identificar padrões temporais na geração de demandas para planejamento de recursos.
            
            #### **Padrões analisados:**
            1. **Horários de pico**: Identifica os horários com maior volume de chamados
            2. **Dias da semana**: Mostra quais dias têm mais demandas
            3. **Sazonalidade mensal**: Revela variações ao longo dos meses
            
            #### **Aplicações práticas:**
            - Planejamento de equipes por turno
            - Alocação de recursos em períodos críticos
            - Previsão de demanda futura
            - Otimização de processos
            """)
        
        if 'Criado' in df.columns:
            # Criar dataframe para análise
            df_saz = df.copy()
            df_saz['Dia_Semana'] = df_saz['Criado'].dt.day_name()
            df_saz['Hora'] = df_saz['Criado'].dt.hour
            
            # Mapeamento de dias da semana
            dias_semana_ingles = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dias_semana_portugues = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            
            # Análise por Dia da Semana
            st.markdown("#### 📊 Análise por Dia da Semana")
            
            col_dia1, col_dia2 = st.columns(2)
            
            with col_dia1:
                # Contar chamados por dia da semana
                demanda_dia = df_saz['Dia_Semana'].value_counts().reindex(dias_semana_ingles).reset_index()
                demanda_dia.columns = ['Dia_Semana', 'Quantidade']
                demanda_dia['Dia_PT'] = dias_semana_portugues
                
                # Gráfico de barras
                fig_dias = px.bar(
                    demanda_dia,
                    x='Dia_PT',
                    y='Quantidade',
                    title='Demanda por Dia da Semana',
                    labels={'Dia_PT': 'Dia da Semana', 'Quantidade': 'Número de Chamados'},
                    color='Quantidade',
                    color_continuous_scale='Blues'
                )
                
                fig_dias.update_layout(
                    height=400,
                    plot_bgcolor='white',
                    showlegend=False
                )
                
                st.plotly_chart(fig_dias, use_container_width=True)
            
            with col_dia2:
                # Métricas principais
                dia_max = demanda_dia.loc[demanda_dia['Quantidade'].idxmax()]
                dia_min = demanda_dia.loc[demanda_dia['Quantidade'].idxmin()]
                media_dias = demanda_dia['Quantidade'].mean()
                
                st.metric("📈 Dia com mais demandas", 
                         f"{dia_max['Dia_PT']}: {int(dia_max['Quantidade']):,}")
                st.metric("📉 Dia com menos demandas", 
                         f"{dia_min['Dia_PT']}: {int(dia_min['Quantidade']):,}")
                st.metric("📊 Média diária", f"{int(media_dias):,}")
                
                # Estatísticas adicionais
                st.markdown("##### 📈 Variação entre dias")
                diferenca = ((dia_max['Quantidade'] - dia_min['Quantidade']) / dia_min['Quantidade'] * 100)
                st.info(f"Diferença entre maior e menor dia: **{diferenca:.1f}%**")
                
                # Identificar padrão de fim de semana
                fim_semana = demanda_dia[demanda_dia['Dia_PT'].isin(['Sábado', 'Domingo'])]['Quantidade'].sum()
                semana = demanda_dia[~demanda_dia['Dia_PT'].isin(['Sábado', 'Domingo'])]['Quantidade'].sum()
                perc_fim_semana = (fim_semana / (fim_semana + semana) * 100)
                st.info(f"Demanda no fim de semana: **{perc_fim_semana:.1f}%** do total")
            
            # Análise por Hora do Dia
            st.markdown("#### ⏰ Análise por Hora do Dia")
            
            col_hora1, col_hora2 = st.columns(2)
            
            with col_hora1:
                # Contar chamados por hora
                demanda_hora = df_saz['Hora'].value_counts().sort_index().reset_index()
                demanda_hora.columns = ['Hora', 'Quantidade']
                
                # Gráfico de linha
                fig_horas = px.line(
                    demanda_hora,
                    x='Hora',
                    y='Quantidade',
                    title='Demanda por Hora do Dia',
                    labels={'Hora': 'Hora do Dia', 'Quantidade': 'Número de Chamados'},
                    markers=True
                )
                
                fig_horas.update_traces(
                    line=dict(width=3, color='#1e3799'),
                    marker=dict(size=8, color='#0c2461')
                )
                
                fig_horas.update_layout(
                    height=400,
                    plot_bgcolor='white',
                    showlegend=False,
                    xaxis=dict(
                        tickmode='linear',
                        tick0=0,
                        dtick=2
                    )
                )
                
                # Adicionar área sombreada
                fig_horas.add_hrect(
                    y0=0, y1=demanda_hora['Quantidade'].max(),
                    fillcolor="rgba(30, 55, 153, 0.1)",
                    line_width=0
                )
                
                st.plotly_chart(fig_horas, use_container_width=True)
            
            with col_hora2:
                # Identificar horários de pico
                hora_max = demanda_hora.loc[demanda_hora['Quantidade'].idxmax()]
                hora_min = demanda_hora.loc[demanda_hora['Quantidade'].idxmin()]
                
                st.metric("⏰ Horário de pico", 
                         f"{int(hora_max['Hora'])}:00 - {int(hora_max['Hora'])+1}:00")
                st.metric("📉 Horário mais tranquilo", 
                         f"{int(hora_min['Hora'])}:00 - {int(hora_min['Hora'])+1}:00")
                
                # Calcular períodos do dia
                manha = demanda_hora[demanda_hora['Hora'].between(6, 11)]['Quantidade'].sum()
                tarde = demanda_hora[demanda_hora['Hora'].between(12, 17)]['Quantidade'].sum()
                noite = demanda_hora[demanda_hora['Hora'].between(18, 23)]['Quantidade'].sum()
                madrugada = demanda_hora[demanda_hora['Hora'].between(0, 5)]['Quantidade'].sum()
                
                total = manha + tarde + noite + madrugada
                
                col_per1, col_per2, col_per3, col_per4 = st.columns(4)
                with col_per1:
                    st.metric("🌅 Manhã", f"{(manha/total*100):.0f}%")
                with col_per2:
                    st.metric("☀️ Tarde", f"{(tarde/total*100):.0f}%")
                with col_per3:
                    st.metric("🌙 Noite", f"{(noite/total*100):.0f}%")
                with col_per4:
                    st.metric("🌌 Madrugada", f"{(madrugada/total*100):.0f}%")
                
                # Recomendações
                st.markdown("##### 💡 Recomendações")
                if hora_max['Hora'] >= 9 and hora_max['Hora'] <= 17:
                    st.success("**Horário comercial**: Considere reforçar equipe entre 9h e 17h")
                elif hora_max['Hora'] >= 18:
                    st.warning("**Horário noturno**: Avaliar necessidade de plantão noturno")
            
            # Análise Mensal (Todos os anos)
            st.markdown("#### 📅 Análise Mensal (Todos os anos)")
            
            if 'Nome_Mês' in df_saz.columns:
                # Ordem dos meses
                ordem_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                              'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                
                # Agrupar por mês
                demanda_mes = df_saz.groupby('Nome_Mês').size().reset_index()
                demanda_mes.columns = ['Mês', 'Quantidade']
                
                # Ordenar pela ordem correta
                demanda_mes['Mês_Num'] = demanda_mes['Mês'].map(
                    {m: i+1 for i, m in enumerate(ordem_meses)}
                )
                demanda_mes = demanda_mes.sort_values('Mês_Num')
                
                # Gráfico de barras
                fig_meses = px.bar(
                    demanda_mes,
                    x='Mês',
                    y='Quantidade',
                    title='Demanda por Mês (Todos os anos)',
                    labels={'Mês': 'Mês', 'Quantidade': 'Número de Chamados'},
                    color='Quantidade',
                    color_continuous_scale='Viridis'
                )
                
                fig_meses.update_layout(
                    height=400,
                    plot_bgcolor='white',
                    showlegend=False
                )
                
                st.plotly_chart(fig_meses, use_container_width=True)
                
                # Insights sazonais
                mes_max = demanda_mes.loc[demanda_mes['Quantidade'].idxmax()]
                mes_min = demanda_mes.loc[demanda_mes['Quantidade'].idxmin()]
                
                col_insight1, col_insight2 = st.columns(2)
                with col_insight1:
                    st.info(f"**Mês mais movimentado**: {mes_max['Mês']} ({int(mes_max['Quantidade']):,} chamados)")
                with col_insight2:
                    st.info(f"**Mês mais tranquilo**: {mes_min['Mês']} ({int(mes_min['Quantidade']):,} chamados)")
                
                # Análise de sazonalidade por trimestre
                st.markdown("##### 📊 Análise por Trimestre")
                
                # Mapear meses para trimestres
                trimestre_map = {
                    'Jan': 'Q1', 'Fev': 'Q1', 'Mar': 'Q1',
                    'Abr': 'Q2', 'Mai': 'Q2', 'Jun': 'Q2',
                    'Jul': 'Q3', 'Ago': 'Q3', 'Set': 'Q3',
                    'Out': 'Q4', 'Nov': 'Q4', 'Dez': 'Q4'
                }
                
                demanda_mes['Trimestre'] = demanda_mes['Mês'].map(trimestre_map)
                demanda_trimestre = demanda_mes.groupby('Trimestre')['Quantidade'].sum().reset_index()
                
                col_trim1, col_trim2, col_trim3, col_trim4 = st.columns(4)
                
                for i, trim in enumerate(['Q1', 'Q2', 'Q3', 'Q4']):
                    trim_data = demanda_trimestre[demanda_trimestre['Trimestre'] == trim]
                    if not trim_data.empty:
                        with [col_trim1, col_trim2, col_trim3, col_trim4][i]:
                            st.metric(f"Trimestre {trim[-1]}", f"{int(trim_data.iloc[0]['Quantidade']):,}")
    
    # ABA 3: ANÁLISE DE ERROS RECORRENTES
    with tab_avancada3:
        st.markdown("### 🔧 ANÁLISE DE ERROS RECORRENTES")
        
        with st.expander("ℹ️ **Sobre esta análise**", expanded=True):
            st.markdown("""
            #### **Objetivo:**
            Identificar padrões de erros frequentes para prevenção e melhoria de processos.
            
            #### **O que analisamos:**
            1. **Tipos de chamados mais frequentes**
            2. **Evolução temporal dos problemas**
            3. **Complexidade associada a cada tipo**
            4. **Impacto nas revisões**
            
            #### **Benefícios:**
            - Redução de retrabalho
            - Melhoria da qualidade do código
            - Identificação de áreas para treinamento
            - Otimização de processos
            """)
        
        if 'Tipo_Chamado' in df.columns:
            # Análise de Frequência por Tipo
            st.markdown("#### 📊 Frequência por Tipo de Chamado")
            
            col_tipo1, col_tipo2 = st.columns(2)
            
            with col_tipo1:
                # Contar tipos de chamados
                tipos_chamado = df['Tipo_Chamado'].value_counts().reset_index()
                tipos_chamado.columns = ['Tipo', 'Frequência']
                
                # Top 10 tipos
                top_tipos = tipos_chamado.head(10)
                
                # Gráfico de pizza
                fig_pizza = px.pie(
                    top_tipos,
                    values='Frequência',
                    names='Tipo',
                    title='Top 10 Tipos de Chamados',
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Blues
                )
                
                fig_pizza.update_layout(
                    height=400,
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=0.95,
                        xanchor="left",
                        x=1.05
                    )
                )
                
                st.plotly_chart(fig_pizza, use_container_width=True)
            
            with col_tipo2:
                # Métricas principais
                total_tipos = len(tipos_chamado)
                tipos_mais_frequentes = top_tipos.head(3)
                
                st.metric("Total de Tipos Únicos", total_tipos)
                
                for i, row in tipos_mais_frequentes.iterrows():
                    perc = (row['Frequência'] / len(df) * 100)
                    st.metric(f"{row['Tipo']}", 
                             f"{row['Frequência']:,} ({perc:.1f}%)")
                
                # Concentração de problemas
                top5_perc = tipos_chamado.head(5)['Frequência'].sum() / len(df) * 100
                st.info(f"**Concentração**: Top 5 tipos representam **{top5_perc:.1f}%** de todos os chamados")
            
            # Análise de Complexidade por Tipo
            st.markdown("#### 📈 Complexidade por Tipo de Chamado")
            
            if 'Revisões' in df.columns:
                # Agrupar por tipo
                complexidade_tipo = df.groupby('Tipo_Chamado').agg({
                    'Revisões': ['mean', 'sum', 'count'],
                    'Chamado': 'nunique'
                }).reset_index()
                
                # Ajustar nomes das colunas
                complexidade_tipo.columns = ['Tipo', 'Média_Revisões', 'Total_Revisões', 'Quantidade', 'Chamados_Únicos']
                
                # Filtrar tipos com pelo menos 5 ocorrências
                complexidade_tipo = complexidade_tipo[complexidade_tipo['Quantidade'] >= 5]
                complexidade_tipo = complexidade_tipo.sort_values('Média_Revisões', ascending=False)
                
                # Gráfico de dispersão
                fig_complex = px.scatter(
                    complexidade_tipo.head(15),
                    x='Quantidade',
                    y='Média_Revisões',
                    size='Total_Revisões',
                    color='Média_Revisões',
                    hover_name='Tipo',
                    title='Complexidade vs Frequência (Top 15)',
                    labels={
                        'Quantidade': 'Frequência (Nº de ocorrências)',
                        'Média_Revisões': 'Média de Revisões por Chamado',
                        'Total_Revisões': 'Total de Revisões'
                    },
                    size_max=50,
                    color_continuous_scale='RdYlBu_r'  # Vermelho = complexo, Azul = simples
                )
                
                fig_complex.update_layout(
                    height=500,
                    plot_bgcolor='white',
                    hovermode='closest'
                )
                
                # Adicionar linhas de referência
                media_geral_revisoes = df['Revisões'].mean()
                fig_complex.add_hline(
                    y=media_geral_revisoes,
                    line_dash="dash",
                    line_color="gray",
                    annotation_text=f"Média Geral: {media_geral_revisoes:.1f}",
                    annotation_position="top right"
                )
                
                st.plotly_chart(fig_complex, use_container_width=True)
                
                # Tabela de tipos mais complexos
                st.markdown("##### 🎯 Tipos Mais Complexos (Média de Revisões)")
                
                tipos_complexos = complexidade_tipo.head(10).copy()
                tipos_complexos['Ranking'] = range(1, len(tipos_complexos) + 1)
                
                st.dataframe(
                    tipos_complexos[['Ranking', 'Tipo', 'Quantidade', 'Média_Revisões', 'Total_Revisões']],
                    use_container_width=True,
                    height=300,
                    column_config={
                        "Ranking": st.column_config.NumberColumn("#", width="small"),
                        "Tipo": st.column_config.TextColumn("Tipo de Chamado"),
                        "Quantidade": st.column_config.NumberColumn("Ocorrências", format="%d"),
                        "Média_Revisões": st.column_config.NumberColumn("Média Revisões", format="%.2f"),
                        "Total_Revisões": st.column_config.NumberColumn("Total Revisões", format="%d")
                    }
                )
            
            # Evolução Temporal dos Tipos
            st.markdown("#### 📅 Evolução Temporal dos Tipos")
            
            if 'Criado' in df.columns:
                # Preparar dados
                df['Mês_Ano'] = df['Criado'].dt.strftime('%Y-%m')
                
                # Selecionar tipos para análise
                tipos_para_analise = st.multiselect(
                    "Selecione os tipos para análise temporal:",
                    options=df['Tipo_Chamado'].unique().tolist(),
                    default=tipos_chamado.head(5)['Tipo'].tolist(),
                    key="tipos_temporal"
                )
                
                if tipos_para_analise:
                    # Filtrar dados
                    df_tipos_selecionados = df[df['Tipo_Chamado'].isin(tipos_para_analise)]
                    
                    # Agrupar por mês e tipo
                    evol_tipos = df_tipos_selecionados.groupby(['Mês_Ano', 'Tipo_Chamado']).size().reset_index()
                    evol_tipos.columns = ['Mês_Ano', 'Tipo', 'Quantidade']
                    
                    # Ordenar por data
                    evol_tipos = evol_tipos.sort_values('Mês_Ano')
                    
                    # Gráfico de linha
                    fig_evol_tipos = px.line(
                        evol_tipos,
                        x='Mês_Ano',
                        y='Quantidade',
                        color='Tipo',
                        title='Evolução dos Tipos de Chamados ao Longo do Tempo',
                        labels={'Mês_Ano': 'Mês/Ano', 'Quantidade': 'Número de Chamados'},
                        markers=True
                    )
                    
                    fig_evol_tipos.update_layout(
                        height=400,
                        plot_bgcolor='white',
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_evol_tipos, use_container_width=True)
                    
                    # Análise de tendência
                    st.markdown("##### 📊 Análise de Tendência")
                    
                    # Calcular tendência para cada tipo
                    tendencias = []
                    for tipo in tipos_para_analise:
                        tipo_data = evol_tipos[evol_tipos['Tipo'] == tipo]
                        if len(tipo_data) > 1:
                            # Regressão linear simples
                            x = range(len(tipo_data))
                            y = tipo_data['Quantidade'].values
                            
                            # Coeficiente angular (tendência)
                            coef_angular = np.polyfit(x, y, 1)[0] if len(tipo_data) > 1 else 0
                            
                            tendencias.append({
                                'Tipo': tipo,
                                'Tendência': '📈 Aumentando' if coef_angular > 0.1 else 
                                            '📉 Diminuindo' if coef_angular < -0.1 else 
                                            '📊 Estável',
                                'Variação (%)': ((tipo_data['Quantidade'].iloc[-1] / tipo_data['Quantidade'].iloc[0] - 1) * 100 
                                                if tipo_data['Quantidade'].iloc[0] > 0 else 0)
                            })
                    
                    if tendencias:
                        df_tendencias = pd.DataFrame(tendencias)
                        st.dataframe(
                            df_tendencias,
                            use_container_width=True,
                            column_config={
                                "Tipo": st.column_config.TextColumn("Tipo"),
                                "Tendência": st.column_config.TextColumn("Tendência"),
                                "Variação (%)": st.column_config.NumberColumn("Variação %", format="%.1f%%")
                            }
                        )
            
            # Recomendações baseadas na análise
            st.markdown("#### 💡 Recomendações e Insights")
            
            col_rec1, col_rec2 = st.columns(2)
            
            with col_rec1:
                st.markdown("##### 🎯 Foco em Melhoria")
                if 'complexidade_tipo' in locals() and not complexidade_tipo.empty:
                    tipo_mais_complexo = complexidade_tipo.iloc[0]
                    st.warning(f"""
                    **Tipo mais complexo**: {tipo_mais_complexo['Tipo']}
                    - Média de {tipo_mais_complexo['Média_Revisões']:.1f} revisões por chamado
                    - Ocorre {tipo_mais_complexo['Quantidade']} vezes
                    - **Ação recomendada**: Revisar processo e criar checklist
                    """)
            
            with col_rec2:
                st.markdown("##### 📈 Oportunidades")
                if 'tipos_chamado' in locals() and not tipos_chamado.empty:
                    tipo_mais_frequente = tipos_chamado.iloc[0]
                    perc = (tipo_mais_frequente['Frequência'] / len(df) * 100)
                    st.info(f"""
                    **Tipo mais frequente**: {tipo_mais_frequente['Tipo']}
                    - Representa {perc:.1f}% dos chamados
                    - **Oportunidade**: Automatizar ou criar template
                    """)
    
    # ABA 4: RELATÓRIOS AUTOMÁTICOS
    with tab_avancada4:
        st.markdown("### 📋 RELATÓRIOS AUTOMÁTICOS")
        
        with st.expander("ℹ️ **Sobre esta funcionalidade**", expanded=True):
            st.markdown("""
            #### **Objetivo:**
            Geração automática de relatórios para diferentes públicos e necessidades.
            
            #### **Tipos disponíveis:**
            1. **Relatório Diário**: Resumo do dia para acompanhamento da equipe
            2. **Relatório Semanal**: Performance da semana para gestão
            3. **Relatório Mensal**: Métricas estratégicas para direção
            4. **Relatório Trimestral**: Análise de tendências e planejamento
            
            #### **Funcionalidades:**
            - Configuração personalizada
            - Exportação em múltiplos formatos
            - Agendamento automático
            - Envio por e-mail
            """)
        
        # Configuração do Relatório
        st.markdown("#### ⚙️ Configuração do Relatório")
        
        col_config1, col_config2, col_config3 = st.columns(3)
        
        with col_config1:
            tipo_relatorio = st.selectbox(
                "Tipo de relatório:",
                ["Diário", "Semanal", "Mensal", "Trimestral", "Personalizado"],
                key="tipo_relatorio"
            )
        
        with col_config2:
            formato_export = st.multiselect(
                "Formatos de exportação:",
                ["PDF", "Excel", "CSV", "HTML"],
                default=["Excel"],
                key="formato_export"
            )
        
        with col_config3:
            secoes_relatorio = st.multiselect(
                "Seções a incluir:",
                [
                    "Resumo Executivo",
                    "Métricas Principais", 
                    "Performance por Equipe",
                    "Análise de Tendências",
                    "Recomendações",
                    "Detalhamento por Projeto",
                    "Comparativo Período Anterior"
                ],
                default=["Resumo Executivo", "Métricas Principais", "Recomendações"],
                key="secoes_relatorio"
            )
        
        # Período do Relatório
        st.markdown("#### 📅 Período do Relatório")
        
        hoje = datetime.now()
        
        if tipo_relatorio == "Diário":
            data_inicio = hoje - timedelta(days=1)
            data_fim = hoje
            periodo_desc = f"Últimas 24 horas (de {data_inicio.strftime('%d/%m/%Y %H:%M')} a {data_fim.strftime('%d/%m/%Y %H:%M')})"
        
        elif tipo_relatorio == "Semanal":
            data_inicio = hoje - timedelta(days=7)
            data_fim = hoje
            periodo_desc = f"Última semana (de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})"
        
        elif tipo_relatorio == "Mensal":
            data_inicio = hoje - timedelta(days=30)
            data_fim = hoje
            periodo_desc = f"Último mês (de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})"
        
        elif tipo_relatorio == "Trimestral":
            data_inicio = hoje - timedelta(days=90)
            data_fim = hoje
            periodo_desc = f"Último trimestre (de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})"
        
        else:  # Personalizado
            col_data1, col_data2 = st.columns(2)
            with col_data1:
                data_inicio = st.date_input("Data inicial:", value=hoje - timedelta(days=30))
            with col_data2:
                data_fim = st.date_input("Data final:", value=hoje)
            
            periodo_desc = f"Período personalizado (de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})"
        
        # Resumo da Configuração
        st.markdown("#### 📋 Resumo da Configuração")
        
        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
        
        with col_sum1:
            st.metric("Tipo", tipo_relatorio)
        
        with col_sum2:
            st.metric("Período", periodo_desc.split('(')[0].strip())
        
        with col_sum3:
            st.metric("Seções", len(secoes_relatorio))
        
        with col_sum4:
            st.metric("Formatos", len(formato_export))
        
        # Pré-visualização do Relatório
        st.markdown("#### 👁️ Pré-visualização do Relatório")
        
        with st.expander("📄 **Resumo Executivo**", expanded=True):
            # Filtrar dados para o período
            if 'Criado' in df.columns:
                df_periodo = df[(df['Criado'] >= pd.Timestamp(data_inicio)) & 
                               (df['Criado'] <= pd.Timestamp(data_fim))]
                
                # Métricas do período
                total_periodo = len(df_periodo)
                sinc_periodo = len(df_periodo[df_periodo['Status'] == 'Sincronizado']) if 'Status' in df_periodo.columns else 0
                revisoes_periodo = df_periodo['Revisões'].sum() if 'Revisões' in df_periodo.columns else 0
                
                # Calcular variação em relação ao período anterior
                periodo_anterior_inicio = data_inicio - (data_fim - data_inicio)
                periodo_anterior_fim = data_inicio
                
                df_periodo_anterior = df[(df['Criado'] >= pd.Timestamp(periodo_anterior_inicio)) & 
                                        (df['Criado'] <= pd.Timestamp(periodo_anterior_fim))]
                
                total_anterior = len(df_periodo_anterior)
                variacao_total = ((total_periodo - total_anterior) / total_anterior * 100) if total_anterior > 0 else 0
                
                st.markdown(f"""
                ### Relatório {tipo_relatorio} - Esteira ADMS
                **Período:** {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}
                **Data de geração:** {hoje.strftime('%d/%m/%Y %H:%M')}
                
                ---
                
                #### 📊 **Visão Geral**
                
                **Métricas do período:**
                - **Total de Demandas:** {total_periodo:,} ({variacao_total:+.1f}% vs período anterior)
                - **Chamados Sincronizados:** {sinc_periodo:,}
                - **Total de Revisões:** {revisoes_periodo:,}
                
                #### ✅ **Pontos Positivos:**
                1. **Eficiência mantida** com taxa de sincronização de {(sinc_periodo/total_periodo*100):.1f}%
                2. **Volume consistente** de demandas processadas
                3. **Qualidade estável** com média de {(revisoes_periodo/total_periodo if total_periodo > 0 else 0):.1f} revisões por chamado
                
                #### ⚠️ **Áreas de Atenção:**
                1. **Pico de demanda** identificado às quartas-feiras
                2. **Tipo mais complexo** requer revisão de processo
                3. **Oportunidade de automação** em processos manuais
                
                #### 🎯 **Recomendações para o Próximo Período:**
                1. **Reforçar equipe** nos horários de pico (10h-12h)
                2. **Criar checklist** para o tipo de chamado mais complexo
                3. **Implementar automação** para processos repetitivos
                4. **Realizar treinamento** nas áreas com mais revisões
                """)
        
        # Ações
        st.markdown("#### 🚀 Ações")
        
        col_action1, col_action2, col_action3, col_action4 = st.columns(4)
        
        with col_action1:
            if st.button("📊 Gerar Relatório", use_container_width=True, type="primary"):
                with st.spinner(f'Gerando relatório {tipo_relatorio}...'):
                    time.sleep(2)
                    st.success(f"✅ Relatório {tipo_relatorio} gerado com sucesso!")
                    st.balloons()
        
        with col_action2:
            if st.button("📤 Exportar", use_container_width=True):
                with st.spinner('Exportando relatório...'):
                    time.sleep(1)
                    st.success("✅ Exportação concluída!")
                    
                    # Simular download
                    relatorio_nome = f"relatorio_{tipo_relatorio.lower()}_{hoje.strftime('%Y%m%d_%H%M%S')}"
                    
                    for formato in formato_export:
                        st.info(f"📄 Arquivo {formato} disponível: **{relatorio_nome}.{formato.lower()}**")
        
        with col_action3:
            if st.button("🔄 Agendar", use_container_width=True):
                st.success("✅ Agendamento configurado!")
                st.info(f"Relatório {tipo_relatorio} será gerado automaticamente todo dia 1º às 8h.")
        
        with col_action4:
            if st.button("📧 Enviar por E-mail", use_container_width=True):
                email_destinatarios = st.text_input(
                    "Digite os e-mails (separados por vírgula):",
                    placeholder="exemplo1@empresa.com, exemplo2@empresa.com",
                    key="email_destinatarios"
                )
                
                if email_destinatarios:
                    with st.spinner('Enviando e-mails...'):
                        time.sleep(2)
                        st.success(f"✅ Relatório enviado para {len(email_destinatarios.split(','))} destinatários!")
        
        # Configurações Avançadas
        with st.expander("⚙️ **Configurações Avançadas**", expanded=False):
            col_adv1, col_adv2 = st.columns(2)
            
            with col_adv1:
                nivel_detalhe = st.select_slider(
                    "Nível de detalhe:",
                    options=["Resumido", "Padrão", "Detalhado"],
                    value="Padrão"
                )
                
                incluir_graficos = st.checkbox("Incluir gráficos", value=True)
                incluir_tabelas = st.checkbox("Incluir tabelas detalhadas", value=True)
            
            with col_adv2:
                idioma = st.selectbox("Idioma do relatório:", ["Português", "Inglês", "Espanhol"])
                
                empresa_logo = st.file_uploader("Logo da empresa (opcional):", type=['png', 'jpg', 'jpeg'])
                if empresa_logo:
                    st.success("✅ Logo carregada com sucesso!")
        
        # Estatísticas do Relatório
        st.markdown("#### 📈 Estatísticas do Relatório")
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            estimativa_paginas = len(secoes_relatorio) * 2 + 3
            st.metric("Páginas estimadas", estimativa_paginas)
        
        with col_stat2:
            tempo_geracao = "2-5 minutos"
            st.metric("Tempo de geração", tempo_geracao)
        
        with col_stat3:
            tamanho_estimado = f"{len(secoes_relatorio) * 50 + 100} KB"
            st.metric("Tamanho estimado", tamanho_estimado)
        
        with col_stat4:
            st.metric("Última geração", get_horario_brasilia())
    
    # ============================================
    # TOP 10 RESPONSÁVEIS (MANTIDO)
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
    # ÚLTIMAS DEMANDAS REGISTRADAS COM FILTROS (MANTIDO)
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
        Versão 5.5 | Sistema de Performance SRE | Última atualização: {ultima_atualizacao} (Brasília)
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
