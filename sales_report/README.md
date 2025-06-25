# 📊 Sales Report - Sistema de Análise de Vendas

Um sistema modular e extensível para análise de dados de vendas a partir de arquivos CSV, desenvolvido seguindo os princípios SOLID e boas práticas de engenharia de software.

## 🚀 Características

- **Flexibilidade**: Processa CSVs com ou sem coluna de data
- **Detecção Automática**: Identifica automaticamente a estrutura dos dados
- **Múltiplos Formatos**: Saída em texto formatado ou JSON
- **Filtros Avançados**: Filtragem por intervalo de datas
- **Validação Robusta**: Validação de dados com relatórios de erro detalhados
- **Arquitetura SOLID**: Código modular, testável e extensível
- **Tratamento de Encoding**: Suporte automático para UTF-8 e CP1252

## 📋 Requisitos

- Python >=3.13
- Poetry (para gerenciamento de dependências)

## 🛠️ Instalação

### Usando Poetry (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/KernelGM/sales-report.git
cd sales-report/sales_report/
```

# Instale as dependências
```bash
poetry install
```
# Ative o ambiente virtual
```bash
poetry shell
```


## 📖 Uso

### Analisar um arquivo CSV no formato texto

```bash
python -m sales_report.main ../data/exemple.csv --format text
```

### Analisar um arquivo CSV no formato JSON

```bash
python -m sales_report.main ../data/exemple.csv --format json
```

### Filtrar por intervalo de datas

```bash
python -m sales_report.main ../data/exemple2.csv --start-date 2025-06-01 --end-date 2025-06-02 --format text
```

### Filtrar por intervalo de datas no formato texto

```bash
python -m sales_report.main ../data/exemple2.csv --start-date 2025-06-01 --end-date 2025-06-02 --format text
```

### Filtrar por intervalo de datas no formato JSON

```bash
python -m sales_report.main ../data/exemple2.csv --start-date 2025-06-01 --end-date 2025-06-02 --format json
```


###  Pular validação de dados

```bash
python -m sales_report.main ../data/exemple.csv --skip-validation
```

### Ajuda

```bash
python -m sales_report.main --help
```

## 📁 Formatos de CSV Suportados

### CSV com Data de Venda

```csv
produto,quantidade,preco_unitario,data_venda
Camiseta,3,49.90,2024-06-01
Calça,2,99.90,2024-06-02
Tênis,1,199.90,2024-06-03
```

### CSV sem Data de Venda

```csv
produto,quantidade,preco_unitario
Camiseta,3,49.90
Calça,2,99.90
Tênis,1,199.90
```

### Colunas Obrigatórias

- `produto`: Nome do produto (texto)
- `quantidade`: Quantidade vendida (número inteiro > 0)
- `preco_unitario`: Preço unitário (número decimal > 0)

### Colunas Opcionais

- `data_venda`: Data da venda no formato YYYY-MM-DD
- Outras colunas são ignoradas automaticamente

## 📊 Exemplo de Saída

### Formato Texto (Padrão)

```
Total de vendas por produto:
Produto    Total (R$)
---------  -----------
Camiseta        149.70
Calça           199.80
Tênis           199.90

Valor total de todas as vendas: R$ 549.40
Produto mais vendido: Camiseta (3 unidades)
```

### Formato JSON

```json
{
  "vendas_por_produto": {
    "Camiseta": 149.70,
    "Calça": 199.80,
    "Tênis": 199.90
  },
  "total_vendas": 549.40,
  "produto_mais_vendido": {
    "nome": "Camiseta",
    "quantidade": 3
  }
}
```

## 🏗️ Arquitetura

O sistema segue os princípios SOLID e está organizado em módulos bem definidos:

```bash
sales_report/
├── interfaces/        # Contratos e abstrações
├── readers/           # Leitores de dados (CSV, etc.)
├── processors/        # Processadores de dados
├── validators/        # Validadores de dados
├── filters/           # Filtros de dados
├── formatters/        # Formatadores de saída
├── factories/         # Factories para criação de objetos
├── utils/             # Utilitários e funções auxiliares
├── app/               # Aplicação principal
└── main.py            # Ponto de entrada
```

### Princípios SOLID Aplicados

- **S**ingle Responsibility: Cada classe tem uma única responsabilidade
- **O**pen/Closed: Extensível via interfaces, fechado para modificação
- **L**iskov Substitution: Implementações são intercambiáveis
- **I**nterface Segregation: Interfaces pequenas e específicas
- **D**ependency Inversion: Dependência de abstrações, não implementações

## 🧪 Testes

### Executar Todos os Testes

#### Com pytest
```bash
task test
```

### Estrutura de Testes

- `tests/test_app.py`: Testes unitários principais
- `tests/test_integration.py`: Testes de integração
- `tests/conftest.py`: Configuração e fixtures dos testes
