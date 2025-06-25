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


def test_csvreader_read_unicode_decode_error(mock_csv_data, parsed_rows):
    m = mock_open(read_data=mock_csv_data)

    def open_side_effect(*args, **kwargs):
        if kwargs.get('encoding') == 'utf-8':
            raise UnicodeDecodeError('utf-8', b'', 0, 1, 'reason')
        else:
            return m()

    with patch('builtins.open', side_effect=open_side_effect):
        reader = CSVReader('fake.csv')
        result = reader.read()
        assert result == parsed_rows


def test_app_run_empty_rows(caplog):
    reader = CSVReader('fake.csv')
    reader.read = MagicMock(return_value=[])
    app = App(reader)

    with caplog.at_level('INFO'):
        result = app.run()

    assert result is None
    assert not caplog.text


def test_app_run_normal_and_log_text(parsed_rows, capsys):
    reader = CSVReader('fake.csv')
    reader.read = MagicMock(return_value=parsed_rows)
    app = App(reader)

    app.run()
    captured = capsys.readouterr()
    assert 'Total de vendas por produto:' in captured.out
    assert 'Camiseta' in captured.out


def test_app_run_with_date_filter(capsys):
    reader = CSVReader('fake.csv')
    reader.read = MagicMock(
        return_value=[
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
    )
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
    reader = CSVReader('fake.csv')
    reader.read = MagicMock(return_value=parsed_rows)
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
