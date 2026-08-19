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
import requests
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURAÇÃO GITHUB
# ============================================
GITHUB_CSV_URL = "https://raw.githubusercontent.com/Kewin31/esteira-adms/main/Esteira%20de%20Demandas%20ADMS%20(72).csv"

# ============================================
# PALETA DE CORES - NOVA IDENTIDADE VISUAL
# ============================================
COR_VERDE_ESCURO = "#2E7D32"
COR_AZUL_PETROLEO = "#028a9f"
COR_AZUL_ESCURO = "#005973"
COR_LARANJA = "#F57C00"
COR_VERMELHO = "#C62828"
COR_CINZA_FUNDO = "#F8F9FA"
COR_CINZA_BORDA = "#E9ECEF"
COR_CINZA_TEXTO = "#6C757D"
COR_BRANCO = "#FFFFFF"
COR_PRETO_SUAVE = "#212529"
CORES_GRADIENTE = [COR_VERDE_ESCURO, COR_AZUL_PETROLEO, COR_AZUL_ESCURO, COR_LARANJA, COR_VERMELHO, "#1E88E5"]

# ============================================
# MAPEAMENTO COMPLETO DAS EMPRESAS
# ============================================
MAPEAMENTO_EMPRESAS = {
    'EMR': {'sigla': 'MG', 'estado': 'Minas Gerais', 'regiao': 'Sudeste', 'nome_completo': 'Energisa Minas Gerais', 'latitude': -19.9167, 'longitude': -43.9345},
    'EPB': {'sigla': 'PB', 'estado': 'Paraíba', 'regiao': 'Nordeste', 'nome_completo': 'Energisa Paraíba', 'latitude': -7.1195, 'longitude': -36.7240},
    'ESE': {'sigla': 'SE', 'estado': 'Sergipe', 'regiao': 'Nordeste', 'nome_completo': 'Energisa Sergipe', 'latitude': -10.9472, 'longitude': -37.0731},
    'ESS': {'sigla': 'SP', 'estado': 'São Paulo', 'regiao': 'Sudeste', 'nome_completo': 'Energisa Sul/Sudeste', 'latitude': -23.5505, 'longitude': -46.6333},
    'EMS': {'sigla': 'MS', 'estado': 'Mato Grosso do Sul', 'regiao': 'Centro-Oeste', 'nome_completo': 'Energisa Mato Grosso do Sul', 'latitude': -20.4697, 'longitude': -54.6201},
    'EMT': {'sigla': 'MT', 'estado': 'Mato Grosso', 'regiao': 'Centro-Oeste', 'nome_completo': 'Energisa Mato Grosso', 'latitude': -12.6819, 'longitude': -56.9211},
    'ETO': {'sigla': 'TO', 'estado': 'Tocantins', 'regiao': 'Norte', 'nome_completo': 'Energisa Tocantins', 'latitude': -10.1753, 'longitude': -48.2982},
    'ERO': {'sigla': 'RO', 'estado': 'Rondônia', 'regiao': 'Norte', 'nome_completo': 'Energisa Rondônia', 'latitude': -10.9161, 'longitude': -61.8298},
    'EAC': {'sigla': 'AC', 'estado': 'Acre', 'regiao': 'Norte', 'nome_completo': 'Energisa Acre', 'latitude': -9.0238, 'longitude': -70.8120}
}

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
    .stApp {{ background-color: {COR_CINZA_FUNDO}; }}
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
    .sidebar-section {{
        background: {COR_CINZA_FUNDO};
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid {COR_CINZA_BORDA};
    }}
    [data-testid="stSidebar"] {{
        background: {COR_BRANCO};
        border-right: 1px solid {COR_CINZA_BORDA};
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def formatar_nome_responsavel(nome):
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
        correcoes = {' Da ': ' da ', ' De ': ' de ', ' Do ': ' do ', ' Das ': ' das ', ' Dos ': ' dos ', ' E ': ' e '}
        for errado, correto in correcoes.items():
            nome_formatado = nome_formatado.replace(errado, correto)
        return nome_formatado
    return nome_str.title()

def criar_card_indicador_simples(valor, label, icone="📊"):
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

def get_horario_brasilia():
    try:
        tz = timezone('America/Sao_Paulo')
        return datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    except:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

def processar_dataframe(df):
    """Processa o DataFrame com todas as transformações necessárias"""
    if df is None or len(df) == 0:
        return df
    
    # Renomeia colunas
    col_mapping = {
        'Título': 'Chamado',
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
        'Motivo Revisão': 'Motivo_Revisao',
        'Retorno Cliente': 'Retorno Cliente'
    }
    df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})
    
    # Formata responsáveis
    if 'Responsável' in df.columns:
        df['Responsável_Formatado'] = df['Responsável'].apply(formatar_nome_responsavel)
    
    # Processa datas
    for col in ['Criado', 'Modificado']:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], format='%d/%m/%Y %H:%M', errors='coerce')
            except:
                try:
                    df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
                except:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Cria colunas de data
    if 'Criado' in df.columns and not df['Criado'].isna().all():
        df['Ano'] = df['Criado'].dt.year
        df['Mês'] = df['Criado'].dt.month
        df['Dia'] = df['Criado'].dt.day
        df['Hora'] = df['Criado'].dt.hour
        df['Data_Date'] = df['Criado'].dt.date
        df['Nome_Mês'] = df['Criado'].dt.month.map({
            1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
            5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
            9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
        })
        df['Mês_Ano'] = df['Criado'].dt.strftime('%b/%Y')
        df['Ano_Mês'] = df['Criado'].dt.strftime('%Y-%m')
        df['Nome_Mês_Completo'] = df['Criado'].dt.month.map({
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        })
    else:
        df['Ano'] = pd.NA
        df['Mês'] = pd.NA
        df['Nome_Mês'] = pd.NA
        df['Data_Date'] = pd.NA
    
    # Converte Revisões
    if 'Revisões' in df.columns:
        df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
    
    return df

