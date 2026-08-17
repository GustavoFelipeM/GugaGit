from unittest.mock import patch, MagicMock
from src.core.types import GitResult
from src.core.git.config import GitConfigService
from src.core.git.branch import BranchService
from src.core.git.history import HistoryService
from src.core.git.remote import RemoteService
from src.core.git.staging import StagingService
from src.core.git.stash import StashService
# -----------------------------------------------------------------------------
# obter_config_git
# -----------------------------------------------------------------------------

# Teste 1: obter_config_git quando as duas chamadas funcionam
@patch("src.core.git.config.interface_git")
def test_obter_config_git_sucesso(mock_interface):
    res_nome = MagicMock(returncode=0, stdout="Dev\n")
    res_email = MagicMock(returncode=0, stdout="dev@email.com\n")
    mock_interface.side_effect = [res_nome, res_email]

    res = GitConfigService().obter_config_git()

    assert isinstance(res, GitResult)
    assert res.sucesso is True
    assert res.dados == {
        "nome": "Dev",
        "email": "dev@email.com"
    }

# -----------------------------------------------------------------------------
# salvar_config_git
# -----------------------------------------------------------------------------

# Teste 2: salvar_config_git quando as duas chamadas funcionam
@patch("src.core.git.config.interface_git")
def test_salvar_config_git_sucesso(mock_interface):
    mock_interface.return_value = MagicMock(returncode=0)

    res = GitConfigService().salvar_config_git("Dev", "dev@email.com")

    assert res.sucesso is True
    assert res.mensagem == "Configurações de autoria atualizadas com sucesso!"
    assert mock_interface.call_count == 2

# Teste 3: salvar_config_git quando uma das chamadas falha
@patch("src.core.git.config.interface_git")
def test_salvar_config_git_falha(mock_interface):
    mock_interface.return_value = MagicMock(returncode=1, stderr="Erro no git config")

    res = GitConfigService().salvar_config_git("Dev", "dev@email.com")

    assert res.sucesso is False
    assert res.mensagem == "Erro ao salvar configurações."
    assert res.erro_detalhado == "Erro no git config"

# -----------------------------------------------------------------------------
# branch_atual
# -----------------------------------------------------------------------------

# Teste 4: branch_atual retorna o nome da branch atual
@patch("src.core.git.branch.interface_git")
def test_branch_atual_sucesso(mock_interface):
    mock_interface.return_value = MagicMock(returncode=0, stdout="main\n")

    res = BranchService().branch_atual()

    assert res.sucesso is True
    assert res.dados == "main"

# Teste 5: branch_atual retorna erro quando não é um repositório git
@patch("src.core.git.branch.interface_git")
def test_branch_atual_falha(mock_interface):
    mock_interface.return_value = MagicMock(returncode=1, stderr="fatal: not a git repository")

    res = BranchService().branch_atual()

    assert res.sucesso is False
    assert res.mensagem == "Não foi possível identificar a branch atual."
    assert res.erro_detalhado == "fatal: not a git repository"

# -----------------------------------------------------------------------------
# status
# -----------------------------------------------------------------------------

# Teste 6: status retorna o status do git
@patch("src.core.git.staging.interface_git")
def test_status_sucesso(mock_interface):
    mock_interface.return_value = MagicMock(
        returncode=0, 
        stdout="On branch main\nYour branch is up to date with 'origin/main'.\n"
    )

    res = StagingService().status()

    assert res.sucesso is True
    assert "On branch main" in res.dados

# -----------------------------------------------------------------------------
# fetch
# -----------------------------------------------------------------------------

# Teste 7: fetch retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.remote.executar_e_tratar")
def test_fetch_sucesso(mock_executar):
    mock_executar.return_value = ("Informações atualizadas!", True, "")

    res = RemoteService().fetch()

    assert res.sucesso is True
    assert res.mensagem == "Informações atualizadas!"

# Teste 8: fetch retorna a mensagem de erro quando a operação falha
@patch("src.core.git.remote.executar_e_tratar")
def test_fetch_falha(mock_executar):
    mock_executar.return_value = ("Erro de conexão", False, "error: could not fetch")

    res = RemoteService().fetch()

    assert res.sucesso is False
    assert res.mensagem == "Erro de conexão"
    assert res.erro_detalhado == "error: could not fetch"

