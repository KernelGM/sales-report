import json
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from sales_report.app.sales_analyzer_app import SalesAnalyzerApp
from sales_report.factories.formatter_factory import FormatterFactory
from sales_report.filters.date_filter import DateFilter
from sales_report.formatters.json_formatter import JSONFormatter
from sales_report.formatters.text_formatter import TextFormatter
from sales_report.main import main
from sales_report.processors.sales_processor import SalesDataProcessor
from sales_report.readers.csv_reader import CSVReader
from sales_report.utils.date_utils import DateUtils
from sales_report.utils.schema_detector import SchemaDetector
from sales_report.validators.sales_validator import (
    DataValidator,
    SalesDataValidator,
)

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestCSVReader:
    """Testes para a classe CSVReader."""

    @staticmethod
    def test_read_success(mock_csv_data, parsed_rows):
        """Testa leitura bem-sucedida de CSV."""
        m = mock_open(read_data=mock_csv_data)
        with patch('builtins.open', m):
            reader = CSVReader('fake.csv')
            result = reader.read()
            assert result == parsed_rows

    @staticmethod
    def test_read_file_not_found(caplog):
        """Testa comportamento quando arquivo não é encontrado."""
        reader = CSVReader('nofile.csv')
        with caplog.at_level('ERROR'):
            result = reader.read()
        assert result == []
        assert 'Arquivo não encontrado' in caplog.text

    @staticmethod
    def test_read_other_exception(caplog):
        """Testa tratamento de outras exceções."""

        def raise_err(*args, **kwargs):
            raise RuntimeError('fail')

        with patch('builtins.open', raise_err):
            reader = CSVReader('fake.csv')
            with caplog.at_level('ERROR'):
                result = reader.read()
            assert result == []
            assert 'Erro ao ler o CSV' in caplog.text

    @staticmethod
    def test_read_fallback_cp1252_success(mock_csv_data, parsed_rows, caplog):
        """Testa fallback bem-sucedido para CP1252."""
        m = mock_open(read_data=mock_csv_data)

        def open_side_effect(*args, **kwargs):
            if kwargs.get('encoding') == 'utf-8':
                raise UnicodeDecodeError('utf-8', b'', 0, 1, 'reason')
            else:
                return m()

        with patch('builtins.open', side_effect=open_side_effect):
            reader = CSVReader('file.csv')
            with caplog.at_level('INFO'):
                result = reader.read()

            assert result == parsed_rows

    @staticmethod
    def test_read_fallback_cp1252_logs_error(caplog):
        """Testa log de erro quando fallback CP1252 falha."""

        def open_side_effect(*args, **kwargs):
            if kwargs.get('encoding') == 'utf-8':
                raise UnicodeDecodeError('utf-8', b'', 0, 1, 'reason')
            else:
                raise RuntimeError('fail cp1252')

        with patch('builtins.open', side_effect=open_side_effect):
            reader = CSVReader('file.csv')
            with caplog.at_level('ERROR'):
                result = reader.read()

            assert result == []
            assert 'Erro ao ler CSV com fallback cp1252' in caplog.text


class TestSchemaDetector:
    """Testes para o detector de schema."""

    @staticmethod
    def test_detect_schema_with_date(parsed_rows):
        """Testa detecção de schema com coluna de data."""
        schema = SchemaDetector.detect_schema(parsed_rows)

        assert schema['has_date_column'] is True
        assert schema['date_column'] == 'data_venda'
        assert schema['is_valid_sales_data'] is True
        assert 'produto' in schema['available_columns']
        assert 'quantidade' in schema['available_columns']
        assert 'preco_unitario' in schema['available_columns']

    @staticmethod
    def test_detect_schema_no_date(parsed_rows_no_date):
        """Testa detecção de schema sem coluna de data."""
        schema = SchemaDetector.detect_schema(parsed_rows_no_date)

        assert schema['has_date_column'] is False
        assert schema['date_column'] is None
        assert schema['is_valid_sales_data'] is True
        assert 'produto' in schema['available_columns']

    @staticmethod
    def test_detect_schema_empty_data():
        """Testa detecção com dados vazios."""
        schema = SchemaDetector.detect_schema([])

        assert schema['has_date_column'] is False
        assert schema['is_valid_sales_data'] is False
        assert len(schema['available_columns']) == 0

    @staticmethod
    def test_detect_schema_invalid_sales_data():
        """Testa detecção com dados inválidos para vendas."""
        invalid_data = [{'nome': 'João', 'idade': '30'}]
        schema = SchemaDetector.detect_schema(invalid_data)

        assert schema['is_valid_sales_data'] is False

    @staticmethod
    def test_detect_date_column_with_partial_name():
        """Testa detecção de coluna de data por substring no nome."""
        columns = {
            'produto',
            'quantidade',
            'preco_unitario',
            'data_venda_errada',
        }
        detected = SchemaDetector._detect_date_column(columns)
        assert detected == 'data_venda_errada'

    @staticmethod
    def test_detect_schema_with_partial_date_column():
        """Testa detecção de schema com coluna de data contendo substring."""
        data = [
            {
                'produto': 'A',
                'quantidade': '1',
                'preco_unitario': '10.0',
                'data_venda_errada': '2025-06-01',
            }
        ]
        schema = SchemaDetector.detect_schema(data)
        assert schema['has_date_column'] is True
        assert schema['date_column'] == 'data_venda_errada'


