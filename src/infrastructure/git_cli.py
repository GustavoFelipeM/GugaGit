import subprocess
import shutil
import shlex

def git_instalado():
    return shutil.which("git") is not None

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