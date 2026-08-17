# Arquitetura do GugaGit

O **GugaGit** foi desenhado com uma arquitetura modular em camadas, priorizando baixo acoplamento, alta coesão e facilitando a automação de testes unitários e de integração.



## 🏢 Visão Geral das Camadas

```text
┌──────────────────────────────────────────────────────────┐
│                   1. Frontend (UI)                       │
│             (HTML / CSS / JavaScript / PyWebView)        │
└────────────────────────────┬─────────────────────────────┘
                             │ IPC (Inter-Process Communication)
┌────────────────────────────▼─────────────────────────────┐
│                  2. API Layer (Facade)                   │
│                     (src/ui/api.py)                      │
└────────────────────────────┬─────────────────────────────┘
                             │ Injeção de Dependência
┌────────────────────────────▼─────────────────────────────┐
│                3. Domain / Service Layer                 │
│      (StagingService, BranchService, RemoteService)      │
└────────────────────────────┬─────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────┐
│             4. Infrastructure & Helper Layer             │
│        (git_cli, process_runner, storage, logger)        │
└──────────────────────────────────────────────────────────┘
```

## 🔄 Responsabilidade das Camadas
- **UI Layer (Frontend):** Responsável apenas pela apresentação e captura de ações do usuário.

- **API Facade (`GugaGitAPI`):** Funciona como porta de entrada (bridge) para as chamadas IPC do PyWebView. Trata exceções da interface gráfica, gerencia o estado da janela ativa e delega toda regra de negócio aos serviços.

- **Domain Services (`src/core/git/`):** Serviços especializados por contexto (`staging.py`, `branch.py`, `remote.py`, `stash.py`, `history.py`). Processam as regras do Git e usam injeção de dependências.

- **Infrastructure Layer (`src/infrastructure/`):** Executa comandos do sistema operacional via `subprocess`, gerencia logs e a persistência em arquivo JSON.

## 🛡️ Tratamento de Erros e Logs
- **Exceptions Próprias (`src/core/exceptions.py`):** Erros de domínio mapeados para evitar exceções genéricas na aplicação.

- **Sem Falhas Silenciosas:** Não utilizamos `except Exception`: pass. Toda exceção é capturada, logada e mapeada para respostas previsíveis (`sucesso: False`).