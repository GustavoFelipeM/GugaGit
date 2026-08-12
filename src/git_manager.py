import subprocess
import shutil
import shlex

def git_instalado():
    return shutil.which("git") is not None

def obter_config_git():
    nome = interface_git(["git", "config", "--global", "user.name"])
    email = interface_git(["git", "config", "--global", "user.email"])
    
    return {
        "nome": nome.stdout.strip() if nome.returncode == 0 else "",
        "email": email.stdout.strip() if email.returncode == 0 else ""
    }

def salvar_config_git(nome, email):
    r1 = interface_git(["git", "config", "--global", "user.name", nome])
    r2 = interface_git(["git", "config", "--global", "user.email", email])
    
    if r1.returncode == 0 and r2.returncode == 0:
        return "Configurações de autoria atualizadas com sucesso!", True
    return "Erro ao salvar configurações.", False

def interface_git(comando):
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True
    )
    return resultado

def tratar_erros(resultado, mensagem):
    if resultado.returncode == 0:
        return mensagem, True
    else:
        return resultado.stderr, False

def branch_atual():
    resultado = interface_git(["git", "branch", "--show-current"])

    return resultado.stdout.strip()

def status():
    resultado = interface_git(["git", "status"])

    return resultado.stdout

def fetch():
    resultado = interface_git(["git", "fetch"])

    return tratar_erros(resultado, "Informações atualizadas!")

def criar_branch(nome):
    resultado = interface_git(["git", "checkout", "-b", nome])

    return tratar_erros(resultado, "Branch criada!")

def adicionar():
    resultado = interface_git(["git", "add", "."])

    return tratar_erros(resultado, "Arquivos adicionados!")

def commit(mensagem):
    resultado = interface_git(["git", "commit", "-m", mensagem])

    return tratar_erros(resultado, "Commit realizado!")

def push(branch):
    resultado = interface_git(["git", "push", "-u", "origin", branch])

    return tratar_erros(resultado, "Push realizado com sucesso!")

def listar_branches():
    resultado = interface_git(["git", "branch"])

    if resultado.returncode == 0:
        branches = resultado.stdout.splitlines()
        return [branch.strip().lstrip("* ") for branch in branches]
    else:
        return None
    
def trocar_branch(nome):
    resultado = interface_git(["git", "checkout", nome])

    return tratar_erros(resultado, "Branch trocado com sucesso!")

def pull():
    resultado = interface_git(["git", "pull"])

    return tratar_erros(resultado, "Pull feito com sucesso!")

def clonar_repositorio(repositorio, pasta):
    resultado = subprocess.run(
        ["git", "clone", repositorio],
        cwd=pasta,
        capture_output=True,
        text=True
    )

    return tratar_erros(
        resultado,
        "Repositorio clonado com sucesso!"
    )

def restaurar_alteracoes():
    resultado = interface_git(["git", "restore", "."])
    
    return tratar_erros(resultado, "Desfeito com sucesso!")

def deletar_branch(nome):
    resultado = interface_git(["git", "branch", "-d", nome])

    return tratar_erros(resultado, "Branch deletada!")

def remover_staging():
    resultado = interface_git(["git", "restore", "--staged", "."])

    return tratar_erros(resultado, "Staging removido com sucesso!")

def historico():
    resultado = interface_git(["git", "log"])

    if resultado.returncode == 0:
        return resultado.stdout

    return None

def diff():
    resultado = interface_git(["git", "diff"])

    if resultado.returncode == 0:
        return resultado.stdout

    return None

def stash():
    resultado = interface_git(["git", "stash"])

    return tratar_erros(resultado, "Alterações guardadas no stash!")


def stash_pop():
    resultado = interface_git(["git", "stash", "pop"])

    return tratar_erros(resultado, "Stash aplicado!")


def listar_stash():
    resultado = interface_git(["git", "stash", "list"])

    if resultado.returncode == 0:
        return resultado.stdout

    return None

def merge(nome):
    resultado = interface_git(["git", "merge", nome])

    return tratar_erros(resultado, "Mergeado com sucesso!")

def listar_tags():
    resultado = interface_git(["git", "tag"])

    if resultado.returncode == 0:
        return resultado.stdout
    
    return None

def executar_comando_livre(comando_texto, pasta_repositorio=None):
    comando_texto = comando_texto.strip()
    if not comando_texto:
        return "Comando vazio.", False

    try:
        args = shlex.split(comando_texto)
        
        resultado = subprocess.run(
            args,
            cwd=pasta_repositorio,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        saida = resultado.stdout if resultado.stdout else resultado.stderr
        if not saida:
            saida = "Comando executado com sucesso (sem retorno de texto)."
            
        return saida, (resultado.returncode == 0)
        
    except subprocess.TimeoutExpired:
        return "ERRO: O comando demorou muito ou exige interação (ex: editor de texto).", False
    except Exception as e:
        return f"ERRO ao executar comando: {str(e)}", False