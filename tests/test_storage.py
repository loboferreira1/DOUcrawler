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
    """Test that saving a match creates a new file if it doesn't exist."""
    data_dir = tmp_path / "data"
    cfg = StorageConfig(output_dir=str(data_dir))
    
    storage.save_match(sample_match, cfg)
    
    # Expected file path: data/teste.jsonl (slugified keyword?)
    # Spec says "one file per keyword/category". 
    # Keyword is "teste".
    expected_file = data_dir / "teste.jsonl"
    
    assert expected_file.exists()
    
    content = expected_file.read_text(encoding="utf-8")
    saved_data = json.loads(content)
    assert saved_data["keyword"] == "teste"
    assert saved_data["url"] == "http://teste.com"

def test_save_match_appends(tmp_path, sample_match):
    """Test that saving appends to existing file."""
    data_dir = tmp_path / "data"
    cfg = StorageConfig(output_dir=str(data_dir))
    
    # Save once
    storage.save_match(sample_match, cfg)
    
    # Save again (simulate different match same keyword)
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
    """Test using a keyword with spaces/special chars generates valid filename."""
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
    
    # Should probably replace / with _ or similar
    # Check directory listing to see what was created
    created_files = list(data_dir.glob("*.jsonl"))
    assert len(created_files) == 1
    filename = created_files[0].name
    
    assert "/" not in filename
    assert "\\" not in filename
    assert "fundacao" in filename.lower() or "funai" in filename.lower() # Depends on slugify logic
    # Basic slugify usually: fundacao-nacional-funai.jsonl
