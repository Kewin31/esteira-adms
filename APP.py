"""
Esteira SRE — Dashboard de Performance (v6.0)

Principais mudanças em relação à v5.5:
- Datas no formato brasileiro (dd/mm) lidas corretamente
- "Com erro" / "Sem erro" calculados só sobre os cards sincronizados
- Dias sem sincronização entram nas médias, percentis e histogramas
- Filtros de período centralizados na barra lateral
- Tema visual único (Plotly + Streamlit), heatmaps e cards padronizados
"""
import io
import os
import hashlib
import warnings
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from plotly.subplots import make_subplots
from pytz import timezone

warnings.filterwarnings("ignore")

# ============================================
# CONFIGURAÇÕES
# ============================================
VERSAO = "6.0"

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

# Volume / quantidade -> escala de um tom só (azul)
ESCALA_AZUL = [[0, "#EAF5F7"], [0.35, "#8CCAD5"], [0.7, COR_AZUL_PETROLEO], [1, COR_AZUL_ESCURO]]
# Vermelho / verde ficam reservados para meta e alerta

META_IPE = 95
HORARIOS_SINCRONISMO = [8, 9, 10, 11, 12, 14, 15, 16]

MESES = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
         7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
MESES_ABREV = {k: v[:3] for k, v in MESES.items()}
MESES_POR_NOME = {v: k for k, v in MESES.items()}
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
DIAS_CURTOS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

# Apelidos dos SREs: (palavras-chave, nome exibido)
APELIDOS_SRE = [
    (("kewin", "ferreira"), "Kewin Marcel"),
    (("pierry", "perez"), "Pierry Perez"),
    (("bruna", "maciel"), "Bruna Maciel"),
    (("ramiza", "irineu"), "Ramiza Irineu"),
]

VALORES_SIM = {"SIM", "S", "YES", "Y", "1", "TRUE"}

MAPEAMENTO_EMPRESAS = {
    "EMR": {"sigla": "MG", "estado": "Minas Gerais", "regiao": "Sudeste",
            "nome_completo": "Energisa Minas Gerais", "latitude": -19.9167, "longitude": -43.9345},
    "EPB": {"sigla": "PB", "estado": "Paraíba", "regiao": "Nordeste",
            "nome_completo": "Energisa Paraíba", "latitude": -7.1195, "longitude": -36.7240},
    "ESE": {"sigla": "SE", "estado": "Sergipe", "regiao": "Nordeste",
            "nome_completo": "Energisa Sergipe", "latitude": -10.9472, "longitude": -37.0731},
    "ESS": {"sigla": "SP", "estado": "São Paulo", "regiao": "Sudeste",
            "nome_completo": "Energisa Sul/Sudeste", "latitude": -23.5505, "longitude": -46.6333},
    "EMS": {"sigla": "MS", "estado": "Mato Grosso do Sul", "regiao": "Centro-Oeste",
            "nome_completo": "Energisa Mato Grosso do Sul", "latitude": -20.4697, "longitude": -54.6201},
    "EMT": {"sigla": "MT", "estado": "Mato Grosso", "regiao": "Centro-Oeste",
            "nome_completo": "Energisa Mato Grosso", "latitude": -12.6819, "longitude": -56.9211},
    "ETO": {"sigla": "TO", "estado": "Tocantins", "regiao": "Norte",
            "nome_completo": "Energisa Tocantins", "latitude": -10.1753, "longitude": -48.2982},
    "ERO": {"sigla": "RO", "estado": "Rondônia", "regiao": "Norte",
            "nome_completo": "Energisa Rondônia", "latitude": -10.9161, "longitude": -61.8298},
    "EAC": {"sigla": "AC", "estado": "Acre", "regiao": "Norte",
            "nome_completo": "Energisa Acre", "latitude": -9.0238, "longitude": -70.8120},
}

CAMINHO_ARQUIVO_PRINCIPAL = "esteira_demandas.csv"
CAMINHOS_ALTERNATIVOS = [
    "data/esteira_demandas.csv", "dados/esteira_demandas.csv",
    "database/esteira_demandas.csv", "base_dados.csv", "dados.csv",
]

TZ_BR = timezone("America/Sao_Paulo")


def agora():
    """Horário de Brasília (sem tzinfo, para comparar com as datas do CSV)."""
    return datetime.now(TZ_BR).replace(tzinfo=None)


# ============================================
# PÁGINA, TEMA E CSS
# ============================================
st.set_page_config(
    page_title="Esteira SRE - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

pio.templates["energisa"] = go.layout.Template(layout=dict(
    font=dict(family="Inter, 'Segoe UI', sans-serif", size=12, color=COR_PRETO_SUAVE),
    colorway=[COR_AZUL_ESCURO, COR_VERDE_ESCURO, COR_LARANJA, COR_AZUL_PETROLEO,
              "#7E57C2", "#1E88E5", "#8D6E63", COR_VERMELHO],
    plot_bgcolor=COR_BRANCO, paper_bgcolor=COR_BRANCO,
    title=dict(font=dict(size=14, color=COR_PRETO_SUAVE), x=0, xanchor="left"),
    xaxis=dict(showgrid=False, linecolor=COR_CINZA_BORDA, ticks="", automargin=True),
    yaxis=dict(gridcolor="#F1F3F5", zeroline=False, linecolor=COR_CINZA_BORDA, automargin=True),
    margin=dict(t=40, b=30, l=10, r=10),
    hoverlabel=dict(bgcolor=COR_BRANCO, bordercolor=COR_CINZA_BORDA, font_size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
    bargap=0.25,
    separators=",.",
))
pio.templates.default = "energisa"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', 'Segoe UI', sans-serif; }}
.block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px; }}

