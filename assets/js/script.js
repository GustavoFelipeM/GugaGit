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