# -----------------------------------------------------------------------------
# criar_branch
# -----------------------------------------------------------------------------

# Teste 9: criar_branch retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.branch.executar_e_tratar")
def test_criar_branch_sucesso(mock_executar):
    mock_executar.return_value = ("Branch 'feature/login' criada com sucesso!", True, "")

    res = BranchService().criar_branch("feature/login")

    assert res.sucesso is True
    assert res.mensagem == "Branch 'feature/login' criada com sucesso!"

# Teste 10: criar_branch retorna a mensagem de erro quando a operação falha
@patch("src.core.git.branch.executar_e_tratar")
def test_criar_branch_falha(mock_executar):
    mock_executar.return_value = ("Erro ao criar branch.", False, "fatal: A branch already exists")

    res = BranchService().criar_branch("feature/login")

    assert res.sucesso is False
    assert res.erro_detalhado == "fatal: A branch already exists"

# -----------------------------------------------------------------------------
# adicionar
# -----------------------------------------------------------------------------

# Teste 11: adicionar retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.staging.executar_e_tratar")
def test_adicionar_sucesso(mock_executar):
    mock_executar.return_value = ("Arquivos adicionados!", True, "")

    res = StagingService().adicionar_todos()

    assert res.sucesso is True
    assert res.mensagem == "Arquivos adicionados!"

# Teste 12: adicionar retorna a mensagem de erro quando a operação falha
@patch("src.core.git.staging.executar_e_tratar")
def test_adicionar_falha(mock_executar):
    mock_executar.return_value = ("Erro ao adicionar arquivos.", False, "error: could not add files")

    res = StagingService().adicionar_todos()

    assert res.sucesso is False
    assert res.erro_detalhado == "error: could not add files"

# -----------------------------------------------------------------------------
# commit
# -----------------------------------------------------------------------------

# Teste 13: commit retorna a mensagem de falha quando está vazio
def test_commit_mensagem_vazia():
    res = StagingService().commit("   ")

    assert res.sucesso is False
    assert res.mensagem == "A mensagem de commit não pode estar vazia."

# Teste 14: commit retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.staging.executar_e_tratar")
def test_commit_sucesso(mock_executar):
    mock_executar.return_value = ("Commit realizado!", True, "")

    res = StagingService().commit("Commit message")

    assert res.sucesso is True
    assert res.mensagem == "Commit realizado!"

# Teste 15: commit retorna a mensagem de erro quando a operação falha
@patch("src.core.git.staging.executar_e_tratar")
def test_commit_falha(mock_executar):
    mock_executar.return_value = ("Erro ao commitar.", False, "nothing to commit")

    res = StagingService().commit("Commit message")

    assert res.sucesso is False
    assert res.erro_detalhado == "nothing to commit"

# -----------------------------------------------------------------------------
# push
# -----------------------------------------------------------------------------

# Teste 16: push retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.remote.executar_e_tratar")
def test_push_sucesso(mock_executar):
    mock_executar.return_value = ("Push realizado com sucesso!", True, "")

    res = RemoteService().push("main")

    assert res.sucesso is True
    assert res.mensagem == "Push realizado com sucesso!"
    mock_executar.assert_called_once_with(["git", "push", "-u", "origin", "main"], "Push realizado com sucesso!")

# Teste 17: push retorna a mensagem de erro quando a operação falha
@patch("src.core.git.remote.executar_e_tratar")
def test_push_falha(mock_executar):
    mock_executar.return_value = ("Push rejeitado: Faça pull antes.", False, "error: failed to push")

    res = RemoteService().push("main")

    assert res.sucesso is False
    assert res.erro_detalhado == "error: failed to push"

# -----------------------------------------------------------------------------
# listar_branches
# -----------------------------------------------------------------------------