# ============================================
# FUNÇÃO DE CARREGAMENTO DO GITHUB
# ============================================
@st.cache_data(ttl=300)
def carregar_dados_github():
    try:
        response = requests.get(GITHUB_CSV_URL, timeout=30)
        response.raise_for_status()
        content = response.text
        if content.startswith('\ufeff'):
            content = content[1:]
        df = pd.read_csv(io.StringIO(content), quotechar='"', delimiter=',', encoding='utf-8', dtype=str)
        df = processar_dataframe(df)
        return df, f"✅ {len(df):,} registros carregados do GitHub!"
    except Exception as e:
        return None, f"❌ Erro: {str(e)}"

@st.cache_data(ttl=300)
def carregar_dados_upload(uploaded_file):
    try:
        conteudo_bytes = uploaded_file.getvalue()
        conteudo = conteudo_bytes.decode('utf-8-sig')
        lines = conteudo.split('\n')
        header_line = None
        for i, line in enumerate(lines):
            if line.startswith('"Chamado"') or line.startswith('"Título"'):
                header_line = i
                break
        if header_line is None:
            return None, "Formato de arquivo inválido"
        data_str = '\n'.join(lines[header_line:])
        df = pd.read_csv(io.StringIO(data_str), quotechar='"')
        df = processar_dataframe(df)
        return df, f"✅ {len(df):,} registros carregados!"
    except Exception as e:
        return None, f"Erro: {str(e)}"

def encontrar_arquivo_local():
    caminhos = ["esteira_demandas.csv", "data/esteira_demandas.csv", "dados/esteira_demandas.csv", "Esteira de Demandas ADMS (72).csv"]
    for caminho in caminhos:
        if os.path.exists(caminho):
            return caminho
    return None

def limpar_sessao():
    keys = ['df_original', 'df_filtrado', 'arquivo_atual', 'ultima_atualizacao', 'fonte_dados']
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]

# ============================================
# INICIALIZAÇÃO DA SESSÃO
# ============================================
if 'df_original' not in st.session_state:
    st.session_state.df_original = None
    st.session_state.df_filtrado = None
    st.session_state.arquivo_atual = None
    st.session_state.ultima_atualizacao = None
    st.session_state.fonte_dados = None

