# API de Backtesting para Estratégias de Trading Algorítmico

## 1. Visão Geral

Este projeto é um serviço backend (API REST) construído em Python com FastAPI, projetado para executar backtests de estratégias de trading do tipo *trend following*. O sistema utiliza dados históricos do Yahoo Finance, emprega a biblioteca `Backtrader` como motor de simulação e persiste todos os dados e resultados num banco de dados Postgres.

A arquitetura foi desenvolvida num padrão de monolito modular, totalmente orquestrada com Docker e Docker Compose para garantir a reprodutibilidade do ambiente.

## 2. Funcionalidades Principais

* **Coleta de Dados Históricos:** Endpoint para buscar e armazenar dados OHLCV de qualquer ativo listado no Yahoo Finance.
* **Motor de Backtest Flexível:** Suporte para múltiplas estratégias de trading, com parâmetros customizáveis via API.
* **Gestão de Risco Obrigatória:** Implementação de stop loss (baseado em ATR) e dimensionamento de posição (limitado a 1% do capital por operação).
* **Persistência de Resultados:** Todos os backtests executados e os seus resultados detalhados (métricas, trades) são guardados no banco de dados para consulta posterior.
* **API Completa:** Endpoints para iniciar, listar e consultar os resultados de cada backtest, com documentação interativa via OpenAPI.
* **Testes Automatizados:** Suíte de testes com Pytest que garante a qualidade e robustez do código, com cobertura superior a 70% nos módulos principais.
* **Diferencial de Machine Learning:** Implementação de um modelo de Regressão Logística que atua como um filtro para os sinais de trading, adicionando uma camada de inteligência à estratégia.

## 3. Estratégias Implementadas

1.  **`sma_cross` (Cruzamento de Médias Móveis):** Compra quando uma média móvel curta cruza acima de uma longa.
2.  **`breakout` (Rompimento de Máximas/Mínimas):** Compra quando o preço rompe a máxima de um período N.
3.  **`sma_cross_ml` (Diferencial):** Versão da `sma_cross` que só compra se o modelo de Machine Learning também prever um dia de alta.

## 4. Stack de Tecnologias

* **Backend:** Python 3.11, FastAPI
* **Base de Dados:** PostgreSQL
* **Motor de Backtest:** Backtrader
* **Manipulação de Dados:** Pandas, SQLAlchemy
* **Machine Learning:** Scikit-learn
* **Infraestrutura:** Docker, Docker Compose
* **Migrações:** Alembic
* **Testes:** Pytest, Pytest-Cov
* **Dados:** yfinance

## 5. Como Executar o Projeto

### Pré-requisitos
* Docker
* Docker Compose

### Passos para a Execução

1.  **Clonar o Repositório**
    ```bash
    # Por favor, substitua pela URL real do seu repositório
    git clone [https://github.com/VTavaress/trading_api.git](https://github.com/VTavaress/trading_api.git)
    cd trading_api
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

## 6. Guia de Uso da API
*(Nota: No código, todos os endpoints têm o prefixo `/api/v1/`)*

### Passo 1: Popular a Base de Dados
* **Endpoint:** `POST /api/v1/data/fetch` (Implementação do requisito `POST /data/indicators/update`)
* **Exemplo de Corpo (JSON):**
    ```json
    {
      "ticker": "PETR4.SA",
      "start_date": "2022-01-01",
      "end_date": "2023-12-31"
    }
    ```

### Passo 2: Executar um Backtest
* **Endpoint:** `POST /api/v1/backtests/run`
* **Exemplo de Corpo (JSON):**
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
* **Listar todos os backtests:** `GET /api/v1/backtests`
* **Ver o resultado detalhado:** `GET /api/v1/backtests/{id}/results`

## 7. Acesso ao Banco de Dados
O Postgres é exposto na porta `5432`. Pode acedê-lo com qualquer cliente de base de dados.
* **Host:** `localhost`
* **Porta:** `5432`
* **Credenciais (configuráveis no `.env`):**
    * **User:** `myuser`
    * **Password:** `mypassword`
    * **Database:** `trading_db`

## 8. Entregáveis
Este repositório contém todos os entregáveis solicitados:
* ✅ Código-fonte completo com `Dockerfile`, `docker-compose.yml` e este `README.md`.
* ✅ Scripts de migração funcionais com **Alembic**.
* ✅ Uma coleção de requests (`api_requests.http`) para testar os endpoints da API.
* ✅ Testes automatizados com **Pytest**, com cobertura superior a 70%.
* ✅ *(Diferencial)* Implementação de um modelo de Machine Learning como filtro de estratégia.

## 9. Notas Finais

O desenvolvimento deste case foi um desafio muito satisfatório; gosto muito de pôr em prática o que aprendi. A persistência em diagnosticar e resolver os desafios de ambiente, especialmente na configuração do Docker, foi uma experiência fundamental que reforçou a minha capacidade de encontrar soluções em cenários complexos.

Agradeço imensamente pela oportunidade de participar deste processo seletivo.