# Teste 18: listar_branches limpando os caracteres de branch ativa '*'
@patch("src.core.git.branch.interface_git")
def test_listar_branches_sucesso(mock_interface):
    mock_interface.return_value = MagicMock(returncode=0, stdout="* main\n  feature/login\n  hotfix/bug")

    res = BranchService().listar_branches()

    assert res.sucesso is True
    assert res.dados == ["main", "feature/login", "hotfix/bug"]

# Teste 19: listar_branches retorna lista vazia quando a operação falha
@patch("src.core.git.branch.interface_git")
def test_listar_branches_falha(mock_interface):
    mock_interface.return_value = MagicMock(returncode=1, stderr="error: could not list branches")

    res = BranchService().listar_branches()

    assert res.sucesso is False
    assert res.erro_detalhado == "error: could not list branches"

# -----------------------------------------------------------------------------
# trocar_branch
# -----------------------------------------------------------------------------

# Teste 20: trocar_branch retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.branch.executar_e_tratar")
def test_trocar_branch_sucesso(mock_executar):
    mock_executar.return_value = ("Trocado para a branch 'feature/login' com sucesso!", True, "")

    res = BranchService().trocar_branch("feature/login")

    assert res.sucesso is True
    assert res.mensagem == "Trocado para a branch 'feature/login' com sucesso!"

# Teste 21: trocar_branch retorna a mensagem de erro quando a operação falha
@patch("src.core.git.branch.executar_e_tratar")
def test_trocar_branch_falha(mock_executar):
    mock_executar.return_value = ("Troca cancelada: alteração local pendente.", False, "error: Your local changes...")

    res = BranchService().trocar_branch("feature/login")

    assert res.sucesso is False
    assert res.erro_detalhado == "error: Your local changes..."

# -----------------------------------------------------------------------------
# pull
# -----------------------------------------------------------------------------

# Teste 22: pull retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.remote.executar_e_tratar")
def test_pull_sucesso(mock_executar):
    mock_executar.return_value = ("Pull feito com sucesso!", True, "")

    res = RemoteService().pull()

    assert res.sucesso is True
    assert res.mensagem == "Pull feito com sucesso!"

# Teste 23: pull retorna a mensagem de erro quando a operação falha
@patch("src.core.git.remote.executar_e_tratar")
def test_pull_falha(mock_executar):
    mock_executar.return_value = ("Erro ao fazer pull", False, "error: could not pull")

    res = RemoteService().pull()

    assert res.sucesso is False
    assert res.erro_detalhado == "error: could not pull"

# -----------------------------------------------------------------------------
# clonar_repositorio
# -----------------------------------------------------------------------------

# Teste 24: clonar_repositorio retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("subprocess.run")
def test_clonar_repositorio_sucesso(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="Cloning into 'repo'...\n")

    res = RemoteService().clonar_repositorio("github.com:user/repo.git", "repo")

    assert res.sucesso is True
    assert res.mensagem == "Repositório clonado com sucesso!"

# Teste 25: clonar_repositorio retorna a mensagem de erro quando a operação falha
@patch("subprocess.run")
def test_clonar_repositorio_falha(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stderr="error: could not clone repository")

    res = RemoteService().clonar_repositorio("github.com:user/repo.git", "repo")

    assert res.sucesso is False
    assert res.erro_detalhado == "error: could not clone repository"

# -----------------------------------------------------------------------------
# restaurar_alteracoes
# -----------------------------------------------------------------------------

# Teste 26: restaurar_alteracoes retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.staging.executar_e_tratar")
def test_restaurar_alteracoes_sucesso(mock_executar):
    mock_executar.return_value = ("Desfeito com sucesso!", True, "")

    res = StagingService().restaurar_alteracoes()

    assert res.sucesso is True
    assert res.mensagem == "Desfeito com sucesso!"

# Teste 27: restaurar_alteracoes retorna a mensagem de erro quando a operação falha
@patch("src.core.git.staging.executar_e_tratar")
def test_restaurar_alteracoes_falha(mock_executar):
    mock_executar.return_value = ("Erro ao restaurar", False, "error: could not restore")

    res = StagingService().restaurar_alteracoes()

    assert res.sucesso is False
    assert res.erro_detalhado == "error: could not restore"

