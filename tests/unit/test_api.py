import os
import json
import pytest
from unittest.mock import MagicMock, patch
from src.infrastructure.storage import obter_ultimo_repositorio, salvar_ultimo_repositorio
from src.infrastructure.storage import salvar_ultimo_repositorio
from src.ui.api import GugaGitAPI
from src.core.types import GitResult
from src.core.git.config import GitConfigService
from src.core.git.branch import BranchService
from src.core.git.staging import StagingService
from src.core.git.remote import RemoteService
from src.core.git.stash import StashService

# Redirecionamentos (para compatibilidade com os testes de API)
obter_config_git = GitConfigService().obter_config_git
salvar_config_git = GitConfigService().salvar_config_git

branch_atual = BranchService().branch_atual
listar_branches = BranchService().listar_branches
criar_branch = BranchService().criar_branch
deletar_branch = BranchService().deletar_branch

clonar_repositorio = RemoteService().clonar_repositorio
fetch = RemoteService().fetch
push = RemoteService().push

adicionar = StagingService().adicionar_todos
commit = StagingService().commit
status = StagingService().status

stash = StashService().stash

@pytest.fixture
def api():
    """Instância limpa do GugaGitAPI para cada teste."""
    return GugaGitAPI()


# =============================================================================
# UTILIDADES DA API & JANELA
# =============================================================================

# Teste 1: obter_config_git retorna o dicionário esperado
def test_obter_config_git(api):
    api.config_svc.obter_config_git = MagicMock(
        return_value={"name": "Guga", "email": "guga@dev.com"}
    )

    res = api.obter_config_git()

    assert res == {"name": "Guga", "email": "guga@dev.com"}
    api.config_svc.obter_config_git.assert_called_once()

# Teste 2: salvar_config_git retorna True quando a operação é bem-sucedida
def test_salvar_config_git(api):
    api.config_svc.salvar_config_git = MagicMock(return_value=True)

    res = api.salvar_config_git("Guga", "guga@dev.com")

    assert res is True
    api.config_svc.salvar_config_git.assert_called_once_with("Guga", "guga@dev.com")

#Teste 3: verificar_git retorna True quando o Git está instalado
def test_verificar_git(api):
    with patch("src.ui.api.git_instalado", return_value=True):
        assert api.verificar_git() is True

# Teste 4: minimizar_janela chama o método minimize da janela atual
def test_minimizar_janela(api):
    api.window_svc.minimizar = MagicMock()
    api.minimizar_janela()
    api.window_svc.minimizar.assert_called_once()

# Teste 5: maximizar_janela chama o método maximize da janela atual e atualiza o estado
def test_maximizar_janela(api):
    api.window_svc.maximizar = MagicMock()
    api.maximizar_janela()
    api.window_svc.maximizar.assert_called_once()

# Teste 6: restaurar_janela chama o método restore da janela atual e atualiza o estado
def test_restaurar_janela(api):
    api.window_svc.restaurar = MagicMock()
    api.restaurar_janela()
    api.window_svc.restaurar.assert_called_once()

# Teste 7: alternar_maximizar_janela sem janela não altera o estado
def test_alternar_maximizar_janela_sem_janela(api):
    api.window_svc.alternar_maximizar = MagicMock()
    api.alternar_maximizar_janela()
    api.window_svc.alternar_maximizar.assert_called_once()

# Teste 8: alternar_maximizar_janela com janela alterna corretamente entre maximizar e restaurar
def test_alternar_maximizar_janela_alternancia(api):
    mock_window = MagicMock()
    with patch("src.ui.api.webview.windows", [mock_window]):
        # Se falso, maximiza
        api.janela_maximizada = False
        api.alternar_maximizar_janela()
        mock_window.maximize.assert_called_once()
        assert api.janela_maximizada is True

        # Se verdadeiro, restaura
        api.alternar_maximizar_janela()
        mock_window.restore.assert_called_once()
        assert api.janela_maximizada is False

# Teste 9: fechar_janela chama o método destroy da janela atual
def test_fechar_janela(api):
    api.window_svc.fechar = MagicMock()
    api.fechar_janela()
    api.window_svc.fechar.assert_called_once()

