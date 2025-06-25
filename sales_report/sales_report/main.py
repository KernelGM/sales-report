from argparse import ArgumentParser
from collections import defaultdict
from csv import DictReader
from logging import INFO, basicConfig, getLogger
from typing import Dict, List

basicConfig(level=INFO, format='%(levelname)s: %(message)s')
logger = getLogger(__name__)


class CSVReader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read(self) -> List[Dict[str, str]]:
        try:
            with open(self.file_path, newline='', encoding='cp1252') as f:
                return list(DictReader(f))
        except FileNotFoundError:
            logger.error(f'Arquivo não encontrado: {self.file_path}')
        except Exception as e:
            logger.error(f'Erro ao ler o CSV: {e}')
        return []


class CSVLogger:
    @staticmethod
    def log(rows: List[Dict[str, str]]) -> None:
        for row in rows:
            logger.info(row)


class App:
    def __init__(self, reader: CSVReader, logger_: CSVLogger):
        self.reader = reader
        self.logger = logger_

    def run(self) -> None:
        rows = self.reader.read()
        if not rows:
            return

        total_por_produto = defaultdict(float)
        total_vendas = 0.0
        quantidade_por_produto = defaultdict(int)

        for row in rows:
            produto = row['produto']
            quantidade = int(row['quantidade'])
            preco = float(row['preco_unitario'])
            valor = quantidade * preco

            total_por_produto[produto] += valor
            total_vendas += valor
            quantidade_por_produto[produto] += quantidade

        produto_mais_vendido = max(
            quantidade_por_produto,
            key=lambda produto: quantidade_por_produto[produto],
        )

        logger.info('Total de vendas por produto:')
        for produto, total in total_por_produto.items():
            logger.info(f'{produto}: R$ {total:.2f}')

        logger.info(f'Valor total de todas as vendas: R$ {total_vendas:.2f}')
        logger.info(
            f'Produto mais vendido: {produto_mais_vendido} '
            f'({quantidade_por_produto[produto_mais_vendido]} unidades)'
        )


def main():
    parser = ArgumentParser(
        description='Lê um arquivo CSV e exibe informações de vendas'
    )
    parser.add_argument(
        'csv_file', help='Caminho para o arquivo CSV a ser lido'
    )
    args = parser.parse_args()

    reader = CSVReader(args.csv_file)
    logger_ = CSVLogger()
    app = App(reader, logger_)
    app.run()


if __name__ == '__main__':  # pragma: no cover
    main()
