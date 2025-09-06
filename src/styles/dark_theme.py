"""
Tema Dark para Dashboard Reach IA
Baseado no visual Luis Imóveis
"""

import streamlit as st

def apply_dark_theme():
    """Aplica o tema dark completo ao dashboard"""
    
    st.markdown("""
    <style>
    /* ===== TEMA DARK REACH IA ===== */
    
    /* Reset e base */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    .main .block-container {
        background-color: #0e1117;
        padding-top: 1rem;
        max-width: 100%;
    }
    
    /* Headers */
    h1 {
        color: #fafafa !important;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    h2, h3 {
        color: #fafafa !important;
        font-weight: 500;
    }
    
    /* Texto e links */
    p, span, label {
        color: #fafafa !important;
    }
    
    a {
        color: #3498db !important;
        text-decoration: none;
    }
    
    a:hover {
        color: #2980b9 !important;
    }
    
    /* Cards de métricas */
    [data-testid="metric-container"] {
        background-color: #262730;
        border: 1px solid #464853;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        border-color: #3498db;
        box-shadow: 0 4px 8px rgba(52, 152, 219, 0.1);
    }
    
    [data-testid="metric-container"] > div {
        color: #fafafa !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #fafafa !important;
        font-weight: 600;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #a3a8b8 !important;
        font-size: 0.9rem;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #262730;
        border-right: 1px solid #464853;
    }
    
    .css-1d391kg {
        background-color: #262730;
    }
    
    [data-testid="stSidebar"] {
        background-color: #262730;
        border-right: 1px solid #464853;
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        background-color: #262730;
    }
    
    /* Inputs e selectbox */
    .stTextInput > div > div {
        background-color: #262730;
        color: #fafafa;
        border: 1px solid #464853;
        border-radius: 6px;
    }
    
    .stSelectbox > div > div {
        background-color: #262730;
        color: #fafafa;
        border: 1px solid #464853;
        border-radius: 6px;
    }
    
    .stDateInput > div > div {
        background-color: #262730;
        color: #fafafa;
        border: 1px solid #464853;
        border-radius: 6px;
    }
    
    input {
        background-color: #1a1d23 !important;
        color: #fafafa !important;
        border: 1px solid #464853 !important;
    }
    
    input:focus {
        border-color: #3498db !important;
        box-shadow: 0 0 0 0.2rem rgba(52, 152, 219, 0.25) !important;
    }
    
    /* Botões */
    .stButton > button {
        background-color: #3498db;
        color: #fafafa;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #2980b9;
        box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background-color: #27ae60;
        color: #fafafa;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stDownloadButton > button:hover {
        background-color: #229954;
    }
    
    /* Gráficos */
    .js-plotly-plot {
        background-color: #262730 !important;
        border-radius: 8px;
    }
    
    /* Dataframe */
    .stDataFrame {
        background-color: #262730;
        border: 1px solid #464853;
        border-radius: 8px;
    }
    
    [data-testid="stTable"] {
        background-color: #262730;
        color: #fafafa;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1d23;
        border-radius: 8px;
        padding: 0.25rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #a3a8b8;
        background-color: transparent;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #fafafa;
        background-color: #262730;
    }
    
    .stTabs [aria-selected="true"] {
        color: #fafafa !important;
        background-color: #3498db !important;
    }
    
    /* Alertas e mensagens */
    .stAlert {
        background-color: #262730;
        border: 1px solid #464853;
        color: #fafafa;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stSuccess {
        background-color: #1e4d3f;
        border-color: #27ae60;
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
    
    /* Checkbox e Radio */
    .stCheckbox > label {
        color: #fafafa !important;
    }
    
    .stRadio > label {
        color: #fafafa !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #262730;
        border: 1px solid #464853;
        border-radius: 8px;
        color: #fafafa;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #3498db;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #3498db;
    }
    
    /* Slider */
    .stSlider > div > div {
        color: #fafafa;
    }
    
    /* Forms */
    [data-testid="stForm"] {
        background-color: #262730;
        border: 1px solid #464853;
        border-radius: 8px;
        padding: 1.5rem;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #3498db !important;
    }
    
    /* Markdown containers */
    .markdown-text-container {
        color: #fafafa;
    }
    
    /* Code blocks */
    code {
        background-color: #1a1d23;
        color: #3498db;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
    }
    
    pre {
        background-color: #1a1d23;
        color: #fafafa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #464853;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1d23;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #464853;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #3498db;
    }
    
    /* Tooltips */
    .tooltip {
        background-color: #262730 !important;
        color: #fafafa !important;
        border: 1px solid #464853 !important;
    }
    
    /* Animações suaves */
    * {
        transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
    }
    
    /* Ajustes específicos para o tema */
    .css-1kyxreq {
        color: #fafafa;
    }
    
    .css-1avcm0n {
        background-color: #262730;
    }
    
    .css-1n543e5 {
        color: #a3a8b8;
    }
    
    /* Remove bordas desnecessárias */
    hr {
        border-color: #464853;
    }
    
    /* Ajuste para métrics delta */
    [data-testid="metric-container"] [data-testid="metric-delta"] svg {
        fill: currentColor;
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .status-resolved {
        background-color: #27ae60;
        color: #fafafa;
    }
    
    .status-pending {
        background-color: #f39c12;
        color: #fafafa;
    }
    
    .status-escalated {
        background-color: #e74c3c;
        color: #fafafa;
    }
    
    /* Login form específico */
    .login-container {
        background-color: #262730;
        border: 1px solid #464853;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    
    </style>
    """, unsafe_allow_html=True)

def get_theme_colors():
    """Retorna o dicionário de cores do tema"""
    return {
        'background': '#0e1117',
        'secondary_bg': '#262730',
        'border': '#464853',
        'text_primary': '#fafafa',
        'text_secondary': '#a3a8b8',
        'primary': '#3498db',
        'primary_dark': '#2980b9',
        'success': '#27ae60',
        'success_dark': '#229954',
        'warning': '#f39c12',
        'warning_dark': '#d68910',
        'danger': '#e74c3c',
        'danger_dark': '#c0392b',
        'info': '#9b59b6',
        'info_dark': '#7d3c98',
        'muted': '#95a5a6',
        'muted_dark': '#7f8c8d'
    }

def apply_custom_css(css_string: str):
    """Aplica CSS customizado adicional"""
    st.markdown(f"<style>{css_string}</style>", unsafe_allow_html=True)