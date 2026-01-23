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
import requests
from pathlib import Path
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURAÇÃO DE PRIORIDADE DE FONTES
# ============================================
# ORDEM DE PRIORIDADE: 1. Upload → 2. Arquivo Local → 3. GitHub
GITHUB_RAW_URL = "https://raw.githubusercontent.com/seu-usuario/seu-repo/main/esteira_demandas.csv"

# CONFIGURE AQUI O CAMINHO DO SEU ARQUIVO LOCAL
CAMINHO_ARQUIVO_PRINCIPAL = "esteira_demandas.csv"

# Caminhos alternativos para busca local
CAMINHOS_ALTERNATIVOS = [
    "data/esteira_demandas.csv",
    "dados/esteira_demandas.csv", 
    "database/esteira_demandas.csv",
    "base_dados.csv",
    "dados.csv"
]

# Configuração de polling para verificar mudanças
POLLING_INTERVAL = 30  # segundos

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
# NOVAS FUNÇÕES PARA SISTEMA DE FONTES
# ============================================

def detectar_fonte_atual():
    """Detecta qual fonte está sendo usada atualmente"""
    if 'fonte_atual' in st.session_state:
        return st.session_state.fonte_atual
    return None

def determinar_melhor_fonte_disponivel():
    """Determina a melhor fonte disponível seguindo a prioridade"""
    # 1. Verificar se há upload na sessão
    if 'uploaded_file_name' in st.session_state and st.session_state.uploaded_file_name:
        return {
            'tipo': 'upload',
            'nome': st.session_state.uploaded_file_name,
            'prioridade': 1
        }
    
    # 2. Verificar arquivo local
    caminho_local = encontrar_arquivo_dados()
    if caminho_local:
        return {
            'tipo': 'local',
            'caminho': caminho_local,
            'nome': os.path.basename(caminho_local),
            'prioridade': 2
        }
    
    # 3. GitHub como fallback
    return {
        'tipo': 'github',
        'url': GITHUB_RAW_URL,
        'nome': 'GitHub (demo)',
        'prioridade': 3
    }

def carregar_da_fonte(fonte):
    """Carrega dados da fonte especificada"""
    try:
        if fonte['tipo'] == 'upload':
            # Recarregar do session state
            if 'df_original' in st.session_state:
                return st.session_state.df_original, f"✅ Dados do upload: {fonte['nome']}", fonte
        
        elif fonte['tipo'] == 'local':
            df, status, hash_conteudo = carregar_dados(caminho_arquivo=fonte['caminho'])
            if df is not None:
                return df, f"✅ Dados locais: {fonte['nome']}", fonte
        
        elif fonte['tipo'] == 'github':
            # Tentar carregar do GitHub
            response = requests.get(fonte['url'])
            if response.status_code == 200:
                # Criar arquivo temporário
                temp_path = "temp_github.csv"
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                
                df, status, hash_conteudo = carregar_dados(caminho_arquivo=temp_path)
                os.remove(temp_path)
                
                if df is not None:
                    return df, f"✅ Dados do GitHub: {fonte['nome']}", fonte
        
        return None, f"❌ Não foi possível carregar da fonte: {fonte['tipo']}", fonte
    
    except Exception as e:
        return None, f"❌ Erro ao carregar da fonte {fonte['tipo']}: {str(e)}", fonte

def verificar_modificacao_arquivo_local():
    """Verifica se o arquivo local foi modificado"""
    if 'fonte_atual' not in st.session_state:
        return False
    
    fonte = st.session_state.fonte_atual
    
    if fonte['tipo'] != 'local':
        return False
    
    if 'caminho' not in fonte or not os.path.exists(fonte['caminho']):
        return False
    
    # Verificar última modificação
    if 'ultima_modificacao_fonte' not in st.session_state:
        st.session_state.ultima_modificacao_fonte = os.path.getmtime(fonte['caminho'])
        return False
    
    modificacao_atual = os.path.getmtime(fonte['caminho'])
    
    if modificacao_atual > st.session_state.ultima_modificacao_fonte:
        st.session_state.ultima_modificacao_fonte = modificacao_atual
        return True
    
    return False

