/* ==========================================================================
   1. GERENCIAMENTO DO TERMINAL E LOGS
   ========================================================================== */
function getTerminalLines() {
    return document.getElementById('terminal-lines');
}

function clearTerminal() {
    const terminal = getTerminalLines();
    if (terminal) terminal.innerHTML = '';
}

function logTerminal(mensagem) {
    const terminal = getTerminalLines();
    if (!terminal) return;

    const novaLinha = document.createElement('div');
    novaLinha.style.color = "#a1a1aa";
    novaLinha.style.wordBreak = "break-all";

    // Trata caracteres especiais para não quebrar o HTML e insere quebras de linha
    const textoFormatado = String(mensagem)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\n/g, '<br>');

    novaLinha.innerHTML = textoFormatado;
    terminal.appendChild(novaLinha);
    terminal.scrollTop = terminal.scrollHeight;
}

async function enviarComandoTerminal(event) {
    if (event.key === 'Enter') {
        const input = document.getElementById('input-comando-livre');
        const comando = input?.value.trim();

        if (!comando) return;

        input.value = '';
        await pywebview.api.executar_comando_customizado(comando);
        await atualizarCabecalhoInicial();
    }
}

/* ==========================================================================
   2. MODAIS E INTERAÇÕES COM O USUÁRIO
   ========================================================================== */
function abrirModal({ titulo, mensagem, placeholder = '', valorInicial = '', mostrarInput = true }) {
    return new Promise((resolve) => {
        const overlay = document.getElementById('modal-overlay');
        const tituloEl = document.getElementById('modal-title');
        const mensagemEl = document.getElementById('modal-message');
        const inputEl = document.getElementById('modal-input');
        const btnOk = document.getElementById('modal-ok');
        const btnCancel = document.getElementById('modal-cancel');

        tituloEl.textContent = titulo;
        mensagemEl.textContent = mensagem;
        inputEl.value = valorInicial;
        inputEl.placeholder = placeholder;
        inputEl.style.display = mostrarInput ? 'block' : 'none';
        overlay.style.display = 'flex';

        const fechar = (resultado) => {
            overlay.style.display = 'none';
            btnOk.onclick = null;
            btnCancel.onclick = null;
            inputEl.onkeydown = null;
            window.removeEventListener('keydown', lidarComEsc);
            resolve(resultado);
        };

        const lidarComEsc = (e) => {
            if (e.key === 'Escape') fechar(null);
        };

        btnCancel.onclick = () => fechar(null);
        btnOk.onclick = () => fechar(mostrarInput ? inputEl.value.trim() : true);

        inputEl.onkeydown = (event) => {
            if (event.key === 'Enter') {
                fechar(inputEl.value.trim());
            }
        };

        window.addEventListener('keydown', lidarComEsc);

        if (mostrarInput) {
            setTimeout(() => {
                inputEl.focus();
                inputEl.select();
            }, 50);
        }
    });
}

async function confirmarAcao(titulo, mensagem) {
    return await abrirModal({ titulo, mensagem, mostrarInput: false });
}

async function solicitarTexto(titulo, mensagem, placeholder = '', valorInicial = '') {
    return await abrirModal({ titulo, mensagem, placeholder, valorInicial, mostrarInput: true });
}

/* ==========================================================================
   3. NAVEGAÇÃO E CONFIGURAÇÕES DE INTERFACE
   ========================================================================== */
function voltarParaDashboard() {
    document.getElementById('view-settings').style.display = 'none';
    document.getElementById('view-dashboard').style.display = 'grid';
    document.getElementById('main-header').style.display = 'flex';

    document.querySelectorAll('.nav-icon').forEach(el => el.classList.remove('active'));
    document.getElementById('nav-repo')?.classList.add('active');
}

async function abrirConfiguracoes() {
    document.getElementById('view-dashboard').style.display = 'none';
    document.getElementById('main-header').style.display = 'none';
    document.getElementById('view-settings').style.display = 'block';

    document.querySelectorAll('.nav-icon').forEach(el => el.classList.remove('active'));
    document.getElementById('nav-config')?.classList.add('active');

    try {
        const config = await pywebview.api.obter_config_git();
        document.getElementById('config-nome').value = config.nome || '';
        document.getElementById('config-email').value = config.email || '';
    } catch (e) {
        console.error("Erro ao obter configurações:", e);
    }
}

