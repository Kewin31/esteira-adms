import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import os
import warnings
warnings.filterwarnings('ignore')

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
# MAPEAMENTO COMPLETO DAS EMPRESAS
# ============================================
MAPEAMENTO_EMPRESAS = {
    'EMR': {
        'sigla': 'MG',
        'estado': 'Minas Gerais',
        'regiao': 'Sudeste',
        'nome_completo': 'Energisa Minas Gerais',
        'latitude': -19.5,
        'longitude': -44.5
    },
    'EPB': {
        'sigla': 'PB',
        'estado': 'Paraíba',
        'regiao': 'Nordeste',
        'nome_completo': 'Energisa Paraíba',
        'latitude': -7.2,
        'longitude': -36.8
    },
    'ESE': {
        'sigla': 'SE',
        'estado': 'Sergipe',
        'regiao': 'Nordeste',
        'nome_completo': 'Energisa Sergipe',
        'latitude': -10.9,
        'longitude': -37.1
    },
    'ESS': {
        'sigla': 'SP',
        'estado': 'São Paulo',
        'regiao': 'Sudeste',
        'nome_completo': 'Energisa Sul/Sudeste',
        'latitude': -23.5,
        'longitude': -46.6
    },
    'EMS': {
        'sigla': 'MS',
        'estado': 'Mato Grosso do Sul',
        'regiao': 'Centro-Oeste',
        'nome_completo': 'Energisa Mato Grosso do Sul',
        'latitude': -20.5,
        'longitude': -54.6
    },
    'EMT': {
        'sigla': 'MT',
        'estado': 'Mato Grosso',
        'regiao': 'Centro-Oeste',
        'nome_completo': 'Energisa Mato Grosso',
        'latitude': -12.5,
        'longitude': -55.0
    },
    'ETO': {
        'sigla': 'TO',
        'estado': 'Tocantins',
        'regiao': 'Norte',
        'nome_completo': 'Energisa Tocantins',
        'latitude': -10.2,
        'longitude': -48.3
    },
    'ERO': {
        'sigla': 'RO',
        'estado': 'Rondônia',
        'regiao': 'Norte',
        'nome_completo': 'Energisa Rondônia',
        'latitude': -10.8,
        'longitude': -63.5
    },
    'EAC': {
        'sigla': 'AC',
        'estado': 'Acre',
        'regiao': 'Norte',
        'nome_completo': 'Energisa Acre',
        'latitude': -9.0,
        'longitude': -70.0
    }
}

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Mapa de Sincronismos - Energisa",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown(f"""
<style>
    .stApp {{
        background-color: {COR_CINZA_FUNDO};
    }}
    
    .main-header {{
        background: linear-gradient(135deg, {COR_AZUL_PETROLEO} 0%, {COR_AZUL_ESCURO} 100%);
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        border-radius: 0;
        box-shadow: 0 4px 15px rgba(2, 138, 159, 0.3);
    }}
    
    .metric-card {{
        background: {COR_BRANCO};
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid {COR_CINZA_BORDA};
        text-align: center;
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
    }}
    
    .metric-label {{
        font-size: 0.85rem;
        color: {COR_CINZA_TEXTO};
    }}
    
    .info-card {{
        background: linear-gradient(135deg, {COR_BRANCO}, #E0F7FA);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {COR_AZUL_PETROLEO};
        margin-bottom: 1rem;
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
    
    .footer {{
        text-align: center;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 2px solid {COR_CINZA_BORDA};
        color: {COR_CINZA_TEXTO};
        font-size: 0.85rem;
    }}
    
    .stButton > button {{
        background: {COR_AZUL_ESCURO};
        color: {COR_BRANCO};
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        background: {COR_AZUL_PETROLEO};
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 89, 115, 0.3);
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
@st.cache_data(ttl=300)
def carregar_dados(uploaded_file=None, caminho_arquivo=None):
    """Carrega e processa os dados do CSV"""
    try:
        if uploaded_file:
            conteudo = uploaded_file.getvalue().decode('utf-8-sig')
        elif caminho_arquivo and os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8-sig') as f:
                conteudo = f.read()
        else:
            return None, "Nenhum arquivo fornecido"
        
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
            return None, "Formato de arquivo inválido"
        
        data_str = '\n'.join(lines[header_line:])
        df = pd.read_csv(io.StringIO(data_str), quotechar='"')
        
        # Renomear colunas
        col_mapping = {
            'Chamado': 'Chamado',
            'Tipo Chamado': 'Tipo_Chamado',
            'Responsável': 'Responsável',
            'Status': 'Status',
            'Criado': 'Criado',
            'Sincronização': 'Sincronização',
            'Empresa': 'Empresa',
            'Revisões': 'Revisões'
        }
        
        df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})
        
        # Converter datas
        if 'Criado' in df.columns:
            df['Criado'] = pd.to_datetime(df['Criado'], errors='coerce')
            df['Ano'] = df['Criado'].dt.year
            df['Mês'] = df['Criado'].dt.month
        
        # Converter Revisões para numérico
        if 'Revisões' in df.columns:
            df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
        
        return df, "✅ Dados carregados com sucesso"
    
    except Exception as e:
        return None, f"Erro: {str(e)}"

def processar_dados_mapa(df, empresas_selecionadas=None, ano_filtro=None, mes_filtro=None):
    """Processa os dados para gerar as métricas do mapa"""
    
    # Filtrar apenas sincronizados
    df_sinc = df[df['Status'] == 'Sincronizado'].copy()
    
    # Aplicar filtros de data
    if ano_filtro and ano_filtro != 'Todos':
        df_sinc = df_sinc[df_sinc['Ano'] == int(ano_filtro)]
    
    if mes_filtro and mes_filtro != 'Todos':
        df_sinc = df_sinc[df_sinc['Mês'] == int(mes_filtro)]
    
    # Filtrar empresas selecionadas
    if empresas_selecionadas and 'Todas' not in empresas_selecionadas:
        df_sinc = df_sinc[df_sinc['Empresa'].isin(empresas_selecionadas)]
    
    # Contar sincronismos por empresa
    sinc_por_empresa = df_sinc['Empresa'].value_counts().reset_index()
    sinc_por_empresa.columns = ['Empresa', 'Sincronismos']
    
    # Preparar dados para o mapa
    dados_mapa = []
    total_sinc = 0
    
    for empresa in sinc_por_empresa['Empresa']:
        if empresa in MAPEAMENTO_EMPRESAS:
            info = MAPEAMENTO_EMPRESAS[empresa]
            qtd = sinc_por_empresa[sinc_por_empresa['Empresa'] == empresa]['Sincronismos'].values[0]
            dados_mapa.append({
                'sigla': info['sigla'],
                'estado': info['estado'],
                'regiao': info['regiao'],
                'empresa': empresa,
                'empresa_nome': info['nome_completo'],
                'sincronismos': qtd,
                'latitude': info['latitude'],
                'longitude': info['longitude']
            })
            total_sinc += qtd
    
    # Adicionar empresas com zero sincronismos se estiverem selecionadas
    if empresas_selecionadas and 'Todas' not in empresas_selecionadas:
        for empresa in empresas_selecionadas:
            if empresa in MAPEAMENTO_EMPRESAS and empresa not in sinc_por_empresa['Empresa'].values:
                info = MAPEAMENTO_EMPRESAS[empresa]
                dados_mapa.append({
                    'sigla': info['sigla'],
                    'estado': info['estado'],
                    'regiao': info['regiao'],
                    'empresa': empresa,
                    'empresa_nome': info['nome_completo'],
                    'sincronismos': 0,
                    'latitude': info['latitude'],
                    'longitude': info['longitude']
                })
    
    return pd.DataFrame(dados_mapa), total_sinc

def criar_mapa_coropletico(df_mapa):
    """Cria o mapa coroplético (por estados)"""
    if df_mapa.empty:
        return None
    
    fig = px.choropleth(
        df_mapa,
        locations='sigla',
        locationmode="USA-states",
        color='sincronismos',
        hover_name='estado',
        hover_data={
            'empresa_nome': True,
            'sincronismos': True,
            'regiao': True
        },
        color_continuous_scale=[
            [0.0, COR_CINZA_TEXTO],
            [0.33, COR_AZUL_PETROLEO],
            [0.66, COR_AZUL_ESCURO],
            [1.0, COR_VERDE_ESCURO]
        ],
        title="<b>Mapa de Sincronizações por Estado</b>",
        labels={'sincronismos': 'Nº de Sincronizações'}
    )
    
    # Personalizar o popup
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                      "Empresa: %{customdata[0]}<br>" +
                      "Sincronizações: <b>%{customdata[1]}</b><br>" +
                      "Região: %{customdata[2]}<extra></extra>"
    )
    
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator"
    )
    
    fig.update_layout(
        height=550,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title="Sincronizações",
            thicknessmode="pixels",
            thickness=20,
            lenmode="pixels",
            len=300,
            yanchor="middle",
            y=0.5
        )
    )
    
    return fig

