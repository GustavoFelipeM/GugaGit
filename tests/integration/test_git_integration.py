import os
import subprocess
import pytest
from src.core.git_service import (
    obter_config_git,
    salvar_config_git,
    branch_atual,
    status,
    fetch,
    criar_branch,
    adicionar,
    commit,
    push,
    listar_branches,
    trocar_branch,
    pull,
    clonar_repositorio,
    restaurar_alteracoes,
    deletar_branch,
    remover_staging,
    historico,
    diff,
    stash,
    stash_pop,
    listar_stash,
    merge,
    listar_tags
)
from src.infrastructure.git_cli import executar_comando_livre, git_instalado


# ==============================================================================
# FIXTURES DE INTEGRAÇÃO
# ==============================================================================

@pytest.fixture
def repo_git_real(tmp_path, monkeypatch):
    """
    Cria um repositório Git local temporário e isolado.
    Isola variáveis de ambiente para não alterar o .gitconfig do sistema.
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    repo_dir = tmp_path / "repo_teste"
    repo_dir.mkdir()

    # Define o diretório atual de execução para a pasta temporária
    monkeypatch.chdir(repo_dir)

    # Inicializa o git e define autor local
    subprocess.run(["git", "init"], check=True, cwd=repo_dir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Dev Teste"], check=True, cwd=repo_dir)
    subprocess.run(["git", "config", "user.email", "dev@teste.com"], check=True, cwd=repo_dir)

    # Cria commit inicial para que HEAD e branches funcionem
    arquivo_init = repo_dir / "init.txt"
    arquivo_init.write_text("commit inicial", encoding="utf-8")
    subprocess.run(["git", "add", "."], check=True, cwd=repo_dir)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True, cwd=repo_dir)

    return repo_dir


@pytest.fixture
def setup_remoto(tmp_path, monkeypatch):
    """
    Cria um repositório 'bare' (remoto) e um local para testar push, pull, fetch e clone.
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    # Repositório Bare (Origin)
    bare_dir = tmp_path / "remote_origin.git"
    bare_dir.mkdir()
    subprocess.run(["git", "init", "--bare"], check=True, cwd=bare_dir, capture_output=True)

    # Repositório Local
    local_dir = tmp_path / "local_repo"
    local_dir.mkdir()
    monkeypatch.chdir(local_dir)

    subprocess.run(["git", "init"], check=True, cwd=local_dir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Dev Remote"], check=True, cwd=local_dir)
    subprocess.run(["git", "config", "user.email", "remote@teste.com"], check=True, cwd=local_dir)

    # Commit inicial e vinculo do origin
    (local_dir / "README.md").write_text("# Test Repo", encoding="utf-8")
    subprocess.run(["git", "add", "."], check=True, cwd=local_dir)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True, cwd=local_dir)
    subprocess.run(["git", "remote", "add", "origin", str(bare_dir)], check=True, cwd=local_dir)

    b_atual = branch_atual()
    subprocess.run(["git", "push", "-u", "origin", b_atual], check=True, cwd=local_dir, capture_output=True)

    return {
        "bare_path": str(bare_dir),
        "local_dir": local_dir,
        "branch": b_atual
    }


# ==============================================================================
# TESTES DE INTEGRAÇÃO - CONFIGURAÇÃO & INSTALAÇÃO
# ==============================================================================

def test_git_instalado_real():
    assert git_instalado() is True


