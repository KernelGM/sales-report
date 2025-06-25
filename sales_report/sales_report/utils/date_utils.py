"""
Utilitários para manipulação de datas.
"""

from datetime import datetime
from logging import getLogger
from typing import Optional

logger = getLogger(__name__)


class DateUtils:
    """
    Classe utilitária para operações com datas.

    Centraliza a lógica de parsing e validação de datas
    para reutilização em diferentes partes da aplicação.
    """

    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """
        Converte uma string de data no formato YYYY-MM-DD para datetime.

        Args:
            date_str (Optional[str]): String da data no formato YYYY-MM-DD
                ou None.

        Returns:
            Optional[datetime]: Objeto datetime se a conversão estiver OK,
                None se date_str for None ou inválida.
        """
        if not date_str:
            return None

        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError as e:
            logger.error(
                f'Data inválida: "{date_str}". Esperado YYYY-MM-DD. Erro: {e}'
            )
            return None
