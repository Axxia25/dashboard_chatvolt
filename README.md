# 🚀 Dashboard Reach IA - Sistema Multi-Cliente

Sistema completo de análise de atendimento e conversão de leads com visual moderno dark theme, sistema de login multi-cliente e análises avançadas de IA.

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.29+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [API](#-api)
- [Desenvolvimento](#-desenvolvimento)
- [Deploy](#-deploy)
- [Troubleshooting](#-troubleshooting)
- [Contribuindo](#-contribuindo)

## 🎯 Visão Geral

O Dashboard Reach IA é uma plataforma completa de análise de atendimento ao cliente e gestão de leads, desenvolvida para empresas que precisam monitorar e otimizar seus processos de vendas e suporte.

### Características Principais

- **🔐 Sistema Multi-Cliente**: Login seguro com ID + Token único
- **🎨 Visual Moderno**: Dark theme inspirado em dashboards profissionais
- **📊 Análises Avançadas**: Funil de conversão, análise de sentimento, lead scoring
- **⚡ Tempo Real**: Atualização automática de dados a cada 30 segundos
- **📱 Responsivo**: Funciona perfeitamente em desktop e mobile
- **🌐 Multi-Canal**: Suporte para WhatsApp, Email, Telefone, Chat

## ✨ Funcionalidades

### Dashboard Principal
- Cards de métricas com variação percentual
- Gráficos interativos (linha, pizza, funil, barras)
- Filtros avançados por período, canal, status, agente
- Exportação de dados em CSV

### Análise de Leads
- **Funil de Conversão**: Visualização completa do processo de vendas
- **Lead Scoring**: Pontuação automática baseada em comportamento
- **Hot Leads**: Identificação automática de oportunidades quentes
- **Análise de Sentimento**: IA detecta satisfação do cliente

### Gestão Multi-Cliente
- Login seguro com autenticação dupla (ID + Token)
- Dados isolados por cliente
- Planilha mestre para gestão centralizada
- Logs de acesso e auditoria

### Visualizações
- Evolução temporal de contatos
- Distribuição por canal de atendimento
- Performance individual por agente
- Volume de mensagens por período
- Mapa de calor de horários de pico

## 🏗️ Arquitetura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│  Google Sheets  │────▶│  Streamlit App   │────▶│   Dashboard     │
│   (Data Store)  │     │   (Processing)   │     │  (Visualization)│
│                 │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        ▲                        │
        │                        │
        └────────────────────────┘
          Auto-sync (5 min)
```

### Stack Tecnológico

- **Frontend**: Streamlit + Plotly
- **Backend**: Python 3.9+
- **Database**: Google Sheets
- **Auth**: Custom JWT-like system
- **Deploy**: Streamlit Cloud
- **CI/CD**: GitHub Actions

## 🛠️ Instalação

### Pré-requisitos

- Python 3.9 ou superior
- Conta Google com acesso ao Google Sheets
- Git

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/chatvolt-dashboard.git
cd chatvolt-dashboard
```

2. **Crie ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale dependências**
```bash
pip install -r requirements.txt
```

4. **Configure credenciais**
```bash
# Crie arquivo secrets.toml local
mkdir -p .streamlit
touch .streamlit/secrets.toml
```

5. **Execute localmente**
```bash
streamlit run app.py
```

## ⚙️ Configuração

### 1. Google Cloud Setup

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto
3. Ative APIs:
   - Google Sheets API
   - Google Drive API
4. Crie Service Account
5. Baixe credenciais JSON

### 2. Planilha Mestre de Clientes

Estrutura necessária:

| client_id | client_name | token | planilha_id | ativo | created_at |
|-----------|-------------|-------|-------------|-------|------------|
| CLI001 | Cliente A | abc123... | 1Ji8h... | TRUE | 2024-01-15 |

### 3. Planilha de Dados do Cliente

Adicione estas colunas na aba "Contatos":

- `lead_stage` (novo/qualificado/convertido/perdido)
- `lead_qualified_date`
- `lead_converted_date`
- `lead_source`
- `lead_score`

### 4. Arquivo secrets.toml

```toml
# ID da planilha mestre
MASTER_SHEET_ID = "seu_id_aqui"

# Credenciais Google
[GOOGLE_CREDENTIALS]
type = "service_account"
project_id = "seu-projeto"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@...iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

## 📱 Uso

### Login

1. Acesse o dashboard
2. Digite seu ID de cliente (ex: CLI001)
3. Digite seu token de acesso
4. Clique em "Entrar"

### Navegação

- **Visão Geral**: Métricas principais e gráficos gerais
- **Funil de Conversão**: Análise do processo de vendas
- **Análise de Mensagens**: Volume e distribuição temporal
- **Performance**: Rankings e análise por agente
- **Dados Detalhados**: Tabela completa com exportação

### Filtros

- **Período**: Últimos 7/30 dias ou customizado
- **Canal**: WhatsApp, Email, Telefone, etc
- **Status**: Resolvido, Pendente, Escalado
- **Lead Stage**: Novo, Qualificado, Convertido
- **Satisfação**: Alta, Média, Baixa

## 📁 Estrutura do Projeto

```
chatvolt-dashboard/
├── app.py                      # Aplicação principal
├── requirements.txt            # Dependências
├── .gitignore                 # Git ignore
├── README.md                  # Este arquivo
│
├── src/                       # Código fonte
│   ├── components/            # Componentes UI
│   │   ├── metrics.py        # Cards de métricas
│   │   ├── charts.py         # Gráficos
│   │   └── filters.py        # Filtros
│   │
│   ├── data/                  # Manipulação de dados
│   │   ├── collectors.py     # Coleta dados
│   │   └── processors.py     # Processamento
│   │
│   ├── utils/                 # Utilidades
│   │   └── auth.py           # Autenticação
│   │
│   └── styles/                # Estilos
│       └── dark_theme.py     # Tema escuro
│
└── config/                    # Configurações
    └── settings.py           # Config geral
```

## 🔌 API

### Endpoints Internos

```python
# Autenticação
auth_manager.authenticate(client_id, token)

# Coleta de dados
collector.load_data()

# Processamento
processor.process_data(df, filters)
```

### Estrutura de Dados

```python
# Lead
{
    'conversation_id': str,
    'lead_stage': 'novo|qualificado|convertido|perdido',
    'lead_score': int,
    'is_hot_lead': bool,
    ...
}
```

## 💻 Desenvolvimento

### Setup de Desenvolvimento

```bash
# Instalar em modo desenvolvimento
pip install -e .

# Instalar ferramentas de dev
pip install black flake8 pytest

# Executar testes
pytest tests/

# Formatar código
black .

# Lint
flake8 src/
```

### Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 🚀 Deploy

### Streamlit Cloud

1. Push código para GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte repositório
4. Configure secrets
5. Deploy!

### Docker (Alternativo)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

## 🔧 Troubleshooting

### Problemas Comuns

**Erro de autenticação Google**
- Verifique se service account tem acesso às planilhas
- Confirme formato correto do JSON de credenciais

**Dados não aparecem**
- Verifique ID da planilha
- Confirme que aba "Contatos" existe
- Valide formato das datas

**Performance lenta**
- Ative cache (5 minutos padrão)
- Limite período de dados
- Use filtros para reduzir volume

### Logs

```python
# Ativar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Atualizações

- **v1.0**: Dashboard completo com métricas básicas
- **v1.1**: (Planejado) Alertas em tempo real
- **v1.2**: (Planejado) Relatórios automatizados
- **v1.3**: (Planejado) ML para previsão de demanda
