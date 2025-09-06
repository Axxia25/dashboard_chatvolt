# 💬 Dashboard Chatvolt Analytics

Sistema completo de métricas de atendimento em tempo real usando a API Chatvolt.

## 🚀 Funcionalidades

### 📊 Métricas Completas
- **Histórico de mensagens** completo por conversa
- **Tempo de atendimento** (primeira resposta e resolução)
- **Quantidade de atendimentos** por período
- **Taxa de resolução** e escalação para humanos
- **Horários de pico** com mapa de calor
- **Satisfação do cliente** com scoring 1-5
- **Conversas não respondidas** e abandonadas
- **Performance por agente** e canal
- **Análise de frustração** dos clientes

### ⚡ Tempo Real & Filtros
- **Auto-refresh** a cada 30 segundos
- **Filtros flexíveis** por período, canal, status, prioridade
- **Múltiplas fontes** de dados (Google Sheets + API)
- **Cache inteligente** para performance

## 🛠️ Configuração

### 1. Pré-requisitos

```bash
# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar API Chatvolt

1. Acesse [Chatvolt Settings](https://app.chatvolt.ai/settings/api-keys)
2. Gere uma nova API Key
3. Configure no Streamlit Cloud em **Settings > Secrets**:

```toml
# secrets.toml
chatvolt_api_key = "sua_api_key_aqui"
```

### 3. Configurar Google Sheets

1. Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/)
2. Ative as APIs: **Google Sheets API** e **Google Drive API**
3. Crie credenciais de conta de serviço (Service Account)
4. Baixe o arquivo JSON das credenciais
5. Configure no Streamlit Cloud:

```toml
# secrets.toml
[GOOGLE_CREDENTIALS]
type = "service_account"
project_id = "seu-projeto"
private_key_id = "key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nsua-chave-aqui\n-----END PRIVATE KEY-----\n"
client_email = "nome@projeto.iam.gserviceaccount.com"
client_id = "client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

### 4. Criar Planilha Google Sheets

Crie uma planilha com as seguintes colunas na aba "Conversas":

| Coluna | Descrição |
|--------|-----------|
| conversation_id | ID único da conversa |
| created_at | Data/hora de criação |
| updated_at | Data/hora da última atualização |
| status | RESOLVED/UNRESOLVED/HUMAN_REQUESTED |
| priority | HIGH/MEDIUM/LOW |
| channel | whatsapp/dashboard/api |
| visitor_id | ID do visitante |
| agent_id | ID do agente |
| frustration_level | Nível 1-5 |
| first_response_time | Tempo primeira resposta (segundos) |
| resolution_time | Tempo total resolução (minutos) |
| message_count | Número de mensagens |
| satisfaction_score | Satisfação 1-5 |
| resolved | true/false |
| escalated_to_human | true/false |
| contact_name | Nome do contato |
| contact_email | Email do contato |

### 5. Configurar ID da Planilha

No arquivo principal, substitua:
```python
PLANILHA_ID = "YOUR_GOOGLE_SHEETS_ID"
```

Pelo ID da sua planilha (extraído da URL).

## 🔗 Integração Automática com Make

Para coleta automática de dados da API Chatvolt:

### 1. Configurar Make (formerly Integromat)

1. Acesse [Make](https://www.make.com/)
2. Crie novo cenário
3. Adicione trigger: **Chatvolt AI** > **Watch Conversations**
4. Configure ação: **Google Sheets** > **Add a Row**

### 2. Template Make

```json
{
  "scenario": {
    "name": "Chatvolt → Google Sheets",
    "modules": [
      {
        "module": "chatvolt:watch_conversations",
        "webhook": true
      },
      {
        "module": "google_sheets:add_row",
        "data": {
          "spreadsheet_id": "{{sheets_id}}",
          "values": [
            "{{conversation.id}}",
            "{{conversation.createdAt}}",
            "{{conversation.status}}",
            "{{conversation.priority}}",
            "{{conversation.channel}}",
            "{{conversation.frustrationLevel}}"
          ]
        }
      }
    ]
  }
}
```

## 🚀 Deploy no Streamlit Cloud

1. Faça fork deste repositório
2. Acesse [Streamlit Cloud](https://share.streamlit.io/)
3. Conecte seu repositório
4. Configure as secrets (API keys)
5. Deploy automático!

## 📊 Uso do Dashboard

### Abas Disponíveis

1. **📊 Visão Geral**: Status, canais, métricas principais
2. **⏱️ Tempo de Atendimento**: SLA, distribuição, estatísticas
3. **📈 Análise Temporal**: Evolução, tendências, sazonalidade  
4. **😤 Frustração**: Níveis de frustração e correlações
5. **📋 Dados Detalhados**: Tabela completa + download CSV

### Filtros Disponíveis

- **Período**: Data inicial e final
- **Canal**: WhatsApp, Dashboard, API
- **Status**: Resolvido, Não resolvido, Escalado
- **Prioridade**: Alta, Média, Baixa
- **Auto-refresh**: Atualização automática

## 📈 Métricas Calculadas

### Principais KPIs
- **Volume total** de conversas
- **Taxa de resolução** (%)
- **Tempo médio** de primeira resposta
- **Tempo médio** de resolução
- **Satisfação média** (1-5)
- **Taxa de escalação** para humanos

### Análises Avançadas
- **Distribuição por status** (pizza)
- **Performance por canal** (barras)
- **Evolução temporal** (linha)
- **Mapa de calor** por horário
- **Histograma** de tempo de resposta
- **SLA por faixas** de tempo

## 🔧 Customização

### Adicionar Nova Métrica

```python
def create_custom_metric(df):
    """Nova métrica customizada"""
    if df.empty:
        return
    
    # Sua lógica aqui
    metric_value = df['campo'].mean()
    
    fig = px.bar(...)
    st.plotly_chart(fig)
```

### Integrar Nova Fonte de Dados

```python
def collect_custom_data():
    """Coletor personalizado"""
    # Conectar com sua API/banco
    data = requests.get("sua_api_url")
    return pd.DataFrame(data.json())
```

## 🔄 Atualizações

- **v1.0**: Dashboard completo com métricas básicas
- **v1.1**: (Planejado) Alertas em tempo real
- **v1.2**: (Planejado) Relatórios automatizados
- **v1.3**: (Planejado) ML para previsão de demanda