def test_salvar_e_obter_config_git_real(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    msg, sucesso = salvar_config_git("Guga Dev", "guga@dev.com")
    assert sucesso is True
    assert msg == "Configurações de autoria atualizadas com sucesso!"

    config = obter_config_git()
    assert config["nome"] == "Guga Dev"
    assert config["email"] == "guga@dev.com"


# ==============================================================================
# TESTES DE INTEGRAÇÃO - FLUXO DE TRABALHO LOCAL
# ==============================================================================

def test_branch_atual_e_listar_branches_real(repo_git_real):
    branch = branch_atual()
    assert branch in ["main", "master"]

    branches = listar_branches()
    assert isinstance(branches, list)
    assert branch in branches


def test_fluxo_criar_trocar_e_deletar_branch_real(repo_git_real):
    nova_branch = "feature/login"

    # Criar branch
    msg_criar, sucesso_criar = criar_branch(nova_branch)
    assert sucesso_criar is True
    assert branch_atual() == nova_branch

    # Trocar para branch principal
    b_principal = "main" if "main" in listar_branches() else "master"
    msg_trocar, sucesso_trocar = trocar_branch(b_principal)
    assert sucesso_trocar is True
    assert branch_atual() == b_principal

    # Deletar branch criada
    msg_del, sucesso_del = deletar_branch(nova_branch)
    assert sucesso_del is True
    assert nova_branch not in listar_branches()


def test_fluxo_adicionar_commit_e_historico_real(repo_git_real):
    novo_arquivo = repo_git_real / "novo.txt"
    novo_arquivo.write_text("linha 1\n", encoding="utf-8")

    # Adicionar
    msg_add, sucesso_add = adicionar()
    assert sucesso_add is True

    # Commit
    msg_commit, sucesso_commit = commit("Adiciona novo.txt")
    assert sucesso_commit is True

    # Historico (Log)
    log_out = historico()
    assert log_out is not None
    assert "Adiciona novo.txt" in log_out


def test_status_e_diff_real(repo_git_real):
    # Altera arquivo existente
    arquivo_init = repo_git_real / "init.txt"
    arquivo_init.write_text("commit inicial - alterado", encoding="utf-8")

    out_status = status()
    assert "modified:" in out_status or "modificado:" in out_status

    out_diff = diff()
    assert out_diff is not None
    assert "-commit inicial" in out_diff
    assert "+commit inicial - alterado" in out_diff


def test_remover_staging_e_restaurar_alteracoes_real(repo_git_real):
    arquivo = repo_git_real / "init.txt"
    arquivo.write_text("alteracao temporaria", encoding="utf-8")

    # Adiciona ao staging
    adicionar()
    out_status_staged = status()
    assert "Changes to be committed" in out_status_staged or "Mudanças a serem submetidas" in out_status_staged

    # Remove do staging
    msg_unstage, sucesso_unstage = remover_staging()
    assert sucesso_unstage is True

    # Restaura arquivo
    msg_restore, sucesso_restore = restaurar_alteracoes()
    assert sucesso_restore is True
    assert arquivo.read_text(encoding="utf-8") == "commit inicial"


def test_stash_fluxo_completo_real(repo_git_real):
    arquivo = repo_git_real / "init.txt"
    arquivo.write_text("alteracao antes do stash", encoding="utf-8")

    # Stash
    msg_stash, sucesso_stash = stash()
    assert sucesso_stash is True
    assert arquivo.read_text(encoding="utf-8") == "commit inicial"

    # Listar Stash
    stashes = listar_stash()
    assert stashes is not None
    assert "WIP on" in stashes

    # Stash Pop
    msg_pop, sucesso_pop = stash_pop()
    assert sucesso_pop is True
    assert arquivo.read_text(encoding="utf-8") == "alteracao antes do stash"


def test_merge_branches_real(repo_git_real):
    b_base = branch_atual()

    # Cria branch paralela
    criar_branch("feature/calc")
    (repo_git_real / "calc.py").write_text("print(1+1)", encoding="utf-8")
    adicionar()
    commit("Adiciona calculadora")

    # Volta para base e faz o merge
    trocar_branch(b_base)
    msg_merge, sucesso_merge = merge("feature/calc")

    assert sucesso_merge is True
    assert (repo_git_real / "calc.py").exists()


def test_listar_tags_real(repo_git_real):
    # Cria tag usando comando livre
    executar_comando_livre("git tag v1.0.0", str(repo_git_real))

    tags = listar_tags()
    assert tags is not None
    assert "v1.0.0" in tags


# ==============================================================================
# TESTES DE INTEGRAÇÃO - SINCRONIZAÇÃO E REMOTO
# ==============================================================================

def test_push_fetch_e_pull_real(setup_remoto):
    local_dir = setup_remoto["local_dir"]
    branch = setup_remoto["branch"]

    # Cria novo commit local
    (local_dir / "remoto.txt").write_text("dados remotos", encoding="utf-8")
    adicionar()
    commit("Commit para o remote")

    # Push
    msg_push, sucesso_push = push(branch)
    assert sucesso_push is True

    # Fetch
    msg_fetch, sucesso_fetch = fetch()
    assert sucesso_fetch is True

    # Pull
    msg_pull, sucesso_pull = pull()
    assert sucesso_pull is True


def test_clonar_repositorio_real(setup_remoto, tmp_path):
    pasta_destino = tmp_path / "clone_destino"
    pasta_destino.mkdir()

    msg_clone, sucesso_clone = clonar_repositorio(setup_remoto["bare_path"], str(pasta_destino))
    assert sucesso_clone is True

    # Verifica se os arquivos foram clonados de fato
    repo_clonado = pasta_destino / "remote_origin"
    assert (repo_clonado / ".git").exists()
    assert (repo_clonado / "README.md").exists()


# ==============================================================================
# TESTES DE INTEGRAÇÃO - EXECUÇÃO LIVRE & EDGE CASES
# ==============================================================================

def test_executar_comando_livre_real(repo_git_real):
    saida, sucesso = executar_comando_livre("git status", str(repo_git_real))
    assert sucesso is True
    assert "On branch" in saida or "Em branch" in saida


def test_edge_case_fora_de_repositorio_git(tmp_path, monkeypatch):
    pasta_vazia = tmp_path / "sem_git"
    pasta_vazia.mkdir()
    monkeypatch.chdir(pasta_vazia)

    # Deve falhar pois não há repositório .git aqui
    msg, sucesso = commit("Commit fantasma")
    assert sucesso is False
    assert "fatal:" in msg or "not a git repository" in msg