import os
import webview

from src.core.git_service import (
    branch_atual, executar_comando_livre, obter_config_git, salvar_config_git, status, fetch, 
    criar_branch, adicionar, commit, push, listar_branches, trocar_branch, pull, clonar_repositorio, 
    restaurar_alteracoes, deletar_branch, remover_staging, historico, diff, stash, stash_pop, 
    listar_stash, merge, listar_tags, git_instalado
)
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
        obter_config_git()

    def salvar_config_git(self, nome, email):
        salvar_config_git(nome, email)
    
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
        if webview.windows:
            # Escapa quebras de linha e aspas para não quebrar o JS
            msg_limpa = str(mensagem).replace('`', "'").replace('\\', '\\\\')
            webview.windows[0].evaluate_js(f"if(typeof logTerminal === 'function') logTerminal(`{msg_limpa}`)")

    def _registrar_workspace(self, pasta):
        os.chdir(pasta)
        self.pasta_atual = pasta
        self.repo_atual = os.path.basename(pasta)
        salvar_ultimo_repositorio(pasta)

        return {
            "sucesso": True,
            "repo": self.repo_atual,
            "branch": branch_atual(),
            "caminho": pasta,
        }

    def obter_estado_atual(self):
        if self.pasta_atual and os.path.isdir(self.pasta_atual):
            repo = self.repo_atual or os.path.basename(self.pasta_atual)
            return {
                "sucesso": True,
                "repo": repo,
                "branch": branch_atual(),
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
        mensagem, sucesso = clonar_repositorio(url, pasta_destino)
        self.log(f"> {mensagem}")

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
        mensagem, sucesso = fetch()
        self.log(f"> {mensagem}")
        return sucesso

    def executar_pull(self):
        self.log("> Executando pull...")
        mensagem, sucesso = pull()
        self.log(f"> {mensagem}")
        return sucesso

    def executar_push(self):
        branch = branch_atual()
        self.log(f"> Executando push na branch {branch}...")
        mensagem, sucesso = push(branch)
        self.log(f"> {mensagem}")
        return sucesso

    # ==========================================
    # BRANCHES & MERGE
    # ==========================================
    def obter_branches(self):
        branches = listar_branches()
        return branches or []

    def executar_listar_branches(self):
        return self.obter_branches()

    def executar_criar_branch(self, nome):
        self.log(f"> Criando branch '{nome}'...")
        mensagem, sucesso = criar_branch(nome.strip())
        self.log(f"> {mensagem}")
        return {"sucesso": sucesso, "branch": branch_atual()}

    def executar_trocar_branch(self, nome):
        self.log(f"> Trocando para a branch '{nome}'...")
        mensagem, sucesso = trocar_branch(nome)
        self.log(f"> {mensagem}")
        return {"sucesso": sucesso, "branch": branch_atual()}

    def executar_deletar_branch(self, nome):
        self.log(f"> Deletando branch '{nome}'...")
        mensagem, sucesso = deletar_branch(nome)
        self.log(f"> {mensagem}")
        return sucesso

    def executar_merge(self, nome_branch):
        self.log(f"> Fazendo merge de '{nome_branch}' na branch atual...")
        mensagem, sucesso = merge(nome_branch)
        self.log(f"> {mensagem}")
        return sucesso

    # ==========================================
    # STAGING E COMMIT
    # ==========================================
    def executar_adicionar_e_commit(self, mensagem):
        if not mensagem.strip():
            self.log("> ERRO: Mensagem de commit vazia.")
            return False
            
        add_msg, add_sucesso = adicionar()
        self.log(f"> {add_msg}")
        
        if add_sucesso:
            com_msg, com_sucesso = commit(mensagem)
            self.log(f"> {com_msg}")
            return com_sucesso
        return False

    def executar_adicionar(self):
        self.log("> Adicionando arquivos ao staging...")
        mensagem, sucesso = adicionar()
        self.log(f"> {mensagem}")
        return sucesso

    def executar_commit(self, mensagem):
        if not mensagem.strip():
            self.log("> ERRO: Mensagem de commit vazia.")
            return False

        self.log("> Criando commit...")
        mensagem_commit, sucesso = commit(mensagem.strip())  
        self.log(f"> {mensagem_commit}")
        return sucesso

    def executar_remover_staging(self):
        self.log("> Removendo arquivos do staging...")
        mensagem, sucesso = remover_staging()  
        self.log(f"> {mensagem}")
        return sucesso

    def executar_restaurar(self):
        self.log("> Restaurando alterações de arquivos modificados...")
        mensagem, sucesso = restaurar_alteracoes()  
        self.log(f"> {mensagem}")
        return sucesso

    # ==========================================
    # CONSULTAS (Status, Log, Diff, Tags)
    # ==========================================
    def executar_status(self):
        resultado = status()  
        self.log(f"> STATUS:\n{resultado}")
        return resultado

    def executar_branches(self):
        resultado = listar_branches()  
        self.log(f"> BRANCHES:\n{resultado}")
        return resultado

    def executar_historico(self):
        resultado = historico()  
        self.log(f"> HISTÓRICO (LOG):\n{resultado}")
        return resultado

    def executar_diff(self):
        resultado = diff()  
        if not resultado or not str(resultado).strip():
            resultado = "Nenhuma diferença encontrada."

        self.log(f"> DIFF:\n{resultado}")
        return resultado

    def obter_tags(self):
        resultado = listar_tags()  
        self.log(f"> TAGS:\n{resultado}")
        return resultado

    # ==========================================
    # STASH
    # ==========================================
    def executar_stash(self):
        self.log("> Guardando alterações em Stash...")
        mensagem, sucesso = stash()  
        self.log(f"> {mensagem}")
        return sucesso

    def executar_stash_pop(self):
        self.log("> Aplicando Stash (Pop)...")
        mensagem, sucesso = stash_pop()  
        self.log(f"> {mensagem}")
        return sucesso

    def obter_stashes(self):
        resultado = listar_stash()  
        return resultado or ""

    def executar_tags(self):
        resultado = listar_tags()  
        return resultado or ""
