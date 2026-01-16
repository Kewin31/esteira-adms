import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Dashboard Esteira ADMS | GEAT",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO - ESTILO EXECUTIVO
# ============================================
st.markdown("""
<style>
    /* Estilos gerais - Estilo Executivo */
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
        padding: 1.5rem;
        border-radius: 12px;
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
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3799;
        margin: 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #6c757d;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    .metric-delta-positive {
        color: #28a745;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .metric-delta-negative {
        color: #dc3545;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .section-title-exec {
        color: #1e3799;
        border-bottom: 3px solid #1e3799;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
        font-size: 1.3rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Sidebar Executivo */
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
    
    /* Gráficos */
    .plotly-graph-div {
        border-radius: 12px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Status */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-success { background: #d4edda; color: #155724; }
    .status-warning { background: #fff3cd; color: #856404; }
    .status-danger { background: #f8d7da; color: #721c24; }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #1e3799 0%, #0c2461 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 55, 153, 0.3);
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
    
    .developer-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1e3799 0%, #0c2461 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: 600;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def formatar_nome_brasileiro(nome_completo):
    """Formata nomes no estilo brasileiro"""
    if pd.isna(nome_completo):
        return "Não informado"
    
    nome = str(nome_completo).strip().title()
    
    # Lista de correções específicas
    correcoes = {
        'Da ': 'da ',
        'De ': 'de ',
        'Do ': 'do ',
        'Das ': 'das ',
        'Dos ': 'dos ',
        'E ': 'e ',
        'Adm': 'ADM',
        'Sre': 'SRE',
        'Ti': 'TI',
        'Rh': 'RH',
        'Dp': 'DP',
        'Fin': 'FIN',
        'Com': 'COM',
        'Tec': 'TEC',
    }
    
    # Aplicar correções
    for errado, correto in correcoes.items():
        if nome.startswith(errado):
            nome = correto + nome[len(errado):]
        nome = nome.replace(' ' + errado, ' ' + correto)
    
    # Extrair primeiro e último nome para e-mails
    if '@' in nome:
        partes = nome.split('@')[0].split('.')
        if len(partes) >= 2:
            primeiro = partes[0].title()
            ultimo = partes[-1].title()
            # Formatar como "Primeiro Último"
            nome = f"{primeiro} {ultimo}"
        else:
            nome = partes[0].title()
    
    return nome

def calcular_crescimento(df_atual, df_anterior, coluna):
    """Calcula crescimento percentual entre períodos"""
    if df_anterior.empty:
        return 0
    
    atual = len(df_atual)
    anterior = len(df_anterior)
    
    if anterior == 0:
        return 0
    
    crescimento = ((atual - anterior) / anterior) * 100
    return round(crescimento, 1)

def criar_indicador(valor, label, crescimento=None, icone="📊"):
    """Cria card de indicador executivo"""
    delta_html = ""
    if crescimento is not None:
        if crescimento > 0:
            delta_html = f'<div class="metric-delta-positive">📈 +{crescimento}%</div>'
        elif crescimento < 0:
            delta_html = f'<div class="metric-delta-negative">📉 {crescimento}%</div>'
        else:
            delta_html = f'<div style="color: #6c757d; font-size: 0.9rem;">➡️ Estável</div>'
    
    return f"""
    <div class="metric-card-exec">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icone}</span>
            <div>
                <div class="metric-value">{valor:,}</div>
                <div class="metric-label">{label}</div>
                {delta_html}
            </div>
        </div>
    </div>
    """

@st.cache_data
def carregar_arquivo_local(caminho_arquivo):
    """Carrega arquivo do sistema de arquivos"""
    try:
        if os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
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
            df = pd.read_csv(io.StringIO(data_str), quotechar='"', dtype={'Chamado': str})
            
            # Renomear colunas para português
            col_mapping = {
                'Chamado': 'ID_Chamado',
                'Tipo Chamado': 'Tipo_Chamado',
                'Responsável': 'Responsável',
                'Status': 'Status',
                'Criado': 'Data_Criação',
                'Modificado': 'Data_Modificação',
                'Modificado por': 'Modificado_Por',
                'Prioridade': 'Prioridade',
                'Sincronização': 'Sincronização',
                'SRE': 'SRE',
                'Empresa': 'Empresa',
                'Revisões': 'Revisões'
            }
            
            df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})
            
            # Converter datas
            date_columns = ['Data_Criação', 'Data_Modificação']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce', format='ISO8601')
            
            # Extrair informações temporais
            if 'Data_Criação' in df.columns:
                df['Ano'] = df['Data_Criação'].dt.year
                df['Mês'] = df['Data_Criação'].dt.month
                df['Dia'] = df['Data_Criação'].dt.day
                df['Mês_Ano'] = df['Data_Criação'].dt.strftime('%b/%Y')
                df['Nome_Mês'] = df['Data_Criação'].dt.strftime('%B')
                df['Nome_Mês_PT'] = df['Data_Criação'].dt.month.map({
                    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                })
                df['Ano_Mês'] = df['Data_Criação'].dt.strftime('%Y-%m')
            
            # Formatar nomes dos responsáveis
            if 'Responsável' in df.columns:
                df['Responsável_Formatado'] = df['Responsável'].apply(formatar_nome_brasileiro)
            
            # Converter revisões
            if 'Revisões' in df.columns:
                df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
            
            return df, "✅ Arquivo carregado com sucesso"
        
        else:
            return None, "Arquivo não encontrado"
    
    except Exception as e:
        return None, f"Erro: {str(e)}"

# ============================================
# SIDEBAR - FILTROS
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h3 style="color: #1e3799; margin: 0;">⚙️ Filtros</h3>
        <p style="color: #6c757d; margin: 0; font-size: 0.9rem;">Personalize sua análise</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Inicializar session state
    if 'df_original' not in st.session_state:
        st.session_state.df_original = None
        st.session_state.df_filtrado = None
        st.session_state.status_carregamento = "📂 Aguardando dados..."
    
    # Upload de arquivo
    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**📤 Importar Dados**")
        
        uploaded_file = st.file_uploader(
            "Selecione o arquivo CSV",
            type=['csv'],
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            with st.spinner('Processando dados...'):
                df_novo, status = carregar_arquivo_local(uploaded_file.name)
                if df_novo is not None:
                    # Salvar conteúdo do arquivo temporariamente
                    with open(uploaded_file.name, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    df_novo, status = carregar_arquivo_local(uploaded_file.name)
                    if df_novo is not None:
                        st.session_state.df_original = df_novo
                        st.session_state.df_filtrado = df_novo.copy()
                        st.session_state.status_carregamento = f"✅ {status}"
                        st.success("Dados carregados!")
                        os.remove(uploaded_file.name)  # Limpar arquivo temporário
                        st.rerun()
                    else:
                        st.error(status)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Carregar arquivo local automaticamente
    if st.session_state.df_original is None:
        caminhos = ['data/esteira_demandas.csv', 'esteira_demandas.csv', 'dados.csv']
        for caminho in caminhos:
            if os.path.exists(caminho):
                df_carregado, status = carregar_arquivo_local(caminho)
                if df_carregado is not None:
                    st.session_state.df_original = df_carregado
                    st.session_state.df_filtrado = df_carregado.copy()
                    st.session_state.status_carregamento = f"✅ {status}"
                    st.rerun()
                break
    
    # Filtros apenas se houver dados
    if st.session_state.df_original is not None:
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**🔍 Filtros de Análise**")
            
            df = st.session_state.df_filtrado.copy() if st.session_state.df_filtrado is not None else st.session_state.df_original.copy()
            
            # Filtro por Ano
            if 'Ano' in df.columns:
                anos = sorted(df['Ano'].dropna().unique().astype(int))
                ano_selecionado = st.selectbox(
                    "📅 Selecione o Ano",
                    options=anos,
                    index=len(anos)-1 if anos else 0
                )
                df = df[df['Ano'] == ano_selecionado]
            
            # Filtro por Responsável
            if 'Responsável_Formatado' in df.columns:
                responsaveis = ['Todos os Responsáveis'] + sorted(df['Responsável_Formatado'].dropna().unique())
                responsavel_selecionado = st.selectbox(
                    "👤 Filtrar por Responsável",
                    options=responsaveis
                )
                if responsavel_selecionado != 'Todos os Responsáveis':
                    df = df[df['Responsável_Formatado'] == responsavel_selecionado]
            
            # Busca por Chamado
            busca_chamado = st.text_input(
                "🔎 Buscar Chamado (ID)",
                placeholder="Digite o ID do chamado..."
            )
            if busca_chamado:
                df = df[df['ID_Chamado'].astype(str).str.contains(busca_chamado, na=False)]
            
            # Filtro por Status
            if 'Status' in df.columns:
                status_opcoes = ['Todos os Status'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox(
                    "📊 Filtrar por Status",
                    options=status_opcoes
                )
                if status_selecionado != 'Todos os Status':
                    df = df[df['Status'] == status_selecionado]
            
            # Filtro por Tipo
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos os Tipos'] + sorted(df['Tipo_Chamado'].dropna().unique())
                tipo_selecionado = st.selectbox(
                    "📝 Filtrar por Tipo",
                    options=tipos
                )
                if tipo_selecionado != 'Todos os Tipos':
                    df = df[df['Tipo_Chamado'] == tipo_selecionado]
            
            # Atualizar dados filtrados
            st.session_state.df_filtrado = df
            
            st.markdown(f"**📈 Registros filtrados:** {len(df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Botões de ação
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**⚡ Ações Rápidas**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Limpar Filtros", use_container_width=True):
                    st.session_state.df_filtrado = st.session_state.df_original.copy()
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Limpar Cache", use_container_width=True, type="secondary"):
                    st.cache_data.clear()
                    st.session_state.clear()
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info(st.session_state.status_carregamento)

# ============================================
# CONTEÚDO PRINCIPAL
# ============================================

# HEADER EXECUTIVO
st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="color: white; margin: 0; font-size: 1.8rem; font-weight: 700;">📊 DASHBOARD ESTEIRA ADMS</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 1rem;">
            Sistema Executivo de Análise de Demandas | Monitoramento em Tempo Real
            </p>
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 8px;">
            <p style="margin: 0; color: white; font-size: 0.9rem;">
            <strong>GEAT</strong> | Gestão Estratégica
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# INDICADORES PRINCIPAIS COM CRESCIMENTO
# ============================================
if st.session_state.df_original is not None:
    df_atual = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    # Calcular dados do período anterior para comparação
    if 'Ano' in df_atual.columns and 'Data_Criação' in df_atual.columns:
        ano_atual = df_atual['Ano'].mode()[0] if not df_atual['Ano'].mode().empty else df_atual['Ano'].max()
        df_periodo_anterior = st.session_state.df_original[
            st.session_state.df_original['Ano'] == (ano_atual - 1)
        ]
    else:
        df_periodo_anterior = pd.DataFrame()
    
    st.markdown("## 📈 INDICADORES DE DESEMPENHO")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_atual = len(df_atual)
        total_anterior = len(df_periodo_anterior)
        crescimento_total = calcular_crescimento(df_atual, df_periodo_anterior, 'total')
        st.markdown(criar_indicador(total_atual, "Total de Demandas", crescimento_total, "📋"), unsafe_allow_html=True)
    
    with col2:
        if 'Status' in df_atual.columns:
            sincronizados = len(df_atual[df_atual['Status'] == 'Sincronizado'])
            sincronizados_anterior = len(df_periodo_anterior[df_periodo_anterior['Status'] == 'Sincronizado']) if not df_periodo_anterior.empty else 0
            crescimento_sinc = calcular_crescimento(
                df_atual[df_atual['Status'] == 'Sincronizado'], 
                df_periodo_anterior[df_periodo_anterior['Status'] == 'Sincronizado'] if not df_periodo_anterior.empty else pd.DataFrame(),
                'sincronizados'
            )
            st.markdown(criar_indicador(sincronizados, "Sincronizados", crescimento_sinc, "✅"), unsafe_allow_html=True)
    
    with col3:
        if 'Tipo_Chamado' in df_atual.columns:
            correcoes = len(df_atual[df_atual['Tipo_Chamado'].str.contains('Correção|Ajuste', case=False, na=False)])
            correcoes_anterior = len(df_periodo_anterior[df_periodo_anterior['Tipo_Chamado'].str.contains('Correção|Ajuste', case=False, na=False)]) if not df_periodo_anterior.empty else 0
            crescimento_corr = calcular_crescimento(
                df_atual[df_atual['Tipo_Chamado'].str.contains('Correção|Ajuste', case=False, na=False)],
                df_periodo_anterior[df_periodo_anterior['Tipo_Chamado'].str.contains('Correção|Ajuste', case=False, na=False)] if not df_periodo_anterior.empty else pd.DataFrame(),
                'correcoes'
            )
            st.markdown(criar_indicador(correcoes, "Correções/Ajustes", crescimento_corr, "🔧"), unsafe_allow_html=True)
    
    with col4:
        if 'Revisões' in df_atual.columns:
            total_revisoes = int(df_atual['Revisões'].sum())
            total_revisoes_anterior = int(df_periodo_anterior['Revisões'].sum()) if not df_periodo_anterior.empty else 0
            crescimento_rev = 0 if total_revisoes_anterior == 0 else round(((total_revisoes - total_revisoes_anterior) / total_revisoes_anterior) * 100, 1)
            st.markdown(criar_indicador(total_revisoes, "Total de Revisões", crescimento_rev, "📝"), unsafe_allow_html=True)
    
    # ============================================
    # GRÁFICO DE DEMANDAS POR MÊS COM SELEÇÃO DE ANO
    # ============================================
    st.markdown("---")
    st.markdown('<div class="section-title-exec">📅 DEMANDAS POR MÊS</div>', unsafe_allow_html=True)
    
    if 'Ano' in df_atual.columns and 'Nome_Mês_PT' in df_atual.columns:
        col_ano, col_vazio = st.columns([1, 3])
        
        with col_ano:
            anos_disponiveis = sorted(df_atual['Ano'].unique())
            ano_grafico = st.selectbox(
                "Selecione o ano para análise:",
                options=anos_disponiveis,
                key="ano_grafico"
            )
        
        # Filtrar dados para o ano selecionado
        df_ano = df_atual[df_atual['Ano'] == ano_grafico].copy()
        
        if not df_ano.empty:
            # Ordenar meses corretamente
            ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                          'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            
            demandas_por_mes = df_ano.groupby('Nome_Mês_PT').size().reindex(ordem_meses).reset_index()
            demandas_por_mes.columns = ['Mês', 'Quantidade']
            demandas_por_mes = demandas_por_mes.fillna(0)
            
            # Criar gráfico com valores
            fig_mes = go.Figure()
            
            fig_mes.add_trace(go.Bar(
                x=demandas_por_mes['Mês'],
                y=demandas_por_mes['Quantidade'],
                text=demandas_por_mes['Quantidade'].astype(int),
                textposition='outside',
                marker_color='#1e3799',
                marker_line_color='#0c2461',
                marker_line_width=1,
                opacity=0.9
            ))
            
            fig_mes.update_layout(
                title=f"Demandas em {ano_grafico}",
                xaxis_title="Mês",
                yaxis_title="Quantidade de Demandas",
                plot_bgcolor='white',
                height=450,
                showlegend=False,
                margin=dict(t=50, b=50, l=50, r=50),
                xaxis=dict(
                    tickangle=45,
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                yaxis=dict(
                    gridcolor='rgba(0,0,0,0.05)'
                )
            )
            
            # Adicionar valor total
            total_ano = int(demandas_por_mes['Quantidade'].sum())
            fig_mes.add_annotation(
                x=0.5, y=0.95,
                xref="paper", yref="paper",
                text=f"Total no ano: {total_ano:,} demandas",
                showarrow=False,
                font=dict(size=12, color="#1e3799"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#1e3799",
                borderwidth=1,
                borderpad=4
            )
            
            st.plotly_chart(fig_mes, use_container_width=True)
            
            # Estatísticas mensais
            mes_max = demandas_por_mes.loc[demandas_por_mes['Quantidade'].idxmax()]
            mes_min = demandas_por_mes.loc[demandas_por_mes['Quantidade'].idxmin()]
            
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                st.metric("Mês com mais demandas", f"{mes_max['Mês']}: {int(mes_max['Quantidade']):,}")
            with col_stats2:
                st.metric("Mês com menos demandas", f"{mes_min['Mês']}: {int(mes_min['Quantidade']):,}")
            with col_stats3:
                media_mensal = int(demandas_por_mes['Quantidade'].mean())
                st.metric("Média mensal", f"{media_mensal:,}")
    
    # ============================================
    # ERROS POR MÊS/ANO (BASEADO EM REVISÕES)
    # ============================================
    st.markdown("---")
    st.markdown('<div class="section-title-exec">📈 ANÁLISE DE REVISÕES POR MÊS</div>', unsafe_allow_html=True)
    
    if 'Revisões' in df_atual.columns and 'Ano_Mês' in df_atual.columns:
        # Considerar revisões como indicador de retrabalho/erros
        df_revisoes = df_atual[df_atual['Revisões'] > 0].copy()
        
        if not df_revisoes.empty:
            revisoes_por_mes = df_revisoes.groupby('Ano_Mês').agg({
                'Revisões': 'sum',
                'ID_Chamado': 'count'
            }).reset_index()
            
            revisoes_por_mes.columns = ['Período', 'Total_Revisões', 'Chamados_Com_Revisão']
            revisoes_por_mes = revisoes_por_mes.sort_values('Período')
            
            fig_erros = go.Figure()
            
            fig_erros.add_trace(go.Bar(
                x=revisoes_por_mes['Período'],
                y=revisoes_por_mes['Total_Revisões'],
                name='Total de Revisões',
                text=revisoes_por_mes['Total_Revisões'],
                textposition='outside',
                marker_color='#e74c3c',
                opacity=0.9
            ))
            
            fig_erros.add_trace(go.Scatter(
                x=revisoes_por_mes['Período'],
                y=revisoes_por_mes['Chamados_Com_Revisão'],
                name='Chamados com Revisão',
                mode='lines+markers',
                line=dict(color='#f39c12', width=3),
                yaxis='y2'
            ))
            
            fig_erros.update_layout(
                title="Evolução de Revisões (Indicador de Retrabalho)",
                xaxis_title="Período (Mês/Ano)",
                yaxis_title="Total de Revisões",
                yaxis2=dict(
                    title="Chamados com Revisão",
                    overlaying='y',
                    side='right'
                ),
                plot_bgcolor='white',
                height=450,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                xaxis=dict(tickangle=45),
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            st.plotly_chart(fig_erros, use_container_width=True)
            
            # Estatísticas de revisões
            col_rev1, col_rev2, col_rev3 = st.columns(3)
            with col_rev1:
                st.metric("Média de revisões por chamado", f"{df_atual['Revisões'].mean():.1f}")
            with col_rev2:
                chamados_com_revisao = len(df_atual[df_atual['Revisões'] > 0])
                percent_revisao = (chamados_com_revisao / len(df_atual)) * 100
                st.metric("Chamados com revisão", f"{percent_revisao:.1f}%")
            with col_rev3:
                st.metric("Maior nº de revisões", f"{int(df_atual['Revisões'].max())}")
        else:
            st.info("✅ Nenhuma revisão registrada no período")
    
    # ============================================
    # TOP RANKINGS
    # ============================================
    col_rank1, col_rank2 = st.columns(2)
    
    with col_rank1:
        st.markdown('<div class="section-title-exec">👥 TOP 10 - RESPONSÁVEIS</div>', unsafe_allow_html=True)
        
        if 'Responsável_Formatado' in df_atual.columns:
            top_responsaveis = df_atual['Responsável_Formatado'].value_counts().head(10).reset_index()
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
                textposition='outside',
                marker_line_color='#0c2461',
                marker_line_width=1
            )
            
            fig_top.update_layout(
                height=400,
                plot_bgcolor='white',
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(t=20, b=20, l=20, r=20)
            )
            
            st.plotly_chart(fig_top, use_container_width=True)
    
    with col_rank2:
        st.markdown('<div class="section-title-exec">🏆 TOP SRE - SINCRONISMOS</div>', unsafe_allow_html=True)
        
        if 'SRE' in df_atual.columns and 'Status' in df_atual.columns:
            df_sincronizados = df_atual[df_atual['Status'] == 'Sincronizado']
            
            if not df_sincronizados.empty and 'SRE' in df_sincronizados.columns:
                top_sre = df_sincronizados['SRE'].value_counts().head(10).reset_index()
                top_sre.columns = ['SRE', 'Sincronismos']
                
                fig_sre = px.bar(
                    top_sre,
                    x='Sincronismos',
                    y='SRE',
                    orientation='h',
                    title='',
                    text='Sincronismos',
                    color='Sincronismos',
                    color_continuous_scale='Greens'
                )
                
                fig_sre.update_traces(
                    textposition='outside',
                    marker_line_color='#27ae60',
                    marker_line_width=1
                )
                
                fig_sre.update_layout(
                    height=400,
                    plot_bgcolor='white',
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'},
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                
                st.plotly_chart(fig_sre, use_container_width=True)
            else:
                st.info("Sem dados de SRE disponíveis")
    
    # ============================================
    # VISÃO DETALHADA
    # =
