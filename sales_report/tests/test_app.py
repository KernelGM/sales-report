import sys
from unittest.mock import MagicMock, mock_open, patch

from sales_report.main import App, CSVLogger, CSVReader, main


def test_csvreader_read_success(csv_data, parsed_rows):
    m = mock_open(read_data=csv_data)
    with patch('builtins.open', m):
        reader = CSVReader('fake.csv')
        result = reader.read()
        assert result == parsed_rows


def test_csvreader_read_file_not_found(caplog):
    reader = CSVReader('nofile.csv')
    with caplog.at_level('ERROR'):
        result = reader.read()
    assert result == []
    assert 'Arquivo não encontrado' in caplog.text


def test_csvreader_read_other_exception(caplog):
    def raise_err(*args, **kwargs):
        raise RuntimeError('fail')

    with patch('builtins.open', raise_err):
        reader = CSVReader('fake.csv')
        with caplog.at_level('ERROR'):
            result = reader.read()
        assert result == []
        assert 'Erro ao ler o CSV' in caplog.text


def test_csvlogger_log_info(parsed_rows, caplog):
    logger = CSVLogger()
    with caplog.at_level('INFO'):
        logger.log(parsed_rows)
    for row in parsed_rows:
        assert str(row) in caplog.text


def test_app_run_calls_read_and_log(parsed_rows, caplog):
    reader = CSVReader('fake.csv')
    reader.read = MagicMock(return_value=parsed_rows)
    logger = CSVLogger()
    app = App(reader, logger)

    with caplog.at_level('INFO'):
        app.run()

    reader.read.assert_called_once()
    assert 'Total de vendas por produto:' in caplog.text


def test_main_function(csv_data, parsed_rows, caplog):
    m = mock_open(read_data=csv_data)
    test_argv = ['program', 'dummy.csv']

    with (
        patch('builtins.open', m),
        patch.object(sys, 'argv', test_argv),
        patch.object(CSVReader, 'read', return_value=parsed_rows),
    ):
        with caplog.at_level('INFO'):
            main()
        assert 'Total de vendas por produto:' in caplog.text
        assert 'Produto mais vendido' in caplog.text


def test_app_run_empty_rows(caplog):
    reader = CSVReader('fake.csv')
    reader.read = MagicMock(return_value=[])
    logger = CSVLogger()
    app = App(reader, logger)

    with caplog.at_level('INFO'):
        result = app.run()
    assert result is None
    assert not caplog.text


def test_app_run_with_sales_calculations(caplog, parsed_rows):
    reader = CSVReader('fake.csv')
    reader.read = MagicMock(return_value=parsed_rows)
    logger = CSVLogger()
    app = App(reader, logger)

    with caplog.at_level('INFO'):
        app.run()

    assert 'Total de vendas por produto:' in caplog.text
    assert 'Camiseta: R$ 199.60' in caplog.text
    assert 'Calça: R$ 199.80' in caplog.text
    assert 'Tênis: R$ 199.90' in caplog.text
    assert 'Valor total de todas as vendas: R$ 599.30' in caplog.text
    assert 'Produto mais vendido: Camiseta (4 unidades)' in caplog.text
