"""
Módulo com a classe base para processadores de dados climáticos.
Define a interface comum para processamento de dados.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

# Configuração de logging
logger = logging.getLogger(__name__)


class ProcessadorBase(ABC):
    """
    Classe base abstrata para processadores de dados climáticos.
    Define a interface comum para diferentes tipos de processamento.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o processador com a configuração.
        
        Args:
            config: Configuração do sistema
        """
        self.config = config
        self.variaveis_ativas = self._obter_variaveis_ativas()
        
    def _obter_variaveis_ativas(self) -> List[str]:
        """
        Obtém a lista de variáveis climáticas ativas na configuração.
        
        Returns:
            Lista de nomes das variáveis ativas
        """
        variaveis_ativas = []
        
        # Obtém as variáveis configuradas
        variaveis_config = self.config.get('variaveis', [])
        
        for variavel in variaveis_config:
            if variavel.get('ativo', True):
                variaveis_ativas.append(variavel.get('nome', ''))
        
        logger.debug(f"Variáveis ativas: {variaveis_ativas}")
        return variaveis_ativas
    
    def _filtrar_variaveis(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filtra dados mantendo apenas as variáveis ativas.
        
        Args:
            dados: Dicionário com dados climáticos
            
        Returns:
            Dicionário filtrado apenas com as variáveis ativas
        """
        # Se não houver variáveis ativas definidas, retorna os dados completos
        if not self.variaveis_ativas:
            return dados
        
        dados_filtrados = {}
        
        # Copia metadados (data, localidade, etc.)
        for chave in ['data', 'ano', 'mes', 'cidade', 'estacao', 'fonte', 'origem_api']:
            if chave in dados:
                dados_filtrados[chave] = dados[chave]
        
        # Filtra as variáveis climáticas
        for variavel in self.variaveis_ativas:
            if variavel == 'temperatura' and 'temperatura' in dados:
                dados_filtrados['temperatura'] = dados['temperatura']
            
            if variavel == 'chuva' and 'chuva' in dados:
                dados_filtrados['chuva'] = dados['chuva']
            
            if variavel == 'umidade' and 'umidade' in dados:
                dados_filtrados['umidade'] = dados['umidade']
        
        return dados_filtrados

    @abstractmethod
    def processar(self, dados: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa os dados conforme as regras específicas de cada implementação.
        
        Args:
            dados: Lista de dicionários com dados climáticos
            
        Returns:
            Lista de dicionários com dados processados
        """
        pass
    
    def validar_dados(self, dados: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Realiza validações básicas nos dados e remove registros inválidos.
        
        Args:
            dados: Lista de dicionários com dados climáticos
            
        Returns:
            Lista de dicionários com dados validados
        """
        dados_validados = []
        
        for registro in dados:
            # Verifica se tem data
            if 'data' not in registro:
                logger.warning("Registro sem data ignorado")
                continue
            
            # Verifica se tem pelo menos uma das variáveis climáticas
            if not any(v in registro for v in ['temperatura', 'chuva', 'umidade']):
                logger.warning(f"Registro para data {registro['data']} sem dados climáticos ignorado")
                continue
            
            # Adiciona à lista de dados validados
            dados_validados.append(registro)
        
        # Registra quantos registros foram removidos
        removidos = len(dados) - len(dados_validados)
        if removidos > 0:
            logger.info(f"{removidos} registros inválidos removidos")
        
        return dados_validados