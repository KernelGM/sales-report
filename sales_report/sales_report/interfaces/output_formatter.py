"""
Interfaces para formatação de saída.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class OutputFormatter(ABC):
    """
    Interface abstrata para formatadores de saída.

    Define o contrato para diferentes tipos de formatação
    de dados processados (texto, JSON, HTML, etc.).
    """

    @abstractmethod
    def format(self, data: Dict[str, Any]) -> str:
        """
        Formata os dados processados para exibição.

        Args:
            data (Dict[str, Any]): Dados processados a serem formatados.

        Returns:
            str: String formatada pronta para exibição.
        """
        pass  # pragma: no cover
