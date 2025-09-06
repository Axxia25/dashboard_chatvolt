"""
REACH IA DASHBOARD - Sistema Multi-Cliente
Aplicação principal com sistema de login e visual moderno
"""

import streamlit as st
from datetime import datetime
import pytz

# Importar módulos locais
from src.utils.auth import AuthManager, check_authentication
from src.data.collectors import DataCollector
from src.data.processors import DataProcessor
from src.components.metrics import render_metrics_cards
from src.components.charts import (
    render_funnel_chart,
    render_timeline_chart, 
    render_channel_chart,
    render_messages_chart,
    render_agent_performance
)
from src.components.filters import render_sidebar_filters
from src.styles.dark_theme import apply_dark_theme
from config.settings import APP_CONFIG

# Configuração da página
st.set_page_config(
    page_title="Dashboard Reach IA",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar tema dark
apply_dark_theme()

def login_page():
    """Página de login do sistema"""
    # Container centralizado para login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🚀 Dashboard Reach IA")
        st.markdown("### Sistema de Análise de Atendimento")
        
        with st.form("login_form"):
            st.markdown("#### 🔐 Acesso ao Sistema")
            
            client_id = st.text_input(
                "ID do Cliente",
                placeholder="Ex: CLI001",
                help="Insira o ID fornecido pela Reach IA"
            )
            
            token = st.text_input(
                "Token de Acesso", 
                type="password",
                placeholder="Insira seu token de acesso",
                help="Token único fornecido para sua empresa"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit = st.form_submit_button(
                    "🚀 Entrar", 
                    use_container_width=True,
                    type="primary"
                )
            with col_btn2:
                if st.form_submit_button("❓ Solicitar Acesso", use_container_width=True):
                    st.info("📧 Entre em contato: suporte@reachsolutions.com.br")
            
            if submit:
                if client_id and token:
                    auth_manager = AuthManager()
                    auth_result = auth_manager.authenticate(client_id, token)
                    
                    if auth_result["success"]:
                        st.success("✅ Login realizado com sucesso!")
                        st.session_state.authenticated = True
                        st.session_state.client_data = auth_result["client_data"]
                        st.rerun()
                    else:
                        st.error(f"❌ {auth_result['message']}")
                else:
                    st.error("❌ Preencha todos os campos!")
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #a3a8b8;'>
                <small>Dashboard Reach IA © 2024 | Versão 2.0</small>
            </div>
            """,
            unsafe_allow_html=True
        )

def main_dashboard():
    """Dashboard principal após login"""
    # Verificar autenticação
    if not check_authentication():
        st.rerun()
    
    # Obter dados do cliente
    client_data = st.session_state.client_data
    
    # Header com informações do cliente
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.markdown(f"# 🏢 Dashboard {client_data['client_name']}")
    with col3:
        if st.button("🚪 Sair", use_container_width=True):
            for key in ["authenticated", "client_data", "df_cache"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    st.markdown("**Acompanhe suas métricas em tempo real**")
    
    # Sidebar com filtros
    filters = render_sidebar_filters()
    
    # Carregar dados
    with st.spinner("📊 Carregando dados..."):
        collector = DataCollector(client_data['planilha_id'])
        raw_data = collector.load_data()
        
        if raw_data is not None:
            processor = DataProcessor()
            df = processor.process_data(raw_data, filters)
            
            if not df.empty:
                # Salvar no cache
                st.session_state.df_cache = df
                
                # Exibir métricas
                render_metrics_cards(df)
                
                # Tabs para diferentes visualizações
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📈 Visão Geral",
                    "🎯 Funil de Conversão", 
                    "💬 Análise de Mensagens",
                    "👥 Performance",
                    "📊 Dados Detalhados"
                ])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    with col1:
                        render_timeline_chart(df)
                    with col2:
                        render_channel_chart(df)
                
                with tab2:
                    render_funnel_chart(df)
                
                with tab3:
                    render_messages_chart(df, filters)
                
                with tab4:
                    render_agent_performance(df)
                
                with tab5:
                    st.subheader("📋 Dados Detalhados")
                    
                    # Opções de visualização
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        show_all = st.checkbox("Mostrar todos os campos", False)
                    with col2:
                        rows_per_page = st.selectbox("Linhas por página", [10, 25, 50, 100], index=1)
                    
                    # Colunas a exibir
                    if show_all:
                        display_cols = df.columns.tolist()
                    else:
                        display_cols = [
                            'created_at', 'contact_name', 'channel', 'status',
                            'lead_stage', 'satisfaction_score', 'message_count',
                            'first_response_time', 'resolution_time'
                        ]
                        display_cols = [col for col in display_cols if col in df.columns]
                    
                    # Exibir dados paginados
                    st.dataframe(
                        df[display_cols].head(rows_per_page),
                        use_container_width=True,
                        height=400
                    )
                    
                    # Download
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Completo (CSV)",
                        data=csv,
                        file_name=f"reach_ia_{client_data['client_id']}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime='text/csv'
                    )
                
                # Footer com informações
                st.markdown("---")
                last_update = datetime.now(pytz.timezone('America/Sao_Paulo'))
                st.markdown(
                    f"""
                    <div style='text-align: center; color: #a3a8b8;'>
                        <small>
                        Última atualização: {last_update.strftime('%d/%m/%Y %H:%M:%S')} | 
                        Total de registros: {len(df):,} | 
                        Cliente: {client_data['client_id']}
                        </small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados")
        else:
            st.error("❌ Erro ao carregar dados. Verifique sua configuração.")
    
    # Auto-refresh opcional
    if st.sidebar.checkbox("🔄 Auto-refresh (30s)", False):
        st.rerun()

def main():
    """Função principal - controla fluxo do app"""
    # Inicializar session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # Roteamento baseado em autenticação
    if st.session_state.authenticated:
        main_dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()