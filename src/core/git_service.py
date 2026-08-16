import subprocess
from typing import List, Optional
from src.infrastructure.git_cli import executar_e_tratar, interface_git, git_instalado, executar_comando_livre
from src.core.types import GitResult

def obter_config_git() -> GitResult:
    """Busca o nome e e-mail configurados globalmente no Git."""
    nome = interface_git(["git", "config", "--global", "user.name"])
    email = interface_git(["git", "config", "--global", "user.email"])
    
    dados = {
        "nome": nome.stdout.strip() if nome.returncode == 0 else "",
        "email": email.stdout.strip() if email.returncode == 0 else ""
    }
    return GitResult(sucesso=True, mensagem="Configurações obtidas.", dados=dados)

def salvar_config_git(nome: str, email: str) -> GitResult:
    """Atualiza o nome e e-mail do usuário no Git global."""
    r1 = interface_git(["git", "config", "--global", "user.name", nome])
    r2 = interface_git(["git", "config", "--global", "user.email", email])
    
    if r1.returncode == 0 and r2.returncode == 0:
        return GitResult(sucesso=True, mensagem="Configurações de autoria atualizadas com sucesso!")
    
    erro = r1.stderr or r2.stderr or "Erro ao salvar configurações."
    return GitResult(sucesso=False, mensagem="Erro ao salvar configurações.", erro_detalhado=erro)

def branch_atual() -> GitResult:
    """Retorna o nome da branch atual em que o repositório se encontra."""
    resultado = interface_git(["git", "branch", "--show-current"])
    if resultado.returncode == 0:
        return GitResult(sucesso=True, mensagem="Branch obtida com sucesso.", dados=resultado.stdout.strip())
    return GitResult(sucesso=False, mensagem="Não foi possível identificar a branch atual.", erro_detalhado=resultado.stderr)

def status() -> GitResult:
    """Executa 'git status' e retorna o resultado bruto."""
    resultado = interface_git(["git", "status"])
    if resultado.returncode == 0:
        return GitResult(sucesso=True, mensagem="Status obtido com sucesso.", dados=resultado.stdout)
    return GitResult(sucesso=False, mensagem="Erro ao obter status.", erro_detalhado=resultado.stderr)

