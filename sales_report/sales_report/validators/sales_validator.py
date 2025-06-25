"""
Implementação de validadores para dados de vendas.
"""

from datetime import datetime
from logging import getLogger
from typing import Dict, List, Optional, Tuple

from sales_report.interfaces.data_validator import DataValidator

logger = getLogger(__name__)


class SalesDataValidator(DataValidator):
    """
    Validador específico para dados de vendas.

    Responsável por validar se os dados de vendas possuem
    todas as colunas necessárias e valores válidos.
    Agora é flexível para diferentes estruturas de CSV.
    """

    def __init__(
        self,
        required_columns: Optional[List[str]] = None,
        schema_info: Optional[Dict] = None,
    ) -> None:
        """
        Inicializa o validador com as colunas obrigatórias.

        Args:
            required_columns (Optional[List[str]]): Lista de col obrigatórias.
                Se None, usa as colunas padrão para vendas.
            schema_info (Optional[Dict]): Informações do schema detectado.
        """
        if schema_info:
            self.required_columns = schema_info.get('required_columns', [])
            self.has_date_column = schema_info.get('has_date_column', False)
            self.date_column = schema_info.get('date_column')
        else:
            self.required_columns = required_columns or [
                'produto',
                'quantidade',
                'preco_unitario',
            ]
            self.has_date_column = False
            self.date_column = None

    def validate(
        self, data: List[Dict[str, str]]
    ) -> Tuple[List[Dict[str, str]], List[str]]:
        """
        Valida os dados de vendas.

        Args:
            data (List[Dict[str, str]]): Lista de registros a serem validados.

        Returns:
            Tuple[List[Dict[str, str]], List[str]]: Tupla contendo
                lista de registros válidos e lista de mensagens de erro.
        """
        valid_data: List[Dict[str, str]] = []
        errors: List[str] = []

        for idx, row in enumerate(data, start=1):
            row_errors = self._validate_row(row, idx)

            if row_errors:
                errors.extend(row_errors)
            else:
                valid_data.append(row)

        return valid_data, errors

    def _validate_row(self, row: Dict[str, str], row_number: int) -> List[str]:
        """
        Valida uma linha individual dos dados.

        Args:
            row (Dict[str, str]): Linha de dados a ser validada.
            row_number (int): Número da linha para referência em erros.

        Returns:
            List[str]: Lista de mensagens de erro para esta linha.
        """
        errors: List[str] = []

        for column in self.required_columns:
            if column not in row or not row[column].strip():
                errors.append(
                    f'Linha {row_number}: Coluna "{column}" '
                    ' está faltando ou vazia'
                )

        if 'quantidade' in row and row['quantidade'].strip():
            try:
                quantidade = int(row['quantidade'])
                if quantidade <= 0:
                    errors.append(
                        f'Linha {row_number}: '
                        'Quantidade deve ser maior que zero'
                    )
            except ValueError:
                errors.append(
                    f'Linha {row_number}: '
                    'Quantidade deve ser um número inteiro'
                )

        if 'preco_unitario' in row and row['preco_unitario'].strip():
            try:
                preco = float(row['preco_unitario'])
                if preco <= 0:
                    errors.append(
                        f'Linha {row_number}: Preço deve ser maior que zero'
                    )
            except ValueError:
                errors.append(
                    f'Linha {row_number}: Preço deve ser um número válido'
                )

        # Validar data apenas se a coluna existir
        if self.has_date_column and self.date_column in row:
            date_str = row[self.date_column].strip()
            if date_str and not self._is_valid_date_format(date_str):
                errors.append(
                    f'Linha {row_number}: Data "{date_str}" '
                    f'em formato inválido. Esperado YYYY-MM-DD'
                )

        return errors

    @staticmethod
    def _is_valid_date_format(date_str: str) -> bool:
        """
        Verifica se a string de data está em formato válido.

        Args:
            date_str (str): String da data a ser validada.

        Returns:
            bool: True se a data estiver em formato válido.
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
