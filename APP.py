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
# CSS PERSONALIZADO OTIMIZADO
# ============================================
st.markdown("""
<style>
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
    
    .info-base {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e3799;
        margin-bottom: 1.5rem;
    }
    
    .footer-exec {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 2px solid #e9ecef;
        color: #6c757d;
        font-size: 0.9rem;
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
# FUNÇÕES AUXILIARES OTIMIZADAS
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

def filtrar_kewin_dos_dados(df):
    """Remove Kewin dos dados de análise de desenvolvedores"""
    if 'Responsável_Formatado' in df.columns:
        kw_patterns = ['kewin', 'Kewin', 'KEWIN', 'Kewin Marcel', 'kewin.ferreira', 'Kewin Ferreira']
        mask = ~df['Responsável_Formatado'].astype(str).str.lower().apply(
            lambda x: any(pattern.lower() in str(x).lower() for pattern in kw_patterns)
        )
        return df[mask].copy()
    return df.copy()

def criar_card_indicador_simples(valor, label, icone="📊"):
    """Cria card de indicador SIMPLES - sem delta"""
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
        
        return df, "✅ Dados carregados com sucesso", hash_conteudo
    
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

def substituir_nome_sre(sre_nome):
    """Substitui e-mails por nomes corretos dos SREs"""
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
        return str(sre_nome).title()

@st.cache_data
def criar_matriz_performance_dev(df):
    """Cria matriz de performance (Eficiência vs Qualidade) para Desenvolvedores"""
    df_filtrado = filtrar_kewin_dos_dados(df)
    
    devs = df_filtrado['Responsável_Formatado'].dropna().unique()
    matriz_data = []
    
    for dev in devs:
        df_dev = df_filtrado[df_filtrado['Responsável_Formatado'] == dev].copy()
        
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
        
        score = (qualidade * 0.5) + (eficiencia * 5 * 0.3) + ((total_cards / max(len(df_filtrado), 1)) * 100 * 0.2)
        
        matriz_data.append({
            'Desenvolvedor': dev,
            'Eficiencia': round(eficiencia, 1),
            'Qualidade': round(qualidade, 1),
            'Score': round(score, 1),
            'Total_Cards': total_cards
        })
    
    return pd.DataFrame(matriz_data)

# ============================================
# SIDEBAR - FILTROS E CONTROLES
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h3 style="color: #1e3799; margin: 0;">⚙️ Painel de Controle</h3>
        <p style="color: #6c757d; margin: 0; font-size: 0.9rem;">Filtros e Configurações</p>
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
                meses_disponiveis = sorted(df['Mês'].dropna().unique().astize(int))
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
                responsaveis_todos = sorted(df['Responsável_Formatado'].dropna().unique())
                responsaveis_filtrados = [
                    resp for resp in responsaveis_todos 
                    if not any(kw in str(resp).lower() for kw in ['kewin', 'kewin marcel', 'kewin.ferreira'])
                ]
                responsaveis = ['Todos'] + responsaveis_filtrados
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
                # Primeiro aplicamos a substituição de nomes aos SREs
                sres_originais = sorted(df['SRE'].dropna().unique())
                sres_formatados = [substituir_nome_sre(sre) for sre in sres_originais]
                
                # Criamos um dicionário de mapeamento
                sre_mapping = dict(zip(sres_originais, sres_formatados))
                
                sres = ['Todos'] + sorted(list(set(sres_formatados)))  # Remover duplicados
                sre_selecionado = st.selectbox(
                    "🔧 SRE Responsável",
                    options=sres,
                    key="filtro_sre"
                )
                if sre_selecionado != 'Todos':
                    # Encontrar os SREs originais que correspondem ao nome formatado selecionado
                    sres_correspondentes = [sre_orig for sre_orig, sre_fmt in sre_mapping.items() if sre_fmt == sre_selecionado]
                    df = df[df['SRE'].isin(sres_correspondentes)]
            
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
                <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem;">
                    <p style="margin: 0 0 0.3rem 0; font-weight: 600;">📄 Arquivo atual:</p>
                    <p style="margin: 0; font-size: 0.9rem; color: #495057;">{os.path.basename(arquivo_atual)}</p>
                    <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #6c757d;">
                    📏 {tamanho_kb:.1f} KB | 📅 {ultima_mod.strftime('%d/%m/%Y %H:%M')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if verificar_atualizacao_arquivo():
                    st.warning("⚠️ O arquivo local foi modificado!")
            
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
        
        if uploaded_file is not None:
            current_hash = calcular_hash_arquivo(uploaded_file.getvalue())
            
            if ('file_hash' not in st.session_state or 
                current_hash != st.session_state.file_hash or
                uploaded_file.name != st.session_state.uploaded_file_name):
                
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
                        st.rerun()
                    else:
                        st.error(f"❌ {status}")
            else:
                st.info("ℹ️ Este arquivo já está carregado.")
        
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
# CONTEÚDO PRINCIPAL
# ============================================
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

if st.session_state.df_original is not None:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
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
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Evolução de Demandas", 
        "📊 Análise de Revisões", 
        "📈 Sincronizados por Dia",
        "🏆 Performance dos SREs"
    ])
    
    with tab1:
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
        
        col_rev_filtro1, col_rev_filtro2 = st.columns(2)
        
        with col_rev_filtro1:
            if 'Ano' in df.columns:
                anos_rev = sorted(df['Ano'].dropna().unique().astize(int))
                anos_opcoes_rev = ['Todos os Anos'] + list(anos_rev)
                ano_rev = st.selectbox(
                    "📅 Filtrar por Ano:",
                    options=anos_opcoes_rev,
                    key="filtro_ano_revisoes"
                )
        
        with col_rev_filtro2:
            if 'Mês' in df.columns:
                meses_rev = sorted(df['Mês'].dropna().unique().astize(int))
                meses_opcoes_rev = ['Todos os Meses'] + [str(m) for m in meses_rev]
                mes_rev = st.selectbox(
                    "📆 Filtrar por Mês:",
                    options=meses_opcoes_rev,
                    key="filtro_mes_revisoes"
                )
        
        df_rev = df.copy()
        
        if ano_rev != 'Todos os Anos':
            df_rev = df_rev[df_rev['Ano'] == int(ano_rev)]
        
        if mes_rev != 'Todos os Meses':
            df_rev = df_rev[df_rev['Mês'] == int(mes_rev)]
        
        if 'Revisões' in df_rev.columns and 'Responsável_Formatado' in df_rev.columns:
            df_com_revisoes = df_rev[df_rev['Revisões'] > 0].copy()
            
            if not df_com_revisoes.empty:
                revisoes_por_responsavel = df_com_revisoes.groupby('Responsável_Formatado').agg({
                    'Revisões': 'sum',
                    'Chamado': 'count'
                }).reset_index()
                
                revisoes_por_responsavel.columns = ['Responsável', 'Total_Revisões', 'Chamados_Com_Revisão']
                revisoes_por_responsavel = revisoes_por_responsavel.sort_values('Total_Revisões', ascending=False)
                
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
                
                fig_revisoes = go.Figure()
                
                max_revisoes = revisoes_por_responsavel['Total_Revisões'].max()
                min_revisoes = revisoes_por_responsavel['Total_Revisões'].min()
                
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
        st.markdown('<div class="section-title_exec">📈 CHAMADOS SINCRONIZADOS POR DIA</div>', unsafe_allow_html=True)
        
        col_sinc_filtro1, col_sinc_filtro2 = st.columns(2)
        
        with col_sinc_filtro1:
            if 'Ano' in df.columns:
                anos_sinc = sorted(df['Ano'].dropna().unique().astize(int))
                anos_opcoes_sinc = ['Todos os Anos'] + list(anos_sinc)
                ano_sinc = st.selectbox(
                    "📅 Filtrar por Ano:",
                    options=anos_opcoes_sinc,
                    key="filtro_ano_sinc"
                )
        
        with col_sinc_filtro2:
            if 'Mês' in df.columns:
                meses_sinc = sorted(df['Mês'].dropna().unique().astize(int))
                meses_opcoes_sinc = ['Todos os Meses'] + [str(m) for m in meses_sinc]
                mes_sinc = st.selectbox(
                    "📆 Filtrar por Mês:",
                    options=meses_opcoes_sinc,
                    key="filtro_mes_sinc"
                )
        
        df_sinc = df.copy()
        
        if ano_sinc != 'Todos os Anos':
            df_sinc = df_sinc[df_sinc['Ano'] == int(ano_sinc)]
        
        if mes_sinc != 'Todos os Meses':
            df_sinc = df_sinc[df_sinc['Mês'] == int(mes_sinc)]
        
        if 'Status' in df_sinc.columns and 'Criado' in df_sinc.columns:
            df_sincronizados = df_sinc[df_sinc['Status'] == 'Sincronizado'].copy()
            
            if not df_sincronizados.empty:
                df_sincronizados['Data'] = df_sincronizados['Criado'].dt.date
                
                sincronizados_por_dia = df_sincronizados.groupby('Data').size().reset_index()
                sincronizados_por_dia.columns = ['Data', 'Quantidade']
                sincronizados_por_dia = sincronizados_por_dia.sort_values('Data')
                
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
            col_filtro1, col_filtro2 = st.columns(2)
            
            with col_filtro1:
                if 'Ano' in df.columns:
                    anos_sre = sorted(df['Ano'].dropna().unique().astize(int))
                    anos_opcoes_sre = ['Todos'] + list(anos_sre)
                    ano_sre = st.selectbox(
                        "📅 Filtrar por Ano:",
                        options=anos_opcoes_sre,
                        key="filtro_ano_sre"
                    )
            
            with col_filtro2:
                if 'Mês' in df.columns:
                    meses_sre = sorted(df['Mês'].dropna().unique().astize(int))
                    meses_opcoes_sre = ['Todos'] + [str(m) for m in meses_sre]
                    mes_sre = st.selectbox(
                        "📆 Filtrar por Mês:",
                        options=meses_opcoes_sre,
                        key="filtro_mes_sre"
                    )
            
            df_sre = df.copy()
            
            if 'Ano' in df_sre.columns and ano_sre != 'Todos':
                df_sre = df_sre[df_sre['Ano'] == int(ano_sre)]
            
            if 'Mês' in df_sre.columns and mes_sre != 'Todos':
                df_sre = df_sre[df_sre['Mês'] == int(mes_sre)]
            
            # CRIAÇÃO DE UMA CÓPIA COM OS NOMES DOS SREs FORMATADOS
            df_sre_display = df_sre.copy()
            df_sre_display['SRE_Formatado'] = df_sre_display['SRE'].apply(substituir_nome_sre)
            
            # REMOVER "NÃO INFORMADO" ANTES DE QUALQUER ANÁLISE
            df_sre_display = df_sre_display[df_sre_display['SRE_Formatado'] != 'Não informado']
            
            # Filtrar apenas chamados sincronizados para análise SRE
            df_sincronizados = df_sre_display[df_sre_display['Status'] == 'Sincronizado'].copy()
            
            # IDENTIFICAR QUAIS SREs TÊM PELO MENOS UM CARD SINCRONIZADO
            sres_com_sincronizados = df_sincronizados['SRE_Formatado'].dropna().unique()
            
            if not df_sincronizados.empty and 'SRE_Formatado' in df_sincronizados.columns and len(sres_com_sincronizados) > 0:
                # ============================================
                # 1. SINCRONIZADOS POR SRE (GRÁFICO DE BARRAS)
                # ============================================
                st.markdown("### 📈 Sincronizados por SRE")
                
                # Calcular sincronizados por SRE (usando nomes formatados)
                sinc_por_sre = df_sincronizados.groupby('SRE_Formatado').size().reset_index()
                sinc_por_sre.columns = ['SRE', 'Sincronizados']
                sinc_por_sre = sinc_por_sre.sort_values('Sincronizados', ascending=False)
                
                # Criar gráfico de barras com nomes formatados
                fig_sinc_bar = go.Figure()
                
                # Cores do maior para o menor (azul escuro para azul claro)
                max_sinc = sinc_por_sre['Sincronizados'].max()
                min_sinc = sinc_por_sre['Sincronizados'].min()
                
                colors = []
                for valor in sinc_por_sre['Sincronizados']:
                    if max_sinc == min_sinc:
                        colors.append('#1e3799')
                    else:
                        normalized = (valor - min_sinc) / (max_sinc - min_sinc)
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
                
                # Top 3 SREs - COM NOMES CORRETOS
                col_top1, col_top2, col_top3 = st.columns(3)
                
                if len(sinc_por_sre) >= 1:
                    with col_top1:
                        sre1 = sinc_por_sre.iloc[0]
                        st.metric("🥇 1º Lugar Sincronizados", 
                                 f"{sre1['SRE']}", 
                                 f"{sre1['Sincronizados']} sinc.")
                
                if len(sinc_por_sre) >= 2:
                    with col_top2:
                        sre2 = sinc_por_sre.iloc[1]
                        st.metric("🥈 2º Lugar Sincronizados", 
                                 f"{sre2['SRE']}", 
                                 f"{sre2['Sincronizados']} sinc.")
                
                if len(sinc_por_sre) >= 3:
                    with col_top3:
                        sre3 = sinc_por_sre.iloc[2]
                        st.metric("🥉 3º Lugar Sincronizados", 
                                 f"{sre3['SRE']}", 
                                 f"{sre3['Sincronizados']} sinc.")
                
                # Tabela completa - APENAS SREs QUE TÊM CARDS SINCRONIZADOS
                st.markdown("### 📋 Performance Detalhada dos SREs")
                
                # Calcular métricas adicionais usando nomes formatados
                sres_metrics = []
                
                # USAR APENAS SREs QUE TÊM CARDS SINCRONIZADOS
                for sre_nome in sres_com_sincronizados:
                    # Filtrar apenas os cards deste SRE (incluindo não sincronizados)
                    df_sre_data = df_sre_display[df_sre_display['SRE_Formatado'] == sre_nome].copy()
                    
                    if len(df_sre_data) > 0:
                        total_cards = len(df_sre_data)
                        sincronizados = len(df_sre_data[df_sre_data['Status'] == 'Sincronizado'])
                        
                        # Cards que retornaram (revisões > 0)
                        if 'Revisões' in df_sre_data.columns:
                            cards_retorno = len(df_sre_data[df_sre_data['Revisões'] > 0])
                        else:
                            cards_retorno = 0
                        
                        sres_metrics.append({
                            'SRE': sre_nome,
                            'Total_Cards': total_cards,
                            'Sincronizados': sincronizados,
                            'Cards_Retorno': cards_retorno
                        })

                if sres_metrics:
                    df_sres_metrics = pd.DataFrame(sres_metrics)
                    
                    # Agrupar por nome (caso haja múltiplos e-mails para a mesma pessoa)
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
                else:
                    st.info("Nenhum SRE com cards sincronizados encontrado para análise.")
            else:
                st.info("Nenhum SRE com cards sincronizados encontrado para análise.")
    
    # ============================================
    # ANÁLISES AVANÇADAS
    # ============================================
    st.markdown("---")
    st.markdown('<div class="section-title-exec">🔍 ANÁLISES AVANÇADAS</div>', unsafe_allow_html=True)
    
    tab_extra1, tab_extra2, tab_extra3 = st.tabs([
        "🚀 Performance de Desenvolvedores",
        "📈 Análise de Sazonalidade", 
        "⚡ Diagnóstico de Erros"
    ])
    
    with tab_extra1:
        if 'Responsável_Formatado' in df.columns and 'Revisões' in df.columns and 'Status' in df.columns:
            col_filtro_perf1, col_filtro_perf2, col_filtro_perf3 = st.columns(3)
            
            with col_filtro_perf1:
                if 'Ano' in df.columns:
                    anos_perf = sorted(df['Ano'].dropna().unique().astize(int))
                    anos_opcoes_perf = ['Todos os Anos'] + list(anos_perf)
                    ano_perf = st.selectbox(
                        "📅 Filtrar por Ano:",
                        options=anos_opcoes_perf,
                        key="filtro_ano_perf"
                    )
            
            with col_filtro_perf2:
                if 'Mês' in df.columns:
                    meses_perf = sorted(df['Mês'].dropna().unique().astize(int))
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
            
            df_perf = df.copy()
            
            if ano_perf != 'Todos os Anos':
                df_perf = df_perf[df_perf['Ano'] == int(ano_perf)]
            
            if mes_perf != 'Todos os Meses':
                df_perf = df_perf[df_perf['Mês'] == int(mes_perf)]
            
            # REMOVER KEWIN DOS DADOS DE PERFORMANCE
            df_perf = filtrar_kewin_dos_dados(df_perf)
            
            # Calcular métricas por desenvolvedor
            dev_metrics = []
            devs = df_perf['Responsável_Formatado'].unique()
            
            for dev in devs:
                dev_data = df_perf[df_perf['Responsável_Formatado'] == dev]
                total_chamados = len(dev_data)
                
                if total_chamados > 0:
                    sem_revisao = len(dev_data[dev_data['Revisões'] == 0])
                    score_qualidade = (sem_revisao / total_chamados * 100) if total_chamados > 0 else 0
                    
                    sincronizados = len(dev_data[dev_data['Status'] == 'Sincronizado'])
                    eficiencia = (sincronizados / total_chamados * 100) if total_chamados > 0 else 0
                    
                    if 'Criado' in dev_data.columns:
                        meses_ativos = dev_data['Criado'].dt.to_period('M').nunique()
                        produtividade = total_chamados / meses_ativos if meses_ativos > 0 else 0
                    else:
                        produtividade = 0
                    
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
                df_dev_metrics = pd.DataFrame(dev_metrics)
                
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
                
                matriz_df = criar_matriz_performance_dev(df_perf)
                
                if not matriz_df.empty:
                    matriz_filtrada = matriz_df.copy()
                    
                    if not matriz_filtrada.empty:
                        media_eficiencia = matriz_filtrada['Eficiencia'].mean()
                        media_qualidade = matriz_filtrada['Qualidade'].mean()
                        
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
                        matriz_filtrada = matriz_filtrada.sort_values('Qualidade', ascending=False)
                        
                        num_devs = len(matriz_filtrada)
                        colors_scatter = []
                        for i in range(num_devs):
                            pos_normalizada = i / max(num_devs - 1, 1)
                            red = int(220 * pos_normalizada + 40 * (1 - pos_normalizada))
                            green = int(53 * pos_normalizada + 167 * (1 - pos_normalizada))
                            blue = int(69 * pos_normalizada + 69 * (1 - pos_normalizada))
                            colors_scatter.append(f'rgb({red}, {green}, {blue})')
                        
                        fig_matriz = px.scatter(
                            matriz_filtrada,
                            x='Eficiencia',
                            y='Qualidade',
                            size='Score',
                            color=colors_scatter,
                            hover_name='Desenvolvedor',
                            title='Matriz de Performance: Eficiência vs Qualidade',
                            labels={
                                'Eficiencia': 'Eficiência (Cards/Mês)',
                                'Qualidade': 'Qualidade (% Aprovação sem Revisão)',
                                'Score': 'Score Performance'
                            },
                            size_max=30
                        )
                        
                        fig_matriz.update_traces(showlegend=False)
                        
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
                
                # Mostrar top 10
                st.markdown(f"### 🏆 Top 10 Desenvolvedores ({ordenar_por})")
                
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
                    
                else:
                    top10_other = df_dev_metrics.head(10)
                    
                    if ordenar_por == "Total de Chamados":
                        col_ordenada = 'Total Chamados'
                        color_scale = 'Blues'
                        titulo = 'Top 10 - Total de Chamados'
                    elif ordenar_por == "Eficiência":
                        col_ordenada = 'Eficiência'
                        color_scale = 'Greens'
                        titulo = 'Top 10 - Eficiência'
                    else:
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
    
    with tab_extra2:
        if 'Criado' in df.columns and 'Status' in df.columns:
            col_saz_filtro1, col_saz_filtro2, col_saz_filtro3 = st.columns(3)
            
            with col_saz_filtro1:
                anos_saz = sorted(df['Ano'].dropna().unique().astize(int))
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
            
            df_saz = df.copy()
            
            if ano_saz != 'Todos os Anos':
                df_saz = df_saz[df_saz['Ano'] == int(ano_saz)]
            
            if mes_saz != 'Todos os Meses':
                df_saz = df_saz[df_saz['Mês'] == int(mes_saz)]
    
    with tab_extra3:
        if 'Tipo_Chamado' in df.columns:
            col_diag1, col_diag2, col_diag3 = st.columns(3)
            
            with col_diag1:
                anos_diag = sorted(df['Ano'].dropna().unique().astize(int))
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
    
    # ============================================
    # TOP 10 RESPONSÁVEIS
    # ============================================
    st.markdown("---")
    col_top, col_dist = st.columns([2, 1])
    
    with col_top:
        st.markdown('<div class="section-title-exec">👥 TOP 10 RESPONSÁVEIS</div>', unsafe_allow_html=True)
        
        if 'Responsável_Formatado' in df.columns:
            # Filtrar Kewin do top 10
            df_top = filtrar_kewin_dos_dados(df)
            
            top_responsaveis = df_top['Responsável_Formatado'].value_counts().head(10).reset_index()
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

# ============================================
# RODAPÉ COM HORÁRIO DE ATUALIZAÇÃO
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
        Versão 5.5 | Sistema de Performance SRE | Última atualização: {ultima_atualizacao} (Brasília)
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
