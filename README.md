# GugaGit

> Um cliente Git desktop moderno, ultrarrápido e elegante, construído com **Python + pywebview** e uma interface web nativa em **HTML5, CSS3 e JavaScript (100% Offline)**.

## 🚀 Sobre o Projeto

O **GugaGit** é uma evolução completa do projeto original. A interface antiga desenvolvida em *CustomTkinter* foi totalmente descartada e substituída por uma arquitetura moderna baseada em **pywebview**. Essa mudança permitiu controle absoluto sobre o design, tipografia e UX da aplicação utilizando tecnologias web modernas, sem abrir mão da integração nativa com o sistema operacional e do controle direto via Python.

Desenvolvido para oferecer uma alternativa visual leve, objetiva e produtiva aos clientes Git tradicionais, o GugaGit Pro combina uma interface estilo *Bento Grid* e *Dark Mode* com o poder e a estabilidade do **Git CLI** rodando em background.

## ✨ O que mudou? (Principais Evoluções)

* 🎨 **Migração Completa para pywebview (HTML5/CSS3/JS):** A antiga GUI em CustomTkinter deu lugar a um motor Webview ultraleve e totalmente customizável, funcionando **100% offline**.
* 🖌️ **Redesign Visual Absoluto (Bento Grid UI):** Design escuro inspirado em dashboards modernos, tipografia refinada (*JetBrains Mono*), animações suaves e barra de título *frameless* customizada.
* 💻 **Terminal Livre Interativo (`$ git ...`):** Prompt de comando integrado que permite digitar e executar **qualquer comando Git livremente**, registrando o histórico de saídas no console do app em tempo real.
* ⚙️ **Painel de Configurações Completo:**

  * Gerenciamento de dados de autoria Git (`user.name` e `user.email`).
  * Definição de diretório padrão e preferências de clonagem.
  * Ajustes de comportamento e preferências da interface.
* ⚡ **Foco em UX e Produtividade:**

  * Status em tempo real da branch ativa e repositório aberto na barra superior.
  * Ações rápidas com 1 clique: `Sync (Fetch/Pull/Push)`, `Staging`, `Commit`, `Branch Management`, `Stash`, `Diff` e `Tags`.
  * Salvamento automático do último workspace utilizado.

## 🛠️ Tecnologias Utilizadas

