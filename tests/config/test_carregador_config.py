"""
Testes para o módulo de carregamento de configurações.
"""

import os
import pytest
import tempfile
import yaml
from unittest.mock import patch

from src.config.carregador_config import CarregadorConfig


@pytest.fixture
def config_teste():
    """Fixture que cria uma configuração de teste temporária."""
    # Cria um arquivo temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp:
        # Configuração de teste
        config = {
            "geral": {
                "modo_api": "principal",
                "formato_saida": "csv",
                "arquivo_saida": {
                    "tipo": "separado",
                    "diretorio": "dados"
                }
            },
            "localidades": [
                {
                    "nome": "São Paulo",
                    "latitude": -23.5505,
                    "longitude": -46.6333
                }
            ],
            "variaveis": [
                {
                    "nome": "temperatura",
                    "unidade": "celsius",
                    "ativo": True
                }
            ],
            "frequencia": {
                "tipo": "diaria",
                "historico": {
                    "ativo": False,
                    "anos": 5
                }
            },
            "apis": {
                "openweather": {
                    "chave": "${OPENWEATHER_API_KEY}",
                    "base_url": "https://api.openweathermap.org/data/2.5",
                    "timeout": 30,
                    "tentativas": 3
                }
            }
        }
        yaml.dump(config, temp, default_flow_style=False)
        temp_path = temp.name
    
    # Retorna o caminho do arquivo temporário
    yield temp_path
    
    # Remove o arquivo temporário após o teste
    os.unlink(temp_path)


def test_carregar_config(config_teste):
    """Testa o carregamento de configuração a partir de arquivo."""
    # Inicializa com arquivo de teste
    carregador = CarregadorConfig(caminho_config=config_teste)
    
    # Verifica se a configuração foi carregada corretamente
    config = carregador.obter_config()
    assert config["geral"]["modo_api"] == "principal"
    assert len(config["localidades"]) == 1
    assert config["localidades"][0]["nome"] == "São Paulo"
    assert len(config["variaveis"]) == 1
    assert config["variaveis"][0]["nome"] == "temperatura"


def test_obter_localidades(config_teste):
    """Testa a obtenção de localidades."""
    carregador = CarregadorConfig(caminho_config=config_teste)
    localidades = carregador.obter_localidades()
    
    assert len(localidades) == 1
    assert localidades[0]["nome"] == "São Paulo"
    assert localidades[0]["latitude"] == -23.5505


def test_obter_variaveis(config_teste):
    """Testa a obtenção de variáveis climáticas."""
    carregador = CarregadorConfig(caminho_config=config_teste)
    variaveis = carregador.obter_variaveis()
    
    assert len(variaveis) == 1
    assert variaveis[0]["nome"] == "temperatura"
    assert variaveis[0]["unidade"] == "celsius"
    assert variaveis[0]["ativo"] is True


def test_obter_config_api(config_teste):
    """Testa a obtenção de configuração de API."""
    carregador = CarregadorConfig(caminho_config=config_teste)
    config_api = carregador.obter_config_api("openweather")
    
    assert config_api is not None
    assert config_api["base_url"] == "https://api.openweathermap.org/data/2.5"
    assert config_api["timeout"] == 30
    
    # API não existente deve retornar None
    assert carregador.obter_config_api("api_inexistente") is None


def test_obter_modo_api(config_teste):
    """Testa a obtenção do modo de API."""
    carregador = CarregadorConfig(caminho_config=config_teste)
    modo = carregador.obter_modo_api()
    
    assert modo == "principal"


def test_obter_formato_saida(config_teste):
    """Testa a obtenção do formato de saída."""
    carregador = CarregadorConfig(caminho_config=config_teste)
    formato = carregador.obter_formato_saida()
    
    assert formato == "csv"


def test_obter_tipo_frequencia(config_teste):
    """Testa a obtenção do tipo de frequência."""
    carregador = CarregadorConfig(caminho_config=config_teste)
    tipo = carregador.obter_tipo_frequencia()
    
    assert tipo == "diaria"


