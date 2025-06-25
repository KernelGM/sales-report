"""
Implementação do leitor de arquivos CSV.
"""

from csv import DictReader
from logging import getLogger
from typing import Dict, List

from sales_report.interfaces.data_reader import DataReader

logger = getLogger(__name__)


class CSVReader(DataReader):
    """
    Implementação concreta do leitor de dados para arquivos CSV.

    Responsável exclusivamente por ler arquivos CSV com tratamento
    de diferentes encodings.
    """

    def __init__(self, file_path: str) -> None:
        """
        Inicializa o leitor de CSV com o caminho do arquivo.

        Args:
            file_path (str): Caminho para o arquivo CSV a ser lido.
        """
        self.file_path: str = file_path

    def read(self) -> List[Dict[str, str]]:
        """
        Lê o arquivo CSV e retorna uma lista de dicionários.

        Tenta ler o arquivo usando encoding UTF-8 primeiro, e em caso de erro,
        faz fallback para CP1252. Trata erros de arquivo não encontrado e
        outros erros de leitura.

        Returns:
            List[Dict[str, str]]: Lista de dicionários onde cada dicionário
                representa uma linha do CSV com as colunas como chaves.
                Retorna lista vazia em caso de erro.
        """
        try:
            with open(self.file_path, newline='', encoding='utf-8') as f:
                logger.debug(f'Lendo arquivo CSV: {self.file_path}')
                return list(DictReader(f))
        except UnicodeDecodeError:
            try:
                with open(self.file_path, newline='', encoding='cp1252') as f:
                    logger.debug(
                        f'Lendo com fallback cp1252: {self.file_path}'
                    )
                    return list(DictReader(f))
            except Exception as e:
                logger.error(f'Erro ao ler CSV com fallback cp1252: {e}')
        except FileNotFoundError:
            logger.error(f'Arquivo não encontrado: {self.file_path}')
        except Exception as e:
            logger.error(f'Erro ao ler o CSV: {e}')
        return []
