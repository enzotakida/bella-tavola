import numpy as np
import pandas as pd
from typing import Tuple


def gerar_dataset(
    n_samples: int = 2000,
    seed: int = 42,
    proporcao_inadimplentes: float = 0.3,
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    if not (0.05 <= proporcao_inadimplentes <= 0.95):
        raise ValueError(
            f"proporcao_inadimplentes deve estar entre 0.05 e 0.95, "
            f"recebido: {proporcao_inadimplentes}"
        )

    rng = np.random.default_rng(seed)

    inadimplente = rng.choice(
        [0, 1],
        size=n_samples,
        p=[1 - proporcao_inadimplentes, proporcao_inadimplentes],
    )

    renda_mensal = np.where(
        inadimplente,
        rng.uniform(800, 3000, n_samples),
        rng.uniform(3000, 15000, n_samples),
    ).round(2)

    divida_atual = np.where(
        inadimplente,
        rng.uniform(5000, 50000, n_samples),
        rng.uniform(0, 8000, n_samples),
    ).round(2)

    score_pagamento = np.where(
        inadimplente,
        rng.integers(0, 45, n_samples),
        rng.integers(55, 101, n_samples),
    )

    idade = np.where(
        inadimplente,
        rng.integers(18, 35, n_samples),
        rng.integers(30, 65, n_samples),
    )

    num_dependentes = np.where(
        inadimplente,
        rng.integers(2, 6, n_samples),
        rng.integers(0, 3, n_samples),
    )

    df = pd.DataFrame(
        {
            "renda_mensal": renda_mensal,
            "divida_atual": divida_atual,
            "score_pagamento": score_pagamento,
            "idade": idade,
            "num_dependentes": num_dependentes,
            "inadimplente": inadimplente,
        }
    )

    X = df.drop(columns=["inadimplente"]).values
    y = df["inadimplente"].values
    return df, X, y


if __name__ == "__main__":
    df, X, y = gerar_dataset()
    print(df.describe().round(2))
    print(f"\nDistribuição do target:\n{df['inadimplente'].value_counts()}")
    print(f"\nShape: {X.shape}")
