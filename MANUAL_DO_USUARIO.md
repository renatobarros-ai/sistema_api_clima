# Manual do Usuário - Sistema API Clima

Este manual detalha como utilizar o Sistema API Clima, uma ferramenta poderosa para coleta e processamento de dados meteorológicos. Siga as instruções neste documento para aproveitar ao máximo os recursos do sistema.

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Configuração](#2-configuração)
3. [Utilizando o Sistema](#3-utilizando-o-sistema)
4. [Entendendo os Dados](#4-entendendo-os-dados)
5. [Casos de Uso Comuns](#5-casos-de-uso-comuns)
6. [Integração com Análise de Dados](#6-integração-com-análise-de-dados)
7. [Solução de Problemas](#7-solução-de-problemas)
8. [Perguntas Frequentes](#8-perguntas-frequentes)

## 1. Visão Geral

O Sistema API Clima é uma ferramenta para coletar, processar e exportar dados climáticos de diversas fontes. Ele foi desenvolvido para fornecer dados confiáveis para análises meteorológicas e modelos de previsão.

### Componentes Principais

- **Coleta de dados**: Acesso às APIs do OpenWeather e INMET
- **Processamento**: Padronização e enriquecimento dos dados
- **Exportação**: Geração de arquivos em formatos utilizáveis (CSV, JSON, Parquet)

### Fluxo Básico de Operação

1. O sistema lê sua configuração (do arquivo YAML ou linha de comando)
2. Conecta-se às APIs para coletar dados das localidades configuradas
3. Processa os dados conforme os parâmetros definidos
4. Exporta os resultados no formato escolhido

## 2. Configuração

### O Arquivo de Configuração

A configuração do sistema é feita através do arquivo `config/config.yaml`. Este arquivo controla todos os aspectos do funcionamento do sistema.

#### Configuração Geral

```yaml
# Configurações gerais
geral:
  # API a ser utilizada: "principal" (OpenWeather), "reserva" (INMET) ou "ambas"
  modo_api: "principal"
  
  # Formato de saída: "csv", "json" ou "parquet"
  formato_saida: "csv"
  
  # Configurações do arquivo de saída
  arquivo_saida:
    # Tipo de arquivo: "separado" (por localidade) ou "concatenado" (todos juntos)
    tipo: "separado"
    # Diretório onde os arquivos serão salvos
    diretorio: "dados"
```

#### Configuração de Localidades

As localidades são definidas por nome e coordenadas geográficas. Você pode adicionar quantas localidades precisar:

```yaml
# Lista de localidades para coleta de dados
localidades:
  - nome: "São Paulo"
    latitude: -23.5505
    longitude: -46.6333
  - nome: "Rio de Janeiro"
    latitude: -22.9068
    longitude: -43.1729
  - nome: "Brasília"
    latitude: -15.7801
    longitude: -47.9292
```

#### Variáveis Climáticas

Configure quais variáveis climáticas deseja coletar:

```yaml
# Variáveis climáticas a serem coletadas
variaveis:
  - nome: "temperatura"
    unidade: "celsius"  # ou "fahrenheit"
    ativo: true
  - nome: "chuva"
    unidade: "mm"
    ativo: true
  - nome: "umidade"
    unidade: "percentual"
    ativo: true
```

#### Frequência de Coleta

Defina a frequência dos dados e se deseja dados históricos:

```yaml
# Configurações de frequência
frequencia:
  tipo: "diaria"  # "diaria" ou "mensal"
  historico:
    ativo: false
    anos: 5  # Número de anos para dados históricos
```

#### Configuração das APIs

Configuração de conexão com as APIs:

```yaml
# Configurações das APIs
apis:
  openweather:
    chave: "${OPENWEATHER_API_KEY}"  # Usar variável de ambiente
    base_url: "https://api.openweathermap.org/data/2.5"
    timeout: 30
    tentativas: 3
  
  inmet:
    chave: "${INMET_API_KEY}"  # Usar variável de ambiente
    base_url: "https://apitempo.inmet.gov.br/api"
    timeout: 30
    tentativas: 3
```

### Dicas para Configuração Eficiente

- **Localidades**: Use coordenadas precisas para melhores resultados
- **Variáveis**: Desative variáveis que não precisa para economizar processamento
- **Modo API**: Use "ambas" para maior confiabilidade ou "reserva" se tiver limite na API principal
- **Formato de Saída**: Use CSV para compatibilidade, JSON para web ou Parquet para análise avançada

## 3. Utilizando o Sistema

### Execução Básica

Para executar o sistema com as configurações padrão:

```bash
python -m src.main
```

### Opções da Linha de Comando

O sistema oferece várias opções de linha de comando para customizar a execução:

| Opção | Descrição | Exemplo |
|-------|-----------|---------|
| `-c, --config` | Especifica o arquivo de configuração | `--config minha_config.yaml` |
| `--gerar-config` | Gera um arquivo de configuração padrão | `--gerar-config` |
| `--modo-api` | Define o modo da API (principal/reserva/ambas) | `--modo-api ambas` |
| `--formato-saida` | Define o formato de saída (csv/json/parquet) | `--formato-saida json` |
| `--tipo-arquivo` | Define o tipo de arquivo (separado/concatenado) | `--tipo-arquivo concatenado` |
| `--diretorio-saida` | Define o diretório de saída | `--diretorio-saida ./meus_dados` |
| `--frequencia` | Define a frequência (diaria/mensal) | `--frequencia mensal` |
| `--historico` | Ativa a coleta de dados históricos | `--historico` |
| `--anos-historico` | Define o número de anos para dados históricos | `--anos-historico 10` |
| `-v, --verbose` | Aumenta o nível de detalhamento do log | `-v` ou `-vv` para mais detalhes |

### Exemplos de Uso

#### Coleta de Dados Diários
```bash
python -m src.main --frequencia diaria --formato-saida csv
```

#### Coleta de Dados Mensais
```bash
python -m src.main --frequencia mensal --formato-saida json
```

#### Coleta de Dados Históricos
```bash
python -m src.main --historico --anos-historico 10
```

#### Uso da API de Backup
```bash
python -m src.main --modo-api reserva
```

#### Salvando em Formato Otimizado para ML
```bash
python -m src.main --formato-saida parquet --tipo-arquivo concatenado
```

### Automatização da Coleta

Para automatizar a coleta diária de dados, você pode configurar uma tarefa programada:

#### Linux (Cron)
```bash
# Adicione ao crontab (executa todos os dias às 6h)
0 6 * * * cd /caminho/para/sistema_api_clima && /caminho/para/python -m src.main
```

#### Windows (Agendador de Tarefas)
1. Abra o Agendador de Tarefas
2. Crie uma nova tarefa básica
3. Configure para execução diária
4. Ação: Iniciar um programa
   - Programa: `C:\caminho\para\python.exe`
   - Argumentos: `-m src.main`
   - Iniciar em: `C:\caminho\para\sistema_api_clima`

## 4. Entendendo os Dados

### Estrutura dos Arquivos de Saída

Os dados coletados são salvos no diretório configurado (padrão: `dados/`) com nomes baseados na localidade e tipo de dados:

- Formato: `clima_[nome_localidade]_[tipo].extensão`
- Exemplos:
  - `clima_sao_paulo_diario.csv`
  - `clima_rio_de_janeiro_mensal.json`

### Dados Diários

Os dados diários incluem:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `data` | Data da coleta (YYYY-MM-DD) | 2025-04-01 |
| `localidade` | Nome da localidade | São Paulo |
| `temperatura_media` | Temperatura média do dia (°C) | 23.5 |
| `temperatura_minima` | Temperatura mínima do dia (°C) | 18.2 |
| `temperatura_maxima` | Temperatura máxima do dia (°C) | 28.7 |
| `amplitude_termica` | Diferença entre máxima e mínima (°C) | 10.5 |
| `chuva_precipitacao` | Volume de chuva em mm | 12.5 |
| `chuva_probabilidade` | Probabilidade de chuva (%) | 80 |
| `umidade_media` | Umidade relativa média (%) | 65 |
| `fonte_dados` | API de origem dos dados | OpenWeather |
| `ano` | Ano da data | 2025 |
| `mes` | Mês da data | 4 |
| `dia` | Dia do mês | 1 |
| `dia_semana` | Dia da semana (0-6, onde 0=segunda) | 1 |

### Dados Mensais

Os dados mensais incluem:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `ano_mes` | Ano e mês (YYYY-MM) | 2025-04 |
| `localidade` | Nome da localidade | São Paulo |
| `temperatura_media` | Temperatura média mensal (°C) | 22.1 |
| `temperatura_minima` | Menor temperatura do mês (°C) | 15.5 |
| `temperatura_maxima` | Maior temperatura do mês (°C) | 30.2 |
| `chuva_total` | Total de precipitação no mês (mm) | 120.5 |
| `dias_com_chuva` | Número de dias com chuva | 12 |
| `umidade_media` | Umidade relativa média mensal (%) | 70 |
| `fonte_dados` | API de origem dos dados | OpenWeather |
| `dias_contabilizados` | Número de dias com dados | 30 |

## 5. Casos de Uso Comuns

### Monitoramento Climático

Utilização do sistema para monitorar condições climáticas diárias de várias localidades:

```bash
python -m src.main --frequencia diaria --modo-api ambas
```

Automatize a execução diária para criar um histórico contínuo.

### Análise Histórica

Para analisar tendências climáticas de longo prazo:

```bash
python -m src.main --historico --anos-historico 10 --frequencia mensal
```

Isso coletará dados mensais dos últimos 10 anos, ideais para identificar padrões sazonais.

### Alimentação de Modelos Preditivos

Para preparar dados para modelos de machine learning:

```bash
python -m src.main --formato-saida parquet --tipo-arquivo concatenado
```

Os dados em formato Parquet são otimizados para leitura e processamento em frameworks como Pandas, Spark e ferramentas de ML.

### Monitoramento de Múltiplas Regiões

Edite seu arquivo de configuração para incluir diversas regiões:

```yaml
localidades:
  - nome: "Norte de SP"
    latitude: -23.2
    longitude: -46.5
  - nome: "Sul de SP"
    latitude: -23.8
    longitude: -46.7
  # Adicione mais regiões...
```

Execute com:
```bash
python -m src.main --tipo-arquivo separado
```

Isso gerará um arquivo para cada região, facilitando a análise comparativa.

## 6. Integração com Análise de Dados

### Uso com Python e Pandas

Os dados exportados podem ser facilmente carregados com Pandas:

```python
import pandas as pd

# Carregar dados CSV
dados_diarios = pd.read_csv('dados/clima_sao_paulo_diario.csv')

# Análise básica
print("Temperatura média:", dados_diarios['temperatura_media'].mean())
print("Dias mais quentes:", dados_diarios.nlargest(5, 'temperatura_maxima')[['data', 'temperatura_maxima']])
print("Dias mais chuvosos:", dados_diarios.nlargest(5, 'chuva_precipitacao')[['data', 'chuva_precipitacao']])

# Visualização
import matplotlib.pyplot as plt
dados_diarios.plot(x='data', y='temperatura_media', figsize=(12, 6))
plt.title('Temperatura Média em São Paulo')
plt.grid(True)
plt.show()
```

### Uso com ferramentas de BI

Os dados CSV podem ser importados em ferramentas como Power BI, Tableau ou Google Data Studio para criar dashboards interativos.

### Uso em Machine Learning

Exemplo de preparação para um modelo preditivo simples:

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Carregar dados
df = pd.read_csv('dados/clima_sao_paulo_diario.csv')

# Preparar features
X = df[['temperatura_media', 'temperatura_minima', 'umidade_media', 'mes', 'dia_semana']]
y = df['chuva_precipitacao']  # Prever precipitação

# Dividir dados
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

# Treinar modelo
modelo = RandomForestRegressor(n_estimators=100)
modelo.fit(X_train, y_train)

# Avaliar
from sklearn.metrics import mean_squared_error
import numpy as np

previsoes = modelo.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, previsoes))
print(f"Erro (RMSE): {rmse:.2f} mm")
```

## 7. Solução de Problemas

### Erros Comuns e Soluções

#### Erro: "API principal não responde"

**Solução**:
1. Verifique sua conexão com a internet
2. Confirme se sua chave de API OpenWeather está correta e ativa
3. Tente usar o modo alternativo: `--modo-api reserva`

#### Erro: "Nenhum dado encontrado para localidade X"

**Solução**:
1. Verifique se as coordenadas estão corretas
2. Algumas áreas remotas podem não ter cobertura completa
3. Tente usar o modo `ambas` para tentar diferentes fontes de dados

#### Erro: "Falha ao criar arquivo"

**Solução**:
1. Verifique se o diretório de saída existe e tem permissões de escrita
2. Certifique-se de que o caminho não contém caracteres especiais
3. Tente um diretório alternativo: `--diretorio-saida ./outro_diretorio`

#### Erro: "Requisição excedeu timeout"

**Solução**:
1. Verifique sua conexão com a internet
2. A API pode estar sobrecarregada, tente mais tarde
3. Aumente o timeout nas configurações das APIs no arquivo config.yaml

### Como Obter Mais Informações de Erro

Use o modo verboso para obter logs mais detalhados:

```bash
python -m src.main -vv
```

Os logs detalhados mostrarão todas as requisições, respostas e passos de processamento.

## 8. Perguntas Frequentes

### Quantos dados posso coletar?

O volume de dados depende das limitações da API que você está usando:
- OpenWeather tem diferentes limites baseados no seu plano (gratuito ou pago)
- INMET geralmente tem limites por IP ou chave de API

### Posso coletar dados de estações meteorológicas específicas?

O sistema trabalha com dados baseados em coordenadas geográficas. Para dados de estações específicas, você precisaria modificar as implementações das APIs.

### Como evitar exceder os limites da API?

1. Use a opção de frequência mensal quando possível
2. Reduza o número de localidades monitoradas
3. Evite solicitações repetidas em curtos períodos (use o agendador para espaçar as coletas)

### Os dados são precisos?

Os dados vêm de fontes confiáveis (OpenWeather e INMET), mas podem haver variações entre elas. Para aplicações que requerem alta precisão, considere:
1. Usar o modo `ambas` para comparar dados
2. Implementar validações adicionais no código 
3. Complementar com dados de outras fontes

### Posso adicionar outras fontes de dados?

Sim, o sistema foi projetado para ser extensível. Para adicionar uma nova fonte:
1. Crie uma nova classe no módulo `api/` que estenda `BaseApiClima`
2. Implemente os métodos requeridos (obter_dados_diarios, etc.)
3. Atualize o `GerenciadorApi` para incluir sua nova fonte

### Preciso das duas chaves de API?

Não. O sistema funcionará com apenas uma das chaves, mas ter ambas permite:
1. Maior robustez com failover automático
2. Comparação de dados de diferentes fontes
3. Continuidade em caso de falha de uma API