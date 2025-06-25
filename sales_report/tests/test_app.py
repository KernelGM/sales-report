import json
import sys
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

from sales_report.main import App, CSVReader, main


def test_csvreader_read_success(mock_csv_data, parsed_rows):
    m = mock_open(read_data=mock_csv_data)
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


def test_csvreader_read_fallback_cp1252_logs_error(caplog):
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


def test_app_parse_date_invalid_format_logs_error(caplog):
    with caplog.at_level('ERROR'):
        result = App._parse_date('2024-13-99')
    assert result is None
    assert 'Data inválida' in caplog.text


def test_filter_by_date_logs_warning_on_invalid_date(
    rows_with_invalid_date, caplog
):
    reader = MagicMock()
    app = App(reader)

    with caplog.at_level('WARNING'):
        filtered = app._filter_by_date(rows_with_invalid_date)

    assert filtered == []
    assert 'Data ignorada por formato inválido' in caplog.text


def test_run_logs_keyerror_and_valueerror(invalid_rows, caplog):
    reader = MagicMock()
    reader.read.return_value = invalid_rows
    app = App(reader)

    with caplog.at_level('ERROR'):
        app.run()

    assert 'Coluna faltando' in caplog.text
    assert 'Erro na conversão de dados' in caplog.text


def test_run_logs_error_no_valid_sales(caplog):
    reader = MagicMock()
    reader.read.return_value = [
        {
            'produto': 'p1',
            'quantidade': 'abc',
            'preco_unitario': '10.0',
            'data_venda': '2024-01-01',
        }
    ]
    app = App(reader)

    with caplog.at_level('ERROR'):
        app.run()

    assert 'Nenhuma venda válida encontrada após processamento.' in caplog.text


def test_parse_date_static_method_logs_error_for_invalid_date(caplog):
    with caplog.at_level('ERROR'):
        result = App.parse_date('2024-02-30')
    assert result is None
    assert 'Data inválida no argumento' in caplog.text


def test_app_run_empty_rows(empty_rows, caplog):
    reader = MagicMock()
    reader.read.return_value = empty_rows
    app = App(reader)

    with caplog.at_level('ERROR'):
        result = app.run()

    assert result is None
    assert 'Nenhum dado disponível para processar.' in caplog.text


def test_app_run_normal_and_log_text(parsed_rows, capsys):
    reader = MagicMock()
    reader.read.return_value = parsed_rows
    app = App(reader)

    app.run()
    captured = capsys.readouterr()
    assert 'Total de vendas por produto:' in captured.out
    assert 'Camiseta' in captured.out


def test_app_run_with_date_filter(capsys):
    reader = MagicMock()
    reader.read.return_value = [
        {
            'produto': 'Camiseta',
            'quantidade': '3',
            'preco_unitario': '49.9',
            'data_venda': '2024-06-01',
        },
        {
            'produto': 'Calça',
            'quantidade': '2',
            'preco_unitario': '99.9',
            'data_venda': '2024-06-05',
        },
    ]
    app = App(
        reader,
        start_date=datetime(2024, 6, 1),
        end_date=datetime(2024, 6, 3),
    )

    app.run()
    captured = capsys.readouterr()
    assert 'Camiseta' in captured.out
    assert 'Calça' not in captured.out


def test_app_run_json_output(parsed_rows, capsys):
    reader = MagicMock()
    reader.read.return_value = parsed_rows
    app = App(reader, output_format='json')

    app.run()
    captured = capsys.readouterr()

    data = json.loads(captured.out)
    assert 'vendas_por_produto' in data
    assert 'total_vendas' in data
    assert 'produto_mais_vendido' in data


def test_main_function(mock_csv_data, parsed_rows, capsys):
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


def test_csvreader_read_fallback_cp1252_success(
    mock_csv_data, parsed_rows, caplog
):
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
        assert 'Read com fallback cp1252: file.csv' in caplog.text