function mudarCorDestaque(elemento, corAccent, corEnd) {
    document.querySelectorAll('.color-bubble').forEach(el => el.classList.remove('active'));
    elemento.classList.add('active');

    document.documentElement.style.setProperty('--accent', corAccent);
    document.documentElement.style.setProperty('--gradient-brand', `linear-gradient(135deg, ${corAccent} 0%, ${corEnd} 100%)`);

    localStorage.setItem('gugagit-color-accent', corAccent);
    localStorage.setItem('gugagit-color-end', corEnd);
}

async function escolherPastaPadrao() {
    const pasta = await pywebview.api.selecionar_pasta_para_clone(); 
    if (pasta) {
        document.getElementById('config-dir').value = pasta;
        pastaPadraoClone = pasta;
    }
}

async function salvarTodasConfiguracoes() {
    const nome = document.getElementById('config-nome').value.trim();
    const email = document.getElementById('config-email').value.trim();
    
    limparTerminalAutomaticamente = document.getElementById('config-term-clear').checked;
    localStorage.setItem('gugagit-term-clear', limparTerminalAutomaticamente);
    localStorage.setItem('gugagit-default-dir', pastaPadraoClone);

    voltarParaDashboard();
    
    await executarComTerminalLimpo(async () => {
        logTerminal("> Salvando preferências do GugaGit...");
        if (nome && email) {
            const resposta = await pywebview.api.salvar_config_git(nome, email);
            if(resposta && resposta[1]) {
                logTerminal("> " + resposta[0]);
            }
        }
        logTerminal("> Preferências de interface atualizadas.");
    });
}

/* ==========================================================================
   4. AÇÕES DO GIT
   ========================================================================== */
async function abrirRepositorio() {
    await executarComTerminalLimpo(async () => {
        logTerminal("> Aguardando seleção de pasta...");
        const response = await pywebview.api.abrir_repositorio();
        if (response.sucesso) {
            document.getElementById('lbl-repo').innerText = '📦 ' + response.repo;
            document.getElementById('lbl-branch').innerText = '🔀 ' + response.branch;
            logTerminal("> Workspace carregado: " + response.repo);
        }
    });

    await carregarArquivosModificados();
}

async function atualizarCabecalhoInicial() {
    try {
        const estado = await pywebview.api.obter_estado_atual();
        if (estado && estado.sucesso) {
            document.getElementById('lbl-repo').innerText = '📦 ' + estado.repo;
            document.getElementById('lbl-branch').innerText = '🔀 ' + estado.branch;
        }
    } catch (e) {
        console.error("Erro ao atualizar cabeçalho:", e);
    }
}

function atualizarBranchCabecalho(branch) {
    if (branch) {
        document.getElementById('lbl-branch').innerText = '🔀 ' + branch;
    }
}

async function minimizarJanela() { await pywebview.api.minimizar_janela(); }
async function fecharJanela() { await pywebview.api.fechar_janela(); }
async function executarPull() { await executarComTerminalLimpo(async () => pywebview.api.executar_pull()); }
async function executarPush() { await executarComTerminalLimpo(async () => pywebview.api.executar_push()); }
async function executarFetch() { await executarComTerminalLimpo(async () => pywebview.api.executar_fetch()); }
async function executarStatus() { await executarComTerminalLimpo(async () => pywebview.api.executar_status()); }

async function executarBranches() {
    await executarComTerminalLimpo(async () => {
        const branches = await pywebview.api.executar_listar_branches();
        logTerminal("> BRANCHES:\n" + (branches.length ? branches.join("\n") : "Nenhuma branch encontrada."));
    });
}

async function executarHistorico() { await executarComTerminalLimpo(async () => pywebview.api.executar_historico()); }
async function executarDiff() { await executarComTerminalLimpo(async () => pywebview.api.executar_diff()); }

async function executarStashes() {
    await executarComTerminalLimpo(async () => {
        const stashes = await pywebview.api.obter_stashes();
        logTerminal("> STASHES:\n" + (stashes || "Nenhum stash encontrado."));
    });
}

async function executarTags() {
    await executarComTerminalLimpo(async () => {
        const tags = await pywebview.api.executar_tags();
        logTerminal("> TAGS:\n" + (tags || "Nenhuma tag encontrada."));
    });
}

