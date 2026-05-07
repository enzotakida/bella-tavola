import os
import joblib
import sklearn
import numpy as np
from dotenv import load_dotenv

load_dotenv()
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from huggingface_hub import HfApi, login

from data_utils import gerar_dataset

REPO_ID = "Main921/mlops-analise-credito-v1"
MODEL_FILENAME = "modelo_credito.pkl"
MODEL_CARD_FILENAME = "README.md"

FEATURE_NAMES = [
    "renda_mensal",
    "divida_atual",
    "score_pagamento",
    "idade",
    "num_dependentes",
]


def treinar():
    print("Gerando dados sintéticos...")
    df, X, y = gerar_dataset(n_samples=2000, seed=42)
    print(f"Dataset: {X.shape[0]} amostras | Inadimplentes: {y.sum()} ({y.mean():.0%})")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\nTreinando Random Forest...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    report = classification_report(
        y_test, y_pred, target_names=["Bom Pagador", "Inadimplente"], output_dict=True
    )
    print("\nMétricas no conjunto de teste:")
    print(
        classification_report(y_test, y_pred, target_names=["Bom Pagador", "Inadimplente"])
    )

    importancias = sorted(
        zip(FEATURE_NAMES, model.feature_importances_), key=lambda x: -x[1]
    )
    print("Importância das variáveis:")
    for name, imp in importancias:
        print(f"  {name:<25} {imp:.6f}")

    joblib.dump(model, MODEL_FILENAME)
    print(f"\nModelo salvo em: {MODEL_FILENAME}")

    modelo_carregado = joblib.load(MODEL_FILENAME)
    amostra = X_test[:5]
    assert np.array_equal(model.predict(amostra), modelo_carregado.predict(amostra))
    print("Artefato validado — predições idênticas.")

    metricas = {
        "precision": report["Inadimplente"]["precision"],
        "recall": report["Inadimplente"]["recall"],
        "f1": report["Inadimplente"]["f1-score"],
        "acuracia": accuracy_score(y_test, y_pred),
    }

    gerar_model_card(metricas, importancias)

    return model


def gerar_model_card(metricas: dict, importancias: list):
    linhas_importancia = "\n".join(
        f"{nome:<30} {imp:.6f}" for nome, imp in importancias
    )

    conteudo = f"""---
language:
  - pt
license: mit
tags:
  - classification
  - credit-risk
  - random-forest
  - sklearn
  - mlops
library_name: sklearn
metrics:
  - accuracy
  - f1
---

# mlops-analise-credito-v1

Modelo de classificação binária para análise de risco de crédito (inadimplência).
Desenvolvido como parte do curso de MLOps — Semana 3.

## Uso

```python
from huggingface_hub import hf_hub_download
import joblib

model = joblib.load(hf_hub_download("Main921/mlops-analise-credito-v1", "modelo_credito.pkl"))
features = [[5000.0, 5000.0, 75, 35, 2]]  # [renda_mensal, divida_atual, score_pagamento, idade, num_dependentes]
prediction = model.predict(features)
```

## Features de entrada

| Feature | Tipo | Descrição |
|---|---|---|
| renda_mensal | float | Renda mensal em reais |
| divida_atual | float | Dívida atual total em reais |
| score_pagamento | int | Score de pagamento (0–100) |
| idade | int | Idade do cliente em anos |
| num_dependentes | int | Número de dependentes |

## Métricas (test set, 20% dos dados)

| Métrica | Valor |
|---|---|
| Precision (Inadimplente) | {metricas['precision']:.2%} |
| Recall (Inadimplente) | {metricas['recall']:.2%} |
| F1 Score (Inadimplente) | {metricas['f1']:.2%} |
| Acurácia Geral | {metricas['acuracia']:.2%} |

## Importância das Variáveis

```
{linhas_importancia}
```

## Dependências

- scikit-learn=={sklearn.__version__}
- joblib=={joblib.__version__}
- pandas
- numpy
- huggingface_hub

## Limitações

> ⚠️ **IMPORTANTE:**
> - Modelo treinado com dados sintéticos, não com dados reais
> - Acurácia e métricas podem não refletir performance em produção
> - Não deve ser usado em decisões de crédito sem validação com dados reais
> - Requer retreinamento periódico com novos dados
> - Features podem precisar de ajustes conforme características do mercado mudam

## Modelo

- **Algoritmo:** Random Forest Classifier (100 árvores)
- **Tipo:** Classificação Binária (0 = Bom Pagador, 1 = Inadimplente)
"""

    with open(MODEL_CARD_FILENAME, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"Model card gerado em: {MODEL_CARD_FILENAME}")


def publicar():
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise EnvironmentError("Defina a variável de ambiente HF_TOKEN antes de publicar.")

    login(token=token)
    api = HfApi()

    print(f"\nPublicando no Hugging Face Hub: {REPO_ID}")
    for arquivo in [MODEL_FILENAME, MODEL_CARD_FILENAME, "requirements.txt"]:
        api.upload_file(
            path_or_fileobj=arquivo,
            path_in_repo=arquivo,
            repo_id=REPO_ID,
            repo_type="model",
            commit_message="chore: atualizar modelo e model card",
        )
        print(f"  Upload concluído: {arquivo}")

    print(f"\nRepositório: https://huggingface.co/{REPO_ID}")


if __name__ == "__main__":
    treinar()
    publicar()