class TestSalesDataValidator:
    """Testes para o validador de dados de vendas."""

    @staticmethod
    def test_validate_price_and_quantity_zero(sample_schema_no_date):
        """Testa quantidade <= 0, preço <= 0 e preço inválido."""
        validator = SalesDataValidator(schema_info=sample_schema_no_date)
        data = [
            {
                'produto': 'A',
                'quantidade': '0',  # quantidade inválida
                'preco_unitario': '0',  # preço inválido
            },
            {
                'produto': 'B',
                'quantidade': '2',
                'preco_unitario': 'abc',  # formato inválido de preço
            },
        ]

        valid_data, errors = validator.validate(data)

        assert len(valid_data) == 0
        assert any('Quantidade deve ser maior que zero' in e for e in errors)
        assert any('Preço deve ser maior que zero' in e for e in errors)
        assert any('Preço deve ser um número válido' in e for e in errors)

    @staticmethod
    def test_validate_with_schema_info(parsed_rows, sample_schema_with_date):
        """Testa validação com informações de schema."""
        validator = SalesDataValidator(schema_info=sample_schema_with_date)
        valid_data, errors = validator.validate(parsed_rows)

        value_expected = 2
        assert len(valid_data) == value_expected
        assert len(errors) == 0

    @staticmethod
    def test_validate_invalid_rows(
        invalid_rows, sample_schema_with_date, caplog
    ):
        """Testa validação com dados inválidos."""
        validator = SalesDataValidator(schema_info=sample_schema_with_date)
        valid_data, errors = validator.validate(invalid_rows)

        assert len(valid_data) == 0
        assert len(errors) > 0
        assert any(
            'produto' in error.lower() and 'faltando' in error.lower()
            for error in errors
        )

    @staticmethod
    def test_validate_no_date_column(
        parsed_rows_no_date, sample_schema_no_date
    ):
        """Testa validação sem coluna de data."""
        validator = SalesDataValidator(schema_info=sample_schema_no_date)
        valid_data, errors = validator.validate(parsed_rows_no_date)

        value_expected = 2
        assert len(valid_data) == value_expected
        assert len(errors) == 0

    @staticmethod
    def test_validate_invalid_date_format(
        rows_with_invalid_date, sample_schema_with_date
    ):
        """Testa validação com formato de data inválido."""
        validator = SalesDataValidator(schema_info=sample_schema_with_date)
        valid_data, errors = validator.validate(rows_with_invalid_date)

        assert len(valid_data) == 0
        assert any('formato inválido' in error for error in errors)


