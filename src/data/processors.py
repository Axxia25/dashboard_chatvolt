"""
Processador de Dados
Responsável por processar e transformar dados para análise
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DataProcessor:
    """Processador de dados do dashboard"""
    
    def __init__(self):
        """Inicializa o processador"""
        self.processed_data = None
    
    def process_data(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Processa e filtra dados conforme necessário
        
        Args:
            df: DataFrame bruto
            filters: Filtros aplicados
            
        Returns:
            DataFrame processado
        """
        if df is None or df.empty:
            logger.warning("DataFrame vazio recebido para processamento")
            return pd.DataFrame()
        
        try:
            # Fazer cópia para não modificar original
            processed_df = df.copy()
            
            # Aplicar processamentos básicos
            processed_df = self._standardize_columns(processed_df)
            processed_df = self._calculate_metrics(processed_df)
            processed_df = self._apply_lead_scoring(processed_df)
            processed_df = self._detect_hot_leads(processed_df)
            processed_df = self._analyze_sentiment(processed_df)
            
            # Aplicar filtros
            processed_df = self._apply_filters(processed_df, filters)
            
            # Ordenar por data mais recente
            if 'created_at' in processed_df.columns:
                processed_df = processed_df.sort_values('created_at', ascending=False)
            
            self.processed_data = processed_df
            logger.info(f"✅ Processamento concluído: {len(processed_df)} registros")
            
            return processed_df
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento: {e}")
            return df
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Padroniza nomes e tipos de colunas"""
        
        # Mapeamento de colunas alternativas
        column_mapping = {
            'nome_cliente': 'contact_name',
            'telefone_cliente': 'contact_phone',
            'cliente_nome': 'contact_name',
            'data_contato': 'created_at',
            'canal_origem': 'channel',
            'agent_responsavel': 'agent_id',
            'status_conversa': 'status',
            'nivel_frustracao': 'frustration_level'
        }
        
        # Renomear colunas se necessário
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns and new_name not in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Garantir colunas essenciais
        essential_columns = {
            'conversation_id': '',
            'created_at': pd.NaT,
            'status': 'UNRESOLVED',
            'channel': 'unknown',
            'contact_name': '',
            'resolved': False,
            'message_count': 0,
            'satisfaction_score': 0,
            'lead_stage': 'novo',
            'lead_score': 0
        }
        
        for col, default_value in essential_columns.items():
            if col not in df.columns:
                df[col] = default_value
        
        # Padronizar valores de status
        status_mapping = {
            'resolvido': 'RESOLVED',
            'resolved': 'RESOLVED',
            'não resolvido': 'UNRESOLVED',
            'unresolved': 'UNRESOLVED',
            'pendente': 'UNRESOLVED',
            'em andamento': 'UNRESOLVED',
            'escalado': 'HUMAN_REQUESTED',
            'human_requested': 'HUMAN_REQUESTED'
        }
        
        if 'status' in df.columns:
            df['status'] = df['status'].astype(str).str.lower()
            df['status'] = df['status'].map(lambda x: status_mapping.get(x, 'UNRESOLVED'))
        
        # Padronizar canais
        channel_mapping = {
            'zapi': 'whatsapp',
            'whatsapp business': 'whatsapp',
            'wa': 'whatsapp',
            'email': 'email',
            'e-mail': 'email',
            'telefone': 'telefone',
            'phone': 'telefone',
            'chat': 'chat online',
            'webchat': 'chat online',
            'dashboard': 'dashboard'
        }
        
        if 'channel' in df.columns:
            df['channel'] = df['channel'].astype(str).str.lower()
            df['channel'] = df['channel'].map(lambda x: channel_mapping.get(x, x))
        
        return df
    
    def _calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula métricas derivadas"""
        
        # Calcular tempo de resposta em minutos
        if 'first_response_time' in df.columns:
            df['response_time_minutes'] = df['first_response_time'] / 60
        
        # Calcular tempo de resolução em horas
        if 'resolution_time' in df.columns:
            df['resolution_time_hours'] = df['resolution_time'] / 3600
        
        # Calcular SLA status
        if 'first_response_time' in df.columns:
            df['sla_status'] = df['first_response_time'].apply(
                lambda x: 'within_sla' if pd.notna(x) and x <= 300 else 'exceeded_sla'
            )
        
        # Calcular satisfação categorizada
        if 'satisfaction_score' in df.columns:
            df['satisfaction_category'] = pd.cut(
                df['satisfaction_score'],
                bins=[0, 2, 3, 5],
                labels=['Baixa', 'Média', 'Alta'],
                include_lowest=True
            )
        
        # Adicionar informações temporais
        if 'created_at' in df.columns:
            df['created_date'] = pd.to_datetime(df['created_at']).dt.date
            df['created_hour'] = pd.to_datetime(df['created_at']).dt.hour
            df['created_weekday'] = pd.to_datetime(df['created_at']).dt.day_name()
            df['created_week'] = pd.to_datetime(df['created_at']).dt.isocalendar().week
            df['created_month'] = pd.to_datetime(df['created_at']).dt.month_name()
        
        return df
    
    def _apply_lead_scoring(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula score de leads baseado em comportamento"""
        
        def calculate_lead_score(row):
            score = 0
            
            # Pontuação por engajamento
            if pd.notna(row.get('message_count', 0)):
                if row['message_count'] > 10:
                    score += 20
                elif row['message_count'] > 5:
                    score += 10
            
            # Pontuação por satisfação
            if pd.notna(row.get('satisfaction_score', 0)):
                if row['satisfaction_score'] >= 4:
                    score += 25
                elif row['satisfaction_score'] >= 3:
                    score += 10
            
            # Pontuação por resolução
            if row.get('resolved', False):
                score += 15
            
            # Pontuação por tempo de resposta rápido
            if pd.notna(row.get('first_response_time', 0)):
                if row['first_response_time'] <= 60:  # 1 minuto
                    score += 20
                elif row['first_response_time'] <= 300:  # 5 minutos
                    score += 10
            
            # Pontuação por canal
            preferred_channels = ['whatsapp', 'telefone']
            if row.get('channel', '') in preferred_channels:
                score += 10
            
            # Penalização por frustração
            if pd.notna(row.get('frustration_level', 0)):
                try:
                    frustration = float(row['frustration_level'])
                    if frustration > 3:
                        score -= 15
                except:
                    pass
            
            # Bonus por menções a produtos/preços
            if row.get('mentions_product', False):
                score += 15
            if row.get('mentions_price', False):
                score += 10
            if row.get('mentions_quantity', False):
                score += 5
            
            return min(100, max(0, score))  # Limitar entre 0 e 100
        
        if 'lead_score' in df.columns:
            df['lead_score'] = df.apply(calculate_lead_score, axis=1)
        
        # Atualizar lead_stage baseado no score e outros fatores
        def determine_lead_stage(row):
            current_stage = row.get('lead_stage', 'novo')
            
            # Se já está convertido ou perdido, manter
            if current_stage in ['convertido', 'perdido']:
                return current_stage
            
            score = row.get('lead_score', 0)
            resolved = row.get('resolved', False)
            
            if score >= 70 and resolved:
                return 'convertido'
            elif score >= 50:
                return 'qualificado'
            elif score < 20 and row.get('frustration_level', 0) > 4:
                return 'perdido'
            else:
                return 'novo'
        
        df['lead_stage'] = df.apply(determine_lead_stage, axis=1)
        
        return df
    
    def _detect_hot_leads(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica leads quentes com alta probabilidade de conversão"""
        
        def is_hot_lead(row):
            # Critérios para hot lead
            score = row.get('lead_score', 0)
            messages = row.get('message_count', 0)
            satisfaction = row.get('satisfaction_score', 0)
            mentions_product = row.get('mentions_product', False)
            mentions_price = row.get('mentions_price', False)
            
            # Lead é quente se:
            # - Score alto (>= 60) E
            # - (Muitas mensagens OU Alta satisfação OU Menciona produto/preço)
            if score >= 60:
                if messages > 8 or satisfaction >= 4 or (mentions_product and mentions_price):
                    return True
            
            # Ou se tem score muito alto
            if score >= 80:
                return True
            
            return False
        
        df['is_hot_lead'] = df.apply(is_hot_lead, axis=1)
        
        return df
    
    def _analyze_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Análise de sentimento baseada em indicadores"""
        
        def analyze_sentiment(row):
            # Análise simples baseada em indicadores disponíveis
            frustration = row.get('frustration_level', 0)
            satisfaction = row.get('satisfaction_score', 3)
            resolved = row.get('resolved', False)
            escalated = row.get('escalated_to_human', False)
            
            # Se já tem context_sentiment, usar
            if pd.notna(row.get('context_sentiment')):
                return row['context_sentiment']
            
            # Calcular sentimento baseado em métricas
            try:
                frustration = float(frustration) if pd.notna(frustration) else 0
                satisfaction = float(satisfaction) if pd.notna(satisfaction) else 3
                
                if frustration > 3 or escalated:
                    return 'negative'
                elif satisfaction >= 4 and resolved:
                    return 'positive'
                elif satisfaction <= 2:
                    return 'negative'
                else:
                    return 'neutral'
            except:
                return 'neutral'
        
        if 'context_sentiment' not in df.columns:
            df['context_sentiment'] = df.apply(analyze_sentiment, axis=1)
        
        return df
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Aplica filtros ao DataFrame"""
        
        if df.empty:
            return df
        
        filtered_df = df.copy()
        
        # Filtro de data
        if 'date_start' in filters and 'date_end' in filters and 'created_at' in filtered_df.columns:
            try:
                # Garantir que created_at é datetime
                filtered_df['created_at'] = pd.to_datetime(filtered_df['created_at'])
                
                # Converter dates para datetime para comparação
                start_date = pd.Timestamp(filters['date_start'])
                end_date = pd.Timestamp(filters['date_end']) + timedelta(days=1)  # Incluir o dia final completo
                
                mask = (filtered_df['created_at'] >= start_date) & (filtered_df['created_at'] < end_date)
                filtered_df = filtered_df[mask]
            except Exception as e:
                logger.warning(f"Erro ao filtrar por data: {e}")
        
        # Filtro de canal
        if filters.get('channel') and filters['channel'] != 'Todos' and 'channel' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['channel'] == filters['channel'].lower()]
        
        # Filtro de status
        if filters.get('status') and filters['status'] != 'Todos' and 'status' in filtered_df.columns:
            status_filter_map = {
                'Resolvido': 'RESOLVED',
                'Não Resolvido': 'UNRESOLVED',
                'Requer Humano': 'HUMAN_REQUESTED'
            }
            status_value = status_filter_map.get(filters['status'], filters['status'])
            filtered_df = filtered_df[filtered_df['status'] == status_value]
        
        # Filtro de lead stage
        if filters.get('lead_stage') and filters['lead_stage'] != 'Todos' and 'lead_stage' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['lead_stage'] == filters['lead_stage'].lower()]
        
        # Filtro de satisfação
        if filters.get('satisfaction') and filters['satisfaction'] != 'Todos' and 'satisfaction_score' in filtered_df.columns:
            if filters['satisfaction'] == 'Alta (4-5)':
                filtered_df = filtered_df[filtered_df['satisfaction_score'] >= 4]
            elif filters['satisfaction'] == 'Média (3)':
                filtered_df = filtered_df[filtered_df['satisfaction_score'] == 3]
            elif filters['satisfaction'] == 'Baixa (1-2)':
                filtered_df = filtered_df[filtered_df['satisfaction_score'] <= 2]
        
        # Filtros avançados
        if filters.get('agent') and filters['agent'] != 'Todos' and 'agent_id' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['agent_id'] == filters['agent']]
        
        if 'response_time_max' in filters and 'first_response_time' in filtered_df.columns:
            max_seconds = filters['response_time_max'] * 60
            filtered_df = filtered_df[filtered_df['first_response_time'] <= max_seconds]
        
        if 'min_messages' in filters and filters['min_messages'] > 0 and 'message_count' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['message_count'] >= filters['min_messages']]
        
        if 'max_frustration' in filters and 'frustration_level' in filtered_df.columns:
            filtered_df = filtered_df[pd.to_numeric(filtered_df['frustration_level'], errors='coerce') <= filters['max_frustration']]
        
        logger.info(f"✅ Filtros aplicados: {len(filtered_df)} registros restantes")
        
        return filtered_df
    
    def get_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula estatísticas resumidas"""
        
        if df.empty:
            return {}
        
        stats = {
            'total_conversations': len(df),
            'unique_contacts': df['contact_name'].nunique() if 'contact_name' in df.columns else 0,
            'channels': df['channel'].value_counts().to_dict() if 'channel' in df.columns else {},
            'lead_stages': df['lead_stage'].value_counts().to_dict() if 'lead_stage' in df.columns else {},
            'avg_satisfaction': df['satisfaction_score'].mean() if 'satisfaction_score' in df.columns else 0,
            'resolution_rate': (df['resolved'].sum() / len(df) * 100) if 'resolved' in df.columns else 0,
            'avg_response_time': df['first_response_time'].mean() if 'first_response_time' in df.columns else 0,
            'hot_leads_count': df['is_hot_lead'].sum() if 'is_hot_lead' in df.columns else 0
        }
        
        return stats