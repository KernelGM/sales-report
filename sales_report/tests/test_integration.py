"""
Testes de integração para o sistema completo.
"""

import json
import os
import sys
import tempfile
from unittest.mock import patch

from sales_report.main import main


class TestIntegration:
    """Testes de integração do sistema completo."""

    @staticmethod
    def test_integration_csv_with_date(capsys):
        """Testa integração completa com CSV contendo data."""
        csv_content = """produto,quantidade,preco_unitario,data_venda
Camiseta,3,49.9,2025-06-01
Calça,2,99.9,2025-06-05
Tênis,1,199.9,2025-06-03"""

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False, encoding='utf-8'
        ) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            test_argv = ['program', csv_path]
            with patch.object(sys, 'argv', test_argv):
                main()

            captured = capsys.readouterr()
            assert 'Total de vendas por produto:' in captured.out
            assert 'Camiseta' in captured.out
            assert 'Calça' in captured.out
            assert 'Tênis' in captured.out
        finally:
            os.unlink(csv_path)

    @staticmethod
    def test_integration_csv_without_date(capsys):
        """Testa integração completa com CSV sem data."""
        csv_content = """produto,quantidade,preco_unitario
Camiseta,3,49.9
Calça,2,99.9
Tênis,1,199.9"""

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False, encoding='utf-8'
        ) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            test_argv = ['program', csv_path]
            with patch.object(sys, 'argv', test_argv):
                main()

            captured = capsys.readouterr()
            assert 'Total de vendas por produto:' in captured.out
            assert 'Camiseta' in captured.out
        finally:
            os.unlink(csv_path)

    @staticmethod
    def test_integration_with_date_filter(capsys):
        """Testa integração com filtro de data."""
        csv_content = """produto,quantidade,preco_unitario,data_venda
Camiseta,3,49.9,2025-06-01
Calça,2,99.9,2025-06-05
Tênis,1,199.9,2025-06-03"""

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False, encoding='utf-8'
        ) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            test_argv = [
                'program',
                csv_path,
                '--start-date',
                '2025-06-01',
                '--end-date',
                '2025-06-03',
            ]
            with patch.object(sys, 'argv', test_argv):
                main()

            captured = capsys.readouterr()
            assert 'Camiseta' in captured.out
            assert 'Tênis' in captured.out
            assert captured.out.count('Calça') == 0
        finally:
            os.unlink(csv_path)

    @staticmethod
    def test_integration_json_output(capsys):
        """Testa integração com saída JSON."""
        csv_content = """produto,quantidade,preco_unitario
Camiseta,3,49.9"""

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False, encoding='utf-8'
        ) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            test_argv = ['program', csv_path, '--format', 'json']
            with patch.object(sys, 'argv', test_argv):
                main()

            captured = capsys.readouterr()

            data = json.loads(captured.out)
            assert 'vendas_por_produto' in data
            assert 'Camiseta' in data['vendas_por_produto']
        finally:
            os.unlink(csv_path)
