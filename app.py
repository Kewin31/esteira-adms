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
    page_title="Esteira ADMS - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO - ATUALIZADO
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
    
    /* Sidebar atualizada */
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
    
    /* Selectboxes e Inputs */
    .stSelectbox, .stTextInput {
        margin-bottom: 1rem;
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
    
    /* Responsividade dos gráficos */
    .plotly-graph-div {
        border-radius: 10px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
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

def calcular_crescimento(valor_atual, valor_anterior):
    """Calcula crescimento percentual"""
    if valor_anterior == 0:
        return None, "neutral"
    
    crescimento = ((valor_atual - valor_anterior) / valor_anterior) * 100
    
    if crescimento > 0:
        return round(crescimento, 1), "positive"
    elif crescimento < 0:
        return round(crescimento, 1), "negative"
    else:
        return None, "neutral"

def calcular_percentual_revisoes(df):
    """Calcula percentual de demandas sem revisões"""
    if 'Revisões' not in df.columns or len(df) == 0:
        return 0
    
    demandas_sem_revisoes = len(df[df['Revisões'] == 0])
    percentual = (demandas_sem_revisoes / len(df)) * 100
    return round(percentual, 1)

def criar_card_indicador(valor, label, delta_info=None, icone="📊"):
    """Cria card de indicador visualmente atraente"""
    delta_html = ""
    if delta_info is not None:
        valor_delta, tipo_delta = delta_info
        if tipo_delta == "positive" and valor_delta is not None:
            delta_html = f'<div class="metric-delta-positive">📈 +{valor_delta}%</div>'
        elif tipo_delta == "negative" and valor_delta is not None:
            delta_html = f'<div class="metric-delta-negative">📉 {valor_delta}%</div>'
        # Não mostra nada se for "neutral" ou valor_delta for None
    
    return f'''
    <div class="metric-card-exec">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <span style="font-size: 1.5rem;">{icone}</span>
            <div style="flex-grow: 1;">
                <div class="metric-value">{valor:,}</div>
                <div class="metric-label">{label}</div>
                {delta_html}
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

# ============================================
# SIDEBAR - FILTROS
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
                    st.success("✅ Dados carregados!")
                    st.rerun()
                else:
                    st.error(f"❌ {status}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CARREGAR ARQUIVO LOCAL AUTOMATICAMENTE
    if st.session_state.df_original is None:
        caminhos = ['data/esteira_demandas.csv', 'esteira_demandas.csv', 'dados.csv']
        for caminho in caminhos:
            if os.path.exists(caminho):
                df_local, status = carregar_dados(caminho_arquivo=caminho)
                if df_local is not None:
                    st.session_state.df_original = df_local
                    st.session_state.df_filtrado = df_local.copy()
                    st.rerun()
                break
    
    # FILTROS APENAS SE HOUVER DADOS
    if st.session_state.df_original is not None:
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**🔍 Filtros de Análise**")
            
            df = st.session_state.df_original.copy()
            
            # FILTRO POR ANO
            if 'Ano' in df.columns:
                anos = sorted(df['Ano'].dropna().unique().astype(int))
                ano_selecionado = st.selectbox(
                    "📅 Ano de Análise",
                    options=anos,
                    index=len(anos)-1 if anos else 0
                )
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
        
        # BOTÕES DE AÇÃO
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**⚡ Ações Rápidas**")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔄 Limpar Filtros", use_container_width=True):
                    st.session_state.df_filtrado = st.session_state.df_original.copy()
                    st.rerun()
            
            with col_btn2:
                if st.button("🗑️ Limpar Cache", use_container_width=True, type="secondary"):
                    st.cache_data.clear()
                    st.session_state.clear()
                    st.success("Cache limpo!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📂 Aguardando upload de dados...")

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
            Sistema de Análise de Demandas | SRE & Monitoramento
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 0.2rem 0 0 0; font-size: 0.9rem;">
            Empresas: Energisa, Concessionárias Regionais | Função SRE: Garantia de Disponibilidade
            </p>
        </div>
        <div style="background: rgba(255,255,255,0.15); padding: 0.5rem 1rem; border-radius: 8px; text-align: center;">
            <p style="margin: 0; color: white; font-size: 0.9rem; font-weight: 600;">
            ⚡ SRE Metrics
            </p>
            <p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 0.8rem;">
            SLA: 99.9% | MTTR: &lt; 4h
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
    # INDICADORES PRINCIPAIS ATUALIZADOS
    # ============================================
    st.markdown("## 📈 INDICADORES DE DESEMPENHO")
    
    # Calcular dados do período anterior
    if 'Ano' in df.columns:
        ano_atual = df['Ano'].mode()[0] if not df['Ano'].mode().empty else df['Ano'].max()
        df_ano_anterior = st.session_state.df_original[
            st.session_state.df_original['Ano'] == (ano_atual - 1)
        ] if not st.session_state.df_original.empty else pd.DataFrame()
    else:
        df_ano_anterior = pd.DataFrame()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_atual = len(df)
        total_anterior = len(df_ano_anterior) if not df_ano_anterior.empty else 0
        crescimento_total = calcular_crescimento(total_atual, total_anterior)
        st.markdown(criar_card_indicador(
            total_atual, 
            "Total de Demandas", 
            crescimento_total, 
            "📋"
        ), unsafe_allow_html=True)
    
    with col2:
        if 'Status' in df.columns:
            sincronizados = len(df[df['Status'] == 'Sincronizado'])
            sincronizados_anterior = len(df_ano_anterior[df_ano_anterior['Status'] == 'Sincronizado']) if not df_ano_anterior.empty else 0
            crescimento_sinc = calcular_crescimento(sincronizados, sincronizados_anterior)
            st.markdown(criar_card_indicador(
                sincronizados,
                "Sincronizados",
                crescimento_sinc,
                "✅"
            ), unsafe_allow_html=True)
    
    with col3:
        if 'Tipo_Chamado' in df.columns:
            correcoes = len(df[df['Tipo_Chamado'].str.contains('Correção|Ajuste', case=False, na=False)])
            correcoes_anterior = len(df_ano_anterior[df_ano_anterior['Tipo_Chamado'].str.contains('Correção|Ajuste', case=False, na=False)]) if not df_ano_anterior.empty else 0
            crescimento_corr = calcular_crescimento(correcoes, correcoes_anterior)
            st.markdown(criar_card_indicador(
                correcoes,
                "Correções/Ajustes",
                crescimento_corr,
                "🔧"
            ), unsafe_allow_html=True)
    
    with col4:
        if 'Revisões' in df.columns:
            # Percentual de demandas sem revisões
            percentual_sem_revisoes = calcular_percentual_revisoes(df)
            st.markdown(criar_card_indicador(
                f"{percentual_sem_revisoes}%",
                "Sem Revisões",
                None,  # Sem delta para este indicador
                "📈"
            ), unsafe_allow_html=True)
    
    # ============================================
    # DEMANDAS POR MÊS - GRÁFICO DE LINHA
    # ============================================
    st.markdown("---")
    
    # Cabeçalho com seletor de ano
    col_titulo, col_seletor = st.columns([3, 1])
    
    with col_titulo:
        st.markdown('<div class="section-title-exec">📅 EVOLUÇÃO DE DEMANDAS POR MÊS</div>', unsafe_allow_html=True)
    
    with col_seletor:
        if 'Ano' in df.columns:
            anos_disponiveis = sorted(df['Ano'].unique())
            ano_grafico = st.selectbox(
                "Ano:",
                options=anos_disponiveis,
                index=len(anos_disponiveis)-1 if anos_disponiveis else 0,
                label_visibility="collapsed"
            )
    
    if 'Ano' in df.columns and 'Nome_Mês' in df.columns:
        # Filtrar dados para o ano selecionado
        df_ano = df[df['Ano'] == ano_grafico].copy()
        
        if not df_ano.empty:
            # Ordem dos meses
            ordem_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                          'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            
            # Agrupar por mês
            demandas_por_mes = df_ano.groupby('Nome_Mês').size().reset_index()
            demandas_por_mes.columns = ['Mês', 'Quantidade']
            
            # Reordenar para manter ordem cronológica
            demandas_por_mes['Mês'] = pd.Categorical(demandas_por_mes['Mês'], categories=ordem_meses, ordered=True)
            demandas_por_mes = demandas_por_mes.sort_values('Mês').reset_index(drop=True)
            
            # Criar gráfico de linha
            fig_mes = go.Figure()
            
            fig_mes.add_trace(go.Scatter(
                x=demandas_por_mes['Mês'],
                y=demandas_por_mes['Quantidade'],
                mode='lines+markers+text',
                name='Demandas',
                line=dict(color='#1e3799', width=3),
                marker=dict(size=10, color='#0c2461'),
                text=demandas_por_mes['Quantidade'],
                textposition='top center',
                textfont=dict(size=12, color='#1e3799')
            ))
            
            fig_mes.update_layout(
                title=f"Demandas em {ano_grafico}",
                xaxis_title="Mês",
                yaxis_title="Número de Demandas",
                plot_bgcolor='white',
                height=400,
                showlegend=False,
                margin=dict(t=50, b=50, l=50, r=50),
                xaxis=dict(
                    gridcolor='rgba(0,0,0,0.05)',
                    tickmode='array',
                    tickvals=list(range(12)),
                    ticktext=ordem_meses
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
                font=dict(size=12, color="#1e3799", weight="bold"),
                bgcolor="rgba(255,255,255,0.9)",
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
                st.metric("📈 Mês com mais demandas", f"{mes_max['Mês']}: {int(mes_max['Quantidade']):,}")
            with col_stats2:
                st.metric("📉 Mês com menos demandas", f"{mes_min['Mês']}: {int(mes_min['Quantidade']):,}")
            with col_stats3:
                media_mensal = int(demandas_por_mes['Quantidade'].mean())
                st.metric("📊 Média mensal", f"{media_mensal:,}")
    
    # ============================================
    # TOP 10 RESPONSÁVEIS - GRÁFICO MAIOR
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
                height=500,  # MAIOR
                plot_bgcolor='white',
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis_title="Número de Demandas",
                yaxis_title=""
            )
            
            st.plotly_chart(fig_top, use_container_width=True)
    
    with col_dist:
        st.markdown('<div class="section-title-exec">📊 DISTRIBUIÇÃO POR STATUS</div>', unsafe_allow_html=True)
        
        if 'Status' in df.columns:
            status_dist = df['Status'].value_counts().reset_index()
            status_dist.columns = ['Status', 'Quantidade']
            
            fig_status = px.bar(
                status_dist,
                x='Quantidade',
                y='Status',
                orientation='h',
                title='',
                text='Quantidade',
                color='Quantidade',
                color_continuous_scale='Viridis'
            )
            
            fig_status.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                marker_line_color='rgb(8,48,107)',
                marker_line_width=1,
                opacity=0.9
            )
            
            fig_status.update_layout(
                height=500,
                plot_bgcolor='white',
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis_title="Quantidade",
                yaxis_title=""
            )
            
            st.plotly_chart(fig_status, use_container_width=True)
    
    # ============================================
    # ÚLTIMAS DEMANDAS REGISTRADAS COM FILTROS
    # ============================================
    st.markdown("---")
    st.markdown('<div class="section-title-exec">🕒 ÚLTIMAS DEMANDAS REGISTRADAS</div>', unsafe_allow_html=True)
    
    if 'Criado' in df.columns:
        # Filtros para a tabela
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
        
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
            Sistema de análise e monitoramento de demandas - Setor SRE
        </p>
        <div style="margin-top: 2rem; padding: 2rem; background: white; border-radius: 8px; display: inline-block;">
            <h4 style="color: #1e3799;">📋 Para começar:</h4>
            <p>1. <strong>Use a barra lateral esquerda</strong> para fazer upload do arquivo CSV</p>
            <p>2. <strong>Aplique os filtros</strong> para análise específica</p>
            <p>3. <strong>Visualize os indicadores</strong> e métricas de desempenho</p>
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
        Versão 3.0 | SRE Monitoring Platform
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
