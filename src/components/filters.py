"""
Componente de Filtros da Sidebar
Gerencia todos os filtros disponíveis no dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date

def render_sidebar_filters() -> dict:
    """
    Renderiza todos os filtros na sidebar
    
    Returns:
        Dict com todos os filtros selecionados
    """
    st.sidebar.title("🔍 Filtros")
    
    filters = {}
    
    # Filtro de período
    st.sidebar.subheader("📅 Período")
    
    # Opções rápidas de período
    period_option = st.sidebar.radio(
        "Selecione o período:",
        ["Últimos 7 dias", "Últimos 30 dias", "Este mês", "Personalizado"],
        index=1
    )
    
    today = date.today()
    
    if period_option == "Últimos 7 dias":
        filters['date_start'] = today - timedelta(days=7)
        filters['date_end'] = today
    elif period_option == "Últimos 30 dias":
        filters['date_start'] = today - timedelta(days=30)
        filters['date_end'] = today
    elif period_option == "Este mês":
        filters['date_start'] = today.replace(day=1)
        filters['date_end'] = today
    else:  # Personalizado
        col1, col2 = st.sidebar.columns(2)
        with col1:
            filters['date_start'] = st.date_input(
                "De:",
                value=today - timedelta(days=30),
                max_value=today
            )
        with col2:
            filters['date_end'] = st.date_input(
                "Até:",
                value=today,
                max_value=today
            )
    
    # Separador
    st.sidebar.markdown("---")
    
    # Filtro de canal
    st.sidebar.subheader("💬 Canal")
    
    # Carregar opções disponíveis do cache se existir
    available_channels = ['Todos', 'WhatsApp', 'Email', 'Telefone', 'Chat Online', 'Dashboard']
    
    if 'df_cache' in st.session_state and not st.session_state.df_cache.empty:
        df = st.session_state.df_cache
        if 'channel' in df.columns:
            unique_channels = df['channel'].dropna().unique().tolist()
            available_channels = ['Todos'] + sorted(unique_channels)
    
    filters['channel'] = st.sidebar.selectbox(
        "Selecione o canal:",
        available_channels,
        index=0
    )
    
    # Filtro de status
    st.sidebar.subheader("📊 Status")
    
    available_status = ['Todos', 'Resolvido', 'Não Resolvido', 'Requer Humano']
    
    if 'df_cache' in st.session_state and not st.session_state.df_cache.empty:
        df = st.session_state.df_cache
        if 'status' in df.columns:
            unique_status = df['status'].dropna().unique().tolist()
            available_status = ['Todos'] + sorted(unique_status)
    
    filters['status'] = st.sidebar.selectbox(
        "Status do atendimento:",
        available_status,
        index=0
    )
    
    # Filtro de lead stage (novo)
    st.sidebar.subheader("🎯 Estágio do Lead")
    
    available_stages = ['Todos', 'Novo', 'Qualificado', 'Convertido', 'Perdido']
    
    if 'df_cache' in st.session_state and not st.session_state.df_cache.empty:
        df = st.session_state.df_cache
        if 'lead_stage' in df.columns:
            unique_stages = df['lead_stage'].dropna().unique().tolist()
            available_stages = ['Todos'] + sorted(unique_stages)
    
    filters['lead_stage'] = st.sidebar.selectbox(
        "Estágio no funil:",
        available_stages,
        index=0
    )
    
    # Filtro de satisfação
    st.sidebar.subheader("⭐ Satisfação")
    
    satisfaction_option = st.sidebar.radio(
        "Filtrar por satisfação:",
        ["Todos", "Alta (4-5)", "Média (3)", "Baixa (1-2)"],
        index=0
    )
    
    filters['satisfaction'] = satisfaction_option
    
    # Separador
    st.sidebar.markdown("---")
    
    # Filtros avançados (expansível)
    with st.sidebar.expander("🔧 Filtros Avançados"):
        # Filtro de agente
        available_agents = ['Todos']
        
        if 'df_cache' in st.session_state and not st.session_state.df_cache.empty:
            df = st.session_state.df_cache
            if 'agent_id' in df.columns:
                unique_agents = df['agent_id'].dropna().unique().tolist()
                available_agents = ['Todos'] + sorted(unique_agents)
        
        filters['agent'] = st.selectbox(
            "Atendente:",
            available_agents,
            index=0
        )
        
        # Filtro de tempo de resposta
        filters['response_time_max'] = st.slider(
            "Tempo máx. resposta (min):",
            min_value=0,
            max_value=60,
            value=60,
            step=5
        )
        
        # Filtro de mensagens
        filters['min_messages'] = st.number_input(
            "Mín. mensagens:",
            min_value=0,
            max_value=100,
            value=0,
            step=1
        )
        
        # Filtro de frustração
        filters['max_frustration'] = st.slider(
            "Nível máx. frustração:",
            min_value=0,
            max_value=5,
            value=5
        )
    
    # Separador
    st.sidebar.markdown("---")
    
    # Opções de atualização
    st.sidebar.subheader("🔄 Atualização")
    
    # Auto-refresh
    filters['auto_refresh'] = st.sidebar.checkbox(
        "Auto-atualizar (30s)",
        value=False,
        help="Atualiza automaticamente os dados a cada 30 segundos"
    )
    
    # Botão de atualização manual
    if st.sidebar.button("🔄 Atualizar Agora", use_container_width=True):
        # Limpar cache
        st.cache_data.clear()
        if 'df_cache' in st.session_state:
            del st.session_state['df_cache']
        st.rerun()
    
    # Informações do filtro
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Informações")
    
    # Mostrar período selecionado
    st.sidebar.info(
        f"**Período:** {filters['date_start']} a {filters['date_end']}\n\n"
        f"**Dias:** {(filters['date_end'] - filters['date_start']).days + 1}"
    )
    
    return filters

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Aplica filtros ao DataFrame
    
    Args:
        df: DataFrame original
        filters: Dict com filtros selecionados
        
    Returns:
        DataFrame filtrado
    """
    if df.empty:
        return df
    
    df_filtered = df.copy()
    
    # Filtro de data
    if 'created_at' in df_filtered.columns and 'date_start' in filters and 'date_end' in filters:
        try:
            df_filtered['created_at'] = pd.to_datetime(df_filtered['created_at'])
            mask = (df_filtered['created_at'].dt.date >= filters['date_start']) & \
                   (df_filtered['created_at'].dt.date <= filters['date_end'])
            df_filtered = df_filtered[mask]
        except:
            st.warning("⚠️ Erro ao filtrar por data")
    
    # Filtro de canal
    if filters.get('channel') and filters['channel'] != 'Todos' and 'channel' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['channel'] == filters['channel']]
    
    # Filtro de status
    if filters.get('status') and filters['status'] != 'Todos' and 'status' in df_filtered.columns:
        # Mapear status amigáveis para valores reais
        status_map = {
            'Resolvido': 'RESOLVED',
            'Não Resolvido': 'UNRESOLVED',
            'Requer Humano': 'HUMAN_REQUESTED'
        }
        status_value = status_map.get(filters['status'], filters['status'])
        df_filtered = df_filtered[df_filtered['status'] == status_value]
    
    # Filtro de lead stage
    if filters.get('lead_stage') and filters['lead_stage'] != 'Todos' and 'lead_stage' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['lead_stage'] == filters['lead_stage'].lower()]
    
    # Filtro de satisfação
    if filters.get('satisfaction') and filters['satisfaction'] != 'Todos' and 'satisfaction_score' in df_filtered.columns:
        try:
            df_filtered['satisfaction_score'] = pd.to_numeric(df_filtered['satisfaction_score'], errors='coerce')
            
            if filters['satisfaction'] == 'Alta (4-5)':
                df_filtered = df_filtered[df_filtered['satisfaction_score'] >= 4]
            elif filters['satisfaction'] == 'Média (3)':
                df_filtered = df_filtered[df_filtered['satisfaction_score'] == 3]
            elif filters['satisfaction'] == 'Baixa (1-2)':
                df_filtered = df_filtered[df_filtered['satisfaction_score'] <= 2]
        except:
            st.warning("⚠️ Erro ao filtrar por satisfação")
    
    # Filtros avançados
    
    # Filtro de agente
    if filters.get('agent') and filters['agent'] != 'Todos' and 'agent_id' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['agent_id'] == filters['agent']]
    
    # Filtro de tempo de resposta
    if 'response_time_max' in filters and 'first_response_time' in df_filtered.columns:
        try:
            df_filtered['first_response_time'] = pd.to_numeric(df_filtered['first_response_time'], errors='coerce')
            # Converter segundos para minutos
            df_filtered = df_filtered[df_filtered['first_response_time'] <= filters['response_time_max'] * 60]
        except:
            pass
    
    # Filtro de mensagens mínimas
    if 'min_messages' in filters and filters['min_messages'] > 0 and 'message_count' in df_filtered.columns:
        try:
            df_filtered['message_count'] = pd.to_numeric(df_filtered['message_count'], errors='coerce')
            df_filtered = df_filtered[df_filtered['message_count'] >= filters['min_messages']]
        except:
            pass
    
    # Filtro de frustração
    if 'max_frustration' in filters and 'frustration_level' in df_filtered.columns:
        try:
            df_filtered['frustration_level'] = pd.to_numeric(df_filtered['frustration_level'], errors='coerce')
            df_filtered = df_filtered[df_filtered['frustration_level'] <= filters['max_frustration']]
        except:
            pass
    
    return df_filtered

def get_filter_summary(filters: dict) -> str:
    """
    Retorna um resumo dos filtros aplicados
    
    Args:
        filters: Dict com filtros
        
    Returns:
        String com resumo dos filtros
    """
    summary_parts = []
    
    # Período
    if 'date_start' in filters and 'date_end' in filters:
        summary_parts.append(f"Período: {filters['date_start']} a {filters['date_end']}")
    
    # Canal
    if filters.get('channel') and filters['channel'] != 'Todos':
        summary_parts.append(f"Canal: {filters['channel']}")
    
    # Status
    if filters.get('status') and filters['status'] != 'Todos':
        summary_parts.append(f"Status: {filters['status']}")
    
    # Lead stage
    if filters.get('lead_stage') and filters['lead_stage'] != 'Todos':
        summary_parts.append(f"Lead: {filters['lead_stage']}")
    
    # Satisfação
    if filters.get('satisfaction') and filters['satisfaction'] != 'Todos':
        summary_parts.append(f"Satisfação: {filters['satisfaction']}")
    
    return " | ".join(summary_parts) if summary_parts else "Todos os dados"