def test_obter_configuracao_historico(config_teste):
    """Testa a obtenção da configuração de histórico."""
    carregador = CarregadorConfig(caminho_config=config_teste)
    historico = carregador.obter_configuracao_historico()
    
    assert historico["ativo"] is False
    assert historico["anos"] == 5


@patch.dict(os.environ, {"OPENWEATHER_API_KEY": "chave_teste"})
def test_substituir_variaveis_ambiente(config_teste):
    """Testa a substituição de variáveis de ambiente."""
    carregador = CarregadorConfig(caminho_config=config_teste)
    config_api = carregador.obter_config_api("openweather")
    
    assert config_api["chave"] == "chave_teste"


def test_validar_config_campos_obrigatorios():
    """Testa a validação de campos obrigatórios."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp:
        # Configuração incompleta (sem campo 'variaveis')
        config_incompleta = {
            "geral": {"modo_api": "principal"},
            "localidades": [],
            # Falta o campo 'variaveis'
            "frequencia": {"tipo": "diaria"},
            "apis": {}
        }
        yaml.dump(config_incompleta, temp, default_flow_style=False)
        temp_path = temp.name
    
    try:
        # Deve levantar ValueError
        with pytest.raises(ValueError) as excinfo:
            CarregadorConfig(caminho_config=temp_path)
        
        assert "Campo obrigatório ausente" in str(excinfo.value)
    finally:
        os.unlink(temp_path)


def test_validar_apis_necessarias():
    """Testa a validação de APIs necessárias conforme o modo configurado."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp:
        # Configuração com modo 'principal' mas sem a API OpenWeather
        config_invalida = {
            "geral": {"modo_api": "principal"},
            "localidades": [],
            "variaveis": [],
            "frequencia": {"tipo": "diaria"},
            "apis": {
                # Falta 'openweather'
                "inmet": {"chave": "inmet_key"}
            }
        }
        yaml.dump(config_invalida, temp, default_flow_style=False)
        temp_path = temp.name
    
    try:
        # Deve levantar ValueError
        with pytest.raises(ValueError) as excinfo:
            CarregadorConfig(caminho_config=temp_path)
        
        assert "OpenWeather não configurada" in str(excinfo.value)
    finally:
        os.unlink(temp_path)


def test_criar_config_padrao():
    """Testa a criação de arquivo de configuração padrão."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = os.path.join(temp_dir, "config.yaml")
        
        # Cria a configuração padrão
        CarregadorConfig.criar_config_padrao(caminho=temp_path)
        
        # Verifica se o arquivo foi criado
        assert os.path.exists(temp_path)
        
        # Carrega a configuração para verificar o conteúdo
        carregador = CarregadorConfig(caminho_config=temp_path)
        config = carregador.obter_config()
        
        # Verifica alguns campos
        assert config["geral"]["modo_api"] == "principal"
        assert len(config["localidades"]) > 0
        assert len(config["variaveis"]) > 0
        assert "openweather" in config["apis"]
        assert "inmet" in config["apis"]


def test_atualizar_config_cli(config_teste):
    """Testa a atualização de configuração a partir de argumentos CLI."""
    carregador = CarregadorConfig(caminho_config=config_teste)
    
    # Argumentos CLI de teste
    args = {
        "modo_api": "ambas",
        "formato_saida": "json",
        "tipo_frequencia": "mensal",
        "historico_ativo": True,
        "historico_anos": 10
    }
    
    # Atualiza a configuração
    carregador.atualizar_config_cli(args)
    
    # Verifica se a configuração foi atualizada
    assert carregador.obter_modo_api() == "ambas"
    assert carregador.obter_formato_saida() == "json"
    assert carregador.obter_tipo_frequencia() == "mensal"
    
    historico = carregador.obter_configuracao_historico()
    assert historico["ativo"] is True
    assert historico["anos"] == 10