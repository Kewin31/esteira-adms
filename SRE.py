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
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
/* === CSS ORIGINAL INTACTO === */
.main-header {
    background: linear-gradient(135deg, #0c2461 0%, #1e3799 100%);
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    color: white;
}
.metric-card-exec {
    background: white;
    padding: 1.2rem;
    border-radius: 10px;
    margin-bottom: 1rem;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1e3799;
}
.metric-label {
    font-size: 0.9rem;
    color: #6c757d;
}
.sidebar-section {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
}
.section-title-exec {
    color: #1e3799;
    border-bottom: 3px solid #1e3799;
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def get_horario_brasilia():
    try:
        tz = timezone('America/Sao_Paulo')
        return datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    except:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

def formatar_nome_responsavel(nome):
    if pd.isna(nome):
        return "Não informado"
    nome_str = str(nome).strip()
    if '@' in nome_str:
        nome_str = nome_str.split('@')[0]
        for sep in ['.', '_', '-']:
            nome_str = nome_str.replace(sep, ' ')
    return nome_str.title()

def calcular_hash_arquivo(conteudo):
    if isinstance(conteudo, bytes):
        return hashlib.md5(conteudo).hexdigest()
    return hashlib.md5(conteudo.encode('utf-8')).hexdigest()

def limpar_sessao_dados():
    for key in [
        'df_original','df_filtrado','arquivo_atual',
        'file_hash','uploaded_file_name','ultima_atualizacao'
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.cache_data.clear()

# ============================================
# CARREGAMENTO E PROCESSAMENTO
# ============================================
@st.cache_data(ttl=3600)
def carregar_e_processar_dados(file_content, filename):
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(file_content.decode('utf-8', errors='ignore')),
                             on_bad_lines='skip')
        else:
            df = pd.read_excel(io.BytesIO(file_content))
        df = processar_dataframe_basico(df)
        return df, "Dados carregados com sucesso"
    except Exception as e:
        return None, str(e)

def processar_dataframe_basico(df):
    if 'Responsável' in df.columns:
        df['Responsável_Formatado'] = df['Responsável'].apply(formatar_nome_responsavel)
    for col in ['Criado', 'Modificado']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    if 'Criado' in df.columns:
        df['Ano'] = df['Criado'].dt.year
        df['Mês'] = df['Criado'].dt.month
        df['Dia_Semana'] = df['Criado'].dt.day_name()
    if 'Revisões' in df.columns:
        df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
    return df

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("### ⚙️ Painel de Controle")

    if 'df_original' not in st.session_state:
        st.session_state.df_original = None
        st.session_state.df_filtrado = None

    uploaded_file = st.file_uploader(
        "Upload CSV ou Excel",
        type=['csv','xlsx','xls']
    )

    if uploaded_file:
        df, msg = carregar_e_processar_dados(
            uploaded_file.getvalue(),
            uploaded_file.name
        )
        if df is not None:
            st.session_state.df_original = df
            st.session_state.df_filtrado = df.copy()
            st.session_state.file_hash = calcular_hash_arquivo(uploaded_file.getvalue())
            st.session_state.ultima_atualizacao = get_horario_brasilia()
            st.success("Arquivo carregado com sucesso")
            st.rerun()

# ============================================
# HEADER
# ============================================
st.markdown("""
<div class="main-header">
    <h1>📊 ESTEIRA ADMS</h1>
    <p>Sistema de Análise de Chamados | SRE</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# CONTEÚDO PRINCIPAL
# ============================================
if st.session_state.df_original is None:
    st.info("Faça upload de um arquivo para iniciar.")
    st.stop()

df = st.session_state.df_filtrado.copy()

# ============================================
# INDICADORES
# ============================================
st.markdown("## 📈 Indicadores Principais")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Demandas", len(df))
with col2:
    st.metric("Sincronizados",
              len(df[df['Status'] == 'Sincronizado']) if 'Status' in df.columns else 0)
with col3:
    st.metric("Total Revisões",
              int(df['Revisões'].sum()) if 'Revisões' in df.columns else 0)

# =========================================================
# >>> A PARTIR DAQUI COMEÇAM AS ANÁLISES AVANÇADAS
# >>> (PARTE 2 / 3 TRARÁ TODAS AS ALTERAÇÕES PEDIDAS)
# =========================================================
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

# ======================================================
# ABA 1 — PERFORMANCE DE DESENVOLVEDORES
# ======================================================
with tab_extra1:

    # ------------------------------
    # EXPLICATIVO DOS QUADRANTES
    # ------------------------------
    with st.expander("ℹ️ Como interpretar a Matriz de Performance", expanded=False):
        st.markdown("""
**A Matriz de Performance cruza Eficiência x Qualidade**

⭐ **Estrelas**  
Alta eficiência e alta qualidade. São referências técnicas.

⚡ **Eficientes**  
Alta produtividade, mas qualidade abaixo da média. Precisam focar em revisão.

🎯 **Cuidadosos**  
Alta qualidade, mas menor volume de entregas.

🔄 **Necessita Apoio**  
Baixa eficiência e baixa qualidade. Demandam acompanhamento.
        """)

    # ------------------------------
    # FILTRAR SOMENTE DESENVOLVEDORES
    # (remove Kewin e Não informado)
    # ------------------------------
    df_dev = df.copy()
    df_dev = df_dev[
        ~df_dev['Responsável_Formatado'].isin([
            'Kewin Marcel',
            'Kewin Marcel Ramirez Ferreira',
            'Não informado'
        ])
    ]

    # ------------------------------
    # CRIAR MATRIZ DE PERFORMANCE
    # ------------------------------
    matriz = []

    for dev in df_dev['Responsável_Formatado'].unique():
        dados = df_dev[df_dev['Responsável_Formatado'] == dev]

        total = len(dados)
        if total == 0:
            continue

        sem_revisao = len(dados[dados['Revisões'] == 0])
        qualidade = (sem_revisao / total) * 100

        meses_ativos = dados['Criado'].dt.to_period('M').nunique()
        eficiencia = total / meses_ativos if meses_ativos > 0 else 0

        matriz.append({
            'Desenvolvedor': dev,
            'Qualidade': round(qualidade, 1),
            'Eficiencia': round(eficiencia, 1)
        })

    df_matriz = pd.DataFrame(matriz)

    if not df_matriz.empty:
        media_q = df_matriz['Qualidade'].mean()
        media_e = df_matriz['Eficiencia'].mean()

        # ------------------------------
        # GRÁFICO MATRIZ COM QUADRANTES
        # ------------------------------
        fig_matriz = px.scatter(
            df_matriz,
            x='Eficiencia',
            y='Qualidade',
            hover_name='Desenvolvedor',
            title='Matriz de Performance: Eficiência x Qualidade'
        )

        # Linhas médias
        fig_matriz.add_vline(x=media_e, line_dash="dash", line_color="gray")
        fig_matriz.add_hline(y=media_q, line_dash="dash", line_color="gray")

        # Quadrantes visuais
        fig_matriz.add_shape(type="rect",
            x0=media_e, y0=media_q,
            x1=df_matriz['Eficiencia'].max(), y1=df_matriz['Qualidade'].max(),
            fillcolor="rgba(40,167,69,0.15)", line_width=0)

        fig_matriz.add_shape(type="rect",
            x0=media_e, y0=df_matriz['Qualidade'].min(),
            x1=df_matriz['Eficiencia'].max(), y1=media_q,
            fillcolor="rgba(255,193,7,0.15)", line_width=0)

        fig_matriz.add_shape(type="rect",
            x0=df_matriz['Eficiencia'].min(), y0=media_q,
            x1=media_e, y1=df_matriz['Qualidade'].max(),
            fillcolor="rgba(0,123,255,0.15)", line_width=0)

        fig_matriz.add_shape(type="rect",
            x0=df_matriz['Eficiencia'].min(), y0=df_matriz['Qualidade'].min(),
            x1=media_e, y1=media_q,
            fillcolor="rgba(220,53,69,0.15)", line_width=0)

        st.plotly_chart(fig_matriz, use_container_width=True)

        # ------------------------------
        # TOP 10 SCORE DE QUALIDADE
        # ------------------------------
        st.markdown("### 🏆 Top 10 – Score de Qualidade")

        top10 = df_matriz.sort_values('Qualidade', ascending=False).head(10)

        fig_top = px.bar(
            top10,
            y='Desenvolvedor',
            x='Qualidade',
            orientation='h',
            text='Qualidade'
        )

        fig_top.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )

        fig_top.update_layout(
            xaxis_title='Score de Qualidade (%)',
            yaxis_title=''
        )

        st.plotly_chart(fig_top, use_container_width=True)

        # ------------------------------
        # PERFORMANCE DETALHADA
        # ------------------------------
        st.markdown("### 📋 Performance Detalhada")
        st.dataframe(df_matriz.sort_values('Qualidade', ascending=False),
                     use_container_width=True)

# ======================================================
# ABA 2 — ANÁLISE DE SAZONALIDADE (DIA DA SEMANA)
# ======================================================
with tab_extra2:

    st.markdown("### 📅 Análise por Dia da Semana")

    df_saz = df.copy()
    df_saz['Dia_Semana'] = df_saz['Criado'].dt.day_name()

    saz = df_saz.groupby('Dia_Semana').agg(
        Demandas=('Chamado', 'count'),
        Sincronizados=('Status', lambda x: (x == 'Sincronizado').sum())
    ).reset_index()

    fig_saz = px.line(
        saz,
        x='Dia_Semana',
        y=['Demandas', 'Sincronizados'],
        markers=True,
        title='Demandas e Sincronizados por Dia da Semana'
    )

    # Pico de sincronismo
    pico = saz.loc[saz['Sincronizados'].idxmax()]
    fig_saz.add_annotation(
        x=pico['Dia_Semana'],
        y=pico['Sincronizados'],
        text=f"🔺 Pico: {int(pico['Sincronizados'])}",
        showarrow=True
    )

    st.plotly_chart(fig_saz, use_container_width=True)

# ======================================================
# ABA 3 — DIAGNÓSTICO DE ERROS
# ======================================================
with tab_extra3:

    st.markdown("### ⚡ Diagnóstico de Erros")

    if 'Tipo_Chamado' in df.columns:
        erros = df['Tipo_Chamado'].value_counts().reset_index()
        erros.columns = ['Tipo', 'Quantidade']

        fig_erros = px.bar(
            erros,
            x='Quantidade',
            y='Tipo',
            orientation='h',
            title='Distribuição de Tipos de Erro'
        )

        st.plotly_chart(fig_erros, use_container_width=True)
    else:
        st.info("Coluna Tipo_Chamado não encontrada.")
# ============================================
# TOP 10 RESPONSÁVEIS
# ============================================
st.markdown("---")
st.markdown('<div class="section-title-exec">👥 TOP 10 RESPONSÁVEIS</div>', unsafe_allow_html=True)

if 'Responsável_Formatado' in df.columns:
    top_responsaveis = (
        df['Responsável_Formatado']
        .value_counts()
        .reset_index()
        .rename(columns={'index': 'Responsável', 'Responsável_Formatado': 'Demandas'})
        .head(10)
    )

    fig_top_resp = px.bar(
        top_responsaveis,
        x='Demandas',
        y='Responsável',
        orientation='h',
        text='Demandas',
        color='Demandas',
        color_continuous_scale='Blues'
    )

    fig_top_resp.update_traces(
        textposition='outside'
    )

    fig_top_resp.update_layout(
        height=450,
        plot_bgcolor='white',
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Número de Demandas',
        yaxis_title=''
    )

    st.plotly_chart(fig_top_resp, use_container_width=True)

# ============================================
# DISTRIBUIÇÃO POR TIPO DE CHAMADO
# ============================================
st.markdown('<div class="section-title-exec">📊 DISTRIBUIÇÃO POR TIPO</div>', unsafe_allow_html=True)

if 'Tipo_Chamado' in df.columns:
    tipos = (
        df['Tipo_Chamado']
        .value_counts()
        .reset_index()
        .rename(columns={'index': 'Tipo', 'Tipo_Chamado': 'Quantidade'})
        .sort_values('Quantidade', ascending=True)
    )

    fig_tipos = px.bar(
        tipos,
        x='Quantidade',
        y='Tipo',
        orientation='h',
        text='Quantidade',
        color='Quantidade',
        color_continuous_scale='Viridis'
    )

    fig_tipos.update_traces(
        textposition='outside'
    )

    fig_tipos.update_layout(
        height=450,
        plot_bgcolor='white',
        showlegend=False,
        xaxis_title='Quantidade',
        yaxis_title=''
    )

    st.plotly_chart(fig_tipos, use_container_width=True)

# ============================================
# ÚLTIMAS DEMANDAS REGISTRADAS
# ============================================
st.markdown("---")
st.markdown('<div class="section-title-exec">🕒 ÚLTIMAS DEMANDAS REGISTRADAS</div>', unsafe_allow_html=True)

if 'Criado' in df.columns:

    col1, col2, col3 = st.columns(3)

    with col1:
        qtd = st.slider(
            "Quantidade de registros",
            min_value=5,
            max_value=50,
            value=15,
            step=5
        )

    with col2:
        ordenacao = st.selectbox(
            "Ordenar por",
            [
                'Data (Mais Recente)',
                'Data (Mais Antiga)',
                'Revisões (Maior)',
                'Revisões (Menor)'
            ]
        )

    with col3:
        filtro_chamado = st.text_input(
            "Buscar Chamado",
            placeholder="Digite o número..."
        )

    df_table = df.copy()

    if ordenacao == 'Data (Mais Recente)':
        df_table = df_table.sort_values('Criado', ascending=False)
    elif ordenacao == 'Data (Mais Antiga)':
        df_table = df_table.sort_values('Criado', ascending=True)
    elif ordenacao == 'Revisões (Maior)':
        df_table = df_table.sort_values('Revisões', ascending=False)
    elif ordenacao == 'Revisões (Menor)':
        df_table = df_table.sort_values('Revisões', ascending=True)

    if filtro_chamado:
        df_table = df_table[
            df_table['Chamado'].astype(str).str.contains(filtro_chamado, na=False)
        ]

    df_table = df_table.head(qtd)

    tabela_exibicao = pd.DataFrame({
        'Chamado': df_table.get('Chamado'),
        'Tipo': df_table.get('Tipo_Chamado'),
        'Responsável': df_table.get('Responsável_Formatado'),
        'Status': df_table.get('Status'),
        'Revisões': df_table.get('Revisões'),
        'Data Criação': df_table['Criado'].dt.strftime('%d/%m/%Y %H:%M')
    })

    st.dataframe(
        tabela_exibicao,
        use_container_width=True,
        height=400
    )

    csv = tabela_exibicao.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📥 Exportar tabela",
        data=csv,
        file_name=f"ultimas_demandas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")

ultima_atualizacao = st.session_state.get(
    'ultima_atualizacao',
    get_horario_brasilia()
)

st.markdown(f"""
<div style="text-align:center; color:#6c757d; font-size:0.85rem;">
    <p style="margin:0;">
        Desenvolvido por <strong>Kewin Marcel Ramirez Ferreira</strong> | GEAT
    </p>
    <p style="margin:0;">
        Versão 5.6 • Última atualização: {ultima_atualizacao} (Brasília)
    </p>
</div>
""", unsafe_allow_html=True)