async function executarAdicionar() { await executarComTerminalLimpo(async () => pywebview.api.executar_adicionar()); }
async function executarStash() { await executarComTerminalLimpo(async () => pywebview.api.executar_stash()); }
async function executarStashPop() { await executarComTerminalLimpo(async () => pywebview.api.executar_stash_pop()); }

async function executarRemoverStaging() {
    const confirmado = await confirmarAcao("Remover staging", "Deseja remover todos os arquivos do staging?");
    if (!confirmado) return;
    await executarComTerminalLimpo(async () => pywebview.api.executar_remover_staging());
    await carregarArquivosModificados();
}

async function executarRestaurar() {
    const confirmado = await confirmarAcao("Restaurar arquivos", "Isso irá descartar as alterações atuais nos arquivos. Continuar?");
    if (!confirmado) return;
    await executarComTerminalLimpo(async () => pywebview.api.executar_restaurar());
    await carregarArquivosModificados();
}

async function criarBranch() {
    const nome = await solicitarTexto("Criar branch", "Nome da nova branch:", "ex: feature/login");
    if (!nome) return;
    await executarComTerminalLimpo(async () => {
        const resposta = await pywebview.api.executar_criar_branch(nome);
        if (resposta && resposta.branch) {
            atualizarBranchCabecalho(resposta.branch);
        }
    });
}

async function trocarBranch() {
    const branches = await pywebview.api.executar_listar_branches();
    if (!branches || !branches.length) {
        logTerminal("> Não foi possível listar as branches.");
        return;
    }

    const nome = await solicitarTexto("Trocar branch", "Digite o nome exato da branch:", "nome-da-branch", branches[0]);
    if (!nome) return;
    await executarComTerminalLimpo(async () => {
        const resposta = await pywebview.api.executar_trocar_branch(nome);
        if (resposta && resposta.branch) {
            atualizarBranchCabecalho(resposta.branch);
        }
    });
    await carregarArquivosModificados();
}

async function mergeBranch() {
    const branches = await pywebview.api.executar_listar_branches();
    if (!branches || !branches.length) {
        logTerminal("> Não existem branches para merge.");
        return;
    }

    const nome = await solicitarTexto("Merge branch", "Digite o nome exato da branch para merge:", "nome-da-branch", branches[0]);
    if (!nome) return;
    await executarComTerminalLimpo(async () => {
        const resposta = await pywebview.api.executar_merge(nome);
        if (resposta && resposta.branch) {
            atualizarBranchCabecalho(resposta.branch);
        }
    });
    await carregarArquivosModificados();
}

async function deletarBranch() {
    const branches = await pywebview.api.executar_listar_branches();
    if (!branches || !branches.length) {
        logTerminal("> Não foi possível listar as branches.");
        return;
    }

    const nome = await solicitarTexto("Deletar branch", "Digite o nome exato da branch para deletar:", "nome-da-branch", branches[0]);
    if (!nome) return;

    const confirmado = await confirmarAcao("Deletar branch", `Tem certeza que deseja deletar a branch ${nome}?`);
    if (!confirmado) return;

    await executarComTerminalLimpo(async () => {
        const resposta = await pywebview.api.executar_deletar_branch(nome);
        if (resposta && resposta.branch) {
            atualizarBranchCabecalho(resposta.branch);
        } else {
            await atualizarCabecalhoInicial();
        }
    });
}

async function clonarRepositorio() {
    const url = await solicitarTexto("Clonar repositório", "URL do repositório:", "https://github.com/usuario/repositorio.git");
    if (!url) return;

    const pasta = await pywebview.api.selecionar_pasta_para_clone();
    if (!pasta) return;

    await executarComTerminalLimpo(async () => pywebview.api.executar_clonar(url, pasta));
}

async function fazerCommit() {
    const input = document.getElementById('input-commit');
    const mensagem = input?.value.trim();
    
    if (!mensagem) {
        logTerminal("> ERRO: Digite uma mensagem de commit.");
        return;
    }
    
    await executarComTerminalLimpo(async () => {
        logTerminal("> Iniciando commit...");
        const sucesso = await pywebview.api.executar_adicionar_e_commit(mensagem);
        if (sucesso && input) {
            input.value = "";
        }
    });

    await carregarArquivosModificados();
}

/* ==========================================================================
   5. GERENCIAMENTO DA LISTA DE STAGING
   ========================================================================== */