.app-header {{
    background: linear-gradient(135deg, {COR_AZUL_PETROLEO} 0%, {COR_AZUL_ESCURO} 100%);
    padding: 1.3rem 1.8rem; border-radius: 12px; margin-bottom: 1rem;
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: .8rem;
}}
.app-header h1 {{ color: #fff; margin: 0; font-size: 1.45rem; font-weight: 700; letter-spacing: -.2px; }}
.app-header p {{ color: rgba(255,255,255,.85); margin: .25rem 0 0; font-size: .85rem; }}
.app-header .meta {{ text-align: right; color: rgba(255,255,255,.85); font-size: .78rem; line-height: 1.5; }}

.section-title {{
    color: {COR_AZUL_ESCURO}; border-left: 4px solid {COR_VERDE_ESCURO};
    padding-left: .8rem; margin: 1.4rem 0 .2rem; font-size: 1rem;
    font-weight: 700; text-transform: uppercase; letter-spacing: .5px;
}}
.section-sub {{ color: {COR_CINZA_TEXTO}; font-size: .83rem; margin: 0 0 .8rem 1.05rem; }}

[data-testid="stMetric"] {{ background: {COR_BRANCO}; }}
[data-testid="stMetricValue"] {{ color: {COR_AZUL_ESCURO}; font-weight: 700; }}
[data-testid="stMetricLabel"] p {{
    color: {COR_CINZA_TEXTO}; text-transform: uppercase; font-size: .72rem !important;
    letter-spacing: .4px; font-weight: 600;
}}

.rank-item {{
    display: flex; align-items: center; gap: .7rem; padding: .55rem .2rem;
    border-bottom: 1px solid {COR_CINZA_BORDA};
}}
.rank-item:last-child {{ border-bottom: none; }}
.rank-item .pos {{ font-size: 1.1rem; width: 1.8rem; text-align: center; }}
.rank-item .nome {{ flex: 1; font-weight: 600; font-size: .85rem; color: {COR_PRETO_SUAVE}; }}
.rank-item .nome small {{ display: block; font-weight: 400; color: {COR_CINZA_TEXTO}; }}
.rank-item .valor {{ text-align: right; font-weight: 700; color: {COR_AZUL_ESCURO}; }}
.rank-item .valor small {{ display: block; font-weight: 400; color: {COR_CINZA_TEXTO}; font-size: .72rem; }}

.footer {{
    text-align: center; margin-top: 2.5rem; padding-top: 1.2rem;
    border-top: 1px solid {COR_CINZA_BORDA}; color: {COR_CINZA_TEXTO}; font-size: .8rem;
}}
.footer a {{ color: {COR_AZUL_ESCURO}; text-decoration: none; }}
</style>
""", unsafe_allow_html=True)


# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def secao(titulo, subtitulo=None):
    st.markdown(f'<div class="section-title">{titulo}</div>', unsafe_allow_html=True)
    if subtitulo:
        st.markdown(f'<div class="section-sub">{subtitulo}</div>', unsafe_allow_html=True)


def mostrar(fig, altura=380):
    fig.update_layout(height=altura)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def fmt_int(v):
    return f"{int(v):,}".replace(",", ".")


def fmt_pct(v, casas=1):
    return f"{v:.{casas}f}%".replace(".", ",")


def formatar_nome_responsavel(nome):
    if pd.isna(nome) or str(nome).strip() in ("", "nan"):
        return "Não informado"
    nome_str = str(nome).strip()
    if "@" in nome_str:
        partes = nome_str.split("@")[0]
        for separador in [".", "_", "-"]:
            partes = partes.replace(separador, " ")
        nome_formatado = " ".join(p.capitalize() for p in partes.split() if not p.isdigit())
        for errado, correto in {" Da ": " da ", " De ": " de ", " Do ": " do ",
                                " Das ": " das ", " Dos ": " dos ", " E ": " e "}.items():
            nome_formatado = nome_formatado.replace(errado, correto)
        return nome_formatado
    return nome_str.title()


def nome_sre(sre):
    if pd.isna(sre) or str(sre).strip() in ("", "nan"):
        return "Não informado"
    texto = str(sre).lower()
    for chaves, apelido in APELIDOS_SRE:
        if any(c in texto for c in chaves):
            return apelido
    return str(sre).strip()


def converter_datas(serie):
    """Converte datas detectando o formato (ISO, dd/mm ou mm/dd).
    Na dúvida, assume dd/mm (padrão brasileiro)."""
    texto = serie.astype(str).str.strip()
    amostra = texto[~texto.isin(["", "nan", "NaT", "None"])].head(1000)
    if amostra.empty:
        return pd.to_datetime(serie, errors="coerce")
    if amostra.str.match(r"^\d{4}-\d{1,2}-\d{1,2}").mean() > 0.5:
        return pd.to_datetime(texto, errors="coerce", format="mixed")
    partes = amostra.str.extract(r"^(\d{1,2})[/.\-](\d{1,2})[/.\-]\d{2,4}")
    primeiro = pd.to_numeric(partes[0], errors="coerce")
    segundo = pd.to_numeric(partes[1], errors="coerce")
    dayfirst = not ((segundo > 12).any() and not (primeiro > 12).any())
    return pd.to_datetime(texto, errors="coerce", dayfirst=dayfirst, format="mixed")


def serie_diaria(datas, so_dias_uteis=True):
    """Contagem por dia INCLUINDO os dias sem registro (dias úteis do intervalo,
    mais qualquer fim de semana que teve atividade)."""
    datas = pd.to_datetime(datas).dropna().dt.normalize()
    if datas.empty:
        return pd.Series(dtype=int)
    contagem = datas.value_counts().sort_index()
    inicio, fim = contagem.index.min(), contagem.index.max()
    if so_dias_uteis:
        indice = pd.bdate_range(inicio, fim).union(contagem.index)
    else:
        indice = pd.date_range(inicio, fim)
    return contagem.reindex(indice, fill_value=0).astype(int)


def indicadores(dfp):
    total = len(dfp)
    validados = int(dfp["Sinc"].sum())
    com_erro = int((dfp["Sinc"] & dfp["Com_Revisao"]).sum())
    sem_erro = validados - com_erro
    return {
        "total": total,
        "validados": validados,
        "nao_sinc": total - validados,
        "com_erro": com_erro,
        "sem_erro": sem_erro,
        "taxa_sucesso": validados / total * 100 if total else 0.0,
        "taxa_erro": com_erro / validados * 100 if validados else 0.0,
    }


def calcular_ipe(ca, cr, cd, ct, na):
    """IPE = (CA - CR) / (CD + |((CT/CD)/NA) - 1|), limitado a 1.
    Fórmula mantida idêntica à v5.5."""
    if cd <= 0 or na <= 0:
        return 0.0
    denominador = cd + abs((ct / cd) / na - 1)
    if denominador <= 0:
        return 0.0
    return min((ca - cr) / denominador, 1.0)


# ============================================
# CARREGAMENTO DE DADOS
# ============================================
@st.cache_data(show_spinner=False)
def carregar_dados(conteudo_bytes: bytes):
    """Lê o export do ADMS e devolve (df, mensagem_de_erro)."""
    try:
        try:
            conteudo = conteudo_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            conteudo = conteudo_bytes.decode("latin-1")
        linhas = conteudo.splitlines()

        header_line = next((i for i, l in enumerate(linhas)
                            if '"Chamado"' in l and '"Tipo Chamado"' in l), None)
        if header_line is None:
            header_line = next((i for i, l in enumerate(linhas) if '"Chamado"' in l), None)
        if header_line is None:
            return None, "Formato de arquivo inválido: cabeçalho com \"Chamado\" não encontrado."

        df = pd.read_csv(io.StringIO("\n".join(linhas[header_line:])), quotechar='"',
                         dtype={"Chamado": str})
        df.columns = [str(c).strip().strip("﻿") for c in df.columns]

        col_mapping = {
            "Tipo Chamado": "Tipo_Chamado", "Modificado por": "Modificado_por",
            "Motivo Revisão": "Motivo_Revisao", "Motivo Revisao": "Motivo_Revisao",
            "Retorno Cliente": "Retorno_Cliente",
        }
        df = df.rename(columns={a: n for a, n in col_mapping.items()
                                if a in df.columns and n not in df.columns})

        # Revisões: padroniza as duas colunas e cria o total
        for v in ["Revisoes", "Revisão", "Revisao"]:
            if v in df.columns and "Revisões" not in df.columns:
                df = df.rename(columns={v: "Revisões"})
        for v in ["Qtd. Revisoes", "Qtd.Revisões", "Qtd.Revisoes", "Qtd Revisões", "Qtd Revisoes"]:
            if v in df.columns and "Qtd. Revisões" not in df.columns:
                df = df.rename(columns={v: "Qtd. Revisões"})
        for c in ["Revisões", "Qtd. Revisões"]:
            if c not in df.columns:
                df[c] = 0
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
        df["Revisões_Total"] = df["Revisões"] + df["Qtd. Revisões"]

        # Colunas mínimas
        for c in ["Status", "SRE", "Empresa", "Tipo_Chamado", "Responsável", "Retorno_Cliente"]:
            if c not in df.columns:
                df[c] = pd.NA
        if "Criado" not in df.columns:
            return None, "A coluna \"Criado\" é obrigatória e não foi encontrada."

        # Datas
        for col in ["Criado", "Modificado", "Vencimento"]:
            if col in df.columns:
                df[col] = converter_datas(df[col])

        datas_invalidas = int(df["Criado"].isna().sum())
        df = df[df["Criado"].notna()].copy()

        df["Ano"] = df["Criado"].dt.year.astype(int)
        df["Mês"] = df["Criado"].dt.month.astype(int)
        df["Ano_Mês"] = df["Criado"].dt.strftime("%Y-%m")
        df["Mês_Label"] = df["Mês"].map(MESES_ABREV) + "/" + df["Criado"].dt.strftime("%y")
        df["Data"] = df["Criado"].dt.normalize()
        df["Hora"] = df["Criado"].dt.hour
        df["Dia_Semana"] = df["Criado"].dt.dayofweek

        # Texto / categorias
        for c in ["Status", "Empresa", "Tipo_Chamado", "SRE"]:
            df[c] = df[c].astype("string").str.strip()
        df["Responsável_Formatado"] = df["Responsável"].apply(formatar_nome_responsavel)
        df["SRE_Nome"] = df["SRE"].apply(nome_sre)

        # Flags pré-calculadas (evita .apply dentro de loops)
        df["Sinc"] = df["Status"].eq("Sincronizado").fillna(False).astype(bool)
        df["Com_Revisao"] = df["Revisões_Total"] > 0
        df["Reaberto"] = (df["Retorno_Cliente"].astype("string").str.strip().str.upper()
                          .isin(VALORES_SIM).fillna(False).astype(bool))

        df.attrs["datas_invalidas"] = datas_invalidas
        return df, None
    except Exception as e:  # noqa: BLE001
        return None, f"Erro ao ler o arquivo: {e}"


def encontrar_arquivo_dados():
    for caminho in [CAMINHO_ARQUIVO_PRINCIPAL] + CAMINHOS_ALTERNATIVOS:
        if os.path.exists(caminho):
            return caminho
    return None


ss = st.session_state
for chave, padrao in {"df_original": None, "origem": None, "origem_local": False,
                      "md5": None, "mtime": None, "ultima_atualizacao": None,
                      "arquivo_mudou": False}.items():
    ss.setdefault(chave, padrao)


def carregar_no_estado(conteudo, origem, local=False):
    df, erro = carregar_dados(conteudo)
    if df is None:
        st.error(f"❌ {erro}")
        return False
    ss.df_original = df
    ss.origem = origem
    ss.origem_local = local
    ss.md5 = hashlib.md5(conteudo).hexdigest()
    ss.mtime = os.path.getmtime(origem) if local else None
    ss.ultima_atualizacao = agora().strftime("%d/%m/%Y %H:%M:%S")
    ss.arquivo_mudou = False
    return True


def carregar_arquivo_local(caminho):
    with open(caminho, "rb") as f:
        return carregar_no_estado(f.read(), caminho, local=True)


def checar_arquivo_local():
    """Marca ss.arquivo_mudou se o CSV local mudou de conteúdo desde a última carga."""
    if not ss.origem_local or not ss.origem or not os.path.exists(ss.origem):
        return
    mtime = os.path.getmtime(ss.origem)
    if ss.mtime is not None and mtime > ss.mtime:
        with open(ss.origem, "rb") as f:
            md5 = hashlib.md5(f.read()).hexdigest()
        if md5 != ss.md5:
            ss.arquivo_mudou = True
        ss.mtime = mtime


# Carga automática do arquivo local na primeira execução
if ss.df_original is None:
    caminho = encontrar_arquivo_dados()
    if caminho:
        with st.spinner("Carregando dados locais..."):
            carregar_arquivo_local(caminho)
checar_arquivo_local()


# ============================================
# FILTROS
# ============================================
FILTROS_PADRAO = {"f_ano": "Todos", "f_meses": [], "f_empresas": [], "f_sres": [],
                  "f_status": "Todos", "f_tipo": "Todos", "f_resp": "Todos", "f_busca": ""}
for chave, padrao in FILTROS_PADRAO.items():
    ss.setdefault(chave, padrao if not isinstance(padrao, list) else list(padrao))


def limpar_filtros():
    for chave, padrao in FILTROS_PADRAO.items():
        ss[chave] = padrao if not isinstance(padrao, list) else list(padrao)


def _opcoes(df, coluna):
    return sorted(df[coluna].dropna().astype(str).unique())


def _validar_selecao(chave, opcoes, multipla=False):
    """Evita erro quando um novo arquivo não tem mais a opção escolhida antes."""
    if multipla:
        ss[chave] = [v for v in ss[chave] if v in opcoes]
    elif ss[chave] not in opcoes:
        ss[chave] = opcoes[0]


def aplicar_filtros(df, periodo=True):
    if periodo:
        if ss.f_ano != "Todos":
            df = df[df["Ano"] == int(ss.f_ano)]
        if ss.f_meses:
            df = df[df["Mês"].isin([MESES_POR_NOME[m] for m in ss.f_meses])]
    if ss.f_empresas:
        df = df[df["Empresa"].isin(ss.f_empresas)]
    if ss.f_sres:
        df = df[df["SRE_Nome"].isin(ss.f_sres)]
    if ss.f_status != "Todos":
        df = df[df["Status"] == ss.f_status]
    if ss.f_tipo != "Todos":
        df = df[df["Tipo_Chamado"] == ss.f_tipo]
    if ss.f_resp != "Todos":
        df = df[df["Responsável_Formatado"] == ss.f_resp]
    if ss.f_busca:
        df = df[df["Chamado"].astype(str).str.contains(ss.f_busca.strip(), na=False, regex=False)]
    return df


# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("### :material/tune: Painel de controle")

    if ss.df_original is not None:
        base = ss.df_original
        with st.container(border=True):
            st.markdown("**Período**")
            anos_op = ["Todos"] + [str(a) for a in sorted(base["Ano"].unique())]
            _validar_selecao("f_ano", anos_op)
            st.selectbox("Ano", anos_op, key="f_ano")
            st.multiselect("Meses", list(MESES.values()), key="f_meses", placeholder="Todos os meses")

        with st.container(border=True):
            st.markdown("**Recorte**")
            emp_op = _opcoes(base, "Empresa")
            _validar_selecao("f_empresas", emp_op, multipla=True)
            st.multiselect("Empresa", emp_op, key="f_empresas", placeholder="Todas")

            sre_op = _opcoes(base, "SRE_Nome")
            _validar_selecao("f_sres", sre_op, multipla=True)
            st.multiselect("SRE", sre_op, key="f_sres", placeholder="Todos")

            for chave, coluna, rotulo in [("f_status", "Status", "Status"),
                                          ("f_tipo", "Tipo_Chamado", "Tipo de chamado"),
                                          ("f_resp", "Responsável_Formatado", "Responsável")]:
                op = ["Todos"] + _opcoes(base, coluna)
                _validar_selecao(chave, op)
                st.selectbox(rotulo, op, key=chave)

            st.text_input("Buscar chamado", key="f_busca", placeholder="Número do chamado")
            st.button("Limpar filtros", icon=":material/filter_alt_off:", on_click=limpar_filtros,
                      width="stretch")

    with st.container(border=True):
        st.markdown("**Dados**")
        if ss.df_original is not None:
            st.caption(f"📄 {os.path.basename(str(ss.origem))}  \n"
                       f"{fmt_int(len(ss.df_original))} registros · carregado em {ss.ultima_atualizacao}")
            invalidas = ss.df_original.attrs.get("datas_invalidas", 0)
            if invalidas:
                st.warning(f"{invalidas} registro(s) ignorado(s) por data de criação inválida.")
            if ss.arquivo_mudou:
                st.info("O arquivo local foi modificado. Clique em **Recarregar** para atualizar.")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Recarregar", icon=":material/refresh:", type="primary", width="stretch",
                             help="Relê o arquivo CSV local"):
                    caminho = encontrar_arquivo_dados()
                    if caminho and carregar_arquivo_local(caminho):
                        st.rerun()
                    elif not caminho:
                        st.error("Arquivo local não encontrado.")
            with c2:
                if st.button("Limpar", icon=":material/delete:", width="stretch",
                             help="Remove os dados carregados e o cache"):
                    st.cache_data.clear()
                    for chave in ["df_original", "origem", "md5", "mtime", "ultima_atualizacao"]:
                        ss[chave] = None
                    ss.origem_local = False
                    ss.arquivo_mudou = False
                    st.rerun()

        arquivo = st.file_uploader("Importar CSV", type=["csv"], key="file_uploader",
                                   help="Envie um novo export do ADMS para substituir os dados atuais")
        if arquivo is not None:
            if st.button("Processar arquivo", icon=":material/upload:", type="primary", width="stretch"):
                with st.spinner("Processando..."):
                    if carregar_no_estado(arquivo.getvalue(), arquivo.name, local=False):
                        st.rerun()


# ============================================
# HEADER
# ============================================
st.markdown(f"""
<div class="app-header">
  <div>
    <h1>Esteira SRE · Site Reliability Engineering</h1>
    <p>Acompanhamento das validações da EAC · EMR · EMS · EMT · EPB · ERO · ESE · ESS · ETO</p>
  </div>
  <div class="meta">Dashboard de Performance · v{VERSAO}<br>{agora().strftime('%d/%m/%Y')}</div>
</div>
""", unsafe_allow_html=True)


# ============================================
# MANCHETE (diálogo)
# ============================================
def recortar_periodo(df, escolha, hoje):
    """Devolve (df_atual, df_anterior, titulo_atual, titulo_anterior)."""
    criado = df["Criado"]
    hoje_d = pd.Timestamp(hoje).normalize()
    amanha = hoje_d + timedelta(days=1)

    def entre(ini, fim):
        return df[(criado >= ini) & (criado < fim)]

    if escolha == "Mês atual":
        ini = hoje_d.replace(day=1)
        ini_ant = (ini - timedelta(days=1)).replace(day=1)
        # Compara com o MESMO trecho do mês anterior (dia 1 até o mesmo dia)
        fim_ant = min(ini_ant + timedelta(days=hoje_d.day), ini)
        return (entre(ini, amanha), entre(ini_ant, fim_ant),
                f"{MESES[ini.month]}/{ini.year} (até dia {hoje_d.day})",
                f"{MESES[ini_ant.month]}/{ini_ant.year} (mesmo trecho)")
    if escolha == "Mês anterior":
        ini = (hoje_d.replace(day=1) - timedelta(days=1)).replace(day=1)
        fim = hoje_d.replace(day=1)
        ini_ant = (ini - timedelta(days=1)).replace(day=1)
        return (entre(ini, fim), entre(ini_ant, ini),
                f"{MESES[ini.month]}/{ini.year}", f"{MESES[ini_ant.month]}/{ini_ant.year}")
    if escolha in ("Últimos 30 dias", "Últimos 90 dias"):
        n = 30 if "30" in escolha else 90
        ini = amanha - timedelta(days=n)
        return (entre(ini, amanha), entre(ini - timedelta(days=n), ini),
                escolha, f"{n} dias anteriores")
    if escolha == "Este ano":
        a = hoje_d.year
        ini_ant = pd.Timestamp(a - 1, 1, 1)
        fim_ant = ini_ant + (hoje_d - pd.Timestamp(a, 1, 1)) + timedelta(days=1)
        return (df[df["Ano"] == a], entre(ini_ant, fim_ant),
                f"{a} (até hoje)", f"{a - 1} (mesmo trecho)")
    if escolha == "Todo o período":
        return df, df.iloc[0:0], "Todo o período disponível", ""
    # "Ano XXXX" e "Ano passado"
    a = hoje_d.year - 1 if escolha == "Ano passado" else int(escolha.split()[-1])
    return df[df["Ano"] == a], df[df["Ano"] == a - 1], f"Ano {a}", f"Ano {a - 1}"


def gauge_sucesso(valor):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=valor,
        number=dict(suffix="%", valueformat=".1f", font=dict(size=34, color=COR_AZUL_ESCURO)),
        gauge=dict(
            axis=dict(range=[0, 100], ticksuffix="%", tickfont=dict(size=10)),
            bar=dict(color=COR_AZUL_ESCURO, thickness=0.3),
            bgcolor=COR_BRANCO, borderwidth=0,
            steps=[dict(range=[0, 70], color="#FDECEA"), dict(range=[70, 85], color="#FFF3E0"),
                   dict(range=[85, 95], color="#E0F2F5"), dict(range=[95, 100], color="#E8F5E9")],
            threshold=dict(line=dict(color=COR_VERDE_ESCURO, width=3), thickness=0.85, value=95),
        ),
        title=dict(text="Taxa de sucesso · meta 95%", font=dict(size=12, color=COR_CINZA_TEXTO)),
    ))
    fig.update_layout(margin=dict(t=50, b=15, l=35, r=35))
    return fig


@st.dialog("Manchete do período", width="large")
def manchete(df_base):
    hoje = agora()
    anos_extra = [f"Ano {a}" for a in sorted(df_base["Ano"].unique(), reverse=True)
                  if a not in (hoje.year, hoje.year - 1)]
    opcoes = ["Mês atual", "Mês anterior", "Últimos 30 dias", "Últimos 90 dias",
              "Este ano", "Ano passado", "Todo o período"] + anos_extra
    escolha = st.selectbox("Período", opcoes, key="manchete_periodo")

    atual, anterior, titulo, titulo_ant = recortar_periodo(df_base, escolha, hoje)
    ia, ip = indicadores(atual), indicadores(anterior)
    tem_anterior = ip["total"] > 0

    if ia["total"] == 0:
        st.error(f"Nenhum dado disponível para **{titulo}**.")
        return

    if ia["com_erro"] == 0 and ia["validados"] > 0:
        st.success(f"**SRE validou {fmt_int(ia['validados'])} cards sem retorno de erro** — "
                   f"100% de aprovação direta em {titulo}.")
    elif ia["taxa_erro"] <= 5:
        st.info(f"**SRE validou {fmt_int(ia['validados'])} cards com apenas "
                f"{fmt_int(ia['com_erro'])} ajuste(s)** — taxa de erro de {fmt_pct(ia['taxa_erro'])} "
                f"em {titulo}.")
    else:
        st.warning(f"**SRE validou {fmt_int(ia['validados'])} cards, {fmt_int(ia['com_erro'])} "
                   f"com retorno** — {fmt_int(ia['sem_erro'])} aprovados direto em {titulo}.")

    def delta(chave):
        return (ia[chave] - ip[chave]) if tem_anterior else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de cards", fmt_int(ia["total"]), delta("total"),
              border=True, help=f"Anterior ({titulo_ant}): {fmt_int(ip['total'])}" if tem_anterior else None)
    c2.metric("Validados", fmt_int(ia["validados"]), delta("validados"), border=True,
              help=f"Anterior: {fmt_int(ip['validados'])}" if tem_anterior else None)
    c3.metric("Sem retorno", fmt_int(ia["sem_erro"]), delta("sem_erro"), border=True,
              help="Sincronizados aprovados na primeira validação")
    c4.metric("Com retorno", fmt_int(ia["com_erro"]), delta("com_erro"), delta_color="inverse",
              border=True, help="Sincronizados que voltaram para ajuste (subir é ruim)")

    g1, g2 = st.columns([1, 1.4])
    with g1:
        mostrar(gauge_sucesso(ia["taxa_sucesso"]), 230)
        if tem_anterior:
            dif = ia["taxa_sucesso"] - ip["taxa_sucesso"]
            st.caption(f"{'▲' if dif >= 0 else '▼'} {abs(dif):.1f} p.p. vs {titulo_ant} "
                       f"({fmt_pct(ip['taxa_sucesso'])}) · {fmt_int(ia['nao_sinc'])} card(s) ainda "
                       f"não sincronizado(s) no período")
    with g2:
        if tem_anterior:
            fig = go.Figure()
            for nome, chave, cor in [("Total", "total", "#B9DDE3"), ("Validados", "validados", COR_AZUL_ESCURO),
                                     ("Com retorno", "com_erro", COR_LARANJA)]:
                fig.add_bar(name=nome, x=[titulo_ant, titulo], y=[ip[chave], ia[chave]], marker_color=cor,
                            text=[ip[chave], ia[chave]], textposition="outside", cliponaxis=False)
            fig.update_layout(barmode="group", title="Período atual vs anterior",
                              yaxis=dict(rangemode="tozero", showticklabels=False),
                              legend=dict(orientation="h", yanchor="top", y=-0.18, x=0),
                              margin=dict(t=40, b=60))
            mostrar(fig, 270)
        else:
            st.caption("Sem período anterior para comparar.")

    t = ia["taxa_sucesso"]
    if t >= 95:
        st.success("**Excelente** — meta de qualidade superada (≥ 95%). Manter os padrões atuais.")
    elif t >= 85:
        st.info("**Bom desempenho** — dentro do esperado (85–94%). Ajustes pontuais.")
    elif t >= 70:
        st.warning("**Oportunidade de melhoria** — abaixo do ideal (70–84%). Identificar causas principais.")
    else:
        st.error("**Atenção necessária** — performance crítica (< 70%). Revisar os fluxos.")

    dias_ativos = atual["Data"].nunique()
    media_dia = f"{ia['total'] / dias_ativos:.1f}".replace(".", ",")
    media_rev = f"{atual['Revisões_Total'].mean():.2f}".replace(".", ",")
    st.caption(f"{dias_ativos} dia(s) com atividade · média de {media_dia} cards/dia ativo · "
               f"média de {media_rev} revisões/card · atualizado em {hoje:%d/%m/%Y %H:%M}")


# ============================================
# CONTEÚDO
# ============================================
if ss.df_original is None:
    st.markdown(f"""
    <div style="text-align:center; padding:3.5rem 2rem; background:{COR_BRANCO};
                border-radius:12px; border:2px dashed {COR_CINZA_BORDA};">
        <h3 style="color:{COR_AZUL_ESCURO}; margin-top:0;">Nenhum dado carregado</h3>
        <p style="color:{COR_CINZA_TEXTO};">Para começar, use <b>Importar CSV</b> na barra lateral
        ou coloque o arquivo <code>{CAMINHO_ARQUIVO_PRINCIPAL}</code> na pasta do app.</p>
    </div>
    """, unsafe_allow_html=True)

else:
    df_base = aplicar_filtros(ss.df_original, periodo=False)  # usado pela Manchete
    df = aplicar_filtros(ss.df_original)

    c_btn, c_info = st.columns([1.3, 5])
    with c_btn:
        if st.button("Ver manchete", icon=":material/newspaper:", type="primary", width="stretch",
                     help="Resumo executivo do período (respeita os filtros de recorte da barra lateral)"):
            manchete(df_base)
    with c_info:
        if not df.empty:
            st.caption(f"**{fmt_int(len(df))}** registros no recorte atual · período de "
                       f"{df['Criado'].min():%d/%m/%Y} a {df['Criado'].max():%d/%m/%Y} · "
                       f"base carregada em {ss.ultima_atualizacao}")

    if df.empty:
        st.warning("Nenhum registro encontrado com os filtros selecionados. "
                   "Use **Limpar filtros** na barra lateral.")
        st.stop()

    dfs = df[df["Sinc"]]  # sincronizados do recorte

    tab_geral, tab_equipe, tab_empresas, tab_ipe, tab_est, tab_dados = st.tabs([
        ":material/dashboard: Visão geral",
        ":material/groups: Equipe",
        ":material/map: Empresas",
        ":material/target: KPI IPE",
        ":material/query_stats: Estatística",
        ":material/table_rows: Dados",
    ])

    # --------------------------------------------
    # VISÃO GERAL
    # --------------------------------------------
    with tab_geral:
        ind = indicadores(df)
        serie_criados = serie_diaria(df["Data"])
        serie_sinc = serie_diaria(dfs["Data"]) if not dfs.empty else pd.Series(dtype=int)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Demandas", fmt_int(ind["total"]), border=True,
                  chart_data=serie_criados.tail(30).tolist(), chart_type="area",
                  help="Cards criados no recorte · gráfico: últimos 30 dias úteis")
        c2.metric("Sincronizados", fmt_int(ind["validados"]), border=True,
                  chart_data=serie_sinc.tail(30).tolist() if not serie_sinc.empty else None,
                  chart_type="area", help="Gráfico: últimos 30 dias úteis")
        c3.metric("Não sincronizados", fmt_int(ind["nao_sinc"]), border=True,
                  help="Cards em qualquer status diferente de 'Sincronizado'")
        c4.metric("Taxa de sucesso", fmt_pct(ind["taxa_sucesso"]), border=True,
                  help="Sincronizados ÷ total de demandas do recorte")
        c5.metric("Taxa de retorno", fmt_pct(ind["taxa_erro"]), border=True,
                  help=f"{fmt_int(ind['com_erro'])} sincronizado(s) com revisão ÷ sincronizados")

        # Evolução mensal
        secao("Evolução mensal", "Demandas criadas e sincronizadas por mês, com a taxa de sucesso abaixo")
        mensal = (df.groupby(["Ano_Mês", "Mês_Label"])
                  .agg(Total=("Sinc", "size"), Sincronizados=("Sinc", "sum"))
                  .reset_index().sort_values("Ano_Mês"))
        mensal["Taxa"] = (mensal["Sincronizados"] / mensal["Total"] * 100).round(1)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28],
                            vertical_spacing=0.06)
        fig.add_bar(x=mensal["Mês_Label"], y=mensal["Total"], name="Demandas", marker_color="#B9DDE3",
                    text=mensal["Total"], textposition="outside", cliponaxis=False, row=1, col=1)
        fig.add_bar(x=mensal["Mês_Label"], y=mensal["Sincronizados"], name="Sincronizados",
                    marker_color=COR_AZUL_ESCURO, text=mensal["Sincronizados"], textposition="inside",
                    row=1, col=1)
        fig.add_scatter(x=mensal["Mês_Label"], y=mensal["Taxa"], name="Taxa de sucesso",
                        mode="lines+markers+text", text=mensal["Taxa"].map(lambda v: f"{v:.0f}%"),
                        textposition="top center", line=dict(color=COR_VERDE_ESCURO, width=2),
                        showlegend=False, row=2, col=1)
        fig.update_layout(barmode="overlay")
        fig.update_yaxes(rangemode="tozero", row=1, col=1)
        fig.update_yaxes(range=[0, 115], showticklabels=False, title_text="Taxa", row=2, col=1)
        fig.update_xaxes(type="category")
        mostrar(fig, 430)

        # Sincronizações diárias
        secao("Sincronizações por dia útil",
              "Barras: quantidade do dia (dias sem sincronização aparecem zerados) · linha: média móvel de 7 dias")
        if serie_sinc.empty:
            st.info("Nenhum card sincronizado no recorte.")
        else:
            mm7 = serie_sinc.rolling(7, min_periods=1).mean()
            fig = go.Figure()
            fig.add_bar(x=serie_sinc.index, y=serie_sinc.values, name="No dia", marker_color="#B9DDE3",
                        hovertemplate="%{x|%d/%m/%Y}: %{y} sinc.<extra></extra>")
            fig.add_scatter(x=mm7.index, y=mm7.values, name="Média 7 dias", mode="lines",
                            line=dict(color=COR_AZUL_ESCURO, width=2.5),
                            hovertemplate="Média 7d: %{y:.1f}<extra></extra>")
            fig.update_xaxes(tickformat="%d/%m", rangebreaks=[dict(bounds=["sat", "mon"])]
                             if serie_sinc.index.dayofweek.max() < 5 else None)
            fig.update_layout(hovermode="x unified")
            mostrar(fig, 340)

            uteis = serie_sinc[serie_sinc.index.dayofweek < 5]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Média por dia útil", f"{uteis.mean():.1f}".replace(".", ","), border=True)
            m2.metric("Melhor dia", f"{serie_sinc.max()} sinc.", border=True,
                      help=f"{serie_sinc.idxmax():%d/%m/%Y}")
            m3.metric("Dias úteis sem sincronização", fmt_int((uteis == 0).sum()), border=True,
                      help=f"De {len(uteis)} dias úteis no intervalo")
            m4.metric("Pior dia útil", f"{uteis.min()} sinc.", border=True,
                      help=f"{uteis.idxmin():%d/%m/%Y}")

        h1, h2 = st.columns(2)
        with h1:
            secao("Calendário de sincronizações", "Cada quadrado é um dia · últimas 26 semanas do recorte")
            if not dfs.empty:
                cont = dfs["Data"].value_counts()
                fim = cont.index.max()
                ini = max(cont.index.min(), fim - timedelta(weeks=26))
                dias = pd.date_range(ini - timedelta(days=ini.dayofweek), fim)
                cal = pd.DataFrame({"Data": dias, "Qtd": cont.reindex(dias, fill_value=0).values})
                cal["Semana"] = cal["Data"] - pd.to_timedelta(cal["Data"].dt.dayofweek, unit="D")
                cal["Dia"] = cal["Data"].dt.dayofweek
                z = cal.pivot(index="Dia", columns="Semana", values="Qtd").reindex(range(7))
                datas_txt = (cal.assign(T=cal["Data"].dt.strftime("%d/%m/%Y"))
                             .pivot(index="Dia", columns="Semana", values="T").reindex(range(7)))
                fig = go.Figure(go.Heatmap(
                    z=z.values, x=z.columns, y=DIAS_CURTOS, customdata=datas_txt.values,
                    colorscale=ESCALA_AZUL, xgap=3, ygap=3, showscale=False,
                    hovertemplate="%{customdata}: %{z} sinc.<extra></extra>"))
                fig.update_yaxes(autorange="reversed", showgrid=False)
                fig.update_xaxes(tickformat="%b", dtick="M1", showgrid=False)
                mostrar(fig, 260)
        with h2:
            secao("Quando as demandas chegam", "Cards criados por dia da semana × hora")
            mapa_hora = (df.pivot_table(index="Dia_Semana", columns="Hora", values="Sinc",
                                        aggfunc="size", fill_value=0)
                         .reindex(index=range(7), fill_value=0))
            mapa_hora = mapa_hora.loc[mapa_hora.sum(axis=1) > 0]
            fig = go.Figure(go.Heatmap(
                z=mapa_hora.values, x=[f"{h}h" for h in mapa_hora.columns],
                y=[DIAS_CURTOS[i] for i in mapa_hora.index], colorscale=ESCALA_AZUL, xgap=2, ygap=2,
                showscale=False, hovertemplate="%{y} %{x}: %{z} demandas<extra></extra>"))
            fig.update_yaxes(autorange="reversed", showgrid=False)
            mostrar(fig, 260)

        t1, t2 = st.columns(2)
        with t1:
            secao("Demandas por tipo")
            tipos = df["Tipo_Chamado"].fillna("Não informado").value_counts().sort_values()
            fig = go.Figure(go.Bar(x=tipos.values, y=tipos.index, orientation="h",
                                   marker_color=COR_AZUL_ESCURO, text=tipos.values,
                                   textposition="outside", cliponaxis=False))
            fig.update_xaxes(showticklabels=False, showgrid=False)
            mostrar(fig, max(260, 34 * len(tipos) + 60))
        with t2:
            secao("Sincronizações por empresa")
            if not dfs.empty:
                emp = dfs["Empresa"].fillna("—").value_counts().sort_values()
                pct = emp / emp.sum() * 100
                fig = go.Figure(go.Bar(x=emp.values, y=emp.index, orientation="h",
                                       marker_color=COR_AZUL_PETROLEO,
                                       text=[f"{v}  ({p:.0f}%)" for v, p in zip(emp.values, pct.values)],
                                       textposition="outside", cliponaxis=False))
                fig.update_xaxes(showticklabels=False, showgrid=False)
                mostrar(fig, max(260, 34 * len(emp) + 60))

    # --------------------------------------------
    # EQUIPE (SREs e responsáveis)
    # --------------------------------------------
    with tab_equipe:
        secao("Performance dos SREs", "Taxa de retorno = sincronizados com revisão ÷ sincronizados do SRE")
        perf = (df.groupby("SRE_Nome")
                .agg(Total=("Sinc", "size"), Sincronizados=("Sinc", "sum"),
                     Com_Retorno=("Com_Revisao", lambda s: int((s & df.loc[s.index, "Sinc"]).sum())),
                     Reabertos=("Reaberto", "sum"))
                .reset_index())
        perf["Taxa_Retorno"] = (perf["Com_Retorno"] / perf["Sincronizados"].where(perf["Sincronizados"] > 0)
                                * 100).fillna(0).round(1)
        perf["Participação"] = (perf["Sincronizados"] / max(perf["Sincronizados"].sum(), 1) * 100).round(1)
        perf = perf.sort_values("Sincronizados", ascending=False)

        top = perf[perf["Sincronizados"] > 0].head(3)
        cols = st.columns(3)
        for col, (_, linha), medalha in zip(cols, top.iterrows(), ["🥇", "🥈", "🥉"]):
            col.metric(f"{medalha} {linha['SRE_Nome']}", f"{fmt_int(linha['Sincronizados'])} sinc.",
                       border=True, help=f"{fmt_pct(linha['Participação'])} do total · taxa de retorno "
                                         f"{fmt_pct(linha['Taxa_Retorno'])}")

        g1, g2 = st.columns([1, 1.3])
        with g1:
            ordem = perf.sort_values("Sincronizados")
            fig = go.Figure(go.Bar(x=ordem["Sincronizados"], y=ordem["SRE_Nome"], orientation="h",
                                   marker_color=COR_AZUL_ESCURO, text=ordem["Sincronizados"],
                                   textposition="outside", cliponaxis=False))
            fig.update_layout(title="Sincronizados por SRE")
            fig.update_xaxes(showticklabels=False)
            mostrar(fig, max(300, 40 * len(ordem) + 80))
        with g2:
            st.dataframe(
                perf[["SRE_Nome", "Total", "Sincronizados", "Com_Retorno", "Taxa_Retorno", "Participação"]],
                hide_index=True, width="stretch",
                column_config={
                    "SRE_Nome": st.column_config.TextColumn("SRE"),
                    "Total": st.column_config.NumberColumn("Cards", format="%d"),
                    "Sincronizados": st.column_config.NumberColumn("Sincronizados", format="%d"),
                    "Com_Retorno": st.column_config.NumberColumn("Com retorno", format="%d"),
                    "Taxa_Retorno": st.column_config.NumberColumn("Taxa retorno", format="%.1f%%"),
                    "Participação": st.column_config.ProgressColumn("Participação", format="%.1f%%",
                                                                    min_value=0, max_value=100),
                })

        secao("Sincronizações por SRE ao longo do tempo", "Total por mês")
        if not dfs.empty:
            mensal_sre = (dfs.groupby(["Ano_Mês", "Mês_Label", "SRE_Nome"]).size()
                          .reset_index(name="Qtd").sort_values("Ano_Mês"))
            fig = px.line(mensal_sre, x="Mês_Label", y="Qtd", color="SRE_Nome", markers=True,
                          labels={"Mês_Label": "", "Qtd": "Sincronizações", "SRE_Nome": "SRE"})
            fig.update_traces(line_width=2.5, hovertemplate="%{x}: %{y}<extra>%{fullData.name}</extra>")
            fig.update_xaxes(type="category")
            fig.update_yaxes(rangemode="tozero")
            fig.update_layout(hovermode="x unified")
            mostrar(fig, 340)

        r1, r2 = st.columns(2)
        with r1:
            secao("Top 10 responsáveis", "Por número de demandas")
            topr = df["Responsável_Formatado"].value_counts().head(10).sort_values()
            fig = go.Figure(go.Bar(x=topr.values, y=topr.index, orientation="h",
                                   marker_color=COR_AZUL_PETROLEO, text=topr.values,
                                   textposition="outside", cliponaxis=False))
            fig.update_xaxes(showticklabels=False)
            mostrar(fig, 420)
        with r2:
            secao("Revisões por responsável", "Top 15 · soma das revisões dos cards")
            rev = (df[df["Com_Revisao"]].groupby("Responsável_Formatado")
                   .agg(Revisões=("Revisões_Total", "sum"), Cards=("Chamado", "count"))
                   .sort_values("Revisões", ascending=False).head(15).sort_values("Revisões"))
            if rev.empty:
                st.success("Nenhuma revisão registrada no recorte.")
            else:
                fig = go.Figure(go.Bar(
                    x=rev["Revisões"], y=rev.index, orientation="h",
                    marker_color=COR_LARANJA,
                    text=rev["Revisões"], textposition="outside", cliponaxis=False,
                    customdata=rev["Cards"],
                    hovertemplate="%{y}<br>%{x} revisões em %{customdata} cards<extra></extra>"))
                fig.update_xaxes(showticklabels=False)
                mostrar(fig, 420)

    # --------------------------------------------
    # EMPRESAS (mapa)
    # --------------------------------------------
    def dados_mapa(dfs_):
        cont = dfs_["Empresa"].value_counts()
        linhas = []
        for empresa, info in MAPEAMENTO_EMPRESAS.items():
            if ss.f_empresas and empresa not in ss.f_empresas:
                continue
            linhas.append({**info, "empresa": empresa, "empresa_nome": info["nome_completo"],
                           "sincronismos": int(cont.get(empresa, 0))})
        return pd.DataFrame(linhas)

    def cor_volume(valor, minimo, maximo):
        """Escala de um tom só: azul-claro (pouco) → azul-escuro (muito)."""
        t = 0.5 if maximo == minimo else (valor - minimo) / (maximo - minimo)
        a, b = (0x5F, 0xB3, 0xC2), (0x00, 0x3F, 0x52)
        return "#{:02X}{:02X}{:02X}".format(*(int(a[i] + t * (b[i] - a[i])) for i in range(3)))

    def criar_mapa(df_mapa):
        try:
            import folium
        except ImportError:
            st.error("Biblioteca 'folium' não instalada. Execute: pip install folium")
            return None
        bolhas = df_mapa[df_mapa["sincronismos"] > 0]
        m = folium.Map(location=[-14.5, -51.5], zoom_start=4, tiles=None, prefer_canvas=True)
        folium.TileLayer(
            tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
                 '&copy; <a href="https://carto.com/attributions">CARTO</a>',
            name="CartoDB Positron", max_zoom=19, subdomains="abcd").add_to(m)
        if bolhas.empty:
            return m
        mx, mn, total = bolhas["sincronismos"].max(), bolhas["sincronismos"].min(), bolhas["sincronismos"].sum()
        ranking = {e: i + 1 for i, e in enumerate(bolhas.sort_values("sincronismos", ascending=False)["empresa"])}
        for _, row in bolhas.iterrows():
            v = row["sincronismos"]
            r = 45 if mx == mn else 18 + (v - mn) / (mx - mn) * 50
            cor = cor_volume(v, mn, mx)
            pct = v / total * 100
            tooltip = f"""
            <div style="font-family:Inter,'Segoe UI',sans-serif; min-width:200px;">
              <div style="font-weight:700; font-size:13px; color:{COR_AZUL_ESCURO}; margin-bottom:6px;">
                {row['empresa_nome']}</div>
              <table style="width:100%; font-size:12px;">
                <tr><td style="color:{COR_CINZA_TEXTO}">Código</td><td style="text-align:right"><b>{row['empresa']}</b></td></tr>
                <tr><td style="color:{COR_CINZA_TEXTO}">Estado</td><td style="text-align:right">{row['estado']} ({row['sigla']})</td></tr>
                <tr><td style="color:{COR_CINZA_TEXTO}">Sincronizações</td><td style="text-align:right"><b>{v:,}</b></td></tr>
                <tr><td style="color:{COR_CINZA_TEXTO}">% do total</td><td style="text-align:right">{pct:.1f}%</td></tr>
                <tr><td style="color:{COR_CINZA_TEXTO}">Ranking</td><td style="text-align:right">{ranking[row['empresa']]}º</td></tr>
              </table>
            </div>"""
            folium.CircleMarker(location=[row["latitude"], row["longitude"]], radius=r,
                                color=COR_BRANCO, weight=2, fill=True, fill_color=cor, fill_opacity=0.85,
                                tooltip=folium.Tooltip(tooltip, sticky=True)).add_to(m)
            fs = max(10, min(15, int(r * 0.38)))
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                icon=folium.DivIcon(
                    html=f"""<div style="font-family:Inter,'Segoe UI',sans-serif; text-align:center;
                                 color:#fff; font-weight:700; line-height:1.15; white-space:nowrap;
                                 text-shadow:0 1px 2px rgba(0,0,0,.45);">
                               <div style="font-size:{fs}px">{row['empresa']}</div>
                               <div style="font-size:{fs - 2}px; font-weight:600">{v}</div></div>""",
                    icon_size=(int(r * 1.8), int(r * 1.8)), icon_anchor=(int(r * 0.9), int(r * 0.6)))
            ).add_to(m)
        legenda = f"""
        <div style="position:absolute; bottom:18px; left:14px; z-index:9999; background:#fff;
                    border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,.12); padding:8px 12px;
                    font:11px Inter,'Segoe UI',sans-serif; color:{COR_CINZA_TEXTO};">
          <div style="width:120px; height:8px; border-radius:4px;
                      background:linear-gradient(to right,#5FB3C2,#003F52);"></div>
          <div style="display:flex; justify-content:space-between; margin-top:3px;">
            <span>{mn}</span><span>{mx}</span></div>
        </div>"""
        m.get_root().html.add_child(folium.Element(legenda))
        return m

    with tab_empresas:
        df_mapa = dados_mapa(dfs)
        total_mapa = int(df_mapa["sincronismos"].sum()) if not df_mapa.empty else 0
        ativas = df_mapa[df_mapa["sincronismos"] > 0] if not df_mapa.empty else df_mapa

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Sincronizações", fmt_int(total_mapa), border=True)
        k2.metric("Empresas com sincronização", f"{len(ativas)} de {len(df_mapa)}", border=True)
        k3.metric("Média por empresa", f"{df_mapa['sincronismos'].mean():.1f}".replace(".", ",")
                  if not df_mapa.empty else "0", border=True)
        if not ativas.empty:
            lider = ativas.sort_values("sincronismos", ascending=False).iloc[0]
            k4.metric("Maior volume", f"{lider['empresa']} · {fmt_int(lider['sincronismos'])}", border=True,
                      help=lider["empresa_nome"])
        else:
            k4.metric("Maior volume", "—", border=True)

        cm, cr = st.columns([2.4, 1])
        with cm:
            secao("Mapa de sincronizações", "Tamanho e tom da bolha proporcionais ao volume · passe o mouse para detalhes")
            m = criar_mapa(df_mapa) if not df_mapa.empty else None
            if m is not None:
                m.get_root().width = "100%"
                m.get_root().height = "540px"
                html_mapa = m.get_root().render()
                with st.container(border=True):
                    if hasattr(st, "iframe"):
                        st.iframe(html_mapa, height=545)
                    else:  # versões antigas do Streamlit
                        st.components.v1.html(html_mapa, height=545)
            else:
                st.info("Nenhuma empresa para exibir no mapa.")
        with cr:
            secao("Ranking")
            if not ativas.empty:
                itens = ""
                ordenado = df_mapa.sort_values("sincronismos", ascending=False).reset_index(drop=True)
                for i, row in ordenado.iterrows():
                    pos = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i + 1}º"
                    pct = row["sincronismos"] / total_mapa * 100 if total_mapa else 0
                    itens += (f'<div class="rank-item"><div class="pos">{pos}</div>'
                              f'<div class="nome">{row["empresa"]}<small>{row["estado"]}</small></div>'
                              f'<div class="valor">{row["sincronismos"]:,}<small>{pct:.1f}%</small></div></div>')
                with st.container(border=True):
                    st.markdown(itens, unsafe_allow_html=True)

        secao("Evolução mensal por empresa", "Sincronizações por mês, empilhadas (5 maiores + demais)")
        if not dfs.empty:
            top5 = list(dfs["Empresa"].value_counts().head(5).index)
            mens_emp = (dfs.assign(Grupo=dfs["Empresa"].where(dfs["Empresa"].isin(top5), "Demais"))
                        .groupby(["Ano_Mês", "Mês_Label", "Grupo"]).size()
                        .reset_index(name="Qtd").sort_values("Ano_Mês"))
            fig = px.bar(mens_emp, x="Mês_Label", y="Qtd", color="Grupo",
                         category_orders={"Grupo": top5 + ["Demais"]},
                         color_discrete_map={"Demais": "#CED4DA"},
                         labels={"Mês_Label": "", "Qtd": "Sincronizações", "Grupo": "Empresa"})
            fig.update_xaxes(type="category")
            fig.update_layout(hovermode="x unified")
            mostrar(fig, 340)

        with st.expander("Detalhes por empresa"):
            if not df_mapa.empty:
                tab = (df_mapa[["empresa", "empresa_nome", "sigla", "estado", "regiao", "sincronismos"]]
                       .sort_values("sincronismos", ascending=False).reset_index(drop=True))
                tab["pct"] = (tab["sincronismos"] / total_mapa * 100).round(1) if total_mapa else 0.0
                tab.columns = ["Código", "Empresa", "UF", "Estado", "Região", "Sincronizações", "% do total"]
                st.dataframe(tab, hide_index=True, width="stretch", column_config={
                    "% do total": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100)})
                st.download_button("Exportar CSV", tab.to_csv(index=False).encode("utf-8-sig"),
                                   file_name=f"sincronismos_empresas_{agora():%Y%m%d_%H%M}.csv",
                                   mime="text/csv", icon=":material/download:")

    # --------------------------------------------
    # KPI IPE
    # --------------------------------------------
    with tab_ipe:
        secao("IPE · Índice de Performance do Especialista",
              f"Meta {META_IPE}% · período definido pelos filtros da barra lateral")

        cd_total = len(df)
        na_total = df["SRE_Nome"].nunique()
        linhas_ipe = []
        for sre, d in df.groupby("SRE_Nome"):
            cd, ca, cr = len(d), int(d["Sinc"].sum()), int(d["Reaberto"].sum())
            ipe = calcular_ipe(ca, cr, cd, cd_total, na_total) * 100
            linhas_ipe.append({"SRE": sre, "Demandados": cd, "Analisados": ca, "Reabertos": cr,
                               "IPE": round(ipe, 2), "Status": "✅ Na meta" if ipe >= META_IPE else "⚠️ Abaixo"})
        df_ipe = pd.DataFrame(linhas_ipe).sort_values("IPE", ascending=False)

        i1, i2 = st.columns([1.2, 1])
        with i1:
            ordem = df_ipe.sort_values("IPE")
            cores = [COR_VERDE_ESCURO if v >= META_IPE else COR_LARANJA for v in ordem["IPE"]]
            fig = go.Figure(go.Bar(x=ordem["IPE"], y=ordem["SRE"], orientation="h", marker_color=cores,
                                   text=ordem["IPE"].map(fmt_pct), textposition="outside",
                                   cliponaxis=False))
            fig.add_vline(x=META_IPE, line_dash="dash", line_color=COR_CINZA_TEXTO,
                          annotation_text=f"Meta {META_IPE}%", annotation_position="top")
            fig.update_xaxes(range=[0, 108], ticksuffix="%")
            fig.update_layout(title="IPE por SRE")
            mostrar(fig, max(300, 42 * len(ordem) + 90))
        with i2:
            st.dataframe(df_ipe, hide_index=True, width="stretch", column_config={
                "IPE": st.column_config.ProgressColumn("IPE", format="%.2f%%", min_value=0, max_value=100)})

        secao("IPE acumulado por mês", "Cada ponto considera todos os cards do início do recorte até aquele mês")
        acumulados = []
        for periodo in sorted(df["Ano_Mês"].unique()):
            d = df[df["Ano_Mês"] <= periodo]
            cd, ca, cr, na = len(d), int(d["Sinc"].sum()), int(d["Reaberto"].sum()), d["SRE_Nome"].nunique()
            ano, mes = periodo.split("-")
            acumulados.append({"Mês": f"{MESES_ABREV[int(mes)]}/{ano[2:]}", "CD": cd, "CA": ca, "CR": cr,
                               "SREs": na, "IPE": round(calcular_ipe(ca, cr, cd, cd, na) * 100, 2)})
        df_acum = pd.DataFrame(acumulados)
        if not df_acum.empty:
            fig = go.Figure()
            fig.add_scatter(x=df_acum["Mês"], y=df_acum["IPE"], mode="lines+markers+text",
                            line=dict(color=COR_AZUL_ESCURO, width=3), marker=dict(size=9),
                            fill="tozeroy", fillcolor="rgba(2,138,159,0.08)",
                            text=df_acum["IPE"].map(fmt_pct), textposition="top center",
                            customdata=df_acum[["CD", "CA", "CR", "SREs"]].values,
                            hovertemplate="<b>%{x}</b><br>IPE: %{y:.2f}%<br>CD: %{customdata[0]}"
                                          "<br>CA: %{customdata[1]}<br>CR: %{customdata[2]}"
                                          "<br>SREs: %{customdata[3]}<extra></extra>")
            fig.add_hline(y=META_IPE, line_dash="dash", line_color=COR_VERDE_ESCURO,
                          annotation_text=f"Meta {META_IPE}%", annotation_position="bottom right")
            fig.update_yaxes(range=[0, 108], ticksuffix="%")
            fig.update_xaxes(type="category", range=[-0.6, len(df_acum) - 0.4])
            fig.update_layout(margin=dict(t=30, l=10, r=30))
            mostrar(fig, 380)

            ult = df_acum.iloc[-1]
            a1, a2, a3, a4 = st.columns(4)
            a1.metric("Período", f"{len(df_acum)} meses", border=True,
                      help=f"{df_acum.iloc[0]['Mês']} a {ult['Mês']}")
            a2.metric("Cards", fmt_int(ult["CD"]), border=True)
            a3.metric("IPE acumulado", fmt_pct(ult["IPE"], 2), f"{ult['IPE'] - META_IPE:+.2f} p.p. vs meta",
                      border=True)
            a4.metric("SREs ativos", int(ult["SREs"]), border=True)

            with st.expander("Tabela de acumulados"):
                st.dataframe(df_acum, hide_index=True, width="stretch", column_config={
                    "IPE": st.column_config.ProgressColumn("IPE", format="%.2f%%", min_value=0, max_value=100)})
                st.download_button("Exportar CSV", df_acum.to_csv(index=False).encode("utf-8-sig"),
                                   file_name=f"ipe_acumulado_{agora():%Y%m%d_%H%M}.csv", mime="text/csv",
                                   icon=":material/download:")

        with st.expander("Entenda o cálculo do IPE"):
            st.markdown(f"""
**Fórmula:** `IPE = (CA − CR) / (CD + |((CT / CD) / NA) − 1|)`, limitado a 100%

- **CA** = cards analisados (status *Sincronizado*)
- **CR** = cards reabertos (*Retorno Cliente = Sim*; vazio conta como *Não*)
- **CD** = cards demandados do SRE no período
- **CT** = total de cards do período (todos os SREs)
- **NA** = número de SREs no período

**Meta: {META_IPE}%**. No acumulado mensal, CT = CD (todos os cards até o mês).
""")

    # --------------------------------------------
    # ESTATÍSTICA
    # --------------------------------------------
    with tab_est:
        secao("Distribuição das sincronizações diárias",
              "Inclui os dias úteis sem nenhuma sincronização (contam como zero)")
        percentil = st.number_input("Percentil de referência (%)", min_value=50, max_value=99, value=75,
                                    step=5, help="Percentil destacado na distribuição e na tendência")
        if dfs.empty:
            st.warning("Nenhum card sincronizado no recorte.")
        else:
            valores = serie_diaria(dfs["Data"])
            q = {p: valores.quantile(p / 100) for p in (10, 25, 50, 75, 90)}
            p_ref = valores.quantile(percentil / 100)

            # Contagens são inteiras: barra por valor, centrada no número
            freq = valores.value_counts().sort_index()
            freq = freq.reindex(range(0, int(freq.index.max()) + 1), fill_value=0)
            fig = go.Figure(go.Bar(x=freq.index, y=freq.values, marker_color="#B9DDE3",
                                   marker_line_color=COR_AZUL_PETROLEO, marker_line_width=1,
                                   hovertemplate="%{x} sinc. no dia: %{y} dias<extra></extra>"))
            for p, cor, estilo in [(25, COR_AZUL_PETROLEO, "dot"), (50, COR_AZUL_ESCURO, "dash"),
                                   (75, COR_AZUL_PETROLEO, "dot")]:
                if p == percentil:
                    continue  # já desenhado como percentil de referência
                fig.add_vline(x=q[p], line_dash=estilo, line_color=cor,
                              annotation_text=f"P{p}: {q[p]:.0f}", annotation_position="top")
            fig.add_vline(x=p_ref, line_color=COR_VERMELHO, line_width=2,
                          annotation_text=f"P{percentil} (ref.): {p_ref:.0f}", annotation_position="top right")
            fig.update_layout(xaxis_title="Sincronizações no dia", yaxis_title="Nº de dias", bargap=0.08)
            fig.update_xaxes(dtick=1)
            mostrar(fig, 380)

            cols = st.columns(6)
            for col, (rotulo, v) in zip(cols, [("P10", q[10]), ("Q1 · P25", q[25]), ("Mediana", q[50]),
                                               ("Q3 · P75", q[75]), ("P90", q[90]),
                                               (f"P{percentil} (ref.)", p_ref)]):
                col.metric(rotulo, f"{v:.0f}", border=True)

            secao("Tendência dos percentis por mês", f"Faixa P25–P90, mediana, média e P{percentil}")
            linhas_t = []
            for periodo, d in dfs.groupby("Ano_Mês"):
                v = serie_diaria(d["Data"])
                ano, mes = periodo.split("-")
                linhas_t.append({"Ano_Mês": periodo, "Mês": f"{MESES_ABREV[int(mes)]}/{ano[2:]}",
                                 "P25": v.quantile(.25),
                                 "P50": v.quantile(.5), f"P{percentil}": v.quantile(percentil / 100),
                                 "P90": v.quantile(.9), "Média": v.mean(), "Dias úteis": len(v),
                                 "Sincronizados": int(v.sum())})
            df_tend = pd.DataFrame(linhas_t)

            fig = go.Figure()
            fig.add_scatter(x=df_tend["Mês"], y=df_tend["P90"], mode="lines", line=dict(width=0),
                            showlegend=False, hoverinfo="skip")
            fig.add_scatter(x=df_tend["Mês"], y=df_tend["P25"], mode="lines", line=dict(width=0),
                            fill="tonexty", fillcolor="rgba(2,138,159,0.15)", name="Faixa P25–P90",
                            hoverinfo="skip")
            fig.add_scatter(x=df_tend["Mês"], y=df_tend["P50"], mode="lines+markers", name="Mediana",
                            line=dict(color=COR_AZUL_ESCURO, width=2.5))
            fig.add_scatter(x=df_tend["Mês"], y=df_tend["Média"], mode="lines+markers", name="Média",
                            line=dict(color=COR_VERDE_ESCURO, width=2, dash="dash"))
            fig.add_scatter(x=df_tend["Mês"], y=df_tend[f"P{percentil}"], mode="lines+markers",
                            name=f"P{percentil}", line=dict(color=COR_VERMELHO, width=2))
            fig.update_layout(hovermode="x unified", yaxis_title="Sincronizações por dia útil")
            fig.update_xaxes(type="category")
            mostrar(fig, 380)

            # Tendência: últimos meses FECHADOS vs mesmo número de meses imediatamente anteriores.
            # O mês corrente (incompleto) fica de fora para não puxar o resultado para baixo.
            fechados = df_tend[df_tend["Ano_Mês"] < agora().strftime("%Y-%m")]
            janela = min(3, len(fechados) // 2)
            if janela >= 1:
                recente = fechados.tail(janela)
                anterior_t = fechados.iloc[-2 * janela:-janela]
                rot = f"{recente.iloc[0]['Mês']}–{recente.iloc[-1]['Mês']}" if janela > 1 else recente.iloc[0]["Mês"]
                rot_ant = (f"{anterior_t.iloc[0]['Mês']}–{anterior_t.iloc[-1]['Mês']}"
                           if janela > 1 else anterior_t.iloc[0]["Mês"])

                def var(c):
                    a, r = anterior_t[c].mean(), recente[c].mean()
                    return (r - a) / a * 100 if a > 0 else 0.0

                def num(v):
                    return f"{v:.1f}".replace(".", ",")

                v1, v2, v3 = st.columns(3)
                v1.metric(f"Média diária · {rot}", num(recente["Média"].mean()),
                          f"{var('Média'):+.1f}% vs {rot_ant}", border=True)
                v2.metric(f"Mediana · {rot}", num(recente["P50"].mean()), f"{var('P50'):+.1f}%", border=True)
                v3.metric(f"P{percentil} · {rot}", num(recente[f"P{percentil}"].mean()),
                          f"{var(f'P{percentil}'):+.1f}%", border=True)
                vm = var("Média")
                if vm > 10:
                    st.success(f"Tendência **positiva**: a média diária subiu {vm:.1f}% ({rot} vs {rot_ant}).")
                elif vm >= -10:
                    st.info(f"Tendência **estável**: a média diária variou {vm:+.1f}% ({rot} vs {rot_ant}).")
                else:
                    st.error(f"Tendência **negativa**: a média diária caiu {abs(vm):.1f}% ({rot} vs {rot_ant}).")
                st.caption("Compara os últimos meses fechados com o mesmo número de meses anteriores; "
                           "o mês corrente fica de fora por estar incompleto.")
            else:
                st.caption("São necessários pelo menos 2 meses fechados para calcular a tendência.")

            with st.expander("Tabela de tendência"):
                st.dataframe(df_tend.drop(columns="Ano_Mês").round(1), hide_index=True, width="stretch")

            e1, e2 = st.columns(2)
            e1.download_button("Exportar tendência",
                               df_tend.drop(columns="Ano_Mês").to_csv(index=False).encode("utf-8-sig"),
                               file_name=f"tendencia_percentis_{agora():%Y%m%d_%H%M}.csv", mime="text/csv",
                               icon=":material/download:", width="stretch")
            e2.download_button("Exportar sincronizações diárias",
                               valores.rename_axis("Data").reset_index(name="Quantidade")
                               .assign(Data=lambda x: x["Data"].dt.strftime("%d/%m/%Y"))
                               .to_csv(index=False).encode("utf-8-sig"),
                               file_name=f"sincronizacoes_diarias_{agora():%Y%m%d_%H%M}.csv", mime="text/csv",
                               icon=":material/download:", width="stretch")

    # --------------------------------------------
    # DADOS
    # --------------------------------------------
    with tab_dados:
        secao("Demandas registradas", "Respeita todos os filtros da barra lateral")
        colunas_disp = {
            "Chamado": "Chamado", "Tipo_Chamado": "Tipo", "Responsável_Formatado": "Responsável",
            "Status": "Status", "Prioridade": "Prioridade", "SRE_Nome": "SRE", "Empresa": "Empresa",
            "Revisões": "Revisões", "Qtd. Revisões": "Qtd. revisões", "Revisões_Total": "Revisões (total)",
            "Retorno_Cliente": "Retorno cliente", "Criado": "Criado", "Modificado": "Modificado",
        }
        colunas_disp = {k: v for k, v in colunas_disp.items() if k in df.columns}
        d1, d2, d3 = st.columns([1, 1, 2])
        with d1:
            qtd = st.selectbox("Linhas", [15, 50, 100, 500, "Todas"], index=0)
        with d2:
            ordenar = st.selectbox("Ordenar por", ["Mais recentes", "Mais antigas",
                                                   "Mais revisões", "Menos revisões"])
        with d3:
            escolhidas = st.multiselect("Colunas", list(colunas_disp.values()),
                                        default=["Chamado", "Tipo", "Responsável", "Status", "SRE",
                                                 "Empresa", "Revisões (total)", "Criado"])
        ordem_cfg = {"Mais recentes": ("Criado", False), "Mais antigas": ("Criado", True),
                     "Mais revisões": ("Revisões_Total", False), "Menos revisões": ("Revisões_Total", True)}
        col_ord, asc = ordem_cfg[ordenar]
        tabela = df.sort_values(col_ord, ascending=asc)
        if qtd != "Todas":
            tabela = tabela.head(qtd)
        inverso = {v: k for k, v in colunas_disp.items()}
        tabela = tabela[[inverso[c] for c in escolhidas]].rename(columns=colunas_disp)
        st.dataframe(tabela, hide_index=True, width="stretch", height=460, column_config={
            "Criado": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm"),
            "Modificado": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm")})
        st.download_button("Exportar esta tabela", tabela.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"demandas_{agora():%Y%m%d_%H%M}.csv", mime="text/csv",
                           icon=":material/download:")


# ============================================
# RODAPÉ
# ============================================
st.markdown(f"""
<div class="footer">
  Desenvolvido por <b style="color:{COR_AZUL_ESCURO}">TIME SRE | GAUT</b> ·
  <a href="mailto:kewin.ferreira@energisa.com.br">kewin.ferreira@energisa.com.br</a><br>
  © {agora().year} Esteira SRE Dashboard · Sistema proprietário Energisa · v{VERSAO}
  · Base carregada em {ss.ultima_atualizacao or '—'} (Brasília)
</div>
""", unsafe_allow_html=True)
