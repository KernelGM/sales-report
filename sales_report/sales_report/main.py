from argparse import ArgumentParser
from collections import defaultdict
from csv import DictReader
from datetime import datetime
from json import dumps
from logging import INFO, basicConfig, getLogger
from typing import Dict, List, Optional

from tabulate import tabulate

basicConfig(level=INFO, format='%(levelname)s: %(message)s')
logger = getLogger(__name__)


class CSVReader:
    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path

    def read(self) -> List[Dict[str, str]]:
        try:
            with open(self.file_path, newline='', encoding='utf-8') as f:
                return list(DictReader(f))
        except UnicodeDecodeError:
            with open(self.file_path, newline='', encoding='cp1252') as f:
                return list(DictReader(f))
        except FileNotFoundError:
            logger.error(f'Arquivo não encontrado: {self.file_path}')
        except Exception as e:
            logger.error(f'Erro ao ler o CSV: {e}')
        return []


class App:
    def __init__(
        self,
        reader: CSVReader,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        output_format: str = 'text',
    ) -> None:
        self.reader: CSVReader = reader
        self.start_date: Optional[datetime] = start_date
        self.end_date: Optional[datetime] = end_date
        self.output_format: str = output_format

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        return datetime.strptime(date_str, '%Y-%m-%d')

    def _filter_by_date(
        self, rows: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        return [
            row
            for row in rows
            if (
                not self.start_date
                or self._parse_date(row['data_venda']) >= self.start_date
            )
            and (
                not self.end_date
                or self._parse_date(row['data_venda']) <= self.end_date
            )
        ]

    def run(self) -> None:
        rows: List[Dict[str, str]] = self.reader.read()
        if not rows:
            return

        if self.start_date or self.end_date:
            rows = self._filter_by_date(rows)

        sales_by_product: Dict[str, float] = defaultdict(float)
        quantity_by_product: Dict[str, int] = defaultdict(int)
        total_sales: float = 0.0

        for row in rows:
            product: str = row['produto']
            quantity: int = int(row['quantidade'])
            price: float = float(row['preco_unitario'])
            value: float = quantity * price

            sales_by_product[product] += value
            quantity_by_product[product] += quantity
            total_sales += value

        quantity_by_product_dict: Dict[str, int] = dict(quantity_by_product)
        top_product: str = max(
            quantity_by_product_dict.items(),
            key=lambda x: x[1],
            default=('', 0),
        )[0]

        data: Dict[str, object] = {
            'vendas_por_produto': dict(sales_by_product),
            'total_vendas': total_sales,
            'produto_mais_vendido': {
                'nome': top_product,
                'quantidade': quantity_by_product.get(top_product, 0),
            },
        }

        self._print(data)

    def _print(self, data: dict) -> None:
        if self.output_format == 'json':
            print(dumps(data, indent=2, ensure_ascii=False))
        else:
            print('Total de vendas por produto:')
            print(
                tabulate(
                    data['vendas_por_produto'].items(),
                    headers=['Produto', 'Total (R$)'],
                )
            )
            print(
                f'\nValor total de todas as vendas: '
                f'R$ {data["total_vendas"]:.2f}'
            )
            print(
                f'Produto mais vendido: {data["produto_mais_vendido"]["nome"]}'
                f'({data["produto_mais_vendido"]["quantidade"]} unidades)'
            )

    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[datetime]:
        return datetime.strptime(date_str, '%Y-%m-%d') if date_str else None


def main() -> None:
    parser = ArgumentParser(description='Relatório de vendas a partir de CSV')
    parser.add_argument('csv_file', help='Caminho do CSV')
    parser.add_argument('--start-date', help='Data inicial (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='Data final (YYYY-MM-DD)')
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Formato de saída',
    )
    args = parser.parse_args()

    start_date: Optional[datetime] = App.parse_date(args.start_date)
    end_date: Optional[datetime] = App.parse_date(args.end_date)

    reader = CSVReader(args.csv_file)
    app = App(
        reader,
        start_date=start_date,
        end_date=end_date,
        output_format=args.format,
    )
    app.run()


if __name__ == '__main__':  # pragma: no cover
    main()
