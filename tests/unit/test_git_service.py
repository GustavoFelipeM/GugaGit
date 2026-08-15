from unittest.mock import patch, MagicMock
from src.core.git_service import adicionar, branch_atual, clonar_repositorio, commit, criar_branch, diff, fetch, obter_config_git, pull, pull, push, remover_staging, restaurar_alteracoes, salvar_config_git, listar_branches, status, deletar_branch, historico, stash, stash_pop, listar_stash, merge, listar_tags, trocar_branch

# -----------------------------------------------------------------------------
# obter_config_git
# -----------------------------------------------------------------------------

# Teste 1: obter_config_git quando as duas chamadas funcionam
@patch("src.core.git_service.interface_git")
def test_obter_config_git_sucesso(mock_interface):
    res_nome = MagicMock()
    res_nome.returncode = 0
    res_nome.stdout = "Dev\n"

    res_email = MagicMock()
    res_email.returncode = 0
    res_email.stdout = "dev@email.com\n"

    mock_interface.side_effect = [res_nome, res_email]

    config = obter_config_git()

    assert config == {
        "nome": "Dev",
        "email": "dev@email.com"
    }

# -----------------------------------------------------------------------------
# salvar_config_git
# -----------------------------------------------------------------------------

# Teste 2: salvar_config_git quando as duas chamadas funcionam
@patch("src.core.git_service.interface_git")
def test_salvar_config_git_sucesso(mock_interface):
    res_sucesso = MagicMock()
    res_sucesso.returncode = 0
    mock_interface.return_value = res_sucesso

    msg, sucesso = salvar_config_git("Dev", "dev@email.com")
    assert sucesso is True
    assert msg == "Configurações de autoria atualizadas com sucesso!"
    assert mock_interface.call_count == 2

# Teste 3: salvar_config_git quando uma das chamadas falha
@patch("src.core.git_service.interface_git")
def test_salvar_config_git_falha(mock_interface):
    res_falha = MagicMock()
    res_falha.returncode = 1
    mock_interface.return_value = res_falha

    msg, sucesso = salvar_config_git("Dev", "dev@email.com")
    assert sucesso is False
    assert msg == "Erro ao salvar configurações."
    assert mock_interface.call_count == 2

# -----------------------------------------------------------------------------
# branch_atual
# -----------------------------------------------------------------------------

# Teste 4: branch_atual retorna o nome da branch atual
@patch("src.core.git_service.interface_git")
def test_branch_atual(mock_interface):
    res_branch = MagicMock()
    res_branch.returncode = 0
    res_branch.stdout = "main\n"
    mock_interface.return_value = res_branch

    branch = branch_atual()
    assert branch == "main"

# -----------------------------------------------------------------------------
# status
# -----------------------------------------------------------------------------

# Teste 5: status retorna o status do git
@patch("src.core.git_service.interface_git")
def test_status(mock_interface):
    res_status = MagicMock()
    res_status.returncode = 0
    res_status.stdout = "On branch main\nYour branch is up to date with 'origin/main'.\n"
    mock_interface.return_value = res_status

    status_output = status()
    assert "On branch main" in status_output
    assert "Your branch is up to date with 'origin/main'." in status_output

# -----------------------------------------------------------------------------
# fetch
# -----------------------------------------------------------------------------

# Teste 6: fetch retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_fetch_sucesso(mock_interface):
    res_fetch = MagicMock()
    res_fetch.returncode = 0
    res_fetch.stdout = "Fetching origin\n"
    mock_interface.return_value = res_fetch

    msg, sucesso = fetch()
    assert msg == "Informações atualizadas!"
    assert sucesso is True

# Teste 7: fetch retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_fetch_falha(mock_interface):
    res_fetch = MagicMock()
    res_fetch.returncode = 1
    res_fetch.stderr = "error: could not fetch"
    mock_interface.return_value = res_fetch

    msg, sucesso = fetch()
    
    assert msg == "error: could not fetch"
    assert sucesso is False

# -----------------------------------------------------------------------------
# criar_branch
# -----------------------------------------------------------------------------

# Teste 8: criar_branch retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_criar_branch_sucesso(mock_interface):
    res_branch = MagicMock()
    res_branch.returncode = 0
    res_branch.stdout = "Switched to a new branch 'feature/login'\n"
    mock_interface.return_value = res_branch

    msg, sucesso = criar_branch("feature/login")
    assert msg == "Branch criada!"
    assert sucesso is True

