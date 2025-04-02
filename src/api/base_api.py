"""
Módulo com a classe base para APIs de dados climáticos.
Define interface comum e comportamentos compartilhados.
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional

import requests

# Configuração de logging
logger = logging.getLogger(__name__)


class BaseApiClima(ABC):
    """
    Classe base abstrata para APIs de dados climáticos.
    Define interface comum para diferentes provedores de dados climáticos.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa a API com sua configuração.
        
        Args:
            config: Dicionário com configuração da API
        """
        self.base_url = config.get('base_url', '')
        self.chave = config.get('chave', '')
        self.timeout = config.get('timeout', 30)
        self.max_tentativas = config.get('tentativas', 3)
        
        if not self.chave:
            logger.warning(f"API {self.__class__.__name__} inicializada sem chave de acesso")
        
        if not self.base_url:
            logger.warning(f"API {self.__class__.__name__} inicializada sem URL base")

    def _fazer_requisicao(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Realiza requisição HTTP para a API com retry em caso de falha.
        
        Args:
            endpoint: Caminho do endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            Dicionário com a resposta da API
            
        Raises:
            requests.RequestException: Se todas as tentativas falharem
        """
        if params is None:
            params = {}
        
        # Adiciona a chave de API aos parâmetros se existir
        if self.chave and 'key' not in params and 'appid' not in params:
            params.update(self._obter_param_chave())
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Tenta fazer a requisição com retry
        for tentativa in range(1, self.max_tentativas + 1):
            try:
                logger.debug(f"Requisição para {url} (tentativa {tentativa}/{self.max_tentativas})")
                
                response = requests.get(
                    url=url,
                    params=params,
                    timeout=self.timeout
                )
                
                response.raise_for_status()  # Levanta exceção para códigos de erro HTTP
                
                return response.json()
                
            except requests.RequestException as e:
                logger.warning(f"Erro na requisição (tentativa {tentativa}/{self.max_tentativas}): {str(e)}")
                
                if tentativa < self.max_tentativas:
                    # Espera antes de tentar novamente (backoff exponencial)
                    tempo_espera = 2 ** (tentativa - 1)
                    logger.debug(f"Aguardando {tempo_espera}s antes da próxima tentativa")
                    time.sleep(tempo_espera)
                else:
                    # Se todas as tentativas falharem, propaga a exceção
                    logger.error(f"Todas as {self.max_tentativas} tentativas falharam")
                    raise

    @abstractmethod
    def _obter_param_chave(self) -> Dict[str, str]:
        """
        Retorna o parâmetro com a chave de API no formato correto.
        Cada API pode usar um nome diferente para o parâmetro.
        
        Returns:
            Dicionário com o parâmetro da chave API
        """
        pass

    @abstractmethod
    def obter_dados_diarios(
        self, 
        latitude: float, 
        longitude: float, 
        data_inicio: Optional[date] = None, 
        data_fim: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados climáticos diários para as coordenadas especificadas.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            data_inicio: Data inicial para coleta (opcional)
            data_fim: Data final para coleta (opcional)
            
        Returns:
            Lista de dicionários com dados climáticos diários
        """
        pass

    @abstractmethod
    def obter_dados_mensais(
        self, 
        latitude: float, 
        longitude: float, 
        data_inicio: Optional[date] = None, 
        data_fim: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados climáticos mensais para as coordenadas especificadas.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            data_inicio: Data inicial para coleta (opcional)
            data_fim: Data final para coleta (opcional)
            
        Returns:
            Lista de dicionários com dados climáticos mensais
        """
        pass

    @abstractmethod
    def obter_dados_historicos(
        self, 
        latitude: float, 
        longitude: float, 
        anos: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados históricos para as coordenadas especificadas.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            anos: Número de anos para recuperar dados históricos
            
        Returns:
            Lista de dicionários com dados climáticos históricos
        """
        pass

    def gerar_datas_ate_hoje(self, anos: int = 5) -> tuple:
        """
        Gera datas de início e fim para busca de dados históricos.
        
        Args:
            anos: Número de anos para trás a partir de hoje
            
        Returns:
            Tupla com data inicial e data final (data_inicio, data_fim)
        """
        data_fim = date.today()
        data_inicio = data_fim.replace(year=data_fim.year - anos)
        
        return data_inicio, data_fim