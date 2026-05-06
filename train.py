import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from huggingface_hub import HfApi, login

from data_utils import gerar_dataset

REPO_ID = "Main921/mlops-analise-credito-v1"
MODEL_FILENAME = "modelo_credito.pkl"


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
    print("\nMétricas no conjunto de teste:")
    print(classification_report(y_test, y_pred, target_names=["Bom Pagador", "Inadimplente"]))

    feature_names = ["renda_mensal", "divida_atual", "score_pagamento", "idade", "num_dependentes"]
    print("Importância das variáveis:")
    for name, imp in sorted(zip(feature_names, model.feature_importances_), key=lambda x: -x[1]):
        print(f"  {name:<25} {imp:.6f}")

    joblib.dump(model, MODEL_FILENAME)
    print(f"\nModelo salvo em: {MODEL_FILENAME}")

    modelo_carregado = joblib.load(MODEL_FILENAME)
    amostra = X_test[:5]
    assert np.array_equal(model.predict(amostra), modelo_carregado.predict(amostra))
    print("Artefato validado — predições idênticas.")

    return model


def publicar():
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise EnvironmentError("Defina a variável de ambiente HF_TOKEN antes de publicar.")

    login(token=token)
    api = HfApi()

    print(f"\nPublicando no Hugging Face Hub: {REPO_ID}")
    api.upload_file(
        path_or_fileobj=MODEL_FILENAME,
        path_in_repo=MODEL_FILENAME,
        repo_id=REPO_ID,
        repo_type="model",
        commit_message="chore: atualizar modelo treinado localmente",
    )
    print(f"Upload concluído: https://huggingface.co/{REPO_ID}")


if __name__ == "__main__":
    treinar()
    publicar()
