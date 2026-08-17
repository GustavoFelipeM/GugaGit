import os
import webview


class WindowService:

    def __init__(self) -> None:
        self.janela_maximizada: bool = False

    def _obter_janela(self) -> None:
        return webview.windows[0] if webview.windows else None

    def minimizar(self) -> None:
        win = self._obter_janela()
        if win:
            win.minimize()

    def alternar_maximizar(self) -> None:
        win = self._obter_janela()
        if not win:
            return

        if self.janela_maximizada:
            if hasattr(win, "restore"):
                win.restore()
            self.janela_maximizada = False
        else:
            if hasattr(win, "maximize"):
                win.maximize()
            self.janela_maximizada = True

    def maximizar_janela(self) -> None:
            if webview.windows:
                janela = webview.windows[0]
                if hasattr(janela, "maximize"):
                    janela.maximize()
                    self.janela_maximizada = True
    
    def restaurar_janela(self) -> None:
        if webview.windows:
            janela = webview.windows[0]
            if hasattr(janela, "restore"):
                janela.restore()
                self.janela_maximizada = False

    def fechar(self) -> None:
        win = self._obter_janela()
        if win:
            win.destroy()

    def aplicar_icone_nativo(self, caminho_icone: str):
        try:
            import clr  # type: ignore

            clr.AddReference("System.Drawing")
            from System.Drawing import Icon  # type: ignore

            win = self._obter_janela()
            if win and os.path.isfile(caminho_icone) and getattr(win, "native", None):
                win.native.Icon = Icon(caminho_icone)
                win.native.ShowIcon = True
        except Exception as exc:
            webview.logger.warning(
                f"Não foi possível aplicar ícone nativo do Windows: {exc}"
            )