# -----------------------------------------------------------------------------
# deletar_branch
# -----------------------------------------------------------------------------

# Teste 28: deletar_branch retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.branch.executar_e_tratar")
def test_deletar_branch_sucesso(mock_executar):
    mock_executar.return_value = ("Branch 'feature/login' deletada!", True, "")

    res = BranchService().deletar_branch("feature/login")

    assert res.sucesso is True
    assert res.mensagem == "Branch 'feature/login' deletada!"
    mock_executar.assert_called_once_with(["git", "branch", "-d", "feature/login"], "Branch 'feature/login' deletada!")

# Teste 29: deletar_branch retorna a mensagem de erro quando a operação falha
@patch("src.core.git.branch.executar_e_tratar")
def test_deletar_branch_falha(mock_executar):
    mock_executar.return_value = ("Erro ao deletar branch", False, "error: branch not found")

    res = BranchService().deletar_branch("feature/login")

    assert res.sucesso is False
    assert res.erro_detalhado == "error: branch not found"

# -----------------------------------------------------------------------------
# remover_staging
# -----------------------------------------------------------------------------

# Teste 30: remover_staging retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.staging.executar_e_tratar")
def test_remover_staging_sucesso(mock_executar):
    mock_executar.return_value = ("Staging removido com sucesso!", True, "")

    res = StagingService().remover_staging_todos()

    assert res.sucesso is True
    assert res.mensagem == "Staging removido com sucesso!"

# Teste 31: remover_staging retorna a mensagem de erro quando a operação falha
@patch("src.core.git.staging.executar_e_tratar")
def test_remover_staging_falha(mock_executar):
    mock_executar.return_value = ("Erro ao remover staging", False, "error: could not remove staging")

    res = StagingService().remover_staging_todos()

    assert res.sucesso is False
    assert res.erro_detalhado == "error: could not remove staging"

# -----------------------------------------------------------------------------
# historico
# -----------------------------------------------------------------------------

# Teste 32: historico retorna o histórico de commits quando a operação é bem-sucedida
@patch("src.core.git.history.interface_git")
def test_historico_sucesso(mock_interface):
    mock_interface.return_value = MagicMock(returncode=0, stdout="commit abc123\nAuthor: Dev\n")

    res = HistoryService().historico()

    assert res.sucesso is True
    assert "commit abc123" in res.dados

# Teste 33: historico retorna None quando a operação falha
@patch("src.core.git.history.interface_git")
def test_historico_falha(mock_interface):
    mock_interface.return_value = MagicMock(returncode=1, stderr="error: could not retrieve log")

    res = HistoryService().historico()

    assert res.sucesso is False
    assert res.erro_detalhado == "error: could not retrieve log"

# -----------------------------------------------------------------------------
# diff
# -----------------------------------------------------------------------------

# Teste 34: diff retorna o diff quando a operação é bem-sucedida
@patch("src.core.git.staging.interface_git")
def test_diff_sucesso(mock_interface):
    mock_interface.return_value = MagicMock(returncode=0, stdout="diff --git a/file.txt b/file.txt\n")

    res = StagingService().diff()

    assert res.sucesso is True
    assert "diff --git" in res.dados

# Teste 35: diff retorna None quando a operação falha
@patch("src.core.git.staging.interface_git")
def test_diff_falha(mock_interface):
    mock_interface.return_value = MagicMock(returncode=1, stderr="error: diff failed")

    res = StagingService().diff()

    assert res.sucesso is False
    assert res.erro_detalhado == "error: diff failed"

# -----------------------------------------------------------------------------
# TESTES COMPLEMENTARES DE DIFF
# -----------------------------------------------------------------------------

# Teste: git diff --staged
@patch("src.core.git.staging.interface_git")
def test_diff_staged_sucesso(mock_interface):
    mock_interface.return_value = MagicMock(returncode=0, stdout="diff --git a/staged.txt b/staged.txt\n")

    res = StagingService().diff(staged=True)

    assert res.sucesso is True
    assert "staged.txt" in res.dados
    mock_interface.assert_called_once_with(["git", "diff", "--staged"])

