import subprocess
from unittest.mock import MagicMock, patch
from src.infrastructure.git_cli import (
    interface_git,
    executar_e_tratar,
    executar_comando_livre,
    git_instalado
)

# -----------------------------------------------------------------------------
# git_instalado
# -----------------------------------------------------------------------------

# Teste 1: Se o git estiver instalado, deve retornar True; caso contrário, False
@patch("shutil.which", return_value="/usr/bin/git")
def test_git_instalado_sucesso(mock_which):
    assert git_instalado() is True

@patch("shutil.which", return_value=None)
def test_git_instalado_falha(mock_which):
    assert git_instalado() is False

# -----------------------------------------------------------------------------
# interface_git
# -----------------------------------------------------------------------------

# Teste 2: Teste da interface_git com retorno simulado
@patch("subprocess.run")
def test_interface_git(mock_run):
    resultado_mock = MagicMock(returncode=0, stdout="git version 2.34.1")
    mock_run.return_value = resultado_mock

    resultado = interface_git(["git", "status"])

    assert resultado.returncode == 0
    assert resultado.stdout == "git version 2.34.1"
    mock_run.assert_called_once_with(["git", "status"], capture_output=True, text=True)

# -----------------------------------------------------------------------------
# executar_e_tratar
# -----------------------------------------------------------------------------

# Teste 3: Quando o comando Git é executado com sucesso (returncode == 0)
@patch("src.infrastructure.git_cli.interface_git")
def test_executar_e_tratar_sucesso(mock_interface):
    mock_interface.return_value = MagicMock(returncode=0, stdout="Everything up-to-date")

    msg, sucesso, erro = executar_e_tratar(["git", "push"], "Push realizado com sucesso!")

    assert msg == "Everything up-to-date"
    assert sucesso is True
    assert erro == ""
    mock_interface.assert_called_once_with(["git", "push"])

# Teste 4: Quando o comando Git falha (returncode != 0)
@patch("subprocess.run")
def test_interface_git(mock_run):
    resultado_mock = MagicMock(returncode=0, stdout="git version 2.34.1")
    mock_run.return_value = resultado_mock

    resultado = interface_git(["git", "status"])

    assert resultado.returncode == 0
    assert resultado.stdout == "git version 2.34.1"
    # Aceita argumentos posicionais ou nomeados que foram passados para o subprocess.run
    assert mock_run.call_args[0][0] == ["git", "status"]

# -----------------------------------------------------------------------------
# executar_comando_livre
# -----------------------------------------------------------------------------

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

# Teste 7: Comando livre quando o stdout e stderr vem vazios
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

# Teste 9: Simula um erro inesperado (ex: erro de permissão)
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