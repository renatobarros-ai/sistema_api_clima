"""
Módulo do gerenciador de exportação para diferentes formatos.
"""

import logging
from typing import Dict, List, Any, Optional

from src.exportadores.base_exportador import BaseExportador
from src.exportadores.exportador_csv import ExportadorCSV
from src.exportadores.exportador_json import ExportadorJSON
from src.exportadores.exportador_parquet import ExportadorParquet

# Configuração de logging
logger = logging.getLogger(__name__)


class GerenciadorExportacao:
    """
    Gerencia a exportação de dados para diferentes formatos.
    
    Seleciona o exportador apropriado conforme a configuração.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o gerenciador com a configuração.
        
        Args:
            config: Configuração do sistema
        """
        self.config = config
        self.formato_saida = self._obter_formato_saida()
        self.exportador = self._criar_exportador()
    
    def _obter_formato_saida(self) -> str:
        """
        Obtém o formato de saída da configuração.
        
        Returns:
            Formato de saída: 'csv', 'json' ou 'parquet'
        """
        formato = self.config.get('geral', {}).get('formato_saida', 'csv')
        
        # Valida o formato (default para CSV se inválido)
        if formato not in ['csv', 'json', 'parquet']:
            logger.warning(f"Formato de saída inválido: {formato}. Usando CSV como padrão.")
            formato = 'csv'
        
        return formato
    
    def _criar_exportador(self) -> BaseExportador:
        """
        Cria o exportador apropriado conforme o formato de saída.
        
        Returns:
            Instância do exportador para o formato configurado
        """
        if self.formato_saida == 'json':
            logger.info("Usando exportador JSON")
            return ExportadorJSON(self.config)
        
        elif self.formato_saida == 'parquet':
            logger.info("Usando exportador Parquet")
            return ExportadorParquet(self.config)
        
        else:  # csv ou qualquer outro valor
            logger.info("Usando exportador CSV")
            return ExportadorCSV(self.config)
    
    def exportar(
        self, 
        dados: List[Dict[str, Any]], 
        localidade: str, 
        tipo_dados: str
    ) -> List[str]:
        """
        Exporta os dados para o formato configurado.
        
        Args:
            dados: Lista de dicionários com dados climáticos
            localidade: Nome da localidade
            tipo_dados: Tipo de dados (diario, mensal, historico)
            
        Returns:
            Lista de caminhos dos arquivos gerados
        """
        return self.exportador.exportar(dados, localidade, tipo_dados)
    
    def exportar_multiplas_localidades(
        self, 
        dados_por_localidade: Dict[str, List[Dict[str, Any]]], 
        tipo_dados: str
    ) -> List[str]:
        """
        Exporta dados de múltiplas localidades, conforme a configuração.
        
        Args:
            dados_por_localidade: Dicionário com localidades como chaves e dados como valores
            tipo_dados: Tipo de dados (diario, mensal, historico)
            
        Returns:
            Lista de caminhos dos arquivos gerados
        """
        return self.exportador.exportar_multiplas_localidades(dados_por_localidade, tipo_dados)