"""
DASHBOARD REACH IA - ANÁLISE INTELIGENTE DE CONVERSAS
Visual dark Luis Imóveis + Correção de erros de conversão
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

# Aplicar CSS para visual dark (igual imagem Luis Imóveis)
st.markdown("""
<style>
/* Tema escuro igual Luis Imóveis */
.stApp {
    background-color: #0e1117;
    color: #fafafa;
}

.main .block-container {
    background-color: #0e1117;
    padding-top: 1rem;
}

/* Header */
h1 {
    color: #fafafa !important;
    font-weight: 600;
}

h2, h3 {
    color: #fafafa !important;
}

/* Métricas */
[data-testid="metric-container"] {
    background-color: #262730;
    border: 1px solid #464853;
    padding: 1rem;
    border-radius: 0.5rem;
    color: #fafafa;
}

[data-testid="metric-container"] > div {
    color: #fafafa !important;
}

[data-testid="metric-container"] [data-testid="metric-value"] {
    color: #fafafa !important;
}

[data-testid="metric-container"] [data-testid="metric-label"] {
    color: #a3a8b8 !important;
}

/* Sidebar */
.css-1d391kg {
    background-color: #262730;
}

.css-1d391kg .css-10trblm {
    color: #fafafa;
}

/* Gráficos */
.js-plotly-plot {
    background-color: #262730 !important;
}

/* Dataframe */
.stDataFrame {
    background-color: #262730;
}

/* Alertas */
.stAlert {
    background-color: #262730;
    border: 1px solid #464853;
    color: #fafafa;
}

.stSuccess {
    background-color: #1e4d3f;
    border-color: #2ecc71;
    color: #fafafa;
}

.stError {
    background-color: #4d1e1e;
    border-color: #e74c3c;
    color: #fafafa;
}

.stInfo {
    background-color: #1e3a5f;
    border-color: #3498db;
    color: #fafafa;
}

.stWarning {
    background-color: #5f4a1e;
    border-color: #f39c12;
    color: #fafafa;
}

/* Selectbox e inputs */
.stSelectbox > div > div {
    background-color: #262730;
    color: #fafafa;
    border-color: #464853;
}

.stDateInput > div > div {
    background-color: #262730;
    color: #fafafa;
    border-color: #464853;
}

/* Botões */
.stButton > button {
    background-color: #3498db;
    color: #fafafa;
    border: none;
}

.stButton > button:hover {
    background-color: #2980b9;
}

