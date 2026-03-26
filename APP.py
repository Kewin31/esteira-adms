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
import folium
from folium import plugins
warnings.filterwarnings('ignore')

# ============================================
# PALETA DE CORES - NOVA IDENTIDADE VISUAL
# ============================================
# Cores principais
COR_VERDE_ESCURO = "#2E7D32"      # Verde escuro - principal
COR_AZUL_PETROLEO = "#028a9f"     # Azul petróleo - secundário
COR_AZUL_ESCURO = "#005973"       # Azul escuro - destaque
COR_LARANJA = "#F57C00"           # Laranja - alertas/positivo
COR_VERMELHO = "#C62828"          # Vermelho - erros/negativo

# Cores neutras
COR_CINZA_FUNDO = "#F8F9FA"       # Cinza muito claro para fundos
COR_CINZA_BORDA = "#E9ECEF"       # Cinza para bordas
COR_CINZA_TEXTO = "#6C757D"       # Cinza para textos secundários
COR_BRANCO = "#FFFFFF"            # Branco
COR_PRETO_SUAVE = "#212529"       # Preto suave para textos principais

# ============================================
# MAPEAMENTO COMPLETO DAS EMPRESAS
# ============================================
MAPEAMENTO_EMPRESAS = {
    'EMR': {
        'sigla': 'MG',
        'estado': 'Minas Gerais',
        'regiao': 'Sudeste',
        'nome_completo': 'Energisa Minas Gerais',
        'latitude': -19.9167,
        'longitude': -43.9345
    },
    'EPB': {
        'sigla': 'PB',
        'estado': 'Paraíba',
        'regiao': 'Nordeste',
        'nome_completo': 'Energisa Paraíba',
        'latitude': -7.1195,
        'longitude': -36.7240
    },
    'ESE': {
        'sigla': 'SE',
        'estado': 'Sergipe',
        'regiao': 'Nordeste',
        'nome_completo': 'Energisa Sergipe',
        'latitude': -10.9472,
        'longitude': -37.0731
    },
    'ESS': {
        'sigla': 'SP',
        'estado': 'São Paulo',
        'regiao': 'Sudeste',
        'nome_completo': 'Energisa Sul/Sudeste',
        'latitude': -23.5505,
        'longitude': -46.6333
    },
    'EMS': {
        'sigla': 'MS',
        'estado': 'Mato Grosso do Sul',
        'regiao': 'Centro-Oeste',
        'nome_completo': 'Energisa Mato Grosso do Sul',
        'latitude': -20.4697,
        'longitude': -54.6201
    },
    'EMT': {
        'sigla': 'MT',
        'estado': 'Mato Grosso',
        'regiao': 'Centro-Oeste',
        'nome_completo': 'Energisa Mato Grosso',
        'latitude': -12.6819,
        'longitude': -56.9211
    },
    'ETO': {
        'sigla': 'TO',
        'estado': 'Tocantins',
        'regiao': 'Norte',
        'nome_completo': 'Energisa Tocantins',
        'latitude': -10.1753,
        'longitude': -48.2982
    },
    'ERO': {
        'sigla': 'RO',
        'estado': 'Rondônia',
        'regiao': 'Norte',
        'nome_completo': 'Energisa Rondônia',
        'latitude': -10.9161,
        'longitude': -61.8298
    },
    'EAC': {
        'sigla': 'AC',
        'estado': 'Acre',
        'regiao': 'Norte',
        'nome_completo': 'Energisa Acre',
        'latitude': -9.0238,
        'longitude': -70.8120
    }
}

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
# CSS PERSONALIZADO
# ============================================
st.markdown(f"""
<style>
    .stApp {{
        background-color: {COR_CINZA_FUNDO};
    }}
    .metric-card {{
        background: {COR_BRANCO};
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid {COR_CINZA_BORDA};
        margin-bottom: 1rem;
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {COR_AZUL_ESCURO};
        margin: 0;
    }}
    .metric-label {{
        font-size: 0.85rem;
        color: {COR_CINZA_TEXTO};
        margin: 0.5rem 0 0 0;
    }}
    .section-title {{
        color: {COR_AZUL_ESCURO};
        border-left: 4px solid {COR_VERDE_ESCURO};
        padding-left: 1rem;
        margin-bottom: 1.5rem;
        font-size: 1.2rem;
        font-weight: 700;
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
        correcoes = {
            ' Da ': ' da ', ' De ': ' de ', ' Do ': ' do ',
            ' Das ': ' das ', ' Dos ': ' dos ', ' E ': ' e ',
        }
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

@st.cache_data(ttl=300)
def carregar_dados(uploaded_file=None, caminho_arquivo=None):
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
            'Chamado': 'Chamado', 'Tipo Chamado': 'Tipo_Chamado',
            'Responsável': 'Responsável', 'Status': 'Status', 'Criado': 'Criado',
            'Modificado': 'Modificado', 'Modificado por': 'Modificado_por',
            'Prioridade': 'Prioridade', 'Sincronização': 'Sincronização',
            'SRE': 'SRE', 'Empresa': 'Empresa', 'Revisões': 'Revisões'
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
                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
            })
            df['Ano_Mês'] = df['Criado'].dt.strftime('%Y-%m')
        
        if 'Revisões' in df.columns:
            df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
        
        hash_conteudo = calcular_hash_arquivo(conteudo_bytes)
        timestamp = time.time()
        return df, "✅ Dados carregados com sucesso", f"{hash_conteudo}_{timestamp}"
    except Exception as e:
        return None, f"Erro: {str(e)}", None

def encontrar_arquivo_dados():
    if os.path.exists(CAMINHO_ARQUIVO_PRINCIPAL):
        return CAMINHO_ARQUIVO_PRINCIPAL
    for caminho in CAMINHOS_ALTERNATIVOS:
        if os.path.exists(caminho):
            return caminho
    return None

def verificar_e_atualizar_arquivo():
    caminho_arquivo = encontrar_arquivo_dados()
    if caminho_arquivo and os.path.exists(caminho_arquivo):
        if 'ultima_modificacao' not in st.session_state:
            st.session_state.ultima_modificacao = os.path.getmtime(caminho_arquivo)
            return False
        modificacao_atual = os.path.getmtime(caminho_arquivo)
        if (modificacao_atual > st.session_state.ultima_modificacao and 
            st.session_state.df_original is not None):
            with open(caminho_arquivo, 'rb') as f:
                conteudo_atual = f.read()
            hash_atual = calcular_hash_arquivo(conteudo_atual)
            if 'file_hash' not in st.session_state or hash_atual != st.session_state.file_hash:
                st.session_state.ultima_modificacao = modificacao_atual
                return True
        st.session_state.ultima_modificacao = modificacao_atual
    return False

def limpar_sessao_dados():
    keys_to_clear = ['df_original', 'df_filtrado', 'arquivo_atual', 'ultima_modificacao', 'file_hash', 'uploaded_file_name', 'ultima_atualizacao']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def get_horario_brasilia():
    try:
        tz = timezone('America/Sao_Paulo')
        return datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    except:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

# ============================================
# FUNÇÕES DO MAPA
# ============================================
def processar_dados_mapa(df, empresas_selecionadas=None, ano_filtro=None, mes_filtro=None):
    df_sinc = df[df['Status'] == 'Sincronizado'].copy()
    if ano_filtro and ano_filtro != 'Todos':
        df_sinc = df_sinc[df_sinc['Ano'] == int(ano_filtro)]
    if mes_filtro and mes_filtro != 'Todos':
        df_sinc = df_sinc[df_sinc['Mês'] == int(mes_filtro)]
    if empresas_selecionadas and 'Todas' not in empresas_selecionadas:
        df_sinc = df_sinc[df_sinc['Empresa'].isin(empresas_selecionadas)]
    
    sinc_por_empresa = df_sinc['Empresa'].value_counts().reset_index()
    sinc_por_empresa.columns = ['Empresa', 'Sincronismos']
    
    dados_mapa = []
    total_sinc = 0
    for empresa, info in MAPEAMENTO_EMPRESAS.items():
        mask = sinc_por_empresa['Empresa'] == empresa
        qtd = int(sinc_por_empresa[mask]['Sincronismos'].values[0]) if mask.any() else 0
        if empresas_selecionadas and 'Todas' not in empresas_selecionadas:
            if empresa not in empresas_selecionadas:
                continue
        dados_mapa.append({
            'sigla': info['sigla'], 'estado': info['estado'], 'regiao': info['regiao'],
            'empresa': empresa, 'empresa_nome': info['nome_completo'],
            'sincronismos': qtd, 'latitude': info['latitude'], 'longitude': info['longitude']
        })
        total_sinc += qtd
    return pd.DataFrame(dados_mapa), total_sinc

def cor_gradiente_folium(valor, min_val, max_val):
    if max_val == min_val:
        return COR_AZUL_PETROLEO
    t = (valor - min_val) / (max_val - min_val)
    cor_baixo = (0x02, 0x8a, 0x9f)
    cor_medio = (0xF5, 0x7C, 0x00)
    cor_alto = (0xC6, 0x28, 0x28)
    if t < 0.5:
        tt = t / 0.5
        r = int(cor_baixo[0] + tt * (cor_medio[0] - cor_baixo[0]))
        g = int(cor_baixo[1] + tt * (cor_medio[1] - cor_baixo[1]))
        b = int(cor_baixo[2] + tt * (cor_medio[2] - cor_baixo[2]))
    else:
        tt = (t - 0.5) / 0.5
        r = int(cor_medio[0] + tt * (cor_alto[0] - cor_medio[0]))
        g = int(cor_medio[1] + tt * (cor_alto[1] - cor_medio[1]))
        b = int(cor_medio[2] + tt * (cor_alto[2] - cor_medio[2]))
    return f"#{r:02X}{g:02X}{b:02X}"

def criar_mapa_folium(df_mapa):
    if df_mapa.empty:
        return None
    
    df_bolhas = df_mapa[df_mapa['sincronismos'] > 0].copy()
    m = folium.Map(location=[-14.5, -51.5], zoom_start=4, tiles=None, prefer_canvas=True)
    
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name='CartoDB Positron', max_zoom=19, subdomains='abcd'
    ).add_to(m)
    
    if df_bolhas.empty:
        return m
    
    max_sinc = df_bolhas['sincronismos'].max()
    min_sinc = df_bolhas['sincronismos'].min()
    total = df_bolhas['sincronismos'].sum()
    R_MIN, R_MAX = 20, 70
    
    def raio(v):
        if max_sinc == min_sinc:
            return (R_MIN + R_MAX) / 2
        return R_MIN + (v - min_sinc) / (max_sinc - min_sinc) * (R_MAX - R_MIN)
    
    df_bolhas_sorted = df_bolhas.sort_values('sincronismos', ascending=False).reset_index(drop=True)
    rank_map = {row['empresa']: i + 1 for i, row in df_bolhas_sorted.iterrows()}
    
    for _, row in df_bolhas.iterrows():
        cor = cor_gradiente_folium(row['sincronismos'], min_sinc, max_sinc)
        r = raio(row['sincronismos'])
        rank = rank_map[row['empresa']]
        pct = row['sincronismos'] / total * 100 if total > 0 else 0
        medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, f'#{rank}')
        
        tooltip_html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; min-width: 220px;">
            <div style="background: {COR_AZUL_ESCURO}; color: white; padding: 10px 14px; border-radius: 8px 8px 0 0; font-weight: 700;">
                {medal} {row['empresa_nome']}
            </div>
            <div style="background: white; border: 1px solid #ddd; border-top: none; border-radius: 0 0 8px 8px; padding: 12px 14px;">
                <table style="width:100%; font-size:13px;">
                    <tr><td style="color:{COR_CINZA_TEXTO};">Código:</td><td style="font-weight:700; text-align:right;">{row['empresa']}</td></tr>
                    <tr><td style="color:{COR_CINZA_TEXTO};">Estado:</td><td style="font-weight:700; text-align:right;">{row['estado']} ({row['sigla']})</td></tr>
                    <tr><td style="color:{COR_CINZA_TEXTO};">Região:</td><td style="font-weight:700; text-align:right;">{row['regiao']}</td></tr>
                    <tr style="border-top:1px solid #eee;"><td style="color:{COR_CINZA_TEXTO}; padding-top:8px;">Sincronizações:</td>
                        <td style="font-weight:800; font-size:18px; color:{cor}; text-align:right;">{row['sincronismos']:,}</td></tr>
                    <tr><td style="color:{COR_CINZA_TEXTO};">% do Total:</td><td style="font-weight:600; text-align:right;">{pct:.1f}%</td></tr>
                    <tr><td style="color:{COR_CINZA_TEXTO};">Ranking:</td><td style="font-weight:600; text-align:right;">{medal} {rank}º lugar</td></tr>
                </table>
            </div>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=r, color=COR_BRANCO, weight=3,
            fill=True, fill_color=cor, fill_opacity=0.85,
            tooltip=folium.Tooltip(tooltip_html, sticky=True)
        ).add_to(m)
        
        font_size_sigla = max(10, min(16, int(r * 0.4)))
        font_size_num = max(9, min(14, int(r * 0.32)))
        label_html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; text-align: center; font-weight: 800; line-height: 1.2; white-space: nowrap;">
            <div style="font-size: {font_size_sigla}px; color: white; text-shadow: 0 1px 2px rgba(0,0,0,0.7);">{row['empresa']}</div>
            <div style="font-size: {font_size_num}px; color: white; text-shadow: 0 1px 2px rgba(0,0,0,0.6);">{row['sincronismos']}</div>
        </div>
        """
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            icon=folium.DivIcon(html=label_html, icon_size=(int(r * 1.8), int(r * 1.8)), icon_anchor=(int(r * 0.9), int(r * 0.9)))
        ).add_to(m)
    
    legenda_html = f"""
    <div style="position: fixed; bottom: 30px; left: 20px; z-index: 9999; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); padding: 14px 20px; font-family: 'Segoe UI', sans-serif; border: 1px solid {COR_CINZA_BORDA};">
        <div style="font-weight:800; margin-bottom:12px;">📊 VOLUME DE SINCRONIZAÇÕES</div>
        <div style="width: 140px; height: 12px; border-radius: 6px; background: linear-gradient(to right, {COR_AZUL_PETROLEO}, {COR_LARANJA}, {COR_VERMELHO}); border: 1px solid #ddd;"></div>
        <div style="display:flex; justify-content:space-between; font-size:10px; margin:8px 0;"><span>⬅️ Menor</span><span>Maior ➡️</span></div>
        <div style="font-size:10px;">🔍 Passe o mouse sobre uma bolha para detalhes</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legenda_html))
    
    if len(df_bolhas_sorted) >= 1:
        top3_rows = df_bolhas_sorted.head(3)
        top3_html_items = ""
        medals = ['🥇', '🥈', '🥉']
        for i, (_, row) in enumerate(top3_rows.iterrows()):
            pct_t = row['sincronismos'] / total * 100 if total > 0 else 0
            cor_top = cor_gradiente_folium(row['sincronismos'], min_sinc, max_sinc)
            top3_html_items += f"""
            <div style="display:flex; align-items:center; gap:10px; padding: 8px 0; border-bottom: 1px solid {COR_CINZA_BORDA};">
                <span style="font-size:18px;">{medals[i]}</span>
                <div style="flex:1;"><div style="font-weight:700;">{row['empresa_nome'][:25]}</div><div style="font-size:10px;">{row['estado']}</div></div>
                <div style="text-align:right;"><div style="font-weight:800; color:{cor_top};">{row['sincronismos']:,}</div><div style="font-size:9px;">{pct_t:.1f}%</div></div>
            </div>
            """
        painel_html = f"""
        <div style="position: fixed; top: 90px; right: 20px; z-index: 9999; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); padding: 14px 18px; font-family: 'Segoe UI', sans-serif; min-width: 240px; border: 1px solid {COR_CINZA_BORDA};">
            <div style="font-weight:800; margin-bottom:10px;">🏆 TOP EMPRESAS</div>
            {top3_html_items}
            <div style="padding-top:10px; font-size:11px; text-align:center; border-top:1px solid {COR_CINZA_BORDA};"><strong style="color:{COR_AZUL_ESCURO};">Total: {total:,}</strong> sincronizações</div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(painel_html))
    
    return m