# Teste 9: criar_branch retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_criar_branch_falha(mock_interface):
    res_branch = MagicMock()
    res_branch.returncode = 1
    res_branch.stderr = "error: could not create branch"
    mock_interface.return_value = res_branch

    msg, sucesso = criar_branch("feature/login")
    
    assert msg == "error: could not create branch"
    assert sucesso is False

# -----------------------------------------------------------------------------
# adicionar
# -----------------------------------------------------------------------------

# Teste 10: adicionar retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_adicionar_sucesso(mock_interface):
    res_add = MagicMock()
    res_add.returncode = 0
    res_add.stdout = "Changes to be committed:\n  (use \"git restore --staged <file>...\" to unstage)\n\n\tnew file:   test_file.txt\n"
    mock_interface.return_value = res_add

    msg, sucesso = adicionar()
    assert msg == "Arquivos adicionados!"
    assert sucesso is True

# Teste 11: adicionar retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_adicionar_falha(mock_interface):
    res_add = MagicMock()
    res_add.returncode = 1
    res_add.stderr = "error: could not add files"
    mock_interface.return_value = res_add

    msg, sucesso = adicionar()
    
    assert msg == "error: could not add files"
    assert sucesso is False

# -----------------------------------------------------------------------------
# commit
# -----------------------------------------------------------------------------

# Teste 12: commit retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_commit_sucesso(mock_interface):
    res_commit = MagicMock()
    res_commit.returncode = 0
    res_commit.stdout = "[main 1a2b3c4] Commit message\n 1 file changed, 1 insertion(+)\n"
    mock_interface.return_value = res_commit

    msg, sucesso = commit("Commit message")
    assert msg == "Commit realizado!"
    assert sucesso is True

# Teste 13: commit retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_commit_falha(mock_interface):
    res_commit = MagicMock()
    res_commit.returncode = 1
    res_commit.stderr = "error: could not commit"
    mock_interface.return_value = res_commit

    msg, sucesso = commit("Commit message")
    
    assert msg == "error: could not commit"
    assert sucesso is False

# -----------------------------------------------------------------------------
# push
# -----------------------------------------------------------------------------

# Teste 14: push retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_push_sucesso(mock_interface):
    res_push = MagicMock()
    res_push.returncode = 0
    res_push.stdout = "To github.com:user/repo.git\n   abc123..def456  main -> main\n"
    mock_interface.return_value = res_push

    msg, sucesso = push("main")

    assert msg == "Push realizado com sucesso!"
    assert sucesso is True

    mock_interface.assert_called_once_with(["git", "push", "-u", "origin", "main"])

# Teste 15: push retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_push_falha(mock_interface):
    res_push = MagicMock()
    res_push.returncode = 1
    res_push.stderr = "error: could not push"
    mock_interface.return_value = res_push

    msg, sucesso = push("main")
    
    assert msg == "error: could not push"
    assert sucesso is False

# -----------------------------------------------------------------------------
# listar_branches
# -----------------------------------------------------------------------------

# Teste 16: listar_branches limpando os caracteres de branch ativa '*'
@patch("src.core.git_service.interface_git")
def test_listar_branches_sucesso(mock_interface):
    res_fake = MagicMock()
    res_fake.returncode = 0

    res_fake.stdout = "* main\n  feature/login\n  hotfix/bug"
    mock_interface.return_value = res_fake

    branches = listar_branches()
    assert branches == ["main", "feature/login", "hotfix/bug"]

# Teste 17: listar_branches retorna lista vazia quando a operação falha
@patch("src.core.git_service.interface_git")
def test_listar_branches_falha(mock_interface):
    res_fake = MagicMock()
    res_fake.returncode = 1
    res_fake.stderr = "error: could not list branches"
    mock_interface.return_value = res_fake

    branches = listar_branches()
    
    assert branches == None

# -----------------------------------------------------------------------------
# trocar_branch
# -----------------------------------------------------------------------------