/* Download button */
.stDownloadButton > button {
    background-color: #27ae60;
    color: #fafafa;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# Configurações
CHATVOLT_API_BASE = "https://api.chatvolt.ai"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
PLANILHA_ID = "1Ji8hgGiQanGKMqblxRzkA_E_sLoI6AnpapmU72nXHsA"

# Cores do tema (cores vibrantes para fundo escuro)
CORES_TEMA = {
    'azul': '#3498db',
    'verde': '#2ecc71', 
    'laranja': '#f39c12',
    'vermelho': '#e74c3c',
    'roxo': '#9b59b6',
    'cinza': '#95a5a6'
}

def safe_numeric_conversion(series, default_value=0):
    """Converte série para numérico de forma segura"""
    try:
        # Tentar conversão direta
        numeric_series = pd.to_numeric(series, errors='coerce')
        # Substituir NaN por valor padrão
        return numeric_series.fillna(default_value)
    except Exception:
        # Se falhar completamente, retornar série com valor padrão
        return pd.Series([default_value] * len(series))

def safe_get_column(df, column_name, default_value=None, numeric=False):
    """Retorna coluna do DataFrame de forma segura"""
    if column_name in df.columns:
        if numeric:
            return safe_numeric_conversion(df[column_name], default_value or 0)
        else:
            return df[column_name]
    else:
        if df.empty:
            return pd.Series(dtype='object')
        default_val = default_value if default_value is not None else (0 if numeric else '')
        return pd.Series([default_val] * len(df))

@st.cache_data(ttl=300)  # Cache por 5 minutos
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
                rows = [row for row in conversas_data[1:] if any(cell.strip() for cell in row if cell)]
                if rows:
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
    """Processa e enriquece os dados de forma segura"""
    
    if not contatos_df.empty:
        df = contatos_df.copy()
        st.info("📊 Usando dados enriquecidos da aba Contatos")
    elif not conversas_df.empty:
        df = conversas_df.copy()
        st.info("📊 Usando dados básicos da aba Conversas")
    else:
        st.warning("⚠️ Nenhum dado encontrado em ambas as abas")
        return pd.DataFrame()
    
    # Processar campos essenciais de forma defensiva
    essential_fields = {
        'conversation_id': ('string', ''),
        'created_at': ('datetime', None),
        'status': ('string', 'UNKNOWN'),
        'channel': ('string', 'unknown'),
        'priority': ('string', 'MEDIUM'),
        'frustration_level': ('numeric', 0),
        'first_response_time': ('numeric', 0),
        'resolution_time': ('numeric', 0),
        'satisfaction_score': ('numeric', 0),
        'context_sentiment': ('string', 'neutral'),
        'mentions_product': ('boolean', False),
        'mentions_price': ('boolean', False),
        'var_preco': ('numeric', 0),
        'quantidade_pneus': ('numeric', 0),
        'resolved': ('boolean', False),
        'escalated_to_human': ('boolean', False)
    }
    
    for field, (field_type, default_value) in essential_fields.items():
        if field not in df.columns:
            if field_type == 'boolean':
                df[field] = False
            elif field_type == 'numeric':
                df[field] = 0
            else:
                df[field] = default_value
    
    # Processar timestamps de forma segura
    for time_col in ['created_at', 'updated_at']:
        if time_col in df.columns:
            try:
                df[time_col] = pd.to_datetime(df[time_col], errors='coerce', dayfirst=True)
                # Se todas as datas são inválidas, usar data atual
                if df[time_col].isna().all():
                    df[time_col] = datetime.now()
            except:
                df[time_col] = datetime.now()
    
    # Processar campos numéricos de forma SEGURA
    numeric_fields = ['frustration_level', 'first_response_time', 'resolution_time', 
                     'satisfaction_score', 'var_preco', 'quantidade_pneus']
    
    for field in numeric_fields:
        if field in df.columns:
            df[field] = safe_numeric_conversion(df[field], default_value=0)
    
    # Processar campos booleanos de forma segura
    bool_fields = ['mentions_product', 'mentions_price', 'resolved', 'escalated_to_human']
    for field in bool_fields:
        if field in df.columns:
            try:
                df[field] = df[field].astype(str).str.lower().isin(['true', 'sim', 'yes', '1'])
            except:
                df[field] = False
    
    # Processar status
    try:
        df['status'] = df['status'].astype(str).str.upper()
        df['is_resolved'] = df['status'] == 'RESOLVED'
        df['needs_human'] = df['status'] == 'HUMAN_REQUESTED'
    except:
        df['is_resolved'] = False
        df['needs_human'] = False
    
    # Classificar sentimento
    try:
        sentiment_map = {'positive': 'Positivo', 'negative': 'Negativo', 'neutral': 'Neutro'}
        df['sentiment_pt'] = df['context_sentiment'].map(sentiment_map).fillna('Neutro')
    except:
        df['sentiment_pt'] = 'Neutro'
    
    # Filtrar registros válidos
    try:
        df = df[df['conversation_id'].notna() & (df['conversation_id'].astype(str) != '')]
    except:
        pass
    
    return df

def create_metrics_cards(df):
    """Cria cards de métricas principais - VERSÃO CORRIGIDA"""
    if df.empty:
        st.warning("Nenhum dado encontrado")
        return
    
    total_conversas = len(df)
    
    # Usar função segura para obter colunas numéricas
    conversas_resolvidas = safe_get_column(df, 'is_resolved', False).sum()
    taxa_resolucao = (conversas_resolvidas / total_conversas * 100) if total_conversas > 0 else 0
    
    # Métricas de tempo - VERSÃO CORRIGIDA
    tempo_resposta_medio = safe_get_column(df, 'first_response_time', 0, numeric=True).mean()
    tempo_resolucao_medio = safe_get_column(df, 'resolution_time', 0, numeric=True).mean()
    
    # Satisfação média
    satisfacao_media = safe_get_column(df, 'satisfaction_score', 0, numeric=True).mean()
    
    # Escalações para humano
    escalacoes = safe_get_column(df, 'needs_human', False).sum()
    taxa_escalacao = (escalacoes / total_conversas * 100) if total_conversas > 0 else 0
    
    # Análises IA
    sentimento_positivo = 0
    if 'context_sentiment' in df.columns:
        sentimento_positivo = (df['context_sentiment'] == 'positive').sum()
    
    mencoes_produto = safe_get_column(df, 'mentions_product', False).sum()
    
    # Conversas por canal
    canais_stats = {}
    if 'channel' in df.columns:
        try:
            canais_stats = df['channel'].value_counts().to_dict()
        except:
            pass
    
    # Exibir métricas em grid 4x2
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
    """Gráfico de distribuição por status"""
    if df.empty or 'status' not in df.columns:
        return
    
    status_count = df['status'].value_counts()
    
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
    
    # Estilo para fundo escuro
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font_color='white'
    )
    st.plotly_chart(fig, use_container_width=True)

