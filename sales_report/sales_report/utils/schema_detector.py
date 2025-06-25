"""
Utilitários para detecção automática de schema de dados.
"""

from logging import getLogger
from typing import Any, Dict, List, Optional, Set

logger = getLogger(__name__)


class SchemaDetector:
    """
    Classe responsável por detectar automaticamente o schema dos dados.

    Analisa os dados de entrada e determina quais colunas estão presentes
    e quais validações devem ser aplicadas.
    """

    # Colunas obrigatórias mínimas para dados de vendas
    REQUIRED_SALES_COLUMNS = {'produto', 'quantidade', 'preco_unitario'}

    # Colunas opcionais conhecidas
    OPTIONAL_COLUMNS = {'data_venda'}

    @classmethod
    def detect_schema(cls, data: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Detecta o schema dos dados baseado nas colunas presentes.

        Args:
            data (List[Dict[str, str]]): Lista de registros de dados.

        Returns:
            Dict[str, any]: Dicionário com informações do schema detectado:
                - available_columns: Set com colunas disponíveis
                - required_columns: List com colunas obrigatórias
                - has_date_column: Bool indicando se tem coluna de data
                - date_column: Nome da coluna de data (se existir)
        """
        if not data:
            logger.warning('Nenhum dado fornecido para detecção de schema')
            return cls._empty_schema()

        available_columns = set(data[0].keys()) if data else set()

        logger.info(
            f'Colunas detectadas: {", ".join(sorted(available_columns))}'
        )

        missing_required = cls.REQUIRED_SALES_COLUMNS - available_columns
        if missing_required:
            logger.warning(
                f'Colunas obrigatórias faltando: {", ".join(missing_required)}'
            )

        date_column = cls._detect_date_column(available_columns)
        has_date_column = date_column is not None

        required_columns = list(cls.REQUIRED_SALES_COLUMNS & available_columns)
        if has_date_column:
            required_columns.append(date_column)

        schema_info = {
            'available_columns': available_columns,
            'required_columns': required_columns,
            'has_date_column': has_date_column,
            'date_column': date_column,
            'is_valid_sales_data': len(missing_required) == 0,
        }

        logger.debug(f'Schema detectado: {schema_info}')
        return schema_info

    @classmethod
    def _detect_date_column(cls, columns: Set[str]) -> Optional[str]:
        """
        Detecta qual coluna contém dados de data.

        Args:
            columns (Set[str]): Set com nomes das colunas disponíveis.

        Returns:
            Optional[str]: Nome da coluna de data ou None se não encontrada.
        """
        date_column_candidates = {
            'data_venda',
            'data',
            'date',
            'data_pedido',
            'data_compra',
            'timestamp',
            'created_at',
        }

        for candidate in date_column_candidates:
            if candidate in columns:
                logger.info(f'Coluna de data detectada: {candidate}')
                return candidate

        for column in columns:
            if 'data' in column.lower() or 'date' in column.lower():
                logger.info(f'Possível coluna de data detectada: {column}')
                return column

        logger.info('Nenhuma coluna de data detectada')
        return None

    @classmethod
    def _empty_schema(cls) -> Dict[str, Any]:
        """
        Retorna um schema vazio.

        Returns:
            Dict[str, any]: Schema vazio.
        """
        return {
            'available_columns': set(),
            'required_columns': [],
            'has_date_column': False,
            'date_column': None,
            'is_valid_sales_data': False,
        }
