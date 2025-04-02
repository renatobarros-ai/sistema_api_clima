# Guia de Uso do Sistema API Clima

Este documento contém instruções detalhadas para instalar, configurar e executar o Sistema API Clima.

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/sistema_api_clima.git
cd sistema_api_clima

# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## Configuração das APIs

O sistema utiliza duas APIs de dados climáticos:

### OpenWeather (Principal)

1. Crie uma conta em [OpenWeather](https://openweathermap.org/)
2. Adquira uma chave de API gratuita no painel do usuário
3. Defina a variável de ambiente:

```bash
# Linux/Mac
export OPENWEATHER_API_KEY="sua_chave_aqui"

# Windows (PowerShell)
$env:OPENWEATHER_API_KEY="sua_chave_aqui"

# Windows (CMD)
set OPENWEATHER_API_KEY=sua_chave_aqui
```

### INMET (Reserva)

1. Acesse o [Portal do INMET](https://portal.inmet.gov.br/)
2. Solicite acesso à API de dados (se necessário)
3. Defina a variável de ambiente:

```bash
# Linux/Mac
export INMET_API_KEY="sua_chave_aqui"

# Windows (PowerShell)
$env:INMET_API_KEY="sua_chave_aqui"

# Windows (CMD)
set INMET_API_KEY=sua_chave_aqui
```

## Configuração do Sistema

### Gerar Configuração Padrão

Para gerar um arquivo de configuração padrão:

```bash
python -m src.main --gerar-config
```

### Editar Configuração

Edite o arquivo `config/config.yaml` conforme suas necessidades:

```yaml
geral:
  # Modo de API: "principal" (OpenWeather), "reserva" (INMET) ou "ambas"
  modo_api: "principal"
  
  # Formato de saída: "csv", "json" ou "parquet"
  formato_saida: "csv"
  
  arquivo_saida:
    # Tipo de arquivo: "separado" (por localidade) ou "concatenado" (todas)
    tipo: "separado"
    # Diretório onde os arquivos serão salvos
    diretorio: "dados"

# Lista de localidades a serem monitoradas
localidades:
  - nome: "São Paulo"
    latitude: -23.5505
    longitude: -46.6333
  - nome: "Rio de Janeiro"
    latitude: -22.9068
    longitude: -43.1729

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

# Configurações de frequência
frequencia:
  # Tipo de frequência: "diaria" ou "mensal"
  tipo: "diaria"
  
  # Configuração para dados históricos
  historico:
    # Ativar coleta de dados históricos?
    ativo: false
    # Número de anos para dados históricos
    anos: 5
```

## Execução do Sistema

### Execução Básica

```bash
python -m src.main
```

### Opções de Linha de Comando

Sobrescrever configurações via linha de comando:

```bash
# Especificar arquivo de configuração personalizado
python -m src.main -c minha_config.yaml

# Usar modo de API específico
python -m src.main --modo-api reserva

# Alterar formato de saída
python -m src.main --formato-saida json

# Alterar frequência
python -m src.main --frequencia mensal

# Ativar dados históricos
python -m src.main --historico --anos-historico 10

# Aumentar nível de detalhes do log
python -m src.main -v
```

## Dados Gerados

Os dados são salvos no diretório especificado na configuração (padrão: `dados/`).

### Formatos de Saída

- **CSV**: Formato tabular compatível com Excel, pandas e outras ferramentas
- **JSON**: Formato hierárquico para integração com aplicações web
- **Parquet**: Formato colunar otimizado para análise e machine learning

### Estrutura dos Dados

Os dados incluem:

- **temperatura**: média, mínima, máxima (Celsius ou Fahrenheit)
- **chuva**: precipitação, probabilidade
- **umidade**: média ou atual
- **metadados**: data, localidade, origem dos dados

## Uso com Machine Learning

Os dados são formatados para uso direto em modelos de ML:

```python
import pandas as pd
from src.processadores.processador_diario import ProcessadorDiario

# Carregar dados
df = pd.read_csv('dados/clima_sao_paulo_diario.csv')

# Alternativamente, usar os processadores para preparar os dados
config = {...}  # Configuração
processador = ProcessadorDiario(config)
df_ml = processador.preparar_para_ml(dados)

# Agora os dados estão prontos para alimentar modelos
# ...
```

## Troubleshooting

### Erros de API

- **Chave inválida**: Verifique as variáveis de ambiente
- **Falha na API principal**: Configure `modo_api: "reserva"` ou `modo_api: "ambas"`
- **Limite de requisições**: Algumas APIs têm limites de uso gratuito

### Erros de Dados

- **Sem dados**: Verifique as coordenadas das localidades
- **Dados incompletos**: Algumas APIs têm limitações em dados históricos

## Suporte

Para dúvidas ou problemas, abra uma issue no repositório do GitHub.