def inicializar_sistema_fontes():
    """Inicializa o sistema de fontes na sessão"""
    if 'sistema_fontes_inicializado' not in st.session_state:
        st.session_state.sistema_fontes_inicializado = True
        st.session_state.fonte_atual = None
        st.session_state.ultima_modificacao_fonte = None
        st.session_state.ultima_verificacao_polling = time.time()

# ============================================
# FUNÇÕES AUXILIARES EXISTENTES (ATUALIZADAS)
# ============================================

@st.cache_data
def carregar_dados(uploaded_file=None, caminho_arquivo=None):
    """Carrega e processa os dados - VERSÃO ATUALIZADA"""
    try:
        conteudo_bytes = None
        conteudo = None
        
        if uploaded_file:
            # Ler conteúdo como bytes para hash
            conteudo_bytes = uploaded_file.getvalue()
            conteudo = conteudo_bytes.decode('utf-8-sig')
        elif caminho_arquivo and os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8-sig') as f:
                conteudo = f.read()
            conteudo_bytes = conteudo.encode('utf-8')
        else:
            return None, "Nenhum arquivo fornecido", None
        
        # Resto do processamento (mantido igual)...
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
            return None, "Formato de arquivo inválido", None
        
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
            df['Mês_Num'] = df['Criado'].dt.month
            df['Dia'] = df['Criado'].dt.day
            df['Hora'] = df['Criado'].dt.hour
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
        
        # Calcular hash do conteúdo
        hash_conteudo = calcular_hash_arquivo(conteudo_bytes) if conteudo_bytes else None
        
        return df, "✅ Dados carregados com sucesso", hash_conteudo
    
    except Exception as e:
        return None, f"Erro: {str(e)}", None

def encontrar_arquivo_dados():
    """Tenta encontrar o arquivo de dados em vários caminhos possíveis"""
    # Tentar primeiro o caminho principal
    if os.path.exists(CAMINHO_ARQUIVO_PRINCIPAL):
        return CAMINHO_ARQUIVO_PRINCIPAL
    
    # Tentar caminhos alternativos
    for caminho in CAMINHOS_ALTERNATIVOS:
        if os.path.exists(caminho):
            return caminho
    
    return None

def calcular_hash_arquivo(conteudo):
    """Calcula hash do conteúdo do arquivo para detectar mudanças"""
    return hashlib.md5(conteudo).hexdigest()

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

def criar_card_indicador_simples(valor, label, icone="📊"):
    """Cria card de indicador SIMPLES - sem delta"""
    # Verificar se o valor é numérico para formatar com vírgula
    if isinstance(valor, (int, float)):
        valor_formatado = f"{valor:,}"
    else:
        valor_formatado = str(valor)
    
    return f'''
    <div class="metric-card-exec">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <span style="font-size: 1.5rem;">{icone}</span>
            <div style="flex-grow: 1;">
                <div class="metric-value">{valor_formatado}</div>
                <div class="metric-label">{label}</div>
            </div>
        </div>
    </div>
    '''

def get_horario_brasilia():
    """Retorna o horário atual de Brasília"""
    try:
        tz = timezone('America/Sao_Paulo')
        return datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    except:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

# ============================================
# SIDEBAR - FILTROS E CONTROLES (ATUALIZADA)
# ============================================

# Inicializar sistema de fontes
inicializar_sistema_fontes()

