"""
Módulo de processamento de dados climáticos diários.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import pandas as pd

from src.processadores.processador_base import ProcessadorBase

# Configuração de logging
logger = logging.getLogger(__name__)


class ProcessadorDiario(ProcessadorBase):
    """
    Processa dados climáticos diários.
    
    Realiza operações como:
    - Filtragem de variáveis
    - Validação e limpeza de dados
    - Padronização do formato de saída
    - Preparação para modelos de machine learning
    """

    def processar(self, dados: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa os dados diários aplicando filtragem, validação e transformações.
        
        Args:
            dados: Lista de dicionários com dados climáticos diários
            
        Returns:
            Lista de dicionários com dados processados
        """
        # Valida os dados e remove registros inválidos
        dados_validados = self.validar_dados(dados)
        
        if not dados_validados:
            logger.warning("Nenhum dado válido para processar")
            return []
        
        # Processa cada registro
        dados_processados = []
        
        for registro in dados_validados:
            # Filtra para manter apenas as variáveis ativas na configuração
            registro_filtrado = self._filtrar_variaveis(registro)
            
            # Padroniza as unidades se necessário
            registro_padronizado = self._padronizar_unidades(registro_filtrado)
            
            # Adiciona campos calculados (se aplicável)
            registro_final = self._adicionar_campos_calculados(registro_padronizado)
            
            dados_processados.append(registro_final)
        
        # Ordena por data
        dados_processados = sorted(
            dados_processados,
            key=lambda x: x.get('data', '0000-00-00')
        )
        
        return dados_processados

    def _padronizar_unidades(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Padroniza as unidades dos dados conforme configuração.
        
        Args:
            dados: Dicionário com dados climáticos
            
        Returns:
            Dicionário com unidades padronizadas
        """
        # Copia os dados para não modificar o original
        dados_padronizados = dados.copy()
        
        # Obtém configurações de unidades
        variaveis_config = {
            var['nome']: var.get('unidade', '') 
            for var in self.config.get('variaveis', [])
        }
        
        # Padroniza temperatura (se presente nos dados)
        if 'temperatura' in dados_padronizados and 'temperatura' in variaveis_config:
            unidade_temp = variaveis_config['temperatura']
            
            # Se a unidade configurada for fahrenheit e os dados estiverem em celsius
            if unidade_temp.lower() == 'fahrenheit' and dados.get('fonte', '').startswith(('openweather', 'inmet')):
                # OpenWeather e INMET fornecem dados em Celsius por padrão
                temperatura = dados_padronizados['temperatura']
                
                # Converte todos os valores de temperatura para Fahrenheit
                for chave in temperatura:
                    if isinstance(temperatura[chave], (int, float)) and temperatura[chave] is not None:
                        temperatura[chave] = round((temperatura[chave] * 9/5) + 32, 1)
                
                # Atualiza a unidade
                temperatura['unidade'] = 'fahrenheit'
        
        return dados_padronizados

    def _adicionar_campos_calculados(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adiciona campos calculados úteis para análise e machine learning.
        
        Args:
            dados: Dicionário com dados climáticos
            
        Returns:
            Dicionário com campos calculados adicionados
        """
        # Copia os dados para não modificar o original
        dados_finais = dados.copy()
        
        # Extrai a data para calcular características temporais
        if 'data' in dados_finais:
            try:
                data_obj = datetime.fromisoformat(dados_finais['data'])
                
                # Adiciona características temporais
                dados_finais['ano'] = data_obj.year
                dados_finais['mes'] = data_obj.month
                dados_finais['dia'] = data_obj.day
                dados_finais['dia_semana'] = data_obj.weekday()  # 0 = Segunda, 6 = Domingo
                dados_finais['dia_do_ano'] = data_obj.timetuple().tm_yday
                
                # Estação do ano (para hemisfério sul)
                # 1 = Verão, 2 = Outono, 3 = Inverno, 4 = Primavera
                mes = data_obj.month
                if mes in [12, 1, 2]:
                    dados_finais['estacao_ano'] = 1  # Verão
                elif mes in [3, 4, 5]:
                    dados_finais['estacao_ano'] = 2  # Outono
                elif mes in [6, 7, 8]:
                    dados_finais['estacao_ano'] = 3  # Inverno
                else:  # mes in [9, 10, 11]
                    dados_finais['estacao_ano'] = 4  # Primavera
            
            except (ValueError, TypeError) as e:
                logger.warning(f"Erro ao processar data '{dados_finais['data']}': {str(e)}")
        
        # Adiciona amplitude térmica se tivermos temperatura máxima e mínima
        if 'temperatura' in dados_finais:
            temp = dados_finais['temperatura']
            if 'maxima' in temp and 'minima' in temp:
                if isinstance(temp['maxima'], (int, float)) and isinstance(temp['minima'], (int, float)):
                    if temp['maxima'] is not None and temp['minima'] is not None:
                        temp['amplitude'] = round(temp['maxima'] - temp['minima'], 1)
        
        return dados_finais
    
    def preparar_para_ml(self, dados: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Prepara os dados para uso em modelos de machine learning.
        
        Args:
            dados: Lista de dicionários com dados climáticos
            
        Returns:
            DataFrame pandas com dados prontos para machine learning
        """
        if not dados:
            return pd.DataFrame()
        
        # Converte para DataFrame pandas
        df = pd.DataFrame(dados)
        
        # Expande dados hierárquicos (ex: temperatura.media -> temperatura_media)
        df_expandido = df.copy()
        
        # Processa cada coluna hierárquica
        for coluna in ['temperatura', 'chuva', 'umidade']:
            if coluna in df.columns and df[coluna].apply(lambda x: isinstance(x, dict)).any():
                # Expande a coluna hierárquica
                for registro in df[coluna]:
                    if isinstance(registro, dict):
                        for subchave, valor in registro.items():
                            nova_coluna = f"{coluna}_{subchave}"
                            df_expandido.loc[df_expandido.index[df[coluna] == registro], nova_coluna] = valor
        
        # Remove as colunas hierárquicas originais
        for coluna in ['temperatura', 'chuva', 'umidade']:
            if coluna in df_expandido.columns:
                df_expandido = df_expandido.drop(coluna, axis=1)
        
        # Converte a coluna de data para datetime
        if 'data' in df_expandido.columns:
            df_expandido['data'] = pd.to_datetime(df_expandido['data'])
            df_expandido = df_expandido.set_index('data')
        
        # Remove colunas não numéricas (exceto data) que podem atrapalhar o modelo
        colunas_texto = ['cidade', 'fonte', 'origem_api', 'descricao']
        for coluna in colunas_texto:
            if coluna in df_expandido.columns:
                df_expandido = df_expandido.drop(coluna, axis=1)
        
        # Preenche valores ausentes (NaN)
        # Para modelos de ML, é importante não ter valores ausentes
        df_limpo = df_expandido.fillna(method='ffill').fillna(method='bfill')
        
        return df_limpo