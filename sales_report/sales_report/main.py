from argparse import ArgumentParser
from csv import DictReader
from logging import INFO, basicConfig, error, info

basicConfig(level=INFO, format='%(levelname)s: %(message)s')

parser = ArgumentParser(
    description='Lê um arquivo CSV e exibe informações de vendas'
)
parser.add_argument('csv_file', help='Caminho para o arquivo CSV a ser lido')
args = parser.parse_args()

try:
    with open(args.csv_file, newline='', encoding='cp1252') as f:
        reader = DictReader(f)
        for row in reader:
            info(row)
except FileNotFoundError:
    error(f'Arquivo não encontrado: {args.csv_file}')
except Exception as e:
    error(f'Erro ao ler o CSV: {e}')
