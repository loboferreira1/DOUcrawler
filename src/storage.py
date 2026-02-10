import json
import re
from dataclasses import asdict
from pathlib import Path

from .models import MatchEntry, StorageConfig

def slugify(text: str) -> str:
    """
    Sanitizes a string to be safe for filenames.
    Replaces non-alphanumeric chars with hyphens, lowercases.
    """
    # Replace non-alphanumeric characters (matches [^a-zA-Z0-9]) with -
    text = re.sub(r'[^a-zA-Z0-9]', '-', text)
    # Collapse multiple hyphens
    text = re.sub(r'-+', '-', text)
    # Strip leading/trailing hyphens and lowercase
    return text.strip('-').lower()

def save_match(match: MatchEntry, config: StorageConfig) -> None:
    """
    Appends a match entry to a JSONL file dedicated to its keyword/category.
    Creates directory and file if they don't exist.
    """
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine filename from keyword
    safe_keyword = slugify(match.keyword)
    file_path = output_dir / f"{safe_keyword}.jsonl"
    
    # Prepare data
    data = asdict(match)
    
    # Append to file
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
