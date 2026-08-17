import logging
import os
import sys
import webview

from src.infrastructure.storage import obter_ultimo_repositorio
from src.ui.api import GugaGitAPI

# Configuração básica de log para capturar falhas na inicialização
logger = logging.getLogger(__name__)


def configurar_app_id_windows() -> None:
    """Configura o AppUserModelID para agrupar o ícone na barra de tarefas do Windows."""
    if sys.platform == "win32":
        try:
            import ctypes

            appid = "gugagit.pro.app.v1.0.3"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
        except (ImportError, AttributeError, OSError) as e:
            logger.warning("Não foi possível definir o AppUserModelID no Windows: %s", e)


def carregar_workspace_inicial(api: GugaGitAPI) -> None:
    """Tenta carregar o último repositório válido utilizado."""
    ultimo = obter_ultimo_repositorio()
    if ultimo and os.path.isdir(ultimo) and os.path.isdir(os.path.join(ultimo, ".git")):
        try:
            api._registrar_workspace(ultimo)
        except (OSError, ValueError) as e:
            logger.error("Falha ao registrar workspace inicial ('%s'): %s", ultimo, e)


def main() -> None:
    configurar_app_id_windows()

    api = GugaGitAPI()
    carregar_workspace_inicial(api)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "assets", "index.html")
    icon_path = os.path.join(base_dir, "assets", "gugabit.ico")

    # Define o seletor da barra de título personalizável para arrastar a janela
    if hasattr(webview, "settings"):
        webview.settings["DRAG_REGION_SELECTOR"] = ".titlebar"

    webview.create_window(
        title="GugaGit Pro",
        url=html_path,
        js_api=api,
        width=1280,
        height=800,
        min_size=(1100, 700),
        resizable=False,
        frameless=True,
        easy_drag=False,
        background_color="#0a0a0a",
    )

    webview.start(func=lambda *args: api.aplicar_icone_nativo(icon_path), icon=icon_path)


if __name__ == "__main__":
    main()