"""
Módulo de carregamento de configurações do sistema.
Responsável por ler, validar e fornecer acesso às configurações do sistema.
"""

import os
import yaml
from typing import Dict, Any, List, Optional
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CarregadorConfig:
    """
    Carrega e valida configurações do sistema a partir de arquivo YAML.
    Permite sobrescrever valores via variáveis de ambiente ou argumentos CLI.
    """

    def __init__(self, caminho_config: str = "config/config.yaml"):
        """
        Inicializa o carregador de configuração.

        Args:
            caminho_config: Caminho para o arquivo de configuração YAML
        """
        self.caminho_config = caminho_config
        self.config = None
        self._carregar_config()
        self._substituir_variaveis_ambiente()
        self._validar_config()
        logger.info("Configuração carregada com sucesso")

    def _carregar_config(self) -> None:
        """Carrega configuração do arquivo YAML."""
        try:
            with open(self.caminho_config, 'r', encoding='utf-8') as arquivo:
                self.config = yaml.safe_load(arquivo)
            logger.debug(f"Arquivo de configuração carregado: {self.caminho_config}")
        except FileNotFoundError:
            logger.error(f"Arquivo de configuração não encontrado: {self.caminho_config}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Erro ao ler arquivo YAML: {e}")
            raise

    def _substituir_variaveis_ambiente(self) -> None:
        """Substitui variáveis de ambiente nas configurações."""
        # Substitui variáveis de ambiente nas chaves de API
        if 'apis' in self.config:
            for api in self.config['apis']:
                chave = self.config['apis'][api].get('chave', '')
                if isinstance(chave, str) and chave.startswith('${') and chave.endswith('}'):
                    var_env = chave[2:-1]
                    valor_env = os.environ.get(var_env)
                    if valor_env:
                        self.config['apis'][api]['chave'] = valor_env
                    else:
                        logger.warning(f"Variável de ambiente não definida: {var_env}")

    def _validar_config(self) -> None:
        """Valida configurações carregadas."""
        # Validação básica de estrutura
        campos_obrigatorios = ['geral', 'localidades', 'variaveis', 'frequencia', 'apis']
        for campo in campos_obrigatorios:
            if campo not in self.config:
                logger.error(f"Campo obrigatório ausente na configuração: {campo}")
                raise ValueError(f"Campo obrigatório ausente na configuração: {campo}")
        
        # Validação das APIs configuradas
        if 'apis' in self.config:
            apis_configuradas = self.config['apis']
            modo_api = self.config.get('geral', {}).get('modo_api', 'principal')
            
            # Verifica se as APIs necessárias estão configuradas
            if modo_api in ['principal', 'ambas'] and 'openweather' not in apis_configuradas:
                logger.error("API OpenWeather não configurada, mas é necessária pelo modo API")
                raise ValueError("API OpenWeather não configurada, mas é necessária pelo modo API")
            
            if modo_api in ['reserva', 'ambas'] and 'inmet' not in apis_configuradas:
                logger.error("API INMET não configurada, mas é necessária pelo modo API")
                raise ValueError("API INMET não configurada, mas é necessária pelo modo API")

    def obter_config(self) -> Dict[str, Any]:
        """
        Retorna a configuração completa.
        
        Returns:
            Dict contendo a configuração completa
        """
        return self.config

    def obter_localidades(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista de localidades configuradas.
        
        Returns:
            Lista de dicionários com informações das localidades
        """
        return self.config.get('localidades', [])

    def obter_variaveis(self) -> List[Dict[str, Any]]:
        """
        Retorna as variáveis climáticas configuradas.
        
        Returns:
            Lista de dicionários com informações das variáveis
        """
        return self.config.get('variaveis', [])

    def obter_config_api(self, nome_api: str) -> Optional[Dict[str, Any]]:
        """
        Retorna a configuração de uma API específica.
        
        Args:
            nome_api: Nome da API (openweather ou inmet)
            
        Returns:
            Dicionário com configuração da API ou None se não existir
        """
        return self.config.get('apis', {}).get(nome_api)

    def obter_modo_api(self) -> str:
        """
        Retorna o modo de API configurado.
        
        Returns:
            String com o modo de API: "principal", "reserva" ou "ambas"
        """
        return self.config.get('geral', {}).get('modo_api', 'principal')

    def obter_formato_saida(self) -> str:
        """
        Retorna o formato de saída configurado.
        
        Returns:
            String com o formato de saída: "csv", "json", "parquet"
        """
        return self.config.get('geral', {}).get('formato_saida', 'csv')
    
    def obter_tipo_frequencia(self) -> str:
        """
        Retorna o tipo de frequência configurado.
        
        Returns:
            String com o tipo de frequência: "diaria" ou "mensal"
        """
        return self.config.get('frequencia', {}).get('tipo', 'diaria')
    
    def obter_configuracao_historico(self) -> Dict[str, Any]:
        """
        Retorna a configuração de dados históricos.
        
        Returns:
            Dicionário com configuração de dados históricos
        """
        return self.config.get('frequencia', {}).get('historico', {'ativo': False, 'anos': 5})

    @staticmethod
    def criar_config_padrao(caminho: str = "config/config.yaml") -> None:
        """
        Cria um arquivo de configuração padrão.
        
        Args:
            caminho: Caminho onde o arquivo será criado
        """
        # Exemplo de configuração padrão
        config_padrao = {
            "geral": {
                "modo_api": "principal",
                "formato_saida": "csv",
                "arquivo_saida": {
                    "tipo": "separado",
                    "diretorio": "dados"
                }
            },
            "localidades": [
                {
                    "nome": "São Paulo",
                    "latitude": -23.5505,
                    "longitude": -46.6333
                }
            ],
            "variaveis": [
                {
                    "nome": "temperatura",
                    "unidade": "celsius",
                    "ativo": True
                },
                {
                    "nome": "chuva",
                    "unidade": "mm",
                    "ativo": True
                },
                {
                    "nome": "umidade",
                    "unidade": "percentual",
                    "ativo": True
                }
            ],
            "frequencia": {
                "tipo": "diaria",
                "historico": {
                    "ativo": False,
                    "anos": 5
                }
            },
            "apis": {
                "openweather": {
                    "chave": "${OPENWEATHER_API_KEY}",
                    "base_url": "https://api.openweathermap.org/data/2.5",
                    "timeout": 30,
                    "tentativas": 3
                },
                "inmet": {
                    "chave": "${INMET_API_KEY}",
                    "base_url": "https://apitempo.inmet.gov.br/api",
                    "timeout": 30,
                    "tentativas": 3
                }
            }
        }
        
        # Cria diretório se não existir
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        
        # Escreve o arquivo
        with open(caminho, 'w', encoding='utf-8') as arquivo:
            yaml.dump(config_padrao, arquivo, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"Arquivo de configuração padrão criado em: {caminho}")

    def atualizar_config_cli(self, args: Dict[str, Any]) -> None:
        """
        Atualiza configurações a partir de argumentos CLI.
        
        Args:
            args: Dicionário com argumentos da linha de comando
        """
        # Exemplo de atualização com argumentos CLI
        if args.get('modo_api'):
            self.config['geral']['modo_api'] = args['modo_api']
        
        if args.get('formato_saida'):
            self.config['geral']['formato_saida'] = args['formato_saida']
        
        if args.get('tipo_frequencia'):
            self.config['frequencia']['tipo'] = args['tipo_frequencia']
        
        if args.get('historico_ativo') is not None:
            self.config['frequencia']['historico']['ativo'] = args['historico_ativo']
        
        if args.get('historico_anos'):
            self.config['frequencia']['historico']['anos'] = args['historico_anos']
            
        logger.info("Configuração atualizada com argumentos CLI")