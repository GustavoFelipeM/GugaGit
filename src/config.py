import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONE = os.path.join(BASE_DIR, "assets", "gugabit.ico")


PASTA_CONFIG = os.path.join(
    os.environ["LOCALAPPDATA"],
    "GugaGit"
)

ARQUIVO_CONFIG = os.path.join(
    PASTA_CONFIG,
    "config.json"
)


def carregar_config():
    if not os.path.exists(ARQUIVO_CONFIG):
        return {}

    with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


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


def aplicar_icone(janela):
    if os.path.exists(ICONE):
        janela.iconbitmap(ICONE)