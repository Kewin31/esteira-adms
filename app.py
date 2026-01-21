import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import os
import time
import warnings
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
# CSS PERSONALIZADO
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
    
    /* Botão de atualização */
    .update-button {
        background: linear-gradient(135deg, #28a745 0%, #218838 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .update-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
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

@st.cache_data
def carregar_dados(uploaded_file=None, caminho_arquivo=None):
    """Carrega e processa os dados"""
    try:
        if uploaded_file:
            content = uploaded_file.getvalue().decode('utf-8-sig')
        elif caminho_arquivo and os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        else:
            return None, "Nenhum arquivo fornecido"
        
        lines = content.split('\n')
        
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
            return None, "Formato de arquivo inválido"
        
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
        
        return df, "✅ Dados carregados com sucesso"
    
    except Exception as e:
        return None, f"Erro: {str(e)}"

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
    if 'arquivo_atual' not in st.session_state:
        st.session_state.arquivo_atual = None
    
    # UPLOAD DE ARQUIVO
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**📤 Importar Dados**")
        
        uploaded_file = st.file_uploader(
            "Selecione arquivo CSV",
            type=['csv'],
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            with st.spinner('Processando...'):
                # Salvar temporariamente
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                df_novo, status = carregar_dados(caminho_arquivo=temp_path)
                os.remove(temp_path)
                
                if df_novo is not None:
                    st.session_state.df_original = df_novo
                    st.session_state.df_filtrado = df_novo.copy()
                    st.session_state.arquivo_atual = uploaded_file.name
                    st.success("✅ Dados carregados!")
                    st.rerun()
                else:
                    st.error(f"❌ {status}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CARREGAMENTO AUTOMÁTICO DO ARQUIVO LOCAL
    if st.session_state.df_original is None:
        caminho_encontrado = encontrar_arquivo_dados()
        
        if caminho_encontrado:
            with st.spinner('Carregando dados locais...'):
                df_local, status = carregar_dados(caminho_arquivo=caminho_encontrado)
                if df_local is not None:
                    st.session_state.df_original = df_local
                    st.session_state.df_filtrado = df_local.copy()
                    st.session_state.arquivo_atual = caminho_encontrado
                    # Registrar data da última modificação
                    if os.path.exists(caminho_encontrado):
                        st.session_state.ultima_modificacao = os.path.getmtime(caminho_encontrado)
                    st.rerun()
                else:
                    st.error(f"❌ {status}")
    
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
                        options=anos_opcoes
                    )
                    if ano_selecionado != 'Todos os Anos':
                        df = df[df['Ano'] == ano_selecionado]
            
            # FILTRO POR RESPONSÁVEL
            if 'Responsável_Formatado' in df.columns:
                responsaveis = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
                responsavel_selecionado = st.selectbox(
                    "👤 Responsável",
                    options=responsaveis
                )
                if responsavel_selecionado != 'Todos':
                    df = df[df['Responsável_Formatado'] == responsavel_selecionado]
            
            # BUSCA POR CHAMADO
            busca_chamado = st.text_input(
                "🔎 Buscar Chamado",
                placeholder="Digite número do chamado..."
            )
            if busca_chamado:
                df = df[df['Chamado'].astype(str).str.contains(busca_chamado, na=False)]
            
            # FILTRO POR STATUS
            if 'Status' in df.columns:
                status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox(
                    "📊 Status",
                    options=status_opcoes
                )
                if status_selecionado != 'Todos':
                    df = df[df['Status'] == status_selecionado]
            
            # FILTRO POR TIPO
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos'] + sorted(df['Tipo_Chamado'].dropna().unique())
                tipo_selecionado = st.selectbox(
                    "📝 Tipo de Chamado",
                    options=tipos
                )
                if tipo_selecionado != 'Todos':
                    df = df[df['Tipo_Chamado'] == tipo_selecionado]
            
            # FILTRO POR EMPRESA
            if 'Empresa' in df.columns:
                empresas = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                empresa_selecionada = st.selectbox(
                    "🏢 Empresa",
                    options=empresas
                )
                if empresa_selecionada != 'Todas':
                    df = df[df['Empresa'] == empresa_selecionada]
            
            # Atualizar dados filtrados
            st.session_state.df_filtrado = df
            
            st.markdown(f"**📈 Registros filtrados:** {len(df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # CONTROLES DE ATUALIZAÇÃO (SEMPRE VISÍVEL SE HOUVER DADOS)
    if st.session_state.df_original is not None:
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**🔄 Controles de Atualização**")
            
            # Verificar se há atualização disponível
            arquivo_atual = st.session_state.arquivo_atual or encontrar_arquivo_dados()
            
            if arquivo_atual and os.path.exists(arquivo_atual):
                # Informações do arquivo
                tamanho_kb = os.path.getsize(arquivo_atual) / 1024
                ultima_mod = datetime.fromtimestamp(os.path.getmtime(arquivo_atual))
                
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem;">
                    <p style="margin: 0 0 0.3rem 0; font-weight: 600;">📄 Arquivo atual:</p>
                    <p style="margin: 0; font-size: 0.9rem; color: #495057;">{arquivo_atual}</p>
                    <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #6c757d;">
                    📏 {tamanho_kb:.1f} KB | 📅 {ultima_mod.strftime('%d/%m/%Y %H:%M')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Verificar se o arquivo foi modificado
                if verificar_atualizacao_arquivo():
                    st.warning("⚠️ O arquivo foi modificado! Clique em 'Recarregar Dados' para atualizar.")
            
            # Botões de ação
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🔄 Recarregar Dados", 
                           use_container_width=True,
                           type="primary",
                           help="Recarrega os dados do arquivo local"):
                    
                    caminho_atual = encontrar_arquivo_dados()
                    
                    if caminho_atual and os.path.exists(caminho_atual):
                        with st.spinner('Recarregando dados...'):
                            try:
                                # Limpar cache desta função
                                carregar_dados.clear()
                                
                                # Recarregar dados
                                df_atualizado, status = carregar_dados(caminho_arquivo=caminho_atual)
                                
                                if df_atualizado is not None:
                                    st.session_state.df_original = df_atualizado
                                    st.session_state.df_filtrado = df_atualizado.copy()
                                    st.session_state.arquivo_atual = caminho_atual
                                    
                                    # Atualizar timestamp da última modificação
                                    st.session_state.ultima_modificacao = os.path.getmtime(caminho_atual)
                                    
                                    st.success(f"✅ Dados atualizados! {len(df_atualizado):,} registros")
                                    st.balloons()
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Erro ao recarregar: {status}")
                            except Exception as e:
                                st.error(f"❌ Erro: {str(e)}")
                    else:
                        st.error("❌ Arquivo não encontrado. Verifique o caminho.")
            
            with col_btn2:
                if st.button("🗑️ Limpar Tudo", 
                           use_container_width=True,
                           type="secondary",
                           help="Limpa todos os dados e cache"):
                    
                    st.cache_data.clear()
                    st.session_state.clear()
                    st.success("✅ Cache e dados limpos!")
                    time.sleep(1)
                    st.rerun()
            
            # Configuração do caminho do arquivo
            with st.expander("⚙️ Configurar Caminho do Arquivo"):
                st.info("Configure o caminho do arquivo CSV para recarregamento automático")
                
                novo_caminho = st.text_input(
                    "Caminho do arquivo CSV:",
                    value=CAMINHO_ARQUIVO_PRINCIPAL,
                    help="Exemplo: data/esteira_demandas.csv"
                )
                
                if st.button("Salvar Configuração", use_container_width=True):
                    # Usar session state para armazenar o caminho configurado
                    st.session_state.caminho_configurado = novo_caminho
                    st.success("✅ Configuração salva! Reinicie o app para aplicar.")
                    
                    # Verificar se o arquivo existe
                    if os.path.exists(novo_caminho):
                        st.info(f"✅ Arquivo encontrado: {novo_caminho}")
                    else:
                        st.warning(f"⚠️ Arquivo não encontrado no caminho: {novo_caminho}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Mensagem quando não há dados
        st.info("📂 Aguardando dados...")
        
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**💡 Dicas de Uso**")
            
            st.markdown("""
            1. **Faça upload** de um arquivo CSV usando o botão acima
            2. Ou **coloque um arquivo** com um destes nomes:
               - `esteira_demandas.csv`
               - `data/esteira_demandas.csv`
               - `dados/esteira_demandas.csv`
            
            3. Após carregar, use os **filtros** para análises específicas
            4. Atualize o arquivo local e clique em **🔄 Recarregar Dados**
            """)
            st.markdown('</div>', unsafe_allow_html=True)

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
            v5.1 | Sistema de Monitoramento
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
    # INFORMAÇÕES DA BASE DE DADOS
    # ============================================
    st.markdown("## 📊 Informações da Base de Dados")
    
    if 'Criado' in df.columns and not df.empty:
        data_min = df['Criado'].min()
        data_max = df['Criado'].max()
        
        # Mostrar informações do arquivo carregado
        arquivo_info = ""
        if st.session_state.arquivo_atual:
            if isinstance(st.session_state.arquivo_atual, str):
                arquivo_info = f" | Arquivo: {st.session_state.arquivo_atual}"
        
        st.markdown(f"""
        <div class="info-base">
            <p style="margin: 0; font-weight: 600;">📅 Base atualizada em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            <p style="margin: 0.3rem 0 0 0; color: #6c757d;">
            Período coberto: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')} | 
            Total de registros: {len(df):,} | 
            Responsáveis únicos: {df['Responsável_Formatado'].nunique() if 'Responsável_Formatado' in df.columns else 0}
            {arquivo_info}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # INDICADORES PRINCIPAIS SIMPLES
    # ============================================
    st.markdown("## 📈 INDICADORES PRINCIPAIS")
    
    col1, col2, col3, col4 = st.columns(4)
    
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
        if 'Tipo_Chamado' in df.columns:
            correcoes = len(df[df['Tipo_Chamado'].str.contains('Correção|Ajuste', case=False, na=False)])
            st.markdown(criar_card_indicador_simples(
                correcoes,
                "Correções/Ajustes",
                "🔧"
            ), unsafe_allow_html=True)
    
    with col4:
        if 'Revisões' in df.columns:
            total_revisoes = int(df['Revisões'].sum())
            st.markdown(criar_card_indicador_simples(
                total_revisoes,
                "Total de Revisões",
                "📝"
            ), unsafe_allow_html=True)
    
    # ============================================
    # ABAS PARA DIFERENTES VISUALIZAÇÕES
    # ============================================
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📅 Evolução de Demandas", "📊 Análise de Revisões", "📈 Sincronizados por Dia"])
    
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
                # Ordem dos meses completos
                ordem_meses_completa = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                                       'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
                
                ordem_meses_abreviados = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                                         'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                
                # Criar dataframe com todos os meses do ano
                todos_meses = pd.DataFrame({
                    'Mês_Num': range(1, 13),
                    'Nome_Mês_Completo': ordem_meses_completa,
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
                    st.metric("📈 Mês com mais demandas", f"{mes_max['Nome_Mês_Completo']}: {int(mes_max['Quantidade']):,}")
                
                with col_stats2:
                    mes_min = demandas_completas.loc[demandas_completas['Quantidade'].idxmin()]
                    st.metric("📉 Mês com menos demandas", f"{mes_min['Nome_Mês_Completo']}: {int(mes_min['Quantidade']):,}")
                
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
                    x=revisoes_por_responsavel['Responsável'].head(15),  # Top 15
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
                
                # Gráfico de dispersão: Revisões vs Chamados
                col_disp1, col_disp2 = st.columns(2)
                
                with col_disp1:
                    fig_dispersao = px.scatter(
                        revisoes_por_responsavel.head(20),
                        x='Chamados_Com_Revisão',
                        y='Total_Revisões',
                        size='Total_Revisões',
                        color='Total_Revisões',
                        hover_name='Responsável',
                        title='Relação: Chamados vs Revisões',
                        labels={'Chamados_Com_Revisão': 'Chamados com Revisão', 'Total_Revisões': 'Total de Revisões'},
                        color_continuous_scale='Reds'
                    )
                    
                    fig_dispersao.update_layout(
                        height=400,
                        plot_bgcolor='white'
                    )
                    
                    st.plotly_chart(fig_dispersao, use_container_width=True)
                
                with col_disp2:
                    # Métricas principais
                    st.markdown("### 📊 Estatísticas de Revisões")
                    
                    col_met1, col_met2 = st.columns(2)
                    
                    with col_met1:
                        total_revisoes_geral = int(df_com_revisoes['Revisões'].sum())
                        st.metric("Total de revisões", f"{total_revisoes_geral:,}")
                    
                    with col_met2:
                        media_revisoes = df_com_revisoes['Revisões'].mean()
                        st.metric("Média por chamado", f"{media_revisoes:.1f}")
                    
                    # Responsável com mais revisões
                    if not revisoes_por_responsavel.empty:
                        responsavel_top = revisoes_por_responsavel.iloc[0]
                        st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                            <h4 style="color: #dc3545; margin: 0 0 0.5rem 0;">⚠️ Maior número de revisões</h4>
                            <p style="margin: 0;"><strong>{responsavel_top['Responsável']}</strong></p>
                            <p style="margin: 0.3rem 0 0 0; color: #6c757d;">
                            {responsavel_top['Total_Revisões']:,} revisões em {responsavel_top['Chamados_Com_Revisão']} chamados
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("✅ Nenhuma revisão registrada na base de dados atual.")
    
    # NOVA ABA: Chamados Sincronizados por Dia
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
                
                # Estatísticas
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                
                with col_stat1:
                    total_sincronizados = sincronizados_por_dia['Quantidade'].sum()
                    st.metric("Total Sincronizados", f"{total_sincronizados:,}")
                
                with col_stat2:
                    media_diaria = sincronizados_por_dia['Quantidade'].mean()
                    st.metric("Média Diária", f"{media_diaria:.1f}")
                
                with col_stat3:
                    max_dia = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmax()]
                    st.metric("Dia com Mais", f"{max_dia['Data'].strftime('%d/%m')}: {int(max_dia['Quantidade'])}")
                
                with col_stat4:
                    min_dia = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmin()]
                    st.metric("Dia com Menos", f"{min_dia['Data'].strftime('%d/%m')}: {int(min_dia['Quantidade'])}")
                
                # Gráfico de calor (calendário) - opcional
                st.markdown("### 📅 Visualização por Calendário")
                
                # Preparar dados para heatmap
                df_sincronizados['Ano'] = df_sincronizados['Criado'].dt.year
                df_sincronizados['Mês'] = df_sincronizados['Criado'].dt.month
                df_sincronizados['Dia_do_Mes'] = df_sincronizados['Criado'].dt.day
                df_sincronizados['Dia_da_Semana'] = df_sincronizados['Criado'].dt.dayofweek
                
                # Agrupar por mês e dia
                heatmap_data = df_sincronizados.groupby(['Ano', 'Mês', 'Dia_do_Mes']).size().reset_index()
                heatmap_data.columns = ['Ano', 'Mês', 'Dia', 'Quantidade']
                
                # Criar pivot table para heatmap
                pivot_data = heatmap_data.pivot_table(
                    index='Dia',
                    columns='Mês',
                    values='Quantidade',
                    aggfunc='sum',
                    fill_value=0
                )
                
                # Nomes dos meses
                meses_nomes = {
                    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
                    5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
                    9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
                }
                
                # Renomear colunas
                pivot_data = pivot_data.rename(columns=meses_nomes)
                
                # Criar heatmap
                fig_heatmap = px.imshow(
                    pivot_data,
                    labels=dict(x="Mês", y="Dia do Mês", color="Chamados Sincronizados"),
                    color_continuous_scale='Greens',
                    title="Distribuição de Chamados Sincronizados por Dia e Mês"
                )
                
                fig_heatmap.update_layout(
                    height=400,
                    margin=dict(t=50, b=50, l=50, r=50)
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
            else:
                st.info("ℹ️ Nenhum chamado sincronizado encontrado nos dados atuais.")
        else:
            st.warning("⚠️ Colunas necessárias (Status, Criado) não encontradas nos dados.")
    
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
    st.markdown('<div class="section-title-exec">🕒 ÚLTIMAS DEMANDAS REGISTRADAS</div>', unsafe_allow_html=True)
    
    if 'Criado' in df.columns:
        # Filtros para a tabela
        col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
        
        with col_filtro1:
            qtd_demandas = st.slider(
                "Número de demandas:",
                min_value=5,
                max_value=50,
                value=15,
                step=5
            )
        
        with col_filtro2:
            ordenar_por = st.selectbox(
                "Ordenar por:",
                options=['Data (Mais Recente)', 'Data (Mais Antiga)', 'Revisões (Maior)', 'Revisões (Menor)']
            )
        
        with col_filtro3:
            mostrar_colunas = st.multiselect(
                "Colunas a mostrar:",
                options=['Chamado', 'Tipo_Chamado', 'Responsável', 'Status', 'Prioridade', 'Revisões', 'Empresa', 'Data'],
                default=['Chamado', 'Tipo_Chamado', 'Responsável', 'Status', 'Data']
            )
        
        with col_filtro4:
            # Filtro de busca por chamado específico
            filtro_chamado_tabela = st.text_input(
                "Filtrar por chamado:",
                placeholder="Ex: 12345"
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
                use_container_width=True
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
            <p>2. <strong>Ou coloque um arquivo CSV</strong> no mesmo diretório do app</p>
            <p>3. <strong>Após atualizar o arquivo</strong>, clique em "🔄 Recarregar Dados" na barra lateral</p>
            <p>4. <strong>Use os filtros</strong> para análises específicas</p>
        </div>
        
        <div style="margin-top: 2rem; color: #6c757d; font-size: 0.9rem;">
            <p>📁 Nomes de arquivo reconhecidos automaticamente:</p>
            <p style="font-family: monospace; background: #e9ecef; padding: 0.5rem; border-radius: 5px; display: inline-block;">
            esteira_demandas.csv | data/esteira_demandas.csv | dados/esteira_demandas.csv
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# RODAPÉ COMPLETO
# ============================================
st.markdown("---")

st.markdown("""
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
        Versão 5.1 | SRE Monitoring Platform | Recarregamento Automático
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
