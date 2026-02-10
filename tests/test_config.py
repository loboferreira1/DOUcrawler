import logging
import pytest
import yaml
from pathlib import Path
from src import config
from src.models import Config, ScheduleConfig, LoggingConfig, StorageConfig

@pytest.fixture
def valid_config_data():
    return {
        "schedule": {"time": "10:00", "timezone": "America/Sao_Paulo"},
        "keywords": ["test1", "test2"],
        "storage": {"output_dir": "test_data", "format": "jsonl"},
        "logging": {"level": "DEBUG", "file": "test_logs/test.log"}
    }

@pytest.fixture
def config_file(tmp_path, valid_config_data):
    p = tmp_path / "test_config.yaml"
    with open(p, "w", encoding="utf-8") as f:
        yaml.dump(valid_config_data, f)
    return str(p)

def test_load_config_valid(config_file):
    """Testa o carregamento de um arquivo de configuração válido."""
    cfg = config.load_config(config_file)
    
    assert isinstance(cfg, Config)
    assert cfg.schedule.time == "10:00"
    assert cfg.schedule.timezone == "America/Sao_Paulo"
    assert cfg.keywords == ["test1", "test2"]
    assert cfg.storage.output_dir == "test_data"
    assert cfg.storage.format == "jsonl"
    assert cfg.logging.level == "DEBUG"
    assert cfg.logging.file == "test_logs/test.log"

def test_load_config_missing_file():
    """Testa o carregamento de um arquivo de configuração inexistente."""
    with pytest.raises(FileNotFoundError):
        config.load_config("non_existent_config.yaml")

def test_load_config_default_values(tmp_path):
    """Testa o carregamento de configuração com seções opcionais faltando para verificar padrões."""
    # Apenas fornecendo campos obrigatórios (keywords e schedule time são obrigatórios pela estrutura da dataclass se não tiverem padrão no uso yaml,
    # mas vamos verificar o que src/config.py faz.
    # Na verdade src/config.py faz: ScheduleConfig(**schedule_data)
    # ScheduleConfig requer 'time'. 'timezone' tem padrão.
    # Config requer keywords.
    # storage e logging têm padrões na dataclass.
    
    minimal_data = {
        "schedule": {"time": "08:00"},
        "keywords": ["minimal"]
    }
    
    p = tmp_path / "minimal_config.yaml"
    with open(p, "w", encoding="utf-8") as f:
        yaml.dump(minimal_data, f)
        
    cfg = config.load_config(str(p))
    
    # Padrões
    assert cfg.schedule.timezone == "America/Sao_Paulo"
    assert cfg.storage.output_dir == "data"
    assert cfg.storage.format == "jsonl"
    assert cfg.logging.level == "INFO"
    assert cfg.logging.file == "logs/scrapper.log"

def test_setup_logging(config_file):
    """Testa se setup_logging roda sem erro."""
    cfg = config.load_config(config_file)
    # Queremos apenas garantir que não trave.
    # Verificar a configuração real de log é complexo e pode interferir com outros testes/captura do pytest.
    # Mas podemos verificar se o manipulador de arquivo foi criado potencialmente, estritamente falando setup_logging modifica estado global.
    
    # Limpa manipuladores antes/depois para evitar efeitos colaterais
    logger = logging.getLogger()
    original_handlers = logger.handlers[:]
    
    try:
        config.setup_logging(cfg)
        # Verifica se não travou
        assert True
    finally:
        # Restaura manipuladores
        logger.handlers = original_handlers
