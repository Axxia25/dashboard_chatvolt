"""
Configurações centralizadas do Dashboard Reach IA
"""

import os
from datetime import timedelta

# Configurações gerais do app
APP_CONFIG = {
    'name': 'Dashboard Reach IA',
    'version': '2.0.0',
    'company': 'Reach Solutions',
    'support_email': 'suporte@reachsolutions.com.br',
    'documentation_url': 'https://docs.reachsolutions.com.br'
}

# Configurações de cache
CACHE_CONFIG = {
    'default_ttl': 300,  # 5 minutos em segundos
    'max_entries': 1000,
    'clear_on_logout': True
}

# Configurações de autenticação
AUTH_CONFIG = {
    'session_timeout': timedelta(hours=8),
    'max_login_attempts': 5,
    'lockout_duration': timedelta(minutes=30),
    'require_strong_token': True,
    'min_token_length': 8
}

# Configurações de dados
DATA_CONFIG = {
    'max_rows_display': 10000,
    'default_date_range_days': 30,
    'refresh_interval': 30,  # segundos
    'enable_auto_refresh': False,
    'batch_size': 1000
}

# Configurações de visualização
VISUALIZATION_CONFIG = {
    'default_chart_height': 400,
    'color_palette': {
        'primary': '#3498db',
        'success': '#2ecc71',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'info': '#9b59b6',
        'muted': '#95a5a6'
    },
    'chart_theme': 'plotly_dark',
    'show_grid': True,
    'animation_duration': 750
}

# Configurações de exportação
EXPORT_CONFIG = {
    'csv_encoding': 'utf-8',
    'csv_separator': ',',
    'excel_engine': 'openpyxl',
    'max_export_rows': 50000,
    'include_metadata': True
}

# Configurações de logging
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'dashboard.log',
    'max_bytes': 10485760,  # 10MB
    'backup_count': 5
}

# Configurações de performance
PERFORMANCE_CONFIG = {
    'enable_profiling': False,
    'lazy_loading': True,
    'pagination_size': 100,
    'enable_compression': True,
    'cache_static_assets': True
}

# Configurações de segurança
SECURITY_CONFIG = {
    'enable_ssl': True,
    'csrf_protection': True,
    'xss_protection': True,
    'content_security_policy': "default-src 'self'",
    'max_upload_size': 10485760,  # 10MB
    'allowed_file_types': ['.csv', '.xlsx', '.json']
}

# Mapeamentos de dados
DATA_MAPPINGS = {
    'lead_stages': {
        'novo': 'Novo',
        'qualificado': 'Qualificado',
        'convertido': 'Convertido',
        'perdido': 'Perdido'
    },
    'status': {
        'RESOLVED': 'Resolvido',
        'UNRESOLVED': 'Não Resolvido',
        'HUMAN_REQUESTED': 'Requer Humano'
    },
    'channels': {
        'whatsapp': 'WhatsApp',
        'email': 'Email',
        'telefone': 'Telefone',
        'chat online': 'Chat Online',
        'dashboard': 'Dashboard',
        'api': 'API'
    },
    'priority': {
        'HIGH': 'Alta',
        'MEDIUM': 'Média',
        'LOW': 'Baixa'
    },
    'satisfaction_levels': {
        5: 'Muito Satisfeito',
        4: 'Satisfeito',
        3: 'Neutro',
        2: 'Insatisfeito',
        1: 'Muito Insatisfeito'
    }
}

# Configurações de métricas
METRICS_CONFIG = {
    'kpis': [
        {
            'id': 'total_contacts',
            'name': 'Total de Contatos',
            'icon': '📊',
            'color': '#3498db',
            'format': 'number'
        },
        {
            'id': 'avg_response_time',
            'name': 'Tempo Médio Resposta',
            'icon': '⏱️',
            'color': '#2ecc71',
            'format': 'duration',
            'unit': 'minutes'
        },
        {
            'id': 'satisfaction_score',
            'name': 'Satisfação Média',
            'icon': '⭐',
            'color': '#9b59b6',
            'format': 'decimal',
            'suffix': '/5'
        },
        {
            'id': 'resolution_rate',
            'name': 'Taxa de Resolução',
            'icon': '✅',
            'color': '#f39c12',
            'format': 'percentage'
        }
    ],
    'targets': {
        'response_time': 5,  # minutos
        'satisfaction': 4.0,
        'resolution_rate': 90  # percentual
    }
}

# Configurações de notificações
NOTIFICATION_CONFIG = {
    'enable_browser_notifications': True,
    'enable_email_notifications': False,
    'notification_types': [
        'new_lead',
        'hot_lead',
        'escalation_required',
        'sla_breach',
        'daily_summary'
    ],
    'quiet_hours': {
        'enabled': True,
        'start': '22:00',
        'end': '08:00'
    }
}

# URLs e endpoints
API_ENDPOINTS = {
    'base_url': os.getenv('API_BASE_URL', 'https://api.reachsolutions.com.br'),
    'auth': '/auth/login',
    'data': '/data/conversations',
    'metrics': '/metrics/summary',
    'export': '/export/data'
}

# Configurações regionais
REGIONAL_CONFIG = {
    'timezone': 'America/Sao_Paulo',
    'locale': 'pt_BR',
    'currency': 'BRL',
    'date_format': '%d/%m/%Y',
    'datetime_format': '%d/%m/%Y %H:%M:%S',
    'number_format': {
        'decimal_sep': ',',
        'thousands_sep': '.'
    }
}

# Feature flags
FEATURES = {
    'enable_ai_insights': True,
    'enable_predictive_analytics': False,
    'enable_real_time_sync': True,
    'enable_advanced_filters': True,
    'enable_custom_dashboards': False,
    'enable_api_access': True,
    'enable_multi_language': False,
    'enable_dark_mode': True,
    'enable_mobile_app': False
}

# Configurações de desenvolvimento
DEV_CONFIG = {
    'debug_mode': os.getenv('DEBUG', 'False').lower() == 'true',
    'show_error_details': os.getenv('SHOW_ERRORS', 'False').lower() == 'true',
    'enable_hot_reload': True,
    'mock_data': False,
    'bypass_auth': False
}

def get_config(key: str, default=None):
    """
    Obtém uma configuração específica
    
    Args:
        key: Chave da configuração (ex: 'APP_CONFIG.name')
        default: Valor padrão se não encontrar
        
    Returns:
        Valor da configuração ou default
    """
    try:
        # Dividir chave em partes
        parts = key.split('.')
        
        # Começar com o módulo atual
        value = globals()[parts[0]]
        
        # Navegar pelos níveis
        for part in parts[1:]:
            value = value[part]
        
        return value
    except (KeyError, IndexError, TypeError):
        return default

def update_config(key: str, value):
    """
    Atualiza uma configuração em tempo de execução
    
    Args:
        key: Chave da configuração
        value: Novo valor
    """
    try:
        parts = key.split('.')
        config_dict = globals()[parts[0]]
        
        # Navegar até o penúltimo nível
        for part in parts[1:-1]:
            config_dict = config_dict[part]
        
        # Atualizar o valor
        config_dict[parts[-1]] = value
        
        return True
    except:
        return False