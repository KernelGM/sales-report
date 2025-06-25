"""
Implementação do processador de dados de vendas.
"""

from collections import defaultdict
from logging import getLogger
from typing import Any, Dict, List

from sales_report.interfaces.data_processor import DataProcessor

logger = getLogger(__name__)


class SalesDataProcessor(DataProcessor):
    """
    Processador específico para dados de vendas.

    Responsável exclusivamente por processar dados de vendas
    e calcular estatísticas relevantes.
    """

    def process(self, data: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Processa os dados de vendas e calcula estatísticas.

        Args:
            data (List[Dict[str, str]]): Lista de registros de vendas válidos.

        Returns:
            Dict[str, Any]: Dicionário com estatísticas de vendas incluindo:
                - vendas_por_produto: Total de vendas por produto
                - total_vendas: Valor total de todas as vendas
                - produto_mais_vendido: Produto com maior quantidade vendida
        """
        if not data:
            logger.warning('Nenhum dado fornecido para processamento')
            return self._empty_result()

        sales_by_product: Dict[str, float] = defaultdict(float)
        quantity_by_product: Dict[str, int] = defaultdict(int)
        total_sales: float = 0.0

        for row in data:
            try:
                product = row['produto']
                quantity = int(row['quantidade'])
                price = float(row['preco_unitario'])

                value = quantity * price
                sales_by_product[product] += value
                quantity_by_product[product] += quantity
                total_sales += value

            except (KeyError, ValueError) as e:
                logger.error(f'Erro ao processar linha: {e}')
                continue

        if not quantity_by_product:
            logger.warning(
                'Nenhuma venda válida encontrada após processamento'
            )
            return self._empty_result()

        top_product = max(
            quantity_by_product.items(), key=lambda x: x[1], default=('', 0)
        )[0]

        return {
            'vendas_por_produto': dict(sales_by_product),
            'total_vendas': total_sales,
            'produto_mais_vendido': {
                'nome': top_product,
                'quantidade': quantity_by_product.get(top_product, 0),
            },
        }

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        """
        Retorna um resultado vazio quando não há dados para processar.

        Returns:
            Dict[str, Any]: Estrutura de resultado vazia.
        """
        return {
            'vendas_por_produto': {},
            'total_vendas': 0.0,
            'produto_mais_vendido': {
                'nome': '',
                'quantidade': 0,
            },
        }
