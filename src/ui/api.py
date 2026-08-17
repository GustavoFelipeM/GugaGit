import os
import json
from typing import Any, Dict, List, Optional, Union
import webview

from src.core.git import (
    BranchService,
    GitConfigService,
    HistoryService,
    RemoteService,
    StagingService,
    StashService,
)
from src.core.types import GitResult
from src.infrastructure.git_cli import executar_comando_livre, git_instalado
from src.infrastructure.storage import obter_ultimo_repositorio, salvar_ultimo_repositorio
from src.infrastructure.window import WindowService

class GugaGitAPI:
    def __init__(
        self,
        branch_service: Optional[BranchService] = None,
        staging_service: Optional[StagingService] = None,
        remote_service: Optional[RemoteService] = None,
        stash_service: Optional[StashService] = None,
        config_service: Optional[GitConfigService] = None,
        history_service: Optional[HistoryService] = None,
        window_svc: Optional[WindowService] = None,
    ) -> None:
        self.pasta_atual: Optional[str] = None
        self.repo_atual: Optional[str] = None
        self.janela_maximizada: bool = False

        self.branch_svc: BranchService = branch_service or BranchService()
        self.staging_svc: StagingService = staging_service or StagingService()
        self.remote_svc: RemoteService = remote_service or RemoteService()
        self.stash_svc: StashService = stash_service or StashService()
        self.config_svc: GitConfigService = config_service or GitConfigService()
        self.history_svc: HistoryService = history_service or HistoryService()
        self.window_svc: WindowService = window_svc or WindowService()

    # ==========================================
    # GIT CONFIG
    # ==========================================

    def obter_config_git(self) -> Dict[str, Any]:
        res = self.config_svc.obter_config_git()
        return res.to_dict() if hasattr(res, "to_dict") else res
    
    def salvar_config_git(self, nome: str, email: str) -> Dict[str, Any]:
        res = self.config_svc.salvar_config_git(nome, email)
        return res.to_dict() if hasattr(res, "to_dict") else res
    
    def verificar_git(self) -> bool:
        return git_instalado()

    # ==========================================
    # JANELA
    # ==========================================
    
    def minimizar_janela(self) -> None:
        self.window_svc.minimizar()

    def maximizar_janela(self) -> None:
        self.window_svc.maximizar()

    def restaurar_janela(self) -> None:
        self.window_svc.restaurar()

    def alternar_maximizar_janela(self) -> None:
        self.window_svc.alternar_maximizar()
        self.janela_maximizada = self.window_svc.janela_maximizada

    def fechar_janela(self) -> None:
        self.window_svc.fechar()

    def aplicar_icone_nativo(self, caminho_icone: str) -> None:
        self.window_svc.aplicar_icone_nativo(caminho_icone)

    # ==========================================
    # UTILIDADES
    # ==========================================

    def log(self, mensagem: Any) -> None:
        if webview.windows and len(webview.windows) > 0:
            msg_json = json.dumps(str(mensagem))
            webview.windows[0].evaluate_js(f"if(typeof logTerminal === 'function') logTerminal({msg_json})")

    def _processar_resultado(self, res: GitResult) -> bool:
        """Centraliza a escrita nos logs da UI e exibe erros detalhados quando houver."""
        self.log(f"> {res.mensagem}")
        if not res.sucesso and res.erro_detalhado:
            self.log(f"[DEBUG GIT]: {res.erro_detalhado}")
        return res.sucesso

    def _registrar_workspace(self, pasta: str) -> Dict[str, Any]:
        os.chdir(pasta)
        self.pasta_atual = pasta
        self.repo_atual = os.path.basename(pasta)
        salvar_ultimo_repositorio(pasta)

        res_branch = self.branch_svc.branch_atual()
        nome_branch = res_branch.dados if res_branch.sucesso else "---"

        return {
            "sucesso": True,
            "repo": self.repo_atual,
            "branch": nome_branch,
            "caminho": pasta,
        }

    def obter_estado_atual(self) -> Dict[str, Any]:
        if self.pasta_atual and os.path.isdir(self.pasta_atual):
            repo = self.repo_atual or os.path.basename(self.pasta_atual)
            res_branch = self.branch_svc.branch_atual()
            nome_branch = res_branch.dados if res_branch.sucesso else "---"

            return {
                "sucesso": True,
                "repo": repo,
                "branch": nome_branch,
                "caminho": self.pasta_atual,
            }

        return {
            "sucesso": False,
            "repo": "Nenhum Repo",
            "branch": "---",
            "caminho": "---",
        }
    
    def executar_comando_customizado(self, comando: str) -> bool:
        if not self.pasta_atual:
            self.log("> ERRO: Nenhum repositório aberto.")
            return False

        self.log(f"$ {comando}")
        try:
            saida, sucesso = executar_comando_livre(comando, self.pasta_atual)
            self.log(saida)
            return sucesso
        except Exception as e:
            self.log(f"> ERRO ao executar comando: {e}")
            return False

    # ==========================================
    # WORKSPACE E REPOSITÓRIO
    # ==========================================
    def abrir_repositorio(self) -> Dict[str, Any]:
        try:
            if not webview.windows:
                return {"sucesso": False}

            folder_dialog = getattr(getattr(webview, "FileDialog", None), "FOLDER", webview.FOLDER_DIALOG)
            pastas = webview.windows[0].create_file_dialog(folder_dialog)

            if pastas and len(pastas) > 0:
                pasta = pastas[0]
                if os.path.isdir(os.path.join(pasta, ".git")):
                    info = self._registrar_workspace(pasta)
                    self.log("> Workspace carregado com sucesso.")
                    return info
                else:
                    self.log("> ERRO: A pasta selecionada não é um repositório Git.")
            return {"sucesso": False}
        except Exception as e:
            self.log(f"> ERRO ao abrir janela de diretório: {e}")
            return {"sucesso": False}

    def selecionar_pasta_para_clone(self) -> str:
        if not webview.windows:
            return ""
        pastas = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        return pastas[0] if pastas else ""

    def executar_clonar(self, url: str, pasta_destino: str) -> bool:
        self.log(f"> Clonando {url} para {pasta_destino}...")
        res = self.remote_svc.clonar_repositorio(url, pasta_destino)
        sucesso = self._processar_resultado(res)

        if sucesso:
            nome_repo = url.rstrip("/").split("/")[-1]
            if nome_repo.endswith(".git"):
                nome_repo = nome_repo[:-4]

            nova_pasta = os.path.join(pasta_destino, nome_repo)
            if os.path.isdir(os.path.join(nova_pasta, ".git")):
                self._registrar_workspace(nova_pasta)

        return sucesso

    # ==========================================
    # SINCRONIZAÇÃO (Pull, Push, Fetch)
    # ==========================================
    def executar_fetch(self) -> bool:
        self.log("> Executando fetch...")
        res = self.remote_svc.fetch()
        return self._processar_resultado(res)

    def executar_pull(self) -> bool:
        self.log("> Executando pull...")
        res = self.remote_svc.pull()
        return self._processar_resultado(res)

    def executar_push(self) -> bool:
        res_branch = self.branch_svc.branch_atual()
        if not res_branch.sucesso or not res_branch.dados:
            self.log(
                "> ERRO: Não foi possível identificar a branch atual para o push."
            )
            return False

        branch = res_branch.dados
        self.log(f"> Executando push na branch {branch}...")
        res = self.remote_svc.push(branch)
        return self._processar_resultado(res)

    # ==========================================
    # BRANCHES & MERGE
    # ==========================================
    def obter_branches(self) -> List[str]:
        res = self.branch_svc.listar_branches()
        return res.dados if res.sucesso and res.dados else []

    def executar_listar_branches(self) -> List[str]:
        return self.obter_branches()

    def executar_criar_branch(self, nome: str) -> Dict[str, Any]:
        self.log(f"> Criando branch '{nome}'...")
        res = self.branch_svc.criar_branch(nome.strip())
        sucesso = self._processar_resultado(res)

        res_b = self.branch_svc.branch_atual()
        nome_branch = res_b.dados if res_b.sucesso else "---"
        return {"sucesso": sucesso, "branch": nome_branch}

    def executar_trocar_branch(self, nome: str) -> Dict[str, Any]:
        self.log(f"> Trocando para a branch '{nome}'...")
        res = self.branch_svc.trocar_branch(nome)
        sucesso = self._processar_resultado(res)

        res_b = self.branch_svc.branch_atual()
        nome_branch = res_b.dados if res_b.sucesso else "---"
        return {"sucesso": sucesso, "branch": nome_branch}

    def executar_deletar_branch(self, nome: str) -> bool:
        self.log(f"> Deletando branch '{nome}'...")
        res = self.branch_svc.deletar_branch(nome)
        return self._processar_resultado(res)

    def executar_merge(self, nome_branch: str) -> bool:
        self.log(f"> Fazendo merge de '{nome_branch}' na branch atual...")
        res = self.branch_svc.merge(nome_branch)
        return self._processar_resultado(res)

    # ==========================================
    # STAGING E COMMIT
    # ==========================================
    def executar_adicionar_e_commit(self, mensagem: str) -> bool:
        if not mensagem.strip():
            self.log("> ERRO: Mensagem de commit vazia.")
            return False

        res_add = self.staging_svc.adicionar_todos()
        if self._processar_resultado(res_add):
            self.log("> Criando commit...")
            res_com = self.staging_svc.commit(mensagem)
            return self._processar_resultado(res_com)
        return False

    def executar_adicionar(self) -> bool:
        self.log("> Adicionando arquivos ao staging...")
        res = self.staging_svc.adicionar_todos()
        return self._processar_resultado(res)

    def executar_commit(self, mensagem: str) -> bool:
        if not mensagem.strip():
            self.log("> ERRO: Mensagem de commit vazia.")
            return False

        self.log("> Criando commit...")
        res = self.staging_svc.commit(mensagem.strip())
        return self._processar_resultado(res)

    def executar_remover_staging(self) -> bool:
        self.log("> Removendo arquivos do staging...")
        res = self.staging_svc.remover_staging_todos()
        return self._processar_resultado(res)

    def executar_restaurar(self) -> bool:
        self.log("> Restaurando alterações de arquivos modificados...")
        res = self.staging_svc.restaurar_alteracoes()
        return self._processar_resultado(res)

    def obter_arquivos_status(self) -> List[Dict[str, Any]]:
        res = self.staging_svc.obter_arquivos_status()
        if isinstance(res, list):
            return res
        if hasattr(res, "sucesso") and res.sucesso and isinstance(res.dados, list):
            return res.dados
        return []

    def executar_adicionar_selecionados(self, arquivos: list) -> bool:
        self.log(f"> Adicionando {len(arquivos)} arquivo(s) ao staging...")
        res = self.staging_svc.adicionar_selecionados(arquivos)
        return self._processar_resultado(res)

    def executar_remover_selecionados_staging(self, arquivos: list) -> bool:
        self.log(f"> Removendo {len(arquivos)} arquivo(s) do staging...")
        res = self.staging_svc.remover_staging_selecionados(arquivos)
        return self._processar_resultado(res)

    # ==========================================
    # CONSULTAS (Status, Log, Diff, Tags)
    # ==========================================
    def executar_status(self) -> Any:
        res = self.staging_svc.status()
        conteudo = res.dados if res.sucesso else res.mensagem
        self.log(f"> STATUS:\n{conteudo}")
        return conteudo

    def executar_branches(self) -> str:
        res = self.branch_svc.listar_branches()
        conteudo = (
            "\n".join(res.dados)
            if (res.sucesso and isinstance(res.dados, list))
            else res.mensagem
        )
        self.log(f"> BRANCHES:\n{conteudo}")
        return conteudo

    def executar_historico(self) -> Any:
        res = self.history_svc.historico()
        conteudo = res.dados if res.sucesso else res.mensagem
        self.log(f"> HISTÓRICO (LOG):\n{conteudo}")
        return conteudo

    def obter_resumo_alteracoes(self) -> Dict[str, Any]:
        try:
            res = self.staging_svc.obter_resumo_alteracoes()
            return res.to_dict() if hasattr(res, "to_dict") else {
                "sucesso": res.sucesso,
                "mensagem": res.mensagem,
                "dados": res.dados
            }
        except Exception as e:
            self.log(f"> ERRO ao obter resumo de alterações: {e}")
            return {"sucesso": False, "mensagem": str(e), "dados": None}

    def executar_diff(self, caminho_arquivo: str = None, staged: bool = False) -> str:
        res = self.staging_svc.diff(caminho=caminho_arquivo, staged=staged)
    
        conteudo = (res.dados if res.sucesso else res.mensagem) or "Nenhuma diferença encontrada."

        modo = " [Staged]" if staged else " [Working Tree]"
        alvo = f" ({caminho_arquivo})" if caminho_arquivo else ""
        
        self.log(f"> DIFF{modo}{alvo}:\n{conteudo}")
        return conteudo

    def obter_estatisticas_alteracoes(self) -> Dict[str, int]:
        """Retorna o dicionário de quantidade de alterações por arquivo."""
        res = self.staging_svc.obter_estatisticas_alteracoes()
        return res.dados if res.sucesso else {}

    def obter_tags(self) -> Any:
        res = self.history_svc.listar_tags()
        conteudo = res.dados if res.sucesso else res.mensagem
        self.log(f"> TAGS:\n{conteudo}")
        return conteudo

    def executar_tags(self) -> Any:
        res = self.history_svc.listar_tags()
        return res.dados if res.sucesso else ""
    
    # ==========================================
    # STASH
    # ==========================================
    def executar_stash(self) -> bool:
        self.log("> Guardando alterações em Stash...")
        res = self.stash_svc.stash()
        return self._processar_resultado(res)

    def executar_stash_pop(self) -> bool:
        self.log("> Aplicando Stash (Pop)...")
        res = self.stash_svc.stash_pop()
        return self._processar_resultado(res)

    def obter_stashes(self) -> Any:
        res = self.stash_svc.listar_stash()
        return res.dados if res.sucesso else ""