async function carregarArquivosModificados() {
    const container = document.getElementById('lista-arquivos-staging');
    if (!container) return;

    try {
        if (!window.pywebview || !window.pywebview.api) {
            container.innerHTML = '<span style="color: #f59e0b; font-size: 11px;">Carregando API do Git...</span>';
            return;
        }

        const arquivos = await window.pywebview.api.obter_arquivos_status();
        container.innerHTML = '';

        if (!arquivos || arquivos.length === 0) {
            container.innerHTML = '<span style="color: #34d399; font-size: 11px;">✓ Nenhuma alteração pendente.</span>';
            return;
        }

        arquivos.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.style.cssText = 'display: flex; align-items: center; gap: 8px; background: rgba(0,0,0,0.4); padding: 6px 8px; border-radius: 6px; border: 1px solid var(--border-color);';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = item.caminho;
            checkbox.checked = item.staged;
            checkbox.dataset.staged = item.staged;
            checkbox.className = 'file-staging-checkbox';
            checkbox.style.cursor = 'pointer';

            const label = document.createElement('span');
            label.textContent = item.caminho;
            label.style.cssText = 'flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #ededed; font-family: "JetBrains Mono", monospace; font-size: 11px;';

            const statusBadge = document.createElement('span');
            const statusTexto = (item.status_unstaged?.trim() || item.status_staged?.trim() || '?');
            statusBadge.textContent = statusTexto;
            statusBadge.style.cssText = 'font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.08); color: #60a5fa;';

            itemDiv.appendChild(checkbox);
            itemDiv.appendChild(label);
            itemDiv.appendChild(statusBadge);
            container.appendChild(itemDiv);
        });
    } catch (erro) {
        console.error("Erro ao carregar status do Git:", erro);
        container.innerHTML = `<span style="color: #f87171; font-size: 11px;">⚠️ Erro ao carregar: ${erro.message || erro}</span>`;
    }
}

function marcarTodosArquivos(marcar) {
    document.querySelectorAll('.file-staging-checkbox').forEach(cb => cb.checked = marcar);
}

async function aplicarStagingSelecionado() {
    const checkboxes = document.querySelectorAll('.file-staging-checkbox');
    const paraAdicionar = [];
    const paraRemover = [];

    checkboxes.forEach(cb => {
        const estavaStaged = cb.dataset.staged === 'true';
        const estaMarcado = cb.checked;

        if (estaMarcado && !estavaStaged) {
            paraAdicionar.push(cb.value);
        } else if (!estaMarcado && estavaStaged) {
            paraRemover.push(cb.value);
        }
    });

    try {
        if (paraAdicionar.length > 0) {
            await window.pywebview.api.executar_adicionar_selecionados(paraAdicionar);
        }
        if (paraRemover.length > 0) {
            await window.pywebview.api.executar_remover_selecionados_staging(paraRemover);
        }
        await carregarArquivosModificados();
    } catch (e) {
        console.error("Erro ao aplicar staging:", e);
    }
}

/* ==========================================================================
   6. INICIALIZAÇÃO DA APLICAÇÃO E EVENTOS
   ========================================================================== */
let limparTerminalAutomaticamente = true;
let pastaPadraoClone = "";

async function executarComTerminalLimpo(acao) {
    if (limparTerminalAutomaticamente) {
        clearTerminal();
    } else {
        logTerminal("> ---------------------------------");
    }
    return await acao();
}

function inicializarBackend() {
    if (typeof logTerminal === 'function') {
        logTerminal("> Conexão com o backend Python estabelecida com sucesso.");
    }
    
    if (window.pywebview?.api?.verificar_git) {
        pywebview.api.verificar_git().then(instalado => {
            if (!instalado && typeof logTerminal === 'function') {
                logTerminal("> ATENÇÃO: Git não encontrado no sistema!");
            }
        });
    }

    if (typeof atualizarCabecalhoInicial === 'function') {
        atualizarCabecalhoInicial();
    }
    
    carregarArquivosModificados();
}

/* ==========================================================================
   7. MODAL DE DIFF E INSPEÇÃO DE ALTERAÇÕES
   ========================================================================== */
async function executarDiff() {
    await abrirModalDiff();
}

async function abrirModalDiff() {
    const modal = document.getElementById('modal-diff');
    if (modal) modal.style.display = 'flex';
    await carregarDiffResumo();
}

function fecharModalDiff() {
    const modal = document.getElementById('modal-diff');
    if (modal) modal.style.display = 'none';
}

