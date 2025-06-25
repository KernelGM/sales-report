"""
Implementação do formatador JSON.
"""

from json import dumps
from typing import Any, Dict

from sales_report.interfaces.output_formatter import OutputFormatter


class JSONFormatter(OutputFormatter):
    """
    Formatador que converte dados processados em JSON.

    Responsável exclusivamente por formatar dados em formato
    JSON com indentação adequada.
    """

    @staticmethod
    def format(data: Dict[str, Any]) -> str:
        """
        Formata os dados processados em JSON.

        Args:
            data (Dict[str, Any]): Dados processados de vendas.

        Returns:
            str: String JSON formatada com os dados de vendas.
        """
        return dumps(data, indent=2, ensure_ascii=False)