# Teste 18: trocar_branch retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_trocar_branch_sucesso(mock_interface):
    res_checkout = MagicMock()
    res_checkout.returncode = 0
    res_checkout.stdout = "Switched to branch 'feature/login'\n"
    mock_interface.return_value = res_checkout

    msg, sucesso = trocar_branch("feature/login")
    assert msg == "Branch trocado com sucesso!"
    assert sucesso is True

# Teste 19: trocar_branch retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_trocar_branch_falha(mock_interface):
    res_checkout = MagicMock()
    res_checkout.returncode = 1
    res_checkout.stderr = "error: could not switch branch"
    mock_interface.return_value = res_checkout

    msg, sucesso = trocar_branch("feature/login")
    
    assert msg == "error: could not switch branch"
    assert sucesso is False

# -----------------------------------------------------------------------------
# pull
# -----------------------------------------------------------------------------

# Teste 20: pull retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_pull_sucesso(mock_interface):
    res_pull = MagicMock()
    res_pull.returncode = 0
    res_pull.stdout = "Updating abc123..def456\nFast-forward\n file.txt | 1 +\n 1 file changed, 1 insertion(+)\n"
    mock_interface.return_value = res_pull

    msg, sucesso = pull()
    assert msg == "Pull feito com sucesso!"
    assert sucesso is True

# Teste 21: pull retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_pull_falha(mock_interface):
    res_pull = MagicMock()
    res_pull.returncode = 1
    res_pull.stderr = "error: could not pull"
    mock_interface.return_value = res_pull

    msg, sucesso = pull()
    
    assert msg == "error: could not pull"
    assert sucesso is False

# -----------------------------------------------------------------------------
# clonar_repositorio
# -----------------------------------------------------------------------------

# Teste 22: clonar_repositorio retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("subprocess.run")
def test_clonar_repositorio_sucesso(mock_interface):
    res_clone = MagicMock()
    res_clone.returncode = 0
    res_clone.stdout = "Cloning into 'repo'...\n"
    mock_interface.return_value = res_clone

    msg, sucesso = clonar_repositorio("github.com:user/repo.git", "repo")
    assert msg == "Repositorio clonado com sucesso!"
    assert sucesso is True

# Teste 23: clonar_repositorio retorna a mensagem de erro quando a operação falha
@patch("subprocess.run")
def test_clonar_repositorio_falha(mock_interface):
    res_clone = MagicMock()
    res_clone.returncode = 1
    res_clone.stderr = "error: could not clone repository"
    mock_interface.return_value = res_clone

    msg, sucesso = clonar_repositorio("github.com:user/repo.git", "repo")
    
    assert msg == "error: could not clone repository"
    assert sucesso is False


# -----------------------------------------------------------------------------
# restaurar_alteracoes
# -----------------------------------------------------------------------------

# Teste 24: restaurar_alteracoes retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_restaurar_alteracoes_sucesso(mock_interface):
    res_restore = MagicMock()
    res_restore.returncode = 0
    res_restore.stdout = "Restoring changes...\n"
    mock_interface.return_value = res_restore

    msg, sucesso = restaurar_alteracoes()
    assert msg == "Desfeito com sucesso!"
    assert sucesso is True

# Teste 25: restaurar_alteracoes retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_restaurar_alteracoes_falha(mock_interface):
    res_restore = MagicMock()
    res_restore.returncode = 1
    res_restore.stderr = "error: could not restore changes"
    mock_interface.return_value = res_restore

    msg, sucesso = restaurar_alteracoes()
    
    assert msg == "error: could not restore changes"
    assert sucesso is False

# -----------------------------------------------------------------------------
# deletar_branch
# -----------------------------------------------------------------------------

# Teste 26: deletar_branch retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_deletar_branch_sucesso(mock_interface):
    res_delete = MagicMock()
    res_delete.returncode = 0
    res_delete.stdout = "Deleted branch feature/login (was abc123).\n"
    mock_interface.return_value = res_delete

    msg, sucesso = deletar_branch("feature/login")
    
    assert msg == "Branch deletada!"
    assert sucesso is True

    mock_interface.assert_called_once_with(["git", "branch", "-d", "feature/login"])

# Teste 27: deletar_branch retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_deletar_branch_falha(mock_interface):
    res_delete = MagicMock()
    res_delete.returncode = 1
    res_delete.stderr = "error: could not delete branch"
    mock_interface.return_value = res_delete

    msg, sucesso = deletar_branch("feature/login")
    
    assert msg == "error: could not delete branch"
    assert sucesso is False

