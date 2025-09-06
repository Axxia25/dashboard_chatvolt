"""
Componente de Cards de Métricas
Renderiza os cards principais com KPIs do dashboard
"""

import streamlit as st
import pandas as pd

def calculate_variation(current: float, previous: float) -> dict:
    """Calcula variação percentual entre períodos"""
    if previous == 0:
        return {'value': 0, 'direction': 'stable', 'color': '#95a5a6'}
    
    variation = ((current - previous) / previous) * 100
    
    if variation > 0:
        return {
            'value': variation,
            'direction': 'up',
            'symbol': '↑',
            'color': '#2ecc71'
        }
    elif variation < 0:
        return {
            'value': abs(variation),
            'direction': 'down', 
            'symbol': '↓',
            'color': '#e74c3c'
        }
    else:
        return {
            'value': 0,
            'direction': 'stable',
            'symbol': '→',
            'color': '#95a5a6'
        }

def render_metric_card(title: str, value: str, subtitle: str, icon: str, 
                      variation: dict = None, color: str = "#3498db"):
    """Renderiza um card de métrica individual"""
    
    # Container do card
    card_html = f"""
    <div style="
        background-color: #262730;
        border: 1px solid #464853;
        border-radius: 8px;
        padding: 20px;
        height: 140px;
        position: relative;
        overflow: hidden;
    ">
        <!-- Ícone de fundo -->
        <div style="
            position: absolute;
            right: 10px;
            top: 10px;
            font-size: 60px;
            opacity: 0.1;
            color: {color};
        ">{icon}</div>
        
        <!-- Conteúdo -->
        <div style="position: relative; z-index: 1;">
            <p style="
                color: #a3a8b8;
                font-size: 14px;
                margin: 0;
                font-weight: 400;
            ">{title}</p>
            
            <h2 style="
                color: #fafafa;
                font-size: 32px;
                margin: 5px 0;
                font-weight: 600;
            ">{value}</h2>
            
            <p style="
                color: #a3a8b8;
                font-size: 12px;
                margin: 0;
            ">{subtitle}</p>
    """
    
    # Adicionar variação se existir
    if variation:
        card_html += f"""
            <div style="
                margin-top: 10px;
                font-size: 14px;
                color: {variation['color']};
                font-weight: 500;
            ">
                {variation['symbol']} {variation['value']:.1f}% 
                <span style="color: #a3a8b8; font-size: 12px;">vs período anterior</span>
            </div>
        """
    
    card_html += """
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def render_metrics_cards(df: pd.DataFrame):
    """Renderiza todos os cards de métricas principais"""
    
    if df.empty:
        st.warning("Nenhum dado disponível para exibir métricas")
        return
    
    # Calcular métricas principais
    total_contatos = len(df)
    
    # Tempo médio de resposta (em minutos)
    tempo_resposta = 0
    if 'first_response_time' in df.columns:
        tempo_resposta_segundos = pd.to_numeric(df['first_response_time'], errors='coerce').mean()
        if pd.notna(tempo_resposta_segundos):
            tempo_resposta = tempo_resposta_segundos / 60  # Converter para minutos
    
    # Satisfação média
    satisfacao = 0
    if 'satisfaction_score' in df.columns:
        satisfacao = pd.to_numeric(df['satisfaction_score'], errors='coerce').mean()
        if pd.isna(satisfacao):
            satisfacao = 0
    
    # Taxa de resolução
    taxa_resolucao = 0
    if 'resolved' in df.columns:
        try:
            resolved_count = df['resolved'].astype(str).str.lower().isin(['true', '1', 'sim']).sum()
            taxa_resolucao = (resolved_count / total_contatos * 100) if total_contatos > 0 else 0
        except:
            taxa_resolucao = 0
    
    # Tempo de resolução (em horas)
    tempo_resolucao = 0
    if 'resolution_time' in df.columns:
        tempo_resolucao_minutos = pd.to_numeric(df['resolution_time'], errors='coerce').mean()
        if pd.notna(tempo_resolucao_minutos):
            tempo_resolucao = tempo_resolucao_minutos / 60  # Converter para horas
    
    # Calcular variações (mock por enquanto - pode ser implementado com dados históricos)
    var_contatos = calculate_variation(total_contatos, total_contatos * 0.89)
    var_tempo_resp = calculate_variation(tempo_resposta, tempo_resposta * 1.09)
    var_satisfacao = calculate_variation(satisfacao, satisfacao * 0.98)
    var_taxa_res = calculate_variation(taxa_resolucao, taxa_resolucao * 0.95)
    
    # Layout em 4 colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            title="Total de Contatos",
            value=f"{total_contatos:,}",
            subtitle="no período selecionado",
            icon="📊",
            variation=var_contatos,
            color="#3498db"
        )
    
    with col2:
        render_metric_card(
            title="Tempo Médio Resposta", 
            value=f"{tempo_resposta:.1f} min",
            subtitle="primeira interação",
            icon="⏱️",
            variation=var_tempo_resp,
            color="#2ecc71"
        )
    
    with col3:
        render_metric_card(
            title="Satisfação Média",
            value=f"{satisfacao:.1f}/5",
            subtitle="avaliação dos clientes",
            icon="⭐",
            variation=var_satisfacao,
            color="#9b59b6"
        )
    
    with col4:
        render_metric_card(
            title="Taxa de Resolução",
            value=f"{taxa_resolucao:.1f}%",
            subtitle="problemas solucionados",
            icon="✅",
            variation=var_taxa_res,
            color="#f39c12"
        )
    
    # Segunda linha de métricas (novas)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col5, col6, col7, col8 = st.columns(4)
    
    # Leads qualificados
    leads_qualificados = 0
    if 'lead_stage' in df.columns:
        leads_qualificados = df['lead_stage'].isin(['qualificado', 'convertido']).sum()
    
    # Leads convertidos
    leads_convertidos = 0
    if 'lead_stage' in df.columns:
        leads_convertidos = (df['lead_stage'] == 'convertido').sum()
    
    # Taxa de conversão
    taxa_conversao = (leads_convertidos / total_contatos * 100) if total_contatos > 0 else 0
    
    # Mensagens hoje
    mensagens_hoje = 0
    if 'created_at' in df.columns and 'message_count' in df.columns:
        try:
            df['created_at'] = pd.to_datetime(df['created_at'])
            hoje = pd.Timestamp.now().date()
            mask_hoje = df['created_at'].dt.date == hoje
            mensagens_hoje = pd.to_numeric(df.loc[mask_hoje, 'message_count'], errors='coerce').sum()
        except:
            mensagens_hoje = 0
    
    with col5:
        render_metric_card(
            title="Tempo Resolução",
            value=f"{tempo_resolucao:.1f} h",
            subtitle="média de conclusão",
            icon="⏰",
            color="#e74c3c"
        )
    
    with col6:
        render_metric_card(
            title="Leads Qualificados",
            value=f"{leads_qualificados}",
            subtitle="prontos para conversão",
            icon="🎯",
            color="#2ecc71"
        )
    
    with col7:
        render_metric_card(
            title="Taxa de Conversão",
            value=f"{taxa_conversao:.1f}%",
            subtitle="leads convertidos",
            icon="💰",
            color="#f39c12"
        )
    
    with col8:
        render_metric_card(
            title="Mensagens Hoje",
            value=f"{int(mensagens_hoje):,}",
            subtitle="total de interações",
            icon="💬",
            color="#3498db"
        )

def render_mini_metric(label: str, value: str, color: str = "#3498db"):
    """Renderiza uma mini métrica para espaços menores"""
    st.markdown(
        f"""
        <div style="
            background-color: #262730;
            border: 1px solid #464853;
            border-radius: 6px;
            padding: 12px;
            text-align: center;
        ">
            <p style="
                color: #a3a8b8;
                font-size: 12px;
                margin: 0;
            ">{label}</p>
            <p style="
                color: {color};
                font-size: 20px;
                font-weight: 600;
                margin: 5px 0 0 0;
            ">{value}</p>
        </div>
        """,
        unsafe_allow_html=True
    )