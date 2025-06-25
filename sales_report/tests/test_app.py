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


def test_app_run_calls_read_and_log(parsed_rows):
    reader = CSVReader('fake.csv')
    reader.read = MagicMock(return_value=parsed_rows)
    logger = CSVLogger()
    logger.log = MagicMock()
    app = App(reader, logger)
    app.run()
    reader.read.assert_called_once()
    logger.log.assert_called_once_with(parsed_rows)


def test_main_function(csv_data, parsed_rows):
    m = mock_open(read_data=csv_data)
    test_argv = ['program', 'dummy.csv']

    with (
        patch('builtins.open', m),
        patch.object(sys, 'argv', test_argv),
        patch.object(CSVReader, 'read', return_value=parsed_rows) as mock_read,
        patch.object(CSVLogger, 'log') as mock_log,
    ):
        main()
        mock_read.assert_called_once()
        mock_log.assert_called_once_with(parsed_rows)
