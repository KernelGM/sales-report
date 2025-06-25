"""
Interfaces para validação de dados.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple


class DataValidator(ABC):
    """
    Interface abstrata para validadores de dados.

    Define o contrato para validação de dados antes do processamento.
    """

    @abstractmethod
    def validate(
        self, data: List[Dict[str, str]]
    ) -> Tuple[List[Dict[str, str]], List[str]]:
        """
        Valida os dados e retorna dados válidos e erros encontrados.

        Args:
            data (List[Dict[str, str]]): Lista de registros a serem validados.

        Returns:
            Tuple[List[Dict[str, str]], List[str]]: Tupla contendo
                lista de registros válidos e lista de mensagens de erro.
        """
        pass  # pragma: no cover
