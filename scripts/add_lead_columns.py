#!/usr/bin/env python3
"""
Script para adicionar colunas de lead tracking em planilhas existentes
Adiciona as colunas necessárias para o funil de conversão
"""

import gspread
from google.oauth2.service_account import Credentials
import sys
from datetime import datetime

# Configurações
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def add_lead_columns(sheet_id: str, credentials_path: str = None):
    """
    Adiciona colunas de lead tracking na planilha
    
    Args:
        sheet_id: ID da planilha Google Sheets
        credentials_path: Caminho para arquivo JSON de credenciais (opcional)
    """
    print(f"🚀 Adicionando colunas de lead tracking na planilha: {sheet_id}")
    
    try:
        # Autenticar
        if credentials_path:
            creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        else:
            # Usar secrets do Streamlit
            import streamlit as st
            creds_dict = dict(st.secrets['GOOGLE_CREDENTIALS'])
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        
        client = gspread.authorize(creds)
        
        # Abrir planilha
        sheet = client.open_by_key(sheet_id)
        
        # Procurar aba Contatos ou similar
        worksheet = None
        for ws_name in ['Contatos', 'Contacts', 'Conversas', 'Sheet1']:
            try:
                worksheet = sheet.worksheet(ws_name)
                print(f"✅ Aba '{ws_name}' encontrada")
                break
            except:
                continue
        
        if not worksheet:
            print("❌ Nenhuma aba de dados encontrada")
            return False
        
        # Obter headers atuais
        current_headers = worksheet.row_values(1)
        if not current_headers:
            print("❌ Planilha sem headers")
            return False
        
        print(f"📊 Headers atuais: {len(current_headers)} colunas")
        
        # Novas colunas para adicionar
        new_columns = [
            'lead_stage',           # novo/qualificado/convertido/perdido
            'lead_qualified_date',  # Data de qualificação
            'lead_converted_date',  # Data de conversão
            'lead_source',         # Origem do lead
            'lead_score',          # Pontuação do lead (0-100)
            'lead_value',          # Valor potencial
            'lead_notes',          # Observações sobre o lead
            'lead_owner',          # Responsável pelo lead
            'lead_campaign',       # Campanha de origem
            'lead_tags'           # Tags do lead
        ]
        
        # Verificar quais já existem
        columns_to_add = [col for col in new_columns if col not in current_headers]
        
        if not columns_to_add:
            print("✅ Todas as colunas já existem!")
            return True
        
        print(f"\n📝 Colunas a adicionar: {', '.join(columns_to_add)}")
        
        # Calcular posição para novas colunas
        last_col_index = len(current_headers)
        
        # Adicionar headers
        for i, col_name in enumerate(columns_to_add):
            col_letter = gspread.utils.rowcol_to_a1(1, last_col_index + i + 1)
            worksheet.update(col_letter, [[col_name]])
            print(f"✅ Adicionada coluna: {col_name} em {col_letter}")
        
        # Adicionar valores padrão para linhas existentes
        total_rows = len(worksheet.get_all_values())
        if total_rows > 1:
            print(f"\n📊 Preenchendo valores padrão para {total_rows - 1} linhas...")
            
            # Preparar valores padrão
            default_values = []
            for row in range(2, total_rows + 1):
                row_defaults = []
                for col in columns_to_add:
                    if col == 'lead_stage':
                        row_defaults.append('novo')
                    elif col == 'lead_score':
                        row_defaults.append('0')
                    elif col == 'lead_value':
                        row_defaults.append('0')
                    else:
                        row_defaults.append('')
                
                default_values.append(row_defaults)
            
            # Atualizar em lote
            if default_values:
                start_cell = gspread.utils.rowcol_to_a1(2, last_col_index + 1)
                end_cell = gspread.utils.rowcol_to_a1(total_rows, last_col_index + len(columns_to_add))
                cell_range = f"{start_cell}:{end_cell}"
                
                worksheet.update(cell_range, default_values)
                print(f"✅ Valores padrão adicionados")
        
        # Adicionar formatação condicional (opcional)
        print("\n🎨 Aplicando formatação...")
        
        # Encontrar índice da coluna lead_stage
        all_headers = worksheet.row_values(1)
        if 'lead_stage' in all_headers:
            stage_col_index = all_headers.index('lead_stage') + 1
            
            # Definir regras de formatação
            formatting_rules = {
                'novo': {'backgroundColor': {'red': 0.3, 'green': 0.5, 'blue': 0.8}},
                'qualificado': {'backgroundColor': {'red': 0.9, 'green': 0.6, 'blue': 0.2}},
                'convertido': {'backgroundColor': {'red': 0.2, 'green': 0.7, 'blue': 0.3}},
                'perdido': {'backgroundColor': {'red': 0.8, 'green': 0.2, 'blue': 0.2}}
            }
            
            # Aplicar formatação seria feito aqui com batch update
            # (requer API mais avançada)
        
        print("\n✅ Colunas de lead tracking adicionadas com sucesso!")
        print(f"📊 Planilha atualizada: {worksheet.title}")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("ADICIONAR COLUNAS DE LEAD TRACKING")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\n❌ Uso: python add_lead_columns.py <SHEET_ID> [credentials.json]")
        print("\nExemplo:")
        print("python add_lead_columns.py 1Ji8hgGiQanGKMqblxRzkA_E_sLoI6AnpapmU72nXHsA")
        print("python add_lead_columns.py 1Ji8hgGiQanGKMqblxRzkA_E_sLoI6AnpapmU72nXHsA credentials.json")
        return
    
    sheet_id = sys.argv[1]
    credentials_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Confirmar
    print(f"\n📋 Planilha ID: {sheet_id}")
    if credentials_path:
        print(f"🔐 Credenciais: {credentials_path}")
    else:
        print("🔐 Credenciais: Usando configuração do Streamlit")
    
    response = input("\nDeseja continuar? (s/n): ")
    if response.lower() != 's':
        print("Operação cancelada.")
        return
    
    # Executar
    success = add_lead_columns(sheet_id, credentials_path)
    
    if success:
        print("\n🎉 Processo concluído com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Verifique as novas colunas na planilha")
        print("2. Preencha os dados de lead_stage para conversas existentes")
        print("3. Configure automações para preencher automaticamente")
    else:
        print("\n😞 Processo falhou. Verifique os erros acima.")

if __name__ == "__main__":
    main()