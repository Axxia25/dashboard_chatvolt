"""
DASHBOARD REACH IA - ANÁLISE INTELIGENTE DE CONVERSAS
Visual inspirado no Dashboard Luis Imóveis - Clean e Profissional
Sistema expandido com dados ricos da planilha Chatvolt
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

# Cores do tema (igual Luis Imóveis)
CORES_TEMA = {
    'azul': '#3498db',
    'verde': '#2ecc71', 
    'laranja': '#f39c12',
    'vermelho': '#e74c3c',
    'roxo': '#9b59b6',
    'cinza': '#95a5a6'
}

@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_rich_data_from_sheets():
    """Carrega dados ricos das duas abas da planilha - MÉTODO MELHORADO"""
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
                rows = [row for row in conversas_data[1:] if any(cell.strip() for cell in row if cell)]
                if rows:
                    # Garantir mesmo número de colunas
                    max_cols = len(headers)
                    processed_rows = []
                    for row in rows:
                        while len(row) < max_cols:
                            row.append('')
                        processed_rows.append(row[:max_cols])
                    
                    conversas_df = pd.DataFrame(processed_rows, columns=headers)
                    st.success(f"✅ Aba Conversas: {len(conversas_df)} registros carregados")
        except Exception as e:
            st.warning(f"⚠️ Aba Conversas não encontrada: {e}")
        
        # Carregar aba "Contatos" (dados ricos)
        contatos_df = pd.DataFrame()
        try:
            contatos_ws = sheet.worksheet('Contatos')
            contatos_data = contatos_ws.get_all_values()
            if len(contatos_data) > 1:
                headers = contatos_data[0]
                rows = [row for row in contatos_data[1:] if any(cell.strip() for cell in row if cell)]
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
        'var_preco', 'quantidade_pneus', 'modelo_pneu', 'resolved', 'escalated_to_human'
    ]
    
    for field in essential_fields:
        if field not in df.columns:
            if field in ['mentions_product', 'mentions_price', 'resolved', 'escalated_to_human']:
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
    
    # Classificar sentimento em português
    if 'context_sentiment' in df.columns:
        sentiment_map = {'positive': 'Positivo', 'negative': 'Negativo', 'neutral': 'Neutro'}
        df['sentiment_pt'] = df['context_sentiment'].map(sentiment_map).fillna('Neutro')
    
    # Filtrar registros válidos
    df = df[df['conversation_id'].notna() & (df['conversation_id'].astype(str) != '')]
    
    return df

def create_metrics_cards(df):
    """Cria cards de métricas principais - ESTILO LUIS IMÓVEIS"""
    if df.empty:
        st.warning("Nenhum dado encontrado")
        return
    
    total_conversas = len(df)
    conversas_resolvidas = df.get('is_resolved', pd.Series([False])).sum()
    taxa_resolucao = (conversas_resolvidas / total_conversas * 100) if total_conversas > 0 else 0
    
    # Calcular métricas de tempo
    tempo_resposta_medio = df.get('first_response_time', pd.Series([0])).mean()
    tempo_resolucao_medio = df.get('resolution_time', pd.Series([0])).mean()
    
    # Satisfação média
    satisfacao_media = df.get('satisfaction_score', pd.Series([0])).mean()
    
    # Escalações para humano
    escalacoes = df.get('needs_human', pd.Series([False])).sum()
    taxa_escalacao = (escalacoes / total_conversas * 100) if total_conversas > 0 else 0
    
    # Análises IA
    sentimento_positivo = (df.get('context_sentiment', pd.Series([])) == 'positive').sum() if 'context_sentiment' in df.columns else 0
    mencoes_produto = df.get('mentions_product', pd.Series([False])).sum() if 'mentions_product' in df.columns else 0
    
    # Conversas por canal
    canais_stats = df.get('channel', pd.Series([])).value_counts().to_dict() if 'channel' in df.columns else {}
    
    # Exibir métricas em grid 4x2 (igual Luis Imóveis)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Conversas", f"{total_conversas:,}")
        st.metric("Taxa de Resolução", f"{taxa_resolucao:.1f}%")
    
    with col2:
        st.metric("Tempo Médio Resposta", f"{tempo_resposta_medio:.1f}s")
        st.metric("Satisfação Média", f"{satisfacao_media:.1f}/5")
    
    with col3:
        st.metric("Escalações Humano", f"{escalacoes} ({taxa_escalacao:.1f}%)")
        st.metric("Sentimento Positivo", f"{sentimento_positivo}")
    
    with col4:
        st.metric("WhatsApp", canais_stats.get('whatsapp', 0))
        st.metric("Menções Produto", f"{mencoes_produto}")

def create_status_distribution_chart(df):
    """Gráfico de distribuição por status - ESTILO LUIS IMÓVEIS"""
    if df.empty or 'status' not in df.columns:
        return
    
    status_count = df['status'].value_counts()
    
    # Cores do tema Luis Imóveis
    cores_status = {
        'RESOLVED': CORES_TEMA['verde'],
        'UNRESOLVED': CORES_TEMA['laranja'], 
        'HUMAN_REQUESTED': CORES_TEMA['vermelho'],
        'UNKNOWN': CORES_TEMA['cinza']
    }
    
    colors = [cores_status.get(status, CORES_TEMA['cinza']) for status in status_count.index]
    
    fig = px.pie(
        values=status_count.values,
        names=status_count.index,
        title="Distribuição por Status de Atendimento",
        color_discrete_sequence=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

def create_channel_analysis(df):
    """Análise por canal - ESTILO LUIS IMÓVEIS"""
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
    
    if not canal_stats.empty:
        # Gráfico de barras simples (estilo Luis Imóveis)
        fig = px.bar(
            canal_stats,
            x='channel',
            y=['Total', 'Resolvidos'],
            title="Performance por Canal de Atendimento",
            barmode='group',
            color_discrete_sequence=[CORES_TEMA['azul'], CORES_TEMA['verde']],
            text_auto=True
        )
        
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada com performance
        st.subheader("Detalhes por Canal")
        canal_stats['Performance'] = canal_stats['Taxa_Resolução'].apply(
            lambda x: '🔥 Excelente' if x >= 90 else '👍 Boa' if x >= 70 else '⚠️ Regular' if x >= 50 else '🔴 Baixa'
        )
        
        st.dataframe(canal_stats, use_container_width=True)

def create_timeline_analysis(df):
    """Análise de evolução temporal - ESTILO LUIS IMÓVEIS"""
    if df.empty or 'created_at' not in df.columns or df['created_at'].isna().all():
        return
    
    # Agrupa por dia
    df_daily = df.set_index('created_at').resample('D').agg({
        'conversation_id': 'count',
        'is_resolved': 'sum'
    }).reset_index()
    
    df_daily.columns = ['Data', 'Total_Conversas', 'Resolvidas']
    df_daily = df_daily[df_daily['Total_Conversas'] > 0]
    
    if df_daily.empty:
        st.warning("Dados insuficientes para análise temporal")
        return
    
    # Calcular média móvel se tiver dados suficientes
    if len(df_daily) >= 3:
        df_daily['Media_Movel'] = df_daily['Total_Conversas'].rolling(window=3, center=True).mean()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Total de conversas
    fig.add_trace(
        go.Scatter(
            x=df_daily['Data'],
            y=df_daily['Total_Conversas'],
            mode='lines+markers',
            name='Total Conversas',
            line=dict(color=CORES_TEMA['azul'], width=3),
            hovertemplate='<b>%{x}</b><br>Total: %{y}<extra></extra>'
        ),
        secondary_y=False,
    )
    
    # Conversas resolvidas
    fig.add_trace(
        go.Scatter(
            x=df_daily['Data'],
            y=df_daily['Resolvidas'],
            mode='lines+markers',
            name='Resolvidas',
            line=dict(color=CORES_TEMA['verde'], width=2),
            hovertemplate='<b>%{x}</b><br>Resolvidas: %{y}<extra></extra>'
        ),
        secondary_y=False,
    )
    
    # Média móvel (se disponível)
    if 'Media_Movel' in df_daily.columns:
        fig.add_trace(
            go.Scatter(
                x=df_daily['Data'],
                y=df_daily['Media_Movel'],
                mode='lines',
                name='Tendência (3 dias)',
                line=dict(color=CORES_TEMA['laranja'], width=1, dash='dash'),
                hovertemplate='<b>%{x}</b><br>Média: %{y:.1f}<extra></extra>'
            ),
            secondary_y=False,
        )
    
    fig.update_xaxes(title_text="Data")
    fig.update_yaxes(title_text="Número de Conversas", secondary_y=False)
    fig.update_layout(
        title_text="Evolução de Conversas ao Longo do Tempo",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_sentiment_analysis(df):
    """Análise de sentimento - ESTILO LUIS IMÓVEIS"""
    if df.empty or 'context_sentiment' not in df.columns:
        st.info("📊 Análise de sentimento não disponível nos dados atuais")
        return
    
    sentiment_count = df['sentiment_pt'].value_counts()
    
    # Cores para sentimento
    cores_sentimento = {
        'Positivo': CORES_TEMA['verde'],
        'Neutro': CORES_TEMA['cinza'],
        'Negativo': CORES_TEMA['vermelho']
    }
    
    colors = [cores_sentimento.get(sent, CORES_TEMA['cinza']) for sent in sentiment_count.index]
    
    fig = px.pie(
        values=sentiment_count.values,
        names=sentiment_count.index,
        title="Análise de Sentimento (IA)",
        color_discrete_sequence=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

def create_product_mentions_analysis(df):
    """Análise de menções de produto - ESTILO LUIS IMÓVEIS"""
    if df.empty or 'mentions_product' not in df.columns:
        return
    
    # Estatísticas de menções
    mencoes_stats = df.groupby(['mentions_product', 'mentions_price']).size().reset_index(name='Quantidade')
    mencoes_stats['Categoria'] = mencoes_stats.apply(
        lambda x: 'Produto + Preço' if x['mentions_product'] and x['mentions_price'] 
                 else 'Apenas Produto' if x['mentions_product'] 
                 else 'Apenas Preço' if x['mentions_price'] 
                 else 'Sem Menções', axis=1
    )
    
    categoria_count = mencoes_stats.groupby('Categoria')['Quantidade'].sum()
    
    fig = px.bar(
        x=categoria_count.index,
        y=categoria_count.values,
        title="Análise de Menções (IA)",
        color=categoria_count.values,
        color_continuous_scale='Blues',
        text=categoria_count.values
    )
    
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def create_commercial_analysis(df):
    """Análise comercial com dados ricos"""
    if df.empty:
        return
    
    st.subheader("💼 Análise Comercial")
    
    # Verificar se temos dados comerciais
    has_price_data = 'var_preco' in df.columns and df['var_preco'].sum() > 0
    has_product_data = 'quantidade_pneus' in df.columns and df['quantidade_pneus'].sum() > 0
    
    if has_price_data or has_product_data:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if has_price_data:
                valor_total = df['var_preco'].sum()
                st.metric("💰 Valor Total Mencionado", f"R$ {valor_total:,.0f}")
            else:
                st.metric("💰 Valor Total", "N/A")
                
        with col2:
            if has_price_data:
                conversas_com_preco = (df['var_preco'] > 0).sum()
                st.metric("💵 Conversas com Preço", f"{conversas_com_preco}")
            else:
                st.metric("💵 Conversas com Preço", "0")
                
        with col3:
            if has_product_data:
                pneus_total = df['quantidade_pneus'].sum()
                st.metric("🛞 Total Pneus Solicitados", f"{pneus_total:.0f}")
            else:
                st.metric("🛞 Total Pneus", "N/A")
                
        with col4:
            if has_price_data:
                conversas_preco = df[df['var_preco'] > 0]
                if len(conversas_preco) > 0:
                    ticket_medio = conversas_preco['var_preco'].mean()
                    st.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.0f}")
                else:
                    st.metric("🎯 Ticket Médio", "R$ 0")
            else:
                st.metric("🎯 Ticket Médio", "N/A")
        
        # Análise de produtos mais mencionados
        if has_product_data and 'modelo_pneu' in df.columns:
            modelos_count = df[df['modelo_pneu'] != '']['modelo_pneu'].value_counts().head(5)
            if not modelos_count.empty:
                st.subheader("🏆 Top 5 Modelos de Pneus Mencionados")
                
                fig = px.bar(
                    x=modelos_count.values,
                    y=modelos_count.index,
                    orientation='h',
                    title="Modelos Mais Procurados",
                    color=modelos_count.values,
                    color_continuous_scale='viridis',
                    text=modelos_count.values
                )
                
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Dados comerciais não disponíveis na fonte atual")

def create_hourly_analysis(df):
    """Análise por horário - ESTILO LUIS IMÓVEIS"""
    if df.empty or 'created_at' not in df.columns or df['created_at'].isna().all():
        return
    
    df_hourly = df.copy()
    df_hourly['Hora'] = df_hourly['created_at'].dt.hour
    
    hourly_stats = df_hourly.groupby('Hora').agg({
        'conversation_id': 'count',
        'is_resolved': 'sum'
    }).reset_index()
    
    hourly_stats.columns = ['Hora', 'Total', 'Resolvidas']
    hourly_stats['Taxa_Resolução'] = (
        hourly_stats['Resolvidas'] / hourly_stats['Total'] * 100
    ).round(1)
    
    # Identificar horários de pico
    if len(hourly_stats) > 0:
        pico_conversas = hourly_stats['Total'].max()
        horarios_pico = hourly_stats[hourly_stats['Total'] == pico_conversas]['Hora'].tolist()
        
        fig = px.line(
            hourly_stats,
            x='Hora',
            y=['Total', 'Resolvidas'],
            title=f"Distribuição por Horário (Pico: {pico_conversas} conversas às {', '.join(map(str, horarios_pico))}h)",
            markers=True,
            color_discrete_sequence=[CORES_TEMA['azul'], CORES_TEMA['verde']]
        )
        
        fig.update_layout(height=400, xaxis_tickmode='linear')
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights dos melhores horários
        if len(hourly_stats) > 0:
            melhor_horario = hourly_stats.loc[hourly_stats['Taxa_Resolução'].idxmax()]
            st.info(f"💡 **Melhor horário para resolução**: {melhor_horario['Hora']}:00h com {melhor_horario['Taxa_Resolução']:.1f}% de resolução")

def main():
    """Função principal do dashboard - ESTILO LUIS IMÓVEIS"""
    
    # Header limpo (igual Luis Imóveis)
    st.title("🚀 Dashboard Reach IA")
    st.subheader("Sistema Expandido de Análise de Conversas - v2.1")
    
    # Sidebar com filtros (igual Luis Imóveis)
    st.sidebar.title("🎛️ Filtros")
    
    # Carregamento de dados
    with st.spinner("Carregando dados da planilha..."):
        conversas_df, contatos_df = get_rich_data_from_sheets()
        df = process_rich_data(conversas_df, contatos_df)
    
    if df.empty:
        st.error("Não foi possível carregar os dados da planilha")
        st.stop()
    
    # Filtros na sidebar
    # Filtro por canal
    canais_disponiveis = ['Todos'] + list(df['channel'].unique()) if 'channel' in df.columns else ['Todos']
    canal_selecionado = st.sidebar.selectbox("Filtrar por Canal:", canais_disponiveis)
    
    # Filtro por status
    status_disponiveis = ['Todos'] + list(df['status'].unique()) if 'status' in df.columns else ['Todos']
    status_selecionado = st.sidebar.selectbox("Filtrar por Status:", status_disponiveis)
    
    # Filtro de período
    if not df['created_at'].isna().all():
        data_min = df['created_at'].min().date()
        data_max = df['created_at'].max().date()
        
        periodo_padrao_inicio = max(data_min, data_max - timedelta(days=30))
        
        periodo = st.sidebar.date_input(
            "Período:",
            value=(periodo_padrao_inicio, data_max),
            min_value=data_min,
            max_value=data_max
        )
        
        # Aplicar filtro de período
        if len(periodo) == 2:
            mask = (df['created_at'].dt.date >= periodo[0]) & (df['created_at'].dt.date <= periodo[1])
            df = df[mask]
    
    # Filtro de sentimento (se disponível)
    if 'context_sentiment' in df.columns:
        sentimentos_disponiveis = ['Todos'] + list(df['sentiment_pt'].unique())
        sentimento_selecionado = st.sidebar.selectbox("Filtrar por Sentimento:", sentimentos_disponiveis)
        if sentimento_selecionado != 'Todos':
            df = df[df['sentiment_pt'] == sentimento_selecionado]
    
    # Aplicar filtros
    if canal_selecionado != 'Todos':
        df = df[df['channel'] == canal_selecionado]
    
    if status_selecionado != 'Todos':
        df = df[df['status'] == status_selecionado]
    
    # Status do sistema
    st.success(f"✅ Sistema funcionando - {len(df)} conversas encontradas")
    
    # Cards de métricas
    create_metrics_cards(df)
    
    # Layout em colunas (igual Luis Imóveis)
    col1, col2 = st.columns(2)
    
    with col1:
        create_status_distribution_chart(df)
        create_timeline_analysis(df)
    
    with col2:
        create_channel_analysis(df)
        create_sentiment_analysis(df)
    
    # Análise por horário
    st.subheader("⏰ Análise por Horário")
    create_hourly_analysis(df)
    
    # Análise de menções IA
    st.subheader("🧠 Análise de Menções (IA)")
    create_product_mentions_analysis(df)
    
    # Análise comercial
    create_commercial_analysis(df)
    
    # Tabela de dados detalhados
    st.subheader("📋 Dados Detalhados")
    
    if not df.empty:
        # Preparar colunas para exibição
        colunas_exibir = [
            'conversation_id', 'created_at', 'status', 'channel', 'priority',
            'satisfaction_score', 'context_sentiment', 'var_preco', 'quantidade_pneus'
        ]
        
        colunas_disponiveis = [col for col in colunas_exibir if col in df.columns]
        df_display = df[colunas_disponiveis].copy()
        
        # Formatar dados para exibição
        if 'created_at' in df_display.columns and not df_display['created_at'].isna().all():
            df_display['created_at'] = df_display['created_at'].dt.strftime('%d/%m/%Y %H:%M')
        
        if 'var_preco' in df_display.columns:
            df_display['var_preco'] = df_display['var_preco'].apply(
                lambda x: f"R$ {x:,.0f}" if x > 0 else "-"
            )
        
        # Mostrar número de registros
        st.info(f"📊 Mostrando {len(df_display)} registros filtrados")
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Botão de download
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f'reach_ia_conversas_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
            mime='text/csv'
        )
    
    # Footer (igual Luis Imóveis)
    st.markdown("---")
    st.markdown(
        f"**Sistema Expandido v2.1** | "
        f"Última atualização: {datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')} | "
        f"Dados em tempo real da planilha Google | "
        f"🔄 Cache de 5 minutos"
    )

if __name__ == "__main__":
    main()
