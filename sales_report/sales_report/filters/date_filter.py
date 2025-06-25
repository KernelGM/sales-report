"""
Implementação de filtros baseados em data.
"""

from datetime import datetime
from logging import getLogger
from typing import Dict, List, Optional

from sales_report.interfaces.data_filter import DataFilter

logger = getLogger(__name__)


class DateFilter(DataFilter):
    """
    Filtro que seleciona registros baseado em data.

    Responsável exclusivamente por filtrar dados baseado em
    datas de início e fim especificadas.
    """

    def __init__(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        date_column: str = 'data_venda',
    ) -> None:
        """
        Inicializa o filtro de data.

        Args:
            start_date (Optional[datetime]): Data inicial para filtro.
            end_date (Optional[datetime]): Data final para filtro.
            date_column (str): Nome da coluna que contém a data.
        """
        self.start_date = start_date
        self.end_date = end_date
        self.date_column = date_column

    def filter(self, data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Aplica o filtro de data aos dados.

        Args:
            data (List[Dict[str, str]]): Lista de registros originais.

        Returns:
            List[Dict[str, str]]: Lista de registros que estão dentro
                do intervalo de datas especificado.
        """
        if not self.start_date and not self.end_date:
            return data

        if not data or self.date_column not in data[0]:
            logger.warning(
                f'Coluna "{self.date_column}" não encontrada nos dados. '
                'Filtro de data será ignorado.'
            )
            return data

        filtered_data: List[Dict[str, str]] = []

        for row in data:
            date_str = row.get(self.date_column, '').strip()

            if not date_str:
                logger.debug(
                    'Linha sem data encontrada, incluindo no resultado'
                )
                filtered_data.append(row)
                continue

            date_obj = self._parse_date(date_str)

            if date_obj is None:
                logger.warning(
                    f'Data ignorada por formato inválido: {date_str}'
                )
                continue

            if self._is_date_in_range(date_obj):
                filtered_data.append(row)

        return filtered_data

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        """
        Converte uma string de data no formato YYYY-MM-DD para datetime.

        Args:
            date_str (str): String da data no formato YYYY-MM-DD.

        Returns:
            Optional[datetime]: Objeto datetime se a conversão estiver OK,
                None caso contrário.
        """
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError as e:
            logger.error(
                f'Data inválida: "{date_str}". Esperado YYYY-MM-DD. Erro: {e}'
            )
            return None

    def _is_date_in_range(self, date_obj: datetime) -> bool:
        """
        Verifica se a data está dentro do intervalo especificado.

        Args:
            date_obj (datetime): Data a ser verificada.

        Returns:
            bool: True se a data estiver no intervalo, False caso contrário.
        """
        if self.start_date and date_obj < self.start_date:
            return False
        if self.end_date and date_obj > self.end_date:
            return False
        return True
