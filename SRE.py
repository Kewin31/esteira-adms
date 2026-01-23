# ============================================
# ESTEIRA ADMS - DASHBOARD
# VERSÃO 5.6
# ============================================

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pytz import timezone
import numpy as np
import hashlib
import io
import os
import time
import warnings
warnings.filterwarnings("ignore")

# ============================================
# CONFIGURAÇÕES INICIAIS
# ============================================
st.set_page_config(
    page_title="Esteira ADMS - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def get_horario_brasilia():
    try:
        return datetime.now(timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S")
    except:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def formatar_nome_responsavel(nome):
    if pd.isna(nome):
        return "Não informado"
    nome = str(nome)
    if "@" in nome:
        nome = nome.split("@")[0]
    nome = nome.replace(".", " ").replace("_", " ").replace("-", " ")
    return nome.title()

def calcular_hash_arquivo(conteudo):
    return hashlib.md5(conteudo).hexdigest()

# ============================================
# PROCESSAMENTO DE DADOS
# ============================================
@st.cache_data(ttl=3600)
def carregar_dados(file_bytes, filename):
    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8", on_bad_lines="skip")
    else:
        df = pd.read_excel(io.BytesIO(file_bytes))

    df.rename(columns={
        "Tipo Chamado": "Tipo_Chamado",
        "Responsável": "Responsável",
        "Modificado por": "Modificado_por"
    }, inplace=True)

    if "Responsável" in df.columns:
        df["Responsável_Formatado"] = df["Responsável"].apply(formatar_nome_responsavel)

    for col in ["Criado", "Modificado"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "Criado" in df.columns:
        df["Ano"] = df["Criado"].dt.year
        df["Mês"] = df["Criado"].dt.month
        df["Dia_Semana"] = df["Criado"].dt.day_name()

    if "Revisões" in df.columns:
        df["Revisões"] = pd.to_numeric(df["Revisões"], errors="coerce").fillna(0).astype(int)

    return df

# ============================================
# SIDEBAR - UPLOAD
# ============================================
with st.sidebar:
    st.markdown("## 📂 Gerenciamento de Dados")

    uploaded = st.file_uploader("Upload CSV ou Excel", type=["csv", "xlsx", "xls"])

    if uploaded:
        df = carregar_dados(uploaded.getvalue(), uploaded.name)
        st.session_state.df = df
        st.session_state.hash = calcular_hash_arquivo(uploaded.getvalue())
        st.session_state.atualizacao = get_horario_brasilia()
        st.success("Dados carregados com sucesso")
        st.rerun()

# ============================================
# CONTEÚDO PRINCIPAL
# ============================================
if "df" not in st.session_state:
    st.info("Faça upload de um arquivo para iniciar.")
    st.stop()

df = st.session_state.df.copy()

# ============================================
# FILTRO GERAL
# ============================================
df = df[
    ~df["Responsável_Formatado"].isin(
        ["Kewin Marcel", "Kewin Marcel Ramirez Ferreira"]
    )
]

# ============================================
# ANÁLISES AVANÇADAS
# ============================================
st.markdown("## 🔍 Análises Avançadas")

tab1, tab2, tab3 = st.tabs([
    "🚀 Performance de Desenvolvedores",
    "📈 Sazonalidade",
    "⚡ Diagnóstico de Erros"
])

# ============================================
# TAB 1 - PERFORMANCE DE DEV
# ============================================
with tab1:
    st.subheader("🎯 Matriz de Performance")

    with st.expander("ℹ️ Como interpretar a matriz", expanded=False):
        st.markdown("""
        **Eficiência x Qualidade**

        ⭐ Estrelas  
        ⚡ Eficientes  
        🎯 Cuidadosos  
        🔄 Necessita Apoio
        """)

    df_dev = df[
        ~df["Responsável_Formatado"].isin(["Não informado"])
    ]

    matriz = []
    for dev in df_dev["Responsável_Formatado"].unique():
        dados = df_dev[df_dev["Responsável_Formatado"] == dev]
        total = len(dados)
        sem_rev = len(dados[dados["Revisões"] == 0])
        qualidade = sem_rev / total * 100 if total else 0
        meses = dados["Criado"].dt.to_period("M").nunique()
        eficiencia = total / meses if meses else 0
        matriz.append({
            "Dev": dev,
            "Qualidade": qualidade,
            "Eficiência": eficiencia
        })

    df_matriz = pd.DataFrame(matriz)

    media_q = df_matriz["Qualidade"].mean()
    media_e = df_matriz["Eficiência"].mean()

    fig = px.scatter(
        df_matriz,
        x="Eficiência",
        y="Qualidade",
        hover_name="Dev",
        title="Eficiência x Qualidade"
    )

    fig.add_hline(y=media_q, line_dash="dash")
    fig.add_vline(x=media_e, line_dash="dash")

    st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2 - SAZONALIDADE
# ============================================
with tab2:
    st.subheader("📅 Análise por Dia da Semana")

    dias = df.groupby("Dia_Semana").agg(
        Demandas=("Chamado", "count"),
        Sincronizados=("Status", lambda x: (x == "Sincronizado").sum())
    ).reset_index()

    fig = px.line(
        dias,
        x="Dia_Semana",
        y=["Demandas", "Sincronizados"],
        markers=True
    )

    pico = dias.loc[dias["Sincronizados"].idxmax()]
    fig.add_annotation(
        x=pico["Dia_Semana"],
        y=pico["Sincronizados"],
        text="🔺 Pico de Sincronização",
        showarrow=True
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 3 - DIAGNÓSTICO DE ERROS
# ============================================
with tab3:
    st.subheader("⚡ Diagnóstico de Erros")

    erros = df["Tipo_Chamado"].value_counts().reset_index()
    erros.columns = ["Tipo", "Quantidade"]

    fig = px.bar(
        erros,
        x="Quantidade",
        y="Tipo",
        orientation="h",
        title="Tipos de Erro"
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")
st.caption(
    f"Versão 5.6 | Última atualização: {st.session_state.get('atualizacao', '')}"
)
