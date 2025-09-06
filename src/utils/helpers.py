"""
Funções auxiliares e utilidades gerais
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import re
import hashlib
import uuid
from typing import Union, List, Dict, Any

def format_currency(value: float, currency: str = "BRL") -> str:
    """
    Formata valor monetário
    
    Args:
        value: Valor numérico
        currency: Código da moeda (padrão BRL)
        
    Returns:
        String formatada
    """
    if pd.isna(value) or value == 0:
        return "R$ 0,00"
    
    # Formatar para Real Brasileiro
    if currency == "BRL":
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        return f"{currency} {value:,.2f}"

def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formata valor como percentual
    
    Args:
        value: Valor entre 0-100
        decimals: Casas decimais
        
    Returns:
        String formatada com %
    """
    if pd.isna(value):
        return "0%"
    
    return f"{value:.{decimals}f}%"

def format_duration(seconds: float) -> str:
    """
    Formata duração em formato legível
    
    Args:
        seconds: Duração em segundos
        
    Returns:
        String formatada (ex: "2h 15m", "45s")
    """
    if pd.isna(seconds) or seconds < 0:
        return "0s"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def format_number(value: float, decimals: int = 0) -> str:
    """
    Formata número com separadores de milhares
    
    Args:
        value: Valor numérico
        decimals: Casas decimais
        
    Returns:
        String formatada
    """
    if pd.isna(value):
        return "0"
    
    if decimals > 0:
        return f"{value:,.{decimals}f}".replace(",", ".")
    else:
        return f"{int(value):,}".replace(",", ".")

def calculate_business_hours(start_time: datetime, end_time: datetime, 
                           business_start: int = 8, business_end: int = 18) -> float:
    """
    Calcula horas úteis entre dois timestamps
    
    Args:
        start_time: Início
        end_time: Fim  
        business_start: Hora início expediente (padrão 8)
        business_end: Hora fim expediente (padrão 18)
        
    Returns:
        Horas úteis
    """
    if start_time >= end_time:
        return 0
    
    total_hours = 0
    current = start_time
    
    while current < end_time:
        # Pular fins de semana
        if current.weekday() >= 5:  # Sábado = 5, Domingo = 6
            current = current + timedelta(days=1)
            current = current.replace(hour=business_start, minute=0, second=0)
            continue
        
        # Calcular horas do dia atual
        day_start = current.replace(hour=business_start, minute=0, second=0)
        day_end = current.replace(hour=business_end, minute=0, second=0)
        
        # Se começou antes do expediente
        if current < day_start:
            current = day_start
        
        # Se terminou depois do expediente
        if end_time > day_end:
            work_end = day_end
        else:
            work_end = end_time
        
        # Adicionar horas trabalhadas
        if work_end > current:
            total_hours += (work_end - current).total_seconds() / 3600
        
        # Próximo dia
        current = current + timedelta(days=1)
        current = current.replace(hour=business_start, minute=0, second=0)
    
    return total_hours

def sanitize_phone_number(phone: str) -> str:
    """
    Padroniza número de telefone brasileiro
    
    Args:
        phone: Número de telefone
        
    Returns:
        Número padronizado
    """
    if pd.isna(phone) or not phone:
        return ""
    
    # Remover caracteres não numéricos
    phone = re.sub(r'\D', '', str(phone))
    
    # Adicionar código do país se não tiver
    if len(phone) == 10 or len(phone) == 11:
        phone = '55' + phone
    
    # Formatar
    if len(phone) == 12:  # Fixo
        return f"+{phone[:2]} ({phone[2:4]}) {phone[4:8]}-{phone[8:]}"
    elif len(phone) == 13:  # Celular
        return f"+{phone[:2]} ({phone[2:4]}) {phone[4:9]}-{phone[9:]}"
    
    return phone

def extract_domain_from_email(email: str) -> str:
    """
    Extrai domínio de um email
    
    Args:
        email: Endereço de email
        
    Returns:
        Domínio ou string vazia
    """
    if pd.isna(email) or not email:
        return ""
    
    match = re.search(r'@([a-zA-Z0-9.-]+)', str(email))
    return match.group(1) if match else ""

def generate_unique_id(prefix: str = "") -> str:
    """
    Gera ID único
    
    Args:
        prefix: Prefixo opcional
        
    Returns:
        ID único
    """
    unique_id = str(uuid.uuid4())[:8]
    
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id

