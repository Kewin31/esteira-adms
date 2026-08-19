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
# !!! SUBSTITUA PELA URL CORRETA DO SEU ARQUIVO !!!
GITHUB_CSV_URL = "https://raw.githubusercontent.com/Kewin31/esteira-adms/refs/heads/main/data/esteira_demandas.csv"

# ============================================
# PALETA DE CORES
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

# ============================================
# MAPEAMENTO DAS EMPRESAS
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

def calcular_hash_arquivo(conteudo):
    return hashlib.md5(conteudo).hexdigest()

def get_horario_brasilia():
    try:
        tz = timezone('America/Sao_Paulo')
        return datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    except:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

# ============================================
# FUNÇÃO PRINCIPAL DE CARREGAMENTO
# ============================================
@st.cache_data(ttl=300)
def carregar_dados_github():
    """Carrega o arquivo CSV diretamente do GitHub"""
    try:
        response = requests.get(GITHUB_CSV_URL, timeout=30)
        response.raise_for_status()
        
        content = response.text
        if content.startswith('\ufeff'):
            content = content[1:]
        
        df = pd.read_csv(
            io.StringIO(content),
            quotechar='"',
            delimiter=',',
            encoding='utf-8',
            dtype=str
        )
        
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
        
        # Verifica coluna de chamado
        if 'Chamado' not in df.columns:
            for col in df.columns:
                if 'chamado' in col.lower() or 'título' in col.lower():
                    df = df.rename(columns={col: 'Chamado'})
                    break
        
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
            # Fallback se não conseguir processar datas
            df['Ano'] = pd.NA
            df['Mês'] = pd.NA
            df['Nome_Mês'] = pd.NA
            df['Ano_Mês'] = pd.NA
        
        # Converte Revisões
        if 'Revisões' in df.columns:
            df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
        
        return df, f"✅ {len(df):,} registros carregados do GitHub!"
    
    except requests.exceptions.RequestException as e:
        return None, f"❌ Erro ao baixar do GitHub: {str(e)}"
    except Exception as e:
        return None, f"❌ Erro ao processar CSV: {str(e)}"

@st.cache_data(ttl=300)
def carregar_dados_upload(uploaded_file):
    """Carrega dados de upload manual"""
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
        
        # Mesmo processamento do GitHub
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
        
        if 'Responsável' in df.columns:
            df['Responsável_Formatado'] = df['Responsável'].apply(formatar_nome_responsavel)
        
        for col in ['Criado', 'Modificado']:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], format='%d/%m/%Y %H:%M', errors='coerce')
                except:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
        
        if 'Criado' in df.columns and not df['Criado'].isna().all():
            df['Ano'] = df['Criado'].dt.year
            df['Mês'] = df['Criado'].dt.month
            df['Dia'] = df['Criado'].dt.day
            df['Hora'] = df['Criado'].dt.hour
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
            df['Ano_Mês'] = pd.NA
        
        if 'Revisões' in df.columns:
            df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
        
        return df, f"✅ {len(df):,} registros carregados!"
    
    except Exception as e:
        return None, f"Erro: {str(e)}"