function formatarDiffColorido(texto) {
    if (!texto || !texto.trim()) {
        return '<span style="color:#a1a1aa;">Nenhuma diferença encontrada para o item selecionado.</span>';
    }

    const linhas = texto.split('\n');
    return linhas.map(linha => {
        const esc = linha
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        if (linha.startsWith('+') && !linha.startsWith('+++')) {
            return `<div style="background: rgba(34, 197, 94, 0.15); color: #4ade80; padding: 0 4px; border-left: 3px solid #22c55e;">${esc}</div>`;
        } else if (linha.startsWith('-') && !linha.startsWith('---')) {
            return `<div style="background: rgba(239, 68, 68, 0.15); color: #f87171; padding: 0 4px; border-left: 3px solid #ef4444;">${esc}</div>`;
        } else if (linha.startsWith('@@')) {
            return `<div style="color: #60a5fa; font-weight: bold; background: rgba(96, 165, 250, 0.1); padding: 2px 4px; margin: 4px 0;">${esc}</div>`;
        } else if (linha.startsWith('diff --git') || linha.startsWith('index ')) {
            return `<div style="color: #a1a1aa; font-weight: bold;">${esc}</div>`;
        }
        return `<div style="color: #d4d4d8;">${esc}</div>`;
    }).join('');
}

async function carregarDiffResumo() {
    const container = document.getElementById('diff-lista-container');
    const contentArea = document.getElementById('diff-content-area');
    if (!container) return;

    container.innerHTML = '<span style="color: var(--text-secondary); font-size: 11px;">Carregando alterações...</span>';

    try {
        const res = await pywebview.api.obter_resumo_alteracoes();
        const dados = res.dados || { working_tree: [], staged: [], total: 0 };

        container.innerHTML = '';

        if (dados.total === 0) {
            container.innerHTML = `
                <div style="padding: 12px; background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.2); border-radius: 8px; font-size: 12px; color: #4ade80;">
                    🟢 Nenhuma alteração pendente no repositório. O Working Tree está limpo.
                </div>
            `;
            if (contentArea) {
                contentArea.innerHTML = '<span style="color:#a1a1aa;">O repositório não possui diferenças pendentes no momento.</span>';
            }
            return;
        }

        const renderGrupo = (titulo, arquivos, ehStaged) => {
            const grupoDiv = document.createElement('div');
            grupoDiv.style.cssText = 'display: flex; flex-direction: column; gap: 6px;';

            const header = document.createElement('div');
            header.style.cssText = 'font-size: 11px; font-weight: bold; color: var(--accent); font-family: "JetBrains Mono", monospace; margin-top: 4px;';
            header.textContent = `${titulo} (${arquivos.length})`;
            grupoDiv.appendChild(header);

            if (arquivos.length === 0) {
                const vazio = document.createElement('div');
                vazio.style.cssText = 'font-size: 11px; color: #71717a; font-style: italic; padding-left: 6px;';
                vazio.textContent = 'Nenhum arquivo';
                grupoDiv.appendChild(vazio);
                return grupoDiv;
            }

            arquivos.forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'diff-item';
                itemDiv.dataset.caminho = item.caminho;
                itemDiv.dataset.staged = ehStaged;

                itemDiv.onclick = () => {
                    document.querySelectorAll('.diff-item').forEach(el => el.classList.remove('active'));
                    itemDiv.classList.add('active');
                    carregarDiffArquivo(item.caminho, ehStaged);
                };

                // Nome do arquivo
                const name = document.createElement('span');
                name.textContent = item.caminho;
                name.style.cssText = 'font-size: 11px; font-family: "JetBrains Mono", monospace; color: #ededed; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1;';

                const right = document.createElement('div');
                right.style.cssText = 'display: flex; align-items: center; gap: 6px; flex-shrink: 0;';

                // Badge de quantidade de alterações
                const badge = document.createElement('span');
                badge.textContent = `${item.alteracoes} alt.`;
                badge.style.cssText = 'font-size: 10px; color: #a1a1aa; background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;';

                // Badge de Status (M, U, D, A, R)
                const statusLetra = (item.status || item.tipo || 'M').toUpperCase();
                const badgeStatus = document.createElement('span');
                badgeStatus.className = `status-badge status-${statusLetra}`;
                badgeStatus.textContent = statusLetra;

                right.appendChild(badge);
                right.appendChild(badgeStatus);

                itemDiv.appendChild(name);
                itemDiv.appendChild(right);
                grupoDiv.appendChild(itemDiv);
            });

            return grupoDiv;
        };

        container.appendChild(renderGrupo('Working Tree (git diff)', dados.working_tree, false));
        container.appendChild(renderGrupo('Staged (git diff --staged)', dados.staged, true));

        const primeiroItem = container.querySelector('.diff-item');
        if (primeiroItem) {
            primeiroItem.classList.add('active');
            const caminho = primeiroItem.dataset.caminho;
            const ehStaged = primeiroItem.dataset.staged === 'true';
            carregarDiffArquivo(caminho, ehStaged);
        } else {
            carregarDiffGeral();
        }

    } catch (e) {
        console.error("Erro ao carregar resumo de diff:", e);
        container.innerHTML = `<span style="color: #f87171; font-size: 11px;">⚠️ Erro ao carregar diff: ${e.message || e}</span>`;
    }
}

