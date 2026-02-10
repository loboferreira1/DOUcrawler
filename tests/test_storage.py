import json
import pytest
from src import storage
from src.models import MatchEntry, StorageConfig

@pytest.fixture
def sample_match():
    return MatchEntry(
        keyword="teste",
        context="contexto de teste",
        date="10/02/2026",
        section="dou1",
        url="http://teste.com",
        capture_timestamp="2026-02-10T10:00:00",
        title="Titulo"
    )

def test_save_match_creates_file(tmp_path, sample_match):
    """Testa se salvar uma correspondência cria um novo arquivo se ele não existir."""
    data_dir = tmp_path / "data"
    cfg = StorageConfig(output_dir=str(data_dir))
    
    storage.save_match(sample_match, cfg)
    
    # Caminho de arquivo esperado: data/teste.jsonl (palavra-chave 'slugified'?)
    # Spec diz "um arquivo por palavra-chave/categoria".
    # Palavra-chave é "teste".
    expected_file = data_dir / "teste.jsonl"
    
    assert expected_file.exists()
    
    content = expected_file.read_text(encoding="utf-8")
    saved_data = json.loads(content)
    assert saved_data["keyword"] == "teste"
    assert saved_data["url"] == "http://teste.com"

def test_save_match_appends(tmp_path, sample_match):
    """Testa se salvar anexa ao arquivo existente."""
    data_dir = tmp_path / "data"
    cfg = StorageConfig(output_dir=str(data_dir))
    
    # Salva uma vez
    storage.save_match(sample_match, cfg)
    
    # Salva novamente (simula correspondência diferente mesma data)
    sample_match_2 = MatchEntry(
        keyword="teste",
        context="contexto 2",
        date="10/02/2026",
        section="dou1",
        url="http://teste2.com",
        capture_timestamp="2026-02-10T11:00:00",
        title="Titulo 2"
    )
    storage.save_match(sample_match_2, cfg)
    
    expected_file = data_dir / "teste.jsonl"
    lines = expected_file.read_text(encoding="utf-8").strip().split('\n')
    
    assert len(lines) == 2
    assert json.loads(lines[0])["context"] == "contexto de teste"
    assert json.loads(lines[1])["context"] == "contexto 2"

def test_filename_sanity_sanitization(tmp_path):
    """Testa se o uso de uma palavra-chave com espaços/caracteres especiais gera um nome de arquivo válido."""
    bad_keyword = "fundação nacional/funai"
    match = MatchEntry(
        keyword=bad_keyword,
        context="ctx",
        date="today",
        section="s1",
        url="u",
        capture_timestamp="t",
        title="t"
    )
    
    data_dir = tmp_path / "data"
    cfg = StorageConfig(output_dir=str(data_dir))
    
    storage.save_match(match, cfg)
    
    # Provavelmente deve substituir / por _ ou similar
    # Verifica listagem de diretório para ver o que foi criado
    created_files = list(data_dir.glob("*.jsonl"))
    assert len(created_files) == 1
    filename = created_files[0].name
    
    assert "/" not in filename
    assert "\\" not in filename
    assert "fundacao" in filename.lower() or "funai" in filename.lower() # Depende da lógica de slugify
    # Slugify básico geralmente: fundacao-nacional-funai.jsonl