# Teste: git diff para arquivo individual
@patch("src.core.git.staging.interface_git")
def test_diff_arquivo_especifico_sucesso(mock_interface):
    mock_interface.return_value = MagicMock(returncode=0, stdout="diff --git a/main.py b/main.py\n")

    res = StagingService().diff(staged=False, caminho="main.py")

    assert res.sucesso is True
    assert "main.py" in res.dados
    mock_interface.assert_called_once_with(["git", "diff", "--", "main.py"])

# Teste: contagem estatística de alterações (--numstat)
@patch("src.core.git.staging.interface_git")
def test_obter_estatisticas_alteracoes_sucesso(mock_interface):
    res_wt = MagicMock(returncode=0, stdout="10\t2\tmain.py\n")
    res_st = MagicMock(returncode=0, stdout="4\t0\tconfig.py\n")
    mock_interface.side_effect = [res_wt, res_st]

    res = StagingService().obter_estatisticas_alteracoes()

    assert res.sucesso is True
    assert res.dados["main.py"] == 12  # 10 + 2
    assert res.dados["config.py"] == 4   # 4 + 0

# -----------------------------------------------------------------------------
# stash
# -----------------------------------------------------------------------------

# Teste 36: stash retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.stash.executar_e_tratar")
def test_stash_sucesso(mock_executar):
    mock_executar.return_value = ("Alterações guardadas no stash!", True, "")

    res = StashService().stash()

    assert res.sucesso is True
    assert res.mensagem == "Alterações guardadas no stash!"

# Teste 37: stash retorna a mensagem de erro quando a operação falha
@patch("src.core.git.stash.executar_e_tratar")
def test_stash_falha(mock_executar):
    mock_executar.return_value = ("error: could not stash changes", False, "")
    
    res = StashService().stash()
    
    assert res.sucesso is False
    assert res.mensagem == "error: could not stash changes"

# Teste 38: stash_pop retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.stash.executar_e_tratar")
def test_stash_pop_sucesso(mock_executar):
    mock_executar.return_value = ("Stash aplicado!", True, "")

    res = StashService().stash_pop()

    assert res.sucesso is True
    assert res.mensagem == "Stash aplicado!"

# Teste 39: stash_pop retorna a mensagem de erro quando a operação falha
@patch("src.core.git.stash.executar_e_tratar")
def test_stash_pop_falha(mock_executar):
    mock_executar.return_value = ("error: could not apply stash", False, "")
    
    res = StashService().stash_pop()
    
    assert res.sucesso is False
    assert res.mensagem == "error: could not apply stash"

# Teste 40: listar_stash retorna a lista de stashes quando a operação é bem-sucedida
@patch("src.core.git.stash.interface_git")
def test_listar_stash_sucesso(mock_interface):
    mock_interface.return_value = MagicMock(returncode=0, stdout="stash@{0}: WIP on main\n")

    res = StashService().listar_stash()

    assert res.sucesso is True
    assert "stash@{0}" in res.dados

# Teste 41: listar_stash retorna False quando a operação falha
@patch("src.core.git.stash.interface_git")
def test_listar_stash_falha(mock_interface):
    mock_interface.return_value = MagicMock(returncode=1, stderr="error: could not list stash")

    res = StashService().listar_stash()

    assert res.sucesso is False
    assert res.dados is None
    assert "error: could not list stash" in res.erro_detalhado

# -----------------------------------------------------------------------------
# merge
# -----------------------------------------------------------------------------

# Teste 42: merge retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git.branch.executar_e_tratar")
def test_merge_sucesso(mock_executar):
    mock_executar.return_value = ("Merge de 'feature/login' realizado com sucesso!", True, "")

    res = BranchService().merge("feature/login")

    assert res.sucesso is True
    assert res.mensagem == "Merge de 'feature/login' realizado com sucesso!"

# Teste 43: merge retorna a mensagem de erro quando a operação falha
@patch("src.core.git.branch.executar_e_tratar")
def test_merge_falha(mock_executar):
    mock_executar.return_value = ("Erro ao realizar merge", False, "error: could not merge")

    res = BranchService().merge("feature/login")

    assert res.sucesso is False
    assert res.erro_detalhado == "error: could not merge"

