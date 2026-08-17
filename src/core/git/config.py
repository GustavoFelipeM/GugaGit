from src.infrastructure.git_cli import interface_git
from src.core.types import GitResult

class GitConfigService:
    def obter_config_git(self) -> GitResult:
        """Busca o nome e e-mail configurados globalmente no Git."""
        nome = interface_git(["git", "config", "--global", "user.name"])
        email = interface_git(["git", "config", "--global", "user.email"])
        
        dados = {
            "nome": nome.stdout.strip() if nome.returncode == 0 else "",
            "email": email.stdout.strip() if email.returncode == 0 else ""
        }
        return GitResult(sucesso=True, mensagem="Configurações obtidas.", dados=dados)

    def salvar_config_git(self, nome: str, email: str) -> GitResult:
        """Atualiza o nome e e-mail do usuário no Git global."""
        r1 = interface_git(["git", "config", "--global", "user.name", nome])
        r2 = interface_git(["git", "config", "--global", "user.email", email])
        
        if r1.returncode == 0 and r2.returncode == 0:
            return GitResult(sucesso=True, mensagem="Configurações de autoria atualizadas com sucesso!")
        
        erro = r1.stderr or r2.stderr or "Erro ao salvar configurações."
        return GitResult(sucesso=False, mensagem="Erro ao salvar configurações.", erro_detalhado=erro)