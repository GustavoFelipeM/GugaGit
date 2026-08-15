import json
import os
import sys

if sys.platform == "win32":
    PASTA_BASE_APP = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
else:
    PASTA_BASE_APP = os.path.expanduser("~/.config")

PASTA_CONFIG = os.path.join(PASTA_BASE_APP, "GugaGit")
ARQUIVO_CONFIG = os.path.join(PASTA_CONFIG, "config.json")

def carregar_config():
    if not os.path.exists(ARQUIVO_CONFIG):
        return {}

    try:
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except Exception:
        return {}

def salvar_config(config):
    os.makedirs(PASTA_CONFIG, exist_ok=True)

    with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as arquivo:
        json.dump(
            config,
            arquivo,
            indent=4,
            ensure_ascii=False
        )

def salvar_ultimo_repositorio(pasta):
    config = carregar_config()
    config["ultimo_repositorio"] = pasta
    salvar_config(config)

def obter_ultimo_repositorio():
    config = carregar_config()
    return config.get("ultimo_repositorio")