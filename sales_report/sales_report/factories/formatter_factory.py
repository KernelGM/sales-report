"""
Factory para criação de formatadores.
"""

from typing import Dict, Type

from sales_report.formatters.json_formatter import JSONFormatter
from sales_report.formatters.text_formatter import TextFormatter
from sales_report.interfaces.output_formatter import OutputFormatter


class FormatterFactory:
    """
    Factory responsável por criar instâncias de formatadores.

    Implementa o padrão Factory para desacoplar a criação
    de formatadores do código cliente.
    """

    _formatters: Dict[str, Type[OutputFormatter]] = {
        'text': TextFormatter,
        'json': JSONFormatter,
    }

    @classmethod
    def create_formatter(cls, format_type: str) -> OutputFormatter:
        """
        Cria uma instância do formatador especificado.

        Args:
            format_type (str): Tipo do formatador ('text' ou 'json').

        Returns:
            OutputFormatter: Instância do formatador solicitado.

        Raises:
            ValueError: Se o tipo de formatador não for suportado.
        """
        if format_type not in cls._formatters:
            available = ', '.join(cls._formatters.keys())
            raise ValueError(
                f'Formatador "{format_type}" não suportado. '
                f'Disponíveis: {available}'
            )

        return cls._formatters[format_type]()

    @classmethod
    def get_available_formats(cls) -> list[str]:
        """
        Retorna a lista de formatos disponíveis.

        Returns:
            list[str]: Lista com os nomes dos formatos suportados.
        """
        return list(cls._formatters.keys())
