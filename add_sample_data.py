#!/usr/bin/env python3
"""
Script para adicionar dados de exemplo na planilha Google Sheets
Execute: python add_sample_data.py
"""

import gspread
from google.oauth2.service_account import Credentials
import json

# Configurações
PLANILHA_ID = "1Ji8hgGiQanGKMqblxRzkA_E_sLoI6AnpapmU72nXHsA"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def load_credentials():
    """Carrega credenciais do arquivo collector_config.json"""
    try:
        with open('collector_config.json', 'r') as f:
            config = json.load(f)
        return config['google_credentials']
    except Exception as e:
        print(f"❌ Erro ao carregar credenciais: {e}")
        print("💡 Certifique-se de que o arquivo collector_config.json existe")
        return None

def add_sample_data():
    """Adiciona dados de exemplo na planilha"""
    print("🚀 Adicionando dados de exemplo na planilha...")
    
    # Carregar credenciais
    creds_dict = load_credentials()
    if not creds_dict:
        return False
    
    try:
        # Conectar com Google Sheets
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(PLANILHA_ID)
        
        # Verificar/criar aba Conversas
        try:
            worksheet = sheet.worksheet('Conversas')
            print("✅ Aba 'Conversas' encontrada")
        except:
            print("📄 Criando aba 'Conversas'...")
            worksheet = sheet.add_worksheet(title="Conversas", rows="100", cols="20")
        
        # Cabeçalhos
        headers = [
            'conversation_id', 'created_at', 'updated_at', 'status', 'priority',
            'channel', 'visitor_id', 'agent_id', 'frustration_level',
            'first_response_time', 'resolution_time', 'message_count',
            'satisfaction_score', 'resolved', 'escalated_to_human',
            'contact_name', 'contact_email'
        ]
        
        # Verificar se cabeçalhos já existem
        existing_headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
        
        if not existing_headers:
            print("📋 Adicionando cabeçalhos...")
            worksheet.append_row(headers)
        else:
            print("✅ Cabeçalhos já existem")
        
        # Dados de exemplo
        sample_data = [
            ['conv_001', '03/09/2025 08:30:00', '03/09/2025 09:15:00', 'RESOLVED', 'HIGH', 'whatsapp', 'user_001', 'agent_001', '2', '45', '45', '8', '4', 'true', 'false', 'João Silva', 'joao@email.com'],
            ['conv_002', '03/09/2025 09:15:00', '03/09/2025 09:45:00', 'RESOLVED', 'MEDIUM', 'dashboard', 'user_002', 'agent_002', '1', '30', '30', '5', '5', 'true', 'false', 'Maria Santos', 'maria@email.com'],
            ['conv_003', '03/09/2025 10:00:00', '03/09/2025 10:30:00', 'UNRESOLVED', 'LOW', 'whatsapp', 'user_003', 'agent_001', '3', '60', '0', '12', '2', 'false', 'false', 'Carlos Lima', 'carlos@email.com'],
            ['conv_004', '03/09/2025 11:20:00', '03/09/2025 12:00:00', 'HUMAN_REQUESTED', 'HIGH', 'api', 'user_004', 'agent_003', '4', '90', '40', '15', '3', 'false', 'true', 'Ana Costa', 'ana@email.com'],
            ['conv_005', '03/09/2025 13:45:00', '03/09/2025 14:15:00', 'RESOLVED', 'MEDIUM', 'whatsapp', 'user_005', 'agent_002', '1', '25', '30', '6', '5', 'true', 'false', 'Pedro Oliveira', 'pedro@email.com'],
            ['conv_006', '03/09/2025 14:30:00', '03/09/2025 15:00:00', 'RESOLVED', 'LOW', 'dashboard', 'user_006', 'agent_001', '2', '35', '30', '4', '4', 'true', 'false', 'Luiza Ferreira', 'luiza@email.com'],
            ['conv_007', '03/09/2025 15:15:00', '03/09/2025 16:00:00', 'UNRESOLVED', 'MEDIUM', 'whatsapp', 'user_007', 'agent_003', '3', '75', '0', '18', '2', 'false', 'false', 'Roberto Alves', 'roberto@email.com'],
            ['conv_008', '03/09/2025 16:20:00', '03/09/2025 17:00:00', 'RESOLVED', 'HIGH', 'api', 'user_008', 'agent_002', '1', '20', '40', '7', '5', 'true', 'false', 'Carla Mendes', 'carla@email.com'],
            ['conv_009', '02/09/2025 09:00:00', '02/09/2025 09:30:00', 'RESOLVED', 'MEDIUM', 'whatsapp', 'user_009', 'agent_001', '2', '40', '30', '5', '4', 'true', 'false', 'Felipe Santos', 'felipe@email.com'],
            ['conv_010', '02/09/2025 11:30:00', '02/09/2025 12:15:00', 'HUMAN_REQUESTED', 'HIGH', 'dashboard', 'user_010', 'agent_003', '5', '120', '45', '20', '1', 'false', 'true', 'Fernanda Lima', 'fernanda@email.com'],
            ['conv_011', '01/09/2025 14:00:00', '01/09/2025 14:45:00', 'RESOLVED', 'LOW', 'whatsapp', 'user_011', 'agent_002', '1', '35', '45', '8', '4', 'true', 'false', 'Gabriel Costa', 'gabriel@email.com'],
            ['conv_012', '01/09/2025 16:45:00', '01/09/2025 17:30:00', 'RESOLVED', 'MEDIUM', 'api', 'user_012', 'agent_001', '2', '50', '45', '6', '5', 'true', 'false', 'Isabella Rocha', 'isabella@email.com']
        ]
        
        # Verificar quantas linhas já existem
        existing_rows = len(worksheet.get_all_values())
        
        if existing_rows <= 1:  # Só cabeçalho ou vazio
            print("📊 Adicionando dados de exemplo...")
            for row in sample_data:
                worksheet.append_row(row)
            print(f"✅ {len(sample_data)} linhas de dados adicionadas!")
        else:
            print(f"⚠️ Planilha já tem {existing_rows-1} linhas de dados")
            response = input("🤔 Adicionar mais dados mesmo assim? (s/n): ")
            if response.lower().startswith('s'):
                for row in sample_data:
                    worksheet.append_row(row)
                print(f"✅ {len(sample_data)} linhas adicionais inseridas!")
        
        # Resumo final
        final_rows = len(worksheet.get_all_values())
        print(f"\n📊 RESUMO:")
        print(f"   Total de linhas na planilha: {final_rows}")
        print(f"   Total de dados (sem cabeçalho): {final_rows - 1}")
        print(f"   URL da planilha: https://docs.google.com/spreadsheets/d/{PLANILHA_ID}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar dados: {e}")
        return False

def main():
    """Função principal"""
    print("🎯 SCRIPT DE DADOS DE EXEMPLO - DASHBOARD CHATVOLT")
    print("=" * 60)
    
    success = add_sample_data()
    
    if success:
        print("\n🎉 DADOS ADICIONADOS COM SUCESSO!")
        print("🚀 Agora você pode testar o dashboard com:")
        print("   streamlit run dashboard_chatvolt.py")
    else:
        print("\n😞 Falha ao adicionar dados.")
        print("🔧 Verifique se:")
        print("   - O arquivo collector_config.json existe")
        print("   - As credenciais estão corretas")
        print("   - A planilha está compartilhada com a service account")

if __name__ == "__main__":
    main()
