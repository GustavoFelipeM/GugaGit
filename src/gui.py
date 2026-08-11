import os
import customtkinter as ctk
from tkinter import filedialog

from src.git_manager import (
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
    listar_tags,
    git_instalado
)

from src.dialogs import confirmar

from src.config import (
    aplicar_icone,
    salvar_ultimo_repositorio,
    obter_ultimo_repositorio
)

class GugaGitApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("GugaGit")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        aplicar_icone(self)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.pasta_atual = None

        self.criar_interface()

        if not git_instalado():
            self.withdraw()
            self.mostrar_git_nao_instalado()
            return

        
        ultimo = obter_ultimo_repositorio()

        if (
            ultimo
            and os.path.isdir(ultimo)
            and os.path.isdir(os.path.join(ultimo, ".git"))
        ):
            self.abrir_repositorio(ultimo)
        else:
            self.mostrar_tela_inicial()

    # ==========================================================
    # INTERFACE PRINCIPAL
    # ==========================================================

    def criar_interface(self):

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ======================================================
        # SIDEBAR
        # ======================================================

        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)

        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="GugaGit",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        self.logo.pack(
            padx=20,
            pady=(30, 5)
        )

        self.logo_subtitulo = ctk.CTkLabel(
            self.sidebar,
            text="Git sem complicação",
            text_color="gray"
        )

        self.logo_subtitulo.pack(
            pady=(0, 30)
        )

        self.btn_repositorio = ctk.CTkButton(
            self.sidebar,
            text="📁 Repositório",
            command=self.trocar_repositorio
        )

        self.btn_repositorio.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.btn_atualizar = ctk.CTkButton(
            self.sidebar,
            text="🔄 Atualizar",
            command=self.executar_fetch
        )

        self.btn_atualizar.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.btn_clonar = ctk.CTkButton(
        self.sidebar,
        text="🔗 Clonar repositório",
        command=self.janela_clonar
        )

        self.btn_clonar.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.sidebar_separator = ctk.CTkFrame(
            self.sidebar,
            height=2
        )

        self.sidebar_separator.pack(
            fill="x",
            padx=20,
            pady=20
        )

        self.label_branch_sidebar = ctk.CTkLabel(
            self.sidebar,
            text="Branch atual",
            text_color="gray"
        )

        self.label_branch_sidebar.pack(
            pady=(5, 0)
        )

        self.label_branch = ctk.CTkLabel(
            self.sidebar,
            text="Nenhum repositório",
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            ),
            wraplength=190
        )

        self.label_branch.pack(
            padx=15,
            pady=(5, 20)
        )

        self.label_repo = ctk.CTkLabel(
            self.sidebar,
            text="",
            text_color="gray",
            wraplength=190
        )

        self.label_repo.pack(
            padx=15
        )

        # ======================================================
        # CONTEÚDO
        # ======================================================

        self.conteudo = ctk.CTkFrame(
            self,
            corner_radius=0
        )

        self.conteudo.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.conteudo.grid_columnconfigure(0, weight=1)
        self.conteudo.grid_columnconfigure(1, weight=1)

        self.conteudo.grid_rowconfigure(1, weight=1)

        # ======================================================
        # HEADER
        # ======================================================

        self.header = ctk.CTkFrame(
            self.conteudo,
            fg_color="transparent"
        )

        self.header.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=30,
            pady=(25, 15)
        )

        self.titulo = ctk.CTkLabel(
            self.header,
            text="GugaGit",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        )

        self.titulo.pack(
            anchor="w"
        )

        self.caminho = ctk.CTkLabel(
            self.header,
            text="Nenhum repositório aberto",
            text_color="gray"
        )

        self.caminho.pack(
            anchor="w",
            pady=(3, 0)
        )

        # ======================================================
        # ÁREA DE FERRAMENTAS
        # ======================================================

        self.acoes_frame = ctk.CTkFrame(
            self.conteudo
        )

        self.acoes_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(25, 10),
            pady=(0, 25)
        )

        self.acoes_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.acoes_frame.grid_rowconfigure(
            1,
            weight=1
        )

        self.acoes_titulo = ctk.CTkLabel(
            self.acoes_frame,
            text="Ferramentas",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        self.acoes_titulo.grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(15, 10)
        )

        self.acoes = ctk.CTkScrollableFrame(
            self.acoes_frame,
            fg_color="transparent"
        )

        self.acoes.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=8,
            pady=(0, 10)
        )

        # ======================================================
        # RESULTADO
        # ======================================================

        self.output_frame = ctk.CTkFrame(
            self.conteudo
        )

        self.output_frame.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(10, 25),
            pady=(0, 25)
        )

        self.output_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.output_frame.grid_rowconfigure(
            1,
            weight=1
        )

        self.output_titulo = ctk.CTkLabel(
            self.output_frame,
            text="Resultado",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        self.output_titulo.grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(15, 10)
        )

        self.output = ctk.CTkTextbox(
            self.output_frame,
            wrap="word",
            font=ctk.CTkFont(
                size=13
            )
        )

        self.output.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12)
        )

    # ==========================================================
    # TELA INICIAL
    # ==========================================================

    def mostrar_tela_inicial(self):

        self.limpar_acoes()

        titulo = ctk.CTkLabel(
            self.acoes,
            text="Começar",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        titulo.pack(
            anchor="w",
            padx=10,
            pady=(10, 5)
        )

        descricao = ctk.CTkLabel(
            self.acoes,
            text="Abra um repositório existente ou clone um novo.",
            text_color="gray",
            wraplength=400
        )

        descricao.pack(
            anchor="w",
            padx=10,
            pady=(0, 20)
        )

        btn_abrir = ctk.CTkButton(
            self.acoes,
            text="📁 Abrir repositório",
            height=45,
            command=self.trocar_repositorio
        )

        btn_abrir.pack(
            fill="x",
            padx=10,
            pady=7
        )

        btn_clonar = ctk.CTkButton(
            self.acoes,
            text="🔗 Clonar repositório",
            height=45,
            command=self.janela_clonar
        )

        btn_clonar.pack(
            fill="x",
            padx=10,
            pady=7
        )

    # ==========================================================
    # MENU
    # ==========================================================

    def mostrar_menu(self):

        self.limpar_acoes()

        self.criar_grupo(
            "🚀 PRINCIPAL",
            [
                ("🔄 Atualizar", self.executar_fetch),
                ("⬇ Pull", self.executar_pull),
                ("⬆ Push", self.janela_push),
                ("🌿 Trocar branch", self.janela_trocar_branch),
                ("＋ Nova branch", self.janela_criar_branch),
                ("✓ Adicionar", self.executar_adicionar),
                ("✓ Commit", self.janela_commit),
            ]
        )

        self.criar_grupo(
            "💾 ALTERAÇÕES",
            [
                ("Guardar Stash", self.executar_stash),
                ("Aplicar Stash", self.executar_stash_pop),
                ("Restaurar", self.executar_restaurar),
                ("Remover staging", self.executar_remover_staging),
            ]
        )

        self.criar_grupo(
            "🔍 CONSULTAR",
            [
                ("Status", self.mostrar_status),
                ("Branches", self.mostrar_branches),
                ("Histórico", self.mostrar_historico),
                ("Diff", self.mostrar_diff),
                ("Stashes", self.mostrar_stashes),
                ("Tags", self.mostrar_tags),
            ]
        )

        self.criar_grupo(
            "⚙ AVANÇADO",
            [
                ("Merge", self.janela_merge),
                ("Deletar branch", self.janela_deletar_branch),
            ]
        )

    def criar_grupo(self, titulo, botoes):

        frame = ctk.CTkFrame(
            self.acoes
        )

        frame.pack(
            fill="x",
            padx=5,
            pady=7
        )

        label = ctk.CTkLabel(
            frame,
            text=titulo,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            )
        )

        label.pack(
            anchor="w",
            padx=15,
            pady=(12, 8)
        )

        botoes_frame = ctk.CTkFrame(
            frame,
            fg_color="transparent"
        )

        botoes_frame.pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )

        # Duas colunas em vez de uma fila enorme.
        for coluna in range(2):
            botoes_frame.grid_columnconfigure(
                coluna,
                weight=1
            )

        for i, (texto, comando) in enumerate(botoes):

            linha = i // 2
            coluna = i % 2

            button = ctk.CTkButton(
                botoes_frame,
                text=texto,
                command=comando,
                height=38
            )

            button.grid(
                row=linha,
                column=coluna,
                sticky="ew",
                padx=4,
                pady=4
            )

    # ==========================================================
    # REPOSITÓRIO
    # ==========================================================

    def trocar_repositorio(self):

        pasta = filedialog.askdirectory(
            title="Selecione um repositório Git"
        )

        if not pasta:
            return

        self.abrir_repositorio(pasta)

    def abrir_repositorio(self, pasta):

        pasta_git = os.path.join(
            pasta,
            ".git"
        )

        if not os.path.isdir(pasta_git):

            self.mostrar_resultado(
                "A pasta selecionada não parece ser um repositório Git."
            )

            return

        try:

            os.chdir(pasta)

            self.pasta_atual = pasta

            salvar_ultimo_repositorio(pasta)

            self.label_repo.configure(
                text=os.path.basename(pasta)
            )

            self.caminho.configure(
                text=pasta
            )

            self.atualizar_informacoes()

            self.mostrar_menu()

        except Exception as erro:

            self.mostrar_resultado(
                f"Erro ao abrir repositório:\n\n{erro}"
            )

    # ==========================================================
    # ATUALIZAÇÃO
    # ==========================================================

    def atualizar_informacoes(self):

        if not self.pasta_atual:
            return

        try:

            branch = branch_atual()

            self.label_branch.configure(
                text=branch if branch else "Sem branch"
            )

        except Exception as erro:

            self.mostrar_resultado(
                f"Erro:\n{erro}"
            )

    def executar_fetch(self):

        mensagem, sucesso = fetch()

        self.mostrar_resultado(mensagem)

        if sucesso:
            self.atualizar_informacoes()

    # ==========================================================
    # BRANCH
    # ==========================================================

    def janela_criar_branch(self):

        self.janela_texto(
            "Criar branch",
            "Nome da nova branch:",
            self.executar_criar_branch
        )

    def executar_criar_branch(self, nome):

        if not nome.strip():
            return

        mensagem, sucesso = criar_branch(
            nome.strip()
        )

        self.mostrar_resultado(mensagem)

        if sucesso:
            self.atualizar_informacoes()

    def janela_trocar_branch(self):

        branches = listar_branches()

        if not branches:

            self.mostrar_resultado(
                "Não foi possível listar as branches."
            )

            return

        self.janela_selecao(
            "Trocar branch",
            "Selecione a branch:",
            branches,
            self.executar_trocar_branch
        )

    def executar_trocar_branch(self, nome):

        mensagem, sucesso = trocar_branch(nome)

        self.mostrar_resultado(mensagem)

        if sucesso:
            self.atualizar_informacoes()

    def janela_deletar_branch(self):

        branches = listar_branches()

        if not branches:
            return

        atual = branch_atual()

        branches = [
            branch
            for branch in branches
            if branch != atual
        ]

        if not branches:

            self.mostrar_resultado(
                "Não há outra branch para deletar."
            )

            return

        self.janela_selecao(
            "Deletar branch",
            "Selecione a branch:",
            branches,
            self.confirmar_deletar_branch
        )

    def confirmar_deletar_branch(self, nome):

        confirmado = confirmar(
            self,
            "⚠️ Deletar branch",
            f"Tem certeza que deseja deletar a branch:\n\n"
            f"{nome}\n\n"
            f"Essa ação não deve ser feita sem certeza."
        )

        if not confirmado:
            return

        mensagem, sucesso = deletar_branch(nome)

        self.mostrar_resultado(mensagem)

        if sucesso:
            self.atualizar_informacoes()

    # ==========================================================
    # COMMIT / PUSH
    # ==========================================================

    def executar_adicionar(self):

        mensagem, sucesso = adicionar()

        self.mostrar_resultado(mensagem)

    def janela_commit(self):

        self.janela_texto(
            "Commit",
            "Mensagem do commit:",
            self.executar_commit
        )

    def executar_commit(self, mensagem):

        if not mensagem.strip():
            return

        resultado, sucesso = commit(
            mensagem.strip()
        )

        self.mostrar_resultado(resultado)

    def janela_push(self):

        branch = branch_atual()

        confirmado = confirmar(
            self,
            "⬆ Push",
            f"Deseja fazer push da branch:\n\n{branch}?"
        )

        if not confirmado:
            return

        mensagem, sucesso = push(branch)

        self.mostrar_resultado(mensagem)

    def executar_pull(self):

        confirmado = confirmar(
            self,
            "⬇ Pull",
            "Deseja atualizar sua branch com o repositório remoto?"
        )

        if not confirmado:
            return

        mensagem, sucesso = pull()

        self.mostrar_resultado(mensagem)

        if sucesso:
            self.atualizar_informacoes()

    # ==========================================================
    # ALTERAÇÕES
    # ==========================================================

    def executar_restaurar(self):

        confirmado = confirmar(
            self,
            "⚠️ Restaurar alterações",
            "Isso irá descartar as alterações atuais nos arquivos.\n\n"
            "Tem certeza que deseja continuar?"
        )

        if not confirmado:
            return

        mensagem, sucesso = restaurar_alteracoes()

        self.mostrar_resultado(mensagem)

    def executar_remover_staging(self):

        confirmado = confirmar(
            self,
            "Remover staging",
            "Deseja remover todos os arquivos do staging?"
        )

        if not confirmado:
            return

        mensagem, sucesso = remover_staging()

        self.mostrar_resultado(mensagem)

    def executar_stash(self):

        mensagem, sucesso = stash()

        self.mostrar_resultado(mensagem)

    def executar_stash_pop(self):

        confirmado = confirmar(
            self,
            "Aplicar stash",
            "Deseja aplicar o stash mais recente?\n\n"
            "Pode haver conflitos."
        )

        if not confirmado:
            return

        mensagem, sucesso = stash_pop()

        self.mostrar_resultado(mensagem)

    # ==========================================================
    # CONSULTAS
    # ==========================================================

    def mostrar_status(self):

        resultado = status()

        self.mostrar_resultado(
            resultado if resultado else "Nenhum resultado."
        )

    def mostrar_branches(self):

        branches = listar_branches()

        if branches is None:

            self.mostrar_resultado(
                "Erro ao listar branches."
            )

            return

        texto = "\n".join(branches)

        self.mostrar_resultado(
            "BRANCHES\n\n" + texto
        )

    def mostrar_historico(self):

        resultado = historico()

        self.mostrar_resultado(
            resultado
            if resultado
            else "Nenhum histórico encontrado."
        )

    def mostrar_diff(self):

        resultado = diff()

        self.mostrar_resultado(
            resultado
            if resultado
            else "Nenhuma diferença encontrada."
        )

    def mostrar_stashes(self):

        resultado = listar_stash()

        self.mostrar_resultado(
            resultado
            if resultado
            else "Nenhum stash encontrado."
        )

    def mostrar_tags(self):

        resultado = listar_tags()

        self.mostrar_resultado(
            resultado
            if resultado
            else "Nenhuma tag encontrada."
        )

    # ==========================================================
    # MERGE
    # ==========================================================

    def janela_merge(self):

        branches = listar_branches()

        if not branches:
            return

        atual = branch_atual()

        branches = [
            branch
            for branch in branches
            if branch != atual
        ]

        if not branches:

            self.mostrar_resultado(
                "Não existem outras branches para fazer merge."
            )

            return

        self.janela_selecao(
            "Merge",
            f"Branch atual: {atual}\n\n"
            "Escolha a branch que deseja incorporar:",
            branches,
            self.confirmar_merge
        )

    def confirmar_merge(self, nome):

        confirmado = confirmar(
            self,
            "⚠️ Merge",
            f"Deseja fazer merge de:\n\n"
            f"{nome}\n\n"
            f"na branch atual ({branch_atual()})?"
        )

        if not confirmado:
            return

        mensagem, sucesso = merge(nome)

        self.mostrar_resultado(mensagem)

    # ==========================================================
    # CLONE
    # ==========================================================

    def janela_clonar(self):

        janela = ctk.CTkToplevel(self)

        aplicar_icone(janela)

        janela.title("Clonar repositório")
        janela.geometry("650x360")
        janela.resizable(False, False)

        janela.grab_set()

        janela.grid_columnconfigure(
            0,
            weight=1
        )

        titulo = ctk.CTkLabel(
            janela,
            text="Clonar repositório",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        titulo.grid(
            row=0,
            column=0,
            pady=(30, 8)
        )

        descricao = ctk.CTkLabel(
            janela,
            text="Informe a URL e escolha onde o repositório será clonado.",
            text_color="gray"
        )

        descricao.grid(
            row=1,
            column=0,
            pady=(0, 25)
        )

        # ======================================================
        # URL
        # ======================================================

        url_frame = ctk.CTkFrame(
            janela,
            fg_color="transparent"
        )

        url_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=40,
            pady=8
        )

        url_frame.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            url_frame,
            text="URL do repositório"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        entrada_url = ctk.CTkEntry(
            url_frame,
            placeholder_text="https://github.com/usuario/repositorio.git",
            height=38
        )

        entrada_url.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        # ======================================================
        # PASTA
        # ======================================================

        pasta_frame = ctk.CTkFrame(
            janela,
            fg_color="transparent"
        )

        pasta_frame.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=40,
            pady=8
        )

        pasta_frame.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            pasta_frame,
            text="Pasta onde clonar"
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 5)
        )

        pasta_var = ctk.StringVar()

        entrada_pasta = ctk.CTkEntry(
            pasta_frame,
            textvariable=pasta_var,
            height=38
        )

        entrada_pasta.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(0, 8)
        )

        def selecionar_pasta():

            pasta = filedialog.askdirectory(
                title="Escolha onde clonar"
            )

            if pasta:
                pasta_var.set(pasta)

        ctk.CTkButton(
            pasta_frame,
            text="📁 Escolher",
            width=110,
            height=38,
            command=selecionar_pasta
        ).grid(
            row=1,
            column=1
        )

        # ======================================================
        # BOTÕES
        # ======================================================

        botoes = ctk.CTkFrame(
            janela,
            fg_color="transparent"
        )

        botoes.grid(
            row=4,
            column=0,
            pady=(20, 25)
        )

        def cancelar():

            janela.destroy()

        def clonar():

            url = entrada_url.get().strip()
            pasta = pasta_var.get().strip()

            if not url:

                self.mostrar_resultado(
                    "Informe a URL do repositório."
                )

                return

            if not pasta:

                self.mostrar_resultado(
                    "Escolha a pasta onde o repositório será clonado."
                )

                return

            mensagem, sucesso = clonar_repositorio(
                url,
                pasta
            )

            if not sucesso:

                self.mostrar_resultado(mensagem)
                return

            nome_repo = url.rstrip("/").split("/")[-1]

            if nome_repo.endswith(".git"):
                nome_repo = nome_repo[:-4]

            nova_pasta = os.path.join(
                pasta,
                nome_repo
            )

            janela.destroy()

            self.mostrar_resultado(mensagem)

            if os.path.isdir(
                os.path.join(
                    nova_pasta,
                    ".git"
                )
            ):
                self.abrir_repositorio(
                    nova_pasta
                )

        ctk.CTkButton(
            botoes,
            text="Cancelar",
            width=120,
            height=40,
            fg_color="transparent",
            border_width=1,
            command=cancelar
        ).pack(
            side="left",
            padx=6
        )

        ctk.CTkButton(
            botoes,
            text="🔗 Clonar",
            width=140,
            height=40,
            command=clonar
        ).pack(
            side="left",
            padx=6
        )

        entrada_url.focus()

        janela.bind(
            "<Return>",
            lambda event: clonar()
        )

    # ==========================================================
    # JANELAS AUXILIARES
    # ==========================================================

    def janela_texto(
        self,
        titulo,
        descricao,
        callback
    ):

        janela = ctk.CTkToplevel(self)

        aplicar_icone(janela)

        janela.title(titulo)
        janela.geometry("500x250")
        janela.resizable(False, False)

        janela.grab_set()

        label = ctk.CTkLabel(
            janela,
            text=descricao,
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            wraplength=420
        )

        label.pack(
            pady=(30, 15)
        )

        entrada = ctk.CTkEntry(
            janela,
            width=400,
            height=38
        )

        entrada.pack(
            pady=10
        )

        entrada.focus()

        def executar():

            valor = entrada.get()

            if not valor.strip():
                return

            janela.destroy()

            callback(valor)

        ctk.CTkButton(
            janela,
            text="Confirmar",
            command=executar
        ).pack(
            pady=20
        )

        janela.bind(
            "<Return>",
            lambda event: executar()
        )

    def janela_selecao(
        self,
        titulo,
        descricao,
        opcoes,
        callback
    ):

        janela = ctk.CTkToplevel(self)

        aplicar_icone(janela)

        janela.title(titulo)
        janela.geometry("500x300")
        janela.resizable(False, False)

        janela.grab_set()

        label = ctk.CTkLabel(
            janela,
            text=descricao,
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            wraplength=430
        )

        label.pack(
            pady=(30, 15)
        )

        combo = ctk.CTkComboBox(
            janela,
            values=opcoes,
            width=400,
            height=38
        )

        combo.pack(
            pady=10
        )

        combo.set(opcoes[0])

        def executar():

            valor = combo.get()

            janela.destroy()

            callback(valor)

        ctk.CTkButton(
            janela,
            text="Confirmar",
            command=executar
        ).pack(
            pady=20
        )

        janela.bind(
            "<Return>",
            lambda event: executar()
        )

    # ==========================================================
    # UTILIDADES
    # ==========================================================

    def limpar_acoes(self):

        for widget in self.acoes.winfo_children():
            widget.destroy()

    def mostrar_resultado(self, texto):

        self.output.delete(
            "1.0",
            "end"
        )

        if texto is None:
            texto = "Nenhum resultado."

        self.output.insert(
            "1.0",
            str(texto)
        )

    def mostrar_git_nao_instalado(self):

        janela = ctk.CTkToplevel(self)

        aplicar_icone(janela)

        janela.title("Git não encontrado")
        janela.geometry("500x280")
        janela.resizable(False, False)

        janela.grab_set()

        titulo = ctk.CTkLabel(
            janela,
            text="Git não encontrado",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        titulo.pack(
            pady=(35, 10)
        )

        descricao = ctk.CTkLabel(
            janela,
            text=(
                "O GugaGit precisa do Git instalado "
                "para funcionar.\n\n"
                "Instale o Git e abra o GugaGit novamente."
            ),
            text_color="gray",
            justify="center"
        )

        descricao.pack(
            pady=10
        )

        botoes = ctk.CTkFrame(
            janela,
            fg_color="transparent"
        )

        botoes.pack(
            pady=25
        )

        btn_fechar = ctk.CTkButton(
            botoes,
            text="Fechar",
            width=120,
            command=self.destroy
        )

        btn_fechar.pack(
            side="left",
            padx=5
        )


if __name__ == "__main__":

    app = GugaGitApp()

    app.mainloop()

