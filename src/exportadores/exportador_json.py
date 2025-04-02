"""
Módulo do exportador de dados para formato JSON.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

import pandas as pd

from src.exportadores.base_exportador import BaseExportador

# Configuração de logging
logger = logging.getLogger(__name__)


class ExportadorJSON(BaseExportador):
    """
    Exportador de dados climáticos para arquivos JSON.
    
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
        Exporta os dados para formato JSON.
        
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
        
        # Define o nome do arquivo
        nome_arquivo = self._gerar_nome_arquivo(localidade, tipo_dados, "json")
        
        # Salva os dados como JSON
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
            
            logger.info(f"Dados exportados para JSON: {nome_arquivo}")
            return [nome_arquivo]
        
        except Exception as e:
            logger.error(f"Erro ao exportar para JSON: {str(e)}")
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
            # Cria estrutura para armazenar os dados de todas as localidades
            dados_concatenados = {
                "tipo": tipo_dados,
                "localidades": {}
            }
            
            # Adiciona os dados de cada localidade
            for localidade, dados in dados_por_localidade.items():
                dados_concatenados["localidades"][localidade] = dados
            
            # Define o nome do arquivo
            nome_arquivo = os.path.join(
                self.diretorio_saida,
                f"clima_todas_localidades_{tipo_dados}.json"
            )
            
            # Salva os dados como JSON
            try:
                with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                    json.dump(dados_concatenados, arquivo, ensure_ascii=False, indent=2)
                
                logger.info(f"Dados concatenados exportados para JSON: {nome_arquivo}")
                arquivos_gerados.append(nome_arquivo)
            
            except Exception as e:
                logger.error(f"Erro ao exportar dados concatenados para JSON: {str(e)}")
        
        return arquivos_gerados