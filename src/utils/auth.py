"""
Sistema de Autenticação Multi-Cliente
Gerencia login e acesso às planilhas específicas de cada cliente
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import hashlib
import hmac

# Configurações
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

class AuthManager:
    """Gerenciador de autenticação multi-cliente"""
    
    def __init__(self):
        """Inicializa o gerenciador de autenticação"""
        self.master_sheet_id = st.secrets.get("MASTER_SHEET_ID", "")
        self.creds = None
        self.client = None
        self._init_google_auth()
    
    def _init_google_auth(self):
        """Inicializa autenticação com Google Sheets"""
        try:
            if 'GOOGLE_CREDENTIALS' in st.secrets:
                creds_dict = dict(st.secrets['GOOGLE_CREDENTIALS'])
                self.creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
                self.client = gspread.authorize(self.creds)
            else:
                st.error("❌ Credenciais do Google não configuradas")
        except Exception as e:
            st.error(f"❌ Erro ao inicializar autenticação: {e}")
    
    def _hash_token(self, token: str) -> str:
        """Cria hash seguro do token para comparação"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def load_clients_database(self) -> pd.DataFrame:
        """Carrega base de dados de clientes da planilha mestre"""
        try:
            if not self.client:
                return pd.DataFrame()
            
            # Abrir planilha mestre
            sheet = self.client.open_by_key(self.master_sheet_id)
            worksheet = sheet.get_worksheet(0)  # Primeira aba
            
            # Carregar dados
            data = worksheet.get_all_values()
            if len(data) < 2:
                return pd.DataFrame()
            
            headers = data[0]
            rows = data[1:]
            
            df = pd.DataFrame(rows, columns=headers)
            
            # Filtrar apenas clientes ativos
            if 'ativo' in df.columns:
                df = df[df['ativo'].str.upper() == 'TRUE']
            
            return df
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar base de clientes: {e}")
            return pd.DataFrame()
    
    def authenticate(self, client_id: str, token: str) -> dict:
        """
        Autentica cliente com ID e token
        
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'client_data': dict ou None
            }
        """
        try:
            # Carregar base de clientes
            clients_df = self.load_clients_database()
            
            if clients_df.empty:
                return {
                    'success': False,
                    'message': 'Erro ao acessar base de clientes',
                    'client_data': None
                }
            
            # Buscar cliente pelo ID
            client_match = clients_df[clients_df['client_id'] == client_id]
            
            if client_match.empty:
                return {
                    'success': False,
                    'message': 'ID de cliente não encontrado',
                    'client_data': None
                }
            
            client_row = client_match.iloc[0]
            
            # Verificar token (comparação segura)
            stored_token = client_row.get('token', '')
            if not hmac.compare_digest(token, stored_token):
                return {
                    'success': False,
                    'message': 'Token inválido',
                    'client_data': None
                }
            
            # Autenticação bem-sucedida
            client_data = {
                'client_id': client_row['client_id'],
                'client_name': client_row['client_name'],
                'planilha_id': client_row['planilha_id'],
                'created_at': client_row.get('created_at', ''),
                'authenticated_at': datetime.now().isoformat()
            }
            
            # Registrar login (opcional)
            self._log_authentication(client_id, success=True)
            
            return {
                'success': True,
                'message': 'Login realizado com sucesso',
                'client_data': client_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro no processo de autenticação: {str(e)}',
                'client_data': None
            }
    
    def _log_authentication(self, client_id: str, success: bool):
        """Registra tentativa de autenticação (opcional)"""
        try:
            # Pode ser implementado para auditoria
            # Por exemplo, salvar em uma aba de logs
            pass
        except:
            pass  # Não bloquear login se log falhar
    
    def validate_session(self) -> bool:
        """Valida se a sessão atual está autenticada e válida"""
        if not st.session_state.get('authenticated', False):
            return False
        
        if 'client_data' not in st.session_state:
            return False
        
        # Pode adicionar validações adicionais como timeout
        # Por exemplo, verificar se não passou de 8 horas
        
        return True
    
    def get_client_info(self) -> dict:
        """Retorna informações do cliente autenticado"""
        if self.validate_session():
            return st.session_state.get('client_data', {})
        return {}

def check_authentication():
    """Função helper para verificar autenticação em qualquer página"""
    auth_manager = AuthManager()
    
    if not auth_manager.validate_session():
        st.error("❌ Sessão expirada ou não autenticada")
        
        # Limpar session state
        for key in ["authenticated", "client_data"]:
            if key in st.session_state:
                del st.session_state[key]
        
        # Botão para voltar ao login
        if st.button("🔐 Fazer Login"):
            st.rerun()
        
        return False
    
    return True

def get_current_client_id() -> str:
    """Retorna ID do cliente atual"""
    if 'client_data' in st.session_state:
        return st.session_state.client_data.get('client_id', '')
    return ''

def get_current_client_name() -> str:
    """Retorna nome do cliente atual"""
    if 'client_data' in st.session_state:
        return st.session_state.client_data.get('client_name', '')
    return ''

def get_current_sheet_id() -> str:
    """Retorna ID da planilha do cliente atual"""
    if 'client_data' in st.session_state:
        return st.session_state.client_data.get('planilha_id', '')
    return ''