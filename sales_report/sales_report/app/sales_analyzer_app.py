"""
Classe principal da aplicação de análise de vendas.
"""

from logging import getLogger
from typing import List, Optional

from sales_report.interfaces.data_filter import DataFilter
from sales_report.interfaces.data_processor import DataProcessor
from sales_report.interfaces.data_reader import DataReader
from sales_report.interfaces.data_validator import DataValidator
from sales_report.interfaces.output_formatter import OutputFormatter
from sales_report.utils.schema_detector import SchemaDetector
from sales_report.validators.sales_validator import SalesDataValidator

logger = getLogger(__name__)


class SalesAnalyzerApp:
    """
    Classe principal da aplicação de análise de vendas.
    Orquestra o fluxo de leitura, validação, filtragem, processamento
    e formatação dos dados de vendas. Segue o princípio da inversão
    de dependência, dependendo apenas de abstrações.
    """

    def __init__(
        self,
        data_reader: DataReader,
        data_processor: DataProcessor,
        output_formatter: OutputFormatter,
        data_validator: Optional[DataValidator] = None,
        data_filters: Optional[List[DataFilter]] = None,
    ) -> None:
        """
        Inicializa a aplicação com suas dependências.

        Args:
            data_reader (DataReader): Leitor de dados.
            data_processor (DataProcessor): Processador de dados.
            output_formatter (OutputFormatter): Formatador de saída.
            data_validator (Optional[DataValidator]): Validador de dados.
            data_filters (Optional[List[DataFilter]]): Lista de filtros.
        """
        self.data_reader = data_reader
        self.data_processor = data_processor
        self.output_formatter = output_formatter
        self.data_validator = data_validator
        self.data_filters = data_filters or []

    def run(self) -> str:  # noqa: PLR0912
        """
        Executa o fluxo completo da aplicação.

        Returns:
            str: Resultado formatado da análise de vendas.
        """
        # 1. Ler dados
        logger.debug('Iniciando leitura dos dados')
        raw_data = self.data_reader.read()

        if not raw_data:
            logger.error('Nenhum dado foi lido')
            return 'Erro: Nenhum dado disponível para processar.'

        logger.debug(f'Lidos {len(raw_data)} registros')

        # 1.5. Detectar schema dos dados
        logger.debug('Detectando schema dos dados')
        schema_info = SchemaDetector.detect_schema(raw_data)

        if not schema_info['is_valid_sales_data']:
            logger.error('Dados não possuem estrutura válida para vendas')
            return (
                'Erro: Dados não possuem as colunas mínimas necessárias '
                '(produto, quantidade, preco_unitario).'
            )

        # 2. Validar dados (se validador fornecido)
        if self.data_validator:
            logger.debug('Validando dados')

            if not hasattr(self.data_validator, 'has_date_column'):
                self.data_validator = SalesDataValidator(
                    schema_info=schema_info
                )

            valid_data, errors = self.data_validator.validate(raw_data)

            if errors:
                for error in errors:
                    logger.warning(error)

            if not valid_data:
                logger.error('Nenhum dado válido encontrado')
                return 'Erro: Nenhum dado válido encontrado após validação.'

            logger.debug(
                f'{len(valid_data)} registros válidos de {
                    len(raw_data)
                } totais'
            )
            data = valid_data
        else:
            data = raw_data

        # 3. Aplicar filtros (apenas filtros de data que são aplicáveis)
        applicable_filters = []
        for data_filter in self.data_filters:
            if hasattr(data_filter, 'date_column'):
                if schema_info['has_date_column']:
                    if hasattr(data_filter, 'date_column'):
                        setattr(
                            data_filter,
                            'date_column',
                            schema_info['date_column'],
                        )
                    applicable_filters.append(data_filter)
                else:
                    logger.info(
                        'Filtro de data ignorado: dados não tem coluna de data'
                    )
            else:
                applicable_filters.append(data_filter)

        for data_filter in applicable_filters:
            logger.info(f'Aplicando filtro: {type(data_filter).__name__}')
            data = data_filter.filter(data)

        if not data:
            logger.warning('Nenhum dado restou após aplicação dos filtros')
            return 'Nenhum dado encontrado após aplicação dos filtros.'

        logger.debug(f'{len(data)} registros após filtragem')

        # 4. Processar dados
        logger.info('Processando dados')
        processed_data = self.data_processor.process(data)

        # 5. Formatar saída
        logger.info('Formatando resultado')
        result = self.output_formatter.format(processed_data)

        logger.info('Processamento concluído com sucesso \n')
        return result