# -----------------------------------------------------------------------------
# remover_staging
# -----------------------------------------------------------------------------

# Teste 28: remover_staging retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_remover_staging_sucesso(mock_interface):
    res_restore = MagicMock()
    res_restore.returncode = 0
    res_restore.stdout = "Unstaged changes...\n"
    mock_interface.return_value = res_restore

    msg, sucesso = remover_staging()
    
    assert msg == "Staging removido com sucesso!"
    assert sucesso is True

# Teste 29: remover_staging retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_remover_staging_falha(mock_interface):
    res_restore = MagicMock()
    res_restore.returncode = 1
    res_restore.stderr = "error: could not remove staging"
    mock_interface.return_value = res_restore

    msg, sucesso = remover_staging()
    
    assert msg == "error: could not remove staging"
    assert sucesso is False

# -----------------------------------------------------------------------------
# historico
# -----------------------------------------------------------------------------

# Teste 30: historico retorna o histórico de commits quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_historico_sucesso(mock_interface):
    res_log = MagicMock()
    res_log.returncode = 0
    res_log.stdout = "commit abc123\nAuthor: Dev <dev@example.com>\nDate: Mon Jan 1 00:00:00 2023 +0000\n\n    Initial commit\n"
    mock_interface.return_value = res_log
    
    resultado = historico()
    
    assert resultado == "commit abc123\nAuthor: Dev <dev@example.com>\nDate: Mon Jan 1 00:00:00 2023 +0000\n\n    Initial commit\n"
    mock_interface.assert_called_once_with(["git", "log"])

# Teste 31: historico retorna None quando a operação falha
@patch("src.core.git_service.interface_git")
def test_historico_falha(mock_interface):
    res_log = MagicMock()
    res_log.returncode = 1
    res_log.stderr = "error: could not retrieve log"
    mock_interface.return_value = res_log
    
    resultado = historico()
    
    assert resultado is None
    mock_interface.assert_called_once_with(["git", "log"])

# -----------------------------------------------------------------------------
# diff
# -----------------------------------------------------------------------------

# Teste 32: diff retorna o diff quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_diff_sucesso(mock_interface):
    res_diff = MagicMock()
    res_diff.returncode = 0
    res_diff.stdout = "diff --git a/file.txt b/file.txt\nindex abc123..def456 100644\n--- a/file.txt\n+++ b/file.txt\n@@ -1 +1 @@\n-Hello World\n+Hello GugaGit\n"
    mock_interface.return_value = res_diff
    
    resultado = diff()
    
    assert resultado == "diff --git a/file.txt b/file.txt\nindex abc123..def456 100644\n--- a/file.txt\n+++ b/file.txt\n@@ -1 +1 @@\n-Hello World\n+Hello GugaGit\n"
    mock_interface.assert_called_once_with(["git", "diff"])

# Teste 33: diff retorna None quando a operação falha
@patch("src.core.git_service.interface_git")
def test_diff_falha(mock_interface):
    res_diff = MagicMock()
    res_diff.returncode = 1
    res_diff.stderr = "error: could not retrieve diff"
    mock_interface.return_value = res_diff
    
    resultado = diff()
    
    assert resultado is None
    mock_interface.assert_called_once_with(["git", "diff"])

# -----------------------------------------------------------------------------
# stash
# -----------------------------------------------------------------------------

# Teste 34: stash retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_stash_sucesso(mock_interface):
    res_stash = MagicMock()
    res_stash.returncode = 0
    res_stash.stdout = "Saved working directory and index state WIP on main: abc123 Commit message\n"
    mock_interface.return_value = res_stash

    msg, sucesso = stash()
    
    assert msg == "Alterações guardadas no stash!"
    assert sucesso is True

# Teste 35: stash retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_stash_falha(mock_interface):
    res_stash = MagicMock()
    res_stash.returncode = 1
    res_stash.stderr = "error: could not stash changes"
    mock_interface.return_value = res_stash

    msg, sucesso = stash()
    
    assert msg == "error: could not stash changes"
    assert sucesso is False