# Teste 10: aplicar_icone_nativo com sucesso chama ShowIcon
def test_aplicar_icone_nativo_sucesso(api):
    api.window_svc.aplicar_icone_nativo = MagicMock()
    caminho = "caminho/icone.ico"
    
    api.aplicar_icone_nativo(caminho)
    
    api.window_svc.aplicar_icone_nativo.assert_called_once_with(caminho)

# Teste 11: aplicar_icone_nativo com exceção não levanta erro
def test_aplicar_icone_nativo_excecao(api):
    with patch("src.ui.api.webview.windows", [MagicMock()]):
        # Força erro ao importar clr
        api.aplicar_icone_nativo("caminho_invalido.ico")

# Teste 12: log chama evaluate_js com o comando correto
def test_log(api):
    mock_window = MagicMock()
    with patch("src.ui.api.webview.windows", [mock_window]):
        api.log("Mensagem de teste")
        mock_window.evaluate_js.assert_called_once()
        args = mock_window.evaluate_js.call_args[0][0]
        assert "logTerminal" in args

# Teste 13: _processar_resultado com sucesso retorna True e não chama log
def test_processar_resultado_com_erro_detalhado(api):
    with patch.object(api, "log") as mock_log:
        res = GitResult(sucesso=False, mensagem="Erro", erro_detalhado="Falha de permissão")
        resultado = api._processar_resultado(res)

        assert resultado is False
        assert mock_log.call_count == 2

# Teste 14: obter_estado_atual retorna sucesso False quando não há pasta atual
def test_obter_estado_atual(api, tmp_path):
    # Quando não há pasta
    estado = api.obter_estado_atual()
    assert estado["sucesso"] is False

    # Quando há pasta válida
    api.pasta_atual = str(tmp_path)
    api.repo_atual = "meu_repo"
    with patch("src.ui.api.BranchService.branch_atual", return_value=GitResult(sucesso=True, mensagem="ok", dados="main")):
        estado = api.obter_estado_atual()
        assert estado["sucesso"] is True
        assert estado["branch"] == "main"

    # Se branch_atual falhar
    with patch("src.ui.api.BranchService.branch_atual", return_value=GitResult(sucesso=False, mensagem="err")):
        estado = api.obter_estado_atual()
        assert estado["branch"] == "---"

# Teste 15: executar_comando_customizado retorna False quando não há pasta atual
def test_executar_comando_customizado(api):
    # Sem pasta
    assert api.executar_comando_customizado("git status") is False

    # Com pasta
    api.pasta_atual = "/tmp/repo"
    with patch("src.ui.api.executar_comando_livre", return_value=("Saida", True)), \
         patch.object(api, "log"):
        assert api.executar_comando_customizado("git status") is True


# =============================================================================
# WORKSPACE E REPOSITÓRIO
# =============================================================================

# Teste 16: abrir_repositorio com sucesso registra o workspace e retorna info correta
def test_abrir_repositorio_sucesso(api, tmp_path):
    repo_dir = tmp_path / "repo_teste"
    git_dir = repo_dir / ".git"
    git_dir.mkdir(parents=True)

    mock_window = MagicMock()
    mock_window.create_file_dialog.return_value = [str(repo_dir)]

    with patch("src.ui.api.webview.windows", [mock_window]), \
         patch("src.ui.api.salvar_ultimo_repositorio"), \
         patch("src.ui.api.BranchService.branch_atual", return_value=GitResult(sucesso=True, mensagem="ok", dados="main")), \
         patch("os.chdir"):

        info = api.abrir_repositorio()
        assert info["sucesso"] is True
        assert info["repo"] == "repo_teste"

# teste 17: abrir_repositorio retorna sucesso False quando a pasta selecionada não é um repositório Git
def test_abrir_repositorio_nao_git_ou_cancelado(api, tmp_path):
    # Caso 1: Sem janela
    with patch("src.ui.api.webview.windows", []):
        assert api.abrir_repositorio() == {"sucesso": False}

    # Caso 2: Pasta selecionada não tem .git
    mock_window = MagicMock()
    mock_window.create_file_dialog.return_value = [str(tmp_path)]
    with patch("src.ui.api.webview.windows", [mock_window]), \
         patch.object(api, "log"):
        assert api.abrir_repositorio() == {"sucesso": False}

