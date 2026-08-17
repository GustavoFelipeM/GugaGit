from src.infrastructure.git_cli import executar_e_tratar, interface_git
from src.core.types import GitResult

class StashService:
    def stash(self) -> GitResult:
        """Guarda as alterações atuais em um stash temporário."""
        msg, ok, erro = executar_e_tratar(["git", "stash"], "Alterações guardadas no stash!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def stash_pop(self) -> GitResult:
        """Aplica o último stash salvo e o remove da pilha."""
        msg, ok, erro = executar_e_tratar(["git", "stash", "pop"], "Stash aplicado!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def listar_stash(self) -> GitResult:
        """Retorna a lista de stashes existentes no repositório."""
        resultado = interface_git(["git", "stash", "list"])
        if resultado.returncode == 0:
            return GitResult(sucesso=True, mensagem="Stashes listados.", dados=resultado.stdout)
        return GitResult(sucesso=False, mensagem="Erro ao listar stashes.", erro_detalhado=resultado.stderr)