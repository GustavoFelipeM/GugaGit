import os
import sys
import webview

from src.ui.api import GugaGitAPI
from src.infrastructure.storage import obter_ultimo_repositorio

if __name__ == '__main__':
    if sys.platform == 'win32':
        try:
            import ctypes
            myappid = 'gugagit.pro.app.v1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            print(f"Aviso: Não foi possível definir o AppUserModelID: {e}")

    api = GugaGitAPI()

    ultimo = obter_ultimo_repositorio()  
    if ultimo and os.path.isdir(ultimo) and os.path.isdir(os.path.join(ultimo, '.git')):
        try:
            api._registrar_workspace(ultimo)
        except Exception:
            pass

    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(os.path.dirname(__file__), 'assets', 'index.html')
    icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'gugabit.ico')

    try:
        webview.settings['DRAG_REGION_SELECTOR'] = '.titlebar'
    except Exception:
        pass
    
    webview.create_window(
        title='GugaGit Pro', 
        url=html_path,
        js_api=api,
        width=1280, 
        height=800,
        min_size=(1100, 700),
        resizable=False,
        frameless=True,
        easy_drag=False,
        background_color='#0a0a0a'
    )

    webview.start(func=lambda *args: api.aplicar_icone_nativo(icon_path), icon=icon_path)