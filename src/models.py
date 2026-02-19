from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal

@dataclass(frozen=True)
class ScheduleConfig:
    time: str
    timezone: str = "America/Sao_Paulo"

@dataclass(frozen=True)
class LoggingConfig:
    level: str = "INFO"
    file: str = "logs/scrapper.log"

@dataclass(frozen=True)
class StorageConfig:
    output_dir: str = "data"
    format: Literal["jsonl"] = "jsonl"

@dataclass(frozen=True)
class AdvancedMatchRule:
    name: str
    body_terms: List[str]
    title_terms: List[str] = field(default_factory=list)
    sections: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class Config:
    schedule: ScheduleConfig
    keywords: List[str]
    storage: StorageConfig
    logging: LoggingConfig
    sections: List[str] = field(default_factory=lambda: ["dou1", "dou2", "dou3"]) # Deprecated global default
    rules: List[AdvancedMatchRule] = field(default_factory=list)

@dataclass
class MatchEntry:
    keyword: str
    context: str
    date: str
    section: str
    url: str
    capture_timestamp: str
    title: str = ""