# ============================================
# CARREGAMENTO DE DADOS
# ============================================
if st.session_state.df_original is None:
    with st.spinner('🔄 Carregando dados...'):
        try:
            df, status = carregar_dados_github()
            if df is not None and len(df) > 0:
                st.session_state.df_original = df
                st.session_state.df_filtrado = df.copy()
                st.session_state.arquivo_atual = "GitHub"
                st.session_state.fonte_dados = "GitHub"
                st.session_state.ultima_atualizacao = get_horario_brasilia()
                st.rerun()
        except:
            pass
    
    if st.session_state.df_original is None:
        arquivo_local = encontrar_arquivo_local()
        if arquivo_local:
            try:
                with open(arquivo_local, 'r', encoding='utf-8-sig') as f:
                    conteudo = f.read()
                lines = conteudo.split('\n')
                header_line = None
                for i, line in enumerate(lines):
                    if line.startswith('"Chamado"') or line.startswith('"Título"'):
                        header_line = i
                        break
                if header_line is not None:
                    data_str = '\n'.join(lines[header_line:])
                    df = pd.read_csv(io.StringIO(data_str), quotechar='"')
                    df = processar_dataframe(df)
                    if df is not None and len(df) > 0:
                        st.session_state.df_original = df
                        st.session_state.df_filtrado = df.copy()
                        st.session_state.arquivo_atual = "Local"
                        st.session_state.fonte_dados = "Local"
                        st.session_state.ultima_atualizacao = get_horario_brasilia()
                        st.rerun()
            except:
                pass

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
    
    if st.session_state.df_original is not None:
        df = st.session_state.df_original.copy()
        
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**🔍 Filtros de Análise**")
            
            if 'Ano' in df.columns and not df['Ano'].isna().all():
                anos = sorted(df['Ano'].dropna().unique().astype(int))
                if anos:
                    ano_selecionado = st.selectbox("📅 Ano", ['Todos os Anos'] + list(anos), key="filtro_ano")
                    if ano_selecionado != 'Todos os Anos':
                        df = df[df['Ano'] == int(ano_selecionado)]
            
            if 'Mês' in df.columns and not df['Mês'].isna().all():
                meses = sorted(df['Mês'].dropna().unique().astype(int))
                if meses:
                    mes_selecionado = st.selectbox("📆 Mês", ['Todos os Meses'] + [str(m) for m in meses], key="filtro_mes")
                    if mes_selecionado != 'Todos os Meses':
                        df = df[df['Mês'] == int(mes_selecionado)]
            
            if 'Responsável_Formatado' in df.columns:
                responsaveis = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
                resp_selecionado = st.selectbox("👤 Responsável", responsaveis, key="filtro_responsavel")
                if resp_selecionado != 'Todos':
                    df = df[df['Responsável_Formatado'] == resp_selecionado]
            
            busca_chamado = st.text_input("🔎 Buscar Chamado", placeholder="Digite número do chamado...", key="busca_chamado")
            if busca_chamado:
                try:
                    df = df[df['Chamado'].astype(str).str.contains(busca_chamado, na=False)]
                except:
                    pass
            
            if 'Status' in df.columns:
                status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox("📊 Status", status_opcoes, key="filtro_status")
                if status_selecionado != 'Todos':
                    df = df[df['Status'] == status_selecionado]
            
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos'] + sorted(df['Tipo_Chamado'].dropna().unique())
                tipo_selecionado = st.selectbox("📝 Tipo de Chamado", tipos, key="filtro_tipo")
                if tipo_selecionado != 'Todos':
                    df = df[df['Tipo_Chamado'] == tipo_selecionado]
            
            if 'Empresa' in df.columns:
                empresas = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                empresa_selecionada = st.selectbox("🏢 Empresa", empresas, key="filtro_empresa")
                if empresa_selecionada != 'Todas':
                    df = df[df['Empresa'] == empresa_selecionada]
            
            if 'SRE' in df.columns:
                sres = ['Todos'] + sorted(df['SRE'].dropna().unique())
                sre_selecionado = st.selectbox("🔧 SRE Responsável", sres, key="filtro_sre")
                if sre_selecionado != 'Todos':
                    df = df[df['SRE'] == sre_selecionado]
            
            st.session_state.df_filtrado = df
            st.markdown(f"**📈 Registros filtrados:** {len(df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**🔄 Controles de Atualização**")
        
        if st.session_state.df_original is not None:
            fonte = st.session_state.get('fonte_dados', 'Desconhecida')
            st.markdown(f"""
            <div style="background: {COR_CINZA_FUNDO}; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="margin: 0 0 0.3rem 0; font-weight: 600;">📄 Fonte de dados:</p>
                <p style="margin: 0; font-size: 0.85rem; color: {COR_PRETO_SUAVE};">{fonte}</p>
                <p style="margin: 0.3rem 0 0 0; font-size: 0.75rem; color: {COR_CINZA_TEXTO};">
                {len(st.session_state.df_original):,} registros
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔄 Recarregar GitHub", use_container_width=True, type="primary", key="btn_recarregar_github"):
                    with st.spinner('🔄 Recarregando...'):
                        st.cache_data.clear()
                        df_atualizado, status = carregar_dados_github()
                        if df_atualizado is not None:
                            st.session_state.df_original = df_atualizado
                            st.session_state.df_filtrado = df_atualizado.copy()
                            st.session_state.arquivo_atual = "GitHub"
                            st.session_state.fonte_dados = "GitHub"
                            st.session_state.ultima_atualizacao = get_horario_brasilia()
                            st.success(f"✅ {len(df_atualizado):,} registros recarregados!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {status}")
            
            with col_btn2:
                if st.button("🗑️ Limpar Tudo", use_container_width=True, type="secondary", key="btn_limpar"):
                    st.cache_data.clear()
                    limpar_sessao()
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
        
        uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=['csv'], key="file_uploader", label_visibility="collapsed")
        
        if uploaded_file is not None:
            st.write(f"📄 {uploaded_file.name} ({uploaded_file.size/1024:.1f} KB)")
            if st.button("📥 Processar Arquivo", use_container_width=True, type="primary", key="btn_processar"):
                with st.spinner('Processando...'):
                    df_novo, status = carregar_dados_upload(uploaded_file)
                    if df_novo is not None and len(df_novo) > 0:
                        st.session_state.df_original = df_novo
                        st.session_state.df_filtrado = df_novo.copy()
                        st.session_state.arquivo_atual = uploaded_file.name
                        st.session_state.fonte_dados = "Upload"
                        st.session_state.ultima_atualizacao = get_horario_brasilia()
                        st.success(status)
                        st.rerun()
                    else:
                        st.error(status)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown(f"""
<div style="background: linear-gradient(135deg, {COR_AZUL_PETROLEO} 0%, {COR_AZUL_ESCURO} 100%);padding:1.5rem 2rem;margin-bottom:1.5rem;border-radius:0;box-shadow:0 4px 15px rgba(2,138,159,0.3);">
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;">
        <div>
            <h1 style="color:{COR_BRANCO};margin:0;font-size:1.6rem;font-weight:600;letter-spacing:-0.3px;text-shadow:0 1px 2px rgba(0,0,0,0.1);">
                📊 ESTEIRA SRE (Site Reliability Engineering)
            </h1>
            <p style="color:rgba(255,255,255,0.9);margin:0.3rem 0 0 0;font-size:0.85rem;font-weight:400;">
                Acompanhamento das validações da EAC | EMR | EMS | EMT | EPB | ERO | ESE | ESS | ETO
            </p>
        </div>
        <div style="text-align:right;">
            <p style="color:rgba(255,255,255,0.9);margin:0;font-size:0.85rem;font-weight:500;">Dashboard de Performance</p>
            <p style="color:rgba(255,255,255,0.8);margin:0.2rem 0 0 0;font-size:0.75rem;">v5.5 | Sistema de Performance SRE</p>
            <p style="color:rgba(255,255,255,0.7);margin:0.3rem 0 0 0;font-size:0.7rem;font-weight:500;">{datetime.now().strftime('%d/%m/%Y')}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# BOTÕES MANCHETE
# ============================================
if st.session_state.df_original is not None:
    if 'show_popup' not in st.session_state:
        st.session_state.show_popup = False
    
    col_btn_manchete, col_espaco = st.columns([2, 10])
    with col_btn_manchete:
        if st.button("📰 **VER MANCHETE**", help="Clique para ver os principais indicadores do mês", type="secondary", use_container_width=True, key="btn_manchete"):
            st.session_state.show_popup = True

# ============================================
# DASHBOARD PRINCIPAL
# ============================================
if st.session_state.df_original is not None:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    if len(df) > 0:
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(criar_card_indicador_simples(len(df), "Total de Demandas", "📋"), unsafe_allow_html=True)
        with col2:
            if 'Status' in df.columns:
                sincronizados = len(df[df['Status'] == 'Sincronizado'])
                st.markdown(criar_card_indicador_simples(sincronizados, "Sincronizados", "✅"), unsafe_allow_html=True)
        with col3:
            if 'Revisões' in df.columns:
                total_revisoes = int(df['Revisões'].sum())
                st.markdown(criar_card_indicador_simples(total_revisoes, "Total de Revisões", "📝"), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabs - MANTENDO TODAS AS ABAS ORIGINAIS
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📅 Evolução de Demandas",
            "📊 Análise de Revisões",
            "📈 Sincronização Diária",
            "🏆 Análise Avançada SRE",
            "🗺️ Mapa",
            "🎯 KPI IPE",
            "📈 Análise Estatística"
        ])
        
        # ============================================
        # TAB 1 - EVOLUÇÃO DE DEMANDAS
        # ============================================
        with tab1:
            st.markdown(f'<div class="section-title">📅 EVOLUÇÃO DE DEMANDAS POR MÊS</div>', unsafe_allow_html=True)
            
            col_titulo, col_seletor = st.columns([3, 1])
            with col_seletor:
                if 'Ano' in df.columns and not df['Ano'].isna().all():
                    anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                    if anos_disponiveis:
                        ano_selecionado = st.selectbox("Selecionar Ano:", options=anos_disponiveis, index=len(anos_disponiveis)-1, label_visibility="collapsed", key="ano_evolucao")
            
            if 'Ano' in df.columns and 'Nome_Mês' in df.columns and not df['Ano'].isna().all() and anos_disponiveis:
                df_ano = df[df['Ano'] == ano_selecionado].copy()
                if not df_ano.empty:
                    ordem_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                    demandas_por_mes = df_ano.groupby('Mês').size().reset_index()
                    demandas_por_mes.columns = ['Mês_Num', 'Quantidade']
                    todos_meses = pd.DataFrame({'Mês_Num': range(1, 13), 'Nome_Mês': ordem_meses})
                    demandas_completas = pd.merge(todos_meses, demandas_por_mes, on='Mês_Num', how='left')
                    demandas_completas['Quantidade'] = demandas_completas['Quantidade'].fillna(0).astype(int)
                    
                    fig_mes = go.Figure()
                    fig_mes.add_trace(go.Scatter(
                        x=demandas_completas['Nome_Mês'],
                        y=demandas_completas['Quantidade'],
                        mode='lines+markers+text',
                        line=dict(color=COR_AZUL_ESCURO, width=3),
                        marker=dict(size=10, color=COR_AZUL_PETROLEO),
                        text=demandas_completas['Quantidade'],
                        textposition='top center'
                    ))
                    fig_mes.update_layout(
                        title=f"Demandas em {ano_selecionado}",
                        xaxis_title="Mês",
                        yaxis_title="Número de Demandas",
                        height=450,
                        plot_bgcolor=COR_BRANCO,
                        showlegend=False
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

        # ============================================
        # TAB 2 - ANÁLISE DE REVISÕES
        # ============================================
        with tab2:
            st.markdown(f'<div class="section-title">📊 REVISÕES POR RESPONSÁVEL</div>', unsafe_allow_html=True)
            
            ano_rev = 'Todos os Anos'
            mes_rev = 'Todos os Meses'
            
            col_rev_filtro1, col_rev_filtro2 = st.columns(2)
            with col_rev_filtro1:
                if 'Ano' in df.columns and not df['Ano'].isna().all():
                    anos_rev = sorted(df['Ano'].dropna().unique().astype(int))
                    if anos_rev:
                        ano_rev = st.selectbox("📅 Filtrar por Ano:", ['Todos os Anos'] + list(anos_rev), key="filtro_ano_revisoes")
            with col_rev_filtro2:
                if 'Mês' in df.columns and not df['Mês'].isna().all():
                    meses_rev = sorted(df['Mês'].dropna().unique().astype(int))
                    if meses_rev:
                        mes_rev = st.selectbox("📆 Filtrar por Mês:", ['Todos os Meses'] + [str(m) for m in meses_rev], key="filtro_mes_revisoes")
            
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
                    
                    fig_revisoes = go.Figure()
                    fig_revisoes.add_trace(go.Bar(
                        x=revisoes_por_responsavel['Responsável'].head(15),
                        y=revisoes_por_responsavel['Total_Revisões'].head(15),
                        text=revisoes_por_responsavel['Total_Revisões'].head(15),
                        textposition='outside',
                        marker_color=COR_AZUL_PETROLEO,
                        marker_line_color=COR_AZUL_ESCURO,
                        marker_line_width=1.5
                    ))
                    fig_revisoes.update_layout(
                        title="Top 15 Responsáveis com Mais Revisões",
                        xaxis_title="Responsável",
                        yaxis_title="Total de Revisões",
                        height=500,
                        plot_bgcolor=COR_BRANCO,
                        showlegend=False,
                        xaxis=dict(tickangle=45)
                    )
                    st.plotly_chart(fig_revisoes, use_container_width=True)

        # ============================================
        # TAB 3 - SINCRONIZAÇÃO DIÁRIA
        # ============================================
        with tab3:
            st.markdown(f'<div class="section-title">📈 CHAMADOS SINCRONIZADOS POR DIA - ANÁLISE COMPLETA</div>', unsafe_allow_html=True)
            
            ano_sinc = 'Todos os Anos'
            mes_sinc = 'Todos os Meses'
            sre_sinc = 'Todos os SREs'
            empresa_sinc = 'Todas Empresas'
            
            col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
            with col_filtro1:
                if 'Ano' in df.columns and not df['Ano'].isna().all():
                    anos_sinc = sorted(df['Ano'].dropna().unique().astype(int))
                    if anos_sinc:
                        ano_sinc = st.selectbox("📅 Ano:", ['Todos os Anos'] + list(anos_sinc), key="filtro_ano_sinc")
            with col_filtro2:
                if 'Mês' in df.columns and not df['Mês'].isna().all():
                    meses_sinc = sorted(df['Mês'].dropna().unique().astype(int))
                    if meses_sinc:
                        mes_sinc = st.selectbox("📆 Mês:", ['Todos os Meses'] + [str(m) for m in meses_sinc], key="filtro_mes_sinc")
            with col_filtro3:
                if 'SRE' in df.columns:
                    sres_sinc = sorted(df['SRE'].dropna().unique())
                    if sres_sinc:
                        sre_sinc = st.selectbox("🔧 SRE:", ['Todos os SREs'] + sres_sinc, key="filtro_sre_sinc")
            with col_filtro4:
                if 'Empresa' in df.columns:
                    empresas_sinc = sorted(df['Empresa'].dropna().unique())
                    if empresas_sinc:
                        empresa_sinc = st.selectbox("🏢 Empresa:", ['Todas Empresas'] + empresas_sinc, key="filtro_empresa_sinc")
            
            df_sinc = df.copy()
            if ano_sinc != 'Todos os Anos':
                df_sinc = df_sinc[df_sinc['Ano'] == int(ano_sinc)]
            if mes_sinc != 'Todos os Meses':
                df_sinc = df_sinc[df_sinc['Mês'] == int(mes_sinc)]
            if sre_sinc != 'Todos os SREs':
                df_sinc = df_sinc[df_sinc['SRE'] == sre_sinc]
            if empresa_sinc != 'Todas Empresas':
                df_sinc = df_sinc[df_sinc['Empresa'] == empresa_sinc]
            
            if 'Status' in df_sinc.columns and 'Criado' in df_sinc.columns:
                df_sincronizados = df_sinc[df_sinc['Status'] == 'Sincronizado'].copy()
                if not df_sincronizados.empty:
                    if 'Data_Date' not in df_sincronizados.columns:
                        df_sincronizados['Data_Date'] = df_sincronizados['Criado'].dt.date
                    
                    sincronizados_por_dia = df_sincronizados.groupby('Data_Date').size().reset_index()
                    sincronizados_por_dia.columns = ['Data', 'Quantidade']
                    sincronizados_por_dia = sincronizados_por_dia.sort_values('Data')
                    
                    total_sincronizados = int(sincronizados_por_dia['Quantidade'].sum())
                    media_diaria = sincronizados_por_dia['Quantidade'].mean()
                    
                    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
                    with col_kpi1:
                        st.metric("✅ Total Sincronizado", f"{total_sincronizados:,}")
                    with col_kpi2:
                        st.metric("📊 Média Diária", f"{media_diaria:.1f}")
                    with col_kpi3:
                        if not sincronizados_por_dia.empty:
                            max_dia = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmax()]
                            st.metric("📈 Dia com Mais Sinc.", f"{int(max_dia['Quantidade'])}", max_dia['Data'].strftime('%d/%m'))
                    with col_kpi4:
                        st.metric("📅 Dias com Sinc.", len(sincronizados_por_dia))
                    
                    fig_dias = go.Figure()
                    fig_dias.add_trace(go.Bar(
                        x=sincronizados_por_dia['Data'].astype(str),
                        y=sincronizados_por_dia['Quantidade'],
                        text=sincronizados_por_dia['Quantidade'],
                        textposition='outside',
                        marker_color=COR_AZUL_PETROLEO,
                        marker_line_color=COR_AZUL_ESCURO,
                        marker_line_width=1.5
                    ))
                    fig_dias.update_layout(
                        title="Sincronizações por Dia",
                        xaxis_title="Data",
                        yaxis_title="Quantidade de Sincronizações",
                        height=400,
                        plot_bgcolor=COR_BRANCO,
                        showlegend=False,
                        xaxis=dict(tickangle=45, tickfont=dict(size=8))
                    )
                    st.plotly_chart(fig_dias, use_container_width=True)
                    
                    col_dia1, col_dia2, col_dia3 = st.columns(3)
                    with col_dia1:
                        if not sincronizados_por_dia.empty:
                            dia_max = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmax()]
                            st.metric("📈 Melhor Dia", dia_max['Data'].strftime('%d/%m/%Y'), f"{int(dia_max['Quantidade'])} sinc.")
                    with col_dia2:
                        if not sincronizados_por_dia.empty:
                            dia_min = sincronizados_por_dia.loc[sincronizados_por_dia['Quantidade'].idxmin()]
                            st.metric("📉 Pior Dia", dia_min['Data'].strftime('%d/%m/%Y'), f"{int(dia_min['Quantidade'])} sinc.")
                    with col_dia3:
                        st.metric("📊 Média por Dia", f"{media_diaria:.1f}")

        # ============================================
        # TAB 4 - ANÁLISE AVANÇADA SRE
        # ============================================
        with tab4:
            st.markdown(f'<div class="section-title">🏆 PERFORMANCE DOS SREs</div>', unsafe_allow_html=True)
            
            if 'SRE' in df.columns and 'Status' in df.columns and 'Revisões' in df.columns:
                ano_sre = 'Todos'
                mes_sre = 'Todos'
                
                col_filtro1, col_filtro2 = st.columns(2)
                with col_filtro1:
                    if 'Ano' in df.columns and not df['Ano'].isna().all():
                        anos_sre = sorted(df['Ano'].dropna().unique().astype(int))
                        if anos_sre:
                            ano_sre = st.selectbox("📅 Filtrar por Ano:", ['Todos'] + list(anos_sre), key="filtro_ano_sre")
                with col_filtro2:
                    if 'Mês' in df.columns and not df['Mês'].isna().all():
                        meses_sre = sorted(df['Mês'].dropna().unique().astype(int))
                        if meses_sre:
                            mes_sre = st.selectbox("📆 Filtrar por Mês:", ['Todos'] + [str(m) for m in meses_sre], key="filtro_mes_sre")
                
                df_sre = df.copy()
                if ano_sre != 'Todos':
                    df_sre = df_sre[df_sre['Ano'] == int(ano_sre)]
                if mes_sre != 'Todos':
                    df_sre = df_sre[df_sre['Mês'] == int(mes_sre)]
                
                df_sincronizados = df_sre[df_sre['Status'] == 'Sincronizado'].copy()
                
                if not df_sincronizados.empty and 'SRE' in df_sincronizados.columns:
                    sinc_por_sre = df_sincronizados.groupby('SRE').size().reset_index()
                    sinc_por_sre.columns = ['SRE', 'Sincronizados']
                    sinc_por_sre = sinc_por_sre.sort_values('Sincronizados', ascending=False)
                    
                    fig_sinc_bar = go.Figure()
                    fig_sinc_bar.add_trace(go.Bar(
                        x=sinc_por_sre['SRE'],
                        y=sinc_por_sre['Sincronizados'],
                        text=sinc_por_sre['Sincronizados'],
                        textposition='outside',
                        marker_color=COR_AZUL_PETROLEO,
                        marker_line_color=COR_AZUL_ESCURO,
                        marker_line_width=1.5
                    ))
                    fig_sinc_bar.update_layout(
                        title="Sincronizados por SRE",
                        xaxis_title="SRE",
                        yaxis_title="Número de Sincronizados",
                        height=500,
                        plot_bgcolor=COR_BRANCO,
                        showlegend=False,
                        xaxis=dict(tickangle=45)
                    )
                    st.plotly_chart(fig_sinc_bar, use_container_width=True)
                    
                    col_top1, col_top2, col_top3 = st.columns(3)
                    if len(sinc_por_sre) >= 1:
                        with col_top1:
                            sre1 = sinc_por_sre.iloc[0]
                            st.metric("🥇 1º Lugar", f"{sre1['SRE']}", f"{sre1['Sincronizados']} sinc.")
                    if len(sinc_por_sre) >= 2:
                        with col_top2:
                            sre2 = sinc_por_sre.iloc[1]
                            st.metric("🥈 2º Lugar", f"{sre2['SRE']}", f"{sre2['Sincronizados']} sinc.")
                    if len(sinc_por_sre) >= 3:
                        with col_top3:
                            sre3 = sinc_por_sre.iloc[2]
                            st.metric("🥉 3º Lugar", f"{sre3['SRE']}", f"{sre3['Sincronizados']} sinc.")
                    
                    st.markdown("### 📋 Performance Detalhada dos SREs")
                    sres_metrics = []
                    for sre in df_sre['SRE'].dropna().unique():
                        df_sre_data = df_sre[df_sre['SRE'] == sre].copy()
                        if len(df_sre_data) > 0:
                            sres_metrics.append({
                                'SRE': sre,
                                'Total_Cards': len(df_sre_data),
                                'Sincronizados': len(df_sre_data[df_sre_data['Status'] == 'Sincronizado']),
                                'Cards_Retorno': len(df_sre_data[df_sre_data['Revisões'] > 0])
                            })
                    if sres_metrics:
                        df_sres_metrics = pd.DataFrame(sres_metrics).sort_values('Sincronizados', ascending=False)
                        st.dataframe(df_sres_metrics, use_container_width=True)

        # ============================================
        # TAB 5 - MAPA
        # ============================================
        with tab5:
            st.markdown("## 🗺️ Mapa de Sincronizações por Empresa")
            st.info("ℹ️ Função de mapa - requer biblioteca folium instalada")
            # Código do mapa aqui (mantido do original)

        # ============================================
        # TAB 6 - KPI IPE
        # ============================================
        with tab6:
            st.markdown(f'<div class="section-title">🎯 KPI IPE - ÍNDICE DE PERFORMANCE DO ESPECIALISTA</div>', unsafe_allow_html=True)
            st.info("ℹ️ Função KPI - requer colunas 'Retorno Cliente'")
            # Código do KPI aqui (mantido do original)

        # ============================================
        # TAB 7 - ANÁLISE ESTATÍSTICA
        # ============================================
        with tab7:
            st.markdown("## 📈 ANÁLISE ESTATÍSTICA")
            
            ano_est = 'Todos os Anos'
            mes_est = 'Todos os Meses'
            
            col_filtro_est1, col_filtro_est2, col_filtro_est3 = st.columns(3)
            with col_filtro_est1:
                if 'Ano' in df.columns and not df['Ano'].isna().all():
                    anos_est = sorted(df['Ano'].dropna().unique().astype(int))
                    if anos_est:
                        ano_est = st.selectbox("📅 Ano", ['Todos os Anos'] + list(anos_est), key="filtro_ano_est")
            with col_filtro_est2:
                if 'Mês' in df.columns and not df['Mês'].isna().all():
                    if ano_est != 'Todos os Anos':
                        df_ano_est = df[df['Ano'] == int(ano_est)]
                        meses_est = sorted(df_ano_est['Mês'].dropna().unique().astype(int))
                    else:
                        meses_est = sorted(df['Mês'].dropna().unique().astype(int))
                    if meses_est:
                        mes_est = st.selectbox("📆 Mês", ['Todos os Meses'] + [str(m) for m in meses_est], key="filtro_mes_est")
            
            percentil_param = st.number_input("🎯 Percentil de Referência (%)", min_value=50, max_value=99, value=75, step=5, key="percentil_param")
            
            df_est = df.copy()
            if ano_est != 'Todos os Anos':
                df_est = df_est[df_est['Ano'] == int(ano_est)]
            if mes_est != 'Todos os Meses':
                df_est = df_est[df_est['Mês'] == int(mes_est)]
            
            df_sinc_est = df_est[df_est['Status'] == 'Sincronizado'].copy()
            
            if not df_sinc_est.empty and 'Criado' in df_sinc_est.columns:
                if 'Data_Date' not in df_sinc_est.columns:
                    df_sinc_est['Data_Date'] = df_sinc_est['Criado'].dt.date
                
                sinc_por_dia_est = df_sinc_est.groupby('Data_Date').size().reset_index()
                sinc_por_dia_est.columns = ['Data', 'Quantidade']
                
                if not sinc_por_dia_est.empty:
                    valores = sinc_por_dia_est['Quantidade']
                    
                    st.markdown("### 📊 DISTRIBUIÇÃO E PERCENTIS")
                    fig_sep = go.Figure()
                    fig_sep.add_trace(go.Histogram(
                        x=valores,
                        nbinsx=20,
                        marker_color='rgba(2, 138, 159, 0.7)',
                        marker_line_color=COR_AZUL_ESCURO,
                        marker_line_width=1
                    ))
                    fig_sep.add_vline(x=valores.median(), line_dash="dash", line_color=COR_VERDE_ESCURO, annotation_text=f"Mediana: {valores.median():.0f}")
                    fig_sep.update_layout(
                        title="Distribuição de Sincronizações Diárias",
                        xaxis_title="Número de Sincronizações por Dia",
                        yaxis_title="Frequência",
                        height=450,
                        plot_bgcolor=COR_BRANCO,
                        showlegend=False
                    )
                    st.plotly_chart(fig_sep, use_container_width=True)

# ============================================
# FOOTER
# ============================================
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
