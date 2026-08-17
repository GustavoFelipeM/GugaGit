from src.infrastructure.git_cli import executar_e_tratar, interface_git, git_instalado, executar_comando_livre
from src.core.types import GitResult

class BranchService:
    def branch_atual(self) -> GitResult:
        """Retorna o nome da branch atual em que o repositório se encontra."""
        resultado = interface_git(["git", "branch", "--show-current"])
        if resultado.returncode == 0:
            return GitResult(sucesso=True, mensagem="Branch obtida com sucesso.", dados=resultado.stdout.strip())
        return GitResult(sucesso=False, mensagem="Não foi possível identificar a branch atual.", erro_detalhado=resultado.stderr)

    def listar_branches(self) -> GitResult:
        """Retorna uma lista limpa contendo todas as branches locais."""
        resultado = interface_git(["git", "branch"])
        if resultado.returncode == 0:
            branches = [b.strip().lstrip("* ") for b in resultado.stdout.splitlines()]
            return GitResult(sucesso=True, mensagem="Branches listadas com sucesso.", dados=branches)
        return GitResult(sucesso=False, mensagem="Erro ao listar branches.", erro_detalhado=resultado.stderr)

    def criar_branch(self, nome: str) -> GitResult:
        """Cria e muda imediatamente para uma nova branch."""
        msg, ok, erro = executar_e_tratar(["git", "checkout", "-b", nome], f"Branch '{nome}' criada com sucesso!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def trocar_branch(self, nome: str) -> GitResult:
        """Realiza a troca (checkout) para a branch informada."""
        msg, ok, erro = executar_e_tratar(["git", "checkout", nome], f"Trocado para a branch '{nome}' com sucesso!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def deletar_branch(self, nome: str) -> GitResult:
        """Deleta a branch local especificada."""
        msg, ok, erro = executar_e_tratar(["git", "branch", "-d", nome], f"Branch '{nome}' deletada!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def merge(self, nome: str) -> GitResult:
        """Realiza a fusão (merge) da branch informada na branch atual."""
        msg, ok, erro = executar_e_tratar(["git", "merge", nome], f"Merge de '{nome}' realizado com sucesso!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)