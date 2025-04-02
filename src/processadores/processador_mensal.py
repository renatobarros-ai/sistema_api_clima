"""
Módulo de processamento de dados climáticos mensais.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import pandas as pd

from src.processadores.processador_base import ProcessadorBase

# Configuração de logging
logger = logging.getLogger(__name__)


class ProcessadorMensal(ProcessadorBase):
    """
    Processa dados climáticos mensais.
    
    Realiza operações como:
    - Filtragem de variáveis
    - Validação e limpeza de dados
    - Padronização do formato de saída
    - Preparação para modelos de machine learning
    """

    def processar(self, dados: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa os dados mensais aplicando filtragem, validação e transformações.
        
        Args:
            dados: Lista de dicionários com dados climáticos mensais
            
        Returns:
            Lista de dicionários com dados processados
        """
        # Valida os dados e remove registros inválidos
        dados_validados = self.validar_dados(dados)
        
        if not dados_validados:
            logger.warning("Nenhum dado mensal válido para processar")
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
            key=lambda x: (x.get('ano', 0), x.get('mes', 0))
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
        
        # Verifica se já temos ano e mês
        if 'ano' not in dados_finais or 'mes' not in dados_finais:
            # Extrai ano e mês da data
            if 'data' in dados_finais:
                try:
                    data_obj = datetime.fromisoformat(dados_finais['data'])
                    dados_finais['ano'] = data_obj.year
                    dados_finais['mes'] = data_obj.month
                except (ValueError, TypeError) as e:
                    logger.warning(f"Erro ao processar data '{dados_finais['data']}': {str(e)}")
        
        # Adiciona estação do ano (para hemisfério sul)
        # 1 = Verão, 2 = Outono, 3 = Inverno, 4 = Primavera
        if 'mes' in dados_finais:
            mes = dados_finais['mes']
            if mes in [12, 1, 2]:
                dados_finais['estacao_ano'] = 1  # Verão
            elif mes in [3, 4, 5]:
                dados_finais['estacao_ano'] = 2  # Outono
            elif mes in [6, 7, 8]:
                dados_finais['estacao_ano'] = 3  # Inverno
            else:  # mes in [9, 10, 11]
                dados_finais['estacao_ano'] = 4  # Primavera
        
        # Adiciona trimestre
        if 'mes' in dados_finais:
            dados_finais['trimestre'] = ((dados_finais['mes'] - 1) // 3) + 1
        
        # Adiciona amplitude térmica se tivermos temperatura máxima e mínima
        if 'temperatura' in dados_finais:
            temp = dados_finais['temperatura']
            if 'maxima' in temp and 'minima' in temp:
                if isinstance(temp['maxima'], (int, float)) and isinstance(temp['minima'], (int, float)):
                    if temp['maxima'] is not None and temp['minima'] is not None:
                        temp['amplitude'] = round(temp['maxima'] - temp['minima'], 1)
        
        return dados_finais
    
    def agregar_diarios_para_mensais(self, dados_diarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Agrega dados diários em médias mensais.
        
        Args:
            dados_diarios: Lista de dicionários com dados diários
            
        Returns:
            Lista de dicionários com médias mensais
        """
        if not dados_diarios:
            return []
        
        # Converte para DataFrame
        df = pd.DataFrame(dados_diarios)
        
        # Verifica se os dados diários têm data
        if 'data' not in df.columns:
            logger.error("Dados diários sem coluna de data")
            return []
        
        # Converte coluna de data para datetime
        df['data'] = pd.to_datetime(df['data'])
        
        # Extrai ano e mês
        df['ano'] = df['data'].dt.year
        df['mes'] = df['data'].dt.month
        
        # Função para extrair valores das colunas hierárquicas
        def extrair_valores(row, coluna, subcoluna, padrao=None):
            if pd.isna(row[coluna]) or not isinstance(row[coluna], dict):
                return padrao
            return row[coluna].get(subcoluna, padrao)
        
        # Extrai os valores das colunas hierárquicas em colunas separadas
        for coluna, subcolunas in {
            'temperatura': ['media', 'minima', 'maxima'],
            'umidade': ['media', 'atual'],
            'chuva': ['precipitacao', 'probabilidade']
        }.items():
            if coluna in df.columns:
                for subcoluna in subcolunas:
                    nova_coluna = f"{coluna}_{subcoluna}"
                    df[nova_coluna] = df.apply(
                        lambda row: extrair_valores(row, coluna, subcoluna), axis=1
                    )
        
        # Agrupa por ano e mês e calcula médias/somas
        agregados = []
        
        for (ano, mes), grupo in df.groupby(['ano', 'mes']):
            # Agregações para diferentes variáveis
            agregado = {
                'ano': ano,
                'mes': mes,
                'data': f"{ano}-{mes:02d}-01",  # Primeiro dia do mês
                'dias_contabilizados': len(grupo)
            }
            
            # Agregações para temperatura
            temp_media = grupo.get('temperatura_media', grupo.get('temperatura_atual')).mean()
            temp_min = grupo.get('temperatura_minima').mean()
            temp_max = grupo.get('temperatura_maxima').mean()
            
            if not pd.isna(temp_media) or not pd.isna(temp_min) or not pd.isna(temp_max):
                agregado['temperatura'] = {}
                
                if not pd.isna(temp_media):
                    agregado['temperatura']['media'] = round(temp_media, 1)
                
                if not pd.isna(temp_min):
                    agregado['temperatura']['minima'] = round(temp_min, 1)
                
                if not pd.isna(temp_max):
                    agregado['temperatura']['maxima'] = round(temp_max, 1)
            
            # Agregações para chuva
            precipitacao = grupo.get('chuva_precipitacao').sum()
            probabilidade = grupo.get('chuva_probabilidade').mean()
            
            if not pd.isna(precipitacao) or not pd.isna(probabilidade):
                agregado['chuva'] = {}
                
                if not pd.isna(precipitacao):
                    agregado['chuva']['precipitacao_total'] = round(precipitacao, 1)
                    agregado['chuva']['precipitacao_media'] = round(precipitacao / len(grupo), 1)
                
                if not pd.isna(probabilidade):
                    agregado['chuva']['probabilidade'] = round(probabilidade, 1)
            
            # Agregações para umidade
            umidade = grupo.get('umidade_media', grupo.get('umidade_atual')).mean()
            
            if not pd.isna(umidade):
                agregado['umidade'] = {'media': round(umidade, 1)}
            
            # Mantém informação de origem
            if 'fonte' in grupo.iloc[0]:
                agregado['fonte'] = f"{grupo.iloc[0]['fonte']}_mensal"
            
            if 'origem_api' in grupo.iloc[0]:
                agregado['origem_api'] = grupo.iloc[0]['origem_api']
            
            agregados.append(agregado)
        
        return agregados
    
    def preparar_para_ml(self, dados: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Prepara os dados mensais para uso em modelos de machine learning.
        
        Args:
            dados: Lista de dicionários com dados climáticos mensais
            
        Returns:
            DataFrame pandas com dados prontos para machine learning
        """
        if not dados:
            return pd.DataFrame()
        
        # Converte para DataFrame pandas
        df = pd.DataFrame(dados)
        
        # Cria uma chave temporal única (ano-mês)
        if 'ano' in df.columns and 'mes' in df.columns:
            df['data'] = pd.to_datetime(df[['ano', 'mes']].assign(day=1))
        
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
        
        # Define a data como índice
        if 'data' in df_expandido.columns:
            df_expandido = df_expandido.set_index('data')
        
        # Remove colunas não numéricas que podem atrapalhar o modelo
        colunas_texto = ['cidade', 'fonte', 'origem_api', 'descricao']
        for coluna in colunas_texto:
            if coluna in df_expandido.columns:
                df_expandido = df_expandido.drop(coluna, axis=1)
        
        # Preenche valores ausentes (NaN)
        df_limpo = df_expandido.fillna(method='ffill').fillna(method='bfill')
        
        return df_limpo