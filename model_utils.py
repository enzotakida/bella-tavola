import os
import joblib
from huggingface_hub import hf_hub_download, login

_model_cache = {}


def load_model(
    repo_id: str = "Main921/mlops-analise-credito-v1",
    filename: str = "modelo_credito.pkl",
    force_download: bool = False,
):
    token = os.environ.get("HF_TOKEN")
    if token:
        login(token=token)

    cache_key = f"{repo_id}/{filename}"
    if cache_key not in _model_cache or force_download:
        local_path = hf_hub_download(
            repo_id=repo_id, filename=filename, force_download=force_download
        )
        _model_cache[cache_key] = joblib.load(local_path)
    return _model_cache[cache_key]
