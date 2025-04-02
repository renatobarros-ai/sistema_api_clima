"""
Módulo do exportador de dados para formato CSV.
"""

import os
import logging
from typing import Dict, List, Any, Optional

import pandas as pd

from src.exportadores.base_exportador import BaseExportador

# Configuração de logging
logger = logging.getLogger(__name__)


class ExportadorCSV(BaseExportador):
    """
    Exportador de dados climáticos para arquivos CSV.
    
    Permite exportar os dados em arquivos separados por localidade
    ou em um único arquivo concatenado.
    """

    def exportar(
        self, 
        dados: List[Dict[str, Any]], 
        localidade: str, 
        tipo_dados: str
    ) -> List[str]:
        """
        Exporta os dados para formato CSV.
        
        Args:
            dados: Lista de dicionários com dados climáticos
            localidade: Nome da localidade
            tipo_dados: Tipo de dados (diario, mensal, historico)
            
        Returns:
            Lista de caminhos dos arquivos gerados
        """
        if not dados:
            logger.warning(f"Nenhum dado para exportar para {localidade}")
            return []
        
        # Converte os dados para DataFrame
        df = self._converter_para_dataframe(dados)
        
        # Define o nome do arquivo
        nome_arquivo = self._gerar_nome_arquivo(localidade, tipo_dados, "csv")
        
        # Salva o DataFrame como CSV
        try:
            df.to_csv(nome_arquivo, index=False, encoding='utf-8')
            logger.info(f"Dados exportados para CSV: {nome_arquivo}")
            return [nome_arquivo]
        
        except Exception as e:
            logger.error(f"Erro ao exportar para CSV: {str(e)}")
            return []
    
    def exportar_multiplas_localidades(
        self, 
        dados_por_localidade: Dict[str, List[Dict[str, Any]]], 
        tipo_dados: str
    ) -> List[str]:
        """
        Exporta dados de múltiplas localidades, conforme o tipo configurado
        (separado ou concatenado).
        
        Args:
            dados_por_localidade: Dicionário com localidades como chaves e dados como valores
            tipo_dados: Tipo de dados (diario, mensal, historico)
            
        Returns:
            Lista de caminhos dos arquivos gerados
        """
        arquivos_gerados = []
        
        # Modo separado: um arquivo para cada localidade
        if self.tipo_arquivo == 'separado':
            for localidade, dados in dados_por_localidade.items():
                arquivos = self.exportar(dados, localidade, tipo_dados)
                arquivos_gerados.extend(arquivos)
        
        # Modo concatenado: um único arquivo com todos os dados
        else:
            # Concatena os dados de todas as localidades
            dados_concatenados = []
            
            for localidade, dados in dados_por_localidade.items():
                for registro in dados:
                    # Adiciona a localidade ao registro
                    registro_com_localidade = registro.copy()
                    registro_com_localidade['localidade'] = localidade
                    dados_concatenados.append(registro_com_localidade)
            
            # Se não houver dados, retorna lista vazia
            if not dados_concatenados:
                logger.warning("Nenhum dado para exportar")
                return []
            
            # Converte para DataFrame
            df_concatenado = self._converter_para_dataframe(dados_concatenados)
            
            # Define o nome do arquivo
            nome_arquivo = os.path.join(
                self.diretorio_saida,
                f"clima_todas_localidades_{tipo_dados}.csv"
            )
            
            # Salva o DataFrame como CSV
            try:
                df_concatenado.to_csv(nome_arquivo, index=False, encoding='utf-8')
                logger.info(f"Dados concatenados exportados para CSV: {nome_arquivo}")
                arquivos_gerados.append(nome_arquivo)
            
            except Exception as e:
                logger.error(f"Erro ao exportar dados concatenados para CSV: {str(e)}")
        
        return arquivos_gerados