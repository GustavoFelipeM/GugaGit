import os
import json
import webview

from src.core.git_service import (
    adicionar_arquivos_staging, branch_atual, executar_comando_livre, obter_config_git, salvar_config_git, status, fetch, 
    criar_branch, adicionar, commit, push, listar_branches, trocar_branch, pull, clonar_repositorio, 
    restaurar_alteracoes, deletar_branch, remover_staging, historico, diff, stash, stash_pop, 
    listar_stash, merge, listar_tags, git_instalado, obter_arquivos_status, remover_selecionados_staging
)
from src.core.types import GitResult
from src.infrastructure.storage import obter_ultimo_repositorio, salvar_ultimo_repositorio

class GugaGitAPI:
    def __init__(self):
        self.pasta_atual = None
        self.repo_atual = None
        self.janela_maximizada = False

    # ==========================================
    # UTILIDADES DA API
    # ==========================================

    def obter_config_git(self):
        res = obter_config_git()
        if hasattr(res, "to_dict"):
            return res.to_dict()
        return res
    
    def salvar_config_git(self, nome, email):
        res = salvar_config_git(nome, email)
        if hasattr(res, "to_dict"):
            return res.to_dict()
        return res
    
    def verificar_git(self):
        return git_instalado()
    
    def minimizar_janela(self):
        if webview.windows:
            webview.windows[0].minimize()

    def maximizar_janela(self):
        if webview.windows:
            janela = webview.windows[0]
            if hasattr(janela, "maximize"):
                janela.maximize()
                self.janela_maximizada = True

    def restaurar_janela(self):
        if webview.windows:
            janela = webview.windows[0]
            if hasattr(janela, "restore"):
                janela.restore()
                self.janela_maximizada = False

    def alternar_maximizar_janela(self):
        if not webview.windows:
            return

        janela = webview.windows[0]

        if self.janela_maximizada:
            if hasattr(janela, "restore"):
                janela.restore()
            self.janela_maximizada = False
        else:
            if hasattr(janela, "maximize"):
                janela.maximize()
            self.janela_maximizada = True

    def fechar_janela(self):
        if webview.windows:
            webview.windows[0].destroy()

    def aplicar_icone_nativo(self, caminho_icone):
        try:
            import clr  # type: ignore

            clr.AddReference('System.Drawing')
            from System.Drawing import Icon  # type: ignore

            if webview.windows and os.path.isfile(caminho_icone):
                janela = webview.windows[0]
                if getattr(janela, 'native', None) is not None:
                    janela.native.Icon = Icon(caminho_icone)
                    janela.native.ShowIcon = True
        except Exception:
            pass

    def log(self, mensagem):
        if webview.windows and len(webview.windows) > 0:
            msg_json = json.dumps(str(mensagem))
            webview.windows[0].evaluate_js(f"if(typeof logTerminal === 'function') logTerminal({msg_json})")

    def _processar_resultado(self, res: GitResult) -> bool:
        """Centraliza a escrita nos logs da UI e exibe erros detalhados quando houver."""
        self.log(f"> {res.mensagem}")
        if not res.sucesso and res.erro_detalhado:
            self.log(f"[DEBUG GIT]: {res.erro_detalhado}")
        return res.sucesso

    def _registrar_workspace(self, pasta):
        os.chdir(pasta)
        self.pasta_atual = pasta
        self.repo_atual = os.path.basename(pasta)
        salvar_ultimo_repositorio(pasta)

        res_branch = branch_atual()
        nome_branch = res_branch.dados if res_branch.sucesso else "---"

        return {
            "sucesso": True,
            "repo": self.repo_atual,
            "branch": nome_branch,
            "caminho": pasta,
        }

    def obter_estado_atual(self):
        if self.pasta_atual and os.path.isdir(self.pasta_atual):
            repo = self.repo_atual or os.path.basename(self.pasta_atual)
            res_branch = branch_atual()
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
    
    def executar_comando_customizado(self, comando):
        if not self.pasta_atual:
            self.log("> ERRO: Nenhum repositório aberto.")
            return False

        self.log(f"$ {comando}")
        saida, sucesso = executar_comando_livre(comando, self.pasta_atual)
        self.log(saida)
        return sucesso

    # ==========================================
    # WORKSPACE E REPOSITÓRIO
    # ==========================================
    def abrir_repositorio(self):
        if not webview.windows: return {"sucesso": False}
        pastas = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        
        if pastas and len(pastas) > 0:
            pasta = pastas[0]
            if os.path.isdir(os.path.join(pasta, ".git")):
                info = self._registrar_workspace(pasta)
                self.log("> Workspace carregado com sucesso.")
                return info
            else:
                self.log("> ERRO: A pasta selecionada não é um repositório Git.")
        return {"sucesso": False}

    def selecionar_pasta_para_clone(self):
        if not webview.windows: return ""
        pastas = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        return pastas[0] if pastas else ""

    def executar_clonar(self, url, pasta_destino):
        self.log(f"> Clonando {url} para {pasta_destino}...")
        res = clonar_repositorio(url, pasta_destino)
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
    def executar_fetch(self):
        self.log("> Executando fetch...")
        res = fetch()
        return self._processar_resultado(res)

    def executar_pull(self):
        self.log("> Executando pull...")
        res = pull()
        return self._processar_resultado(res)

    def executar_push(self):
        res_branch = branch_atual()
        if not res_branch.sucesso or not res_branch.dados:
            self.log("> ERRO: Não foi possível identificar a branch atual para o push.")
            return False

        branch = res_branch.dados
        self.log(f"> Executando push na branch {branch}...")
        res = push(branch)
        return self._processar_resultado(res)

    # ==========================================
    # BRANCHES & MERGE
    # ==========================================
    def obter_branches(self):
        res = listar_branches()
        return res.dados if res.sucesso and res.dados else []

    def executar_listar_branches(self):
        return self.obter_branches()

    def executar_criar_branch(self, nome):
        self.log(f"> Criando branch '{nome}'...")
        res = criar_branch(nome.strip())
        sucesso = self._processar_resultado(res)
        
        res_b = branch_atual()
        nome_branch = res_b.dados if res_b.sucesso else "---"
        return {"sucesso": sucesso, "branch": nome_branch}

    def executar_trocar_branch(self, nome):
        self.log(f"> Trocando para a branch '{nome}'...")
        res = trocar_branch(nome)
        sucesso = self._processar_resultado(res)
        
        res_b = branch_atual()
        nome_branch = res_b.dados if res_b.sucesso else "---"
        return {"sucesso": sucesso, "branch": nome_branch}

    def executar_deletar_branch(self, nome):
        self.log(f"> Deletando branch '{nome}'...")
        res = deletar_branch(nome)
        return self._processar_resultado(res)

    def executar_merge(self, nome_branch):
        self.log(f"> Fazendo merge de '{nome_branch}' na branch atual...")
        res = merge(nome_branch)
        return self._processar_resultado(res)

    # ==========================================
    # STAGING E COMMIT
    # ==========================================
    def executar_adicionar_e_commit(self, mensagem):
        if not mensagem.strip():
            self.log("> ERRO: Mensagem de commit vazia.")
            return False
            
        res_add = adicionar()
        if self._processar_resultado(res_add):
            self.log("> Criando commit...")
            res_com = commit(mensagem)
            return self._processar_resultado(res_com)
        return False

    def executar_adicionar(self):
        self.log("> Adicionando arquivos ao staging...")
        res = adicionar()
        return self._processar_resultado(res)

    def executar_commit(self, mensagem):
        if not mensagem.strip():
            self.log("> ERRO: Mensagem de commit vazia.")
            return False

        self.log("> Criando commit...")
        res = commit(mensagem.strip())
        return self._processar_resultado(res)

    def executar_remover_staging(self):
        self.log("> Removendo arquivos do staging...")
        res = remover_staging()
        return self._processar_resultado(res)

    def executar_restaurar(self):
        self.log("> Restaurando alterações de arquivos modificados...")
        res = restaurar_alteracoes()
        return self._processar_resultado(res)

    def obter_arquivos_status(self):
        res = obter_arquivos_status()
        if isinstance(res, list):
            return res
        if hasattr(res, "sucesso") and res.sucesso and isinstance(res.dados, list):
            return res.dados
        return []


    def executar_adicionar_selecionados(self, arquivos):
        self.log(f"> Adicionando {len(arquivos)} arquivo(s) ao staging...")
        res = adicionar_arquivos_staging(arquivos)
        return self._processar_resultado(res)

    def executar_remover_selecionados_staging(self, arquivos):
        self.log(f"> Removendo {len(arquivos)} arquivo(s) do staging...")
        res = remover_selecionados_staging(arquivos)
        return self._processar_resultado(res)

    # ==========================================
    # CONSULTAS (Status, Log, Diff, Tags)
    # ==========================================
    def executar_status(self):
        res = status()
        conteudo = res.dados if res.sucesso else res.mensagem
        self.log(f"> STATUS:\n{conteudo}")
        return conteudo

    def executar_branches(self):
        res = listar_branches()
        conteudo = "\n".join(res.dados) if (res.sucesso and isinstance(res.dados, list)) else res.mensagem
        self.log(f"> BRANCHES:\n{conteudo}")
        return conteudo

    def executar_historico(self):
        res = historico()
        conteudo = res.dados if res.sucesso else res.mensagem
        self.log(f"> HISTÓRICO (LOG):\n{conteudo}")
        return conteudo

    def executar_diff(self):
        res = diff()
        conteudo = res.dados if res.sucesso else res.mensagem
        if not conteudo or not str(conteudo).strip():
            conteudo = "Nenhuma diferença encontrada."

        self.log(f"> DIFF:\n{conteudo}")
        return conteudo

    def obter_tags(self):
        res = listar_tags()
        conteudo = res.dados if res.sucesso else res.mensagem
        self.log(f"> TAGS:\n{conteudo}")
        return conteudo

    # ==========================================
    # STASH
    # ==========================================
    def executar_stash(self):
        self.log("> Guardando alterações em Stash...")
        res = stash()
        return self._processar_resultado(res)

    def executar_stash_pop(self):
        self.log("> Aplicando Stash (Pop)...")
        res = stash_pop()
        return self._processar_resultado(res)

    def obter_stashes(self):
        res = listar_stash()
        return res.dados if res.sucesso else ""

    def executar_tags(self):
        res = listar_tags()
        return res.dados if res.sucesso else ""