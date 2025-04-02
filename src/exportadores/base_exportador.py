"""
Módulo com a classe base para exportadores de dados climáticos.
Define a interface comum para diferentes formatos de exportação.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

import pandas as pd

# Configuração de logging
logger = logging.getLogger(__name__)


class BaseExportador(ABC):
    """
    Classe base abstrata para exportadores de dados climáticos.
    Define a interface comum para diferentes formatos de exportação.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o exportador com a configuração.
        
        Args:
            config: Configuração do sistema
        """
        self.config = config
        self.diretorio_saida = self._obter_diretorio_saida()
        self.tipo_arquivo = self._obter_tipo_arquivo()
        
        # Cria o diretório de saída se não existir
        self._criar_diretorio_saida()
    
    def _obter_diretorio_saida(self) -> str:
        """
        Obtém o diretório de saída da configuração.
        
        Returns:
            Caminho do diretório de saída
        """
        return self.config.get('geral', {}).get('arquivo_saida', {}).get('diretorio', 'dados')
    
    def _obter_tipo_arquivo(self) -> str:
        """
        Obtém o tipo de arquivo da configuração (separado ou concatenado).
        
        Returns:
            Tipo de arquivo: 'separado' ou 'concatenado'
        """
        return self.config.get('geral', {}).get('arquivo_saida', {}).get('tipo', 'separado')
    
    def _criar_diretorio_saida(self) -> None:
        """
        Cria o diretório de saída se não existir.
        """
        if not os.path.exists(self.diretorio_saida):
            os.makedirs(self.diretorio_saida)
            logger.info(f"Diretório de saída criado: {self.diretorio_saida}")
    
    def _converter_para_dataframe(self, dados: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Converte os dados para um DataFrame Pandas.
        
        Args:
            dados: Lista de dicionários com dados climáticos
            
        Returns:
            DataFrame Pandas com os dados
        """
        if not dados:
            return pd.DataFrame()
        
        # Cria um DataFrame a partir dos dados
        df = pd.DataFrame(dados)
        
        # Expande dados hierárquicos (ex: temperatura.media -> temperatura_media)
        df_expandido = df.copy()
        
        # Processa cada coluna hierárquica
        for coluna in ['temperatura', 'chuva', 'umidade']:
            if coluna in df.columns and df[coluna].apply(lambda x: isinstance(x, dict)).any():
                # Expande a coluna hierárquica
                for i, registro in enumerate(df[coluna]):
                    if isinstance(registro, dict):
                        for subchave, valor in registro.items():
                            nova_coluna = f"{coluna}_{subchave}"
                            df_expandido.loc[i, nova_coluna] = valor
        
        # Remove as colunas hierárquicas originais
        for coluna in ['temperatura', 'chuva', 'umidade']:
            if coluna in df_expandido.columns:
                df_expandido = df_expandido.drop(coluna, axis=1)
        
        return df_expandido
    
    def _gerar_nome_arquivo(self, localidade: str, tipo_dados: str, extensao: str) -> str:
        """
        Gera o nome do arquivo de saída.
        
        Args:
            localidade: Nome da localidade
            tipo_dados: Tipo de dados (diario, mensal, historico)
            extensao: Extensão do arquivo
            
        Returns:
            Nome do arquivo
        """
        # Padroniza o nome da localidade (remove acentos, espaços, etc.)
        localidade_padrao = localidade.lower().replace(' ', '_').replace('-', '_')
        
        # Cria o nome do arquivo
        return os.path.join(
            self.diretorio_saida,
            f"clima_{localidade_padrao}_{tipo_dados}.{extensao}"
        )
    
    @abstractmethod
    def exportar(
        self, 
        dados: List[Dict[str, Any]], 
        localidade: str, 
        tipo_dados: str
    ) -> List[str]:
        """
        Exporta os dados para o formato específico.
        
        Args:
            dados: Lista de dicionários com dados climáticos
            localidade: Nome da localidade
            tipo_dados: Tipo de dados (diario, mensal, historico)
            
        Returns:
            Lista de caminhos dos arquivos gerados
        """
        pass