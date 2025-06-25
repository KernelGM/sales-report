"""
Interfaces para filtros de dados.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class DataFilter(ABC):
    """
    Interface abstrata para filtros de dados.

    Permite implementar diferentes tipos de filtros que podem
    ser aplicados aos dados antes do processamento.
    """

    @abstractmethod
    def filter(self, data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Aplica o filtro aos dados.

        Args:
            data (List[Dict[str, str]]): Lista de registros originais.

        Returns:
            List[Dict[str, str]]: Lista de registros filtrados.
        """
        pass  # pragma: no cover
