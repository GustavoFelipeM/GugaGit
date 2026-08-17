import os
import subprocess
import pytest
from src.core.git.config import GitConfigService
from src.core.git.branch import BranchService
from src.core.git.history import HistoryService
from src.core.git.remote import RemoteService
from src.core.git.staging import StagingService
from src.core.git.stash import StashService
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

    res_b = BranchService().branch_atual()
    b_nome = res_b.dados if res_b.sucesso else "master"
    subprocess.run(["git", "push", "-u", "origin", b_nome], check=True, cwd=local_dir, capture_output=True)

    return {
        "bare_path": str(bare_dir),
        "local_dir": local_dir,
        "branch": b_nome
    }


# ==============================================================================
# TESTES DE INTEGRAÇÃO - CONFIGURAÇÃO & INSTALAÇÃO
# ==============================================================================

def test_git_instalado_real():
    assert git_instalado() is True


def test_salvar_e_obter_config_git_real(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    res_salvar = GitConfigService().salvar_config_git("Guga Dev", "guga@dev.com")
    assert res_salvar.sucesso is True
    assert "com sucesso" in res_salvar.mensagem.lower()

    res_config = GitConfigService().obter_config_git()
    assert res_config.sucesso is True
    # Os dados da configuração estão no atributo .dados
    assert res_config.dados["nome"] == "Guga Dev" or res_config.dados.get("name") == "Guga Dev"
    assert res_config.dados["email"] == "guga@dev.com"


# ==============================================================================
# TESTES DE INTEGRAÇÃO - FLUXO DE TRABALHO LOCAL
# ==============================================================================

def test_branch_atual_e_listar_branches_real(repo_git_real):
    res_b = BranchService().branch_atual()
    assert res_b.sucesso is True
    assert res_b.dados in ["main", "master"]

    res_list = BranchService().listar_branches()
    assert res_list.sucesso is True
    assert isinstance(res_list.dados, list)
    assert res_b.dados in res_list.dados


def test_fluxo_criar_trocar_e_deletar_branch_real(repo_git_real):
    nova_branch = "feature/login"

    # Criar branch
    res_criar = BranchService().criar_branch(nova_branch)
    assert res_criar.sucesso is True
    assert BranchService().branch_atual().dados == nova_branch

    # Trocar para branch principal
    list_b = BranchService().listar_branches().dados
    b_principal = "main" if "main" in list_b else "master"
    res_trocar = BranchService().trocar_branch(b_principal)
    assert res_trocar.sucesso is True
    assert BranchService().branch_atual().dados == b_principal

    # Deletar branch criada
    res_del = BranchService().deletar_branch(nova_branch)
    assert res_del.sucesso is True
    assert nova_branch not in BranchService().listar_branches().dados


def test_fluxo_adicionar_commit_e_historico_real(repo_git_real):
    novo_arquivo = repo_git_real / "novo.txt"
    novo_arquivo.write_text("linha 1\n", encoding="utf-8")

    # Adicionar
    res_add = StagingService().adicionar_todos()
    assert res_add.sucesso is True

    # Commit
    res_commit = StagingService().commit("Adiciona novo.txt")
    assert res_commit.sucesso is True

    # Historico (Log)
    res_hist = HistoryService().historico()
    assert res_hist.sucesso is True
    assert res_hist.dados is not None
    assert "Adiciona novo.txt" in str(res_hist.dados)


def test_status_e_diff_real(repo_git_real):
    # Altera arquivo existente
    arquivo_init = repo_git_real / "init.txt"
    arquivo_init.write_text("commit inicial - alterado", encoding="utf-8")

    res_status = StagingService().status()
    assert res_status.sucesso is True
    status_str = str(res_status.dados)
    assert "modified:" in status_str or "modificado:" in status_str

    res_diff = StagingService().diff()
    assert res_diff.sucesso is True
    diff_str = str(res_diff.dados)
    assert "-commit inicial" in diff_str
    assert "+commit inicial - alterado" in diff_str


def test_remover_staging_e_restaurar_alteracoes_real(repo_git_real):
    arquivo = repo_git_real / "init.txt"
    arquivo.write_text("alteracao temporaria", encoding="utf-8")

    # Adiciona ao staging
    res_add = StagingService().adicionar_todos()
    res_status = StagingService().status()
    status_str = str(res_status.dados)
    assert "Changes to be committed" in status_str or "Mudanças a serem submetidas" in status_str

    # Remove do staging
    res_unstage = StagingService().remover_staging_todos()
    assert res_unstage.sucesso is True

    # Restaura arquivo
    res_restore = StagingService().restaurar_alteracoes()
    assert res_restore.sucesso is True
    assert arquivo.read_text(encoding="utf-8") == "commit inicial"


def test_stash_fluxo_completo_real(repo_git_real):
    arquivo = repo_git_real / "init.txt"
    arquivo.write_text("alteracao antes do stash", encoding="utf-8")

    # Stash
    res_stash = StashService().stash()
    assert res_stash.sucesso is True
    assert arquivo.read_text(encoding="utf-8") == "commit inicial"

    # Listar Stash
    res_list = StashService().listar_stash()
    assert res_list.sucesso is True
    assert "WIP on" in str(res_list.dados)

    # Stash Pop
    res_pop = StashService().stash_pop()
    assert res_pop.sucesso is True
    assert arquivo.read_text(encoding="utf-8") == "alteracao antes do stash"


def test_merge_branches_real(repo_git_real):
    res_b = BranchService().branch_atual()
    b_base = res_b.dados

    # Cria branch paralela
    BranchService().criar_branch("feature/calc")
    BranchService().trocar_branch("feature/calc")
    (repo_git_real / "calc.py").write_text("print(1+1)", encoding="utf-8")
    StagingService().adicionar_todos()
    StagingService().commit("Adiciona calculadora")

    # Volta para base e faz o merge
    BranchService().trocar_branch(b_base)
    res_merge = BranchService().merge("feature/calc")

    assert res_merge.sucesso is True
    assert (repo_git_real / "calc.py").exists()


def test_listar_tags_real(repo_git_real):
    # Cria tag usando comando livre
    executar_comando_livre("git tag v1.0.0", str(repo_git_real))

    res_tags = HistoryService().listar_tags()
    assert res_tags.sucesso is True
    assert res_tags.dados is not None
    assert "v1.0.0" in str(res_tags.dados)


# ==============================================================================
# TESTES DE INTEGRAÇÃO - SINCRONIZAÇÃO E REMOTO
# ==============================================================================

def test_push_fetch_e_pull_real(setup_remoto):
    local_dir = setup_remoto["local_dir"]
    branch = setup_remoto["branch"]

    # Cria novo commit local
    (local_dir / "remoto.txt").write_text("dados remotos", encoding="utf-8")
    StagingService().adicionar_todos()
    StagingService().commit("Commit para o remote")

    # Push
    res_push = RemoteService().push(branch)
    assert res_push.sucesso is True

    # Fetch
    res_fetch = RemoteService().fetch()
    assert res_fetch.sucesso is True

    # Pull
    res_pull = RemoteService().pull()
    assert res_pull.sucesso is True


def test_clonar_repositorio_real(setup_remoto, tmp_path):
    pasta_destino = tmp_path / "clone_destino"
    pasta_destino.mkdir()

    res_clone = RemoteService().clonar_repositorio(setup_remoto["bare_path"], str(pasta_destino))
    assert res_clone.sucesso is True

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
    res = StagingService().commit("Commit fantasma")
    assert res.sucesso is False
    msg = res.mensagem or (res.erro_detalhado if hasattr(res, "erro_detalhado") else "")
    assert "fatal:" in msg or "not a git repository" in msg or res.sucesso is False


def test_staging_seletivo_e_obter_status_real(repo_git_real):
    # Criar dois arquivos diferentes
    arq1 = repo_git_real / "arquivo1.txt"
    arq2 = repo_git_real / "arquivo2.txt"
    arq1.write_text("conteudo 1", encoding="utf-8")
    arq2.write_text("conteudo 2", encoding="utf-8")

    # Verificar se o status detecta os 2 arquivos não staged
    res_status = StagingService().obter_arquivos_status()
    assert res_status.sucesso is True
    caminhos = [item["caminho"] for item in res_status.dados]
    assert "arquivo1.txt" in caminhos
    assert "arquivo2.txt" in caminhos

    # Adicionar APENAS o arquivo1 ao Staging
    res_add = StagingService().adicionar_selecionados(["arquivo1.txt"])
    assert res_add.sucesso is True

    # Confirmar que apenas o arquivo1 está staged
    res_status_pos = StagingService().obter_arquivos_status()
    for item in res_status_pos.dados:
        if item["caminho"] == "arquivo1.txt":
            assert item["staged"] is True
        elif item["caminho"] == "arquivo2.txt":
            assert item["staged"] is False

    # Remover arquivo1 do Staging
    res_unstage = StagingService().remover_staging_selecionados(["arquivo1.txt"])
    assert res_unstage.sucesso is True

def test_push_e_fetch_em_remoto_invalido_real(repo_git_real):
    # Adiciona um remote apontando para um caminho inexistente
    subprocess.run(["git", "remote", "add", "origin", "https://servidor-que-nao-existe.com/repo.git"], check=True, cwd=repo_git_real)

    # Fetch deve falhar graciosamente sem quebrar a aplicação
    res_fetch = RemoteService().fetch()
    assert res_fetch.sucesso is False
    assert res_fetch.erro_detalhado != ""

# -----------------------------------------------------------------------------
# TESTES DE INTEGRAÇÃO REAL DE DIFF E ARQUIVOS (NOVOS/DELETADOS/STAGED)
# -----------------------------------------------------------------------------

def test_diff_staged_e_working_tree_separados_real(repo_git_real):
    arquivo = repo_git_real / "init.txt"
    
    # 1. Alteração no Working Tree
    arquivo.write_text("linha working tree\n", encoding="utf-8")
    res_wt = StagingService().diff(staged=False)
    assert "+linha working tree" in str(res_wt.dados)

    # 2. Mover para o Staging
    StagingService().adicionar_todos()
    res_st = StagingService().diff(staged=True)
    assert "+linha working tree" in str(res_st.dados)


def test_diff_arquivo_novo_untracked_real(repo_git_real):
    novo_arq = repo_git_real / "novo_arquivo.py"
    novo_arq.write_text("print('novo')\n", encoding="utf-8")

    # Testa o diff direto no arquivo novo que ainda não está no git
    res_diff = StagingService().diff(caminho="novo_arquivo.py")
    assert res_diff.sucesso is True
    assert "print('novo')" in str(res_diff.dados)


def test_diff_arquivo_deletado_real(repo_git_real):
    arquivo = repo_git_real / "init.txt"
    arquivo.unlink()  # Deleta o arquivo físico

    res_diff = StagingService().diff(caminho="init.txt")
    assert res_diff.sucesso is True
    assert "-commit inicial" in str(res_diff.dados)


def test_estatisticas_contagem_alteracoes_real(repo_git_real):
    arquivo = repo_git_real / "init.txt"
    arquivo.write_text("linha 1\nlinha 2\nlinha 3\n", encoding="utf-8")

    res_stats = StagingService().obter_estatisticas_alteracoes()
    assert res_stats.sucesso is True
    assert "init.txt" in res_stats.dados
    assert res_stats.dados["init.txt"] > 0