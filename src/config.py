import pathlib
import sys
import logging
from typing import TextIO

import structlog
import yaml

from .models import Config, LoggingConfig, ScheduleConfig, StorageConfig

def load_config(config_path: str = "config.yaml") -> Config:
    """
    Loads configuration from a YAML file and validates expected structure.
    Returns:
        Config: Populated configuration object.
    Throws:
        FileNotFoundError: If config file is missing.
        yaml.YAMLError: If config file is invalid.
    """
    path = pathlib.Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Basic structure validation could happen here, but we rely on dataclass mapping
    schedule_data = data.get("schedule", {})
    logging_data = data.get("logging", {})
    storage_data = data.get("storage", {})
    keywords = data.get("keywords", [])
    sections = data.get("sections", ["dou1", "dou2", "dou3"])

    return Config(
        schedule=ScheduleConfig(**schedule_data),
        keywords=keywords,
        storage=StorageConfig(**storage_data),
        logging=LoggingConfig(**logging_data),
        sections=sections,
    )

def setup_logging(config: Config) -> None:
    """
    Configures structlog and standard logging based on configuration.
    """
    log_level = getattr(logging, config.logging.level.upper(), logging.INFO)
    
    # Configure standard logging to capture library logs (requests, etc)
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Setup file logging if needed (optional implementation detail)
    # Using standard logging file handler for simplicity mixed with structlog
    if config.logging.file:
        log_path = pathlib.Path(config.logging.file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(config.logging.file, encoding="utf-8")
        file_handler.setLevel(log_level)
        # We can reuse the JSON formatter or use a different one
        # For uniformity, let's keep it structured JSON in file too
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
        )
        file_handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
