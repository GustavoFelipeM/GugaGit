import subprocess
from unittest.mock import MagicMock, patch
from src.infrastructure.git_cli import interface_git, tratar_erros, executar_comando_livre, git_instalado

# Teste 1: Se o git estiver instalado, deve retornar True; caso contrário, False
@patch("shutil.which", return_value="/usr/bin/git")
def test_git_instalado_sucesso(mock_which):
    assert git_instalado() is True

@patch("shutil.which", return_value=None)
def test_git_instalado_falha(mock_which):
    assert git_instalado() is False

# Teste 2: Teste da interface_git com retorno simulado
@patch("subprocess.run")
def test_interface_git(mock_run):
    resultado_mock = MagicMock(returncode=0, stdout="git version 2.34.1")
    mock_run.return_value = resultado_mock

    resultado = interface_git(["git", "status"])

    assert resultado.returncode == 0
    assert resultado.stdout == "git version 2.34.1"
    mock_run.assert_called_once_with(["git", "status"], capture_output=True, text=True)

# Teste 3: Quando returncode é 0, deve retornar a mensagem de sucesso e True
def test_tratar_erros_sucesso():
    resultado = MagicMock()
    resultado.returncode = 0
    
    mensagem, sucesso = tratar_erros(resultado, "Sucesso!")
    assert mensagem == "Sucesso!"
    assert sucesso is True

# Teste 4: Quando returncode != 0, deve retornar o erro do stderr e False
def test_tratar_erros_falha():
    resultado = MagicMock()
    resultado.returncode = 1
    resultado.stderr = "Erro ao executar comando."
    
    mensagem, sucesso = tratar_erros(resultado, "Sucesso!")
    assert mensagem == "Erro ao executar comando."
    assert sucesso is False

# Teste 5: Comando livre vazio deve retornar erro imediato
def test_executar_comando_livre_vazio():
    saida, sucesso = executar_comando_livre("   ")
    assert saida == "Comando vazio."
    assert sucesso is False

# Teste 6: Comando livre com stdout deve retornar a saída correta e sucesso True
@patch("subprocess.run")
def test_executar_comando_livre_stdout(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="Branch main", stderr="")

    saida, sucesso = executar_comando_livre("git branch", "/caminho/repositorio")

    assert saida == "Branch main"
    assert sucesso is True

# Teste 7: Comando livre quando o stdout e stderr vem vazios (ex: ao criar uma tag silenciosa)
@patch("subprocess.run")
def test_executar_comando_livre_sem_saida(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    saida, sucesso = executar_comando_livre("git checkout main")

    assert saida == "Comando executado com sucesso (sem retorno de texto)."
    assert sucesso is True

# Teste 8: Simula o lançamento da exceção TimeoutExpired do subprocess
@patch("subprocess.run")
def test_executar_comando_livre_timeout(mock_run):
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="git log", timeout=15)

    saida, sucesso = executar_comando_livre("git log")

    assert "ERRO: O comando demorou muito" in saida
    assert sucesso is False

# Teste 9: Simula um erro inesperado (ex: comando mal formatado ou erro de permissão)
@patch("subprocess.run")
def test_executar_comando_livre_excecao_generica(mock_run):
    mock_run.side_effect = Exception("Erro interno de permissao")
    
    saida, sucesso = executar_comando_livre("git status")
    
    assert "ERRO ao executar comando: Erro interno de permissao" in saida
    assert sucesso is False

# Teste 10: Comando livre que falha e devolve a mensagem de erro no stderr
@patch("subprocess.run")
def test_executar_comando_livre_erro_stderr(mock_run):
    mock_run.return_value = MagicMock(
        returncode=1, 
        stdout="", 
        stderr="fatal: not a git repository"
    )

    saida, sucesso = executar_comando_livre("git status")

    assert saida == "fatal: not a git repository"
    assert sucesso is False