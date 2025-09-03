"""
DASHBOARD REACH IA - ANÁLISE INTELIGENTE DE CONVERSAS
Sistema Premium de Métricas com IA - Visual Elegante + Dados Ricos
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

# Configuração da página
st.set_page_config(
    page_title="Dashboard Reach IA",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações
CHATVOLT_API_BASE = "https://api.chatvolt.ai"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
PLANILHA_ID = "1Ji8hgGiQanGKMqblxRzkA_E_sLoI6AnpapmU72nXHsA"

# Estado do tema
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

def apply_elegant_styling():
    """Aplica estilo elegante e moderno com toggle claro/escuro"""
    
    if st.session_state.dark_mode:
        # TEMA ESCURO ELEGANTE
        st.markdown("""
        <style>
        /* ============= TEMA ESCURO ELEGANTE ============= */
        
        .stApp {
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2d47 50%, #1e1e2e 100%);
            color: #ffffff;
        }
        
        .main .block-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 2rem;
            max-width: 95%;
        }
        
        /* Header moderno */
        .main-header {
            text-align: center;
            padding: 1rem 0 2rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 2rem;
        }
        
        .main-title {
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60a5fa, #3b82f6, #1d4ed8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .main-subtitle {
            font-size: 1.1rem;
            color: #94a3b8;
            font-weight: 400;
        }
        
        /* Cards elegantes */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.1));
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(59, 130, 246, 0.1);
            border-color: rgba(59, 130, 246, 0.4);
        }
        
        /* Valores das métricas */
        [data-testid="metric-container"] [data-testid="metric-value"] {
            font-size: 2.25rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
        }
        
        /* Labels das métricas */
        [data-testid="metric-container"] [data-testid="metric-label"] {
            font-size: 0.875rem !important;
            color: #94a3b8 !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Sidebar elegante */
        .css-1d391kg {
            background: linear-gradient(180deg, #1e1e2e, #2a2d47);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Botões modernos */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #1d4ed8, #1e40af);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.5);
        }
        
        /* Toggle theme button */
        .theme-toggle {
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 999;
            background: rgba(59, 130, 246, 0.2);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .theme-toggle:hover {
            background: rgba(59, 130, 246, 0.4);
            transform: scale(1.1);
        }
        
        /* Gráficos com fundo escuro */
        .js-plotly-plot {
            background: rgba(255, 255, 255, 0.05) !important;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        /* Tabelas elegantes */
        .stDataFrame {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            overflow: hidden;
        }
        
        .stDataFrame table {
            background: transparent !important;
        }
        
        .stDataFrame th {
            background: rgba(59, 130, 246, 0.2) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
        }
        
        /* Abas modernas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: 8px;
            color: #94a3b8;
            font-weight: 500;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            border-color: #3b82f6;
        }
        
        /* Alerts elegantes */
        .stAlert {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 12px;
            color: #ffffff;
        }
        
        .stSuccess {
            background: rgba(34, 197, 94, 0.1);
            border-color: rgba(34, 197, 94, 0.2);
        }
        
        .stError {
            background: rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.2);
        }
        
        .stWarning {
            background: rgba(245, 158, 11, 0.1);
            border-color: rgba(245, 158, 11, 0.2);
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # TEMA CLARO ELEGANTE
        st.markdown("""
        <style>
        /* ============= TEMA CLARO ELEGANTE ============= */
        
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%);
            color: #1e293b;
        }
        
        .main .block-container {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            border: 1px solid rgba(0, 0, 0, 0.05);
            padding: 2rem;
            max-width: 95%;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
        }
        
        /* Header claro */
        .main-header {
            text-align: center;
            padding: 1rem 0 2rem 0;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }
        
        .main-title {
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8, #1e40af);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .main-subtitle {
            font-size: 1.1rem;
            color: #64748b;
            font-weight: 400;
        }
        
        /* Cards claro */
        [data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(59, 130, 246, 0.2);
            border-color: rgba(59, 130, 246, 0.4);
        }
        
        /* Valores métricas claro */
        [data-testid="metric-container"] [data-testid="metric-value"] {
            font-size: 2.25rem !important;
            font-weight: 700 !important;
            color: #1e293b !important;
        }
        
        [data-testid="metric-container"] [data-testid="metric-label"] {
            font-size: 0.875rem !important;
            color: #64748b !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Sidebar claro */
        .css-1d391kg {
            background: linear-gradient(180deg, #ffffff, #f8fafc);
            border-right: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        /* Botões claro */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #1d4ed8, #1e40af);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
        }
        
        /* Toggle tema claro */
        .theme-toggle {
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 999;
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        /* Gráficos claro */
        .js-plotly-plot {
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 16px;
            border: 1px solid rgba(0, 0, 0, 0.05);
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        
        /* Tabelas claro */
        .stDataFrame {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 12px;
            border: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        .stDataFrame th {
            background: rgba(59, 130, 246, 0.1) !important;
            color: #1e293b !important;
            font-weight: 600 !important;
        }
        </style>
        """, unsafe_allow_html=True)

def toggle_theme():
    """Toggle entre tema claro e escuro"""
    st.session_state.dark_mode = not st.session_state.dark_mode

@st.cache_data(ttl=300)
def get_rich_data_from_sheets():
    """Carrega dados ricos das duas abas da planilha"""
    try:
        if 'GOOGLE_CREDENTIALS' not in st.secrets:
            st.error("🔐 Credenciais do Google não configuradas")
            return pd.DataFrame(), pd.DataFrame()
        
        creds_dict = dict(st.secrets['GOOGLE_CREDENTIALS'])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(PLANILHA_ID)
        
        # Carregar aba "Conversas"
        conversas_df = pd.DataFrame()
        try:
            conversas_ws = sheet.worksheet('Conversas')
            conversas_data = conversas_ws.get_all_values()
            if len(conversas_data) > 1:
                headers = conversas_data[0]
                rows = conversas_data[1:]
                rows = [row for row in rows if any(cell.strip() for cell in row if cell)]
                if rows:
                    conversas_df = pd.DataFrame(rows, columns=headers)
                    st.success(f"✅ Aba Conversas: {len(conversas_df)} registros")
        except Exception as e:
            st.warning(f"⚠️ Aba Conversas não encontrada: {e}")
        
        # Carregar aba "Contatos" (dados ricos)
        contatos_df = pd.DataFrame()
        try:
            contatos_ws = sheet.worksheet('Contatos')
            contatos_data = contatos_ws.get_all_values()
            if len(contatos_data) > 1:
                headers = contatos_data[0]
                rows = contatos_data[1:]
                rows = [row for row in rows if any(cell.strip() for cell in row if cell)]
                if rows:
                    # Garantir mesmo número de colunas
                    max_cols = len(headers)
                    processed_rows = []
                    for row in rows:
                        while len(row) < max_cols:
                            row.append('')
                        processed_rows.append(row[:max_cols])
                    
                    contatos_df = pd.DataFrame(processed_rows, columns=headers)
                    st.success(f"✅ Aba Contatos: {len(contatos_df)} registros com {len(headers)} campos")
        except Exception as e:
            st.warning(f"⚠️ Aba Contatos não encontrada: {e}")
        
        return conversas_df, contatos_df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame()

def process_rich_data(conversas_df, contatos_df):
    """Processa e enriquece os dados combinando as duas abas"""
    
    if not contatos_df.empty:
        # Usar dados da aba Contatos (mais rica)
        df = contatos_df.copy()
        st.info("📊 Usando dados enriquecidos da aba Contatos")
    elif not conversas_df.empty:
        # Fallback para aba Conversas
        df = conversas_df.copy()
        st.info("📊 Usando dados básicos da aba Conversas")
    else:
        st.warning("⚠️ Nenhum dado encontrado em ambas as abas")
        return pd.DataFrame()
    
    # Processar campos essenciais
    essential_fields = [
        'conversation_id', 'created_at', 'status', 'channel', 'priority',
        'frustration_level', 'first_response_time', 'satisfaction_score',
        'context_sentiment', 'mentions_product', 'mentions_price',
        'var_preco', 'quantidade_pneus', 'modelo_pneu'
    ]
    
    for field in essential_fields:
        if field not in df.columns:
            if field in ['mentions_product', 'mentions_price']:
                df[field] = False
            elif field == 'context_sentiment':
                df[field] = 'neutral'
            else:
                df[field] = '' if field in ['conversation_id', 'status', 'channel'] else 0
    
    # Processar timestamps
    for time_col in ['created_at', 'updated_at']:
        if time_col in df.columns:
            df[time_col] = pd.to_datetime(df[time_col], errors='coerce', dayfirst=True)
    
    # Processar campos numéricos
    numeric_fields = ['frustration_level', 'first_response_time', 'satisfaction_score', 'var_preco', 'quantidade_pneus']
    for field in numeric_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
    
    # Processar campos booleanos
    bool_fields = ['mentions_product', 'mentions_price', 'resolved', 'escalated_to_human']
    for field in bool_fields:
        if field in df.columns:
            df[field] = df[field].astype(str).str.lower().isin(['true', 'sim', 'yes', '1'])
    
    # Processar status
    if 'status' in df.columns:
        df['status'] = df['status'].astype(str).str.upper()
        df['is_resolved'] = df['status'] == 'RESOLVED'
        df['needs_human'] = df['status'] == 'HUMAN_REQUESTED'
    
    # Classificar sentimento
    if 'context_sentiment' in df.columns:
        sentiment_map = {'positive': 'Positivo', 'negative': 'Negativo', 'neutral': 'Neutro'}
        df['sentiment_pt'] = df['context_sentiment'].map(sentiment_map).fillna('Neutro')
    
    # Filtrar registros válidos
    df = df[df['conversation_id'].notna() & (df['conversation_id'].astype(str) != '')]
    
    return df

def create_metric_card(title, value, delta=None, help_text=None, icon="📊"):
    """Cria um card de métrica elegante"""
    col = st.columns(1)[0]
    with col:
        if delta:
            st.metric(
                label=f"{icon} {title}",
                value=value,
                delta=delta,
                help=help_text
            )
        else:
            st.metric(
                label=f"{icon} {title}",
                value=value,
                help=help_text
            )

def create_elegant_kpi_section(df):
    """Seção de KPIs principais com design elegante"""
    if df.empty:
        st.warning("📊 Aguardando dados para análise...")
        return
    
    st.markdown("### 📊 Indicadores Principais")
    
    # Calcular KPIs
    total_conversas = len(df)
    taxa_resolucao = (df.get('is_resolved', pd.Series([False])).sum() / total_conversas * 100) if total_conversas > 0 else 0
    tempo_resposta = df.get('first_response_time', pd.Series([0])).mean()
    satisfacao = df.get('satisfaction_score', pd.Series([0])).mean()
    
    # Análises IA (se disponível)
    sentimento_positivo = (df.get('context_sentiment', pd.Series([])) == 'positive').sum() if 'context_sentiment' in df.columns else 0
    mencoes_produto = df.get('mentions_product', pd.Series([False])).sum() if 'mentions_product' in df.columns else 0
    valor_medio = df.get('var_preco', pd.Series([0])).mean() if 'var_preco' in df.columns else 0
    
    # Layout em grid 4x2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card(
            "Total Conversas", 
            f"{total_conversas:,}", 
            help_text="Total de conversas analisadas"
        )
        
    with col2:
        delta_resolucao = "↗️ Boa" if taxa_resolucao > 70 else "↘️ Baixa"
        create_metric_card(
            "Taxa Resolução", 
            f"{taxa_resolucao:.1f}%", 
            delta=delta_resolucao,
            help_text="Percentual de conversas resolvidas"
        )
        
    with col3:
        delta_tempo = "↗️ Rápido" if tempo_resposta < 60 else "↘️ Lento"
        create_metric_card(
            "Tempo Resposta", 
            f"{tempo_resposta:.0f}s", 
            delta=delta_tempo,
            help_text="Tempo médio de primeira resposta"
        )
        
    with col4:
        delta_satisfacao = "↗️ Alta" if satisfacao > 3.5 else "↘️ Baixa"
        create_metric_card(
            "Satisfação", 
            f"{satisfacao:.1f}/5", 
            delta=delta_satisfacao,
            help_text="Nota média de satisfação"
        )
    
    # Segunda linha - KPIs de IA
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        create_metric_card(
            "Sentimento +", 
            f"{sentimento_positivo}", 
            icon="😊",
            help_text="Conversas com sentimento positivo"
        )
        
    with col6:
        create_metric_card(
            "Menções Produto", 
            f"{mencoes_produto}", 
            icon="🛍️",
            help_text="Conversas que mencionam produtos"
        )
        
    with col7:
        create_metric_card(
            "Valor Médio", 
            f"R$ {valor_medio:,.0f}", 
            icon="💰",
            help_text="Valor médio mencionado"
        )
        
    with col8:
        escalacoes = df.get('needs_human', pd.Series([False])).sum()
        create_metric_card(
            "Escalações", 
            f"{escalacoes}", 
            icon="🆘",
            help_text="Conversas escaladas para humano"
        )

def create_status_donut_chart(df):
    """Gráfico donut de status elegante"""
    if df.empty or 'status' not in df.columns:
        return
    
    status_count = df['status'].value_counts()
    
    # Cores elegantes
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
    
    fig = go.Figure(data=[go.Pie(
        labels=status_count.index,
        values=status_count.values,
        hole=0.6,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='auto',
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
    )])
    
    # Personalização elegante
    fig.update_layout(
        title={
            'text': "📊 Distribuição por Status",
            'x': 0.5,
            'font': {'size': 18, 'color': '#ffffff' if st.session_state.dark_mode else '#1e293b'}
        },
        font=dict(
            color='#ffffff' if st.session_state.dark_mode else '#1e293b',
            size=12
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    # Adicionar anotação central
    fig.add_annotation(
        text=f"<b>{len(df)}</b><br>Total",
        x=0.5, y=0.5,
        font_size=16,
        showarrow=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_channel_performance_chart(df):
    """Gráfico de performance por canal"""
    if df.empty or 'channel' not in df.columns:
        return
    
    # Calcular métricas por canal
    channel_stats = df.groupby('channel').agg({
        'conversation_id': 'count',
        'is_resolved': 'sum',
        'satisfaction_score': 'mean',
        'first_response_time': 'mean'
    }).round(2)
    
    channel_stats['taxa_resolucao'] = (channel_stats['is_resolved'] / channel_stats['conversation_id'] * 100).round(1)
    channel_stats = channel_stats.reset_index()
    
    # Gráfico de barras elegante
    fig = go.Figure()
    
    # Barras para total
    fig.add_trace(go.Bar(
        x=channel_stats['channel'],
        y=channel_stats['conversation_id'],
        name='Total Conversas',
        marker_color='#3b82f6',
        text=channel_stats['conversation_id'],
        textposition='auto'
    ))
    
    # Barras para resolvidas
    fig.add_trace(go.Bar(
        x=channel_stats['channel'],
        y=channel_stats['is_resolved'],
        name='Resolvidas',
        marker_color='#10b981',
        text=channel_stats['is_resolved'],
        textposition='auto'
    ))
    
    fig.update_layout(
        title={
            'text': "📈 Performance por Canal",
            'x': 0.5,
            'font': {'size': 18, 'color': '#ffffff' if st.session_state.dark_mode else '#1e293b'}
        },
        barmode='group',
        font=dict(
            color='#ffffff' if st.session_state.dark_mode else '#1e293b',
            size=12
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis=dict(
            title="Canal",
            gridcolor='rgba(255,255,255,0.1)' if st.session_state.dark_mode else 'rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            title="Quantidade",
            gridcolor='rgba(255,255,255,0.1)' if st.session_state.dark_mode else 'rgba(0,0,0,0.1)'
        ),
        legend=dict(
            bgcolor='rgba(255,255,255,0.05)' if st.session_state.dark_mode else 'rgba(0,0,0,0.05)'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela complementar
    st.dataframe(channel_stats.rename(columns={
        'channel': 'Canal',
        'conversation_id': 'Total',
        'is_resolved': 'Resolvidas',
        'satisfaction_score': 'Satisfação Média',
        'first_response_time': 'Tempo Resposta (s)',
        'taxa_resolucao': 'Taxa Resolução (%)'
    }), use_container_width=True)

def create_sentiment_analysis(df):
    """Análise de sentimento com dados ricos"""
    if df.empty or 'context_sentiment' not in df.columns:
        st.info("📊 Análise de sentimento não disponível nos dados atuais")
        return
    
    sentiment_count = df['sentiment_pt'].value_counts()
    
    # Gráfico de pizza para sentimento
    colors = {'Positivo': '#10b981', 'Neutro': '#6b7280', 'Negativo': '#ef4444'}
    
    fig = go.Figure(data=[go.Pie(
        labels=sentiment_count.index,
        values=sentiment_count.values,
        marker_colors=[colors.get(label, '#6b7280') for label in sentiment_count.index],
        textinfo='label+percent+value',
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title={
            'text': "🧠 Análise de Sentimento (IA)",
            'x': 0.5,
            'font': {'size': 18, 'color': '#ffffff' if st.session_state.dark_mode else '#1e293b'}
        },
        font=dict(
            color='#ffffff' if st.session_state.dark_mode else '#1e293b'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_product_mentions_chart(df):
    """Gráfico de menções de produto"""
    if df.empty or 'mentions_product' not in df.columns:
        return
    
    # Calcular estatísticas de menções
    mentions_stats = {
        'Com Menção Produto': df['mentions_product'].sum(),
        'Sem Menção Produto': (~df['mentions_product']).sum(),
        'Com Menção Preço': df.get('mentions_price', pd.Series([False])).sum(),
        'Sem Menção Preço': (~df.get('mentions_price', pd.Series([False]))).sum()
    }
    
    # Gráfico de barras horizontais
    fig = go.Figure()
    
    categories = ['Menção Produto', 'Menção Preço']
    with_mention = [mentions_stats['Com Menção Produto'], mentions_stats['Com Menção Preço']]
    without_mention = [mentions_stats['Sem Menção Produto'], mentions_stats['Sem Menção Preço']]
    
    fig.add_trace(go.Bar(
        y=categories,
        x=with_mention,
        name='Com Menção',
        orientation='h',
        marker_color='#3b82f6'
    ))
    
    fig.add_trace(go.Bar(
        y=categories,
        x=without_mention,
        name='Sem Menção',
        orientation='h',
        marker_color='#6b7280'
    ))
    
    fig.update_layout(
        title={
            'text': "🛍️ Análise de Menções (IA)",
            'x': 0.5,
            'font': {'size': 18, 'color': '#ffffff' if st.session_state.dark_mode else '#1e293b'}
        },
        barmode='stack',
        font=dict(
            color='#ffffff' if st.session_state.dark_mode else '#1e293b'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Função principal do dashboard elegante"""
    
    # Aplicar estilo elegante
    apply_elegant_styling()
    
    # Toggle de tema no canto superior direito
    if st.button("🌓", key="theme_toggle", help="Alternar tema claro/escuro"):
        toggle_theme()
        st.rerun()
    
    # Header elegante
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🚀 Dashboard Reach IA</div>
        <div class="main-subtitle">Análise Inteligente de Conversas | Sistema Premium de Métricas com IA</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar elegante
    with st.sidebar:
        st.markdown("### 🎛️ Centro de Controle")
        st.markdown("---")
        
        # Status de conexão
        config_ok = True
        if 'GOOGLE_CREDENTIALS' not in st.secrets:
            st.error("🔐 Google não configurado")
            config_ok = False
        else:
            st.success("🔐 Google Sheets conectado")
        
        st.markdown("---")
        
        # Fonte de dados
        data_source = st.radio(
            "📊 Fonte de Dados:",
            ["📋 Planilha Completa", "🧪 Demonstração"],
            help="Escolha entre dados reais ou demonstração"
        )
        
        st.markdown("---")
        
        # Filtros (implementar na próxima iteração)
        st.markdown("### 🔍 Filtros")
        st.info("🔧 Filtros avançados em desenvolvimento...")
        
        st.markdown("---")
        
        # Controles
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", False)
        if auto_refresh:
            time.sleep(30)
            st.rerun()
    
    # Carregamento de dados
    with st.spinner("🚀 Carregando dados do Reach IA..."):
        if data_source == "📋 Planilha Completa" and config_ok:
            conversas_df, contatos_df = get_rich_data_from_sheets()
            df = process_rich_data(conversas_df, contatos_df)
        else:
            # Dados de demonstração mais ricos
            st.info("🧪 **Modo Demonstração** - Dados simulados com funcionalidades de IA")
            mock_data = {
                'conversation_id': [f'conv_{i:03d}' for i in range(1, 11)],
                'created_at': [datetime.now() - timedelta(hours=i) for i in range(10)],
                'status': ['RESOLVED', 'UNRESOLVED', 'RESOLVED', 'HUMAN_REQUESTED', 'RESOLVED'] * 2,
                'channel': ['whatsapp', 'dashboard', 'whatsapp', 'zapi', 'whatsapp'] * 2,
                'frustration_level': [1, 3, 2, 4, 1, 2, 3, 4, 2, 1],
                'first_response_time': [25, 45, 30, 90, 20, 35, 60, 120, 40, 25],
                'satisfaction_score': [5, 2, 4, 3, 5, 4, 2, 1, 4, 5],
                'context_sentiment': ['positive', 'negative', 'positive', 'negative', 'positive'] * 2,
                'mentions_product': [True, False, True, True, False, True, True, False, True, False],
                'mentions_price': [True, True, False, True, False, False, True, True, False, True],
                'var_preco': [150, 0, 200, 350, 0, 180, 250, 400, 0, 120],
                'quantidade_pneus': [4, 0, 2, 4, 0, 2, 4, 2, 0, 4],
                'is_resolved': [True, False, True, False, True, True, False, False, True, True]
            }
            df = pd.DataFrame(mock_data)
            df = process_rich_data(pd.DataFrame(), df)  # Simular processamento
    
    if df.empty:
        st.error("❌ Nenhum dado disponível")
        st.info("💡 **Soluções:**")
        st.info("• Verificar acesso à planilha Google Sheets")
        st.info("• Testar com dados de demonstração")
        st.stop()
    
    # Status de sucesso
    st.success(f"✅ **Sistema Reach IA operacional** - {len(df)} conversas analisadas")
    
    # KPIs principais
    create_elegant_kpi_section(df)
    
    st.markdown("---")
    
    # Layout principal em abas elegantes
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 **Visão Geral**",
        "🧠 **Análise com IA**", 
        "💼 **Dados Comerciais**",
        "📋 **Detalhes**"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            create_status_donut_chart(df)
            
        with col2:
            create_channel_performance_chart(df)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            create_sentiment_analysis(df)
            
        with col2:
            create_product_mentions_chart(df)
    
    with tab3:
        st.markdown("### 💼 Análise Comercial")
        
        # Métricas comerciais
        if 'var_preco' in df.columns and df['var_preco'].sum() > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                valor_total = df['var_preco'].sum()
                st.metric("💰 Valor Total", f"R$ {valor_total:,.0f}")
                
            with col2:
                conversas_com_preco = (df['var_preco'] > 0).sum()
                st.metric("💵 Com Preço", f"{conversas_com_preco}")
                
            with col3:
                pneus_total = df.get('quantidade_pneus', pd.Series([0])).sum()
                st.metric("🛞 Total Pneus", f"{pneus_total:.0f}")
                
            with col4:
                ticket_medio = df[df['var_preco'] > 0]['var_preco'].mean()
                st.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.0f}")
        else:
            st.info("📊 Dados comerciais não disponíveis na fonte atual")
    
    with tab4:
        st.markdown("### 📋 Dados Detalhados")
        
        # Mostrar dados com colunas principais
        display_columns = [
            'conversation_id', 'created_at', 'status', 'channel', 
            'satisfaction_score', 'context_sentiment', 'var_preco'
        ]
        
        available_columns = [col for col in display_columns if col in df.columns]
        
        if available_columns:
            display_df = df[available_columns].copy()
            
            # Formatar dados para exibição
            if 'created_at' in display_df.columns:
                display_df['created_at'] = display_df['created_at'].dt.strftime('%d/%m/%Y %H:%M')
            
            if 'var_preco' in display_df.columns:
                display_df['var_preco'] = display_df['var_preco'].apply(lambda x: f"R$ {x:,.0f}" if x > 0 else "-")
            
            st.info(f"📊 Exibindo **{len(display_df)}** conversas")
            st.dataframe(display_df, use_container_width=True, height=400)
            
            # Download
            if st.button("📥 Preparar Download"):
                csv = display_df.to_csv(index=False)
                st.download_button(
                    "📥 Baixar Dados CSV",
                    csv,
                    f"reach_ia_dados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv"
                )
        else:
            st.warning("Colunas para exibição não encontradas")
    
    # Footer elegante
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: {"#94a3b8" if st.session_state.dark_mode else "#64748b"}; padding: 1rem;'>
            <strong>🚀 Dashboard Reach IA</strong> | 
            Última atualização: {datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M')} | 
            Registros: {len(df)} | 
            Tema: {"Escuro" if st.session_state.dark_mode else "Claro"} | 
            <strong>Powered by IA</strong>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
