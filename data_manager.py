"""
Módulo gerenciador de dados - Simplificado e otimizado
"""
import pandas as pd
import streamlit as st
import hashlib
import os
from datetime import datetime
from pytz import timezone
import io

class DataManager:
    """Gerencia o carregamento e atualização de dados"""
    
    def __init__(self):
        self.data_version = "1.0"
        self.supported_formats = ['.csv', '.xlsx', '.parquet']
    
    def calculate_file_hash(self, file_content):
        """Calcula hash do arquivo para verificar mudanças"""
        if isinstance(file_content, bytes):
            return hashlib.md5(file_content).hexdigest()
        return hashlib.md5(file_content.encode('utf-8')).hexdigest()
    
    def format_responsible_name(self, nome):
        """Formata nomes de responsáveis de forma consistente"""
        if pd.isna(nome):
            return "Não informado"
        
        nome_str = str(nome).strip()
        
        # Se for e-mail, extrair nome
        if '@' in nome_str:
            partes = nome_str.split('@')[0]
            for separador in ['.', '_', '-']:
                partes = partes.replace(separador, ' ')
            
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
        
        return nome_str.title()
    
    def load_csv_data(self, file_content, filename=None):
        """Carrega e processa dados CSV de forma eficiente"""
        try:
            # Determinar encoding
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    content_str = file_content.decode(encoding)
                    break
                except:
                    continue
            else:
                content_str = file_content.decode('utf-8-sig', errors='ignore')
            
            # Ler CSV
            df = pd.read_csv(io.StringIO(content_str), quotechar='"', on_bad_lines='skip')
            
            # Processamento básico
            df = self._process_dataframe(df)
            
            return df, "✅ Dados carregados com sucesso"
            
        except Exception as e:
            return None, f"❌ Erro ao carregar CSV: {str(e)}"
    
    def load_excel_data(self, file_content, filename=None):
        """Carrega e processa dados Excel"""
        try:
            # Salvar temporariamente para pandas
            temp_path = f"temp_{filename if filename else 'data'}.xlsx"
            with open(temp_path, 'wb') as f:
                f.write(file_content)
            
            # Ler Excel
            df = pd.read_excel(temp_path, engine='openpyxl')
            
            # Remover arquivo temporário
            os.remove(temp_path)
            
            # Processamento básico
            df = self._process_dataframe(df)
            
            return df, "✅ Dados carregados com sucesso"
            
        except Exception as e:
            return None, f"❌ Erro ao carregar Excel: {str(e)}"
    
    def _process_dataframe(self, df):
        """Processamento básico do dataframe"""
        # Renomear colunas para padrão
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
            df['Responsável_Formatado'] = df['Responsável'].apply(self.format_responsible_name)
        
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
            df['Nome_Mês'] = df['Criado'].dt.month.map({
                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
                5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
                9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
            })
        
        # Converter revisões
        if 'Revisões' in df.columns:
            df['Revisões'] = pd.to_numeric(df['Revisões'], errors='coerce').fillna(0).astype(int)
        
        return df
    
    def get_file_info(self, filepath):
        """Obtém informações do arquivo"""
        if not os.path.exists(filepath):
            return None
        
        stats = os.stat(filepath)
        return {
            'filename': os.path.basename(filepath),
            'size_kb': stats.st_size / 1024,
            'last_modified': datetime.fromtimestamp(stats.st_mtime),
            'created': datetime.fromtimestamp(stats.st_ctime)
        }
