"""
Módulo principal do Sistema API Clima.
Ponto de entrada para execução do sistema.
"""

import os
import sys
import logging
from datetime import date, timedelta
from typing import Dict, List, Any

# Configura o módulo para estar no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.carregador_config import CarregadorConfig
from src.config.cli_args import processar_argumentos
from src.api.gerenciador_api import GerenciadorApi
from src.processadores.processador_diario import ProcessadorDiario
from src.processadores.processador_mensal import ProcessadorMensal
from src.exportadores.gerenciador_exportacao import GerenciadorExportacao


# Configuração inicial de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def configurar_nivel_log(verbose: int) -> None:
    """
    Configura o nível de log com base no parâmetro de verbosidade.
    
    Args:
        verbose: Nível de verbosidade (0=INFO, 1=DEBUG)
    """
    if verbose >= 1:
        # Define o nível de log para DEBUG
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Modo de log detalhado ativado")


def coletar_dados_diarios(
    gerenciador_api: GerenciadorApi,
    localidades: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Coleta dados diários para todas as localidades configuradas.
    
    Args:
        gerenciador_api: Gerenciador de API para coleta de dados
        localidades: Lista de localidades configuradas
        
    Returns:
        Dicionário com dados diários por localidade
    """
    dados_por_localidade = {}
    
    for localidade in localidades:
        nome = localidade.get('nome', 'desconhecida')
        lat = localidade.get('latitude')
        lon = localidade.get('longitude')
        
        if lat is None or lon is None:
            logger.warning(f"Coordenadas ausentes para {nome}, ignorando")
            continue
        
        logger.info(f"Coletando dados diários para {nome} ({lat}, {lon})")
        
        try:
            # Coleta dados dos últimos 7 dias
            data_fim = date.today()
            data_inicio = data_fim - timedelta(days=7)
            
            dados = gerenciador_api.obter_dados_diarios(
                latitude=lat,
                longitude=lon,
                data_inicio=data_inicio,
                data_fim=data_fim
            )
            
            if dados:
                dados_por_localidade[nome] = dados
                logger.info(f"Coletados {len(dados)} registros diários para {nome}")
            else:
                logger.warning(f"Nenhum dado diário encontrado para {nome}")
        
        except Exception as e:
            logger.error(f"Erro ao coletar dados diários para {nome}: {str(e)}")
    
    return dados_por_localidade


def coletar_dados_mensais(
    gerenciador_api: GerenciadorApi,
    localidades: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Coleta dados mensais para todas as localidades configuradas.
    
    Args:
        gerenciador_api: Gerenciador de API para coleta de dados
        localidades: Lista de localidades configuradas
        
    Returns:
        Dicionário com dados mensais por localidade
    """
    dados_por_localidade = {}
    
    for localidade in localidades:
        nome = localidade.get('nome', 'desconhecida')
        lat = localidade.get('latitude')
        lon = localidade.get('longitude')
        
        if lat is None or lon is None:
            logger.warning(f"Coordenadas ausentes para {nome}, ignorando")
            continue
        
        logger.info(f"Coletando dados mensais para {nome} ({lat}, {lon})")
        
        try:
            # Coleta dados dos últimos 12 meses
            dados = gerenciador_api.obter_dados_mensais(
                latitude=lat,
                longitude=lon
            )
            
            if dados:
                dados_por_localidade[nome] = dados
                logger.info(f"Coletados {len(dados)} registros mensais para {nome}")
            else:
                logger.warning(f"Nenhum dado mensal encontrado para {nome}")
        
        except Exception as e:
            logger.error(f"Erro ao coletar dados mensais para {nome}: {str(e)}")
    
    return dados_por_localidade


def coletar_dados_historicos(
    gerenciador_api: GerenciadorApi,
    localidades: List[Dict[str, Any]],
    anos: int
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Coleta dados históricos para todas as localidades configuradas.
    
    Args:
        gerenciador_api: Gerenciador de API para coleta de dados
        localidades: Lista de localidades configuradas
        anos: Número de anos para coletar dados históricos
        
    Returns:
        Dicionário com dados históricos por localidade
    """
    dados_por_localidade = {}
    
    for localidade in localidades:
        nome = localidade.get('nome', 'desconhecida')
        lat = localidade.get('latitude')
        lon = localidade.get('longitude')
        
        if lat is None or lon is None:
            logger.warning(f"Coordenadas ausentes para {nome}, ignorando")
            continue
        
        logger.info(f"Coletando dados históricos para {nome} ({lat}, {lon}) - {anos} anos")
        
        try:
            dados = gerenciador_api.obter_dados_historicos(
                latitude=lat,
                longitude=lon,
                anos=anos
            )
            
            if dados:
                dados_por_localidade[nome] = dados
                logger.info(f"Coletados {len(dados)} registros históricos para {nome}")
            else:
                logger.warning(f"Nenhum dado histórico encontrado para {nome}")
        
        except Exception as e:
            logger.error(f"Erro ao coletar dados históricos para {nome}: {str(e)}")
    
    return dados_por_localidade


def processar_e_exportar_dados(
    dados_por_localidade: Dict[str, List[Dict[str, Any]]],
    config: Dict[str, Any],
    tipo_dados: str
) -> None:
    """
    Processa e exporta os dados coletados.
    
    Args:
        dados_por_localidade: Dicionário com dados por localidade
        config: Configuração do sistema
        tipo_dados: Tipo de dados (diario, mensal, historico)
    """
    if not dados_por_localidade:
        logger.warning(f"Nenhum dado {tipo_dados} para processar")
        return
    
    # Inicializa o processador adequado
    if tipo_dados in ['diario', 'historico']:
        processador = ProcessadorDiario(config)
    else:  # mensal
        processador = ProcessadorMensal(config)
    
    # Inicializa o gerenciador de exportação
    gerenciador_exportacao = GerenciadorExportacao(config)
    
    # Processa e exporta para cada localidade
    dados_processados_por_localidade = {}
    
    for localidade, dados in dados_por_localidade.items():
        try:
            # Processa os dados
            dados_processados = processador.processar(dados)
            
            if dados_processados:
                dados_processados_por_localidade[localidade] = dados_processados
                logger.info(f"Processados {len(dados_processados)} registros {tipo_dados} para {localidade}")
            else:
                logger.warning(f"Nenhum dado {tipo_dados} processado para {localidade}")
        
        except Exception as e:
            logger.error(f"Erro ao processar dados {tipo_dados} para {localidade}: {str(e)}")
    
    # Exporta os dados processados
    try:
        arquivos = gerenciador_exportacao.exportar_multiplas_localidades(
            dados_processados_por_localidade, tipo_dados
        )
        
        if arquivos:
            logger.info(f"Dados {tipo_dados} exportados para {len(arquivos)} arquivos")
            for arquivo in arquivos:
                logger.info(f"Arquivo gerado: {arquivo}")
        else:
            logger.warning(f"Nenhum arquivo de dados {tipo_dados} gerado")
    
    except Exception as e:
        logger.error(f"Erro ao exportar dados {tipo_dados}: {str(e)}")


def main() -> None:
    """
    Função principal que coordena a execução do sistema.
    """
    try:
        # Processa argumentos da linha de comando
        args = processar_argumentos()
        
        # Configura o nível de log
        configurar_nivel_log(args.get('verbose', 0))
        
        # Se solicitado, gera o arquivo de configuração padrão e sai
        if args.get('gerar_config'):
            caminho_config = args.get('caminho_config', 'config/config.yaml')
            CarregadorConfig.criar_config_padrao(caminho_config)
            logger.info(f"Arquivo de configuração padrão criado em: {caminho_config}")
            return
        
        # Carrega a configuração
        caminho_config = args.get('caminho_config', 'config/config.yaml')
        carregador = CarregadorConfig(caminho_config)
        
        # Atualiza a configuração com argumentos da linha de comando
        carregador.atualizar_config_cli(args)
        
        # Obtém a configuração atualizada
        config = carregador.obter_config()
        
        # Obtém as localidades configuradas
        localidades = carregador.obter_localidades()
        
        if not localidades:
            logger.error("Nenhuma localidade configurada")
            return
        
        # Inicializa o gerenciador de API
        gerenciador_api = GerenciadorApi(config)
        
        # Obtém o tipo de frequência configurado
        tipo_frequencia = carregador.obter_tipo_frequencia()
        
        # Coleta e processa dados conforme a frequência configurada
        if tipo_frequencia == 'diaria':
            # Coleta dados diários
            dados_diarios = coletar_dados_diarios(gerenciador_api, localidades)
            processar_e_exportar_dados(dados_diarios, config, 'diario')
        
        elif tipo_frequencia == 'mensal':
            # Coleta dados mensais
            dados_mensais = coletar_dados_mensais(gerenciador_api, localidades)
            processar_e_exportar_dados(dados_mensais, config, 'mensal')
        
        # Verifica se deve coletar dados históricos
        config_historico = carregador.obter_configuracao_historico()
        
        if config_historico.get('ativo'):
            anos = config_historico.get('anos', 5)
            
            # Coleta dados históricos
            dados_historicos = coletar_dados_historicos(gerenciador_api, localidades, anos)
            
            # Processa e exporta dados históricos
            processar_e_exportar_dados(dados_historicos, config, 'historico')
        
        logger.info("Processamento concluído com sucesso")
    
    except Exception as e:
        logger.error(f"Erro na execução principal: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()