class TestDateFilter:
    """Testes para o filtro de data."""

    @staticmethod
    def test_filter_with_date_range(parsed_rows):
        """Testa filtro com intervalo de datas."""
        start_date = datetime(2025, 6, 1)
        end_date = datetime(2025, 6, 3)
        date_filter = DateFilter(start_date, end_date)

        filtered_data = date_filter.filter(parsed_rows)

        assert len(filtered_data) == 1
        assert filtered_data[0]['produto'] == 'Camiseta'

    @staticmethod
    def test_filter_no_date_column(parsed_rows_no_date, caplog):
        """Testa filtro quando não há coluna de data."""
        start_date = datetime(2025, 6, 1)
        date_filter = DateFilter(start_date)

        with caplog.at_level('WARNING'):
            filtered_data = date_filter.filter(parsed_rows_no_date)

        assert len(filtered_data) == len(parsed_rows_no_date)
        assert 'não encontrada nos dados' in caplog.text

    @staticmethod
    def test_filter_invalid_date_format(rows_with_invalid_date, caplog):
        """Testa filtro com formato de data inválido."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        date_filter = DateFilter(start_date, end_date)

        with caplog.at_level('WARNING'):
            filtered_data = date_filter.filter(rows_with_invalid_date)

        assert len(filtered_data) == 0
        assert 'Data ignorada por formato inválido' in caplog.text

    @staticmethod
    def test_filter_no_dates_specified(parsed_rows):
        """Testa filtro quando nenhuma data é especificada."""
        date_filter = DateFilter()

        filtered_data = date_filter.filter(parsed_rows)

        assert len(filtered_data) == len(parsed_rows)

    @staticmethod
    def test_filter_empty_date_in_row():
        """Testa filtro com linha que tem data vazia."""
        data_with_empty_date = [
            {
                'produto': 'Produto1',
                'quantidade': '1',
                'preco_unitario': '10.0',
                'data_venda': '',  # Data vazia
            }
        ]

        start_date = datetime(2024, 1, 1)
        date_filter = DateFilter(start_date)

        filtered_data = date_filter.filter(data_with_empty_date)

        assert len(filtered_data) == 1

    @staticmethod
    def test_filter_date_before_start(parsed_rows):
        """Testa filtro onde a data está antes da start_date (deve excluir)."""
        start_date = datetime(2025, 6, 6)  # agora sim > 2025-06-05
        date_filter = DateFilter(start_date=start_date)

        filtered_data = date_filter.filter(parsed_rows)

        assert len(filtered_data) == 0


class TestSalesDataProcessor:
    """Testes para o processador de dados de vendas."""

    @staticmethod
    def test_process_valid_data(parsed_rows):
        """Testa processamento de dados válidos."""
        processor = SalesDataProcessor()
        result = processor.process(parsed_rows)

        assert 'vendas_por_produto' in result
        assert 'total_vendas' in result
        assert 'produto_mais_vendido' in result
        assert result['total_vendas'] > 0

    @staticmethod
    def test_process_empty_data():
        """Testa processamento de dados vazios."""
        processor = SalesDataProcessor()
        result = processor.process([])

        assert result['total_vendas'] == 0.0
        assert result['vendas_por_produto'] == {}

    @staticmethod
    def test_process_invalid_data(caplog):
        """Testa processamento com dados inválidos."""
        invalid_data = [
            {'produto': 'test', 'quantidade': 'abc', 'preco_unitario': '10'}
        ]
        processor = SalesDataProcessor()

        with caplog.at_level('ERROR'):
            result = processor.process(invalid_data)

        assert result['total_vendas'] == 0.0
        assert 'Erro ao processar linha' in caplog.text


class TestFormatters:
    """Testes para os formatadores."""

    @staticmethod
    def test_create_formatter_invalid_type():
        """Testa criação de formatador com tipo inválido."""
        invalid_type = 'xml'

        with pytest.raises(
            ValueError, match=r'Formatador "xml" não suportado'
        ):
            FormatterFactory.create_formatter(invalid_type)

    @staticmethod
    def test_text_formatter():
        """Testa formatador de texto."""
        data = {
            'vendas_por_produto': {'Camiseta': 149.7, 'Calça': 199.8},
            'total_vendas': 349.5,
            'produto_mais_vendido': {'nome': 'Camiseta', 'quantidade': 3},
        }

        formatter = TextFormatter()
        result = formatter.format(data)

        assert 'Total de vendas por produto:' in result
        assert 'Camiseta' in result
        assert 'R$ 349.50' in result

    @staticmethod
    def test_json_formatter():
        """Testa formatador JSON."""
        data = {
            'vendas_por_produto': {'Camiseta': 149.7},
            'total_vendas': 149.7,
            'produto_mais_vendido': {'nome': 'Camiseta', 'quantidade': 3},
        }

        formatter = JSONFormatter()
        result = formatter.format(data)

        parsed_result = json.loads(result)
        value_expected = 149.7
        assert parsed_result['total_vendas'] == value_expected
        assert 'Camiseta' in parsed_result['vendas_por_produto']

    @staticmethod
    def test_text_formatter_empty_data():
        """Testa formatador de texto com dados vazios."""
        data = {'vendas_por_produto': {}}
        formatter = TextFormatter()
        result = formatter.format(data)

        assert 'Nenhum dado de vendas disponível' in result


class TestDateUtils:
    """Testes para utilitários de data."""

    @staticmethod
    def test_parse_date_valid():
        """Testa parsing de data válida."""
        result = DateUtils.parse_date('2025-06-01')
        assert result == datetime(2025, 6, 1)

    @staticmethod
    def test_parse_date_invalid(caplog):
        """Testa parsing de data inválida."""
        with caplog.at_level('ERROR'):
            result = DateUtils.parse_date('2025-13-99')

        assert result is None
        assert 'Data inválida' in caplog.text

    @staticmethod
    def test_parse_date_none():
        """Testa parsing com valor None."""
        result = DateUtils.parse_date(None)
        assert result is None

    @staticmethod
    def test_date_filter_ignored_log(parsed_rows, caplog):
        mock_reader = MagicMock()
        mock_reader.read.return_value = parsed_rows

        date_filter = DateFilter()

        app = SalesAnalyzerApp(
            data_reader=mock_reader,
            data_processor=MagicMock(),
            output_formatter=MagicMock(),
            data_filters=[date_filter],
        )

        with (
            patch(
                'sales_report.utils.schema_detector.SchemaDetector.detect_schema',
                return_value={
                    'is_valid_sales_data': True,
                    'has_date_column': False,
                    'date_column': None,
                },
            ),
            caplog.at_level('INFO'),
        ):
            app.run()

        assert any('Filtro de data ignorado' in m for m in caplog.messages)


class TestSalesAnalyzerApp:
    """Testes para a aplicação principal."""

    @staticmethod
    def test_run_success(parsed_rows, capsys):
        """Testa execução bem-sucedida da aplicação."""
        mock_reader = MagicMock()
        mock_reader.read.return_value = parsed_rows

        processor = SalesDataProcessor()
        formatter = TextFormatter()
        validator = SalesDataValidator()

        app = SalesAnalyzerApp(
            data_reader=mock_reader,
            data_processor=processor,
            output_formatter=formatter,
            data_validator=validator,
        )

        result = app.run()

        assert 'Total de vendas por produto:' in result
        assert 'Camiseta' in result

    @staticmethod
    def test_run_no_data(caplog):
        """Testa execução sem dados."""
        mock_reader = MagicMock()
        mock_reader.read.return_value = []

        processor = SalesDataProcessor()
        formatter = TextFormatter()

        app = SalesAnalyzerApp(
            data_reader=mock_reader,
            data_processor=processor,
            output_formatter=formatter,
        )

        result = app.run()

        assert 'Nenhum dado disponível para processar' in result

    @staticmethod
    def test_run_invalid_schema():
        """Testa execução com schema inválido."""
        invalid_data = [{'nome': 'João', 'idade': '30'}]

        mock_reader = MagicMock()
        mock_reader.read.return_value = invalid_data

        processor = SalesDataProcessor()
        formatter = TextFormatter()

        app = SalesAnalyzerApp(
            data_reader=mock_reader,
            data_processor=processor,
            output_formatter=formatter,
        )

        result = app.run()

        assert 'colunas mínimas necessárias' in result

    @staticmethod
    def test_run_with_date_filter(parsed_rows):
        """Testa execução com filtro de data."""
        mock_reader = MagicMock()
        mock_reader.read.return_value = parsed_rows

        processor = SalesDataProcessor()
        formatter = TextFormatter()

        start_date = datetime(2025, 6, 1)
        end_date = datetime(2025, 6, 3)
        date_filter = DateFilter(start_date, end_date)

        app = SalesAnalyzerApp(
            data_reader=mock_reader,
            data_processor=processor,
            output_formatter=formatter,
            data_filters=[date_filter],
        )

        result = app.run()

        assert 'Camiseta' in result

    @staticmethod
    def test_run_json_output(parsed_rows):
        """Testa execução com saída JSON."""
        mock_reader = MagicMock()
        mock_reader.read.return_value = parsed_rows

        processor = SalesDataProcessor()
        formatter = JSONFormatter()

        app = SalesAnalyzerApp(
            data_reader=mock_reader,
            data_processor=processor,
            output_formatter=formatter,
        )

        result = app.run()

        data = json.loads(result)
        assert 'vendas_por_produto' in data
        assert 'total_vendas' in data

    @staticmethod
    def test_run_with_invalid_data_and_custom_validator():
        """Testa execução com validador customizado sem has_date_column."""
        mock_reader = MagicMock()
        mock_reader.read.return_value = [
            {
                'produto': 'Camiseta',
                'quantidade': 'abc',
                'preco_unitario': '10',
            }
        ]

        class DummyValidator(DataValidator):
            @staticmethod
            def validate(data):
                return [], ['Erro: quantidade inválida']

        processor = SalesDataProcessor()
        formatter = TextFormatter()
        validator = DummyValidator()

        app = SalesAnalyzerApp(
            data_reader=mock_reader,
            data_processor=processor,
            output_formatter=formatter,
            data_validator=validator,
        )

        result = app.run()
        assert 'Erro: Nenhum dado válido encontrado após validação.' in result

    @staticmethod
    def test_run_with_non_date_filter(parsed_rows):
        """Testa execução com filtro que não depende de coluna de data."""
        mock_reader = MagicMock()
        mock_reader.read.return_value = parsed_rows

        class DummyFilter:
            @staticmethod
            def filter(data):
                return data

        processor = SalesDataProcessor()
        formatter = TextFormatter()

        app = SalesAnalyzerApp(
            data_reader=mock_reader,
            data_processor=processor,
            output_formatter=formatter,
            data_filters=[DummyFilter()],  # type: ignore
        )

        result = app.run()
        assert 'Total de vendas por produto:' in result

    @staticmethod
    def test_run_filters_result_empty(parsed_rows):
        """Testa execução onde filtros removem todos os dados."""
        mock_reader = MagicMock()
        mock_reader.read.return_value = parsed_rows

        class AlwaysExcludeFilter:
            date_column = 'data_venda'

            @staticmethod
            def filter(data):
                return []

        processor = SalesDataProcessor()
        formatter = TextFormatter()

        app = SalesAnalyzerApp(
            data_reader=mock_reader,
            data_processor=processor,
            output_formatter=formatter,
            data_filters=[AlwaysExcludeFilter()],  # type: ignore
        )

        result = app.run()
        assert 'Nenhum dado encontrado após aplicação dos filtros.' in result


class TestMainFunction:
    """Testes para a função main."""

    @staticmethod
    def test_main_function(mock_csv_data, parsed_rows, capsys):
        """Testa função main."""
        m = mock_open(read_data=mock_csv_data)
        test_argv = ['program', 'dummy.csv']

        with (
            patch('builtins.open', m),
            patch.object(sys, 'argv', test_argv),
            patch.object(CSVReader, 'read', return_value=parsed_rows),
        ):
            main()
            captured = capsys.readouterr()

            assert 'Total de vendas por produto:' in captured.out
            assert 'Produto mais vendido' in captured.out

    @staticmethod
    def test_main_with_date_filter(mock_csv_data, parsed_rows, capsys):
        """Testa função main com filtro de data."""
        m = mock_open(read_data=mock_csv_data)
        test_argv = [
            'program',
            'dummy.csv',
            '--start-date',
            '2025-06-01',
            '--end-date',
            '2025-06-03',
        ]

        with (
            patch('builtins.open', m),
            patch.object(sys, 'argv', test_argv),
            patch.object(CSVReader, 'read', return_value=parsed_rows),
        ):
            main()
            captured = capsys.readouterr()

            assert 'Total de vendas por produto:' in captured.out

    @staticmethod
    def test_main_json_format(mock_csv_data, parsed_rows, capsys):
        """Testa função main com formato JSON."""
        m = mock_open(read_data=mock_csv_data)
        test_argv = ['program', 'dummy.csv', '--format', 'json']

        with (
            patch('builtins.open', m),
            patch.object(sys, 'argv', test_argv),
            patch.object(CSVReader, 'read', return_value=parsed_rows),
        ):
            main()
            captured = capsys.readouterr()

            data = json.loads(captured.out)
            assert 'vendas_por_produto' in data

    @staticmethod
    def test_main_handles_exception(caplog):
        """Testa tratamento de exceção no main."""
        test_argv = ['program', 'dummy.csv']

        with (
            patch.object(sys, 'argv', test_argv),
            patch.object(
                CSVReader, '__init__', side_effect=Exception('Erro simulado')
            ),
            caplog.at_level('ERROR', logger='sales_report.__main__'),
        ):
            main()

        assert any(
            'Erro na execução da aplicação: Erro simulado' in msg
            for msg in caplog.messages
        )