# Teste 35: stash_pop retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_stash_pop_sucesso(mock_interface):
    res_stash_pop = MagicMock()
    res_stash_pop.returncode = 0
    res_stash_pop.stdout = "On branch main\nChanges not staged for commit:\n  (use \"git add <file>...\" to update what will be committed)\n  (use \"git restore <file>...\" to discard changes in working directory)\n\n\tmodified:   file.txt\n"
    mock_interface.return_value = res_stash_pop

    msg, sucesso = stash_pop()
    
    assert msg == "Stash aplicado!"
    assert sucesso is True

# Teste 36: stash_pop retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_stash_pop_falha(mock_interface):
    res_stash_pop = MagicMock()
    res_stash_pop.returncode = 1
    res_stash_pop.stderr = "error: could not apply stash"
    mock_interface.return_value = res_stash_pop

    msg, sucesso = stash_pop()
    
    assert msg == "error: could not apply stash"
    assert sucesso is False

# Teste 37: listar_stash retorna a lista de stashes quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_listar_stash_sucesso(mock_interface):
    res_listar_stash = MagicMock()
    res_listar_stash.returncode = 0
    res_listar_stash.stdout = "stash@{0}: WIP on main: abc123 Commit message\nstash@{1}: WIP on main: def456 Another commit\n"
    mock_interface.return_value = res_listar_stash

    resultado = listar_stash()
    
    assert resultado == "stash@{0}: WIP on main: abc123 Commit message\nstash@{1}: WIP on main: def456 Another commit\n"
    mock_interface.assert_called_once_with(["git", "stash", "list"])

# Teste 38: listar_stash retorna None quando a operação falha
@patch("src.core.git_service.interface_git")
def test_listar_stash_falha(mock_interface):
    res_listar_stash = MagicMock()
    res_listar_stash.returncode = 1
    res_listar_stash.stderr = "error: could not list stash"
    mock_interface.return_value = res_listar_stash

    resultado = listar_stash()
    
    assert resultado is None
    mock_interface.assert_called_once_with(["git", "stash", "list"])

# -----------------------------------------------------------------------------
# merge
# -----------------------------------------------------------------------------

# Teste 39: merge retorna a mensagem de sucesso quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_merge_sucesso(mock_interface):
    res_merge = MagicMock()
    res_merge.returncode = 0
    res_merge.stdout = "Merge made by the 'recursive' strategy.\n file.txt | 1 +\n 1 file changed, 1 insertion(+)\n"
    mock_interface.return_value = res_merge

    msg, sucesso = merge("feature/login")
    
    assert msg == "Mergeado com sucesso!"
    assert sucesso is True

# Teste 40: merge retorna a mensagem de erro quando a operação falha
@patch("src.core.git_service.interface_git")
def test_merge_falha(mock_interface):
    res_merge = MagicMock()
    res_merge.returncode = 1
    res_merge.stderr = "error: could not merge"
    mock_interface.return_value = res_merge

    msg, sucesso = merge("feature/login")
    
    assert msg == "error: could not merge"
    assert sucesso is False

# -----------------------------------------------------------------------------
# listar_tags
# -----------------------------------------------------------------------------

# Teste 41: listar_tags retorna a lista de tags quando a operação é bem-sucedida
@patch("src.core.git_service.interface_git")
def test_listar_tags_sucesso(mock_interface):
    res_listar_tags = MagicMock()
    res_listar_tags.returncode = 0
    res_listar_tags.stdout = "v1.0.0\nv1.1.0\nv2.0.0\n"
    mock_interface.return_value = res_listar_tags

    resultado = listar_tags()
    
    assert resultado == "v1.0.0\nv1.1.0\nv2.0.0\n"
    mock_interface.assert_called_once_with(["git", "tag"])

# Teste 42: listar_tags retorna None quando a operação falha
@patch("src.core.git_service.interface_git")
def test_listar_tags_falha(mock_interface):
    res_listar_tags = MagicMock()
    res_listar_tags.returncode = 1
    res_listar_tags.stderr = "error: could not list tags"
    mock_interface.return_value = res_listar_tags

    resultado = listar_tags()
    
    assert resultado is None
    mock_interface.assert_called_once_with(["git", "tag"])

# -----------------------------------------------------------------------------
# trocar_branch
# -----------------------------------------------------------------------------