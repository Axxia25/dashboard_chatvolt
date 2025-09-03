"""
DASHBOARD CHATVOLT - MÉTRICAS DE ATENDIMENTO
Sistema completo de análise de conversas e performance de atendimento
Deploy: Streamlit Cloud
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
    page_title="Dashboard Chatvolt Analytics",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações da API Chatvolt
CHATVOLT_API_BASE = "https://api.chatvolt.ai"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# ID da planilha Google Sheets (substitua pelo seu)
PLANILHA_ID = "YOUR_GOOGLE_SHEETS_ID"

class ChatvoltDataCollector:
    """Classe para coleta de dados da API Chatvolt"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.base_url = CHATVOLT_API_BASE
    
    def get_conversation(self, conversation_id):
        """Busca dados completos de uma conversa"""
        try:
            response = requests.get(
                f'{self.base_url}/conversation/{conversation_id}',
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao buscar conversa {conversation_id}: {e}")
            return None
    
    def get_conversation_messages(self, conversation_id):
        """Busca mensagens de uma conversa"""
        try:
            response = requests.get(
                f'{self.base_url}/conversation/{conversation_id}/messages',
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao buscar mensagens: {e}")
            return []
    
    def get_agent_data(self, agent_id):
        """Busca dados do agente"""
        try:
            response = requests.get(
                f'{self.base_url}/agents/{agent_id}',
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao buscar agente: {e}")
            return None
    
    def set_conversation_variable(self, conversation_id, var_name, var_value):
        """Define variável customizada para uma conversa"""
        try:
            response = requests.post(
                f'{self.base_url}/variables',
                headers=self.headers,
                json={
                    'conversationId': conversation_id,
                    'varName': var_name[:20],  # Limitação da API
                    'varValue': str(var_value)[:100]  # Limitação da API
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao definir variável: {e}")
            return None

@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_data_from_sheets():
    """Carrega dados das conversas da planilha Google - MÉTODO OTIMIZADO"""
    try:
        # Configurar credenciais
        creds_dict = dict(st.secrets['GOOGLE_CREDENTIALS'])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(PLANILHA_ID)
        
        # Buscar aba de conversas
        worksheet_names = ['Conversas', 'Conversations', 'Atendimentos', 'Sheet1']
        worksheet = None
        
        for name in worksheet_names:
            try:
                worksheet = sheet.worksheet(name)
                break
            except:
                continue
        
        if not worksheet:
            st.error("Nenhuma aba encontrada na planilha")
            return pd.DataFrame()
        
        # Coletar dados
        all_values = worksheet.get_all_values()
        
        if not all_values or len(all_values) < 2:
            st.warning("Planilha encontrada, mas sem dados suficientes")
            return pd.DataFrame()
        
        headers = all_values[0]
        data_rows = all_values[1:]
        
        # Filtrar linhas vazias
        data_rows = [row for row in data_rows if any(cell.strip() for cell in row)]
        
        if not data_rows:
            st.warning("Nenhuma linha de dados encontrada")
            return pd.DataFrame()
        
        # Criar DataFrame
        max_cols = len(headers)
        processed_rows = []
        
        for row in data_rows:
            while len(row) < max_cols:
                row.append('')
            row = row[:max_cols]
            processed_rows.append(row)
        
        df = pd.DataFrame(processed_rows, columns=headers)
        
        # Processar campos específicos do Chatvolt
        return process_chatvolt_data(df)
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def process_chatvolt_data(df):
    """Processa e limpa dados do Chatvolt"""
    if df.empty:
        return df
    
    # Mapeamento de colunas esperadas
    expected_columns = [
        'conversation_id', 'created_at', 'updated_at', 'status', 'priority',
        'channel', 'visitor_id', 'agent_id', 'frustration_level',
        'first_response_time', 'resolution_time', 'message_count',
        'satisfaction_score', 'resolved', 'escalated_to_human',
        'total_duration', 'response_time_avg', 'contact_email', 'contact_name'
    ]
    
    # Adicionar colunas ausentes
    for col in expected_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Processar timestamps
    for time_col in ['created_at', 'updated_at']:
        if time_col in df.columns:
            df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    
    # Processar campos numéricos
    numeric_fields = ['frustration_level', 'first_response_time', 'resolution_time',
                     'message_count', 'satisfaction_score', 'total_duration', 'response_time_avg']
    
    for field in numeric_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
    
    # Processar campos booleanos
    bool_fields = ['resolved', 'escalated_to_human']
    for field in bool_fields:
        if field in df.columns:
            df[field] = df[field].astype(str).str.lower().isin(['true', 'sim', 'yes', '1'])
    
    # Processar status e prioridade
    if 'status' in df.columns:
        df['status'] = df['status'].str.upper()
        df['is_resolved'] = df['status'] == 'RESOLVED'
        df['needs_human'] = df['status'] == 'HUMAN_REQUESTED'
    
    if 'priority' in df.columns:
        df['priority'] = df['priority'].str.upper()
    
    # Calcular métricas derivadas
    df['hour_of_day'] = df['created_at'].dt.hour
    df['day_of_week'] = df['created_at'].dt.day_name()
    df['date'] = df['created_at'].dt.date
    
    # Classificar nível de frustração
    df['frustration_category'] = df['frustration_level'].apply(classify_frustration)
    
    # Filtrar dados válidos
    df = df[df['conversation_id'].notna() & (df['conversation_id'] != '')]
    
    st.info(f"✅ Dados processados: {len(df)} conversas carregadas")
    
    return df

def classify_frustration(level):
    """Classifica nível de frustração"""
    if pd.isna(level) or level == 0:
        return 'Não Informado'
    elif level <= 2:
        return 'Baixo'
    elif level <= 4:
        return 'Médio'
    else:
        return 'Alto'

def collect_realtime_data():
    """Coleta dados em tempo real da API Chatvolt"""
    if 'chatvolt_api_key' not in st.secrets:
        st.warning("⚠️ Chave da API Chatvolt não configurada")
        return pd.DataFrame()
    
    try:
        collector = ChatvoltDataCollector(st.secrets['chatvolt_api_key'])
        
        # Simular coleta de dados recentes (implementar polling real aqui)
        # Por enquanto, vamos usar dados mock para demonstração
        
        mock_data = [
            {
                'conversation_id': f'conv_{i}',
                'created_at': datetime.now() - timedelta(hours=i),
                'status': ['RESOLVED', 'UNRESOLVED', 'HUMAN_REQUESTED'][i % 3],
                'priority': ['HIGH', 'MEDIUM', 'LOW'][i % 3],
                'channel': ['whatsapp', 'dashboard', 'api'][i % 3],
                'frustration_level': (i % 5) + 1,
                'first_response_time': (i % 30) + 10,
                'satisfaction_score': (i % 5) + 1,
                'message_count': (i % 20) + 1
            }
            for i in range(10)
        ]
        
        return pd.DataFrame(mock_data)
        
    except Exception as e:
        st.error(f"Erro na coleta em tempo real: {e}")
        return pd.DataFrame()

def create_metrics_cards(df):
    """Cria cards de métricas principais"""
    if df.empty:
        st.warning("Nenhum dado encontrado")
        return
    
    total_conversas = len(df)
    conversas_resolvidas = df['is_resolved'].sum() if 'is_resolved' in df.columns else 0
    taxa_resolucao = (conversas_resolvidas / total_conversas * 100) if total_conversas > 0 else 0
    
    # Calcular métricas de tempo
    tempo_resposta_medio = df['first_response_time'].mean() if 'first_response_time' in df.columns else 0
    tempo_resolucao_medio = df['resolution_time'].mean() if 'resolution_time' in df.columns else 0
    
    # Satisfação média
    satisfacao_media = df['satisfaction_score'].mean() if 'satisfaction_score' in df.columns else 0
    
    # Escalações para humano
    escalacoes = df['needs_human'].sum() if 'needs_human' in df.columns else 0
    taxa_escalacao = (escalacoes / total_conversas * 100) if total_conversas > 0 else 0
    
    # Conversas por canal
    canais_stats = df['channel'].value_counts().to_dict() if 'channel' in df.columns else {}
    
    # Exibir métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Conversas", total_conversas)
        st.metric("Taxa de Resolução", f"{taxa_resolucao:.1f}%")
    
    with col2:
        st.metric("Tempo Médio de Resposta", f"{tempo_resposta_medio:.1f}s")
        st.metric("Tempo Médio de Resolução", f"{tempo_resolucao_medio:.1f}min")
    
    with col3:
        st.metric("Satisfação Média", f"{satisfacao_media:.1f}/5")
        st.metric("Escalações para Humano", f"{escalacoes} ({taxa_escalacao:.1f}%)")
    
    with col4:
        st.metric("WhatsApp", canais_stats.get('whatsapp', 0))
        st.metric("Dashboard", canais_stats.get('dashboard', 0))

def create_status_distribution_chart(df):
    """Gráfico de distribuição por status"""
    if df.empty or 'status' not in df.columns:
        return
    
    status_count = df['status'].value_counts()
    
    # Cores por status
    cores_status = {
        'RESOLVED': '#2ecc71',
        'UNRESOLVED': '#f39c12', 
        'HUMAN_REQUESTED': '#e74c3c'
    }
    
    colors = [cores_status.get(status, '#95a5a6') for status in status_count.index]
    
    fig = px.pie(
        values=status_count.values,
        names=status_count.index,
        title="Distribuição por Status de Atendimento",
        color_discrete_sequence=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def create_channel_analysis(df):
    """Análise por canal de origem"""
    if df.empty or 'channel' not in df.columns:
        return
    
    canal_stats = df.groupby('channel').agg({
        'conversation_id': 'count',
        'is_resolved': 'sum',
        'satisfaction_score': 'mean',
        'first_response_time': 'mean'
    }).round(2)
    
    canal_stats.columns = ['Total', 'Resolvidos', 'Satisfação_Média', 'Tempo_Resposta_Médio']
    canal_stats['Taxa_Resolução'] = (canal_stats['Resolvidos'] / canal_stats['Total'] * 100).round(1)
    canal_stats = canal_stats.reset_index()
    
    fig = px.bar(
        canal_stats,
        x='channel',
        y=['Total', 'Resolvidos'],
        title="Performance por Canal de Atendimento",
        barmode='group',
        color_discrete_sequence=['#3498db', '#2ecc71'],
        text_auto=True
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.subheader("Detalhes por Canal")
    
    # Adicionar performance
    canal_stats['Performance'] = canal_stats['Taxa_Resolução'].apply(
        lambda x: '🔥 Excelente' if x >= 90 else '👍 Boa' if x >= 70 else '⚠️ Regular' if x >= 50 else '🔴 Baixa'
    )
    
    st.dataframe(canal_stats, use_container_width=True)

def create_timeline_analysis(df):
    """Análise de evolução temporal"""
    if df.empty or 'created_at' not in df.columns:
        return
    
    # Agrupa por hora
    df_hourly = df.set_index('created_at').resample('H').agg({
        'conversation_id': 'count',
        'is_resolved': 'sum',
        'satisfaction_score': 'mean'
    }).reset_index()
    
    df_hourly.columns = ['Hora', 'Total_Conversas', 'Resolvidas', 'Satisfação_Média']
    df_hourly = df_hourly[df_hourly['Total_Conversas'] > 0]
    
    if df_hourly.empty:
        st.warning("Dados insuficientes para análise temporal")
        return
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Volume de conversas
    fig.add_trace(
        go.Scatter(
            x=df_hourly['Hora'],
            y=df_hourly['Total_Conversas'],
            mode='lines+markers',
            name='Total Conversas',
            line=dict(color='#3498db', width=3)
        ),
        secondary_y=False,
    )
    
    # Conversas resolvidas
    fig.add_trace(
        go.Scatter(
            x=df_hourly['Hora'],
            y=df_hourly['Resolvidas'],
            mode='lines+markers',
            name='Resolvidas',
            line=dict(color='#2ecc71', width=2)
        ),
        secondary_y=False,
    )
    
    # Satisfação (eixo secundário)
    fig.add_trace(
        go.Scatter(
            x=df_hourly['Hora'],
            y=df_hourly['Satisfação_Média'],
            mode='lines+markers',
            name='Satisfação Média',
            line=dict(color='#f39c12', width=2),
            yaxis='y2'
        ),
        secondary_y=True,
    )
    
    fig.update_xaxes(title_text="Período")
    fig.update_yaxes(title_text="Número de Conversas", secondary_y=False)
    fig.update_yaxes(title_text="Satisfação (1-5)", secondary_y=True)
    fig.update_layout(
        title_text="Evolução Temporal de Atendimentos",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_frustration_analysis(df):
    """Análise de nível de frustração"""
    if df.empty or 'frustration_category' not in df.columns:
        return
    
    frustration_stats = df.groupby('frustration_category').agg({
        'conversation_id': 'count',
        'is_resolved': 'sum',
        'first_response_time': 'mean'
    }).round(2)
    
    frustration_stats.columns = ['Total', 'Resolvidas', 'Tempo_Resposta_Médio']
    frustration_stats['Taxa_Resolução'] = (
        frustration_stats['Resolvidas'] / frustration_stats['Total'] * 100
    ).round(1)
    frustration_stats = frustration_stats.reset_index()
    
    fig = px.bar(
        frustration_stats,
        x='frustration_category',
        y='Total',
        title="Distribuição por Nível de Frustração",
        color='Taxa_Resolução',
        color_continuous_scale='RdYlGn',
        text='Total'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def create_hourly_heatmap(df):
    """Mapa de calor por horário"""
    if df.empty or 'hour_of_day' not in df.columns or 'day_of_week' not in df.columns:
        return
    
    # Criar pivot table
    heatmap_data = df.pivot_table(
        values='conversation_id',
        index='day_of_week',
        columns='hour_of_day',
        aggfunc='count',
        fill_value=0
    )
    
    # Reordenar dias da semana
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex(day_order)
    
    fig = px.imshow(
        heatmap_data,
        title="Mapa de Calor: Volume de Atendimentos por Horário",
        labels=dict(x="Hora do Dia", y="Dia da Semana", color="Conversas"),
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def create_response_time_analysis(df):
    """Análise detalhada de tempo de resposta"""
    if df.empty or 'first_response_time' not in df.columns:
        return
    
    # Distribuição de tempo de resposta
    fig = px.histogram(
        df[df['first_response_time'] > 0],
        x='first_response_time',
        title="Distribuição de Tempo de Primeira Resposta",
        nbins=20,
        labels={'first_response_time': 'Tempo de Resposta (segundos)'}
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas descritivas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estatísticas de Tempo de Resposta")
        response_times = df['first_response_time'][df['first_response_time'] > 0]
        
        if len(response_times) > 0:
            st.metric("Tempo Mínimo", f"{response_times.min():.1f}s")
            st.metric("Tempo Máximo", f"{response_times.max():.1f}s")
            st.metric("Mediana", f"{response_times.median():.1f}s")
    
    with col2:
        st.subheader("SLA de Atendimento")
        
        if len(response_times) > 0:
            sla_30s = (response_times <= 30).mean() * 100
            sla_60s = (response_times <= 60).mean() * 100
            sla_120s = (response_times <= 120).mean() * 100
            
            st.metric("< 30 segundos", f"{sla_30s:.1f}%")
            st.metric("< 60 segundos", f"{sla_60s:.1f}%")
            st.metric("< 2 minutos", f"{sla_120s:.1f}%")

def main():
    """Função principal do dashboard"""
    
    # Header
    st.title("💬 Dashboard Chatvolt Analytics")
    st.subheader("Sistema Completo de Métricas de Atendimento - v1.0")
    
    # Sidebar com filtros e controles
    st.sidebar.title("🎛️ Controles")
    
    # Opção de fonte de dados
    data_source = st.sidebar.radio(
        "Fonte de Dados:",
        ["Google Sheets", "Tempo Real (API)", "Ambas"]
    )
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", False)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Botão de atualização manual
    if st.sidebar.button("🔄 Atualizar Dados Agora"):
        st.cache_data.clear()
        st.rerun()
    
    # Carregamento de dados
    with st.spinner("Carregando dados..."):
        if data_source == "Google Sheets":
            df = get_data_from_sheets()
        elif data_source == "Tempo Real (API)":
            df = collect_realtime_data()
        else:  # Ambas
            df_sheets = get_data_from_sheets()
            df_api = collect_realtime_data()
            df = pd.concat([df_sheets, df_api], ignore_index=True) if not df_sheets.empty else df_api
    
    if df.empty:
        st.error("Não foi possível carregar os dados")
        st.stop()
    
    # Filtros na sidebar
    st.sidebar.subheader("🔍 Filtros")
    
    # Filtro de período
    if 'created_at' in df.columns and not df['created_at'].isna().all():
        data_min = df['created_at'].min().date()
        data_max = df['created_at'].max().date()
        
        periodo = st.sidebar.date_input(
            "Período:",
            value=(data_max - timedelta(days=7), data_max),
            min_value=data_min,
            max_value=data_max
        )
        
        if len(periodo) == 2:
            mask = (df['created_at'].dt.date >= periodo[0]) & (df['created_at'].dt.date <= periodo[1])
            df = df[mask]
    
    # Filtro de canal
    if 'channel' in df.columns:
        canais_disponiveis = ['Todos'] + list(df['channel'].unique())
        canal_selecionado = st.sidebar.selectbox("Canal:", canais_disponiveis)
        if canal_selecionado != 'Todos':
            df = df[df['channel'] == canal_selecionado]
    
    # Filtro de status
    if 'status' in df.columns:
        status_disponiveis = ['Todos'] + list(df['status'].unique())
        status_selecionado = st.sidebar.selectbox("Status:", status_disponiveis)
        if status_selecionado != 'Todos':
            df = df[df['status'] == status_selecionado]
    
    # Filtro de prioridade
    if 'priority' in df.columns:
        prioridades_disponiveis = ['Todas'] + list(df['priority'].unique())
        prioridade_selecionada = st.sidebar.selectbox("Prioridade:", prioridades_disponiveis)
        if prioridade_selecionada != 'Todas':
            df = df[df['priority'] == prioridade_selecionada]
    
    # Status do sistema
    st.success(f"✅ Sistema funcionando - {len(df)} conversas carregadas")
    
    # Cards de métricas
    create_metrics_cards(df)
    
    # Layout em abas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral", 
        "⏱️ Tempo de Atendimento", 
        "📈 Análise Temporal", 
        "😤 Frustração", 
        "📋 Dados Detalhados"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            create_status_distribution_chart(df)
        with col2:
            create_channel_analysis(df)
    
    with tab2:
        create_response_time_analysis(df)
    
    with tab3:
        create_timeline_analysis(df)
        st.subheader("🕐 Mapa de Calor por Horário")
        create_hourly_heatmap(df)
    
    with tab4:
        create_frustration_analysis(df)
    
    with tab5:
        st.subheader("📋 Dados Detalhados das Conversas")
        
        if not df.empty:
            # Preparar colunas para exibição
            colunas_exibir = [
                'conversation_id', 'created_at', 'status', 'channel', 'priority',
                'frustration_level', 'first_response_time', 'satisfaction_score',
                'is_resolved', 'contact_name', 'contact_email'
            ]
            
            colunas_disponiveis = [col for col in colunas_exibir if col in df.columns]
            df_display = df[colunas_disponiveis].copy()
            
            # Formatar datas
            if 'created_at' in df_display.columns:
                df_display['created_at'] = df_display['created_at'].dt.strftime('%d/%m/%Y %H:%M')
            
            st.info(f"📊 Mostrando {len(df_display)} conversas")
            st.dataframe(df_display, use_container_width=True, height=400)
            
            # Download CSV
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f'chatvolt_conversas_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv'
            )
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"**Chatvolt Analytics v1.0** | "
        f"Última atualização: {datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')} | "
        f"Fonte: {data_source} | "
        f"🔄 Cache: 5 minutos"
    )

if __name__ == "__main__":
    main()
