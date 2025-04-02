# Guia Rápido do Sistema API Clima

Este guia oferece instruções passo a passo para começar a usar o Sistema API Clima rapidamente. Siga os exemplos práticos para configurar, executar e aproveitar os dados climáticos.

## 🚀 Primeiros Passos

### Instalação em 5 minutos

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/sistema_api_clima.git
cd sistema_api_clima

# 2. Configure o ambiente
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure suas chaves de API (obrigatório)
# Linux/Mac
export OPENWEATHER_API_KEY="sua_chave_aqui"
# ou Windows (PowerShell)
$env:OPENWEATHER_API_KEY="sua_chave_aqui"

# 5. Gere a configuração padrão
python -m src.main --gerar-config

# 6. Execute pela primeira vez
python -m src.main
```

## 🔧 Exemplos Práticos

### Exemplo 1: Monitorar São Paulo e Rio de Janeiro (dados diários)

1. Edite o arquivo `config/config.yaml`:
   ```yaml
   localidades:
     - nome: "São Paulo"
       latitude: -23.5505
       longitude: -46.6333
     - nome: "Rio de Janeiro"
       latitude: -22.9068
       longitude: -43.1729
   ```

2. Execute:
   ```bash
   python -m src.main --frequencia diaria
   ```

3. Verifique os resultados:
   ```bash
   ls dados/
   # Você verá arquivos como:
   # clima_sao_paulo_diario.csv
   # clima_rio_de_janeiro_diario.csv
   ```

### Exemplo 2: Análise histórica mensal do clima em Brasília

1. Configure apenas Brasília no arquivo `config/config.yaml`:
   ```yaml
   localidades:
     - nome: "Brasília"
       latitude: -15.7801
       longitude: -47.9292
   ```

2. Execute com dados históricos:
   ```bash
   python -m src.main --frequencia mensal --historico --anos-historico 5
   ```

3. Analise os resultados:
   ```python
   import pandas as pd
   import matplotlib.pyplot as plt

   # Carregue os dados
   df = pd.read_csv('dados/clima_brasilia_mensal.csv')
   
   # Visualize a temperatura média por mês
   df['ano_mes'] = pd.to_datetime(df['ano_mes'] + '-01')
   plt.figure(figsize=(12, 6))
   plt.plot(df['ano_mes'], df['temperatura_media'])
   plt.title('Temperatura Média Mensal em Brasília')
   plt.grid(True)
   plt.xticks(rotation=45)
   plt.tight_layout()
   plt.show()
   ```

### Exemplo 3: Comparação entre regiões (modo JSON)

1. Configure múltiplas regiões no `config/config.yaml`:
   ```yaml
   localidades:
     - nome: "Recife"
       latitude: -8.0584
       longitude: -34.8848
     - nome: "Porto Alegre"
       latitude: -30.0277
       longitude: -51.2287
   ```

2. Execute com saída JSON:
   ```bash
   python -m src.main --formato-saida json --tipo-arquivo concatenado
   ```

3. Analise os resultados:
   ```python
   import json
   import pandas as pd
   
   # Carregue os dados
   with open('dados/clima_todas_localidades_diario.json', 'r') as f:
       dados = json.load(f)
   
   # Converta para DataFrame
   df = pd.DataFrame(dados)
   
   # Compare a temperatura entre cidades
   df_pivot = df.pivot(index='data', columns='localidade', values='temperatura_media')
   df_pivot.plot(figsize=(12, 6), title='Comparação de Temperatura')
   plt.grid(True)
   plt.show()
   ```

## 📊 Visualizações Rápidas

### Dashboard Básico com Dados Diários

```python
import pandas as pd
import matplotlib.pyplot as plt

# Carregue os dados
df = pd.read_csv('dados/clima_sao_paulo_diario.csv')

# Configure o dashboard
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Dashboard Climático - São Paulo', fontsize=16)

# Gráfico 1: Temperatura (min, média, max)
df.plot(x='data', y=['temperatura_minima', 'temperatura_media', 'temperatura_maxima'], 
        ax=axes[0,0], title='Temperaturas')
axes[0,0].grid(True)

# Gráfico 2: Precipitação
df.plot(x='data', y='chuva_precipitacao', kind='bar', ax=axes[0,1], 
        title='Precipitação (mm)', color='blue')
axes[0,1].grid(True)

# Gráfico 3: Umidade
df.plot(x='data', y='umidade_media', ax=axes[1,0], title='Umidade (%)', color='green')
axes[1,0].grid(True)

# Gráfico 4: Amplitude térmica
df.plot(x='data', y='amplitude_termica', kind='bar', ax=axes[1,1], 
        title='Amplitude Térmica (°C)', color='red')
axes[1,1].grid(True)

