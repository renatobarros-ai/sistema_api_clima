# Sistema API Clima

Sistema para coleta automatizada de dados climáticos (temperatura, chuva e umidade) das APIs do OpenWeather (principal) e INMET (reserva).

## Descrição

O Sistema API Clima permite automatizar o acesso a informações climáticas para diversas localidades, fornecendo dados diários e mensais. Os dados coletados são preparados para alimentar modelos preditivos de machine learning.

## Características

- Coleta de dados diários e mensais
- Integração com múltiplas APIs (OpenWeather e INMET)
- Coleta de diversos tipos de dados climáticos (temperatura, chuva, umidade)
- Fácil configuração para diferentes localidades
- Suporte a diversos formatos de saída (CSV, JSON, Parquet)
- Opção para dados históricos (até 15 anos)
- Sistema de testes automatizados

## Instalação

```bash
# Clone o repositório
git clone https://seu-repositorio/sistema_api_clima.git
cd sistema_api_clima

# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
```

## Configuração

O sistema utiliza um arquivo YAML para configuração. Você pode personalizar:
- Localidades (coordenadas/cidades)
- Variáveis climáticas (temperatura, chuva, umidade)
- Frequência de coleta (diária/mensal)
- Formato de saída (CSV, JSON, Parquet)
- Configurações das APIs

Exemplo de arquivo de configuração:
```yaml
geral:
  modo_api: "principal"
  formato_saida: "csv"

localidades:
  - nome: "São Paulo"
    latitude: -23.5505
    longitude: -46.6333

variaveis:
  - nome: "temperatura"
    unidade: "celsius"
    ativo: true
```

## Uso

```bash
# Gerar arquivo de configuração padrão
python -m src.main --gerar-config

# Executar com configuração padrão
python -m src.main

# Especificar arquivo de configuração
python -m src.main --config minha_config.yaml

# Sobrescrever opções via linha de comando
python -m src.main --modo-api ambas --formato-saida json --historico
```

## APIs Suportadas

### OpenWeather (Principal)
- Requer chave de API do OpenWeather
- Configurar via variável de ambiente: `OPENWEATHER_API_KEY`

### INMET (Reserva)
- Instituto Nacional de Meteorologia do Brasil
- Requer chave de API do INMET
- Configurar via variável de ambiente: `INMET_API_KEY`

## Executando Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=src

# Gerar relatório de cobertura
pytest --cov=src --cov-report=html
```

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.