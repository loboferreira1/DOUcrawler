import json
import re
from dataclasses import asdict
from pathlib import Path

from .models import MatchEntry, StorageConfig

def slugify(text: str) -> str:
    """
    Higieniza uma string para ser segura para nomes de arquivos.
    Substitui caracteres não alfanuméricos por hifens, minúsculas.
    """
    # Substitui caracteres não alfanuméricos (corresponde a [^a-zA-Z0-9]) por -
    text = re.sub(r'[^a-zA-Z0-9]', '-', text)
    # Colapsa múltiplos hifens
    text = re.sub(r'-+', '-', text)
    # Remove hifens à esquerda/direita e converte para minúsculas
    return text.strip('-').lower()

def save_match(match: MatchEntry, config: StorageConfig) -> None:
    """
    Anexa uma entrada de correspondência a um arquivo JSONL dedicado à sua palavra-chave/categoria.
    Cria diretório e arquivo se não existirem.
    """
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determina o nome do arquivo a partir da regra ou palavra-chave (keyword_group)
    # Se keyword_group estiver vazio (legado), usa keyword
    group_name = match.keyword_group if match.keyword_group else match.keyword
    safe_keyword = slugify(group_name)
    file_path = output_dir / f"{safe_keyword}.jsonl"
    
    # Prepara dados
    data = asdict(match)
    
    # Anexa ao arquivo
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
