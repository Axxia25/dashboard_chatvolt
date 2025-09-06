"""
Componentes de Gráficos
Todos os gráficos do dashboard incluindo o funil de conversão
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Cores do tema
COLORS = {
    'primary': '#3498db',
    'success': '#2ecc71',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#9b59b6',
    'muted': '#95a5a6',
    'background': '#262730',
    'text': '#fafafa'
}

def apply_dark_theme(fig):
    """Aplica tema escuro aos gráficos Plotly"""
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text']),
        title_font_color=COLORS['text'],
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(255,255,255,0.1)'
        ),
        xaxis=dict(
            color=COLORS['text'],
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            color=COLORS['text'],
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.1)'
        )
    )
    return fig

def render_funnel_chart(df: pd.DataFrame):
    """Renderiza gráfico de funil de conversão de leads"""
    st.subheader("🎯 Funil de Conversão de Leads")
    
    # Verificar se existe coluna lead_stage
    if 'lead_stage' not in df.columns:
        # Simular dados se não existir
        st.info("ℹ️ Configurando análise de funil. Adicione a coluna 'lead_stage' para dados reais.")
        
        # Dados simulados para demonstração
        total_leads = len(df)
        leads_qualificados = int(total_leads * 0.6)
        leads_convertidos = int(total_leads * 0.25)
    else:
        # Usar dados reais
        total_leads = len(df)
        leads_qualificados = df['lead_stage'].isin(['qualificado', 'convertido']).sum()
        leads_convertidos = (df['lead_stage'] == 'convertido').sum()
    
    # Criar dados do funil
    funnel_data = pd.DataFrame({
        'Etapa': ['Leads Novos', 'Leads Qualificados', 'Leads Convertidos'],
        'Quantidade': [total_leads, leads_qualificados, leads_convertidos],
        'Taxa': ['100%', f'{leads_qualificados/total_leads*100:.1f}%' if total_leads > 0 else '0%',
                 f'{leads_convertidos/total_leads*100:.1f}%' if total_leads > 0 else '0%']
    })
    
    # Criar gráfico de funil
    fig = go.Figure(go.Funnel(
        y=funnel_data['Etapa'],
        x=funnel_data['Quantidade'],
        text=funnel_data['Taxa'],
        textposition="inside",
        textinfo="value+percent initial+text",
        opacity=0.9,
        marker=dict(
            color=[COLORS['primary'], COLORS['warning'], COLORS['success']]
        ),
        connector=dict(line=dict(color="rgba(255,255,255,0.2)", width=2))
    ))
    
    fig.update_layout(
        height=400,
        showlegend=False,
        title=dict(
            text="Conversão de Leads no Período",
            font=dict(size=16)
        )
    )
    
    apply_dark_theme(fig)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Métricas do funil
        st.markdown("### 📊 Métricas do Funil")
        
        taxa_qualificacao = (leads_qualificados / total_leads * 100) if total_leads > 0 else 0
        taxa_conversao = (leads_convertidos / total_leads * 100) if total_leads > 0 else 0
        taxa_conv_qualificados = (leads_convertidos / leads_qualificados * 100) if leads_qualificados > 0 else 0
        
        st.metric("Taxa de Qualificação", f"{taxa_qualificacao:.1f}%")
        st.metric("Taxa de Conversão Total", f"{taxa_conversao:.1f}%")
        st.metric("Conversão de Qualificados", f"{taxa_conv_qualificados:.1f}%")
        
        # Insights
        st.markdown("### 💡 Insights")
        if taxa_qualificacao < 50:
            st.warning("⚠️ Taxa de qualificação abaixo de 50%. Revisar critérios de captação.")
        else:
            st.success("✅ Boa taxa de qualificação de leads!")
        
        if taxa_conv_qualificados < 40:
            st.warning("⚠️ Conversão de qualificados pode melhorar. Revisar processo de vendas.")

def render_timeline_chart(df: pd.DataFrame):
    """Renderiza gráfico de evolução temporal"""
    st.subheader("📈 Evolução de Contatos - Dezembro 2024")
    
    if 'created_at' not in df.columns:
        st.warning("Dados de tempo não disponíveis")
        return
    
    try:
        # Garantir datetime
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Agrupar por dia
        daily_stats = df.groupby(df['created_at'].dt.date).agg({
            'conversation_id': 'count',
            'resolved': lambda x: x.astype(str).str.lower().isin(['true', '1', 'sim']).sum()
        }).reset_index()
        
        daily_stats.columns = ['Data', 'Total', 'Resolvidos']
        
        # Criar gráfico de linha
        fig = go.Figure()
        
        # Linha de total
        fig.add_trace(go.Scatter(
            x=daily_stats['Data'],
            y=daily_stats['Total'],
            mode='lines+markers',
            name='Total de Contatos',
            line=dict(color=COLORS['primary'], width=3),
            marker=dict(size=8),
            fill='tonexty',
            fillcolor='rgba(52, 152, 219, 0.1)'
        ))
        
        # Linha de resolvidos
        fig.add_trace(go.Scatter(
            x=daily_stats['Data'],
            y=daily_stats['Resolvidos'],
            mode='lines+markers',
            name='Resolvidos',
            line=dict(color=COLORS['success'], width=2),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            height=350,
            showlegend=True,
            hovermode='x unified',
            title=None
        )
        
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico: {e}")

def render_channel_chart(df: pd.DataFrame):
    """Renderiza gráfico de distribuição por canal"""
    st.subheader("💬 Contatos por Canal")
    
    if 'channel' not in df.columns:
        st.warning("Dados de canal não disponíveis")
        return
    
    # Contar por canal
    channel_counts = df['channel'].value_counts()
    
    # Definir cores por canal
    channel_colors = {
        'whatsapp': COLORS['success'],
        'email': COLORS['danger'],
        'telefone': COLORS['info'],
        'chat online': COLORS['primary'],
        'zapi': COLORS['success'],  # WhatsApp via Zapi
        'dashboard': COLORS['primary']
    }
    
    colors = [channel_colors.get(channel.lower(), COLORS['muted']) for channel in channel_counts.index]
    
    # Criar gráfico de rosca
    fig = go.Figure(data=[go.Pie(
        labels=channel_counts.index,
        values=channel_counts.values,
        hole=0.4,
        marker_colors=colors,
        textposition='auto',
        textinfo='label+percent'
    )])
    
    fig.update_layout(
        height=350,
        showlegend=True,
        title=None
    )
    
    apply_dark_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

def render_messages_chart(df: pd.DataFrame, filters: dict):
    """Renderiza análise de volume de mensagens por período"""
    st.subheader("📊 Volume de Mensagens por Período")
    
    if 'created_at' not in df.columns or 'message_count' not in df.columns:
        st.warning("Dados de mensagens não disponíveis")
        return
    
    try:
        # Garantir tipos corretos
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['message_count'] = pd.to_numeric(df['message_count'], errors='coerce').fillna(0)
        
        # Seletor de período
        period_option = st.radio(
            "Agrupar por:",
            ["Dia", "Semana", "Mês"],
            horizontal=True
        )
        
        # Agrupar conforme seleção
        if period_option == "Dia":
            grouped = df.groupby(df['created_at'].dt.date)['message_count'].sum().reset_index()
            grouped.columns = ['Período', 'Total de Mensagens']
        elif period_option == "Semana":
            df['week'] = df['created_at'].dt.isocalendar().week
            df['year'] = df['created_at'].dt.year
            grouped = df.groupby(['year', 'week'])['message_count'].sum().reset_index()
            grouped['Período'] = 'Sem ' + grouped['week'].astype(str) + '/' + grouped['year'].astype(str)
            grouped = grouped[['Período', 'message_count']]
            grouped.columns = ['Período', 'Total de Mensagens']
        else:  # Mês
            grouped = df.groupby(df['created_at'].dt.to_period('M'))['message_count'].sum().reset_index()
            grouped['Período'] = grouped['created_at'].astype(str)
            grouped = grouped[['Período', 'Total de Mensagens']]
        
        # Criar gráfico de barras
        fig = px.bar(
            grouped,
            x='Período',
            y='Total de Mensagens',
            text='Total de Mensagens',
            color_discrete_sequence=[COLORS['primary']]
        )
        
        fig.update_traces(
            texttemplate='%{text:,.0f}',
            textposition='outside'
        )
        
        fig.update_layout(
            height=400,
            showlegend=False,
            title=f"Total de Mensagens por {period_option}"
        )
        
        apply_dark_theme(fig)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Estatísticas
            st.markdown("### 📊 Estatísticas")
            total_msgs = df['message_count'].sum()
            avg_msgs = df['message_count'].mean()
            max_msgs = df['message_count'].max()
            
            st.metric("Total de Mensagens", f"{int(total_msgs):,}")
            st.metric("Média por Conversa", f"{avg_msgs:.1f}")
            st.metric("Máximo em uma Conversa", f"{int(max_msgs)}")
            
            # Distribuição por canal se disponível
            if 'channel' in df.columns:
                st.markdown("### 📱 Por Canal")
                channel_msgs = df.groupby('channel')['message_count'].sum().sort_values(ascending=False)
                for channel, count in channel_msgs.head(3).items():
                    st.write(f"**{channel}**: {int(count):,} msgs")
        
    except Exception as e:
        st.error(f"Erro ao criar análise de mensagens: {e}")

def render_agent_performance(df: pd.DataFrame):
    """Renderiza análise de performance por atendente"""
    st.subheader("👥 Performance por Atendente")
    
    if 'agent_id' not in df.columns:
        # Simular dados se não existir
        st.info("ℹ️ Dados de atendentes não disponíveis. Mostrando exemplo.")
        
        # Dados simulados
        agents_data = pd.DataFrame({
            'Atendente': ['Ana Silva', 'João Santos', 'Maria Costa', 'Pedro Lima'],
            'Total Atendimentos': [245, 198, 176, 142],
            'Taxa Resolução': [94.5, 92.3, 89.7, 87.2],
            'Satisfação Média': [4.7, 4.5, 4.3, 4.1]
        })
    else:
        # Usar dados reais
        agents_data = df.groupby('agent_id').agg({
            'conversation_id': 'count',
            'resolved': lambda x: (x.astype(str).str.lower().isin(['true', '1', 'sim']).sum() / len(x) * 100) if len(x) > 0 else 0,
            'satisfaction_score': lambda x: pd.to_numeric(x, errors='coerce').mean()
        }).reset_index()
        
        agents_data.columns = ['Atendente', 'Total Atendimentos', 'Taxa Resolução', 'Satisfação Média']
        agents_data = agents_data.sort_values('Total Atendimentos', ascending=False)
    
    # Criar gráfico de barras horizontais
    fig = go.Figure()
    
    # Barras de total de atendimentos
    fig.add_trace(go.Bar(
        y=agents_data['Atendente'],
        x=agents_data['Total Atendimentos'],
        name='Total Atendimentos',
        orientation='h',
        marker_color=COLORS['primary'],
        text=agents_data['Total Atendimentos'],
        textposition='auto'
    ))
    
    fig.update_layout(
        height=400,
        showlegend=False,
        title="Ranking de Atendimentos",
        xaxis_title="Número de Atendimentos",
        yaxis_title=""
    )
    
    apply_dark_theme(fig)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top performer
        if not agents_data.empty:
            top_agent = agents_data.iloc[0]
            st.markdown("### 🏆 Top Performer")
            st.markdown(f"**{top_agent['Atendente']}**")
            st.metric("Atendimentos", f"{int(top_agent['Total Atendimentos'])}")
            st.metric("Taxa de Resolução", f"{top_agent['Taxa Resolução']:.1f}%")
            st.metric("Satisfação", f"{top_agent['Satisfação Média']:.1f}/5")
    
    # Tabela completa
    st.markdown("### 📊 Detalhamento Completo")
    
    # Formatar tabela
    styled_df = agents_data.copy()
    styled_df['Taxa Resolução'] = styled_df['Taxa Resolução'].apply(lambda x: f"{x:.1f}%")
    styled_df['Satisfação Média'] = styled_df['Satisfação Média'].apply(lambda x: f"{x:.1f}/5")
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Total Atendimentos": st.column_config.ProgressColumn(
                "Total Atendimentos",
                min_value=0,
                max_value=agents_data['Total Atendimentos'].max()
            )
        }
    )