"""
Ponto de entrada principal da aplicação de análise de vendas.
"""

from argparse import ArgumentParser
from logging import INFO, basicConfig, getLogger

from sales_report.app.sales_analyzer_app import SalesAnalyzerApp
from sales_report.factories.formatter_factory import FormatterFactory
from sales_report.filters.date_filter import DateFilter
from sales_report.processors.sales_processor import SalesDataProcessor
from sales_report.readers.csv_reader import CSVReader
from sales_report.utils.date_utils import DateUtils
from sales_report.validators.sales_validator import SalesDataValidator

basicConfig(level=INFO, format='%(levelname)s: %(message)s')
logger = getLogger(__name__)


def main() -> None:
    """
    Função principal que configura e executa a aplicação.

    Configura o parser de argumentos da linha de comando, cria as
    instâncias necessárias seguindo o padrão de injeção de dependência
    e executa a aplicação.
    """
    parser = ArgumentParser(description='Relatório de vendas a partir de CSV')
    parser.add_argument('csv_file', help='Caminho do arquivo CSV')
    parser.add_argument('--start-date', help='Data inicial (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='Data final (YYYY-MM-DD)')
    parser.add_argument(
        '--format',
        choices=FormatterFactory.get_available_formats(),
        default='text',
        help='Formato de saída',
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Pular validação de dados',
    )

    args = parser.parse_args()

    try:
        # Criar dependências
        data_reader = CSVReader(args.csv_file)
        data_processor = SalesDataProcessor()
        output_formatter = FormatterFactory.create_formatter(args.format)

        # Criar validador (será reconfigurado automaticamente pela app)
        data_validator = None if args.skip_validation else SalesDataValidator()

        # Criar filtros
        data_filters = []
        start_date = DateUtils.parse_date(args.start_date)
        end_date = DateUtils.parse_date(args.end_date)

        if start_date or end_date:
            # Criar filtro de data (a coluna será detectada automaticamente)
            date_filter = DateFilter(start_date, end_date)
            data_filters.append(date_filter)

        # Criar e executar aplicação
        app = SalesAnalyzerApp(
            data_reader=data_reader,
            data_processor=data_processor,
            output_formatter=output_formatter,
            data_validator=data_validator,
            data_filters=data_filters,
        )

        result = app.run()
        print(result)

    except Exception as e:
        logger.error(f'Erro na execução da aplicação: {e}')
        return


if __name__ == '__main__':  # pragma: no cover
    main()