def criar_mapa_bolhas(df_mapa):
    """Cria um mapa de bolhas (scatter geo) para visualização alternativa"""
    if df_mapa.empty:
        return None
    
    # Filtrar apenas empresas com sincronismos > 0 para as bolhas
    df_bolhas = df_mapa[df_mapa['sincronismos'] > 0].copy()
    
    if df_bolhas.empty:
        return None
    
    fig = px.scatter_geo(
        df_bolhas,
        lat='latitude',
        lon='longitude',
        size='sincronismos',
        hover_name='estado',
        text='empresa',
        color='sincronismos',
        color_continuous_scale=[
            [0.0, COR_AZUL_PETROLEO],
            [0.5, COR_AZUL_ESCURO],
            [1.0, COR_VERDE_ESCURO]
        ],
        size_max=50,
        title="<b>Mapa de Bolhas - Volume de Sincronizações</b>",
        labels={'sincronismos': 'Nº de Sincronizações'}
    )
    
    # Personalizar o popup
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                      "Empresa: %{text}<br>" +
                      "Sincronizações: <b>%{marker.size}</b><br>" +
                      "<extra></extra>"
    )
    
    fig.update_geos(
        projection_type="natural earth",
        showcountries=False,
        showsubunits=True,
        showland=True,
        landcolor='rgb(243, 243, 243)',
        subunitcolor='rgb(217, 217, 217)'
    )
    
    fig.update_layout(
        height=550,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title="Sincronizações",
            thicknessmode="pixels",
            thickness=20
        )
    )
    
    return fig

