"""
Interface de upload otimizada
"""
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from data_manager import DataManager

class UploadInterface:
    """Gerencia a interface de upload de arquivos"""
    
    def __init__(self):
        self.data_manager = DataManager()
        
    def show_upload_section(self):
        """Mostra seção de upload otimizada"""
        st.markdown("---")
        
        # Container principal de upload
        with st.container():
            col_title, col_actions = st.columns([3, 1])
            
            with col_title:
                st.markdown("### 📁 Carregamento de Dados")
                st.caption("Faça upload de um arquivo CSV ou Excel para iniciar a análise")
            
            with col_actions:
                # Botão para limpar tudo
                if st.button("🔄 Limpar Tudo", 
                           use_container_width=True,
                           type="secondary",
                           help="Limpa todos os dados carregados"):
                    self._clear_all_data()
                    st.rerun()
        
        # Métodos de carregamento
        tab_local, tab_upload, tab_history = st.tabs([
            "📂 Local", 
            "⬆️ Upload", 
            "📊 Histórico"
        ])
        
        with tab_local:
            self._show_local_file_loader()
        
        with tab_upload:
            self._show_file_uploader()
        
        with tab_history:
            self._show_file_history()
    
    def _show_local_file_loader(self):
        """Carrega arquivos locais de forma otimizada"""
        st.markdown("#### 📂 Arquivos Locais")
        
        # Caminhos pré-configurados
        file_paths = [
            "esteira_demandas.csv",
            "data/esteira_demandas.csv",
            "dados/demandas.csv",
            "base_dados.csv"
        ]
        
        # Verificar quais arquivos existem
        existing_files = []
        for path in file_paths:
            import os
            if os.path.exists(path):
                file_info = self.data_manager.get_file_info(path)
                if file_info:
                    existing_files.append((path, file_info))
        
        if existing_files:
            for path, info in existing_files:
                col_file, col_size, col_action = st.columns([3, 1, 1])
                
                with col_file:
                    st.markdown(f"**{info['filename']}**")
                    st.caption(f"Atualizado: {info['last_modified'].strftime('%d/%m/%Y %H:%M')}")
                
                with col_size:
                    st.markdown(f"**{info['size_kb']:.1f} KB**")
                
                with col_action:
                    if st.button("📥 Carregar", key=f"load_{path}", use_container_width=True):
                        with st.spinner(f"Carregando {info['filename']}..."):
                            self._load_local_file(path)
            
            st.markdown("---")
        
        # Upload manual de novo arquivo
        st.markdown("#### 📤 Enviar novo arquivo local")
        uploaded_file = st.file_uploader(
            "Selecione um arquivo CSV ou Excel",
            type=['csv', 'xlsx', 'xls'],
            key="local_uploader",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            if st.button("✅ Processar Arquivo", type="primary", use_container_width=True):
                with st.spinner("Processando arquivo..."):
                    self._process_uploaded_file(uploaded_file)
    
    def _show_file_uploader(self):
        """Interface principal de upload"""
        st.markdown("#### ⬆️ Upload Direto")
        
        # Área de drop
        uploaded_file = st.file_uploader(
            "Arraste e solte ou clique para selecionar",
            type=['csv', 'xlsx', 'xls'],
            key="main_uploader",
            help="Formatos suportados: CSV, Excel (.xlsx, .xls)",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            # Preview rápido
            col_preview, col_info = st.columns([2, 1])
            
            with col_preview:
                st.success(f"✅ Arquivo pronto: **{uploaded_file.name}**")
                
                # Pré-visualização rápida
                try:
                    preview_df = pd.read_csv(uploaded_file, nrows=5)
                    with st.expander("📋 Pré-visualização (5 primeiras linhas)"):
                        st.dataframe(preview_df, use_container_width=True)
                except:
                    pass
            
            with col_info:
                st.metric("Tamanho", f"{uploaded_file.size / 1024:.1f} KB")
                st.metric("Tipo", uploaded_file.type)
            
            # Botão de processamento
            if st.button("🚀 Processar e Carregar Dados", 
                        type="primary",
                        use_container_width=True):
                with st.spinner("Processando dados..."):
                    self._process_uploaded_file(uploaded_file)
    
    def _show_file_history(self):
        """Mostra histórico de arquivos carregados"""
        if 'loaded_files_history' not in st.session_state:
            st.session_state.loaded_files_history = []
        
        st.markdown("#### 📊 Histórico de Arquivos")
        
        if st.session_state.loaded_files_history:
            for i, file_info in enumerate(reversed(st.session_state.loaded_files_history[-5:])):
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{file_info['name']}**")
                        st.caption(f"Carregado: {file_info['timestamp']}")
                    
                    with col2:
                        st.caption(f"Registros: {file_info['records']:,}")
                        st.caption(f"Hash: {file_info['hash'][:8]}...")
                    
                    with col3:
                        if st.button("↻ Recarregar", key=f"reload_{i}", use_container_width=True):
                            # Lógica para recarregar
                            pass
        else:
            st.info("Nenhum arquivo carregado recentemente.")
    
    def _load_local_file(self, filepath):
        """Carrega arquivo local"""
        try:
            with open(filepath, 'rb') as f:
                file_content = f.read()
                filename = os.path.basename(filepath)
                
                if filepath.endswith('.csv'):
                    df, message = self.data_manager.load_csv_data(file_content, filename)
                elif filepath.endswith(('.xlsx', '.xls')):
                    df, message = self.data_manager.load_excel_data(file_content, filename)
                else:
                    st.error("Formato de arquivo não suportado")
                    return
            
            if df is not None:
                # Calcular hash
                file_hash = self.data_manager.calculate_file_hash(file_content)
                
                # Atualizar session state
                st.session_state.df_original = df
                st.session_state.df_filtrado = df.copy()
                st.session_state.file_hash = file_hash
                st.session_state.uploaded_file_name = filename
                st.session_state.arquivo_atual = filepath
                st.session_state.ultima_atualizacao = self._get_current_time()
                
                # Adicionar ao histórico
                self._add_to_history(filename, len(df), file_hash)
                
                st.success(f"✅ {message} - {len(df):,} registros carregados")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {message}")
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
    
    def _process_uploaded_file(self, uploaded_file):
        """Processa arquivo enviado"""
        try:
            file_content = uploaded_file.getvalue()
            filename = uploaded_file.name
            
            # Verificar se é o mesmo arquivo
            current_hash = self.data_manager.calculate_file_hash(file_content)
            
            if ('file_hash' in st.session_state and 
                current_hash == st.session_state.file_hash):
                st.info("ℹ️ Este arquivo já está carregado.")
                return
            
            # Processar conforme o tipo
            if filename.endswith('.csv'):
                df, message = self.data_manager.load_csv_data(file_content, filename)
            elif filename.endswith(('.xlsx', '.xls')):
                df, message = self.data_manager.load_excel_data(file_content, filename)
            else:
                st.error("❌ Formato de arquivo não suportado")
                return
            
            if df is not None:
                # Atualizar session state
                st.session_state.df_original = df
                st.session_state.df_filtrado = df.copy()
                st.session_state.file_hash = current_hash
                st.session_state.uploaded_file_name = filename
                st.session_state.arquivo_atual = filename
                st.session_state.ultima_atualizacao = self._get_current_time()
                
                # Adicionar ao histórico
                self._add_to_history(filename, len(df), current_hash)
                
                # Limpar cache se necessário
                if 'df_original' in st.session_state:
                    del st.session_state.df_original
                
                st.success(f"✅ {message} - {len(df):,} registros carregados")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {message}")
                
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
    
    def _add_to_history(self, filename, records, file_hash):
        """Adiciona arquivo ao histórico"""
        if 'loaded_files_history' not in st.session_state:
            st.session_state.loaded_files_history = []
        
        history_entry = {
            'name': filename,
            'records': records,
            'hash': file_hash,
            'timestamp': self._get_current_time()
        }
        
        st.session_state.loaded_files_history.append(history_entry)
        
        # Manter apenas últimos 10 registros
        if len(st.session_state.loaded_files_history) > 10:
            st.session_state.loaded_files_history = st.session_state.loaded_files_history[-10:]
    
    def _get_current_time(self):
        """Retorna hora atual formatada"""
        from datetime import datetime
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    def _clear_all_data(self):
        """Limpa todos os dados"""
        keys_to_clear = [
            'df_original', 'df_filtrado', 'arquivo_atual',
            'ultima_modificacao', 'file_hash', 'uploaded_file_name',
            'ultima_atualizacao', 'loaded_files_history'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Limpar cache
        st.cache_data.clear()
