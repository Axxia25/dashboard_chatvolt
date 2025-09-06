"""
Sistema de Cache para otimização de performance
"""

import streamlit as st
from datetime import datetime, timedelta
import hashlib
import json
import pickle
from typing import Any, Optional, Callable, Dict
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Gerenciador centralizado de cache"""
    
    def __init__(self):
        """Inicializa o gerenciador de cache"""
        self._init_cache_state()
    
    def _init_cache_state(self):
        """Inicializa estado do cache no session_state"""
        if 'cache_storage' not in st.session_state:
            st.session_state.cache_storage = {}
        
        if 'cache_metadata' not in st.session_state:
            st.session_state.cache_metadata = {}
    
    def _generate_cache_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """
        Gera chave única para cache baseada nos parâmetros
        
        Args:
            prefix: Prefixo da chave
            params: Parâmetros para hash
            
        Returns:
            Chave de cache
        """
        # Serializar parâmetros de forma determinística
        param_str = json.dumps(params, sort_keys=True)
        
        # Gerar hash
        hash_obj = hashlib.md5(param_str.encode())
        hash_str = hash_obj.hexdigest()[:8]
        
        return f"{prefix}_{hash_str}"
    
    def get(self, key: str, 
            func: Optional[Callable] = None,
            ttl: int = 300,
            params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Obtém valor do cache ou executa função
        
        Args:
            key: Chave base do cache
            func: Função para executar se não houver cache
            ttl: Tempo de vida em segundos
            params: Parâmetros para a função
            
        Returns:
            Valor do cache ou resultado da função
        """
        # Gerar chave completa
        if params:
            cache_key = self._generate_cache_key(key, params)
        else:
            cache_key = key
        
        # Verificar se existe no cache
        if self._is_valid_cache(cache_key):
            logger.info(f"Cache hit: {cache_key}")
            return st.session_state.cache_storage[cache_key]
        
        # Se não existe ou expirou, executar função
        if func:
            logger.info(f"Cache miss: {cache_key}")
            result = func(**(params or {}))
            self.set(cache_key, result, ttl)
            return result
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Armazena valor no cache
        
        Args:
            key: Chave do cache
            value: Valor para armazenar
            ttl: Tempo de vida em segundos
        """
        st.session_state.cache_storage[key] = value
        st.session_state.cache_metadata[key] = {
            'timestamp': datetime.now(),
            'ttl': ttl
        }
        logger.info(f"Cache set: {key}")
    
    def invalidate(self, key: str = None, prefix: str = None):
        """
        Invalida cache específico ou por prefixo
        
        Args:
            key: Chave específica
            prefix: Prefixo para invalidar múltiplas chaves
        """
        if key:
            # Invalidar chave específica
            if key in st.session_state.cache_storage:
                del st.session_state.cache_storage[key]
                del st.session_state.cache_metadata[key]
                logger.info(f"Cache invalidated: {key}")
        
        elif prefix:
            # Invalidar todas as chaves com prefixo
            keys_to_delete = [
                k for k in st.session_state.cache_storage.keys()
                if k.startswith(prefix)
            ]
            
            for k in keys_to_delete:
                del st.session_state.cache_storage[k]
                del st.session_state.cache_metadata[k]
            
            logger.info(f"Cache invalidated: {len(keys_to_delete)} keys with prefix '{prefix}'")
        
        else:
            # Invalidar todo o cache
            st.session_state.cache_storage.clear()
            st.session_state.cache_metadata.clear()
            logger.info("All cache invalidated")
    
    def _is_valid_cache(self, key: str) -> bool:
        """
        Verifica se cache é válido (existe e não expirou)
        
        Args:
            key: Chave do cache
            
        Returns:
            True se válido, False caso contrário
        """
        if key not in st.session_state.cache_storage:
            return False
        
        if key not in st.session_state.cache_metadata:
            return False
        
        metadata = st.session_state.cache_metadata[key]
        timestamp = metadata['timestamp']
        ttl = metadata['ttl']
        
        # Verificar expiração
        if datetime.now() - timestamp > timedelta(seconds=ttl):
            # Cache expirado
            del st.session_state.cache_storage[key]
            del st.session_state.cache_metadata[key]
            return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache
        
        Returns:
            Dict com estatísticas
        """
        total_keys = len(st.session_state.cache_storage)
        
        # Calcular tamanho aproximado
        total_size = 0
        for value in st.session_state.cache_storage.values():
            try:
                total_size += len(pickle.dumps(value))
            except:
                pass
        
        # Verificar expirados
        expired_count = 0
        for key in list(st.session_state.cache_metadata.keys()):
            if not self._is_valid_cache(key):
                expired_count += 1
        
        return {
            'total_keys': total_keys,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'expired_count': expired_count,
            'active_count': total_keys - expired_count
        }

