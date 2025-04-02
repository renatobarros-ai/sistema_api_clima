"""
Módulo de integração com a API do OpenWeather.
Implementa a interface para obter dados climáticos do OpenWeather.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional

from src.api.base_api import BaseApiClima

# Configuração de logging
logger = logging.getLogger(__name__)


class OpenWeatherApi(BaseApiClima):
    """
    Implementação da API do OpenWeather.
    
    Documentação da API: https://openweathermap.org/api
    """

    def _obter_param_chave(self) -> Dict[str, str]:
        """
        Retorna o parâmetro com a chave de API no formato específico do OpenWeather.
        
        Returns:
            Dicionário com o parâmetro da chave API (appid)
        """
        return {"appid": self.chave}

    def obter_dados_diarios(
        self, 
        latitude: float, 
        longitude: float, 
        data_inicio: Optional[date] = None, 
        data_fim: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados climáticos diários do OpenWeather.
        
        Para dados atuais, usa a API Current Weather.
        Para múltiplos dias, usa a API 5 Day Forecast ou API histórica.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            data_inicio: Data inicial para coleta (opcional)
            data_fim: Data final para coleta (opcional)
            
        Returns:
            Lista de dicionários com dados climáticos diários
        """
        hoje = date.today()
        
        # Se não tiver data especificada, usa data atual
        if not data_inicio and not data_fim:
            return self._obter_dados_atuais(latitude, longitude)
        
        # Se data de início for no futuro (próximos 5 dias), usa previsão
        if data_inicio and data_inicio > hoje and (data_inicio - hoje).days <= 5:
            return self._obter_dados_previsao(latitude, longitude, data_inicio, data_fim)
        
        # Se data estiver no passado, usa dados históricos
        if (data_inicio and data_inicio < hoje) or (data_fim and data_fim < hoje):
            return self._obter_dados_historicos_diarios(latitude, longitude, data_inicio, data_fim)
        
        # Caso padrão para outras situações
        logger.warning("Intervalo de datas não suportado, usando dados atuais")
        return self._obter_dados_atuais(latitude, longitude)

    def obter_dados_mensais(
        self, 
        latitude: float, 
        longitude: float, 
        data_inicio: Optional[date] = None, 
        data_fim: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados climáticos mensais do OpenWeather.
        
        Agrega dados diários para formar médias mensais.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            data_inicio: Data inicial para coleta (opcional)
            data_fim: Data final para coleta (opcional)
            
        Returns:
            Lista de dicionários com dados climáticos mensais
        """
        # Se não tiver data especificada, usa o mês atual
        if not data_inicio and not data_fim:
            hoje = date.today()
            primeiro_dia_mes = date(hoje.year, hoje.month, 1)
            dados_diarios = self._obter_dados_historicos_diarios(
                latitude, longitude, primeiro_dia_mes, hoje)
            return self._agregar_dados_mensais(dados_diarios)
        
        # Para outros períodos, obtém dados diários e agrega
        dados_diarios = self._obter_dados_historicos_diarios(
            latitude, longitude, data_inicio, data_fim)
        return self._agregar_dados_mensais(dados_diarios)

    def obter_dados_historicos(
        self, 
        latitude: float, 
        longitude: float, 
        anos: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados históricos do OpenWeather.
        
        Note: Dados históricos do OpenWeather são pagos e requerem assinatura especial.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            anos: Número de anos para recuperar dados históricos
            
        Returns:
            Lista de dicionários com dados climáticos históricos
        """
        data_inicio, data_fim = self.gerar_datas_ate_hoje(anos)
        
        logger.info(f"Obtendo dados históricos de {data_inicio} até {data_fim}")
        
        return self._obter_dados_historicos_diarios(latitude, longitude, data_inicio, data_fim)

    def _obter_dados_atuais(self, latitude: float, longitude: float) -> List[Dict[str, Any]]:
        """
        Obtém dados climáticos atuais usando a API Current Weather.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            
        Returns:
            Lista com um dicionário contendo dados climáticos atuais
        """
        try:
            params = {
                "lat": latitude,
                "lon": longitude,
                "units": "metric",  # Celsius, m/s
                "lang": "pt_br"
            }
            
            resposta = self._fazer_requisicao("weather", params)
            
            # Converte para o formato padronizado
            dados_formatados = self._formatar_dados_atuais(resposta)
            return [dados_formatados]  # Retorna como lista para manter interface consistente
            
        except Exception as e:
            logger.error(f"Erro ao obter dados atuais: {str(e)}")
            return []

    def _obter_dados_previsao(
        self, 
        latitude: float, 
        longitude: float, 
        data_inicio: date, 
        data_fim: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém previsão de 5 dias usando a API 5 Day Forecast.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            data_inicio: Data inicial da previsão
            data_fim: Data final da previsão (opcional)
            
        Returns:
            Lista de dicionários com previsões diárias
        """
        try:
            params = {
                "lat": latitude,
                "lon": longitude,
                "units": "metric",
                "lang": "pt_br"
            }
            
            resposta = self._fazer_requisicao("forecast", params)
            
            # A API retorna dados a cada 3 horas, precisamos agregar por dia
            dados_formatados = self._formatar_dados_previsao(resposta, data_inicio, data_fim)
            return dados_formatados
            
        except Exception as e:
            logger.error(f"Erro ao obter previsão: {str(e)}")
            return []

    def _obter_dados_historicos_diarios(
        self, 
        latitude: float, 
        longitude: float, 
        data_inicio: Optional[date] = None, 
        data_fim: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados históricos diários.
        
        Nota: Para acesso completo é necessário assinatura One Call API.
        Nesta implementação, usamos chamadas simuladas para demonstração.
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            data_inicio: Data inicial para dados históricos
            data_fim: Data final para dados históricos
            
        Returns:
            Lista de dicionários com dados históricos
        """
        # Define datas padrão se não forem fornecidas
        if not data_inicio:
            data_inicio, _ = self.gerar_datas_ate_hoje(1)  # Último ano
            
        if not data_fim:
            data_fim = date.today()
        
        logger.info(f"Obtendo dados históricos de {data_inicio} até {data_fim}")
        
        # Como a API histórica completa é paga, esta é uma implementação simulada
        # Em um ambiente real, seria necessário usar a API histórica apropriada 
        # e processar os resultados de acordo
        
        # Simulação de dados históricos para demonstração
        resultado = []
        data_atual = data_inicio
        
        while data_atual <= data_fim:
            # Gera um registro por dia no intervalo
            registro = {
                "data": data_atual.isoformat(),
                "temperatura": {
                    "media": 20 + (data_atual.month / 3),  # Simulação simples de temperatura
                    "minima": 15 + (data_atual.month / 4),
                    "maxima": 25 + (data_atual.month / 2)
                },
                "chuva": {
                    "precipitacao": 5 if data_atual.month in [1, 2, 3, 11, 12] else 0.5,
                    "probabilidade": 80 if data_atual.month in [1, 2, 3, 11, 12] else 10
                },
                "umidade": {
                    "media": 75 if data_atual.month in [1, 2, 3, 11, 12] else 60
                },
                "fonte": "openweather_simulado"
            }
            
            resultado.append(registro)
            data_atual += timedelta(days=1)
        
        return resultado

    def _formatar_dados_atuais(self, dados_api: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formata os dados da API Current Weather para o formato padronizado.
        
        Args:
            dados_api: Resposta da API do OpenWeather
            
        Returns:
            Dicionário com dados no formato padronizado
        """
        try:
            # Data de medição (convertendo timestamp Unix para data)
            timestamp = dados_api.get('dt', 0)
            data_medicao = datetime.fromtimestamp(timestamp).date()
            
            # Extrai os dados relevantes da resposta da API
            dados_formatados = {
                "data": data_medicao.isoformat(),
                "temperatura": {
                    "atual": dados_api.get('main', {}).get('temp'),
                    "minima": dados_api.get('main', {}).get('temp_min'),
                    "maxima": dados_api.get('main', {}).get('temp_max'),
                    "sensacao": dados_api.get('main', {}).get('feels_like')
                },
                "chuva": {
                    "precipitacao": dados_api.get('rain', {}).get('1h', 0),
                    "probabilidade": 0  # API atual não fornece probabilidade
                },
                "umidade": {
                    "atual": dados_api.get('main', {}).get('humidity')
                },
                "vento": {
                    "velocidade": dados_api.get('wind', {}).get('speed'),
                    "direcao": dados_api.get('wind', {}).get('deg')
                },
                "descricao": dados_api.get('weather', [{}])[0].get('description', ''),
                "cidade": dados_api.get('name', ''),
                "fonte": "openweather_atual"
            }
            
            return dados_formatados
            
        except Exception as e:
            logger.error(f"Erro ao formatar dados atuais: {str(e)}")
            # Retorna um objeto mínimo em caso de erro
            return {
                "data": date.today().isoformat(),
                "erro": str(e),
                "fonte": "openweather_erro"
            }

    def _formatar_dados_previsao(
        self, 
        dados_api: Dict[str, Any], 
        data_inicio: date, 
        data_fim: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Formata os dados da API 5 Day Forecast para o formato padronizado.
        A API fornece dados a cada 3 horas, que são agregados por dia.
        
        Args:
            dados_api: Resposta da API do OpenWeather
            data_inicio: Data inicial para filtrar resultados
            data_fim: Data final para filtrar resultados
            
        Returns:
            Lista de dicionários com dados no formato padronizado
        """
        try:
            # Se não tiver data_fim, usa 5 dias a partir da data_inicio (máximo da API)
            if not data_fim:
                data_fim = data_inicio + timedelta(days=5)
                
            # Organiza os dados por dia (a API retorna a cada 3h)
            dados_por_dia = {}
            
            # Lista de previsões a cada 3 horas
            previsoes = dados_api.get('list', [])
            
            for previsao in previsoes:
                # Converte timestamp para data
                timestamp = previsao.get('dt', 0)
                data_previsao = datetime.fromtimestamp(timestamp).date()
                
                # Só processa se estiver no intervalo solicitado
                if data_inicio <= data_previsao <= data_fim:
                    # Inicializa o acumulador para o dia se não existir
                    if data_previsao not in dados_por_dia:
                        dados_por_dia[data_previsao] = {
                            "temp_min": float('inf'),
                            "temp_max": float('-inf'),
                            "temp_soma": 0,
                            "umidade_soma": 0,
                            "precipitacao_soma": 0,
                            "prob_precipitacao_soma": 0,
                            "contagem": 0,
                            "descricoes": set()
                        }
                    
                    # Extrai dados da previsão atual
                    temp = previsao.get('main', {}).get('temp', 0)
                    temp_min = previsao.get('main', {}).get('temp_min', temp)
                    temp_max = previsao.get('main', {}).get('temp_max', temp)
                    umidade = previsao.get('main', {}).get('humidity', 0)
                    precipitacao = previsao.get('rain', {}).get('3h', 0)
                    prob_precipitacao = previsao.get('pop', 0) * 100  # Converte de 0-1 para 0-100%
                    descricao = previsao.get('weather', [{}])[0].get('description', '')
                    
                    # Atualiza dados acumulados
                    dados_por_dia[data_previsao]["temp_soma"] += temp
                    dados_por_dia[data_previsao]["temp_min"] = min(dados_por_dia[data_previsao]["temp_min"], temp_min)
                    dados_por_dia[data_previsao]["temp_max"] = max(dados_por_dia[data_previsao]["temp_max"], temp_max)
                    dados_por_dia[data_previsao]["umidade_soma"] += umidade
                    dados_por_dia[data_previsao]["precipitacao_soma"] += precipitacao
                    dados_por_dia[data_previsao]["prob_precipitacao_soma"] += prob_precipitacao
                    dados_por_dia[data_previsao]["contagem"] += 1
                    dados_por_dia[data_previsao]["descricoes"].add(descricao)
            
            # Converte os dados acumulados para o formato final
            resultado = []
            
            cidade = dados_api.get('city', {}).get('name', '')
            
            for data_previsao, dados in sorted(dados_por_dia.items()):
                # Calcula médias
                contagem = dados["contagem"] or 1  # Evita divisão por zero
                temp_media = dados["temp_soma"] / contagem
                umidade_media = dados["umidade_soma"] / contagem
                prob_precipitacao_media = dados["prob_precipitacao_soma"] / contagem
                
                # Descrição mais comum do dia
                descricao = "; ".join(dados["descricoes"]) if dados["descricoes"] else ""
                
                # Formata os dados finais
                dados_formatados = {
                    "data": data_previsao.isoformat(),
                    "temperatura": {
                        "media": round(temp_media, 1),
                        "minima": round(dados["temp_min"], 1) if dados["temp_min"] != float('inf') else None,
                        "maxima": round(dados["temp_max"], 1) if dados["temp_max"] != float('-inf') else None
                    },
                    "chuva": {
                        "precipitacao": round(dados["precipitacao_soma"], 1),
                        "probabilidade": round(prob_precipitacao_media, 1)
                    },
                    "umidade": {
                        "media": round(umidade_media, 1)
                    },
                    "descricao": descricao,
                    "cidade": cidade,
                    "fonte": "openweather_previsao"
                }
                
                resultado.append(dados_formatados)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao formatar dados de previsão: {str(e)}")
            return []

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
                        "cidade": dado.get('cidade', '')
                    }
                
                # Extrai valores numéricos dos dados
                temp = dado.get('temperatura', {}).get('media')
                if temp is None:
                    temp = dado.get('temperatura', {}).get('atual', 0)
                    
                temp_min = dado.get('temperatura', {}).get('minima', temp)
                temp_max = dado.get('temperatura', {}).get('maxima', temp)
                umidade = dado.get('umidade', {}).get('media')
                if umidade is None:
                    umidade = dado.get('umidade', {}).get('atual', 0)
                    
                precipitacao = dado.get('chuva', {}).get('precipitacao', 0)
                
                # Atualiza acumuladores
                dados_por_mes[chave_mes]["temp_soma"] += temp
                dados_por_mes[chave_mes]["temp_min_soma"] += temp_min
                dados_por_mes[chave_mes]["temp_max_soma"] += temp_max
                dados_por_mes[chave_mes]["umidade_soma"] += umidade
                dados_por_mes[chave_mes]["precipitacao_soma"] += precipitacao
                dados_por_mes[chave_mes]["contagem"] += 1
                
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
                "cidade": dados["cidade"],
                "fonte": "openweather_mensal"
            }
            
            resultado.append(dados_formatados)
        
        return resultado