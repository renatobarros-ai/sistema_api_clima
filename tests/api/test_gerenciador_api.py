"""
Testes para o módulo de gerenciamento de APIs de dados climáticos.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date

from src.api.gerenciador_api import GerenciadorApi
from src.api.openweather_api import OpenWeatherApi
from src.api.inmet_api import InmetApi


@pytest.fixture
def config_mock():
    """Fixture que fornece uma configuração mock para testes."""
    return {
        'geral': {
            'modo_api': 'principal'
        },
        'apis': {
            'openweather': {
                'chave': 'teste_key',
                'base_url': 'https://api.openweathermap.org/data/2.5'
            },
            'inmet': {
                'chave': 'teste_key',
                'base_url': 'https://apitempo.inmet.gov.br/api'
            }
        }
    }


@pytest.fixture
def dados_diarios_mock():
    """Fixture que fornece dados diários mockados."""
    return [
        {
            "data": "2023-04-01",
            "temperatura": {
                "media": 25.5,
                "minima": 20.0,
                "maxima": 31.0
            },
            "chuva": {
                "precipitacao": 10.5,
                "probabilidade": 80
            },
            "umidade": {
                "media": 75
            },
            "fonte": "api_teste"
        }
    ]


class TestGerenciadorApi:
    """Classe de testes para o GerenciadorApi."""

    def test_inicializacao(self, config_mock):
        """Testa a inicialização do gerenciador com diferentes modos."""
        # Modo principal
        gerenciador = GerenciadorApi(config_mock)
        assert gerenciador.modo_api == 'principal'
        assert isinstance(gerenciador.api_principal, OpenWeatherApi)
        assert isinstance(gerenciador.api_reserva, InmetApi)

        # Modo reserva
        config_mock['geral']['modo_api'] = 'reserva'
        gerenciador = GerenciadorApi(config_mock)
        assert gerenciador.modo_api == 'reserva'

        # Modo ambas
        config_mock['geral']['modo_api'] = 'ambas'
        gerenciador = GerenciadorApi(config_mock)
        assert gerenciador.modo_api == 'ambas'

    @patch('src.api.openweather_api.OpenWeatherApi.obter_dados_diarios')
    @patch('src.api.inmet_api.InmetApi.obter_dados_diarios')
    def test_obter_dados_diarios_modo_principal(
        self, mock_inmet, mock_openweather, config_mock, dados_diarios_mock
    ):
        """Testa obtenção de dados diários no modo principal."""
        # Configura os mocks
        mock_openweather.return_value = dados_diarios_mock
        mock_inmet.return_value = []

        # Cria o gerenciador e chama o método
        gerenciador = GerenciadorApi(config_mock)
        resultado = gerenciador.obter_dados_diarios(
            latitude=-23.5505, longitude=-46.6333
        )

        # Verifica os resultados
        assert len(resultado) == 1
        assert resultado[0]['temperatura']['media'] == 25.5
        assert resultado[0]['origem_api'] == 'principal'
        
        # Verifica se apenas a API principal foi chamada
        mock_openweather.assert_called_once()
        mock_inmet.assert_not_called()

    @patch('src.api.openweather_api.OpenWeatherApi.obter_dados_diarios')
    @patch('src.api.inmet_api.InmetApi.obter_dados_diarios')
    def test_obter_dados_diarios_fallback(
        self, mock_inmet, mock_openweather, config_mock, dados_diarios_mock
    ):
        """Testa fallback para API reserva quando a principal falha."""
        # Configura os mocks - principal falha, reserva funciona
        mock_openweather.side_effect = Exception("Erro simulado da API")
        mock_inmet.return_value = dados_diarios_mock

        # Cria o gerenciador e chama o método
        gerenciador = GerenciadorApi(config_mock)
        resultado = gerenciador.obter_dados_diarios(
            latitude=-23.5505, longitude=-46.6333
        )

        # Verifica os resultados
        assert len(resultado) == 1
        assert resultado[0]['temperatura']['media'] == 25.5
        assert resultado[0]['origem_api'] == 'reserva (fallback)'
        
        # Verifica se ambas as APIs foram chamadas
        mock_openweather.assert_called_once()
        mock_inmet.assert_called_once()

    @patch('src.api.openweather_api.OpenWeatherApi.obter_dados_diarios')
    @patch('src.api.inmet_api.InmetApi.obter_dados_diarios')
    def test_obter_dados_diarios_modo_reserva(
        self, mock_inmet, mock_openweather, config_mock, dados_diarios_mock
    ):
        """Testa obtenção de dados diários no modo reserva."""
        # Configura o modo como reserva
        config_mock['geral']['modo_api'] = 'reserva'
        
        # Configura os mocks
        mock_inmet.return_value = dados_diarios_mock
        
        # Cria o gerenciador e chama o método
        gerenciador = GerenciadorApi(config_mock)
        resultado = gerenciador.obter_dados_diarios(
            latitude=-23.5505, longitude=-46.6333
        )

        # Verifica os resultados
        assert len(resultado) == 1
        assert resultado[0]['temperatura']['media'] == 25.5
        assert resultado[0]['origem_api'] == 'reserva'
        
        # Verifica se apenas a API reserva foi chamada
        mock_openweather.assert_not_called()
        mock_inmet.assert_called_once()

    @patch('src.api.openweather_api.OpenWeatherApi.obter_dados_diarios')
    @patch('src.api.inmet_api.InmetApi.obter_dados_diarios')
    def test_obter_dados_diarios_modo_ambas(
        self, mock_inmet, mock_openweather, config_mock, dados_diarios_mock
    ):
        """Testa obtenção de dados diários no modo ambas."""
        # Configura o modo como ambas
        config_mock['geral']['modo_api'] = 'ambas'
        
        # Configura os mocks
        mock_openweather.return_value = dados_diarios_mock
        mock_inmet.return_value = dados_diarios_mock
        
        # Cria o gerenciador e chama o método
        gerenciador = GerenciadorApi(config_mock)
        resultado = gerenciador.obter_dados_diarios(
            latitude=-23.5505, longitude=-46.6333
        )

        # Verifica os resultados
        assert len(resultado) == 2  # Dados de ambas as APIs
        assert resultado[0]['origem_api'] == 'principal'
        assert resultado[1]['origem_api'] == 'reserva'
        
        # Verifica se ambas as APIs foram chamadas
        mock_openweather.assert_called_once()
        mock_inmet.assert_called_once()

    @patch('src.api.openweather_api.OpenWeatherApi.obter_dados_mensais')
    def test_obter_dados_mensais(
        self, mock_openweather, config_mock, dados_diarios_mock
    ):
        """Testa obtenção de dados mensais."""
        # Configura os mocks
        mock_openweather.return_value = dados_diarios_mock
        
        # Cria o gerenciador e chama o método
        gerenciador = GerenciadorApi(config_mock)
        resultado = gerenciador.obter_dados_mensais(
            latitude=-23.5505, longitude=-46.6333
        )

        # Verifica os resultados
        assert len(resultado) == 1
        assert resultado[0]['origem_api'] == 'principal'
        
        # Verifica se a API foi chamada com os parâmetros corretos
        mock_openweather.assert_called_once_with(
            -23.5505, -46.6333, None, None
        )

    @patch('src.api.openweather_api.OpenWeatherApi.obter_dados_historicos')
    def test_obter_dados_historicos(
        self, mock_openweather, config_mock, dados_diarios_mock
    ):
        """Testa obtenção de dados históricos."""
        # Configura os mocks
        mock_openweather.return_value = dados_diarios_mock
        
        # Cria o gerenciador e chama o método
        gerenciador = GerenciadorApi(config_mock)
        resultado = gerenciador.obter_dados_historicos(
            latitude=-23.5505, longitude=-46.6333, anos=10
        )

        # Verifica os resultados
        assert len(resultado) == 1
        assert resultado[0]['origem_api'] == 'principal'
        
        # Verifica se a API foi chamada com os parâmetros corretos
        mock_openweather.assert_called_once_with(
            -23.5505, -46.6333, 10
        )

    def test_falha_ambas_apis(self, config_mock):
        """Testa comportamento quando ambas as APIs falham."""
        # Cria mocks para as APIs que sempre falham
        api_principal_mock = MagicMock()
        api_principal_mock.obter_dados_diarios.side_effect = Exception("Erro API principal")
        
        api_reserva_mock = MagicMock()
        api_reserva_mock.obter_dados_diarios.side_effect = Exception("Erro API reserva")
        
        # Substitui as APIs do gerenciador pelos mocks
        gerenciador = GerenciadorApi(config_mock)
        gerenciador.api_principal = api_principal_mock
        gerenciador.api_reserva = api_reserva_mock
        
        # Tenta obter dados
        resultado = gerenciador.obter_dados_diarios(
            latitude=-23.5505, longitude=-46.6333
        )
        
        # Verifica que o resultado é uma lista vazia
        assert resultado == []
        
        # Verifica que ambas as APIs foram chamadas
        api_principal_mock.obter_dados_diarios.assert_called_once()
        api_reserva_mock.obter_dados_diarios.assert_called_once()