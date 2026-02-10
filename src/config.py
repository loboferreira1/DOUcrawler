import pathlib
import sys
import logging
from typing import TextIO

import structlog
import yaml

from .models import Config, LoggingConfig, ScheduleConfig, StorageConfig

def load_config(config_path: str = "config.yaml") -> Config:
    """
    Carrega a configuração de um arquivo YAML e valida a estrutura esperada.
    Retorna:
        Config: Objeto de configuração preenchido.
    Lança:
        FileNotFoundError: Se o arquivo de configuração estiver faltando.
        yaml.YAMLError: Se o arquivo de configuração for inválido.
    """
    path = pathlib.Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Validação básica de estrutura poderia acontecer aqui, mas confiamos no mapeamento de dataclass
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
    Configura structlog e log padrão com base na configuração.
    """
    log_level = getattr(logging, config.logging.level.upper(), logging.INFO)
    
    # Configura log padrão para capturar logs de bibliotecas (requests, etc)
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Configura structlog
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

    # Configura log em arquivo se necessário (detalhe de implementação opcional)
    # Usando manipulador de arquivo de log padrão para simplicidade misturado com structlog
    if config.logging.file:
        log_path = pathlib.Path(config.logging.file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(config.logging.file, encoding="utf-8")
        file_handler.setLevel(log_level)
        # Podemos reutilizar o formatador JSON ou usar um diferente
        # Para uniformidade, vamos manter JSON estruturado no arquivo também
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
        )
        file_handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
