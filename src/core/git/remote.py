import subprocess
from src.infrastructure.git_cli import executar_e_tratar
from src.core.types import GitResult

class RemoteService:
    def fetch(self) -> GitResult:
        """Executa 'git fetch' para sincronizar com o remoto."""
        msg, ok, erro = executar_e_tratar(["git", "fetch"], "Informações atualizadas!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def pull(self) -> GitResult:
        """Baixa e mescla as atualizações do remoto na branch atual."""
        msg, ok, erro = executar_e_tratar(["git", "pull"], "Pull feito com sucesso!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def push(self, branch: str) -> GitResult:
        """Envia os commits locais para o repositório remoto."""
        msg, ok, erro = executar_e_tratar(["git", "push", "-u", "origin", branch], "Push realizado com sucesso!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def clonar_repositorio(self, repositorio: str, pasta: str) -> GitResult:
        """Clona um repositório remoto para um diretório local."""
        resultado = subprocess.run(
            ["git", "clone", repositorio],
            cwd=pasta,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if resultado.returncode == 0:
            return GitResult(sucesso=True, mensagem="Repositório clonado com sucesso!")
        erro = resultado.stderr.strip() or "Erro desconhecido ao clonar."
        return GitResult(sucesso=False, mensagem="Erro ao clonar repositório.", erro_detalhado=erro)