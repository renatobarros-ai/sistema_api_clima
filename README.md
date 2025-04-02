# Sistema API Clima

Sistema para coleta automatizada de dados climáticos das APIs do OpenWeather e INMET, com processamento inteligente para análise e machine learning.

## 📋 Visão Geral

O Sistema API Clima automatiza a coleta, processamento e exportação de dados meteorológicos (temperatura, precipitação, umidade) de múltiplas fontes. Ideal para alimentar modelos preditivos, análises de tendências climáticas e aplicações que necessitam de dados meteorológicos confiáveis.

## ✨ Características

- Coleta de dados diários e/ou mensais
- Integração com múltiplas fontes (OpenWeather como principal, INMET como reserva)
- Fallback automático entre APIs para maior confiabilidade
- Exportação em formatos versáteis (CSV, JSON, Parquet)
- Suporte a dados históricos (até 15 anos)
- Configuração flexível via arquivo YAML ou argumentos CLI
- Processamento personalizado para dados diários e mensais
- Preparação automática para modelos de machine learning

## 🚀 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Acesso à internet

### Passos

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/sistema_api_clima.git
cd sistema_api_clima

# Crie e ative um ambiente virtual
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

### Configuração das Chaves de API

Para usar o sistema, você precisa configurar ao menos uma chave de API:

```bash
# Linux/Mac
export OPENWEATHER_API_KEY="sua_chave_aqui"
export INMET_API_KEY="sua_chave_aqui"  # Opcional

# Windows (PowerShell)
$env:OPENWEATHER_API_KEY="sua_chave_aqui"
$env:INMET_API_KEY="sua_chave_aqui"  # Opcional
```

## ⚙️ Configuração Inicial

Gere um arquivo de configuração padrão:

```bash
python -m src.main --gerar-config
```

Este comando cria o arquivo `config/config.yaml` que você pode personalizar conforme suas necessidades.

## 🔍 Uso Básico

```bash
# Executar com configuração padrão
python -m src.main

# Especificar arquivo de configuração alternativo
python -m src.main --config minha_config.yaml

# Sobrescrever opções específicas
python -m src.main --modo-api ambas --formato-saida json --historico
```

## 🔄 APIs Suportadas

### OpenWeather (Principal)
- API completa de meteorologia global
- Utilizado por padrão para todas as requisições
- Obtenha uma chave em: [OpenWeather API](https://openweathermap.org/api)

### INMET (Reserva)
- Instituto Nacional de Meteorologia do Brasil
- Usado como alternativa quando OpenWeather falha
- Obtenha uma chave em: [Portal do INMET](https://portal.inmet.gov.br/)

## 📊 Dados Gerados

Os dados são salvos no diretório configurado (padrão: `dados/`):

```
dados/
  ├── clima_sao_paulo_diario.csv
  ├── clima_rio_de_janeiro_diario.csv
  └── ...
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=src --cov-report=html
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie sua branch de feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📜 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📚 Documentação Adicional

- [Manual do Usuário](MANUAL_DO_USUARIO.md) - Instruções detalhadas de uso
- [Guia de Uso](COMO_USAR.md) - Guia rápido e exemplos práticos