async function carregarDiffArquivo(caminho, staged) {
    const titulo = document.getElementById('diff-titulo-arquivo');
    const contentArea = document.getElementById('diff-content-area');

    if (titulo) {
        titulo.textContent = `${staged ? '[Staged]' : '[Working Tree]'} ${caminho}`;
    }

    if (contentArea) {
        contentArea.innerHTML = '<span style="color:#a1a1aa;">Carregando diff...</span>';
        const diffTexto = await pywebview.api.executar_diff(caminho, staged);
        contentArea.innerHTML = formatarDiffColorido(diffTexto);
    }
}

async function carregarDiffGeral() {
    const titulo = document.getElementById('diff-titulo-arquivo');
    const contentArea = document.getElementById('diff-content-area');

    if (titulo) {
        titulo.textContent = 'Diff Geral (Working Tree)';
    }

    if (contentArea) {
        contentArea.innerHTML = '<span style="color:#a1a1aa;">Carregando diff geral...</span>';
        const diffTexto = await pywebview.api.executar_diff(null, false);
        contentArea.innerHTML = formatarDiffColorido(diffTexto);
    }
}


document.addEventListener('DOMContentLoaded', () => {
    const configTerm = localStorage.getItem('gugagit-term-clear');
    if (configTerm !== null) {
        limparTerminalAutomaticamente = configTerm === 'true';
        const inputClear = document.getElementById('config-term-clear');
        if (inputClear) inputClear.checked = limparTerminalAutomaticamente;
    }

    pastaPadraoClone = localStorage.getItem('gugagit-default-dir') || "";
    const inputDir = document.getElementById('config-dir');
    if (inputDir) inputDir.value = pastaPadraoClone;

    const corAccent = localStorage.getItem('gugagit-color-accent');
    const corEnd = localStorage.getItem('gugagit-color-end');
    if (corAccent && corEnd) {
        document.documentElement.style.setProperty('--accent', corAccent);
        document.documentElement.style.setProperty('--gradient-brand', `linear-gradient(135deg, ${corAccent} 0%, ${corEnd} 100%)`);
    }
    
    document.getElementById('btn-refresh')?.addEventListener('click', carregarArquivosModificados);
    document.getElementById('btn-marcar-todos')?.addEventListener('click', () => marcarTodosArquivos(true));
    document.getElementById('btn-desmarcar-todos')?.addEventListener('click', () => marcarTodosArquivos(false));
    document.getElementById('btn-aplicar-staging')?.addEventListener('click', aplicarStagingSelecionado);

    document.getElementById('input-commit')?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') fazerCommit();
    });

    if (window.pywebview && window.pywebview.api) {
        inicializarBackend();
    } else {
        window.addEventListener('pywebviewready', inicializarBackend);
    }
});

// Alternar exibição da aba de staging
function toggleStagingView() {
    const wrapper = document.getElementById('wrapper-staging');
    const btn = document.getElementById('btn-toggle-staging');

    if (!wrapper || !btn) return;

    if (wrapper.style.display === 'none' || wrapper.style.display === '') {
        wrapper.style.display = 'block';
        btn.innerHTML = '▲ Ocultar Arquivos';
    } else {
        wrapper.style.display = 'none';
        btn.innerHTML = '▼ Selecionar Arquivos';
    }
}

window.toggleStagingView = toggleStagingView;