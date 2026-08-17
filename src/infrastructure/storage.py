import json
import os
import sys
from typing import Any, Dict, Optional
from webview import logger

if sys.platform == "win32":
    PASTA_BASE_APP = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
else:
    PASTA_BASE_APP = os.path.expanduser("~/.config")

PASTA_CONFIG = os.path.join(PASTA_BASE_APP, "GugaGit")
ARQUIVO_CONFIG = os.path.join(PASTA_CONFIG, "config.json")

def carregar_config() -> Dict[str, Any]:
    if not os.path.exists(ARQUIVO_CONFIG):
        return {}

    try:
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error(f"Falha ao carregar o arquivo de config: {exc}")
        return {}

def salvar_config(config: Dict[str, Any]) -> None:
    try:
        os.makedirs(PASTA_CONFIG, exist_ok=True)
        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as arquivo:
            json.dump(config, arquivo, indent=4, ensure_ascii=False)
    except OSError as exc:
        logger.error(f"Falha ao salvar as configurações: {exc}")

def salvar_ultimo_repositorio(pasta: str) -> None:
    config = carregar_config()
    config["ultimo_repositorio"] = pasta
    salvar_config(config)

def obter_ultimo_repositorio() -> Optional[str]:
    config = carregar_config()
    return config.get("ultimo_repositorio")