"""
Implementação do formatador de texto.
"""

from typing import Any, Dict

from tabulate import tabulate

from sales_report.interfaces.output_formatter import OutputFormatter


class TextFormatter(OutputFormatter):
    """
    Formatador que converte dados processados em texto legível.

    Responsável exclusivamente por formatar dados em formato
    de texto usando tabelas para melhor visualização.
    """

    @staticmethod
    def format(data: Dict[str, Any]) -> str:
        """
        Formata os dados processados em texto legível.

        Args:
            data (Dict[str, Any]): Dados processados de vendas.

        Returns:
            str: String formatada com as informações de vendas.
        """
        if not data.get('vendas_por_produto'):
            return 'Nenhum dado de vendas disponível para exibição.'

        lines = []

        lines.append('Total de vendas por produto:')
        table_data = list(data['vendas_por_produto'].items())
        table = tabulate(
            table_data, headers=['Produto', 'Total (R$)'], floatfmt='.2f'
        )
        lines.append(table)

        lines.append(
            f'\nValor total de todas as vendas: R$ {data["total_vendas"]:.2f}'
        )

        top_product = data['produto_mais_vendido']
        if top_product['nome']:
            lines.append(
                f'Produto mais vendido: {top_product["nome"]} '
                f'({top_product["quantidade"]} unidades)'
            )

        return '\n'.join(lines)
