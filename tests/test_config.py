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
    """Test loading a valid configuration file."""
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
    """Test loading a non-existent configuration file."""
    with pytest.raises(FileNotFoundError):
        config.load_config("non_existent_config.yaml")

def test_load_config_default_values(tmp_path):
    """Test loading config with missing optional sections to verify defaults."""
    # Only providing required fields (keywords and schedule time are required by dataclass structure if not defaulted in yaml usage, 
    # but let's check what src/config.py does. 
    # Actually src/config.py does: ScheduleConfig(**schedule_data)
    # ScheduleConfig requires 'time'. 'timezone' has default.
    # Config requires keywords.
    # storage and logging have defaults in dataclass.
    
    minimal_data = {
        "schedule": {"time": "08:00"},
        "keywords": ["minimal"]
    }
    
    p = tmp_path / "minimal_config.yaml"
    with open(p, "w", encoding="utf-8") as f:
        yaml.dump(minimal_data, f)
        
    cfg = config.load_config(str(p))
    
    # Defaults
    assert cfg.schedule.timezone == "America/Sao_Paulo"
    assert cfg.storage.output_dir == "data"
    assert cfg.storage.format == "jsonl"
    assert cfg.logging.level == "INFO"
    assert cfg.logging.file == "logs/scrapper.log"

def test_setup_logging(config_file):
    """Test that setup_logging runs without error."""
    cfg = config.load_config(config_file)
    # We just want to ensure it doesn't crash. 
    # Verifying actual logging configuration is complex and might interfere with other tests/pytest capture.
    # But we can check if the file handler was created potentially, strictly speaking setup_logging modifies global state.
    
    # Clean up handlers before/after to avoid side effects
    logger = logging.getLogger()
    original_handlers = logger.handlers[:]
    
    try:
        config.setup_logging(cfg)
        # Check if we didn't crash
        assert True
    finally:
        # Restore handlers
        logger.handlers = original_handlers
