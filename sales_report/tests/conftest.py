import pytest


@pytest.fixture
def csv_data():
    return (
        'produto,quantidade,preco_unitario\n'
        'Camiseta,3,49.9\n'
        'Calça,2,99.9\n'
        'Camiseta,1,49.9\n'
        'Tênis,1,199.9\n'
    )


@pytest.fixture
def parsed_rows():
    return [
        {'produto': 'Camiseta', 'quantidade': '3', 'preco_unitario': '49.9'},
        {'produto': 'Calça', 'quantidade': '2', 'preco_unitario': '99.9'},
        {'produto': 'Camiseta', 'quantidade': '1', 'preco_unitario': '49.9'},
        {'produto': 'Tênis', 'quantidade': '1', 'preco_unitario': '199.9'},
    ]