# Teste 18: selecionar_pasta_para_clone retorna caminho correto ou vazio quando cancelado
def test_selecionar_pasta_para_clone(api):
    with patch("src.ui.api.webview.windows", []):
        assert api.selecionar_pasta_para_clone() == ""

    mock_window = MagicMock()
    mock_window.create_file_dialog.return_value = ["/pasta/clone"]
    with patch("src.ui.api.webview.windows", [mock_window]):
        assert api.selecionar_pasta_para_clone() == "/pasta/clone"

# Teste 19: executar_clonar chama clonar_repositorio e registra workspace quando bem-sucedido
def test_executar_clonar(api, tmp_path):
    url = "https://github.com/usuario/repo.git"
    pasta_dest = str(tmp_path)
    nova_pasta = tmp_path / "repo"
    (nova_pasta / ".git").mkdir(parents=True)

    with patch("src.ui.api.RemoteService.clonar_repositorio", return_value=GitResult(sucesso=True, mensagem="ok")), \
         patch.object(api, "_registrar_workspace") as mock_reg:

        res = api.executar_clonar(url, pasta_dest)
        assert res is True
        mock_reg.assert_called_once_with(str(nova_pasta))


# =============================================================================
# SINCRONIZAÇÃO (Pull, Push, Fetch)
# =============================================================================