def fetch() -> GitResult:
    """Executa 'git fetch' para sincronizar com o remoto."""
    msg, ok, erro = executar_e_tratar(["git", "fetch"], "Informações atualizadas!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

def criar_branch(nome: str) -> GitResult:
    """Cria e muda imediatamente para uma nova branch."""
    msg, ok, erro = executar_e_tratar(["git", "checkout", "-b", nome], f"Branch '{nome}' criada com sucesso!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

def adicionar() -> GitResult:
    """Adiciona todas as alterações locais ao staging (git add .)."""
    msg, ok, erro = executar_e_tratar(["git", "add", "."], "Arquivos adicionados!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

def commit(mensagem: str) -> GitResult:
    """Cria um novo commit com a mensagem especificada."""
    if not mensagem.strip():
        return GitResult(sucesso=False, mensagem="A mensagem de commit não pode estar vazia.")
    
    msg, ok, erro = executar_e_tratar(["git", "commit", "-m", mensagem], "Commit realizado!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

def push(branch: str) -> GitResult:
    """Envia os commits locais para o repositório remoto."""
    msg, ok, erro = executar_e_tratar(["git", "push", "-u", "origin", branch], "Push realizado com sucesso!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

def listar_branches() -> GitResult:
    """Retorna uma lista limpa contendo todas as branches locais."""
    resultado = interface_git(["git", "branch"])
    if resultado.returncode == 0:
        branches = [b.strip().lstrip("* ") for b in resultado.stdout.splitlines()]
        return GitResult(sucesso=True, mensagem="Branches listadas com sucesso.", dados=branches)
    return GitResult(sucesso=False, mensagem="Erro ao listar branches.", erro_detalhado=resultado.stderr)
    
def trocar_branch(nome: str) -> GitResult:
    """Realiza a troca (checkout) para a branch informada."""
    msg, ok, erro = executar_e_tratar(["git", "checkout", nome], f"Trocado para a branch '{nome}' com sucesso!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

def pull() -> GitResult:
    """Baixa e mescla as atualizações do remoto na branch atual."""
    msg, ok, erro = executar_e_tratar(["git", "pull"], "Pull feito com sucesso!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

def clonar_repositorio(repositorio: str, pasta: str) -> GitResult:
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

def restaurar_alteracoes() -> GitResult:
    """Descarte alterações não salvas no diretório de trabalho."""
    msg, ok, erro = executar_e_tratar(["git", "restore", "."], "Desfeito com sucesso!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

def deletar_branch(nome: str) -> GitResult:
    """Deleta a branch local especificada."""
    msg, ok, erro = executar_e_tratar(["git", "branch", "-d", nome], f"Branch '{nome}' deletada!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

def remover_staging() -> GitResult:
    """Remove todas as alterações da área de staging (unstage)."""
    msg, ok, erro = executar_e_tratar(["git", "restore", "--staged", "."], "Staging removido com sucesso!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

def historico() -> GitResult:
    """Retorna o histórico de commits do repositório."""
    resultado = interface_git(["git", "log"])
    if resultado.returncode == 0:
        return GitResult(sucesso=True, mensagem="Histórico obtido.", dados=resultado.stdout)
    return GitResult(sucesso=False, mensagem="Erro ao obter histórico.", erro_detalhado=resultado.stderr)

def diff() -> GitResult:
    """Retorna a diferença das alterações locais não enviadas para o staging."""
    resultado = interface_git(["git", "diff"])
    if resultado.returncode == 0:
        conteudo = resultado.stdout or "Nenhuma diferença encontrada."
        return GitResult(sucesso=True, mensagem="Diff obtido.", dados=conteudo)
    return GitResult(sucesso=False, mensagem="Erro ao gerar diff.", erro_detalhado=resultado.stderr)

def stash() -> GitResult:
    """Guarda as alterações atuais em um stash temporário."""
    msg, ok, erro = executar_e_tratar(["git", "stash"], "Alterações guardadas no stash!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)


def stash_pop() -> GitResult:
    """Aplica o último stash salvo e o remove da pilha."""
    msg, ok, erro = executar_e_tratar(["git", "stash", "pop"], "Stash aplicado!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)


def listar_stash() -> GitResult:
    """Retorna a lista de stashes existentes no repositório."""
    resultado = interface_git(["git", "stash", "list"])
    if resultado.returncode == 0:
        return GitResult(sucesso=True, mensagem="Stashes listados.", dados=resultado.stdout)
    return GitResult(sucesso=False, mensagem="Erro ao listar stashes.", erro_detalhado=resultado.stderr)

def merge(nome: str) -> GitResult:
    """Realiza a fusão (merge) da branch informada na branch atual."""
    msg, ok, erro = executar_e_tratar(["git", "merge", nome], f"Merge de '{nome}' realizado com sucesso!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

def listar_tags() -> GitResult:
    """Retorna todas as tags criadas no repositório."""
    resultado = interface_git(["git", "tag"])
    if resultado.returncode == 0:
        return GitResult(sucesso=True, mensagem="Tags listadas.", dados=resultado.stdout)
    return GitResult(sucesso=False, mensagem="Erro ao listar tags.", erro_detalhado=resultado.stderr)

def obter_arquivos_status() -> GitResult:
    """Retorna uma lista estruturada dos arquivos modificados/não rastreados."""
    resultado = interface_git(["git", "status", "--porcelain"])

    if resultado.returncode != 0:
        return GitResult(
            sucesso=False, 
            mensagem="Erro ao consultar status dos arquivos.", 
            dados=[], 
            erro_detalhado=resultado.stderr
        )

    if not resultado.stdout.strip():
        return GitResult(sucesso=True, mensagem="Nenhum arquivo modificado.", dados=[])

    arquivos = []
    for linha in resultado.stdout.splitlines():
        if len(linha) < 3:
            continue

        status_staged = linha[0]
        status_unstaged = linha[1]
        arquivo = linha[3:].strip().replace('"', '')
        is_staged = status_staged not in (' ', '?')

        arquivos.append({
            "caminho": arquivo,
            "staged": is_staged,
            "status_staged": status_staged,
            "status_unstaged": status_unstaged
        })

    return GitResult(sucesso=True, mensagem="Arquivos analisados com sucesso.", dados=arquivos)

def adicionar_arquivos_staging(arquivos: List[str]) -> GitResult:
    """Executa git add apenas nos arquivos especificados."""
    if not arquivos:
        return GitResult(sucesso=True, mensagem="Nenhum arquivo selecionado.")
    
    msg, ok, erro = executar_e_tratar(["git", "add"] + arquivos, "Arquivos selecionados adicionados ao staging!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

def remover_selecionados_staging(arquivos: List[str]) -> GitResult:
    """Executa git restore --staged apenas nos arquivos especificados."""
    if not arquivos:
        return GitResult(sucesso=True, mensagem="Nenhum arquivo selecionado.")
    
    msg, ok, erro = executar_e_tratar(["git", "restore", "--staged"] + arquivos, "Arquivos removidos do staging!")
    return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)