plt.tight_layout()
plt.subplots_adjust(top=0.9)
plt.show()
```

## 🛠️ Tarefas de Manutenção Comuns

### Atualização Diária Automatizada

Arquivo `atualizar_clima.sh`:
```bash
#!/bin/bash
cd /caminho/para/sistema_api_clima
source venv/bin/activate
export OPENWEATHER_API_KEY="sua_chave_aqui"
python -m src.main
```

Configure no crontab (Linux/Mac):
```bash
0 6 * * * /caminho/para/atualizar_clima.sh >> /caminho/para/logs/clima.log 2>&1
```

### Limpeza de Dados Antigos

Script `limpar_dados_antigos.py`:
```python
"""Script para manter apenas os dados dos últimos X meses."""
import os
import glob
import pandas as pd
from datetime import datetime, timedelta

# Configurações
DIRETORIO = 'dados'
MESES_MANTER = 6

# Data limite
data_limite = (datetime.now() - timedelta(days=30*MESES_MANTER)).strftime('%Y-%m-%d')

# Processa arquivos CSV
for arquivo in glob.glob(f'{DIRETORIO}/*.csv'):
    try:
        # Lê o arquivo
        df = pd.read_csv(arquivo)
        
        # Verifica se tem coluna de data
        if 'data' in df.columns:
            # Filtra para manter apenas dados recentes
            df_filtrado = df[df['data'] >= data_limite]
            
            # Se houver redução, salva o arquivo
            if len(df_filtrado) < len(df):
                df_filtrado.to_csv(arquivo, index=False)
                print(f"Arquivo {arquivo} atualizado. Removidos {len(df) - len(df_filtrado)} registros antigos.")
        
    except Exception as e:
        print(f"Erro ao processar {arquivo}: {str(e)}")
```

## 🔍 Dicas e Truques

### Aumento de Performance

Para coletar dados de muitas localidades mais rapidamente:

```bash
# Divida em grupos e execute em paralelo
python -m src.main --config config/grupo1.yaml &
python -m src.main --config config/grupo2.yaml &
```

### Alternância entre APIs

Se estiver próximo do limite de requisições da API OpenWeather:

```bash
# Manhã: use OpenWeather
python -m src.main --modo-api principal

# Tarde: use INMET
python -m src.main --modo-api reserva
```

### Formato para Ciência de Dados

Para usar em projetos de machine learning:

```bash
# Formato Parquet é mais eficiente
python -m src.main --formato-saida parquet --tipo-arquivo concatenado
```

## 📱 Notificações de Alerta

Script para alertar sobre condições extremas:
```python
import pandas as pd
import requests

# Carregar os últimos dados
df = pd.read_csv('dados/clima_sao_paulo_diario.csv')
ultimo_dia = df.iloc[-1]

# Verificar condições de alerta
alertas = []
if ultimo_dia['temperatura_maxima'] > 35:
    alertas.append(f"ALERTA DE CALOR: {ultimo_dia['temperatura_maxima']}°C")
if ultimo_dia['chuva_precipitacao'] > 50:
    alertas.append(f"ALERTA DE CHUVA INTENSA: {ultimo_dia['chuva_precipitacao']}mm")

# Enviar alerta (exemplo com webhook)
if alertas:
    mensagem = "\n".join(alertas)
    requests.post('https://seu-webhook.exemplo/alertas', 
                 json={'text': f"Alertas climáticos: {mensagem}"})
```

## 🔄 Integração com Outras Ferramentas

### Exportação para Google Sheets

```python
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Carregar dados
df = pd.read_csv('dados/clima_sao_paulo_diario.csv')

# Configurar credenciais
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gc = gspread.authorize(credentials)

# Abrir planilha
sheet = gc.open('Monitoramento Climático').worksheet('Dados Diários')

# Limpar planilha
sheet.clear()

# Adicionar cabeçalho
sheet.append_row(df.columns.tolist())

# Adicionar dados
sheet.append_rows(df.values.tolist())
```

## 🔧 Resolução Rápida de Problemas

### Problema: "Nenhum dado encontrado"

Solução rápida:
```bash
# Verifique se as chaves de API estão configuradas
echo $OPENWEATHER_API_KEY

# Teste a conexão básica com a API
curl "https://api.openweathermap.org/data/2.5/weather?lat=-23.5505&lon=-46.6333&appid=$OPENWEATHER_API_KEY"

# Tente usar ambas as APIs
python -m src.main --modo-api ambas -v
```

### Problema: "Arquivo não pode ser criado"

Solução rápida:
```bash
# Verifique se o diretório de dados existe
mkdir -p dados

# Verifique permissões
chmod 755 dados

# Use um caminho alternativo
python -m src.main --diretorio-saida ./tmp_dados
```

## ⚙️ Integrações Avançadas (Exemplos)

### Webhook para Notificação de Coleta

```python
import requests
import json
import os
from datetime import datetime

def notificar_coleta(arquivos, status="sucesso"):
    """Notifica uma API externa sobre a coleta de dados."""
    webhook_url = os.environ.get('WEBHOOK_URL')
    if not webhook_url:
        return
    
    payload = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "arquivos": arquivos,
        "sistema": "API Clima"
    }
    
    try:
        requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        print(f"Erro ao notificar: {str(e)}")

# Uso:
# notificar_coleta(['clima_sao_paulo_diario.csv', 'clima_rio_de_janeiro_diario.csv'])
```