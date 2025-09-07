"""
Coletor de Dados do Dashboard
Responsável por buscar dados das planilhas Google Sheets
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    """Coletor principal de dados das planilhas"""
    
    def __init__(self, sheet_id: str):
        """
        Inicializa o coletor
        
        Args:
            sheet_id: 1b7CQ3TjbhLsYAKxyaWR7_GjmMSNv1ixmBHybEG2k_H0
        """
        self.sheet_id = sheet_id
        self.client = None
        self.sheet = None
        self._init_google_client()
    
    def _init_google_client(self):
        """Inicializa cliente Google Sheets"""
        try:
            SCOPES = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            if 'GOOGLE_CREDENTIALS' in st.secrets:
                creds_dict = dict(st.secrets['GOOGLE_CREDENTIALS'])
                creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
                self.client = gspread.authorize(creds)
                logger.info("Cliente Google Sheets inicializado com sucesso")
            else:
                logger.error("Credenciais Google não encontradas")
                st.error("❌ Credenciais do Google não configuradas")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente: {e}")
            st.error(f"❌ Erro na autenticação Google: {e}")
    
    @st.cache_data(ttl=300)  # Cache por 5 minutos
    def load_data(_self) -> pd.DataFrame:
        """
        Carrega dados da planilha do cliente
        
        Returns:
            DataFrame com os dados ou DataFrame vazio em caso de erro
        """
        try:
            if not _self.client:
                return pd.DataFrame()
            
            # Abrir planilha
            sheet = _self.client.open_by_key(_self.sheet_id)
            
            # Tentar múltiplas abas em ordem de preferência
            worksheet_names = ['Contatos', 'Contacts', 'Conversas', 'Conversations', 'Sheet1']
            worksheet = None
            
            for name in worksheet_names:
                try:
                    worksheet = sheet.worksheet(name)
                    logger.info(f"Aba '{name}' encontrada")
                    break
                except:
                    continue
            
            if not worksheet:
                logger.warning("Nenhuma aba de dados encontrada")
                st.warning("⚠️ Nenhuma aba de dados encontrada na planilha")
                return pd.DataFrame()
            
            # Carregar todos os dados
            all_values = worksheet.get_all_values()
            
            if not all_values or len(all_values) < 2:
                logger.warning("Planilha sem dados suficientes")
                return pd.DataFrame()
            
            # Processar dados
            headers = all_values[0]
            data_rows = all_values[1:]
            
            # Filtrar linhas completamente vazias
            data_rows = [row for row in data_rows if any(cell.strip() for cell in row if cell)]
            
            if not data_rows:
                logger.warning("Nenhuma linha de dados válida encontrada")
                return pd.DataFrame()
            
            # Criar DataFrame
            max_cols = len(headers)
            processed_rows = []
            
            for row in data_rows:
                # Garantir que todas as linhas tenham o mesmo número de colunas
                while len(row) < max_cols:
                    row.append('')
                row = row[:max_cols]  # Cortar se tiver colunas extras
                processed_rows.append(row)
            
            df = pd.DataFrame(processed_rows, columns=headers)
            
            # Log de sucesso
            logger.info(f"Dados carregados com sucesso: {len(df)} registros, {len(df.columns)} colunas")
            
            # Verificar colunas importantes para lead tracking
            required_cols = ['lead_stage', 'lead_qualified_date', 'lead_converted_date']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.info(f"ℹ️ Colunas de lead tracking ausentes: {', '.join(missing_cols)}")
                st.info("💡 Adicione essas colunas na planilha para análise completa de funil")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            st.error(f"❌ Erro ao carregar dados: {e}")
            return pd.DataFrame()
    
    def get_sheet_info(self) -> dict:
        """
        Retorna informações sobre a planilha
        
        Returns:
            Dict com informações da planilha
        """
        try:
            if not self.client:
                return {}
            
            sheet = self.client.open_by_key(self.sheet_id)
            
            info = {
                'title': sheet.title,
                'id': sheet.id,
                'url': sheet.url,
                'worksheets': [ws.title for ws in sheet.worksheets()],
                'last_updated': datetime.now().isoformat()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Erro ao obter informações da planilha: {e}")
            return {}
    
    def validate_data_structure(self, df: pd.DataFrame) -> dict:
        """
        Valida estrutura dos dados
        
        Args:
            df: DataFrame para validar
            
        Returns:
            Dict com resultado da validação
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Verificar se DataFrame está vazio
        if df.empty:
            validation['is_valid'] = False
            validation['errors'].append("DataFrame está vazio")
            return validation
        
        # Colunas essenciais
        essential_cols = ['conversation_id', 'created_at', 'channel']
        missing_essential = [col for col in essential_cols if col not in df.columns]
        
        if missing_essential:
            validation['is_valid'] = False
            validation['errors'].append(f"Colunas essenciais ausentes: {', '.join(missing_essential)}")
        
        # Colunas importantes (não essenciais mas úteis)
        important_cols = ['status', 'lead_stage', 'satisfaction_score', 'message_count']
        missing_important = [col for col in important_cols if col not in df.columns]
        
        if missing_important:
            validation['warnings'].append(f"Colunas importantes ausentes: {', '.join(missing_important)}")
        
        # Informações gerais
        validation['info'].append(f"Total de registros: {len(df)}")
        validation['info'].append(f"Total de colunas: {len(df.columns)}")
        
        # Verificar tipos de dados em colunas importantes
        if 'created_at' in df.columns:
            try:
                pd.to_datetime(df['created_at'].head())
                validation['info'].append("Formato de data válido em 'created_at'")
            except:
                validation['warnings'].append("Formato de data inválido em 'created_at'")
        
        return validation

class CacheManager:
    """Gerenciador de cache para otimizar performance"""
    
    @staticmethod
    def get_cached_data(key: str, ttl: int = 300):
        """Obtém dados do cache se disponível"""
        cache_key = f"cache_{key}"
        
        if cache_key in st.session_state:
            cached_data, timestamp = st.session_state[cache_key]
            
            # Verificar se ainda está válido
            if (datetime.now() - timestamp).seconds < ttl:
                return cached_data
        
        return None
    
    @staticmethod
    def set_cached_data(key: str, data):
        """Armazena dados no cache"""
        cache_key = f"cache_{key}"
        st.session_state[cache_key] = (data, datetime.now())
    
    @staticmethod
    def clear_cache(key: str = None):
        """Limpa cache específico ou todo o cache"""
        if key:
            cache_key = f"cache_{key}"
            if cache_key in st.session_state:
                del st.session_state[cache_key]
        else:
            # Limpar todo o cache
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith("cache_")]
            for k in keys_to_delete:
                del st.session_state[k]