# Instância global
cache_manager = CacheManager()

# Decorador para cache
def cached(ttl: int = 300, key_prefix: str = None):
    """
    Decorador para cache de funções
    
    Args:
        ttl: Tempo de vida em segundos
        key_prefix: Prefixo customizado da chave
        
    Usage:
        @cached(ttl=600)
        def expensive_function(param1, param2):
            return result
    """
    def decorator(func):
        def wrapper(**kwargs):
            # Gerar prefixo baseado no nome da função
            prefix = key_prefix or func.__name__
            
            # Usar cache manager
            return cache_manager.get(
                key=prefix,
                func=func,
                ttl=ttl,
                params=kwargs
            )
        
        return wrapper
    
    return decorator

# Funções auxiliares para uso direto

def get_cached_data(key: str, default: Any = None) -> Any:
    """
    Obtém dados do cache
    
    Args:
        key: Chave do cache
        default: Valor padrão se não encontrar
        
    Returns:
        Valor do cache ou default
    """
    result = cache_manager.get(key)
    return result if result is not None else default

def set_cached_data(key: str, value: Any, ttl: int = 300):
    """
    Armazena dados no cache
    
    Args:
        key: Chave do cache
        value: Valor para armazenar
        ttl: Tempo de vida em segundos
    """
    cache_manager.set(key, value, ttl)

def invalidate_cache(key: str = None, prefix: str = None):
    """
    Invalida cache
    
    Args:
        key: Chave específica
        prefix: Prefixo para invalidar múltiplas chaves
    """
    cache_manager.invalidate(key, prefix)

def clear_all_cache():
    """Limpa todo o cache"""
    cache_manager.invalidate()

def get_cache_stats() -> Dict[str, Any]:
    """Retorna estatísticas do cache"""
    return cache_manager.get_stats()

# Cache específico para dados do dashboard
class DashboardCache:
    """Cache especializado para dados do dashboard"""
    
    @staticmethod
    @cached(ttl=300, key_prefix='dashboard_data')
    def get_processed_data(client_id: str, filters: Dict[str, Any]) -> Any:
        """Cache para dados processados do dashboard"""
        # Esta função seria implementada com a lógica real
        pass
    
    @staticmethod
    def invalidate_client_cache(client_id: str):
        """Invalida cache de um cliente específico"""
        invalidate_cache(prefix=f"dashboard_data_{client_id}")
    
    @staticmethod
    @cached(ttl=3600, key_prefix='client_info')
    def get_client_info(client_id: str) -> Dict[str, Any]:
        """Cache para informações do cliente"""
        # Esta função seria implementada com a lógica real
        # Por enquanto retorna vazio - será implementado quando integrado
        return {}
    
    @staticmethod
    @cached(ttl=86400, key_prefix='master_sheet')  # 24 horas
    def get_master_sheet_data() -> Any:
        """Cache para planilha mestre (muda raramente)"""
        # Esta função seria implementada com a lógica real
        # Por enquanto retorna vazio - será implementado quando integrado
        return {}