def encontrar_arquivo_local():
    """Tenta encontrar arquivo local"""
    caminhos = [
        "esteira_demandas.csv",
        "data/esteira_demandas.csv",
        "dados/esteira_demandas.csv",
        "Esteira de Demandas ADMS (72).csv"
    ]
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
    # Tenta GitHub
    with st.spinner('🔄 Carregando dados do GitHub...'):
        try:
            df, status = carregar_dados_github()
            if df is not None:
                st.session_state.df_original = df
                st.session_state.df_filtrado = df.copy()
                st.session_state.arquivo_atual = "GitHub"
                st.session_state.fonte_dados = "GitHub"
                st.session_state.ultima_atualizacao = get_horario_brasilia()
                st.rerun()
        except:
            pass
    
    # Fallback para local
    if st.session_state.df_original is None:
        arquivo_local = encontrar_arquivo_local()
        if arquivo_local:
            with st.spinner('🔄 Carregando arquivo local...'):
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
                        # Processa df...
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
# SIDEBAR
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
            
            # Filtro Ano
            if 'Ano' in df.columns and not df['Ano'].isna().all():
                anos = sorted(df['Ano'].dropna().unique().astype(int))
                if anos:
                    ano_selecionado = st.selectbox("📅 Ano", ['Todos os Anos'] + list(anos), key="filtro_ano")
                    if ano_selecionado != 'Todos os Anos':
                        df = df[df['Ano'] == int(ano_selecionado)]
            
            # Filtro Mês
            if 'Mês' in df.columns and not df['Mês'].isna().all():
                meses = sorted(df['Mês'].dropna().unique().astype(int))
                if meses:
                    mes_selecionado = st.selectbox("📆 Mês", ['Todos os Meses'] + [str(m) for m in meses], key="filtro_mes")
                    if mes_selecionado != 'Todos os Meses':
                        df = df[df['Mês'] == int(mes_selecionado)]
            
            # Filtro Responsável
            if 'Responsável_Formatado' in df.columns:
                responsaveis = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
                resp_selecionado = st.selectbox("👤 Responsável", responsaveis, key="filtro_responsavel")
                if resp_selecionado != 'Todos':
                    df = df[df['Responsável_Formatado'] == resp_selecionado]
            
            # Busca Chamado
            busca = st.text_input("🔎 Buscar Chamado", placeholder="Digite o número...", key="busca_chamado")
            if busca:
                df = df[df['Chamado'].astype(str).str.contains(busca, na=False)]
            
            # Filtro Status
            if 'Status' in df.columns:
                status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox("📊 Status", status_opcoes, key="filtro_status")
                if status_selecionado != 'Todos':
                    df = df[df['Status'] == status_selecionado]
            
            # Filtro Tipo
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos'] + sorted(df['Tipo_Chamado'].dropna().unique())
                tipo_selecionado = st.selectbox("📝 Tipo de Chamado", tipos, key="filtro_tipo")
                if tipo_selecionado != 'Todos':
                    df = df[df['Tipo_Chamado'] == tipo_selecionado]
            
            # Filtro Empresa
            if 'Empresa' in df.columns:
                empresas = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                empresa_selecionada = st.selectbox("🏢 Empresa", empresas, key="filtro_empresa")
                if empresa_selecionada != 'Todas':
                    df = df[df['Empresa'] == empresa_selecionada]
            
            # Filtro SRE
            if 'SRE' in df.columns:
                sres = ['Todos'] + sorted(df['SRE'].dropna().unique())
                sre_selecionado = st.selectbox("🔧 SRE", sres, key="filtro_sre")
                if sre_selecionado != 'Todos':
                    df = df[df['SRE'] == sre_selecionado]
            
            st.session_state.df_filtrado = df
            st.markdown(f"**📈 Registros filtrados:** {len(df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**🔄 Controles**")
            
            if st.session_state.df_original is not None:
                fonte = st.session_state.get('fonte_dados', 'Desconhecida')
                st.markdown(f"""
                <div style="background:{COR_CINZA_FUNDO};padding:0.8rem;border-radius:8px;margin-bottom:1rem;">
                    <p style="margin:0;font-weight:600;">📄 Fonte: {fonte}</p>
                    <p style="margin:0.3rem 0 0 0;font-size:0.85rem;">{len(st.session_state.df_original):,} registros</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Recarregar", use_container_width=True, key="btn_recarregar"):
                        st.cache_data.clear()
                        limpar_sessao()
                        st.rerun()
                with col2:
                    if st.button("🗑️ Limpar", use_container_width=True, key="btn_limpar"):
                        st.cache_data.clear()
                        limpar_sessao()
                        st.rerun()
            
            st.markdown("---")
            st.markdown("**📤 Importar CSV**")
            
            uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=['csv'], key="file_uploader", label_visibility="collapsed")
            
            if uploaded_file is not None:
                st.write(f"📄 {uploaded_file.name} ({uploaded_file.size/1024:.1f} KB)")
                if st.button("📥 Processar", use_container_width=True, type="primary", key="btn_processar"):
                    with st.spinner('Processando...'):
                        df_novo, status = carregar_dados_upload(uploaded_file)
                        if df_novo is not None:
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
# DASHBOARD PRINCIPAL
# ============================================
if st.session_state.df_original is not None:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
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
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Evolução", "📊 Revisões", "📈 Sincronização", "🏆 SRE", "📊 Estatística"
    ])
    
    # ============================================
    # TAB 1 - EVOLUÇÃO DE DEMANDAS
    # ============================================
    with tab1:
        st.markdown(f'<div class="section-title">📅 EVOLUÇÃO DE DEMANDAS POR MÊS</div>', unsafe_allow_html=True)
        
        # Verifica se há dados de ano
        tem_dados_ano = 'Ano' in df.columns and not df['Ano'].isna().all()
        
        if tem_dados_ano:
            anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
            if anos_disponiveis:
                ano_selecionado = st.selectbox(
                    "Selecionar Ano:",
                    options=anos_disponiveis,
                    index=len(anos_disponiveis)-1,
                    key="ano_evolucao"
                )
                
                df_ano = df[df['Ano'] == ano_selecionado].copy()
                
                if not df_ano.empty and 'Nome_Mês' in df_ano.columns:
                    ordem_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                    
                    demandas_por_mes = df_ano.groupby('Mês').size().reset_index()
                    demandas_por_mes.columns = ['Mês_Num', 'Quantidade']
                    
                    todos_meses = pd.DataFrame({'Mês_Num': range(1, 13), 'Nome_Mês': ordem_meses})
                    demandas_completas = pd.merge(todos_meses, demandas_por_mes, on='Mês_Num', how='left')
                    demandas_completas['Quantidade'] = demandas_completas['Quantidade'].fillna(0).astype(int)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=demandas_completas['Nome_Mês'],
                        y=demandas_completas['Quantidade'],
                        mode='lines+markers+text',
                        line=dict(color=COR_AZUL_ESCURO, width=3),
                        marker=dict(size=10, color=COR_AZUL_PETROLEO),
                        text=demandas_completas['Quantidade'],
                        textposition='top center'
                    ))
                    fig.update_layout(
                        title=f"Demandas em {ano_selecionado}",
                        xaxis_title="Mês",
                        yaxis_title="Número de Demandas",
                        height=400,
                        plot_bgcolor=COR_BRANCO,
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("ℹ️ Nenhum dado disponível para o ano selecionado.")
            else:
                st.info("ℹ️ Nenhum ano disponível para análise.")
        else:
            st.warning("⚠️ Coluna 'Ano' não encontrada ou sem dados.")

    # ============================================
    # TAB 2 - REVISÕES POR RESPONSÁVEL
    # ============================================
    with tab2:
        st.markdown(f'<div class="section-title">📊 REVISÕES POR RESPONSÁVEL</div>', unsafe_allow_html=True)
        
        # Inicializa variáveis
        ano_rev = 'Todos os Anos'
        mes_rev = 'Todos os Meses'
        
        col_rev1, col_rev2 = st.columns(2)
        
        with col_rev1:
            if 'Ano' in df.columns and not df['Ano'].isna().all():
                anos = sorted(df['Ano'].dropna().unique().astype(int))
                ano_rev = st.selectbox("📅 Filtrar por Ano:", ['Todos os Anos'] + list(anos), key="filtro_ano_rev")
        
        with col_rev2:
            if 'Mês' in df.columns and not df['Mês'].isna().all():
                meses = sorted(df['Mês'].dropna().unique().astype(int))
                mes_rev = st.selectbox("📆 Filtrar por Mês:", ['Todos os Meses'] + [str(m) for m in meses], key="filtro_mes_rev")
        
        df_rev = df.copy()
        if ano_rev != 'Todos os Anos':
            df_rev = df_rev[df_rev['Ano'] == int(ano_rev)]
        if mes_rev != 'Todos os Meses':
            df_rev = df_rev[df_rev['Mês'] == int(mes_rev)]
        
        if 'Revisões' in df_rev.columns and 'Responsável_Formatado' in df_rev.columns:
            df_com_rev = df_rev[df_rev['Revisões'] > 0].copy()
            
            if not df_com_rev.empty:
                revisoes_por_resp = df_com_rev.groupby('Responsável_Formatado').agg({
                    'Revisões': 'sum',
                    'Chamado': 'count'
                }).reset_index()
                revisoes_por_resp.columns = ['Responsável', 'Total_Revisões', 'Chamados_Com_Revisão']
                revisoes_por_resp = revisoes_por_resp.sort_values('Total_Revisões', ascending=False)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=revisoes_por_resp['Responsável'].head(15),
                    y=revisoes_por_resp['Total_Revisões'].head(15),
                    text=revisoes_por_resp['Total_Revisões'].head(15),
                    textposition='outside',
                    marker_color=COR_AZUL_PETROLEO,
                    marker_line_color=COR_AZUL_ESCURO,
                    marker_line_width=1.5
                ))
                fig.update_layout(
                    title="Top 15 Responsáveis com Mais Revisões",
                    xaxis_title="Responsável",
                    yaxis_title="Total de Revisões",
                    height=500,
                    plot_bgcolor=COR_BRANCO,
                    showlegend=False,
                    xaxis=dict(tickangle=45)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ Nenhuma revisão encontrada com os filtros selecionados.")

    # ============================================
    # TAB 3 - SINCRONIZAÇÃO DIÁRIA
    # ============================================
    with tab3:
        st.markdown(f'<div class="section-title">📈 CHAMADOS SINCRONIZADOS POR DIA</div>', unsafe_allow_html=True)
        
        # Filtros
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        with col_f1:
            if 'Ano' in df.columns and not df['Ano'].isna().all():
                anos = sorted(df['Ano'].dropna().unique().astype(int))
                ano_sinc = st.selectbox("📅 Ano:", ['Todos'] + list(anos), key="filtro_ano_sinc")
            else:
                ano_sinc = 'Todos'
        
        with col_f2:
            if 'Mês' in df.columns and not df['Mês'].isna().all():
                meses = sorted(df['Mês'].dropna().unique().astype(int))
                mes_sinc = st.selectbox("📆 Mês:", ['Todos'] + [str(m) for m in meses], key="filtro_mes_sinc")
            else:
                mes_sinc = 'Todos'
        
        with col_f3:
            if 'SRE' in df.columns:
                sre_sinc = st.selectbox("🔧 SRE:", ['Todos'] + sorted(df['SRE'].dropna().unique()), key="filtro_sre_sinc")
            else:
                sre_sinc = 'Todos'
        
        with col_f4:
            if 'Empresa' in df.columns:
                empresa_sinc = st.selectbox("🏢 Empresa:", ['Todas'] + sorted(df['Empresa'].dropna().unique()), key="filtro_empresa_sinc")
            else:
                empresa_sinc = 'Todas'
        
        df_sinc = df.copy()
        if ano_sinc != 'Todos':
            df_sinc = df_sinc[df_sinc['Ano'] == int(ano_sinc)]
        if mes_sinc != 'Todos':
            df_sinc = df_sinc[df_sinc['Mês'] == int(mes_sinc)]
        if sre_sinc != 'Todos':
            df_sinc = df_sinc[df_sinc['SRE'] == sre_sinc]
        if empresa_sinc != 'Todas':
            df_sinc = df_sinc[df_sinc['Empresa'] == empresa_sinc]
        
        if 'Status' in df_sinc.columns and 'Criado' in df_sinc.columns:
            df_sincronizados = df_sinc[df_sinc['Status'] == 'Sincronizado'].copy()
            
            if not df_sincronizados.empty:
                df_sincronizados['Data'] = df_sincronizados['Criado'].dt.date
                sinc_por_dia = df_sincronizados.groupby('Data').size().reset_index()
                sinc_por_dia.columns = ['Data', 'Quantidade']
                sinc_por_dia = sinc_por_dia.sort_values('Data')
                
                total_sinc = int(sinc_por_dia['Quantidade'].sum())
                media_diaria = sinc_por_dia['Quantidade'].mean()
                
                # Métricas
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                with col_m1:
                    st.metric("✅ Total Sincronizado", f"{total_sinc:,}")
                with col_m2:
                    st.metric("📊 Média Diária", f"{media_diaria:.1f}")
                with col_m3:
                    if not sinc_por_dia.empty:
                        max_dia = sinc_por_dia.loc[sinc_por_dia['Quantidade'].idxmax()]
                        st.metric("📈 Dia com Mais Sinc.", f"{int(max_dia['Quantidade'])}", max_dia['Data'].strftime('%d/%m'))
                with col_m4:
                    st.metric("📅 Dias com Sinc.", len(sinc_por_dia))
                
                # Gráfico
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=sinc_por_dia['Data'].dt.strftime('%d/%m'),
                    y=sinc_por_dia['Quantidade'],
                    text=sinc_por_dia['Quantidade'],
                    textposition='outside',
                    marker_color=COR_AZUL_PETROLEO,
                    marker_line_color=COR_AZUL_ESCURO,
                    marker_line_width=1.5
                ))
                fig.update_layout(
                    title="Sincronizações por Dia",
                    xaxis_title="Data (Dia/Mês)",
                    yaxis_title="Quantidade",
                    height=400,
                    plot_bgcolor=COR_BRANCO,
                    showlegend=False,
                    xaxis=dict(tickangle=45)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Nenhum chamado sincronizado encontrado.")

    # ============================================
    # TAB 4 - PERFORMANCE DOS SREs
    # ============================================
    with tab4:
        st.markdown(f'<div class="section-title">🏆 PERFORMANCE DOS SREs</div>', unsafe_allow_html=True)
        
        if 'SRE' in df.columns and 'Status' in df.columns:
            # Filtros
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                if 'Ano' in df.columns and not df['Ano'].isna().all():
                    anos = sorted(df['Ano'].dropna().unique().astype(int))
                    ano_sre = st.selectbox("📅 Filtrar por Ano:", ['Todos'] + list(anos), key="filtro_ano_sre")
                else:
                    ano_sre = 'Todos'
            with col_f2:
                if 'Mês' in df.columns and not df['Mês'].isna().all():
                    meses = sorted(df['Mês'].dropna().unique().astype(int))
                    mes_sre = st.selectbox("📆 Filtrar por Mês:", ['Todos'] + [str(m) for m in meses], key="filtro_mes_sre")
                else:
                    mes_sre = 'Todos'
            
            df_sre = df.copy()
            if ano_sre != 'Todos':
                df_sre = df_sre[df_sre['Ano'] == int(ano_sre)]
            if mes_sre != 'Todos':
                df_sre = df_sre[df_sre['Mês'] == int(mes_sre)]
            
            df_sinc_sre = df_sre[df_sre['Status'] == 'Sincronizado'].copy()
            
            if not df_sinc_sre.empty and 'SRE' in df_sinc_sre.columns:
                sinc_por_sre = df_sinc_sre.groupby('SRE').size().reset_index()
                sinc_por_sre.columns = ['SRE', 'Sincronizados']
                sinc_por_sre = sinc_por_sre.sort_values('Sincronizados', ascending=False)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=sinc_por_sre['SRE'],
                    y=sinc_por_sre['Sincronizados'],
                    text=sinc_por_sre['Sincronizados'],
                    textposition='outside',
                    marker_color=COR_AZUL_PETROLEO,
                    marker_line_color=COR_AZUL_ESCURO,
                    marker_line_width=1.5
                ))
                fig.update_layout(
                    title="Sincronizações por SRE",
                    xaxis_title="SRE",
                    yaxis_title="Número de Sincronizados",
                    height=400,
                    plot_bgcolor=COR_BRANCO,
                    showlegend=False,
                    xaxis=dict(tickangle=45)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Top 3
                if len(sinc_por_sre) >= 1:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        sre = sinc_por_sre.iloc[0]
                        st.success(f"🥇 {sre['SRE']}\n\n{sre['Sincronizados']} sincronizações")
                    if len(sinc_por_sre) >= 2:
                        with col2:
                            sre = sinc_por_sre.iloc[1]
                            st.info(f"🥈 {sre['SRE']}\n\n{sre['Sincronizados']} sincronizações")
                    if len(sinc_por_sre) >= 3:
                        with col3:
                            sre = sinc_por_sre.iloc[2]
                            st.warning(f"🥉 {sre['SRE']}\n\n{sre['Sincronizados']} sincronizações")
            else:
                st.info("ℹ️ Nenhum dado de SRE disponível.")

    # ============================================
    # TAB 5 - ANÁLISE ESTATÍSTICA
    # ============================================
    with tab5:
        st.markdown(f'<div class="section-title">📊 ANÁLISE ESTATÍSTICA</div>', unsafe_allow_html=True)
        
        # Filtros
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            if 'Ano' in df.columns and not df['Ano'].isna().all():
                anos = sorted(df['Ano'].dropna().unique().astype(int))
                ano_est = st.selectbox("📅 Ano:", ['Todos'] + list(anos), key="filtro_ano_est")
            else:
                ano_est = 'Todos'
        with col_e2:
            if 'Mês' in df.columns and not df['Mês'].isna().all():
                meses = sorted(df['Mês'].dropna().unique().astype(int))
                mes_est = st.selectbox("📆 Mês:", ['Todos'] + [str(m) for m in meses], key="filtro_mes_est")
            else:
                mes_est = 'Todos'
        
        df_est = df.copy()
        if ano_est != 'Todos':
            df_est = df_est[df_est['Ano'] == int(ano_est)]
        if mes_est != 'Todos':
            df_est = df_est[df_est['Mês'] == int(mes_est)]
        
        df_sinc_est = df_est[df_est['Status'] == 'Sincronizado'].copy()
        
        if not df_sinc_est.empty and 'Criado' in df_sinc_est.columns:
            df_sinc_est['Data'] = df_sinc_est['Criado'].dt.date
            sinc_por_dia_est = df_sinc_est.groupby('Data').size().reset_index()
            sinc_por_dia_est.columns = ['Data', 'Quantidade']
            
            if not sinc_por_dia_est.empty:
                valores = sinc_por_dia_est['Quantidade']
                
                # Estatísticas
                col_e1, col_e2, col_e3, col_e4 = st.columns(4)
                with col_e1:
                    st.metric("📊 Mediana", f"{valores.median():.0f}")
                with col_e2:
                    st.metric("📊 Média", f"{valores.mean():.1f}")
                with col_e3:
                    st.metric("📊 Q1 (P25)", f"{valores.quantile(0.25):.0f}")
                with col_e4:
                    st.metric("📊 Q3 (P75)", f"{valores.quantile(0.75):.0f}")
                
                # Histograma
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=valores,
                    nbinsx=20,
                    marker_color='rgba(2, 138, 159, 0.7)',
                    marker_line_color=COR_AZUL_ESCURO,
                    marker_line_width=1
                ))
                fig.add_vline(x=valores.median(), line_dash="dash", line_color=COR_VERDE_ESCURO, 
                             annotation_text=f"Mediana: {valores.median():.0f}")
                fig.update_layout(
                    title="Distribuição de Sincronizações Diárias",
                    xaxis_title="Número de Sincronizações por Dia",
                    yaxis_title="Frequência",
                    height=400,
                    plot_bgcolor=COR_BRANCO,
                    showlegend=False,
                    bargap=0.05
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Boxplot
                fig2 = go.Figure()
                fig2.add_trace(go.Box(
                    y=valores,
                    name="Sincronizações Diárias",
                    marker_color=COR_AZUL_PETROLEO,
                    boxmean=True
                ))
                fig2.update_layout(
                    title="Boxplot das Sincronizações Diárias",
                    yaxis_title="Número de Sincronizações",
                    height=300,
                    plot_bgcolor=COR_BRANCO,
                    showlegend=False
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("ℹ️ Nenhum dado disponível para análise estatística.")
        else:
            st.info("ℹ️ Nenhum dado sincronizado encontrado.")

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
