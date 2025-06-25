import pytest


@pytest.fixture
def mock_csv_data():
    return (
        'produto,quantidade,preco_unitario,data_venda\n'
        'Camiseta,3,49.9,2025-06-01\n'
        'Calça,2,99.9,2025-06-05\n'
    )


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
