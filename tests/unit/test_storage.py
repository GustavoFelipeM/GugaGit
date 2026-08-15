import json
from unittest.mock import patch, mock_open
from src.infrastructure.storage import (
    carregar_config,
    salvar_config,
    salvar_ultimo_repositorio,
    obter_ultimo_repositorio
)

# Teste 1: Se o arquivo de config não existir, deve retornar um dicionário vazio
@patch("os.path.exists", return_value=False)
def test_carregar_config_arquivo_inexistente(mock_exists):
    config = carregar_config()
    assert config == {}

# Teste 2: Se o arquivo existir, deve ler e retornar o conteúdo JSON
@patch("os.path.exists", return_value=True)
def test_carregar_config_sucesso(mock_exists):
    conteudo_json = '{"ultimo_repositorio": "/caminho/test"}'
    with patch("builtins.open", mock_open(read_data=conteudo_json)):
        config = carregar_config()
        assert config == {"ultimo_repositorio": "/caminho/test"}

# Teste 3: salvar_config deve criar diretório e gravar o JSON com formatação
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_salvar_config(mock_file, mock_makedirs):
    dados = {"ultimo_repositorio": "/pasta/demo"}
    salvar_config(dados)
    
    mock_makedirs.assert_called_once()
    mock_file.assert_called_once()

# Teste 4: salvar_ultimo_repositorio deve atualizar o config e chamar salvar_config
@patch("src.infrastructure.storage.carregar_config")
@patch("src.infrastructure.storage.salvar_config")
def test_salvar_ultimo_repositorio(mock_salvar, mock_carregar):
    mock_carregar.return_value = {"tema": "escuro"}

    caminho_pasta = "/meus_projetos/gugagit"

    salvar_ultimo_repositorio(caminho_pasta)

    dicionario_esperado = {
        "tema": "escuro", 
        "ultimo_repositorio": caminho_pasta
    }

    mock_salvar.assert_called_once_with(dicionario_esperado)

# Teste 5: obter_ultimo_repositorio deve retornar o valor correto do config
@patch("src.infrastructure.storage.carregar_config")
def test_obter_ultimo_repositorio(mock_carregar):
    mock_carregar.return_value = {"ultimo_repositorio": "/meu/repo"}
    caminho = obter_ultimo_repositorio()
    assert caminho == "/meu/repo"

# Teste 6: Se o arquivo existir mas estiver corrompido (JSON inválido), deve cair no except e retornar {}
@patch("os.path.exists", return_value=True)
def test_carregar_config_json_corrompido(mock_exists):
    conteudo_invalido = "{json_quebrado: }"
    with patch("builtins.open", mock_open(read_data=conteudo_invalido)):
        config = carregar_config()
        assert config == {}

# Teste 7: Se a chave "ultimo_repositorio" não existir no config, deve retornar None
@patch("src.infrastructure.storage.carregar_config")
def test_obter_ultimo_repositorio_inexistente(mock_carregar):
    mock_carregar.return_value = {"outro_dado": "valor"}
    caminho = obter_ultimo_repositorio()
    assert caminho is None