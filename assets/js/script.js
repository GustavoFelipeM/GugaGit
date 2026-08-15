function getTerminalLines() {
    return document.getElementById('terminal-lines');
}

function clearTerminal() {
    const terminal = getTerminalLines();
    terminal.innerHTML = '';
}

function logTerminal(mensagem) {
    const terminal = getTerminalLines();
    const novaLinha = document.createElement('span');
    
    novaLinha.innerHTML = mensagem.replace(/\n/g, '<br>');
    novaLinha.style.color = "#a1a1aa";
    
    terminal.appendChild(novaLinha);
    terminal.scrollTop = terminal.scrollHeight;
}

async function enviarComandoTerminal(event) {
    if (event.key === 'Enter') {
        const input = document.getElementById('input-comando-livre');
        const comando = input.value.trim();

        if (!comando) return;

        input.value = '';

        await pywebview.api.executar_comando_customizado(comando);
        
        await atualizarCabecalhoInicial();
    }
}

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
            resolve(resultado);
        };

        btnCancel.onclick = () => fechar(null);
        btnOk.onclick = () => fechar(mostrarInput ? inputEl.value.trim() : true);

        inputEl.onkeydown = (event) => {
            if (event.key === 'Enter') {
                fechar(inputEl.value.trim());
            }
        };

        if (mostrarInput) {
            inputEl.focus();
            inputEl.select();
        }
    });
}

function voltarParaDashboard() {
    document.getElementById('view-settings').style.display = 'none';
    
    document.getElementById('view-dashboard').style.display = 'grid';
    document.getElementById('main-header').style.display = 'flex';

    document.querySelectorAll('.nav-icon').forEach(el => el.classList.remove('active'));
    document.getElementById('nav-repo').classList.add('active');
}

async function salvarConfiguracoesGit() {
    const nome = document.getElementById('config-nome').value.trim();
    const email = document.getElementById('config-email').value.trim();
    
    if (!nome || !email) {
        alert("O nome e o e-mail não podem estar vazios.");
        return;
    }

    voltarParaDashboard();
    
    await executarComTerminalLimpo(async () => {
        logTerminal("> Atualizando dados de autoria no Git...");
        const resposta = await pywebview.api.salvar_config_git(nome, email);
        if(resposta && resposta[1]) {
            logTerminal("> " + resposta[0]);
        } else {
            logTerminal("> ERRO: Falha ao atualizar configurações.");
        }
    });
}

async function confirmarAcao(titulo, mensagem) {
    return await abrirModal({
        titulo,
        mensagem,
        mostrarInput: false
    });
}

async function solicitarTexto(titulo, mensagem, placeholder = '', valorInicial = '') {
    return await abrirModal({
        titulo,
        mensagem,
        placeholder,
        valorInicial,
        mostrarInput: true
    });
}

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
}

async function atualizarCabecalhoInicial() {
    const estado = await pywebview.api.obter_estado_atual();
    if (estado && estado.sucesso) {
        document.getElementById('lbl-repo').innerText = '📦 ' + estado.repo;
        document.getElementById('lbl-branch').innerText = '🔀 ' + estado.branch;
    }
}

function atualizarBranchCabecalho(branch) {
    if (branch) {
        document.getElementById('lbl-branch').innerText = '🔀 ' + branch;
    }
}

async function minimizarJanela() {
    await pywebview.api.minimizar_janela();
}

async function fecharJanela() {
    await pywebview.api.fechar_janela();
}

async function executarPull() {
    await executarComTerminalLimpo(async () => pywebview.api.executar_pull());
}

async function executarPush() {
    await executarComTerminalLimpo(async () => pywebview.api.executar_push());
}

async function executarFetch() {
    await executarComTerminalLimpo(async () => pywebview.api.executar_fetch());
}

async function executarStatus() {
    await executarComTerminalLimpo(async () => pywebview.api.executar_status());
}

async function executarBranches() {
    await executarComTerminalLimpo(async () => {
        const branches = await pywebview.api.executar_listar_branches();
        logTerminal("> BRANCHES:\n" + (branches.length ? branches.join("\n") : "Nenhuma branch encontrada."));
    });
}

async function executarHistorico() {
    await executarComTerminalLimpo(async () => pywebview.api.executar_historico());
}

async function executarDiff() {
    await executarComTerminalLimpo(async () => pywebview.api.executar_diff());
}

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

async function executarAdicionar() {
    await executarComTerminalLimpo(async () => pywebview.api.executar_adicionar());
}

async function executarStash() {
    await executarComTerminalLimpo(async () => pywebview.api.executar_stash());
}

async function executarStashPop() {
    await executarComTerminalLimpo(async () => pywebview.api.executar_stash_pop());
}

async function executarRemoverStaging() {
    const confirmado = await confirmarAcao("Remover staging", "Deseja remover todos os arquivos do staging?");
    if (!confirmado) return;
    await executarComTerminalLimpo(async () => pywebview.api.executar_remover_staging());
}

async function executarRestaurar() {
    const confirmado = await confirmarAcao("Restaurar arquivos", "Isso irá descartar as alterações atuais nos arquivos. Continuar?");
    if (!confirmado) return;
    await executarComTerminalLimpo(async () => pywebview.api.executar_restaurar());
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
    const mensagem = input.value;
    
    if (!mensagem) {
        logTerminal("> ERRO: Digite uma mensagem de commit.");
        return;
    }
    
    await executarComTerminalLimpo(async () => {
        logTerminal("> Iniciando commit...");
        const sucesso = await pywebview.api.executar_adicionar_e_commit(mensagem);
        if (sucesso) {
            input.value = "";
        }
    });
}

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

window.addEventListener('DOMContentLoaded', () => {
    const configTerm = localStorage.getItem('gugagit-term-clear');
    if (configTerm !== null) {
        limparTerminalAutomaticamente = configTerm === 'true';
        document.getElementById('config-term-clear').checked = limparTerminalAutomaticamente;
    }

    pastaPadraoClone = localStorage.getItem('gugagit-default-dir') || "";
    document.getElementById('config-dir').value = pastaPadraoClone;

    const corAccent = localStorage.getItem('gugagit-color-accent');
    const corEnd = localStorage.getItem('gugagit-color-end');
    if (corAccent && corEnd) {
        document.documentElement.style.setProperty('--accent', corAccent);
        document.documentElement.style.setProperty('--gradient-brand', `linear-gradient(135deg, ${corAccent} 0%, ${corEnd} 100%)`);
    }
});

async function abrirConfiguracoes() {
    document.getElementById('view-dashboard').style.display = 'none';
    document.getElementById('main-header').style.display = 'none';
    document.getElementById('view-settings').style.display = 'block';

    document.querySelectorAll('.nav-icon').forEach(el => el.classList.remove('active'));
    document.getElementById('nav-config').classList.add('active');

    const config = await pywebview.api.obter_config_git();
    document.getElementById('config-nome').value = config.nome || '';
    document.getElementById('config-email').value = config.email || '';
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

window.addEventListener('pywebviewready', function() {
    logTerminal("> Conexão com o backend Python estabelecida com sucesso.");
    pywebview.api.verificar_git().then(instalado => {
        if (!instalado) {
            logTerminal("> ATENÇÃO: Git não encontrado no sistema!");
        }
    });

    atualizarCabecalhoInicial();
});