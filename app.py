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
# CSS PERSONALIZADO - MELHORIAS VISUAIS
# ============================================
st.markdown("""
<style>
    /* Estilos gerais */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #2a5298;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3c72;
        margin: 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    .metric-delta {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.3rem;
    }
    
    .delta-positive {
        color: #28a745;
    }
    
    .delta-negative {
        color: #dc3545;
    }
    
    .delta-neutral {
        color: #6c757d;
    }
    
    .section-title {
        color: #2d3748;
        border-bottom: 2px solid #2a5298;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    /* Botão de limpar cache melhorado */
    .stButton > button[kind="secondary"] {
        border: 1px solid #dc3545;
        color: #dc3545;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #dc3545;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def formatar_nome_responsavel(nome):
    """Corrige o formato dos nomes dos responsáveis"""
    if pd.isna(nome):
        return "Não informado"
    
    nome_str = str(nome).strip()
    
    # Se for e-mail, extrair a parte antes do @
    if '@' in nome_str:
        partes = nome_str.split('@')[0]
        
        # Dividir por pontos, underlines ou hífens
        for separador in ['.', '_', '-']:
            if separador in partes:
                partes = partes.replace(separador, ' ')
        
        # Capitalizar e remover números
        partes = ' '.join([p.capitalize() for p in partes.split() if not p.isdigit()])
        return partes
    
    # Se já for um nome, apenas capitalizar
    nome_formatado = nome_str.title()
    
    # Corrigir conectivos comuns
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

def calcular_crescimento(valor_atual, valor_anterior):
    """Calcula crescimento percentual"""
    if valor_anterior == 0:
        return 0, "neutral"
    
    crescimento = ((valor_atual - valor_anterior) / valor_anterior) * 100
    
    if crescimento > 0:
        return round(crescimento, 1), "positive"
    elif crescimento < 0:
        return round(crescimento, 1), "negative"
    else:
        return 0, "neutral"

def criar_card_indicador(valor, label, crescimento=None, icone="📊"):
    """Cria card de indicador visualmente atraente"""
    if crescimento is not None:
        valor_cresc, tipo_cresc = crescimento
        if tipo_cresc == "positive":
            delta_html = f'<div class="metric-delta delta-positive">📈 +{valor_cresc}%</div>'
        elif tipo_cresc == "negative":
            delta_html = f'<div class="metric-delta delta-negative">📉 {valor_cresc}%</div>'
        else:
            delta_html = f'<div class="metric-delta delta-neutral">➡️ Estável</div>'
    else:
        delta_html = ''
    
    return f'''
    <div class="metric-card">
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
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            })
            df['Ano_Mês'] = df['Criado'].dt.strftime('%Y-%m')
        
        # Converter revisões para numérico
        if 'Revisões' in df.columns:
            df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
        
        return df, "✅ Dados carregados com sucesso"
    
    except Exception as e:
        return None, f"Erro: {str(e)}"

# ============================================
# SIDEBAR - FILTROS
# ============================================
with st.sidebar:
    st.markdown("## ⚙️ Filtros")
    st.markdown("---")
    
    # Inicializar session state
    if 'df_original' not in st.session_state:
        st.session_state.df_original = None
        st.session_state.df_filtrado = None
    
    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "📤 Carregar arquivo CSV",
        type=['csv'],
        help="Faça upload do arquivo da esteira de demandas"
    )
    
    if uploaded_file is not None:
        with st.spinner('Processando dados...'):
            df_novo, status = carregar_dados(uploaded_file=uploaded_file)
            if df_novo is not None:
                st.session_state.df_original = df_novo
                st.session_state.df_filtrado = df_novo.copy()
                st.success(status)
                st.rerun()
            else:
                st.error(status)
    
    # Tentar carregar arquivo local
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
    
    # Filtrar por responsável
    if st.session_state.df_filtrado is not None:
        st.markdown("### 🔍 Filtrar por Responsável")
        
        # Obter lista única de responsáveis formatados
        responsaveis = ['Todos'] + sorted(st.session_state.df_filtrado['Responsável_Formatado'].dropna().unique().tolist())
        
        responsavel_selecionado = st.selectbox(
            "Selecione o responsável:",
            options=responsaveis
        )
        
        if responsavel_selecionado != 'Todos':
            df_filtrado = st.session_state.df_filtrado[
                st.session_state.df_filtrado['Responsável_Formatado'] == responsavel_selecionado
            ].copy()
        else:
            df_filtrado = st.session_state.df_filtrado.copy()
        
        st.session_state.df_filtrado = df_filtrado
        st.markdown(f"**Registros filtrados:** {len(df_filtrado):,}")
    
    st.markdown("---")
    
    # Botão para limpar cache - FUNCIONANDO
    if st.button("🗑️ **Limpar Cache do Sistema**", type="secondary", use_container_width=True):
        st.cache_data.clear()
        st.session_state.clear()
        st.success("Cache limpo com sucesso!")
        st.rerun()

# ============================================
# CONTEÚDO PRINCIPAL
# ============================================

# Header
st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin: 0;">📊 Dashboard Esteira ADMS</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
    Análise e monitoramento de demandas
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# EXIBIR DASHBOARD SE HOUVER DADOS
# ============================================
if st.session_state.df_original is not None:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    # ============================================
    # INDICADORES PRINCIPAIS COM CRESCIMENTO
    # ============================================
    st.markdown("## 📈 Indicadores Principais")
    
    # Calcular dados do período anterior para comparação
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
            total_revisoes = int(df['Revisões'].sum())
            total_revisoes_anterior = int(df_ano_anterior['Revisões'].sum()) if not df_ano_anterior.empty else 0
            crescimento_rev = calcular_crescimento(total_revisoes, total_revisoes_anterior)
            st.markdown(criar_card_indicador(
                total_revisoes,
                "Total de Revisões",
                crescimento_rev,
                "📝"
            ), unsafe_allow_html=True)
    
    # ============================================
    # GRÁFICO DE DEMANDAS POR MÊS COM SELEÇÃO DE ANO
    # ============================================
    st.markdown("---")
    st.markdown("## 📅 Demandas por Mês")
    
    if 'Ano' in df.columns and 'Nome_Mês' in df.columns:
        # Seletor de ano
        anos_disponiveis = sorted(df['Ano'].unique())
        ano_selecionado = st.selectbox(
            "Selecione o ano para visualizar:",
            options=anos_disponiveis,
            index=len(anos_disponiveis)-1 if anos_disponiveis else 0,
            key="ano_demandas_mes"
        )
        
        # Filtrar dados para o ano selecionado
        df_ano = df[df['Ano'] == ano_selecionado].copy()
        
        if not df_ano.empty:
            # Ordenar meses corretamente
            ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                          'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            
            # Agrupar por mês
            demandas_por_mes = df_ano.groupby('Nome_Mês').size().reset_index()
            demandas_por_mes.columns = ['Mês', 'Quantidade']
            
            # Reordenar para manter ordem cronológica
            demandas_por_mes['Mês'] = pd.Categorical(demandas_por_mes['Mês'], categories=ordem_meses, ordered=True)
            demandas_por_mes = demandas_por_mes.sort_values('Mês').reset_index(drop=True)
            
            # Criar gráfico com valores explícitos
            fig_mes = px.bar(
                demandas_por_mes,
                x='Mês',
                y='Quantidade',
                title=f'Demandas em {ano_selecionado}',
                labels={'Quantidade': 'Número de Demandas', 'Mês': 'Mês'},
                text='Quantidade',
                color='Quantidade',
                color_continuous_scale='blues'
            )
            
            fig_mes.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                marker_line_color='rgb(8,48,107)',
                marker_line_width=1.5,
                opacity=0.9
            )
            
            fig_mes.update_layout(
                xaxis_title="Mês",
                yaxis_title="Número de Demandas",
                plot_bgcolor='white',
                showlegend=False,
                height=450,
                xaxis=dict(
                    tickangle=45,
                    tickmode='array',
                    tickvals=list(range(12)),
                    ticktext=ordem_meses
                )
            )
            
            st.plotly_chart(fig_mes, use_container_width=True)
            
            # Estatísticas do ano selecionado
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                total_ano = demandas_por_mes['Quantidade'].sum()
                st.metric(f"Total em {ano_selecionado}", f"{total_ano:,}")
            
            with col_stats2:
                mes_max = demandas_por_mes.loc[demandas_por_mes['Quantidade'].idxmax()]
                st.metric("Mês com mais demandas", f"{mes_max['Mês']}: {mes_max['Quantidade']:,}")
            
            with col_stats3:
                media_mensal = int(demandas_por_mes['Quantidade'].mean())
                st.metric("Média mensal", f"{media_mensal:,}")
    
    # ============================================
    # ERROS POR MÊS/ANO (BASEADO EM REVISÕES) - CORRIGIDO
    # ============================================
    st.markdown("---")
    st.markdown("## 📈 Erros/Retrabalhos por Mês (Baseado em Revisões)")
    
    if 'Revisões' in df.columns and 'Ano_Mês' in df.columns:
        # Filtrar apenas registros com revisões (indicador de retrabalho/erro)
        df_com_revisoes = df[df['Revisões'] > 0].copy()
        
        if not df_com_revisoes.empty:
            # Agrupar por mês/ano
            revisoes_por_mes = df_com_revisoes.groupby('Ano_Mês').agg({
                'Revisões': 'sum',
                'Chamado': 'count'
            }).reset_index()
            
            revisoes_por_mes.columns = ['Período', 'Total_Revisões', 'Chamados_Com_Revisão']
            revisoes_por_mes = revisoes_por_mes.sort_values('Período')
            
            # Criar gráfico combinado
            fig_erros = go.Figure()
            
            # Barras para total de revisões
            fig_erros.add_trace(go.Bar(
                x=revisoes_por_mes['Período'],
                y=revisoes_por_mes['Total_Revisões'],
                name='Total de Revisões',
                text=revisoes_por_mes['Total_Revisões'],
                textposition='outside',
                marker_color='#e74c3c',
                opacity=0.8
            ))
            
            # Linha para chamados com revisão
            fig_erros.add_trace(go.Scatter(
                x=revisoes_por_mes['Período'],
                y=revisoes_por_mes['Chamados_Com_Revisão'],
                name='Chamados com Revisão',
                mode='lines+markers',
                line=dict(color='#f39c12', width=3),
                yaxis='y2'
            ))
            
            fig_erros.update_layout(
                title='Evolução de Revisões (Indicador de Retrabalho/Erro)',
                xaxis_title='Período (Mês/Ano)',
                yaxis_title='Total de Revisões',
                yaxis2=dict(
                    title='Chamados com Revisão',
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
            col_erro1, col_erro2, col_erro3 = st.columns(3)
            with col_erro1:
                chamados_com_revisao = len(df_com_revisoes)
                percentual = (chamados_com_revisao / len(df)) * 100
                st.metric("Chamados com revisão", f"{chamados_com_revisao:,}", f"{percentual:.1f}% do total")
            
            with col_erro2:
                media_revisoes = df_com_revisoes['Revisões'].mean()
                st.metric("Média de revisões", f"{media_revisoes:.1f}")
            
            with col_erro3:
                max_revisoes = int(df_com_revisoes['Revisões'].max())
                st.metric("Máximo de revisões", f"{max_revisoes:,}")
        else:
            st.info("✅ Nenhum registro com revisões encontrado no período")
    
    # ============================================
    # GRÁFICOS EXISTENTES (mantidos da versão anterior)
    # ============================================
    st.markdown("---")
    
    col_grafico1, col_grafico2 = st.columns(2)
    
    with col_grafico1:
        st.markdown("### 👥 Top 10 Responsáveis")
        
        if 'Responsável_Formatado' in df.columns:
            top_responsaveis = df['Responsável_Formatado'].value_counts().head(10).reset_index()
            top_responsaveis.columns = ['Responsável', 'Demandas']
            
            fig_resp = px.bar(
                top_responsaveis,
                x='Demandas',
                y='Responsável',
                orientation='h',
                title='',
                text='Demandas',
                color='Demandas',
                color_continuous_scale='blues'
            )
            
            fig_resp.update_traces(
                texttemplate='%{text}',
                textposition='outside'
            )
            
            fig_resp.update_layout(
                height=400,
                plot_bgcolor='white',
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(t=20, b=20, l=20, r=20)
            )
            
            st.plotly_chart(fig_resp, use_container_width=True)
    
    with col_grafico2:
        st.markdown("### 📊 Distribuição por Status")
        
        if 'Status' in df.columns:
            status_dist = df['Status'].value_counts()
            fig_status = px.pie(
                values=status_dist.values,
                names=status_dist.index,
                title='',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_status.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                textfont_size=12
            )
            fig_status.update_layout(height=400)
            st.plotly_chart(fig_status, use_container_width=True)
    
    # ============================================
    # ÚLTIMAS DEMANDAS
    # ============================================
    st.markdown("---")
    st.markdown("### 🕒 Últimas Demandas Registradas")
    
    if 'Criado' in df.columns:
        ultimas_demandas = df.sort_values('Criado', ascending=False).head(10)
        
        display_cols = []
        if 'Chamado' in ultimas_demandas.columns:
            display_cols.append('Chamado')
        if 'Tipo_Chamado' in ultimas_demandas.columns:
            display_cols.append('Tipo_Chamado')
        if 'Responsável_Formatado' in ultimas_demandas.columns:
            display_cols.append('Responsável')
            ultimas_demandas['Responsável'] = ultimas_demandas['Responsável_Formatado']
        if 'Status' in ultimas_demandas.columns:
            display_cols.append('Status')
        if 'Criado' in ultimas_demandas.columns:
            display_cols.append('Data_Criação')
            ultimas_demandas['Data_Criação'] = ultimas_demandas['Criado'].dt.strftime('%d/%m/%Y %H:%M')
        
        if display_cols:
            st.dataframe(
                ultimas_demandas[display_cols],
                use_container_width=True,
                height=300
            )

else:
    # Tela inicial
    st.info("📂 Faça upload do arquivo CSV da esteira de demandas na barra lateral para começar a análise")

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>Desenvolvido por <strong>Kewin Marcel Ramirez Ferreira | GEAT</strong></p>
    <p>Dashboard Esteira ADMS • © 2024</p>
</div>
""", unsafe_allow_html=True)