# -----------------------------------------------------------------------------
# listar_tags
# -----------------------------------------------------------------------------

# Teste 44: listar_tags retorna a lista de tags quando a operação é bem-sucedida
@patch("src.core.git.history.interface_git")
def test_listar_tags_sucesso(mock_interface):
    mock_interface.return_value = MagicMock(returncode=0, stdout="v1.0.0\nv1.1.0\n")

    res = HistoryService().listar_tags()

    assert res.sucesso is True
    assert "v1.0.0" in res.dados

# Teste 45: listar_tags retorna False quando a operação falha
@patch("src.core.git.history.interface_git")
def test_listar_tags_falha(mock_interface):
    mock_interface.return_value = MagicMock(returncode=1, stderr="error: could not list tags")

    res = HistoryService().listar_tags()

    assert res.sucesso is False
    assert res.dados is None  # Em caso de falha, dados deve ser None
    assert "error: could not list tags" in res.erro_detalhado

# -----------------------------------------------------------------------------
# obter_arquivos_status
# -----------------------------------------------------------------------------

# Teste 46: obter_arquivos_status retorna a lista de arquivos com status quando a operação é bem-sucedida
@patch("src.core.git.staging.interface_git")
def test_obter_arquivos_status_sucesso(mock_interface):
    mock_interface.return_value = MagicMock(
        returncode=0, 
        stdout=" M file1.txt\nM  file2.txt\n?? file3.txt\n"
    )

    res = StagingService().obter_arquivos_status()

    assert res.sucesso is True
    assert len(res.dados) == 3
    assert res.dados[0]["caminho"] == "file1.txt"
    assert res.dados[0]["staged"] is False
    assert res.dados[1]["staged"] is True

# Teste 47: obter_arquivos_status retorna lista vazia quando não há arquivos modificados
@patch("src.core.git.staging.interface_git")
def test_obter_arquivos_status_vazio(mock_interface):
    mock_interface.return_value = MagicMock(returncode=0, stdout="")

    res = StagingService().obter_arquivos_status()

    assert res.sucesso is True
    assert res.dados == []

# -----------------------------------------------------------------------------
# adicionar_arquivos_staging & remover_selecionados_staging
# -----------------------------------------------------------------------------

# Teste 48: adicionar_arquivos_staging retorna sucesso quando a lista de arquivos está vazia
def test_adicionar_arquivos_staging_vazio():
    res = StagingService().adicionar_selecionados([])

    assert res.sucesso is True
    assert res.mensagem == "Nenhum arquivo selecionado."

# Teste 49: adicionar_arquivos_staging retorna sucesso quando a operação é bem-sucedida
@patch("src.core.git.staging.executar_e_tratar")
def test_adicionar_arquivos_staging_sucesso(mock_executar):
    mock_executar.return_value = ("Arquivos selecionados adicionados ao staging!", True, "")

    res = StagingService().adicionar_selecionados(["file1.txt", "file2.txt"])

    assert res.sucesso is True
    mock_executar.assert_called_once_with(
        ["git", "add", "file1.txt", "file2.txt"], 
        "Arquivos selecionados adicionados ao staging!"
    )

# Teste 50: remover_selecionados_staging retorna sucesso quando a lista de arquivos está vazia
def test_remover_selecionados_staging_vazio():
    res = StagingService().remover_staging_selecionados([])

    assert res.sucesso is True
    assert res.mensagem == "Nenhum arquivo selecionado."

# Teste 51: remover_selecionados_staging retorna sucesso quando a operação é bem-sucedida
@patch("src.core.git.staging.executar_e_tratar")
def test_remover_selecionados_staging_sucesso(mock_executar):
    mock_executar.return_value = ("Arquivos removidos do staging!", True, "")

    res = StagingService().remover_staging_selecionados(["file1.txt"])

    assert res.sucesso is True
    mock_executar.assert_called_once_with(
        ["git", "restore", "--staged", "file1.txt"], 
        "Arquivos removidos do staging!"
    )