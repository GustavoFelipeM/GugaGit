import os
from typing import Optional, List, Dict, Any
from src.infrastructure.git_cli import executar_e_tratar, interface_git
from src.core.types import GitResult

class StagingService:
    def status(self) -> GitResult:
        """Executa 'git status' e retorna o resultado bruto."""
        resultado = interface_git(["git", "status"])
        if resultado.returncode == 0:
            return GitResult(sucesso=True, mensagem="Status obtido com sucesso.", dados=resultado.stdout)
        return GitResult(sucesso=False, mensagem="Erro ao obter status.", erro_detalhado=resultado.stderr)

    def obter_arquivos_status(self) -> GitResult:
        """Retorna uma lista estruturada dos arquivos modificados/não rastreados."""
        resultado = interface_git(["git", "status", "--porcelain"])
        if resultado.returncode != 0:
            return GitResult(sucesso=False, mensagem="Erro ao consultar status dos arquivos.", dados=[], erro_detalhado=resultado.stderr)

        if not resultado.stdout.strip():
            return GitResult(sucesso=True, mensagem="Nenhum arquivo modificado.", dados=[])

        arquivos = []
        for linha in resultado.stdout.splitlines():
            if len(linha) < 3:
                continue
            status_staged, status_unstaged = linha[0], linha[1]
            arquivo = linha[3:].strip().replace('"', '')
            is_staged = status_staged not in (' ', '?')
            arquivos.append({
                "caminho": arquivo,
                "staged": is_staged,
                "status_staged": status_staged,
                "status_unstaged": status_unstaged
            })

        return GitResult(sucesso=True, mensagem="Arquivos analisados com sucesso.", dados=arquivos)

    def adicionar_todos(self) -> GitResult:
        """Adiciona todas as alterações locais ao staging (git add .)."""
        msg, ok, erro = executar_e_tratar(["git", "add", "."], "Arquivos adicionados!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def adicionar_selecionados(self, arquivos: List[str]) -> GitResult:
        """Executa git add apenas nos arquivos especificados."""
        if not arquivos:
            return GitResult(sucesso=True, mensagem="Nenhum arquivo selecionado.")
        msg, ok, erro = executar_e_tratar(["git", "add"] + arquivos, "Arquivos selecionados adicionados ao staging!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def remover_staging_todos(self) -> GitResult:
        """Remove todas as alterações da área de staging (unstage)."""
        msg, ok, erro = executar_e_tratar(["git", "restore", "--staged", "."], "Staging removido com sucesso!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def remover_staging_selecionados(self, arquivos: List[str]) -> GitResult:
        """Executa git restore --staged apenas nos arquivos especificados."""
        if not arquivos:
            return GitResult(sucesso=True, mensagem="Nenhum arquivo selecionado.")
        msg, ok, erro = executar_e_tratar(["git", "restore", "--staged"] + arquivos, "Arquivos removidos do staging!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def commit(self, mensagem: str) -> GitResult:
        """Cria um novo commit com a mensagem especificada."""
        if not mensagem.strip():
            return GitResult(sucesso=False, mensagem="A mensagem de commit não pode estar vazia.")
        msg, ok, erro = executar_e_tratar(["git", "commit", "-m", mensagem], "Commit realizado!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    def diff(self, caminho: str = None, staged: bool = False) -> GitResult:
        """
        Retorna as diferenças do repositório ou de um arquivo específico.
        Trata arquivos no Staging (--staged) e novos (untracked).
        """
        cmd = ["git", "diff"]
        
        if staged:
            cmd.append("--staged")

        if caminho:
            cmd.extend(["--", caminho])

        res = interface_git(cmd)

        if res.returncode == 0 and not res.stdout.strip() and caminho and not staged:
            if os.path.exists(caminho):
                null_device = "NUL" if os.name == "nt" else "/dev/null"
                res_untracked = interface_git(["git", "diff", "--no-index", null_device, caminho])
                if res_untracked.stdout:
                    return GitResult(sucesso=True, mensagem="Diff de arquivo novo gerado.", dados=res_untracked.stdout)

        if res.returncode == 0:
            stdout = res.stdout.strip()
            if not stdout:
                return GitResult(sucesso=True, mensagem="Nenhuma diferença encontrada.", dados="")
            return GitResult(sucesso=True, mensagem="Diff retornado com sucesso.", dados=res.stdout)
        
        return GitResult(sucesso=False, mensagem="Erro ao obter diff.", erro_detalhado=res.stderr)

    def obter_estatisticas_alteracoes(self) -> GitResult:
        """
        Retorna o número de linhas adicionadas e removidas por arquivo (git diff --numstat).
        """
        # Obter contagem do Working Tree e do Staging
        res_wt = interface_git(["git", "diff", "--numstat"])
        res_st = interface_git(["git", "diff", "--staged", "--numstat"])

        stats: Dict[str, int] = {}

        for res in [res_wt, res_st]:
            if res.returncode == 0 and res.stdout.strip():
                for linha in res.stdout.strip().split("\n"):
                    partes = linha.split("\t")
                    if len(partes) == 3:
                        adds, dels, arquivo = partes
                        adds_num = int(adds) if adds.isdigit() else 0
                        dels_num = int(dels) if dels.isdigit() else 0
                        stats[arquivo] = stats.get(arquivo, 0) + (adds_num + dels_num)

        return GitResult(sucesso=True, mensagem="Estatísticas obtidas.", dados=stats)

    def obter_resumo_alteracoes(self) -> GitResult:
        """Retorna resumo detalhado de alterações separadas por Working Tree e Staged."""
        res_status = self.obter_arquivos_status()
        if not res_status.sucesso:
            return res_status

        arquivos_status = res_status.dados if isinstance(res_status.dados, list) else []
        if not arquivos_status:
            return GitResult(
                sucesso=True,
                mensagem="Nenhuma alteração pendente.",
                dados={"working_tree": [], "staged": [], "total": 0}
            )

        res_wt_numstat = interface_git(["git", "diff", "--numstat"])
        res_st_numstat = interface_git(["git", "diff", "--staged", "--numstat"])

        numstat_map = {}

        def parse_numstat(stdout, is_staged):
            for linha in stdout.splitlines():
                if not linha.strip():
                    continue
                partes = linha.split("\t")
                if len(partes) >= 3:
                    adds = int(partes[0]) if partes[0].isdigit() else 0
                    dels = int(partes[1]) if partes[1].isdigit() else 0
                    caminho = partes[2].strip()
                    numstat_map[(caminho, is_staged)] = adds + dels

        if res_wt_numstat.returncode == 0 and res_wt_numstat.stdout:
            parse_numstat(res_wt_numstat.stdout, False)
        if res_st_numstat.returncode == 0 and res_st_numstat.stdout:
            parse_numstat(res_st_numstat.stdout, True)

        working_tree = []
        staged = []

        for item in arquivos_status:
            caminho = item["caminho"]
            eh_staged = item.get("staged", False)
            status_staged = item.get("status_staged", " ")
            status_unstaged = item.get("status_unstaged", " ")

            cod = status_staged if eh_staged else status_unstaged
            if "?" in (status_staged + status_unstaged):
                status_letra = "U"
            else:
                status_letra = cod.strip() if cod.strip() else "M"

            total_alt = numstat_map.get((caminho, eh_staged), 0)
            if total_alt == 0:
                total_alt = 1

            dados_arquivo = {
                "caminho": caminho,
                "alteracoes": total_alt,
                "staged": eh_staged,
                "status": status_letra,
                "status_staged": status_staged,
                "status_unstaged": status_unstaged
            }

            if eh_staged:
                staged.append(dados_arquivo)
            else:
                working_tree.append(dados_arquivo)

        total_geral = len(working_tree) + len(staged)
        return GitResult(
            sucesso=True,
            mensagem="Resumo de alterações gerado.",
            dados={
                "working_tree": working_tree,
                "staged": staged,
                "total": total_geral
            }
        )

    def restaurar_alteracoes(self) -> GitResult:
        """Descarte alterações não salvas no diretório de trabalho."""
        msg, ok, erro = executar_e_tratar(["git", "restore", "."], "Desfeito com sucesso!")
        return GitResult(sucesso=ok, mensagem=msg, erro_detalhado=erro if not ok else None)

    