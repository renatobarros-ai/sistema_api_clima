"""
Módulo de gerenciamento de APIs de dados climáticos.
Coordena o acesso às diferentes APIs (OpenWeather e INMET) com fallback.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import date

from src.api.base_api import BaseApiClima
from src.api.openweather_api import OpenWeatherApi
from src.api.inmet_api import InmetApi


# Configuração de logging
logger = logging.getLogger(__name__)


class GerenciadorApi:
    """
    Gerencia o acesso às diferentes APIs de dados climáticos.
    
    Implementa a estratégia de fallback: tenta a API principal e, 
    em caso de falha, utiliza a API reserva.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o gerenciador de APIs.
        
        Args:
            config: Configuração completa do sistema
        """
        self.modo_api = config.get('geral', {}).get('modo_api', 'principal')
        self.apis_config = config.get('apis', {})
        
        # Inicializa as APIs conforme configuração
        self.api_principal = None
        self.api_reserva = None
        
        if 'openweather' in self.apis_config:
            self.api_principal = OpenWeatherApi(self.apis_config['openweather'])
            logger.info("API principal (OpenWeather) inicializada")
        
        if 'inmet' in self.apis_config:
            self.api_reserva = InmetApi(self.apis_config['inmet'])
            logger.info("API reserva (INMET) inicializada")
        
        # Verifica se as APIs necessárias foram inicializadas
        if self.modo_api in ['principal', 'ambas'] and not self.api_principal:
            logger.warning("Modo API 'principal' ou 'ambas' selecionado, mas API principal não configurada")
        
        if self.modo_api in ['reserva', 'ambas'] and not self.api_reserva:
            logger.warning("Modo API 'reserva' ou 'ambas' selecionado, mas API reserva não configurada")

    def obter_dados_diarios(
        self, 
        latitude: float, 
        longitude: float, 
        data_inicio: Optional[date] = None, 
        data_fim: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados climáticos diários, usando a estratégia de fallback se necessário.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            data_inicio: Data inicial para coleta (opcional)
            data_fim: Data final para coleta (opcional)
            
        Returns:
            Lista de dicionários com dados climáticos diários
        """
        resultado = []
        
        # Modo ambas: tenta obter das duas APIs e combina os resultados
        if self.modo_api == 'ambas':
            resultados_apis = []
            
            if self.api_principal:
                try:
                    dados_principal = self.api_principal.obter_dados_diarios(
                        latitude, longitude, data_inicio, data_fim)
                    resultados_apis.append(('principal', dados_principal))
                except Exception as e:
                    logger.error(f"Erro ao obter dados da API principal: {str(e)}")
            
            if self.api_reserva:
                try:
                    dados_reserva = self.api_reserva.obter_dados_diarios(
                        latitude, longitude, data_inicio, data_fim)
                    resultados_apis.append(('reserva', dados_reserva))
                except Exception as e:
                    logger.error(f"Erro ao obter dados da API reserva: {str(e)}")
            
            # Combina os resultados (estratégia simples: concatenação com marcação de fonte)
            for fonte, dados in resultados_apis:
                for dado in dados:
                    dado['origem_api'] = fonte
                    resultado.append(dado)
            
            return resultado
        
        # Modo principal: tenta principal com fallback para reserva
        if self.modo_api == 'principal':
            if self.api_principal:
                try:
                    resultado = self.api_principal.obter_dados_diarios(
                        latitude, longitude, data_inicio, data_fim)
                    
                    if resultado:
                        for dado in resultado:
                            dado['origem_api'] = 'principal'
                        return resultado
                    
                except Exception as e:
                    logger.error(f"Erro ao obter dados da API principal: {str(e)}")
            
            # Fallback para API reserva
            if self.api_reserva:
                try:
                    resultado = self.api_reserva.obter_dados_diarios(
                        latitude, longitude, data_inicio, data_fim)
                    
                    if resultado:
                        for dado in resultado:
                            dado['origem_api'] = 'reserva (fallback)'
                        return resultado
                        
                except Exception as e:
                    logger.error(f"Erro ao obter dados da API reserva (fallback): {str(e)}")
        
        # Modo reserva: usa apenas a API reserva
        elif self.modo_api == 'reserva':
            if self.api_reserva:
                try:
                    resultado = self.api_reserva.obter_dados_diarios(
                        latitude, longitude, data_inicio, data_fim)
                    
                    if resultado:
                        for dado in resultado:
                            dado['origem_api'] = 'reserva'
                        return resultado
                        
                except Exception as e:
                    logger.error(f"Erro ao obter dados da API reserva: {str(e)}")
        
        # Se chegou aqui, não conseguiu obter dados
        logger.warning(f"Não foi possível obter dados diários para {latitude}, {longitude}")
        return []

    def obter_dados_mensais(
        self, 
        latitude: float, 
        longitude: float, 
        data_inicio: Optional[date] = None, 
        data_fim: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados climáticos mensais, usando a estratégia de fallback se necessário.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            data_inicio: Data inicial para coleta (opcional)
            data_fim: Data final para coleta (opcional)
            
        Returns:
            Lista de dicionários com dados climáticos mensais
        """
        # Implementação semelhante à de dados diários, adaptada para dados mensais
        resultado = []
        
        # Modo ambas: tenta obter das duas APIs e combina os resultados
        if self.modo_api == 'ambas':
            resultados_apis = []
            
            if self.api_principal:
                try:
                    dados_principal = self.api_principal.obter_dados_mensais(
                        latitude, longitude, data_inicio, data_fim)
                    resultados_apis.append(('principal', dados_principal))
                except Exception as e:
                    logger.error(f"Erro ao obter dados mensais da API principal: {str(e)}")
            
            if self.api_reserva:
                try:
                    dados_reserva = self.api_reserva.obter_dados_mensais(
                        latitude, longitude, data_inicio, data_fim)
                    resultados_apis.append(('reserva', dados_reserva))
                except Exception as e:
                    logger.error(f"Erro ao obter dados mensais da API reserva: {str(e)}")
            
            # Combina os resultados
            for fonte, dados in resultados_apis:
                for dado in dados:
                    dado['origem_api'] = fonte
                    resultado.append(dado)
            
            return resultado
        
        # Modo principal: tenta principal com fallback para reserva
        if self.modo_api == 'principal':
            if self.api_principal:
                try:
                    resultado = self.api_principal.obter_dados_mensais(
                        latitude, longitude, data_inicio, data_fim)
                    
                    if resultado:
                        for dado in resultado:
                            dado['origem_api'] = 'principal'
                        return resultado
                    
                except Exception as e:
                    logger.error(f"Erro ao obter dados mensais da API principal: {str(e)}")
            
            # Fallback para API reserva
            if self.api_reserva:
                try:
                    resultado = self.api_reserva.obter_dados_mensais(
                        latitude, longitude, data_inicio, data_fim)
                    
                    if resultado:
                        for dado in resultado:
                            dado['origem_api'] = 'reserva (fallback)'
                        return resultado
                        
                except Exception as e:
                    logger.error(f"Erro ao obter dados mensais da API reserva (fallback): {str(e)}")
        
        # Modo reserva: usa apenas a API reserva
        elif self.modo_api == 'reserva':
            if self.api_reserva:
                try:
                    resultado = self.api_reserva.obter_dados_mensais(
                        latitude, longitude, data_inicio, data_fim)
                    
                    if resultado:
                        for dado in resultado:
                            dado['origem_api'] = 'reserva'
                        return resultado
                        
                except Exception as e:
                    logger.error(f"Erro ao obter dados mensais da API reserva: {str(e)}")
        
        # Se chegou aqui, não conseguiu obter dados
        logger.warning(f"Não foi possível obter dados mensais para {latitude}, {longitude}")
        return []

    def obter_dados_historicos(
        self, 
        latitude: float, 
        longitude: float, 
        anos: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados históricos, usando a estratégia de fallback se necessário.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            anos: Número de anos para recuperar dados históricos
            
        Returns:
            Lista de dicionários com dados climáticos históricos
        """
        # Implementação semelhante às anteriores, adaptada para dados históricos
        resultado = []
        
        # Modo ambas: tenta obter das duas APIs e combina os resultados
        if self.modo_api == 'ambas':
            resultados_apis = []
            
            if self.api_principal:
                try:
                    dados_principal = self.api_principal.obter_dados_historicos(
                        latitude, longitude, anos)
                    resultados_apis.append(('principal', dados_principal))
                except Exception as e:
                    logger.error(f"Erro ao obter dados históricos da API principal: {str(e)}")
            
            if self.api_reserva:
                try:
                    dados_reserva = self.api_reserva.obter_dados_historicos(
                        latitude, longitude, anos)
                    resultados_apis.append(('reserva', dados_reserva))
                except Exception as e:
                    logger.error(f"Erro ao obter dados históricos da API reserva: {str(e)}")
            
            # Combina os resultados
            for fonte, dados in resultados_apis:
                for dado in dados:
                    dado['origem_api'] = fonte
                    resultado.append(dado)
            
            return resultado
        
        # Modo principal: tenta principal com fallback para reserva
        if self.modo_api == 'principal':
            if self.api_principal:
                try:
                    resultado = self.api_principal.obter_dados_historicos(
                        latitude, longitude, anos)
                    
                    if resultado:
                        for dado in resultado:
                            dado['origem_api'] = 'principal'
                        return resultado
                    
                except Exception as e:
                    logger.error(f"Erro ao obter dados históricos da API principal: {str(e)}")
            
            # Fallback para API reserva
            if self.api_reserva:
                try:
                    resultado = self.api_reserva.obter_dados_historicos(
                        latitude, longitude, anos)
                    
                    if resultado:
                        for dado in resultado:
                            dado['origem_api'] = 'reserva (fallback)'
                        return resultado
                        
                except Exception as e:
                    logger.error(f"Erro ao obter dados históricos da API reserva (fallback): {str(e)}")
        
        # Modo reserva: usa apenas a API reserva
        elif self.modo_api == 'reserva':
            if self.api_reserva:
                try:
                    resultado = self.api_reserva.obter_dados_historicos(
                        latitude, longitude, anos)
                    
                    if resultado:
                        for dado in resultado:
                            dado['origem_api'] = 'reserva'
                        return resultado
                        
                except Exception as e:
                    logger.error(f"Erro ao obter dados históricos da API reserva: {str(e)}")
        
        # Se chegou aqui, não conseguiu obter dados
        logger.warning(f"Não foi possível obter dados históricos para {latitude}, {longitude}")
        return []