def criar_grafico_barras(df_mapa):
    """Cria gráfico de barras comparativo"""
    if df_mapa.empty:
        return None
    
    df_barras = df_mapa.sort_values('sincronismos', ascending=True)
    
    fig = go.Figure()
    
    cores = []
    for val in df_barras['sincronismos']:
        if val == 0:
            cores.append(COR_CINZA_TEXTO)
        elif val < 10:
            cores.append(COR_AZUL_PETROLEO)
        elif val < 30:
            cores.append(COR_AZUL_ESCURO)
        else:
            cores.append(COR_VERDE_ESCURO)
    
    fig.add_trace(go.Bar(
        x=df_barras['sincronismos'],
        y=df_barras['empresa_nome'],
        orientation='h',
        text=df_barras['sincronismos'],
        textposition='outside',
        marker_color=cores,
        marker_line_color=COR_AZUL_ESCURO,
        marker_line_width=1,
        hovertemplate="Empresa: %{y}<br>Sincronizações: %{x}<extra></extra>"
    ))
    
    fig.update_layout(
        title="<b>Ranking de Sincronizações por Empresa</b>",
        xaxis_title="Número de Sincronizações",
        yaxis_title="",
        height=400,
        showlegend=False,
        plot_bgcolor=COR_BRANCO,
        xaxis=dict(gridcolor=COR_CINZA_BORDA),
        yaxis=dict(gridcolor=COR_CINZA_BORDA)
    )
    
    return fig

