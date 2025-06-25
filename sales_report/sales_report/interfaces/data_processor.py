"""
Interfaces para processamento de dados.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class DataProcessor(ABC):
    """
    Interface abstrata para processadores de dados.

    Define o contrato para classes que processam dados de vendas
    e geram estatísticas.
    """

    @abstractmethod
    def process(self, data: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Processa os dados e retorna estatísticas.

        Args:
            data (List[Dict[str, str]]): Lista de registros de dados.

        Returns:
            Dict[str, Any]: Dicionário com as estatísticas processadas.
        """
        pass  # pragma: no cover
