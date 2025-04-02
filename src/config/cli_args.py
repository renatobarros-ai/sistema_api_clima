"""
Módulo para processamento de argumentos de linha de comando.
Permite sobrescrever configurações do arquivo YAML através da CLI.
"""

import argparse
from typing import Dict, Any


def criar_parser_argumentos() -> argparse.ArgumentParser:
    """
    Cria o parser de argumentos da linha de comando.
    
    Returns:
        Parser de argumentos configurado
    """
    parser = argparse.ArgumentParser(
        description="Sistema API Clima - Coleta de dados climáticos",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Argumento para caminho do arquivo de configuração
    parser.add_argument(
        "-c", "--config",
        dest="caminho_config",
        default="config/config.yaml",
        help="Caminho para o arquivo de configuração YAML"
    )
    
    # Argumentos para sobrescrever configurações
    parser.add_argument(
        "--modo-api",
        choices=["principal", "reserva", "ambas"],
        help="Modo de API a ser utilizado"
    )
    
    parser.add_argument(
        "--formato-saida",
        choices=["csv", "json", "parquet"],
        help="Formato de saída dos dados"
    )
    
    parser.add_argument(
        "--tipo-arquivo",
        choices=["separado", "concatenado"],
        help="Tipo de arquivo de saída"
    )
    
    parser.add_argument(
        "--diretorio-saida",
        help="Diretório para salvar os arquivos de saída"
    )
    
    parser.add_argument(
        "--frequencia",
        choices=["diaria", "mensal"],
        help="Frequência de coleta dos dados"
    )
    
    # Argumentos para dados históricos
    grupo_historico = parser.add_argument_group("Dados históricos")
    
    grupo_historico.add_argument(
        "--historico",
        dest="historico_ativo",
        action="store_true",
        help="Ativar coleta de dados históricos"
    )
    
    grupo_historico.add_argument(
        "--no-historico",
        dest="historico_ativo",
        action="store_false",
        help="Desativar coleta de dados históricos"
    )
    
    grupo_historico.add_argument(
        "--anos-historico",
        dest="historico_anos",
        type=int,
        help="Número de anos para dados históricos"
    )
    
    # Configurações da execução
    grupo_execucao = parser.add_argument_group("Controle de execução")
    
    grupo_execucao.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="Aumenta o nível de detalhamento do log (use -vv para ainda mais detalhes)"
    )
    
    grupo_execucao.add_argument(
        "--gerar-config",
        action="store_true",
        help="Gera um arquivo de configuração padrão e sai"
    )
    
    return parser


def processar_argumentos() -> Dict[str, Any]:
    """
    Processa os argumentos da linha de comando.
    
    Returns:
        Dicionário com os argumentos processados
    """
    parser = criar_parser_argumentos()
    args = parser.parse_args()
    
    # Converte Namespace para dicionário
    return vars(args)