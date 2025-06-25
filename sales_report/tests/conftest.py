import pytest


@pytest.fixture
def mock_csv_data():
    return (
        'produto,quantidade,preco_unitario,data_venda\n'
        'Camiseta,3,49.9,2025-06-01\n'
        'Calça,2,99.9,2025-06-05\n'
    )


@pytest.fixture
def mock_csv_data_no_date():
    """CSV sem coluna de data."""
    return 'produto,quantidade,preco_unitario\nCamiseta,3,49.9\nCalça,2,99.9\n'


@pytest.fixture
def parsed_rows():
    return [
        {
            'produto': 'Camiseta',
            'quantidade': '3',
            'preco_unitario': '49.9',
            'data_venda': '2025-06-01',
        },
        {
            'produto': 'Calça',
            'quantidade': '2',
            'preco_unitario': '99.9',
            'data_venda': '2025-06-05',
        },
    ]


@pytest.fixture
def parsed_rows_no_date():
    """Dados sem coluna de data."""
    return [
        {
            'produto': 'Camiseta',
            'quantidade': '3',
            'preco_unitario': '49.9',
        },
        {
            'produto': 'Calça',
            'quantidade': '2',
            'preco_unitario': '99.9',
        },
    ]


@pytest.fixture
def invalid_rows():
    return [
        {
            'quantidade': '1',
            'preco_unitario': '10.0',
            'data_venda': '2024-01-01',
        },  # falta 'produto'
        {
            'produto': 'p2',
            'quantidade': 'NaN',
            'preco_unitario': '10.0',
            'data_venda': '2024-01-01',
        },  # quantidade inválida
    ]


@pytest.fixture
def rows_with_invalid_date():
    return [
        {
            'produto': 'p1',
            'quantidade': '1',
            'preco_unitario': '10.0',
            'data_venda': 'invalid-date',
        },
    ]


@pytest.fixture
def empty_rows():
    return []


@pytest.fixture
def sample_schema_with_date():
    """Schema de exemplo com coluna de data."""
    return {
        'available_columns': {
            'produto',
            'quantidade',
            'preco_unitario',
            'data_venda',
        },
        'required_columns': [
            'produto',
            'quantidade',
            'preco_unitario',
            'data_venda',
        ],
        'has_date_column': True,
        'date_column': 'data_venda',
        'is_valid_sales_data': True,
    }


@pytest.fixture
def sample_schema_no_date():
    """Schema de exemplo sem coluna de data."""
    return {
        'available_columns': {'produto', 'quantidade', 'preco_unitario'},
        'required_columns': ['produto', 'quantidade', 'preco_unitario'],
        'has_date_column': False,
        'date_column': None,
        'is_valid_sales_data': True,
    }
