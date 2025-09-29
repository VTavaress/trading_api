# app/modules/ml/services.py

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def create_features_and_target(df: pd.DataFrame):
    """
    Cria features (características) e a variável alvo para o modelo de ML.
    """
    # Features: Retornos passados (1, 3, 5 e 10 dias)
    for lag in [1, 3, 5, 10]:
        df[f'return_{lag}d'] = df['close'].pct_change(lag)

    # Alvo: A direção do próximo dia (1 para 'UP', 0 para 'DOWN')
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

    # Remove linhas com dados faltantes (NaN) gerados pelos cálculos
    df.dropna(inplace=True)
    return df

def train_prediction_model(df: pd.DataFrame):
    """
    Treina um modelo de Regressão Logística e retorna o modelo treinado.
    """
    processed_df = create_features_and_target(df.copy())
    
    if processed_df.empty:
        return None, None

    features = [col for col in processed_df.columns if 'return_' in col]
    X = processed_df[features]
    y = processed_df['target']

    # Treina o modelo com todos os dados disponíveis (sem split de teste aqui para simplificar)
    model = LogisticRegression()
    model.fit(X, y)
    
    return model, features