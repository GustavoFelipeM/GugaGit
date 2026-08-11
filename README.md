# GugaGit

GugaGit é um gerenciador visual de Git desenvolvido em Python com CustomTkinter, criado para simplificar tarefas do dia a dia em repositórios Git por meio de uma interface desktop moderna e objetiva.

Este projeto foi pensado tanto como ferramenta de produtividade quanto como peça de portfólio, mostrando domínio de interface gráfica, integração com Git CLI, organização modular e persistência local de configurações.

## Como usar

### Versão executável

A forma mais prática de usar o GugaGit é pela versão em `.exe`. Assim, qualquer pessoa pode abrir a aplicação sem precisar instalar Python ou configurar ambiente virtual.

Essa é a opção ideal para apresentação, testes rápidos e distribuição como portfólio.

### Versão com Python

Se você quiser estudar o código, ajustar a aplicação ou rodar direto do projeto, também é possível executar via Python.

Esse modo é indicado para desenvolvimento, manutenção e contribuições.

## Visão geral

A aplicação oferece uma interface visual para executar operações comuns de Git sem depender do terminal a todo momento. O foco é reduzir atrito em tarefas como abrir repositórios, clonar projetos, alternar branches, criar commits e acompanhar o histórico.

## Funcionalidades

- Abrir repositórios Git existentes
- Clonar repositórios pela interface
- Exibir a branch atual e o caminho do repositório
- Atualizar status e informações do projeto
- Criar, trocar e deletar branches
- Adicionar arquivos, criar commits e fazer push
- Executar pull e fetch
- Restaurar alterações e remover staging
- Gerenciar stash com guardar, listar e aplicar
- Visualizar status, branches, histórico, diff, stashes e tags
- Exibir janelas modais para entradas e seleções
- Salvar o último repositório usado localmente
- Aplicar ícone personalizado nas janelas do app

## Tecnologias utilizadas

- Python
- CustomTkinter
- Tkinter
- Git CLI

## Requisitos

Para usar a aplicação, a máquina precisa ter:

- Git instalado e disponível no PATH
- No caso da versão em Python, Python instalado também

## Estrutura do projeto

```text
GugaGit/
├─ main.py
├─ README.md
├─ assets/
│  └─ gugabit.ico
└─ src/
   ├─ config.py
   ├─ dialogs.py
   ├─ git_manager.py
   └─ gui.py
```

## Execução via Python

Para rodar o projeto em modo fonte:

```bash
pip install -r requirements.txt
python main.py
```

Se preferir, você também pode instalar apenas a dependência principal com `pip install customtkinter`.

## Execução da versão executável

Se você estiver usando a versão compilada, basta abrir o arquivo `.exe` gerado na distribuição do projeto.

## Como o projeto funciona

- `main.py` inicia a aplicação.
- `src/gui.py` concentra a interface principal, menus, modais e ações de usuário.
- `src/git_manager.py` encapsula os comandos Git executados pela aplicação.
- `src/config.py` cuida de configurações locais, como o último repositório acessado e o ícone da janela.
- `src/dialogs.py` contém diálogos reutilizáveis de confirmação.

## Destaques para portfólio

O GugaGit mostra prática em:

- desenvolvimento de interface desktop com Python
- integração com ferramentas de linha de comando
- organização em módulos separados por responsabilidade
- persistência de dados locais do usuário
- foco em experiência de uso e produtividade
- distribuição em formato executável para usuários finais

## Observações

- A aplicação depende do Git instalado para funcionar corretamente.
- O projeto salva o último repositório aberto no diretório de dados local do usuário.
- O ícone personalizado é aplicado às janelas principais e secundárias.
- A versão executável é a melhor opção para demonstração em portfólio.

## Possíveis melhorias

- Adicionar empacotamento automatizado do `.exe`
- Incluir screenshots da interface
- Criar alternância entre tema claro e escuro
- Melhorar feedback visual para operações longas de Git
- Disponibilizar release com instalador

## Licença

Projeto pessoal para estudo, prática e portfólio.
