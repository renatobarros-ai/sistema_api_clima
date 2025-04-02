"""
Módulo de integração com a API do INMET (Instituto Nacional de Meteorologia).
Implementa a interface para obter dados climáticos do INMET.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional

from src.api.base_api import BaseApiClima

# Configuração de logging
logger = logging.getLogger(__name__)


class InmetApi(BaseApiClima):
    """
    Implementação da API do INMET (Instituto Nacional de Meteorologia).
    
    Esta API serve como alternativa (reserva) caso a API principal (OpenWeather) falhe.
    
    Documentação da API: https://portal.inmet.gov.br/manual/manual-de-uso-da-api-estações
    """

    def _obter_param_chave(self) -> Dict[str, str]:
        """
        Retorna o parâmetro com a chave de API no formato específico do INMET.
        
        Returns:
            Dicionário com o parâmetro da chave API
        """
        return {"key": self.chave}

    def obter_dados_diarios(
        self, 
        latitude: float, 
        longitude: float, 
        data_inicio: Optional[date] = None, 
        data_fim: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados climáticos diários do INMET.
        
        Utiliza a estação automática mais próxima das coordenadas especificadas.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            data_inicio: Data inicial para coleta (opcional)
            data_fim: Data final para coleta (opcional)
            
        Returns:
            Lista de dicionários com dados climáticos diários
        """
        # Define datas padrão se não forem fornecidas
        if not data_inicio:
            # Por padrão, obtém dados dos últimos 7 dias
            data_inicio = date.today() - timedelta(days=7)
            
        if not data_fim:
            data_fim = date.today()
        
        try:
            # Primeiro, encontra a estação meteorológica mais próxima
            estacao = self._encontrar_estacao_proxima(latitude, longitude)
            
            if not estacao:
                logger.error(f"Não foi possível encontrar estação próxima às coordenadas {latitude}, {longitude}")
                return []
            
            # Formata as datas no padrão esperado pela API
            data_inicio_str = data_inicio.strftime("%Y-%m-%d")
            data_fim_str = data_fim.strftime("%Y-%m-%d")
            
            # Constrói o endpoint para dados diários
            endpoint = f"estacao/dados/{estacao['codigo']}/{data_inicio_str}/{data_fim_str}"
            
            # Faz a requisição
            resposta = self._fazer_requisicao(endpoint)
            
            # Formata os dados para o padrão da aplicação
            return self._formatar_dados_diarios(resposta, estacao)
            
        except Exception as e:
            logger.error(f"Erro ao obter dados diários do INMET: {str(e)}")
            return []

    def obter_dados_mensais(
        self, 
        latitude: float, 
        longitude: float, 
        data_inicio: Optional[date] = None, 
        data_fim: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados climáticos mensais do INMET.
        
        Agrega dados diários para formar médias mensais.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            data_inicio: Data inicial para coleta (opcional)
            data_fim: Data final para coleta (opcional)
            
        Returns:
            Lista de dicionários com dados climáticos mensais
        """
        # Se não tiver data especificada, usa os últimos 3 meses
        if not data_inicio:
            hoje = date.today()
            data_inicio = date(hoje.year, hoje.month, 1) - timedelta(days=90)  # ~3 meses
            
        if not data_fim:
            data_fim = date.today()
        
        try:
            # Obtém dados diários para o período
            dados_diarios = self.obter_dados_diarios(latitude, longitude, data_inicio, data_fim)
            
            # Agrega em dados mensais
            return self._agregar_dados_mensais(dados_diarios)
            
        except Exception as e:
            logger.error(f"Erro ao obter dados mensais do INMET: {str(e)}")
            return []

    def obter_dados_historicos(
        self, 
        latitude: float, 
        longitude: float, 
        anos: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados históricos do INMET.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            anos: Número de anos para recuperar dados históricos
            
        Returns:
            Lista de dicionários com dados climáticos históricos
        """
        data_inicio, data_fim = self.gerar_datas_ate_hoje(anos)
        
        logger.info(f"Obtendo dados históricos de {data_inicio} até {data_fim}")
        
        # Para dados históricos extensos, precisamos fazer requisições por períodos menores
        # já que a API pode limitar o tamanho da resposta
        
        resultados = []
        periodo_atual = data_inicio
        
        # Define o tamanho de cada período (6 meses)
        tamanho_periodo = timedelta(days=180)
        
        while periodo_atual < data_fim:
            # Define o fim do período atual
            fim_periodo = min(periodo_atual + tamanho_periodo, data_fim)
            
            # Obtém dados para o período atual
            dados_periodo = self.obter_dados_diarios(
                latitude, longitude, periodo_atual, fim_periodo)
            
            resultados.extend(dados_periodo)
            
            # Avança para o próximo período
            periodo_atual = fim_periodo + timedelta(days=1)
            
            logger.debug(f"Obtidos {len(dados_periodo)} registros para o período {periodo_atual} - {fim_periodo}")
        
        return resultados

    def _encontrar_estacao_proxima(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Encontra a estação meteorológica mais próxima das coordenadas especificadas.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            
        Returns:
            Dicionário com informações da estação mais próxima ou None se não encontrar
        """
        try:
            # Endpoint para listar todas as estações
            endpoint = "estacoes/T"  # T = todas as estações
            
            # Obtém a lista de estações
            estacoes = self._fazer_requisicao(endpoint)
            
            if not estacoes or not isinstance(estacoes, list):
                logger.error("Não foi possível obter a lista de estações")
                return None
            
            # Função para calcular distância (simplificada)
            def calcular_distancia(lat1, lon1, lat2, lon2):
                return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5
            
            # Encontra a estação mais próxima
            estacao_proxima = None
            menor_distancia = float('inf')
            
            for estacao in estacoes:
                try:
                    est_lat = float(estacao.get('VL_LATITUDE', 0))
                    est_lon = float(estacao.get('VL_LONGITUDE', 0))
                    
                    # Converte coordenadas se necessário (alguns sistemas usam formatos diferentes)
                    # Aqui assumimos que as coordenadas estão em graus decimais
                    
                    distancia = calcular_distancia(latitude, longitude, est_lat, est_lon)
                    
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        estacao_proxima = {
                            'codigo': estacao.get('CD_ESTACAO'),
                            'nome': estacao.get('DC_NOME'),
                            'latitude': est_lat,
                            'longitude': est_lon,
                            'altitude': estacao.get('VL_ALTITUDE'),
                            'distancia': distancia
                        }
                        
                except (ValueError, TypeError) as e:
                    # Ignora estações com coordenadas inválidas
                    logger.debug(f"Erro ao processar estação: {str(e)}")
                    continue
            
            if estacao_proxima:
                logger.info(f"Estação mais próxima: {estacao_proxima['nome']} "
                            f"(distância: {estacao_proxima['distancia']:.2f})")
                return estacao_proxima
            else:
                logger.warning("Nenhuma estação encontrada")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar estação mais próxima: {str(e)}")
            return None

    def _formatar_dados_diarios(
        self, 
        dados_api: List[Dict[str, Any]], 
        estacao: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Formata os dados diários do INMET para o formato padronizado.
        
        Args:
            dados_api: Resposta da API do INMET
            estacao: Informações da estação meteorológica
            
        Returns:
            Lista de dicionários com dados no formato padronizado
        """
        if not dados_api or not isinstance(dados_api, list):
            return []
        
        resultados = []
        
        for dado in dados_api:
            try:
                # Extrai a data do registro
                data_str = dado.get('DT_MEDICAO')
                if not data_str:
                    continue
                    
                data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
                
                # Extrai os valores de temperatura, chuva e umidade
                # (convertendo para numérico e tratando valores ausentes)
                def extrair_valor(chave, padrao=None):
                    valor = dado.get(chave, padrao)
                    if valor in [None, '', 'null']:
                        return padrao
                    try:
                        return float(valor)
                    except (ValueError, TypeError):
                        return padrao
                
                temp_inst = extrair_valor('TEM_INST')
                temp_max = extrair_valor('TEM_MAX')
                temp_min = extrair_valor('TEM_MIN')
                umidade = extrair_valor('UMD_INST')
                precipitacao = extrair_valor('CHUVA', 0)
                
                # Formata os dados no padrão da aplicação
                dados_formatados = {
                    "data": data_obj.isoformat(),
                    "temperatura": {
                        "atual": temp_inst,
                        "maxima": temp_max,
                        "minima": temp_min,
                        "media": None  # INMET não fornece média diretamente
                    },
                    "chuva": {
                        "precipitacao": precipitacao,
                        "probabilidade": None  # INMET não fornece probabilidade
                    },
                    "umidade": {
                        "atual": umidade
                    },
                    "estacao": {
                        "nome": estacao.get('nome'),
                        "codigo": estacao.get('codigo'),
                        "distancia": estacao.get('distancia')
                    },
                    "fonte": "inmet_diario"
                }
                
                # Se tivermos temperatura máxima e mínima, calculamos a média
                if temp_max is not None and temp_min is not None:
                    dados_formatados["temperatura"]["media"] = round((temp_max + temp_min) / 2, 1)
                
                resultados.append(dados_formatados)
                
            except Exception as e:
                logger.warning(f"Erro ao processar registro diário: {str(e)}")
                continue
        
        return resultados

    def _agregar_dados_mensais(self, dados_diarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Agrega dados diários em médias mensais.
        
        Args:
            dados_diarios: Lista de dados climáticos diários
            
        Returns:
            Lista de dicionários com médias mensais
        """
        if not dados_diarios:
            return []
        
        # Organiza os dados por mês
        dados_por_mes = {}
        
        for dado in dados_diarios:
            # Extrai o ano-mês da data (ex: 2023-04)
            data_str = dado.get('data', '')
            if not data_str:
                continue
                
            try:
                data_obj = datetime.fromisoformat(data_str).date()
                chave_mes = f"{data_obj.year}-{data_obj.month:02d}"
                
                # Inicializa o acumulador para o mês se não existir
                if chave_mes not in dados_por_mes:
                    dados_por_mes[chave_mes] = {
                        "ano": data_obj.year,
                        "mes": data_obj.month,
                        "temp_soma": 0,
                        "temp_min_soma": 0,
                        "temp_max_soma": 0,
                        "umidade_soma": 0,
                        "precipitacao_soma": 0,
                        "contagem": 0,
                        "estacao": dado.get('estacao', {})
                    }
                
                # Extrai valores numéricos dos dados
                temp = dado.get('temperatura', {}).get('media')
                if temp is None:
                    temp = dado.get('temperatura', {}).get('atual', 0)
                    
                temp_min = dado.get('temperatura', {}).get('minima', temp)
                temp_max = dado.get('temperatura', {}).get('maxima', temp)
                umidade = dado.get('umidade', {}).get('atual', 0)
                precipitacao = dado.get('chuva', {}).get('precipitacao', 0)
                
                # Ignora valores None
                if temp is not None:
                    dados_por_mes[chave_mes]["temp_soma"] += temp
                    dados_por_mes[chave_mes]["contagem"] += 1
                
                if temp_min is not None:
                    dados_por_mes[chave_mes]["temp_min_soma"] += temp_min
                
                if temp_max is not None:
                    dados_por_mes[chave_mes]["temp_max_soma"] += temp_max
                
                if umidade is not None:
                    dados_por_mes[chave_mes]["umidade_soma"] += umidade
                
                if precipitacao is not None:
                    dados_por_mes[chave_mes]["precipitacao_soma"] += precipitacao
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Erro ao processar data '{data_str}': {str(e)}")
                continue
        
        # Calcula médias mensais
        resultado = []
        
        for chave_mes, dados in sorted(dados_por_mes.items()):
            # Calcula médias
            contagem = dados["contagem"] or 1  # Evita divisão por zero
            temp_media = dados["temp_soma"] / contagem
            temp_min_media = dados["temp_min_soma"] / contagem
            temp_max_media = dados["temp_max_soma"] / contagem
            umidade_media = dados["umidade_soma"] / contagem
            
            # Formata data do primeiro dia do mês
            data_mes = date(dados["ano"], dados["mes"], 1)
            
            # Formata os dados finais
            dados_formatados = {
                "data": data_mes.isoformat(),
                "ano": dados["ano"],
                "mes": dados["mes"],
                "temperatura": {
                    "media": round(temp_media, 1),
                    "minima": round(temp_min_media, 1),
                    "maxima": round(temp_max_media, 1)
                },
                "chuva": {
                    "precipitacao_total": round(dados["precipitacao_soma"], 1),
                    "precipitacao_media": round(dados["precipitacao_soma"] / contagem, 1)
                },
                "umidade": {
                    "media": round(umidade_media, 1)
                },
                "dias_contabilizados": contagem,
                "estacao": dados["estacao"],
                "fonte": "inmet_mensal"
            }
            
            resultado.append(dados_formatados)
        
        return resultado