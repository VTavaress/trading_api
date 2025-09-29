# API de Backtesting para Estratégias de Trading Algorítmico

## 1. Visão Geral

[cite_start]Este projeto é um serviço backend (API REST) construído em Python com FastAPI, projetado para executar backtests de estratégias de trading do tipo *trend following*[cite: 3]. [cite_start]O sistema utiliza dados históricos do Yahoo Finance, emprega a biblioteca `Backtrader` como motor de simulação e persiste todos os dados e resultados num banco de dados Postgres[cite: 3, 7, 9, 13].

[cite_start]A arquitetura foi desenvolvida num padrão de monolito modular, totalmente orquestrada com Docker e Docker Compose para garantir a reprodutibilidade do ambiente[cite: 4, 12, 46]. [cite_start]O projeto cumpre todos os requisitos obrigatórios do case, incluindo gestão de risco, múltiplas estratégias, migrações com Alembic e testes automatizados, além de implementar diferenciais como um modelo de Machine Learning[cite: 10, 36, 44, 45].

## 2. Funcionalidades Principais

* [cite_start]**Coleta de Dados Históricos:** Endpoint para buscar e armazenar dados OHLCV de qualquer ativo listado no Yahoo Finance[cite: 7, 28].
* [cite_start]**Motor de Backtest Flexível:** Suporte para múltiplas estratégias de trading, com parâmetros customizáveis via API[cite: 6, 9].
* [cite_start]**Gestão de Risco Obrigatória:** Implementação de stop loss (baseado em ATR) e dimensionamento de posição (limitado a 1% do capital por operação)[cite: 37, 38].
* [cite_start]**Persistência de Resultados:** Todos os backtests e seus resultados detalhados (métricas, trades) são guardados no banco de dados[cite: 13, 53].
* [cite_start]**API Completa:** Endpoints para iniciar, listar e consultar os resultados de cada backtest[cite: 15].

## 3. Estratégias Implementadas

1.  [cite_start]**`sma_cross` (Cruzamento de Médias Móveis):** Compra quando uma média móvel curta cruza acima de uma longa[cite: 24].
2.  [cite_start]**`breakout` (Rompimento de Máximas/Mínimas):** Compra quando o preço rompe a máxima de um período N[cite: 23].
3.  [cite_start]**`sma_cross_ml` (Diferencial):** Versão da `sma_cross` que só compra se um modelo de Machine Learning (Regressão Logística) também prever um dia de alta[cite: 10, 75].

## 4. Stack de Tecnologias

* [cite_start]**Backend:** Python 3.11, FastAPI [cite: 40, 41]
* [cite_start]**Base de Dados:** PostgreSQL [cite: 13]
* [cite_start]**Motor de Backtest:** Backtrader [cite: 42]
* [cite_start]**Manipulação de Dados:** Pandas, SQLAlchemy [cite: 43, 44]
* **Machine Learning:** Scikit-learn
* [cite_start]**Infraestrutura:** Docker, Docker Compose [cite: 46]
* [cite_start]**Migrações:** Alembic [cite: 44]
* [cite_start]**Testes:** Pytest [cite: 45]

## 5. Como Executar o Projeto

### Pré-requisitos
* Docker
* Docker Compose

### Passos para a Execução

1.  **Clonar o Repositório**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd <NOME_DA_PASTA_DO_PROJETO>
    ```

2.  **Construir a Imagem e Iniciar os Serviços**
    Este comando irá construir a imagem da API e iniciar os contêineres da aplicação e do banco de dados em segundo plano.
    ```bash
    docker compose up --build -d
    ```

3.  **Executar as Migrações da Base de Dados**
    Com os serviços a correr, execute o seguinte comando para criar todas as tabelas:
    ```bash
    docker compose exec app alembic upgrade head
    ```

4.  **Aceder à API**
    A API estará agora a funcionar. A documentação interativa (Swagger UI) está disponível em:
    [http://localhost:8000/docs](http://localhost:8000/docs)

## 6. Como Usar a API

### Passo 1: Popular a Base de Dados
Antes de executar um backtest, precisa de ter os dados históricos do ativo no banco.

* **Endpoint:** `POST /api/v1/data/fetch`
* **Exemplo de Corpo (JSON):**
    ```json
    {
      "ticker": "PETR4.SA",
      "start_date": "2022-01-01",
      "end_date": "2023-12-31"
    }
    ```

### Passo 2: Executar um Backtest
Com os dados no banco, pode agora executar uma simulação.

* **Endpoint:** `POST /api/v1/backtests/run`
* **Exemplo com Filtro de ML (Diferencial):**
    ```json
    {
      "ticker": "PETR4.SA",
      "start_date": "2022-01-01",
      "end_date": "2023-12-31",
      "strategy_type": "sma_cross_ml",
      "strategy_params": {
        "fast": 10,
        "slow": 30
      },
      "initial_cash": 100000,
      "commission": 0.001
    }
    ```

### Passo 3: Consultar os Resultados
* **Listar todos os backtests:** `GET /backtests`
* **Ver o resultado detalhado de um backtest:** `GET /backtests/{id}/results`

## 7. Testes Automatizados
Para executar a suíte de testes e ver o relatório de cobertura, use o comando:
```bash
docker compose exec app pytest
```
[cite_start]O projeto atinge a meta de >70% de cobertura nos módulos principais, conforme exigido[cite: 45, 81].