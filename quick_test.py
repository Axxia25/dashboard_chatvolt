#!/usr/bin/env python3
"""
TESTE RÁPIDO DO DASHBOARD CHATVOLT
Execute antes de fazer deploy para verificar se tudo funciona
"""

import sys
import os
import json

def check_files():
    """Verifica se todos os arquivos necessários existem"""
    print("📁 Verificando arquivos...")
    
    required_files = [
        'dashboard_chatvolt.py',
        'requirements.txt',
        '.gitignore',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - AUSENTE")
            missing_files.append(file)
    
    return len(missing_files) == 0

def check_config():
    """Verifica configuração local"""
    print("\n🔧 Verificando configuração...")
    
    if os.path.exists('collector_config.json'):
        try:
            with open('collector_config.json', 'r') as f:
                config = json.load(f)
            
            required_keys = ['chatvolt_api_key', 'google_sheets_id', 'google_credentials']
            
            for key in required_keys:
                if key in config:
                    if key == 'chatvolt_api_key':
                        value = config[key][:15] + '...' if len(config[key]) > 15 else config[key]
                        print(f"   ✅ {key}: {value}")
                    elif key == 'google_sheets_id':
                        print(f"   ✅ {key}: {config[key]}")
                    else:
                        print(f"   ✅ {key}: [configurado]")
                else:
                    print(f"   ❌ {key}: AUSENTE")
                    return False
            
            return True
            
        except Exception as e:
            print(f"   ❌ Erro ao ler collector_config.json: {e}")
            return False
    else:
        print("   ⚠️ collector_config.json não encontrado (OK se for deploy no Streamlit Cloud)")
        return True

def check_dependencies():
    """Verifica se dependências podem ser importadas"""
    print("\n📦 Verificando dependências...")
    
    dependencies = [
        'streamlit',
        'pandas', 
        'plotly',
        'gspread',
        'google.oauth2.service_account',
        'requests'
    ]
    
    missing_deps = []
    for dep in dependencies:
        try:
            if dep == 'google.oauth2.service_account':
                from google.oauth2.service_account import Credentials
            else:
                __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - NÃO INSTALADO")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n💡 Para instalar dependências ausentes:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_dashboard_syntax():
    """Verifica se o dashboard não tem erros de sintaxe"""
    print("\n🐍 Verificando sintaxe do dashboard...")
    
    try:
        import ast
        with open('dashboard_chatvolt.py', 'r') as f:
            source = f.read()
        
        ast.parse(source)
        print("   ✅ Sintaxe do Python OK")
        
        # Verificar IDs importantes
        if 'YOUR_GOOGLE_SHEETS_ID' in source:
            print("   ⚠️ PLANILHA_ID ainda é placeholder - precisa ser atualizado")
            return False
        elif '1Ji8hgGiQanGKMqblxRzkA_E_sLoI6AnpapmU72nXHsA' in source:
            print("   ✅ PLANILHA_ID configurado corretamente")
        
        return True
        
    except SyntaxError as e:
        print(f"   ❌ Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erro ao verificar arquivo: {e}")
        return False

def simulate_streamlit_test():
    """Simula teste básico do Streamlit"""
    print("\n🚀 Teste de simulação Streamlit...")
    
    try:
        # Importar componentes principais
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        
        print("   ✅ Imports principais OK")
        
        # Testar criação de DataFrame básico
        test_data = {
            'conversation_id': ['test_1', 'test_2'],
            'status': ['RESOLVED', 'UNRESOLVED'],
            'created_at': ['03/09/2025 10:00:00', '03/09/2025 11:00:00']
        }
        df = pd.DataFrame(test_data)
        df['created_at'] = pd.to_datetime(df['created_at'], format='%d/%m/%Y %H:%M:%S')
        
        print("   ✅ Processamento de dados OK")
        
        # Testar criação de gráfico básico
        fig = px.pie(values=[1, 1], names=['A', 'B'])
        print("   ✅ Geração de gráficos OK")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na simulação: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 TESTE RÁPIDO - DASHBOARD CHATVOLT")
    print("=" * 50)
    
    tests = [
        ("Arquivos", check_files),
        ("Configuração", check_config),
        ("Dependências", check_dependencies),
        ("Sintaxe", check_dashboard_syntax),
        ("Simulação", simulate_streamlit_test)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name:.<15} {status}")
        if result:
            passed += 1
    
    success_rate = (passed / len(results)) * 100
    print(f"\n🎯 TAXA DE SUCESSO: {passed}/{len(results)} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 Dashboard pronto para:")
        print("   • Teste local: streamlit run dashboard_chatvolt.py")
        print("   • Deploy no Streamlit Cloud")
        print("   • Adicionar dados: python add_sample_data.py")
    elif success_rate >= 80:
        print("\n👍 MAIORIA DOS TESTES PASSOU!")
        print("⚠️ Corrija os problemas menores antes do deploy")
    else:
        print("\n😞 MUITOS PROBLEMAS ENCONTRADOS")
        print("🔧 Corrija os erros antes de continuar")
    
    return success_rate == 100

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
