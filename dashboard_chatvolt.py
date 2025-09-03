"""
DASHBOARD REACH IA - ANÁLISE INTELIGENTE DE CONVERSAS
Sistema avançado de métricas com IA para otimização de atendimento
Deploy: Streamlit Cloud - Versão Premium Design
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gspread
from google.oauth2.service_account import Credentials
import requests
import json
import time
from datetime import datetime, timedelta
import pytz
import numpy as np

# Configuração da página com tema premium
st.set_page_config(
    page_title="Dashboard Reach IA",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações da API Chatvolt
CHATVOLT_API_BASE = "https://api.chatvolt.ai"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# ID da planilha Google Sheets
PLANILHA_ID = "1Ji8hgGiQanGKMqblxRzkA_E_sLoI6AnpapmU72nXHsA"

def apply_premium_styling():
    """Aplica estilo premium com tema azul escuro e degradê"""
    st.markdown("""
    <style>
    /* ============= TEMA PRINCIPAL REACH IA ============= */
    
    /* Background principal com degradê azul escuro */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a2332 25%, #2d3748 50%, #1a2332 75%, #0f1419 100%);
        background-attachment: fixed;
    }
    
    /* Container principal */
    .main .block-container {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        margin-top: 1rem;
    }
    
    /* ============= HEADER REACH IA ============= */
    
    /* Título principal */
    h1 {
        background: linear-gradient(135deg, #64b5f6 0%, #1e88e5 50%, #0d47a1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
        font-size: 3rem !important;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(100, 181, 246, 0.3);
    }
    
    /* Subtítulo */
    .subtitle {
        color: #90caf9;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 300;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    /* ============= CARDS PREMIUM ============= */
    
    /* Métricas cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(100, 181, 246, 0.1) 0%, rgba(30, 136, 229, 0.1) 100%);
        border: 1px solid rgba(100, 181, 246, 0.2);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(100, 181, 246, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 45px rgba(100, 181, 246, 0.2);
        border-color: rgba(100, 181, 246, 0.4);
    }
    
    /* Valores das métricas */
    [data-testid="metric-container"] > div > div > div > div {
        color: #e3f2fd !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(227, 242, 253, 0.3);
    }
    
    /* Labels das métricas */
    [data-testid="metric-container"] > div > div > div:first-child {
        color: #90caf9 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* ============= SIDEBAR PREMIUM ============= */
    
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(15, 20, 25, 0.95) 0%, rgba(26, 35, 50, 0.95) 100%);
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(100, 181, 246, 0.2);
    }
    
    /* Título da sidebar */
    .css-1d391kg .css-10trblm {
        color: #64b5f6;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* ============= COMPONENTES INTERATIVOS ============= */
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #1e88e5 0%, #1976d2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(30, 136, 229, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(30, 136, 229, 0.4);
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: rgba(100, 181, 246, 0.1);
        border: 1px solid rgba(100, 181, 246, 0.3);
        border-radius: 8px;
        color: #e3f2fd;
    }
    
    /* Date input */
    .stDateInput > div > div {
        background: rgba(100, 181, 246, 0.1);
        border: 1px solid rgba(100, 181, 246, 0.3);
        border-radius: 8px;
        color: #e3f2fd;
    }
    
    /* Checkbox */
    .stCheckbox > label {
        color: #90caf9 !important;
        font-weight: 500;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #90caf9 !important;
        font-weight: 500;
    }
    
    /* ============= ABAS ============= */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(100, 181, 246, 0.05);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(100, 181, 246, 0.1);
        border-radius: 8px;
        color: #90caf9;
        font-weight: 600;
        border: 1px solid rgba(100, 181, 246, 0.2);
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #1e88e5 0%, #1976d2 100%);
        color: white;
        border-color: #1976d2;
        box-shadow: 0 4px 15px rgba(30, 136, 229, 0.3);
    }
    
    /* ============= GRÁFICOS ============= */
    
    /* Container dos gráficos */
    .js-plotly-plot {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 15px;
        border: 1px solid rgba(100, 181, 246, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* ============= DATAFRAME ============= */
    
    .stDataFrame {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
        border: 1px solid rgba(100, 181, 246, 0.2);
        overflow: hidden;
    }
    
    .stDataFrame table {
        background: transparent !important;
        color: #e3f2fd !important;
    }
    
    .stDataFrame th {
        background: rgba(100, 181, 246, 0.2) !important;
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .stDataFrame td {
        border-color: rgba(100, 181, 246, 0.1) !important;
    }
    
    /* ============= ALERTS E MENSAGENS ============= */
    
    .stAlert {
        background: rgba(100, 181, 246, 0.1);
        border: 1px solid rgba(100, 181, 246, 0.3);
        border-radius: 10px;
        color: #e3f2fd;
    }
    
    .stSuccess {
        background: rgba(76, 175, 80, 0.1);
        border: 1px solid rgba(76, 175, 80, 0.3);
        color: #c8e6c9;
    }
    
    .stError {
        background: rgba(244, 67, 54, 0.1);
        border: 1px solid rgba(244, 67, 54, 0.3);
        color: #ffcdd2;
    }
    
    .stWarning {
        background: rgba(255, 152, 0, 0.1);
        border: 1px solid rgba(255, 152, 0, 0.3);
        color: #ffe0b2;
    }
    
    /* ============= TEXTOS GERAIS ============= */
    
    .css-10trblm {
        color: #e3f2fd;
    }
    
    .markdown-text-container {
        color: #b3e5fc;
    }
    
    /* ============= FOOTER ============= */
    
    .footer {
        background: linear-gradient(135deg, rgba(100, 181, 246, 0.1) 0%, rgba(30, 136, 229, 0.1) 100%);
        border: 1px solid rgba(100, 181, 246, 0.2);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 2rem;
        text-align: center;
        color: #90caf9;
        font-size: 0.9rem;
    }
    
    /* ============= SPINNER LOADING ============= */
    
    .stSpinner {
        color: #64b5f6 !important;
    }
    
    /* ============= RESPONSIVIDADE ============= */
    
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem !important;
        }
        
        .main .block-container {
            padding: 1rem;
        }
        
        [data-testid="metric-container"] {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def safe_get_column(df, column_name, default_value=None):
    """Retorna coluna do DataFrame ou valor padrão se não existir"""
    if column_name in df.columns:
        return df[column_name]
    else:
        if default_value is None:
            if df.empty:
                return pd.Series(dtype='object')
            return pd.Series([None] * len(df))
        return pd.Series([default_value] * len(df))

def ensure_required_columns(df):
    """Garante que DataFrame tenha todas as colunas necessárias"""
    required_columns = {
        'conversation_id': '',
        'created_at': pd.NaT,
        'updated_at': pd.NaT,
        'status': 'UNKNOWN',
        'priority': 'MEDIUM',
        'channel': 'unknown',
        'visitor_id': '',
        'agent_id': '',
        'frustration_level': 0,
        'first_response_time': 0,
        'resolution_time': 0,
        'message_count': 0,
        'satisfaction_score': 0,
        'resolved': False,
        'escalated_to_human': False,
        'contact_name': '',
        'contact_email': ''
    }
    
    for col, default_val in required_columns.items():
        if col not in df.columns:
            df[col] = default_val
    
    return df

class ChatvoltDataCollector:
    """Classe para coleta de dados da API Chatvolt"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.base_url = CHATVOLT_API_BASE

@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_data_from_sheets():
    """Carrega dados das conversas da planilha Google - VERSÃO PREMIUM"""
    try:
        # Verificar se secrets existem
        if 'GOOGLE_CREDENTIALS' not in st.secrets:
            st.error("🔐 Credenciais do Google não configuradas")
            return pd.DataFrame()
        
        # Configurar credenciais
        creds_dict = dict(st.secrets['GOOGLE_CREDENTIALS'])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # Conectar com a planilha
        try:
            sheet = client.open_by_key(PLANILHA_ID)
        except Exception as e:
            st.error(f"❌ Erro ao abrir planilha: {e}")
            return pd.DataFrame()
        
        # Buscar aba de conversas
        worksheet_names = ['Conversas', 'Conversations', 'Atendimentos', 'Sheet1']
        worksheet = None
        
        for name in worksheet_names:
            try:
                worksheet = sheet.worksheet(name)
                st.success(f"✅ Conectado à aba: **{name}**")
                break
            except:
                continue
        
        if not worksheet:
            st.error("❌ Nenhuma aba encontrada na planilha")
            return pd.DataFrame()
        
        # Coletar dados
        try:
            all_values = worksheet.get_all_values()
        except Exception as e:
            st.error(f"❌ Erro ao ler dados da planilha: {e}")
            return pd.DataFrame()
        
        if not all_values:
            st.warning("⚠️ Planilha completamente vazia")
            return pd.DataFrame()
        
        if len(all_values) < 2:
            st.warning("⚠️ Planilha só tem cabeçalhos, sem dados")
            return pd.DataFrame()
        
        headers = all_values[0]
        data_rows = all_values[1:]
        
        # Filtrar linhas completamente vazias
        data_rows = [row for row in data_rows if any(cell.strip() for cell in row if cell)]
        
        if not data_rows:
            st.warning("⚠️ Nenhuma linha de dados encontrada")
            return pd.DataFrame()
        
        # Criar DataFrame
        max_cols = len(headers)
        processed_rows = []
        
        for row in data_rows:
            # Garantir que a linha tenha o mesmo número de colunas
            while len(row) < max_cols:
                row.append('')
            row = row[:max_cols]  # Truncar se tiver colunas extras
            processed_rows.append(row)
        
        df = pd.DataFrame(processed_rows, columns=headers)
        
        st.success(f"🚀 **{len(df)} registros** carregados com sucesso")
        
        # Processar dados
        return process_chatvolt_data(df)
        
    except Exception as e:
        st.error(f"❌ Erro geral ao carregar dados: {e}")
        return pd.DataFrame()

def process_chatvolt_data(df):
    """Processa e limpa dados do Chatvolt - VERSÃO PREMIUM"""
    if df.empty:
        return df
    
    # Garantir colunas obrigatórias
    df = ensure_required_columns(df)
    
    # Processar timestamps de forma defensiva
    for time_col in ['created_at', 'updated_at']:
        if time_col in df.columns:
            try:
                # Tentar diferentes formatos de data
                df[time_col] = pd.to_datetime(df[time_col], format='%d/%m/%Y %H:%M:%S', errors='coerce')
                if df[time_col].isna().all():
                    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
                
                # Se ainda estão NaT, usar data atual
                if df[time_col].isna().all():
                    df[time_col] = datetime.now()
            except:
                df[time_col] = datetime.now()
    
    # Processar campos numéricos de forma segura
    numeric_fields = ['frustration_level', 'first_response_time', 'resolution_time',
                     'message_count', 'satisfaction_score']
    
    for field in numeric_fields:
        if field in df.columns:
            try:
                df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
            except:
                df[field] = 0
    
    # Processar campos booleanos de forma segura
    bool_fields = ['resolved', 'escalated_to_human']
    for field in bool_fields:
        if field in df.columns:
            try:
                df[field] = df[field].astype(str).str.lower().isin(['true', 'sim', 'yes', '1'])
            except:
                df[field] = False
    
    # Processar status e prioridade
    try:
        df['status'] = df['status'].astype(str).str.upper()
        df['is_resolved'] = df['status'] == 'RESOLVED'
        df['needs_human'] = df['status'] == 'HUMAN_REQUESTED'
    except:
        df['is_resolved'] = False
        df['needs_human'] = False
    
    try:
        df['priority'] = df['priority'].astype(str).str.upper()
    except:
        df['priority'] = 'MEDIUM'
    
    # Calcular campos derivados de forma segura
    try:
        if 'created_at' in df.columns and not df['created_at'].isna().all():
            df['hour_of_day'] = df['created_at'].dt.hour
            df['day_of_week'] = df['created_at'].dt.day_name()
            df['date'] = df['created_at'].dt.date
        else:
            df['hour_of_day'] = 12
            df['day_of_week'] = 'Monday'
            df['date'] = datetime.now().date()
    except:
        df['hour_of_day'] = 12
        df['day_of_week'] = 'Monday'
        df['date'] = datetime.now().date()
    
    # Classificar frustração
    try:
        df['frustration_category'] = df['frustration_level'].apply(classify_frustration)
    except:
        df['frustration_category'] = 'Não Informado'
    
    # Filtrar registros válidos
    try:
        df = df[df['conversation_id'].notna() & (df['conversation_id'].astype(str) != '') & (df['conversation_id'].astype(str) != 'nan')]
    except:
        pass
    
    return df

def classify_frustration(level):
    """Classifica nível de frustração de forma segura"""
    try:
        if pd.isna(level) or level == 0:
            return 'Não Informado'
        elif level <= 2:
            return 'Baixo'
        elif level <= 4:
            return 'Médio'
        else:
            return 'Alto'
    except:
        return 'Não Informado'

def create_premium_metrics_cards(df):
    """Cria cards de métricas principais - DESIGN PREMIUM"""
    if df.empty:
        st.warning("📊 Aguardando dados para análise...")
        
        # Mostrar métricas zeradas com visual premium
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💬 Total de Conversas", 0, help="Total de conversas no período selecionado")
            st.metric("✅ Taxa de Resolução", "0%", help="Percentual de conversas resolvidas")
        with col2:
            st.metric("⚡ Tempo de Resposta", "0s", help="Tempo médio para primeira resposta")
            st.metric("🏁 Tempo de Resolução", "0min", help="Tempo médio para resolver conversa")
        with col3:
            st.metric("😊 Satisfação Média", "0/5", help="Nota média de satisfação do cliente")
            st.metric("🆘 Escalações", "0 (0%)", help="Conversas escaladas para humanos")
        with col4:
            st.metric("📱 WhatsApp", 0, help="Conversas via WhatsApp")
            st.metric("💻 Dashboard", 0, help="Conversas via Dashboard")
        return
    
    # Calcular métricas de forma segura
    total_conversas = len(df)
    
    try:
        conversas_resolvidas = safe_get_column(df, 'is_resolved', False).sum()
        taxa_resolucao = (conversas_resolvidas / total_conversas * 100) if total_conversas > 0 else 0
    except:
        conversas_resolvidas = 0
        taxa_resolucao = 0
    
    try:
        tempo_resposta_medio = safe_get_column(df, 'first_response_time', 0).mean()
        tempo_resolucao_medio = safe_get_column(df, 'resolution_time', 0).mean()
    except:
        tempo_resposta_medio = 0
        tempo_resolucao_medio = 0
    
    try:
        satisfacao_media = safe_get_column(df, 'satisfaction_score', 0).mean()
    except:
        satisfacao_media = 0
    
    try:
        escalacoes = safe_get_column(df, 'needs_human', False).sum()
        taxa_escalacao = (escalacoes / total_conversas * 100) if total_conversas > 0 else 0
    except:
        escalacoes = 0
        taxa_escalacao = 0
    
    try:
        canais_stats = safe_get_column(df, 'channel', 'unknown').value_counts().to_dict()
    except:
        canais_stats = {}
    
    # Exibir métricas com visual premium
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💬 Total de Conversas", 
            f"{total_conversas:,}", 
            help="Total de conversas no período selecionado"
        )
        delta_resolucao = "↗️" if taxa_resolucao > 70 else "↘️"
        st.metric(
            "✅ Taxa de Resolução", 
            f"{taxa_resolucao:.1f}%", 
            delta=delta_resolucao,
            help="Percentual de conversas resolvidas com sucesso"
        )
    
    with col2:
        delta_resposta = "↗️" if tempo_resposta_medio < 60 else "↘️"
        st.metric(
            "⚡ Tempo de Resposta", 
            f"{tempo_resposta_medio:.1f}s", 
            delta=delta_resposta,
            help="Tempo médio para primeira resposta"
        )
        st.metric(
            "🏁 Tempo de Resolução", 
            f"{tempo_resolucao_medio:.1f}min", 
            help="Tempo médio para resolver conversa"
        )
    
    with col3:
        delta_satisfacao = "↗️" if satisfacao_media > 3.5 else "↘️"
        st.metric(
            "😊 Satisfação Média", 
            f"{satisfacao_media:.1f}/5", 
            delta=delta_satisfacao,
            help="Nota média de satisfação do cliente"
        )
        delta_escalacao = "↘️" if taxa_escalacao < 20 else "↗️"
        st.metric(
            "🆘 Escalações", 
            f"{escalacoes} ({taxa_escalacao:.1f}%)", 
            delta=delta_escalacao,
            help="Conversas escaladas para atendimento humano"
        )
    
    with col4:
        st.metric(
            "📱 WhatsApp", 
            canais_stats.get('whatsapp', 0), 
            help="Conversas originadas via WhatsApp"
        )
        st.metric(
            "💻 Dashboard", 
            canais_stats.get('dashboard', 0), 
            help="Conversas originadas via Dashboard"
        )

def create_premium_status_chart(df):
    """Gráfico de distribuição por status - DESIGN PREMIUM"""
    if df.empty:
        st.info("📊 Aguardando dados para gráfico de status")
        return
    
    try:
        status_column = safe_get_column(df, 'status', 'UNKNOWN')
        status_count = status_column.value_counts()
        
        if status_count.empty:
            st.warning("📊 Nenhum status encontrado nos dados")
            return
        
        # Cores premium para status
        cores_status = {
            'RESOLVED': '#4caf50',
            'UNRESOLVED': '#ff9800', 
            'HUMAN_REQUESTED': '#f44336',
            'UNKNOWN': '#9e9e9e'
        }
        
        colors = [cores_status.get(status, '#9e9e9e') for status in status_count.index]
        
        # Criar gráfico com estilo premium
        fig = px.pie(
            values=status_count.values,
            names=status_count.index,
            title="📊 Distribuição por Status de Atendimento",
            color_discrete_sequence=colors,
            hole=0.4  # Donut chart para visual mais moderno
        )
        
        # Personalização premium
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont_size=12,
            marker=dict(line=dict(color='rgba(255,255,255,0.2)', width=2))
        )
        
        fig.update_layout(
            font=dict(color='#e3f2fd', size=12),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font_size=16,
            title_font_color='#90caf9',
            height=400,
            showlegend=True,
            legend=dict(
                bgcolor='rgba(255,255,255,0.05)',
                bordercolor='rgba(100,181,246,0.2)',
                borderwidth=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico de status: {e}")

def create_premium_channel_analysis(df):
    """Análise por canal - DESIGN PREMIUM"""
    if df.empty:
        st.info("📊 Aguardando dados para análise de canais")
        return
    
    try:
        # Criar dados seguros
        safe_data = {}
        safe_data['channel'] = safe_get_column(df, 'channel', 'unknown')
        safe_data['conversation_id'] = safe_get_column(df, 'conversation_id', 'conv_unknown')
        safe_data['is_resolved'] = safe_get_column(df, 'is_resolved', False)
        safe_data['satisfaction_score'] = safe_get_column(df, 'satisfaction_score', 0)
        safe_data['first_response_time'] = safe_get_column(df, 'first_response_time', 0)
        
        safe_df = pd.DataFrame(safe_data)
        
        canal_stats = safe_df.groupby('channel').agg({
            'conversation_id': 'count',
            'is_resolved': 'sum',
            'satisfaction_score': 'mean',
            'first_response_time': 'mean'
        }).round(2)
        
        canal_stats.columns = ['Total', 'Resolvidos', 'Satisfação_Média', 'Tempo_Resposta_Médio']
        canal_stats['Taxa_Resolução'] = (canal_stats['Resolvidos'] / canal_stats['Total'] * 100).round(1)
        canal_stats = canal_stats.reset_index()
        
        if not canal_stats.empty:
            # Gráfico premium
            fig = px.bar(
                canal_stats,
                x='channel',
                y=['Total', 'Resolvidos'],
                title="📈 Performance por Canal de Atendimento",
                barmode='group',
                color_discrete_sequence=['#64b5f6', '#4caf50'],
                text_auto=True
            )
            
            # Personalização premium
            fig.update_layout(
                font=dict(color='#e3f2fd', size=12),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title_font_size=16,
                title_font_color='#90caf9',
                height=400,
                xaxis=dict(
                    gridcolor='rgba(100,181,246,0.1)',
                    title_font_color='#90caf9'
                ),
                yaxis=dict(
                    gridcolor='rgba(100,181,246,0.1)',
                    title_font_color='#90caf9'
                ),
                legend=dict(
                    bgcolor='rgba(255,255,255,0.05)',
                    bordercolor='rgba(100,181,246,0.2)',
                    borderwidth=1
                )
            )
            
            fig.update_traces(
                textfont_color='white',
                marker_line_color='rgba(255,255,255,0.2)',
                marker_line_width=1
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela premium
            st.markdown("### 📋 Detalhes por Canal")
            canal_stats['🎯 Performance'] = canal_stats['Taxa_Resolução'].apply(
                lambda x: '🔥 Excelente' if x >= 90 else '👍 Boa' if x >= 70 else '⚠️ Regular' if x >= 50 else '🔴 Baixa'
            )
            st.dataframe(canal_stats, use_container_width=True)
        else:
            st.warning("📊 Sem dados de canal para exibir")
            
    except Exception as e:
        st.error(f"❌ Erro na análise de canais: {e}")

def main():
    """Função principal do dashboard premium"""
    
    # Aplicar estilo premium
    apply_premium_styling()
    
    # Header premium com branding Reach IA
    st.markdown("""
    <h1>🚀 Dashboard Reach IA</h1>
    <div class="subtitle">
        Análise Inteligente de Conversas | Otimização de Atendimento com IA
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar premium
    with st.sidebar:
        st.markdown("### 🎛️ Centro de Controle")
        
        # Status de conexão premium
        st.markdown("#### 🔍 Status do Sistema")
        
        config_ok = True
        if 'GOOGLE_CREDENTIALS' not in st.secrets:
            st.error("🔐 Google Credentials")
            config_ok = False
        else:
            st.success("🔐 Google Credentials")
        
        if 'chatvolt_api_key' not in st.secrets:
            st.warning("🔑 API Chatvolt")
        else:
            st.success("🔑 API Chatvolt")
        
        st.markdown("---")
        
        # Controles premium
        data_source = st.radio(
            "📊 Fonte de Dados:",
            ["Google Sheets", "Dados Demonstração"],
            help="Escolha a fonte dos dados para análise"
        )
        
        st.markdown("---")
        
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", False, help="Atualização automática dos dados")
        
        if auto_refresh:
            time.sleep(30)
            st.rerun()
        
        if st.button("🔄 Atualizar Agora", help="Atualizar dados manualmente"):
            st.cache_data.clear()
            st.rerun()
    
    # Carregamento de dados com spinner premium
    with st.spinner("🚀 Carregando dados do Reach IA..."):
        if data_source == "Google Sheets" and config_ok:
            df = get_data_from_sheets()
        else:
            # Dados de demonstração
            st.info("🔧 **Modo Demonstração** - Dados simulados para teste")
            mock_data = {
                'conversation_id': ['conv_001', 'conv_002', 'conv_003', 'conv_004', 'conv_005'],
                'created_at': [datetime.now() - timedelta(hours=i) for i in range(5)],
                'status': ['RESOLVED', 'UNRESOLVED', 'RESOLVED', 'HUMAN_REQUESTED', 'RESOLVED'],
                'priority': ['HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM'],
                'channel': ['whatsapp', 'dashboard', 'whatsapp', 'api', 'whatsapp'],
                'frustration_level': [2, 3, 1, 4, 2],
                'first_response_time': [30, 45, 25, 90, 35],
                'satisfaction_score': [4, 2, 5, 3, 4],
                'is_resolved': [True, False, True, False, True],
                'needs_human': [False, False, False, True, False]
            }
            df = pd.DataFrame(mock_data)
            df = process_chatvolt_data(df)
    
    # Verificar se temos dados
    if df.empty:
        st.error("❌ Nenhum dado disponível para análise")
        st.info("🔧 **Soluções sugeridas:**")
        st.info("• Verifique se a service account tem acesso à planilha")
        st.info("• Configure as credenciais no Streamlit Secrets") 
        st.info("• Use o modo demonstração para testar")
        st.stop()
    
    # Status de carregamento premium
    st.success(f"✅ **Sistema Reach IA ativo** - {len(df)} conversas analisadas")
    
    # Cards de métricas premium
    create_premium_metrics_cards(df)
    
    # Separador visual
    st.markdown("---")
    
    # Layout em abas premium
    tab1, tab2, tab3 = st.tabs([
        "📊 **Visão Geral**", 
        "📈 **Análise Temporal**", 
        "📋 **Dados Detalhados**"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            create_premium_status_chart(df)
        with col2:
            create_premium_channel_analysis(df)
    
    with tab2:
        st.info("📈 Análise temporal será implementada na próxima fase")
        st.markdown("**Em desenvolvimento:**")
        st.markdown("• Evolução temporal das conversas")
        st.markdown("• Mapa de calor por horário") 
        st.markdown("• Tendências e padrões")
    
    with tab3:
        st.markdown("### 📋 Dados Detalhados das Conversas")
        
        if not df.empty:
            colunas_exibir = [
                'conversation_id', 'created_at', 'status', 'channel', 'priority',
                'frustration_level', 'first_response_time', 'satisfaction_score'
            ]
            
            colunas_disponiveis = [col for col in colunas_exibir if col in df.columns]
            df_display = df[colunas_disponiveis].copy()
            
            # Formatar datas
            if 'created_at' in df_display.columns:
                df_display['created_at'] = df_display['created_at'].dt.strftime('%d/%m/%Y %H:%M')
            
            st.info(f"📊 Exibindo **{len(df_display)}** conversas")
            st.dataframe(df_display, use_container_width=True, height=400)
            
            # Download premium
            if st.button("📥 Preparar Download CSV"):
                csv = df_display.to_csv(index=False)
                st.download_button(
                    label="📥 Baixar Dados CSV",
                    data=csv,
                    file_name=f'reach_ia_conversas_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                    mime='text/csv'
                )
        else:
            st.warning("Nenhum dado disponível para exibição")
    
    # Footer premium
    st.markdown("""
    <div class="footer">
        <strong>🚀 Dashboard Reach IA Premium</strong> | 
        Última atualização: """ + f"""{datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')} | 
        Conversas analisadas: {len(df)} | 
        Powered by IA
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