def criar_grafico_barras(df_mapa):
    if df_mapa.empty:
        return None
    df_barras = df_mapa.sort_values('sincronismos', ascending=False).reset_index(drop=True)
    total = df_barras['sincronismos'].sum()
    fig = go.Figure()
    max_val = df_barras['sincronismos'].max()
    min_val = df_barras['sincronismos'].min()
    
    for _, row in df_barras.iterrows():
        if max_val == min_val:
            cor = COR_AZUL_PETROLEO
        else:
            normalized = (row['sincronismos'] - min_val) / (max_val - min_val)
            if normalized < 0.5:
                tt = normalized / 0.5
                r = int(2 + tt * (245 - 2))
                g = int(138 + tt * (124 - 138))
                b = int(159 + tt * (0 - 159))
            else:
                tt = (normalized - 0.5) / 0.5
                r = int(245 + tt * (198 - 245))
                g = int(124 + tt * (40 - 124))
                b = int(0 + tt * (40 - 0))
            cor = f'rgb({r}, {g}, {b})'
        
        percentual = (row['sincronismos'] / total * 100) if total > 0 else 0
        fig.add_trace(go.Bar(
            x=[row['sincronismos']],
            y=[f"{row['empresa']} - {row['empresa_nome'][:20]}"],
            orientation='h',
            text=[f"{row['sincronismos']:,} ({percentual:.1f}%)"],
            textposition='outside',
            marker_color=cor,
            marker_line_color=COR_AZUL_ESCURO,
            hovertemplate=f"<b>{row['empresa_nome']}</b><br>Sincronizações: {row['sincronismos']:,}<br>Percentual: {percentual:.1f}%<extra></extra>"
        ))
    
    fig.update_layout(
        title="<b>🏆 RANKING DE SINCRONIZAÇÕES POR EMPRESA</b>",
        xaxis_title="Número de Sincronizações",
        yaxis_title="", height=450, showlegend=False,
        plot_bgcolor=COR_BRANCO,
        xaxis=dict(gridcolor=COR_CINZA_BORDA),
        yaxis=dict(gridcolor=COR_CINZA_BORDA, categoryorder='total ascending'),
        margin=dict(l=20, r=80, t=60, b=20)
    )
    return fig

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <h3 style="color: {COR_AZUL_ESCURO};">⚙️ Painel de Controle</h3>
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
                    ano_selecionado = st.selectbox("📅 Ano", options=anos_opcoes, key="filtro_ano")
                    if ano_selecionado != 'Todos os Anos':
                        df = df[df['Ano'] == int(ano_selecionado)]
            
            if 'Mês' in df.columns:
                meses_disponiveis = sorted(df['Mês'].dropna().unique().astype(int))
                if meses_disponiveis:
                    meses_opcoes = ['Todos os Meses'] + [str(m) for m in meses_disponiveis]
                    mes_selecionado = st.selectbox("📆 Mês", options=meses_opcoes, key="filtro_mes")
                    if mes_selecionado != 'Todos os Meses':
                        df = df[df['Mês'] == int(mes_selecionado)]
            
            if 'Responsável_Formatado' in df.columns:
                responsaveis = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
                responsavel_selecionado = st.selectbox("👤 Responsável", options=responsaveis, key="filtro_responsavel")
                if responsavel_selecionado != 'Todos':
                    df = df[df['Responsável_Formatado'] == responsavel_selecionado]
            
            busca_chamado = st.text_input("🔎 Buscar Chamado", placeholder="Digite número do chamado...")
            if busca_chamado:
                df = df[df['Chamado'].astype(str).str.contains(busca_chamado, na=False)]
            
            if 'Status' in df.columns:
                status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox("📊 Status", options=status_opcoes, key="filtro_status")
                if status_selecionado != 'Todos':
                    df = df[df['Status'] == status_selecionado]
            
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos'] + sorted(df['Tipo_Chamado'].dropna().unique())
                tipo_selecionado = st.selectbox("📝 Tipo de Chamado", options=tipos, key="filtro_tipo")
                if tipo_selecionado != 'Todos':
                    df = df[df['Tipo_Chamado'] == tipo_selecionado]
            
            if 'Empresa' in df.columns:
                empresas = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                empresa_selecionada = st.selectbox("🏢 Empresa", options=empresas, key="filtro_empresa")
                if empresa_selecionada != 'Todas':
                    df = df[df['Empresa'] == empresa_selecionada]
            
            if 'SRE' in df.columns:
                sres = ['Todos'] + sorted(df['SRE'].dropna().unique())
                sre_selecionado = st.selectbox("🔧 SRE Responsável", options=sres, key="filtro_sre")
                if sre_selecionado != 'Todos':
                    df = df[df['SRE'] == sre_selecionado]
            
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
                <div style="background: {COR_CINZA_FUNDO}; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem;">
                    <p style="margin: 0 0 0.3rem 0; font-weight: 600;">📄 Arquivo atual:</p>
                    <p style="margin: 0; font-size: 0.85rem;">{os.path.basename(arquivo_atual)}</p>
                    <p style="margin: 0.3rem 0 0 0; font-size: 0.75rem;">📏 {tamanho_kb:.1f} KB | 📅 {ultima_mod.strftime('%d/%m/%Y %H:%M')}</p>
                </div>
                """, unsafe_allow_html=True)
                if verificar_e_atualizar_arquivo():
                    st.warning("⚠️ O arquivo local foi modificado! Clique em 'Recarregar Local' para atualizar.")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔄 Recarregar Local", use_container_width=True, type="primary"):
                    caminho_atual = encontrar_arquivo_dados()
                    if caminho_atual and os.path.exists(caminho_atual):
                        with st.spinner('Recarregando dados...'):
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
                                    st.error(f"❌ Erro: {status}")
                            except Exception as e:
                                st.error(f"❌ Erro: {str(e)}")
                    else:
                        st.error("❌ Arquivo local não encontrado.")
            
            with col_btn2:
                if st.button("🗑️ Limpar Tudo", use_container_width=True, type="secondary"):
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
            <div class="status-success">
                <strong>📊 Status atual:</strong><br>
                <small>Registros: {len(st.session_state.df_original):,}</small><br>
                <small>Atualizado: {ultima_atualizacao}</small>
            </div>
            """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=['csv'], key="file_uploader", label_visibility="collapsed")
        if uploaded_file is not None:
            file_details = {"Nome": uploaded_file.name, "Tamanho": f"{uploaded_file.size / 1024:.1f} KB"}
            st.write("📄 Detalhes do arquivo:")
            st.json(file_details)
            if st.button("📥 Processar Arquivo", use_container_width=True, type="primary"):
                with st.spinner('Processando...'):
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
                        st.success(f"✅ {len(df_novo):,} registros carregados!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {status}")
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
# HEADER
# ============================================
st.markdown(f"""
<div style="background: linear-gradient(135deg, {COR_AZUL_PETROLEO} 0%, {COR_AZUL_ESCURO} 100%); padding: 1.5rem 2rem; margin-bottom: 1.5rem;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 style="color: white; margin: 0;">📊 ESTEIRA ADMS</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0;">Acompanhamento de Demandas - EAC | EMR | EMS | EMT | EPB | ERO | ESE | ESS | ETO</p>
        </div>
        <div style="text-align: right;">
            <p style="color: white; margin: 0;">Dashboard de Performance</p>
            <p style="color: rgba(255,255,255,0.8); margin: 0.2rem 0 0 0;">v5.5 | Sistema de Performance SRE</p>
            <p style="color: rgba(255,255,255,0.7); margin: 0.3rem 0 0 0;">{datetime.now().strftime('%d/%m/%Y')}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# EXIBIR DASHBOARD
# ============================================
if st.session_state.df_original is not None:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    tab_principal, tab_mapa = st.tabs(["📊 Dashboard Principal", "🗺️ Mapa de Sincronizações"])
    
    with tab_principal:
        st.markdown("## 📊 Informações da Base de Dados")
        if 'Criado' in df.columns and not df.empty:
            data_min = df['Criado'].min()
            data_max = df['Criado'].max()
            st.markdown(f"""
            <div class="info-base">
                <p style="margin: 0; font-weight: 600;">📅 Base atualizada em: {get_horario_brasilia()}</p>
                <p style="margin: 0.3rem 0 0 0; color: {COR_CINZA_TEXTO};">Período: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')} | Total: {len(df):,}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("## 📈 INDICADORES PRINCIPAIS")
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
        st.info("📌 As demais abas de análise (Evolução de Demandas, Análise de Revisões, etc.) estão disponíveis na versão completa do dashboard.")
    
    with tab_mapa:
        st.markdown("## 🗺️ Mapa de Sincronizações por Empresa")
        
        col_mapa_filtro1, col_mapa_filtro2, col_mapa_filtro3 = st.columns(3)
        
        with col_mapa_filtro1:
            empresas_disponiveis = df['Empresa'].dropna().unique()
            empresas_opcoes = ['Todas'] + sorted([e for e in empresas_disponiveis if e in MAPEAMENTO_EMPRESAS])
            empresas_selecionadas_mapa = st.multiselect("🏢 Empresas", options=empresas_opcoes, default=['Todas'], key="mapa_empresas")
        
        with col_mapa_filtro2:
            if 'Ano' in df.columns:
                anos_disponiveis_mapa = sorted(df['Ano'].dropna().unique().astype(int))
                anos_opcoes_mapa = ['Todos'] + list(anos_disponiveis_mapa)
                ano_filtro_mapa = st.selectbox("📅 Ano", options=anos_opcoes_mapa, index=0, key="mapa_ano")
            else:
                ano_filtro_mapa = 'Todos'
        
        with col_mapa_filtro3:
            if 'Mês' in df.columns and ano_filtro_mapa != 'Todos':
                df_ano_mapa = df[df['Ano'] == int(ano_filtro_mapa)]
                meses_disponiveis_mapa = sorted(df_ano_mapa['Mês'].dropna().unique().astype(int))
                meses_opcoes_mapa = ['Todos'] + [f"{m:02d}" for m in meses_disponiveis_mapa]
                mes_filtro_mapa = st.selectbox("📆 Mês", options=meses_opcoes_mapa, index=0, key="mapa_mes")
            else:
                mes_filtro_mapa = 'Todos'
        
        df_mapa, total_sinc_filtrado = processar_dados_mapa(
            df, empresas_selecionadas=empresas_selecionadas_mapa,
            ano_filtro=ano_filtro_mapa, mes_filtro=mes_filtro_mapa
        )
        
        col_metrica1, col_metrica2, col_metrica3, col_metrica4 = st.columns(4)
        with col_metrica1:
            st.markdown(f"""<div class="metric-card"><div class="metric-value">{total_sinc_filtrado:,}</div><div class="metric-label">Total Sincronizações</div></div>""", unsafe_allow_html=True)
        with col_metrica2:
            empresas_ativas = len(df_mapa[df_mapa['sincronismos'] > 0])
            st.markdown(f"""<div class="metric-card"><div class="metric-value">{empresas_ativas}</div><div class="metric-label">Empresas com Sinc.</div></div>""", unsafe_allow_html=True)
        with col_metrica3:
            media_sinc = df_mapa['sincronismos'].mean() if not df_mapa.empty else 0
            st.markdown(f"""<div class="metric-card"><div class="metric-value">{media_sinc:.1f}</div><div class="metric-label">Média por Empresa</div></div>""", unsafe_allow_html=True)
        with col_metrica4:
            if not df_mapa.empty and df_mapa['sincronismos'].max() > 0:
                max_sinc = df_mapa['sincronismos'].max()
                empresa_max = df_mapa[df_mapa['sincronismos'] == max_sinc]['empresa_nome'].values[0]
                st.markdown(f"""<div class="metric-card"><div class="metric-value">{max_sinc:,}</div><div class="metric-label">🏆 Maior: {empresa_max[:20]}</div></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="metric-card"><div class="metric-value">0</div><div class="metric-label">Maior Sincronização</div></div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<div class="section-title">📍 MAPA DE BOLHAS</div>', unsafe_allow_html=True)
        
        m = criar_mapa_folium(df_mapa)
        if m:
            mapa_html = m._repr_html_()
            wrapper = f"""
            <div style="border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,89,115,0.12); border: 1px solid {COR_CINZA_BORDA};">
                {mapa_html}
            </div>
            """
            st.components.v1.html(wrapper, height=620)
        else:
            st.info("ℹ️ Nenhuma empresa com sincronizações para exibir no mapa.")
        
        st.markdown('<div class="section-title">📊 RANKING DE SINCRONIZAÇÕES</div>', unsafe_allow_html=True)
        fig_barras = criar_grafico_barras(df_mapa)
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True)
        
        with st.expander("📋 Ver Detalhes por Empresa", expanded=False):
            if not df_mapa.empty:
                tabela_detalhes = df_mapa[['empresa_nome', 'sigla', 'estado', 'regiao', 'sincronismos']].copy()
                tabela_detalhes.columns = ['Empresa', 'UF', 'Estado', 'Região', 'Sincronizações']
                tabela_detalhes = tabela_detalhes.sort_values('Sincronizações', ascending=False).reset_index(drop=True)
                
                total_geral = tabela_detalhes['Sincronizações'].sum()
                
                tabela_detalhes['% Total'] = (tabela_detalhes['Sincronizações'] / total_geral * 100).round(1) if total_geral > 0 else 0
                
                # Criar coluna de posição com medalhas
                posicoes = []
                for i in range(len(tabela_detalhes)):
                    if i == 0:
                        posicoes.append("🥇")
                    elif i == 1:
                        posicoes.append("🥈")
                    elif i == 2:
                        posicoes.append("🥉")
                    else:
                        posicoes.append(f"{i+1}º")
                tabela_detalhes.insert(0, 'Posição', posicoes)
                
                # Criar coluna de empresa com UF
                tabela_detalhes['Empresa (UF)'] = tabela_detalhes.apply(lambda x: f"{x['Empresa']} ({x['UF']})", axis=1)
                
                # Exibir tabela - REMOVIDA A COLUNA "Progresso"
                st.dataframe(
                    tabela_detalhes[['Posição', 'Empresa (UF)', 'Estado', 'Região', 'Sincronizações', '% Total']],
                    use_container_width=True,
                    column_config={
                        "Posição": st.column_config.TextColumn("Posição", width="small"),
                        "Empresa (UF)": st.column_config.TextColumn("Empresa", width="large"),
                        "Estado": st.column_config.TextColumn("Estado", width="medium"),
                        "Região": st.column_config.TextColumn("Região", width="medium"),
                        "Sincronizações": st.column_config.NumberColumn("Sinc.", format="%d", width="small"),
                        "% Total": st.column_config.NumberColumn("% Total", format="%.1f%%", width="small"),
                    }
                )
                
                csv = tabela_detalhes[['Empresa', 'UF', 'Estado', 'Região', 'Sincronizações', '% Total']].to_csv(index=False).encode('utf-8-sig')
                st.download_button(label="📥 Exportar dados para CSV", data=csv, file_name=f"sincronismos_empresas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)
        
        with st.expander("🌊 Sobre as Cores do Mapa", expanded=False):
            st.markdown(f"""
            ### 🎨 Escala de Cores
            <div style="display: flex; gap: 30px; margin: 15px 0;">
                <div><span style="display: inline-block; width: 30px; height: 20px; background: {COR_AZUL_PETROLEO}; border-radius: 4px;"></span> Baixo volume</div>
                <div><span style="display: inline-block; width: 30px; height: 20px; background: {COR_LARANJA}; border-radius: 4px;"></span> Médio volume</div>
                <div><span style="display: inline-block; width: 30px; height: 20px; background: {COR_VERMELHO}; border-radius: 4px;"></span> Alto volume</div>
            </div>
            
            ### 📍 Mapa de Bolhas
            - Quanto mais **<span style="color: {COR_VERMELHO};">vermelha</span>** a bolha, maior o número de sincronizações
            - Quanto mais **<span style="color: {COR_AZUL_PETROLEO};">azul</span>** a bolha, menor o número de sincronizações
            - O **tamanho** da bolha também é proporcional ao volume
            - O texto **dentro da bolha** mostra a sigla da empresa e o número de sincronizações
            - **Passe o mouse** sobre cada bolha para ver detalhes completos
            """, unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div style="text-align: center; padding: 4rem; background: {COR_CINZA_FUNDO}; border-radius: 12px; border: 2px dashed {COR_CINZA_BORDA};">
        <h3 style="color: {COR_PRETO_SUAVE};">📊 Esteira ADMS Dashboard</h3>
        <p style="color: {COR_CINZA_TEXTO}; margin-bottom: 2rem;">Sistema de análise e monitoramento de chamados - Setor SRE</p>
        <div style="margin-top: 2rem; padding: 2rem; background: {COR_BRANCO}; border-radius: 8px; display: inline-block;">
            <h4 style="color: {COR_AZUL_ESCURO};">📋 Para começar:</h4>
            <p>1. <strong>Use a barra lateral esquerda</strong> para fazer upload do arquivo CSV</p>
            <p>2. <strong>Use a seção "Importar Dados"</strong> no final da barra lateral</p>
            <p>3. <strong>Ou coloque um arquivo CSV</strong> no mesmo diretório do app</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
ultima_atualizacao = st.session_state.get('ultima_atualizacao', get_horario_brasilia())

st.markdown(f"""
<div class="footer">
    <p>Desenvolvido por: <strong>Kewin Marcel Ramirez Ferreira | GEAT</strong></p>
    <p>📧 Contato: <a href="mailto:kewin.ferreira@energisa.com.br">kewin.ferreira@energisa.com.br</a></p>
    <p>© 2024 Esteira ADMS Dashboard | Versão 5.5 | Última atualização: {ultima_atualizacao}</p>
</div>
""", unsafe_allow_html=True)
