"""
Interfaces para leitura de dados.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class DataReader(ABC):
    """
    Interface abstrata para leitores de dados.

    Define o contrato que todos os leitores de dados devem seguir,
    permitindo diferentes implementações (CSV, JSON, XML, etc.).
    """

    @abstractmethod
    def read(self) -> List[Dict[str, str]]:
        """
        Lê os dados da fonte e retorna uma lista de dicionários.

        Returns:
            List[Dict[str, str]]: Lista de registros onde cada registro
                é um dicionário com os dados.
        """
        pass  # pragma: no cover
