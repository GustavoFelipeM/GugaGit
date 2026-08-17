from src.infrastructure.git_cli import interface_git
from src.core.types import GitResult

class HistoryService:
    def historico(self) -> GitResult:
        """Retorna o histórico de commits do repositório."""
        resultado = interface_git(["git", "log"])
        if resultado.returncode == 0:
            return GitResult(sucesso=True, mensagem="Histórico obtido.", dados=resultado.stdout)
        return GitResult(sucesso=False, mensagem="Erro ao obter histórico.", erro_detalhado=resultado.stderr)

    def listar_tags(self) -> GitResult:
        """Retorna todas as tags criadas no repositório."""
        resultado = interface_git(["git", "tag"])
        if resultado.returncode == 0:
            return GitResult(sucesso=True, mensagem="Tags listadas.", dados=resultado.stdout)
        return GitResult(sucesso=False, mensagem="Erro ao listar tags.", erro_detalhado=resultado.stderr)