# ============================================
# HEADER
# ============================================
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="color: {COR_BRANCO}; margin: 0;">🗺️ Mapa de Sincronismos</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0;">
                Visualização geográfica das sincronizações por empresa
            </p>
        </div>
        <div style="text-align: right;">
            <p style="color: rgba(255,255,255,0.9); margin: 0;">Energisa Group</p>
            <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 0.8rem;">
                {datetime.now().strftime('%d/%m/%Y')}
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    st.markdown("---")
    
    # Upload de arquivo
    st.markdown("### 📂 Fonte de Dados")
    
    uploaded_file = st.file_uploader(
        "Carregar arquivo CSV",
        type=['csv'],
        help="Selecione o arquivo CSV com os dados das demandas"
    )
    
    # Opção de arquivo local
    caminhos_possiveis = [
        "esteira_demandas.csv",
        "data/esteira_demandas.csv",
        "dados/esteira_demandas.csv",
    ]
    
    arquivo_local = None
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            arquivo_local = caminho
            break
    
    if uploaded_file:
        with st.spinner('Carregando dados...'):
            df, msg = carregar_dados(uploaded_file=uploaded_file)
            if df is not None:
                st.session_state.df = df
                st.success(msg)
            else:
                st.error(msg)
    elif arquivo_local:
        if 'df' not in st.session_state:
            with st.spinner('Carregando dados locais...'):
                df, msg = carregar_dados(caminho_arquivo=arquivo_local)
                if df is not None:
                    st.session_state.df = df
                    st.success(f"✅ Dados carregados: {arquivo_local}")
                else:
                    st.error(msg)
        else:
            st.success(f"✅ Dados carregados: {arquivo_local}")
    
    if 'df' in st.session_state:
        df = st.session_state.df
        
        st.markdown("---")
        st.markdown("### 🎛️ Filtros")
        
        # Filtro de empresas
        empresas_disponiveis = df['Empresa'].dropna().unique()
        empresas_opcoes = ['Todas'] + sorted([e for e in empresas_disponiveis if e in MAPEAMENTO_EMPRESAS])
        
        empresas_selecionadas = st.multiselect(
            "🏢 Empresas",
            options=empresas_opcoes,
            default=['Todas'],
            help="Selecione as empresas para visualizar no mapa"
        )
        
        # Filtro de ano
        if 'Ano' in df.columns:
            anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
            anos_opcoes = ['Todos'] + list(anos_disponiveis)
            ano_filtro = st.selectbox("📅 Ano", options=anos_opcoes, index=0)
        else:
            ano_filtro = 'Todos'
        
        # Filtro de mês
        if 'Mês' in df.columns and ano_filtro != 'Todos':
            df_ano = df[df['Ano'] == int(ano_filtro)]
            meses_disponiveis = sorted(df_ano['Mês'].dropna().unique().astype(int))
            meses_opcoes = ['Todos'] + [f"{m:02d}" for m in meses_disponiveis]
            mes_filtro = st.selectbox("📆 Mês", options=meses_opcoes, index=0)
        else:
            mes_filtro = 'Todos'
        
        # Tipo de visualização
        st.markdown("---")
        st.markdown("### 🗺️ Tipo de Mapa")
        
        tipo_mapa = st.radio(
            "Visualização",
            options=["Coroplético (Estados)", "Bolhas (Pontos)", "Ambos"],
            index=0,
            help="Coroplético: cores nos estados | Bolhas: círculos proporcionais"
        )
        
        # Status dos dados
        st.markdown("---")
        st.markdown("### 📊 Status")
        
        total_registros = len(df)
        total_sinc = len(df[df['Status'] == 'Sincronizado'])
        
        st.markdown(f"""
        <div class="info-card">
            <strong>📈 Total de registros:</strong> {total_registros:,}<br>
            <strong>✅ Sincronizados:</strong> {total_sinc:,}<br>
            <strong>🏢 Empresas mapeadas:</strong> {len([e for e in df['Empresa'].unique() if e in MAPEAMENTO_EMPRESAS])}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Recarregar Dados", use_container_width=True):
            st.cache_data.clear()
            if 'df' in st.session_state:
                del st.session_state.df
            st.rerun()

# ============================================
# CORPO PRINCIPAL
# ============================================
if 'df' in st.session_state:
    df = st.session_state.df
    
    # Processar dados para o mapa
    df_mapa, total_sinc_filtrado = processar_dados_mapa(
        df,
        empresas_selecionadas=empresas_selecionadas,
        ano_filtro=ano_filtro,
        mes_filtro=mes_filtro
    )
    
    # Métricas principais
    st.markdown("### 📊 Indicadores Gerais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_sinc_filtrado:,}</div>
            <div class="metric-label">Total Sincronizações</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        empresas_ativas = len(df_mapa[df_mapa['sincronismos'] > 0])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{empresas_ativas}</div>
            <div class="metric-label">Empresas com Sinc.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if not df_mapa.empty:
            media_sinc = df_mapa['sincronismos'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{media_sinc:.1f}</div>
                <div class="metric-label">Média por Empresa</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">0</div>
                <div class="metric-label">Média por Empresa</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if not df_mapa.empty:
            max_sinc = df_mapa['sincronismos'].max()
            empresa_max = df_mapa[df_mapa['sincronismos'] == max_sinc]['empresa_nome'].values[0] if max_sinc > 0 else "Nenhuma"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{max_sinc:,}</div>
                <div class="metric-label">🏆 Maior: {empresa_max[:20]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">0</div>
                <div class="metric-label">Maior Sincronização</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mapas
    if tipo_mapa in ["Coroplético (Estados)", "Ambos"]:
        st.markdown('<div class="section-title">🗺️ MAPA COROPLÉTICO</div>', unsafe_allow_html=True)
        
        fig_coropletico = criar_mapa_coropletico(df_mapa)
        if fig_coropletico:
            st.plotly_chart(fig_coropletico, use_container_width=True, config={'displayModeBar': True})
        else:
            st.warning("⚠️ Não há dados suficientes para gerar o mapa coroplético.")
    
    if tipo_mapa in ["Bolhas (Pontos)", "Ambos"]:
        if tipo_mapa == "Ambos":
            st.markdown('<div class="section-title" style="margin-top: 2rem;">📍 MAPA DE BOLHAS</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-title">📍 MAPA DE BOLHAS</div>', unsafe_allow_html=True)
        
        fig_bolhas = criar_mapa_bolhas(df_mapa)
        if fig_bolhas:
            st.plotly_chart(fig_bolhas, use_container_width=True, config={'displayModeBar': True})
        else:
            st.info("ℹ️ Nenhuma empresa com sincronizações para exibir no mapa de bolhas.")
    
    # Gráfico de barras
    st.markdown('<div class="section-title" style="margin-top: 2rem;">📊 RANKING DE SINCRONIZAÇÕES</div>', unsafe_allow_html=True)
    
    fig_barras = criar_grafico_barras(df_mapa)
    if fig_barras:
        st.plotly_chart(fig_barras, use_container_width=True, config={'displayModeBar': True})
    
    # Tabela detalhada
    with st.expander("📋 Ver Detalhes por Empresa", expanded=False):
        if not df_mapa.empty:
            tabela_detalhes = df_mapa[['empresa_nome', 'sigla', 'regiao', 'sincronismos']].copy()
            tabela_detalhes.columns = ['Empresa', 'UF', 'Região', 'Sincronizações']
            tabela_detalhes = tabela_detalhes.sort_values('Sincronizações', ascending=False)
            
            st.dataframe(
                tabela_detalhes,
                use_container_width=True,
                column_config={
                    "Empresa": st.column_config.TextColumn("Empresa", width="large"),
                    "UF": st.column_config.TextColumn("UF", width="small"),
                    "Região": st.column_config.TextColumn("Região", width="medium"),
                    "Sincronizações": st.column_config.NumberColumn("Sinc.", format="%d")
                }
            )
            
            # Botão para exportar
            csv = tabela_detalhes.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Exportar dados para CSV",
                data=csv,
                file_name=f"sincronismos_empresas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # Legenda e informações
    st.markdown("---")
    with st.expander("ℹ️ Sobre este Dashboard", expanded=False):
        st.markdown("""
        **🗺️ Mapa de Sincronismos - Guia Rápido**
        
        Este dashboard visualiza geograficamente os sincronismos por empresa da Energisa.
        
        **Tipos de Visualização:**
        - **Mapa Coroplético**: Cores nos estados representam o volume de sincronizações
        - **Mapa de Bolhas**: Círculos proporcionais ao volume, posicionados geograficamente
        
        **Interpretação:**
        - 🟢 **Verde escuro**: Alto volume de sincronizações
        - 🔵 **Azul**: Volume médio
        - ⚪ **Cinza**: Sem sincronizações no período
        
        **Filtros Disponíveis:**
        - Selecione empresas específicas para análise focada
        - Filtre por ano e mês para análise temporal
        - Combine diferentes visualizações para insights mais profundos
        
        **Empresas Mapeadas:**
        - **EMR** - Energisa Minas Gerais (MG)
        - **EPB** - Energisa Paraíba (PB)
        - **ESE** - Energisa Sergipe (SE)
        - **ESS** - Energisa Sul/Sudeste (SP)
        - **EMS** - Energisa Mato Grosso do Sul (MS)
        - **EMT** - Energisa Mato Grosso (MT)
        - **ETO** - Energisa Tocantins (TO)
        - **ERO** - Energisa Rondônia (RO)
        - **EAC** - Energisa Acre (AC)
        
        **Regiões:**
        - **Sudeste**: MG, SP
        - **Nordeste**: PB, SE
        - **Centro-Oeste**: MS, MT
        - **Norte**: TO, RO, AC
        """)
    
else:
    # Estado sem dados
    st.markdown(f"""
    <div style="text-align: center; padding: 4rem; background: {COR_CINZA_FUNDO}; border-radius: 12px; margin-top: 2rem;">
        <h2 style="color: {COR_AZUL_ESCURO};">🗺️ Bem-vindo ao Mapa de Sincronismos</h2>
        <p style="color: {COR_CINZA_TEXTO}; font-size: 1.1rem; margin: 1rem 0;">
            Para começar, carregue um arquivo CSV com os dados das demandas.
        </p>
        <div style="background: {COR_BRANCO}; padding: 2rem; border-radius: 8px; display: inline-block; text-align: left;">
            <h4 style="color: {COR_AZUL_ESCURO};">📋 Instruções:</h4>
            <p>1. Use a barra lateral esquerda para fazer upload do arquivo CSV</p>
            <p>2. O arquivo deve conter as colunas: Chamado, Status, Empresa, Criado, etc.</p>
            <p>3. Após o carregamento, o mapa será gerado automaticamente</p>
            <p>4. Utilize os filtros para refinar a visualização</p>
        </div>
        <p style="margin-top: 2rem; color: {COR_CINZA_TEXTO};">
            <strong>Empresas suportadas:</strong> EMR, EPB, ESE, ESS, EMS, EMT, ETO, ERO, EAC
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================
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
        © 2024 Mapa de Sincronismos | Sistema proprietário - Energisa Group
        </p>
        <p style="margin: 0.2rem 0 0 0; color: {COR_CINZA_TEXTO}; font-size: 0.7rem;">
        Versão 1.0 | Mapa Interativo de Sincronizações | Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