# Teste 20: sincronização (fetch, pull) retorna True quando bem-sucedida
def test_sincronizacao(api):
    with patch("src.ui.api.RemoteService.fetch", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_fetch() is True

    with patch("src.ui.api.RemoteService.pull", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_pull() is True

# Teste 21: executar_push retorna False quando não há branch válida
def test_executar_push(api):
    # Sem branch válida
    with patch("src.ui.api.BranchService.branch_atual", return_value=GitResult(sucesso=False, mensagem="err")):
        assert api.executar_push() is False

    # Com branch válida
    with patch("src.ui.api.BranchService.branch_atual", return_value=GitResult(sucesso=True, mensagem="ok", dados="main")), \
         patch("src.ui.api.RemoteService.push", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_push() is True


# =============================================================================
# BRANCHES & MERGE
# =============================================================================

# Teste 22: obter_branches retorna lista de branches quando bem-sucedido
def test_obter_branches(api):
    with patch("src.ui.api.BranchService.listar_branches", return_value=GitResult(sucesso=True, mensagem="ok", dados=["main", "dev"])):
        assert api.obter_branches() == ["main", "dev"]
        assert api.executar_listar_branches() == ["main", "dev"]

# Teste 23: executar_criar_branch e executar_trocar_branch retornam sucesso True quando bem-sucedidos
def test_executar_criar_e_trocar_branch(api):
    res_git = GitResult(sucesso=True, mensagem="ok")
    res_b = GitResult(sucesso=True, mensagem="ok", dados="feature")

    with patch("src.ui.api.BranchService.criar_branch", return_value=res_git), \
         patch("src.ui.api.BranchService.branch_atual", return_value=res_b):
        res = api.executar_criar_branch("feature")
        assert res == {"sucesso": True, "branch": "feature"}

    with patch("src.ui.api.BranchService.trocar_branch", return_value=res_git), \
         patch("src.ui.api.BranchService.branch_atual", return_value=res_b):
        res = api.executar_trocar_branch("feature")
        assert res == {"sucesso": True, "branch": "feature"}


# Teste 24: deletar_branch e merge retornam sucesso True quando bem-sucedidos
def test_deletar_e_merge_branch(api):
    with patch("src.ui.api.BranchService.deletar_branch", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_deletar_branch("feature") is True

    with patch("src.ui.api.BranchService.merge", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_merge("feature") is True


# =============================================================================
# STAGING E COMMIT
# =============================================================================

# Teste 25: executar_adicionar_e_commit retorna False quando a mensagem de commit é vazia
def test_executar_adicionar_e_commit(api):
    # Mensagem vazia
    assert api.executar_adicionar_e_commit("   ") is False

    # Sucesso
    with patch("src.ui.api.StagingService.adicionar_todos", return_value=GitResult(sucesso=True, mensagem="ok")), \
         patch("src.ui.api.StagingService.commit", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_adicionar_e_commit("Commit valido") is True

# Teste 26: executar_commit_isolado retorna False quando a mensagem de commit é vazia
def test_executar_commit_isolado(api):
    assert api.executar_commit("   ") is False

    with patch("src.ui.api.StagingService.commit", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_commit("Commit valido") is True

# Teste 27: staging_e_restaurar operações retornam sucesso True quando bem-sucedidas
def test_staging_e_restaurar(api):
    with patch("src.ui.api.StagingService.adicionar_todos", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_adicionar() is True

    with patch("src.ui.api.StagingService.remover_staging_todos", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_remover_staging() is True

    with patch("src.ui.api.StagingService.restaurar_alteracoes", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_restaurar() is True

    with patch("src.ui.api.StagingService.obter_arquivos_status", return_value=[]):
        assert api.obter_arquivos_status() == []

    with patch("src.ui.api.StagingService.adicionar_selecionados", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_adicionar_selecionados(["file1.txt"]) is True

    with patch("src.ui.api.StagingService.remover_staging_selecionados", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_remover_selecionados_staging(["file1.txt"]) is True


# =============================================================================
# CONSULTAS (Status, Log, Diff, Tags, Stash)
# =============================================================================

# Teste 28: consultas retornam os dados esperados quando bem-sucedidas
def test_consultas(api):
    with patch("src.ui.api.StagingService.status", return_value=GitResult(sucesso=True, mensagem="ok", dados="Clean")):
        assert api.executar_status() == "Clean"

    with patch("src.ui.api.BranchService.listar_branches", return_value=GitResult(sucesso=True, mensagem="ok", dados=["main"])):
        assert api.executar_branches() == "main"

    with patch("src.ui.api.HistoryService.historico", return_value=GitResult(sucesso=True, mensagem="ok", dados="Log output")):
        assert api.executar_historico() == "Log output"

    with patch("src.ui.api.StagingService.diff", return_value=GitResult(sucesso=True, mensagem="ok", dados="")):
        assert api.executar_diff() == "Nenhuma diferença encontrada."

    with patch("src.ui.api.HistoryService.listar_tags", return_value=GitResult(sucesso=True, mensagem="ok", dados="v1.0.0")):
        assert api.obter_tags() == "v1.0.0"
        assert api.executar_tags() == "v1.0.0"

# Teste 29: stash_operações retornam sucesso True quando bem-sucedidas
def test_stash_operações(api):
    with patch("src.ui.api.StashService.stash", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_stash() is True

    with patch("src.ui.api.StashService.stash_pop", return_value=GitResult(sucesso=True, mensagem="ok")):
        assert api.executar_stash_pop() is True

    with patch("src.ui.api.StashService.listar_stash", return_value=GitResult(sucesso=True, mensagem="ok", dados="stash@{0}")):
        assert api.obter_stashes() == "stash@{0}"

# Teste 30: Simula uma exceção genérica no comando livre
def test_executar_comando_customizado_com_excecao(api):
    api.pasta_atual = "/tmp/repo"
    
    with patch("src.ui.api.executar_comando_livre", side_effect=Exception("Erro crítico de I/O")), \
         patch.object(api, "log") as mock_log:
        
        resultado = api.executar_comando_customizado("git status")
        assert resultado is False
        mock_log.assert_called()

# Teste 31: Simula erro ao abrir a caixa de diálogo do SO
def test_abrir_repositorio_excecao_dialog(api):
    mock_window = MagicMock()
    mock_window.create_file_dialog.side_effect = Exception("Falha na janela nativa")
    
    with patch("src.ui.api.webview.windows", [mock_window]), \
         patch.object(api, "log") as mock_log:
        
        info = api.abrir_repositorio()
        assert info == {"sucesso": False}
        mock_log.assert_called()


# Teste 32: fluxo de persistência do último repositório aberto funciona corretamente
def test_fluxo_persistencia_ultimo_repositorio_real(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    pasta_projeto = str(tmp_path / "meu_projeto_git")
    
    salvar_ultimo_repositorio(pasta_projeto)

    ultimo = obter_ultimo_repositorio()
    assert ultimo == pasta_projeto