def create_channel_analysis(df):
    """Análise por canal"""
    if df.empty or 'channel' not in df.columns:
        return
    
    try:
        # Usar funções seguras para evitar erros
        canal_data = []
        for channel in df['channel'].unique():
            channel_df = df[df['channel'] == channel]
            total = len(channel_df)
            resolvidos = safe_get_column(channel_df, 'is_resolved', False).sum()
            satisfacao = safe_get_column(channel_df, 'satisfaction_score', 0, numeric=True).mean()
            tempo_resposta = safe_get_column(channel_df, 'first_response_time', 0, numeric=True).mean()
            
            canal_data.append({
                'channel': channel,
                'Total': total,
                'Resolvidos': resolvidos,
                'Satisfação_Média': round(satisfacao, 2),
                'Tempo_Resposta_Médio': round(tempo_resposta, 2),
                'Taxa_Resolução': round((resolvidos / total * 100), 1) if total > 0 else 0
            })
        
        canal_stats = pd.DataFrame(canal_data)
        
        if not canal_stats.empty:
            fig = px.bar(
                canal_stats,
                x='channel',
                y=['Total', 'Resolvidos'],
                title="Performance por Canal de Atendimento",
                barmode='group',
                color_discrete_sequence=[CORES_TEMA['azul'], CORES_TEMA['verde']],
                text_auto=True
            )
            
            # Estilo para fundo escuro
            fig.update_layout(
                height=400,
                xaxis_tickangle=-45,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                title_font_color='white',
                xaxis=dict(color='white', gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(color='white', gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela detalhada
            st.subheader("Detalhes por Canal")
            canal_stats['Performance'] = canal_stats['Taxa_Resolução'].apply(
                lambda x: '🔥 Excelente' if x >= 90 else '👍 Boa' if x >= 70 else '⚠️ Regular' if x >= 50 else '🔴 Baixa'
            )
            st.dataframe(canal_stats, use_container_width=True)
    
    except Exception as e:
        st.error(f"Erro na análise de canais: {e}")

def create_timeline_analysis(df):
    """Análise temporal"""
    if df.empty or 'created_at' not in df.columns or df['created_at'].isna().all():
        return
    
    try:
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
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(
                x=df_daily['Data'],
                y=df_daily['Total_Conversas'],
                mode='lines+markers',
                name='Total Conversas',
                line=dict(color=CORES_TEMA['azul'], width=3)
            ),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(
                x=df_daily['Data'],
                y=df_daily['Resolvidas'],
                mode='lines+markers',
                name='Resolvidas',
                line=dict(color=CORES_TEMA['verde'], width=2)
            ),
            secondary_y=False,
        )
        
        fig.update_layout(
            title_text="Evolução de Conversas ao Longo do Tempo",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font_color='white',
            xaxis=dict(color='white', gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(color='white', gridcolor='rgba(255,255,255,0.1)')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Erro na análise temporal: {e}")

def create_sentiment_analysis(df):
    """Análise de sentimento"""
    if df.empty or 'context_sentiment' not in df.columns:
        st.info("📊 Análise de sentimento não disponível")
        return
    
    try:
        sentiment_count = df['sentiment_pt'].value_counts()
        
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
        
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Erro na análise de sentimento: {e}")

def main():
    """Função principal do dashboard"""
    
    # Header
    st.title("🚀 Dashboard Reach IA")
    st.subheader("Sistema Expandido de Análise de Conversas - v2.1")
    
    # Sidebar
    st.sidebar.title("🎛️ Filtros")
    
    # Carregamento de dados
    with st.spinner("Carregando dados da planilha..."):
        conversas_df, contatos_df = get_rich_data_from_sheets()
        df = process_rich_data(conversas_df, contatos_df)
    
    if df.empty:
        st.error("Não foi possível carregar os dados da planilha")
        st.stop()
    
    # Filtros básicos
    if 'channel' in df.columns:
        canais_disponiveis = ['Todos'] + list(df['channel'].unique())
        canal_selecionado = st.sidebar.selectbox("Filtrar por Canal:", canais_disponiveis)
        if canal_selecionado != 'Todos':
            df = df[df['channel'] == canal_selecionado]
    
    if 'status' in df.columns:
        status_disponiveis = ['Todos'] + list(df['status'].unique())
        status_selecionado = st.sidebar.selectbox("Filtrar por Status:", status_disponiveis)
        if status_selecionado != 'Todos':
            df = df[df['status'] == status_selecionado]
    
    # Status do sistema
    st.success(f"✅ Sistema funcionando - {len(df)} conversas encontradas")
    
    # Cards de métricas
    create_metrics_cards(df)
    
    # Layout em colunas
    col1, col2 = st.columns(2)
    
    with col1:
        create_status_distribution_chart(df)
        create_timeline_analysis(df)
    
    with col2:
        create_channel_analysis(df)
        create_sentiment_analysis(df)
    
    # Tabela de dados
    st.subheader("📋 Dados Detalhados")
    
    if not df.empty:
        colunas_exibir = [
            'conversation_id', 'created_at', 'status', 'channel', 
            'satisfaction_score', 'context_sentiment', 'var_preco'
        ]
        
        colunas_disponiveis = [col for col in colunas_exibir if col in df.columns]
        df_display = df[colunas_disponiveis].copy()
        
        # Formatar dados
        if 'created_at' in df_display.columns:
            try:
                df_display['created_at'] = df_display['created_at'].dt.strftime('%d/%m/%Y %H:%M')
            except:
                pass
        
        if 'var_preco' in df_display.columns:
            try:
                df_display['var_preco'] = df_display['var_preco'].apply(
                    lambda x: f"R$ {x:,.0f}" if pd.notna(x) and x > 0 else "-"
                )
            except:
                pass
        
        st.info(f"📊 Mostrando {len(df_display)} registros")
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Download
        try:
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f'reach_ia_conversas_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv'
            )
        except Exception as e:
            st.error(f"Erro no download: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"**Sistema Expandido v2.1** | "
        f"Última atualização: {datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')} | "
        f"🔄 Cache de 5 minutos"
    )

if __name__ == "__main__":
    main()
