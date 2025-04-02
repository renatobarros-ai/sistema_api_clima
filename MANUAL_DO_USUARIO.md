# Manual do Usuário - Sistema API Clima

Este manual explica como instalar, configurar e utilizar o Sistema API Clima para coletar dados climáticos de diversas localidades.

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Instalação](#2-instalação)
3. [Configuração](#3-configuração)
4. [Execução](#4-execução)
5. [Resultados e Dados](#5-resultados-e-dados)
6. [Uso Avançado](#6-uso-avançado)
7. [Solução de Problemas](#7-solução-de-problemas)

## 1. Visão Geral

O Sistema API Clima é uma ferramenta para coleta automatizada de dados climáticos (temperatura, chuva e umidade) das APIs do OpenWeather (principal) e INMET (reserva) para diversas localidades. Os dados são processados e disponibilizados em formato adequado para uso em modelos de machine learning.

### Principais Funcionalidades

- Coleta de dados diários e mensais
- Suporte para múltiplas localidades
- Backup automático entre APIs (fallback)
- Exportação em vários formatos (CSV, JSON, Parquet)
- Dados históricos de até 15 anos
- Adaptado para modelos de machine learning

## 2. Instalação

### Requisitos

- Python 3.8 ou superior
- Acesso à internet
- Chaves de API (OpenWeather e/ou INMET)

### Passo a Passo

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/sistema_api_clima.git
cd sistema_api_clima
```

2. **Crie e ative um ambiente virtual**

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual (Linux/Mac)
source .venv/bin/activate

# Ativar ambiente virtual (Windows)
.venv\Scripts\activate
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure as chaves de API**

```bash
# Linux/Mac
export OPENWEATHER_API_KEY="sua_chave_aqui"
export INMET_API_KEY="sua_chave_aqui"

# Windows (PowerShell)
$env:OPENWEATHER_API_KEY="sua_chave_aqui"
$env:INMET_API_KEY="sua_chave_aqui"

# Windows (Prompt de Comando)
set OPENWEATHER_API_KEY=sua_chave_aqui
set INMET_API_KEY=sua_chave_aqui
```

## 3. Configuração

### Configuração Inicial

Para gerar um arquivo de configuração padrão:

```bash
python -m src.main --gerar-config
```

Isso criará o arquivo `config/config.yaml` com configurações básicas.

### Edição da Configuração

Abra o arquivo `config/config.yaml` em um editor de texto e personalize conforme necessário:

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

# Lista de localidades para coleta de dados
localidades:
  - nome: "São Paulo"
    latitude: -23.5505
    longitude: -46.6333
  - nome: "Rio de Janeiro"
    latitude: -22.9068
    longitude: -43.1729
    
# Adicione ou remova localidades conforme necessário
```

### Principais Configurações

1. **Localidades**
   - Adicione ou remova localidades conforme necessário
   - Cada localidade precisa de nome, latitude e longitude

2. **Variáveis Climáticas**
   - Ative ou desative variáveis específicas (temperatura, chuva, umidade)
   - Configure as unidades desejadas (ex: celsius ou fahrenheit)

3. **Frequência**
   - Escolha entre dados `diaria` ou `mensal`
   - Configure coleta de dados históricos (anos)

4. **Saída**
   - Escolha o formato (`csv`, `json`, `parquet`)
   - Defina se os arquivos serão separados por localidade ou concatenados

## 4. Execução

### Execução Básica

Para executar o sistema com as configurações padrão:

```bash
python -m src.main
```

### Opções de Linha de Comando

Você pode sobrescrever configurações usando argumentos de linha de comando:

```bash
# Usar configuração personalizada
python -m src.main -c minha_config.yaml

# Mudar o modo de API
python -m src.main --modo-api reserva

# Mudar o formato de saída
python -m src.main --formato-saida json

# Coletar dados mensais
python -m src.main --frequencia mensal

# Ativar coleta de dados históricos
python -m src.main --historico --anos-historico 10

# Aumentar detalhamento do log
python -m src.main -v
```

Use `python -m src.main --help` para ver todas as opções disponíveis.

## 5. Resultados e Dados

### Localização dos Dados

Os dados são salvos no diretório especificado na configuração (padrão: `dados/`):

```
dados/
  ├── clima_sao_paulo_diario.csv
  ├── clima_rio_de_janeiro_diario.csv
  ├── clima_sao_paulo_mensal.csv
  └── ...
```

### Estrutura dos Dados

#### Dados Diários

Os dados diários incluem:
- Data
- Temperatura (média, mínima, máxima)
- Precipitação
- Umidade
- Características temporais (ano, mês, dia da semana, etc.)

#### Dados Mensais

Os dados mensais incluem:
- Mês e ano
- Médias mensais de temperatura, precipitação e umidade
- Total de precipitação
- Número de dias contabilizados

### Uso dos Dados em Python

```python
import pandas as pd

# Carregando dados CSV
dados = pd.read_csv('dados/clima_sao_paulo_diario.csv')

# Visualizando os dados
print(dados.head())

# Análise básica
print("Temperatura média:", dados['temperatura_media'].mean())
print("Precipitação total:", dados['chuva_precipitacao'].sum())
```

## 6. Uso Avançado

### Coleta de Dados Históricos

Para coletar dados históricos de vários anos:

1. **Configure o arquivo YAML**:
   ```yaml
   frequencia:
     # ...
     historico:
       ativo: true
       anos: 10  # Quantidade de anos para retroagir
   ```

2. **Ou use a linha de comando**:
   ```bash
   python -m src.main --historico --anos-historico 10
   ```

### Uso com Modelos de Machine Learning

Os dados são formatados para uso direto em modelos de ML:

```python
from src.processadores.processador_diario import ProcessadorDiario
import pandas as pd

# Carrega a configuração
config = {...}  # Sua configuração

# Instancia o processador
processador = ProcessadorDiario(config)

# Preparar para ML (a partir de dados já coletados)
dados = [...]  # Seus dados coletados
df_ml = processador.preparar_para_ml(dados)

# Agora você pode usar com scikit-learn, TensorFlow, etc.
# X = df_ml[['temperatura_media', 'umidade_media', ...]]
# y = df_ml['chuva_precipitacao']
# ...
```

### Automação com Cron/Agendador de Tarefas

Para coletar dados automaticamente todos os dias:

**Linux (crontab)**:
```
# Executar todos os dias às 6h da manhã
0 6 * * * cd /caminho/para/sistema_api_clima && /caminho/para/python -m src.main
```

**Windows (Agendador de Tarefas)**:
1. Abra o Agendador de Tarefas
2. Crie uma nova tarefa básica
3. Configure para executar diariamente
4. Ação: Iniciar um programa
   - Programa/script: `C:\caminho\para\python.exe`
   - Adicionar argumentos: `-m src.main`
   - Iniciar em: `C:\caminho\para\sistema_api_clima`

## 7. Solução de Problemas

### Problemas Comuns

#### Erro de Chave de API

**Sintoma**: Mensagem "API principal não responde" ou "Erro de autenticação"

**Solução**:
1. Verifique se as variáveis de ambiente estão configuradas corretamente
2. Confirme se as chaves de API estão válidas
3. Tente usar o modo de API alternativo: `--modo-api reserva`

#### Sem Dados para uma Localidade

**Sintoma**: Mensagem "Nenhum dado encontrado para [localidade]"

**Solução**:
1. Confirme que as coordenadas estão corretas
2. Verifique se há cobertura da API para a região
3. Tente usar o modo `ambas` para comparar entre APIs

#### Erro ao Exportar

**Sintoma**: Erro "Não foi possível gravar o arquivo"

**Solução**:
1. Verifique se o diretório de saída existe e tem permissões de escrita
2. Verifique se algum outro processo está usando os arquivos
3. Tente um diretório diferente: `--diretorio-saida outro_diretorio`

### Logs e Depuração

Para obter mais detalhes sobre problemas:

```bash
# Aumenta o nível de detalhamento do log
python -m src.main -v

# Para ainda mais detalhes
python -m src.main -vv
```

### Obter Ajuda

Se precisar de mais ajuda:

1. Consulte a documentação no código-fonte
2. Verifique o arquivo README.md
3. Abra uma issue no repositório do GitHub