def calculate_sla_status(response_time: float, sla_minutes: float = 5) -> str:
    """
    Calcula status do SLA
    
    Args:
        response_time: Tempo de resposta em segundos
        sla_minutes: SLA em minutos
        
    Returns:
        'within_sla', 'exceeded_sla' ou 'no_data'
    """
    if pd.isna(response_time):
        return 'no_data'
    
    response_minutes = response_time / 60
    
    if response_minutes <= sla_minutes:
        return 'within_sla'
    else:
        return 'exceeded_sla'

def get_brazilian_timezone() -> pytz.tzinfo:
    """Retorna timezone brasileiro"""
    return pytz.timezone('America/Sao_Paulo')

def localize_datetime(dt: datetime) -> datetime:
    """
    Localiza datetime para horário brasileiro
    
    Args:
        dt: Datetime naive ou aware
        
    Returns:
        Datetime com timezone brasileiro
    """
    tz = get_brazilian_timezone()
    
    if dt.tzinfo is None:
        # Datetime naive - assumir que já está em horário brasileiro
        return tz.localize(dt)
    else:
        # Datetime aware - converter
        return dt.astimezone(tz)

def get_date_range_labels(days: int) -> Dict[str, Any]:
    """
    Gera labels para range de datas
    
    Args:
        days: Número de dias
        
    Returns:
        Dict com start_date, end_date e label
    """
    today = datetime.now(get_brazilian_timezone()).date()
    
    if days == 7:
        label = "Últimos 7 dias"
    elif days == 30:
        label = "Últimos 30 dias"
    elif days == 90:
        label = "Últimos 3 meses"
    else:
        label = f"Últimos {days} dias"
    
    return {
        'start_date': today - timedelta(days=days),
        'end_date': today,
        'label': label
    }

def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Trunca string se exceder tamanho máximo
    
    Args:
        text: Texto original
        max_length: Tamanho máximo
        suffix: Sufixo para texto truncado
        
    Returns:
        Texto truncado ou original
    """
    if pd.isna(text) or not text:
        return ""
    
    text = str(text)
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def calculate_variation(current: float, previous: float) -> Dict[str, Any]:
    """
    Calcula variação percentual entre valores
    
    Args:
        current: Valor atual
        previous: Valor anterior
        
    Returns:
        Dict com variation, direction, symbol
    """
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return {
            'value': 0,
            'direction': 'stable',
            'symbol': '→',
            'formatted': '0%'
        }
    
    variation = ((current - previous) / previous) * 100
    
    if variation > 0:
        return {
            'value': variation,
            'direction': 'up',
            'symbol': '↑',
            'formatted': f"+{variation:.1f}%"
        }
    elif variation < 0:
        return {
            'value': abs(variation),
            'direction': 'down',
            'symbol': '↓',
            'formatted': f"-{abs(variation):.1f}%"
        }
    else:
        return {
            'value': 0,
            'direction': 'stable',
            'symbol': '→',
            'formatted': '0%'
        }

def get_greeting() -> str:
    """Retorna saudação baseada no horário"""
    hour = datetime.now(get_brazilian_timezone()).hour
    
    if 5 <= hour < 12:
        return "Bom dia"
    elif 12 <= hour < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

def parse_bool(value: Any) -> bool:
    """
    Parse flexível de valores booleanos
    
    Args:
        value: Qualquer valor
        
    Returns:
        Boolean
    """
    if isinstance(value, bool):
        return value
    
    if pd.isna(value):
        return False
    
    str_value = str(value).lower().strip()
    return str_value in ['true', '1', 'sim', 'yes', 's', 'y', 'verdadeiro']

def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """
    Divisão segura que evita divisão por zero
    
    Args:
        numerator: Numerador
        denominator: Denominador
        default: Valor padrão se denominador for zero
        
    Returns:
        Resultado da divisão ou valor padrão
    """
    if denominator == 0 or pd.isna(denominator):
        return default
    
    return numerator / denominator

def get_color_by_value(value: float, thresholds: Dict[str, float]) -> str:
    """
    Retorna cor baseada em thresholds
    
    Args:
        value: Valor para avaliar
        thresholds: Dict com {'good': 90, 'warning': 70}
        
    Returns:
        Cor hex
    """
    colors = {
        'good': '#2ecc71',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'default': '#95a5a6'
    }
    
    if pd.isna(value):
        return colors['default']
    
    if value >= thresholds.get('good', 90):
        return colors['good']
    elif value >= thresholds.get('warning', 70):
        return colors['warning']
    else:
        return colors['danger']