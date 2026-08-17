class GugaGitError(Exception):
    """Exceção base para todas as falhas do aplicativo GugaGit."""

    pass


class GitCommandError(GugaGitError):
    """Lançada quando um comando nativo do Git falha na execução."""

    def __init__(self, comando: str, erro_detalhado: str = ""):
        self.comando = comando
        self.erro_detalhado = erro_detalhado
        msg = f"Falha ao executar o comando '{comando}'."
        if erro_detalhado:
            msg += f" Detalhes: {erro_detalhado}"
        super().__init__(msg)


class RepositoryNotFoundError(GugaGitError):
    """Lançada quando o diretório especificado não contém um repositório Git válido."""

    def __init__(self, caminho: str):
        super().__init__(
            f"O diretório '{caminho}' não é um repositório Git válido."
        )


class UIError(GugaGitError):
    """Lançada para falhas relacionadas ao PyWebView ou integrações de janela."""

    pass

class GitNotInstalledError(GugaGitError):
    """Lançada quando a CLI do Git não é encontrada no PATH do sistema operacional."""

    def __init__(self):
        super().__init__(
            "O executável do Git não foi encontrado no sistema. Por favor, instale o Git."
        )