* **Back-end & Integração Nativa:**

  * [Python 3.x](https://www.python.org/)
  * **`pywebview`** (Ponte bidirecional e assíncrona entre Python e JavaScript)
  * **`pythonnet`** (Integração com APIs nativas do Windows para manipulção de ícones e janelas)
  * **`subprocess` & `shlex`** (Execução segura de comandos do Git CLI em background)
* **Front-end UI (Offline):**

  * **HTML5 & CSS3** (Layout estilo Bento Box, variáveis CSS e design responsivo)
  * **JavaScript puro (ES6+)** (Integração em tempo real com a API bridge do Python)
* **Compilação & Empacotamento:**

  * **PyInstaller** (Geração do executável standalone `.exe` para Windows)

## 📁 Estrutura do Projeto

```text
GugaGit/
├── assets/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   ├── gugabit.ico
│   └── index.html
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   └── git_service.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── git_cli.py
│   │   └── storage.py
│   ├── ui/
│   │   ├── __init__.py
│   │   └── api.py
│   └── __init__.py
├── tests/
│   ├── integration/
│   │   ├── test_git_integration.py
│   │   └── test_storage_integration.py
│   └── unit/
│       ├── test_git_cli.py
│       ├── test_git_service.py
│       └── test_storage.py
├── .gitignore
├── main.py
├── README.md
└── requirements.txtss
```

## 🔧 Requisitos de Sistema

### Windows

* **Git CLI** instalado e disponível no `PATH` do sistema.
* **Python 3.10+** (apenas para execução a partir do código-fonte).
* **Windows 10/11** (com suporte otimizado para ícone na barra de tarefas e janela *frameless*).

### Linux

* **Git CLI** instalado e disponível no `PATH` do sistema.
* **Python 3.10+**.
* Um ambiente gráfico compatível com o backend Qt do `pywebview`.

> **Testado no Debian, Ubuntu e Fedora.** A execução em outras distribuições Linux não foi validada.

## 📥 Como Executar

### Opção 1: Via Código Fonte (Desenvolvimento)

#### Windows

1. Clone o repositório:

   ```bash
   git clone https://github.com/GustavoFelipeM/GugaGit.git
   cd GugaGit
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   ```

   No Windows (PowerShell/CMD):

   ```text
   .venv\Scripts\activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Execute o projeto:

   ```bash
   python main.py
   ```

---

#### Linux

1. Clone o repositório:

   ```bash
   git clone https://github.com/GustavoFelipeM/GugaGit.git
   cd GugaGit
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Instale o backend Qt do `pywebview`:

   ```bash
   pip install "pywebview[qt]"
   ```

5. Execute o projeto utilizando o backend Qt:

   ```bash
   PYWEBVIEW_GUI=qt python3 main.py
   ```

> Compatibilidade validada em Debian 13.6, Ubuntu 26.04 e Fedora 44-1.7.

### Opção 2: Baixar Executável Pronto (`.exe`)

Se você quer apenas utilizar o programa sem precisar instalar o Python e configurar dependências:

1. Acesse a seção de **[Releases do GitHub](https://github.com/GustavoFelipeM/GugaGit/releases)**.
2. Baixe o arquivo executável da versão mais recente (ex: `GugaGit.exe`).
3. Dê um duplo clique para rodar a aplicação diretamente no Windows.

## 🧪 Executando os Testes
O projeto possui uma suíte automatizada completa dividida em **testes unitários** (executados com mocks isolados para rápida validação) e **testes de integração** (que operam comandos reais sobre repositórios Git temporários em disco).

### Instalar dependências de teste
Certifique-se de que o ambiente virtual está ativo e instale o `pytest`:

```bash
pip install pytest
```

### Comandos de Execução
* **Executar toda a suíte de testes (Unitários + Integração):**

```bash
pytest -v
```

* **Executar apenas os testes unitários (Mocks rápidos):**

```bash
pytest tests/test_git_service.py tests/test_git_cli.py tests/test_storage.py -v
```

* **Executar apenas os testes de integração reais (Em repositórios Git temporários):**

```bash
pytest tests/test_git_integration.py tests/test_storage_integration.py -v
```

> 🛡️ Garantia de Isolamento: Os testes de integração utilizam as fixtures `tmp_path` e `monkeypatch` do Pytest. Nenhum repositório pessoal ou arquivo de configuração global (`.gitconfig`) é modificado durante a execução dos testes.

## 🎯 Destaques de Arquitetura para Portfólio

* **Arquitetura Híbrida Leve (Python + Webview):** Elimina o consumo massivo de memória do Electron/Node.js, utilizando o motor de renderização nativo do SO junto com a simplicidade e performance do Python.
* **Comunicação Assíncrona Bi-direcional:** Chamadas entre a camada visual (JS) e o gerenciador Git (Python) acontecem sem congelar a interface.
* **Execução Segura de Comandos no Terminal:** O terminal integrado trata entradas com `shlex.split` e define *timeouts* rigorosos no `subprocess` para evitar que comandos interativos (que exijam editores de texto) travem o programa.
* **Persistência de Estado Local:** Mantém automaticamente o contexto de trabalho e as preferências em diretórios padrão do sistema (`%LOCALAPPDATA%` ou `~/.config/GugaGit`).
* **Suíte de Testes Automatizados:** Cobertura de edge cases do Git (operações fora do repo, branches inexistentes, timeout, conflitos e stashes sem alterações).

## 📸 Demonstração da Interface

<div align="center">
  <img src="https://github.com/user-attachments/assets/8a946def-7ddb-43d2-a81e-361a699929db" alt="Interface do GugaGit Pro" width="100%" />
</div>
<br>

<div align="center">
  <img src="https://github.com/user-attachments/assets/971bb8ad-3087-4c8a-9388-75ef786ec31b" alt="Painel de Configurações" width="100%" />
</div>

## 📝 Licença

Projeto desenvolvido para fins de estudo, prática de arquitetura desktop e composição de portfólio.