with st.sidebar:
    # Logo e título
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h3 style="color: #1e3799; margin: 0;">⚙️ Painel de Controle</h3>
        <p style="color: #6c757d; margin: 0; font-size: 0.9rem;">Filtros e Configurações</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============================================
    # SEÇÃO DE STATUS DA FONTE ATUAL
    # ============================================
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("**📊 Status da Fonte de Dados**")
    
    # Verificar modificação do arquivo local
    arquivo_modificado = False
    if verificar_modificacao_arquivo_local():
        arquivo_modificado = True
        st.warning("⚠️ O arquivo local foi modificado!")
    
    # Mostrar fonte atual
    fonte_atual = detectar_fonte_atual()
    
    if fonte_atual:
        # Badge colorido baseado no tipo
        if fonte_atual['tipo'] == 'upload':
            badge_cor = "success"
            badge_texto = "UPLOAD"
            icone = "📤"
        elif fonte_atual['tipo'] == 'local':
            badge_cor = "info" 
            badge_texto = "ARQUIVO LOCAL"
            icone = "💾"
        else:
            badge_cor = "secondary"
            badge_texto = "GITHUB (DEMO)"
            icone = "🌐"
        
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem;">{icone}</span>
                <span style="background: {'#28a745' if badge_cor == 'success' else '#17a2b8' if badge_cor == 'info' else '#6c757d'}; 
                      color: white; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                    {badge_texto}
                </span>
            </div>
            <p style="margin: 0; font-size: 0.9rem; color: #495057;">
            <strong>Fonte atual:</strong> {fonte_atual.get('nome', 'N/A')}
            </p>
            <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #6c757d;">
            Atualizado: {get_horario_brasilia()}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Nenhuma fonte carregada. Use os controles abaixo.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================
    # SEÇÃO DE CONTROLES DE RECARREGAMENTO (ITEM 3)
    # ============================================
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("**🔄 Controles de Recarregamento**")
    
    # Botões de ação aprimorados
    col_rec1, col_rec2 = st.columns(2)
    
    with col_rec1:
        if st.button("🔄 Recarregar Fonte Atual", 
                   use_container_width=True,
                   type="primary",
                   help="Recarrega os dados da fonte atual",
                   key="btn_recarregar_fonte"):
            
            if fonte_atual:
                with st.spinner(f'Recarregando da {fonte_atual["tipo"]}...'):
                    try:
                        # Recarregar da fonte atual
                        df_recarregado, status, fonte_rec = carregar_da_fonte(fonte_atual)
                        
                        if df_recarregado is not None:
                            # Atualizar session state
                            st.session_state.df_original = df_recarregado
                            st.session_state.df_filtrado = df_recarregado.copy()
                            st.session_state.fonte_atual = fonte_rec
                            st.session_state.ultima_atualizacao = get_horario_brasilia()
                            
                            # Atualizar timestamp da última modificação
                            if fonte_rec['tipo'] == 'local' and 'caminho' in fonte_rec:
                                st.session_state.ultima_modificacao_fonte = os.path.getmtime(fonte_rec['caminho'])
                            
                            st.success(f"✅ {status}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {status}")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
            else:
                st.warning("⚠️ Nenhuma fonte disponível para recarregar.")
    
    with col_rec2:
        if st.button("🔄 Recarregar Tudo", 
                   use_container_width=True,
                   type="secondary",
                   help="Recarrega de todas as fontes disponíveis",
                   key="btn_recarregar_tudo"):
            
            with st.spinner('Buscando melhor fonte disponível...'):
                # Determinar melhor fonte
                melhor_fonte = determinar_melhor_fonte_disponivel()
                
                if melhor_fonte:
                    # Carregar da melhor fonte
                    df_novo, status, fonte_carregada = carregar_da_fonte(melhor_fonte)
                    
                    if df_novo is not None:
                        # Atualizar session state
                        st.session_state.df_original = df_novo
                        st.session_state.df_filtrado = df_novo.copy()
                        st.session_state.fonte_atual = fonte_carregada
                        st.session_state.ultima_atualizacao = get_horario_brasilia()
                        
                        # Limpar filtros
                        if 'filtros_aplicados' in st.session_state:
                            del st.session_state.filtros_aplicados
                        
                        st.success(f"✅ {status}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {status}")
                else:
                    st.error("❌ Nenhuma fonte disponível encontrada.")
    
    # Botão para recarregar de fonte específica
    st.markdown("**Selecionar Fonte:**")
    
    # Opções de fonte
    opcoes_fonte = []
    
    # Verificar disponibilidade de cada fonte
    if 'uploaded_file_name' in st.session_state and st.session_state.uploaded_file_name:
        opcoes_fonte.append(f"📤 Upload: {st.session_state.uploaded_file_name}")
    
    caminho_local = encontrar_arquivo_dados()
    if caminho_local:
        opcoes_fonte.append(f"💾 Local: {os.path.basename(caminho_local)}")
    
    # Sempre disponível (fallback)
    opcoes_fonte.append("🌐 GitHub (dados demo)")
    
    if opcoes_fonte:
        fonte_selecionada = st.selectbox(
            "Escolha a fonte para carregar:",
            options=opcoes_fonte,
            key="select_fonte_carregar",
            label_visibility="collapsed"
        )
        
        if st.button("📥 Carregar da Fonte Selecionada",
                   use_container_width=True,
                   key="btn_carregar_fonte_selecionada"):
            
            with st.spinner('Carregando da fonte selecionada...'):
                # Mapear seleção para fonte
                if "Upload:" in fonte_selecionada:
                    # Usar upload existente
                    if 'df_original' in st.session_state:
                        st.session_state.fonte_atual = {
                            'tipo': 'upload',
                            'nome': st.session_state.uploaded_file_name,
                            'prioridade': 1
                        }
                        st.success(f"✅ Usando upload: {st.session_state.uploaded_file_name}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Upload não encontrado na sessão.")
                
                elif "Local:" in fonte_selecionada and caminho_local:
                    # Carregar arquivo local
                    df_local, status, hash_conteudo = carregar_dados(caminho_arquivo=caminho_local)
                    
                    if df_local is not None:
                        st.session_state.df_original = df_local
                        st.session_state.df_filtrado = df_local.copy()
                        st.session_state.fonte_atual = {
                            'tipo': 'local',
                            'caminho': caminho_local,
                            'nome': os.path.basename(caminho_local),
                            'prioridade': 2
                        }
                        st.session_state.ultima_atualizacao = get_horario_brasilia()
                        st.session_state.ultima_modificacao_fonte = os.path.getmtime(caminho_local)
                        
                        st.success(f"✅ {status}")
                        time.sleep(1)
                        st.rerun()
                
                elif "GitHub" in fonte_selecionada:
                    # Carregar do GitHub
                    try:
                        response = requests.get(GITHUB_RAW_URL)
                        if response.status_code == 200:
                            temp_path = "temp_github_load.csv"
                            with open(temp_path, 'wb') as f:
                                f.write(response.content)
                            
                            df_github, status, hash_conteudo = carregar_dados(caminho_arquivo=temp_path)
                            os.remove(temp_path)
                            
                            if df_github is not None:
                                st.session_state.df_original = df_github
                                st.session_state.df_filtrado = df_github.copy()
                                st.session_state.fonte_atual = {
                                    'tipo': 'github',
                                    'url': GITHUB_RAW_URL,
                                    'nome': 'GitHub (demo)',
                                    'prioridade': 3
                                }
                                st.session_state.ultima_atualizacao = get_horario_brasilia()
                                
                                st.success(f"✅ {status}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {status}")
                        else:
                            st.error(f"❌ Erro ao acessar GitHub: {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Erro ao carregar do GitHub: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================
    # SEÇÃO DE UPLOAD (ITEM 1 - PRIORIDADE)
    # ============================================
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("**📤 Upload de Arquivo (Prioridade Máxima)**")
    
    uploaded_file = st.file_uploader(
        "Selecione um arquivo CSV para upload",
        type=['csv'],
        key="file_uploader_prioritario",
        help="Arquivos enviados têm prioridade máxima sobre outras fontes",
        label_visibility="collapsed"
    )
    
    # Se um arquivo foi enviado
    if uploaded_file is not None:
        # Verificar se é um arquivo diferente do atual
        current_hash = calcular_hash_arquivo(uploaded_file.getvalue())
        
        if ('file_hash' not in st.session_state or 
            current_hash != st.session_state.file_hash or
            uploaded_file.name != st.session_state.uploaded_file_name):
            
            with st.spinner('Processando arquivo de upload...'):
                # Salvar temporariamente
                temp_path = f"temp_upload_{uploaded_file.name}"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                # Carregar dados
                df_novo, status, hash_conteudo = carregar_dados(caminho_arquivo=temp_path)
                os.remove(temp_path)
                
                if df_novo is not None:
                    # Atualizar session state com prioridade
                    st.session_state.df_original = df_novo
                    st.session_state.df_filtrado = df_novo.copy()
                    st.session_state.arquivo_atual = uploaded_file.name
                    st.session_state.file_hash = hash_conteudo
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.session_state.ultima_atualizacao = get_horario_brasilia()
                    st.session_state.fonte_atual = {
                        'tipo': 'upload',
                        'nome': uploaded_file.name,
                        'prioridade': 1
                    }
                    
                    # Limpar filtros
                    if 'filtros_aplicados' in st.session_state:
                        del st.session_state.filtros_aplicados
                    
                    st.success(f"✅ {len(df_novo):,} registros carregados do upload!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {status}")
        else:
            st.info("ℹ️ Este arquivo já está carregado como fonte atual.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================
    # FILTROS APENAS SE HOUVER DADOS (MANTIDO)
    # ============================================
    if 'df_original' in st.session_state and st.session_state.df_original is not None:
        with st.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("**🔍 Filtros de Análise**")
            
            df = st.session_state.df_original.copy()
            
            # FILTRO POR ANO
            if 'Ano' in df.columns:
                anos_disponiveis = sorted(df['Ano'].dropna().unique().astype(int))
                if anos_disponiveis:
                    anos_opcoes = ['Todos os Anos'] + list(anos_disponiveis)
                    ano_selecionado = st.selectbox(
                        "📅 Ano",
                        options=anos_opcoes,
                        key="filtro_ano"
                    )
                    if ano_selecionado != 'Todos os Anos':
                        df = df[df['Ano'] == int(ano_selecionado)]
            
            # FILTRO POR MÊS
            if 'Mês' in df.columns:
                meses_disponiveis = sorted(df['Mês'].dropna().unique().astype(int))
                if meses_disponiveis:
                    meses_opcoes = ['Todos os Meses'] + [str(m) for m in meses_disponiveis]
                    mes_selecionado = st.selectbox(
                        "📆 Mês",
                        options=meses_opcoes,
                        key="filtro_mes"
                    )
                    if mes_selecionado != 'Todos os Meses':
                        df = df[df['Mês'] == int(mes_selecionado)]
            
            # FILTRO POR RESPONSÁVEL
            if 'Responsável_Formatado' in df.columns:
                responsaveis = ['Todos'] + sorted(df['Responsável_Formatado'].dropna().unique())
                responsavel_selecionado = st.selectbox(
                    "👤 Responsável",
                    options=responsaveis,
                    key="filtro_responsavel"
                )
                if responsavel_selecionado != 'Todos':
                    df = df[df['Responsável_Formatado'] == responsavel_selecionado]
            
            # BUSCA POR CHAMADO
            busca_chamado = st.text_input(
                "🔎 Buscar Chamado",
                placeholder="Digite número do chamado...",
                key="busca_chamado"
            )
            if busca_chamado:
                df = df[df['Chamado'].astype(str).str.contains(busca_chamado, na=False)]
            
            # FILTRO POR STATUS
            if 'Status' in df.columns:
                status_opcoes = ['Todos'] + sorted(df['Status'].dropna().unique())
                status_selecionado = st.selectbox(
                    "📊 Status",
                    options=status_opcoes,
                    key="filtro_status"
                )
                if status_selecionado != 'Todos':
                    df = df[df['Status'] == status_selecionado]
            
            # FILTRO POR TIPO
            if 'Tipo_Chamado' in df.columns:
                tipos = ['Todos'] + sorted(df['Tipo_Chamado'].dropna().unique())
                tipo_selecionado = st.selectbox(
                    "📝 Tipo de Chamado",
                    options=tipos,
                    key="filtro_tipo"
                )
                if tipo_selecionado != 'Todos':
                    df = df[df['Tipo_Chamado'] == tipo_selecionado]
            
            # FILTRO POR EMPRESA
            if 'Empresa' in df.columns:
                empresas = ['Todas'] + sorted(df['Empresa'].dropna().unique())
                empresa_selecionada = st.selectbox(
                    "🏢 Empresa",
                    options=empresas,
                    key="filtro_empresa"
                )
                if empresa_selecionada != 'Todas':
                    df = df[df['Empresa'] == empresa_selecionada]
            
            # FILTRO POR SRE
            if 'SRE' in df.columns:
                sres = ['Todos'] + sorted(df['SRE'].dropna().unique())
                sre_selecionado = st.selectbox(
                    "🔧 SRE Responsável",
                    options=sres,
                    key="filtro_sre"
                )
                if sre_selecionado != 'Todos':
                    df = df[df['SRE'] == sre_selecionado]
            
            # Atualizar dados filtrados
            st.session_state.df_filtrado = df
            
            st.markdown(f"**📈 Registros filtrados:** {len(df):,}")
            st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MONITORAMENTO AUTOMÁTICO (ITEM 4)
# ============================================

# Verificar se é hora de fazer polling
tempo_atual = time.time()
if 'ultima_verificacao_polling' in st.session_state:
    tempo_decorrido = tempo_atual - st.session_state.ultima_verificacao_polling
    
    if tempo_decorrido > POLLING_INTERVAL:
        # Atualizar timestamp
        st.session_state.ultima_verificacao_polling = tempo_atual
        
        # Verificar modificação do arquivo local
        if verificar_modificacao_arquivo_local():
            # Mostrar notificação no topo da página
            st.toast("⚠️ O arquivo local foi modificado externamente! Use o botão 'Recarregar Fonte Atual'.", icon="⚠️")

# ============================================
# CARREGAMENTO INICIAL AUTOMÁTICO
# ============================================
if 'df_original' not in st.session_state or st.session_state.df_original is None:
    # Determinar melhor fonte disponível
    melhor_fonte = determinar_melhor_fonte_disponivel()
    
    if melhor_fonte:
        # Mostrar status de carregamento
        loading_placeholder = st.empty()
        loading_placeholder.info(f"🔄 Carregando dados da fonte: {melhor_fonte['nome']}...")
        
        # Carregar dados
        df_carregado, status, fonte_carregada = carregar_da_fonte(melhor_fonte)
        
        if df_carregado is not None:
            # Atualizar session state
            st.session_state.df_original = df_carregado
            st.session_state.df_filtrado = df_carregado.copy()
            st.session_state.fonte_atual = fonte_carregada
            st.session_state.ultima_atualizacao = get_horario_brasilia()
            
            # Registrar timestamp de modificação se for arquivo local
            if fonte_carregada['tipo'] == 'local' and 'caminho' in fonte_carregada:
                st.session_state.ultima_modificacao_fonte = os.path.getmtime(fonte_carregada['caminho'])
            
            loading_placeholder.success(f"✅ {status}")
            time.sleep(1)
            st.rerun()
        else:
            loading_placeholder.error(f"❌ {status}")
    else:
        st.warning("⚠️ Nenhuma fonte de dados disponível. Faça upload de um arquivo CSV.")

# RESTANTE DO CÓDIGO PERMANECE IGUAL A PARTIR DAQUI...
# ============================================
# CONTEÚDO PRINCIPAL
# ============================================

# HEADER ATUALIZADO (removida a data completamente)
st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="color: white; margin: 0; font-size: 1.8rem; font-weight: 700;">📊 ESTEIRA ADMS</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 1rem;">
            Sistema de Análise de Chamados | SRE
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 0.2rem 0 0 0; font-size: 0.9rem;">
            EMS | EMR | ESS
            </p>
        </div>
        <div style="text-align: right;">
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
            Dashboard de Performance
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 0.2rem 0 0 0; font-size: 0.85rem;">
            v5.5 | Sistema de Performance SRE
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# EXIBIR DASHBOARD SE HOUVER DADOS
# ============================================
if st.session_state.df_original is not None:
    # O RESTANTE DO SEU CÓDIGO ORIGINAL CONTINUA AQUI...
    # (Todas as abas, gráficos, análises permanecem iguais)
    
    # Como exemplo, vou mostrar apenas a primeira parte que já estava no seu código:
    df = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_original
    
    # ============================================
    # INFORMAÇÕES DA BASE DE DADOS (SIMPLIFICADO)
    # ============================================
    st.markdown("## 📊 Informações da Base de Dados")
    
    if 'Criado' in df.columns and not df.empty:
        data_min = df['Criado'].min()
        data_max = df['Criado'].max()
        
        # Mostrar fonte atual no cabeçalho
        fonte_info = ""
        if 'fonte_atual' in st.session_state and st.session_state.fonte_atual:
            fonte = st.session_state.fonte_atual
            if fonte['tipo'] == 'upload':
                fonte_info = "📤 | "
            elif fonte['tipo'] == 'local':
                fonte_info = "💾 | "
            else:
                fonte_info = "🌐 | "
        
        st.markdown(f"""
        <div class="info-base">
            <p style="margin: 0; font-weight: 600;">{fonte_info}📅 Base atualizada em: {get_horario_brasilia()}</p>
            <p style="margin: 0.3rem 0 0 0; color: #6c757d;">
            Período coberto: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')} | 
            Total de registros: {len(df):,}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # O RESTANTE DO SEU CÓDIGO CONTINUA IGUAL...

else:
    # TELA INICIAL ATUALIZADA
    st.markdown("""
    <div style="text-align: center; padding: 4rem; background: #f8f9fa; border-radius: 10px; border: 2px dashed #dee2e6;">
        <h3 style="color: #495057;">📊 Esteira ADMS Dashboard</h3>
        <p style="color: #6c757d; margin-bottom: 2rem;">
            Sistema de análise e monitoramento de chamados - Setor SRE
        </p>
        <div style="margin-top: 2rem; padding: 2rem; background: white; border-radius: 8px; display: inline-block;">
            <h4 style="color: #1e3799;">📋 Para começar:</h4>
            <p>1. <strong>Use a seção "Upload de Arquivo"</strong> na barra lateral (prioridade máxima)</p>
            <p>2. <strong>Coloque um arquivo CSV local</strong> no diretório do app</p>
            <p>3. <strong>O sistema carregará automaticamente</strong> do GitHub como fallback</p>
            <p>4. <strong>Use "Controles de Recarregamento"</strong> para gerenciar fontes</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# RODAPÉ ATUALIZADO
# ============================================
st.markdown("---")

# Obter horário da última atualização
ultima_atualizacao = st.session_state.get('ultima_atualizacao', get_horario_brasilia())

# Mostrar fonte atual no rodapé
fonte_rodape = ""
if 'fonte_atual' in st.session_state and st.session_state.fonte_atual:
    fonte = st.session_state.fonte_atual
    if fonte['tipo'] == 'upload':
        fonte_rodape = f" | Fonte: 📤 Upload"
    elif fonte['tipo'] == 'local':
        fonte_rodape = f" | Fonte: 💾 Local"
    else:
        fonte_rodape = f" | Fonte: 🌐 GitHub"

st.markdown(f"""
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
        Versão 5.5 | Sistema de Performance SRE | Última atualização: {ultima_atualizacao} (Brasília){fonte_rodape}
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
