import os
import pytest
import src.infrastructure.storage as storage

def test_fluxo_storage_persistencia_real(tmp_path, monkeypatch):
    # Redireciona os caminhos de configuração para uma pasta temporária do teste
    pasta_config_temp = tmp_path / "GugaGitConfig"
    arquivo_config_temp = pasta_config_temp / "config.json"

    monkeypatch.setattr(storage, "PASTA_CONFIG", str(pasta_config_temp))
    monkeypatch.setattr(storage, "ARQUIVO_CONFIG", str(arquivo_config_temp))

    # 1. Carregar quando não existe deve retornar dicionário vazio
    assert storage.carregar_config() == {}
    assert storage.obter_ultimo_repositorio() is None

    # 2. Salvar último repositório
    caminho_teste = str(tmp_path / "meu_projeto_git")
    storage.salvar_ultimo_repositorio(caminho_teste)

    # 3. Validar se o arquivo realmente foi criado no disco
    assert arquivo_config_temp.exists()

    # 4. Ler do disco e conferir dados
    assert storage.obter_ultimo_repositorio() == caminho_teste
    dados_carregados = storage.carregar_config()
    assert dados_carregados["ultimo_repositorio"] == caminho_teste