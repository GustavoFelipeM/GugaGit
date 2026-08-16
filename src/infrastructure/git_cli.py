import logging
import subprocess
import shutil
import shlex
from typing import List, Optional, Tuple

logger = logging.getLogger("GugaGit")

def git_instalado() -> bool:
    return shutil.which("git") is not None

def interface_git(comando: List[str]) -> subprocess.CompletedProcess:
    """Executa um comando Git no terminal e retorna o resultado do subprocesso."""
    logger.debug(f"Executando comando: {' '.join(comando)}")
    return subprocess.run(
        comando,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

def interpretar_erro_git(comando: List[str], stderr: str) -> str:
    """Mapeia erros técnicos do Git para mensagens amigáveis (Issue #19)."""
    err_lower = stderr.lower()
    cmd_principal = comando[1] if len(comando) > 1 else ""

    if "permission denied" in err_lower or "authentication failed" in err_lower:
        return "Erro de Autenticação: Verifique suas credenciais de acesso ao repositório."
    
    if cmd_principal == "push" and ("fetch first" in err_lower or "non-fast-forward" in err_lower):
        return "Push rejeitado: Existem alterações no servidor remoto. Faça um 'Pull' antes de enviar."
    
    if cmd_principal == "checkout" and "local changes to the following files would be overwritten" in err_lower:
        return "Troca de branch cancelada: Salve ou descarte suas alterações locais antes de mudar de branch."
        
    if "could not resolve host" in err_lower:
        return "Erro de Conexão: Sem acesso à internet ou ao servidor Git remoto."

    return f"Erro ao executar operação '{cmd_principal}'."

def executar_e_tratar(comando: List[str], msg_sucesso: str) -> Tuple[str, bool, str]:
    """Centraliza execução, traduz erros (Issue #19) e retorna (msg_amigavel, sucesso, erro_bruto)."""
    resultado = interface_git(comando)
    
    if resultado.returncode == 0:
        saida = resultado.stdout.strip()
        return (saida if saida else msg_sucesso), True, ""
    
    erro_bruto = resultado.stderr.strip() or "Erro desconhecido no Git."
    logger.error(f"Erro no comando {' '.join(comando)}: {erro_bruto}")
    
    msg_amigavel = interpretar_erro_git(comando, erro_bruto)
    return msg_amigavel, False, erro_bruto

def executar_comando_livre(comando_texto: str, pasta_repositorio: Optional[str] = None) -> Tuple[str, bool]:
    """Executa comandos de texto livre digitados pelo usuário no console do app."""
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
        logger.warning(f"Timeout ao executar comando livre: {comando_texto}")
        return "ERRO: O comando demorou muito ou exige interação (ex: editor de texto).", False
    except Exception as e:
        logger.exception("Falha ao executar comando livre.")
        return f"ERRO ao executar comando: {str(e)}", False