import unicodedata
from bs4 import BeautifulSoup

def extract_title(html_content: str) -> str:
    """
    Extrai o título do conteúdo HTML.
    Retorna o texto da tag <title>, ou string vazia se não encontrado.
    """
    soup = BeautifulSoup(html_content, "lxml")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return ""

def extract_text(html_content: str) -> str:
    """
    Extrai texto limpo do HTML, removendo scripts, estilos e tags.
    Preserva acentos originais e maiúsculas/minúsculas (formato de armazenamento).
    """
    soup = BeautifulSoup(html_content, "lxml")
    
    # Remove tags indesejadas
    for script in soup(["script", "style", "meta", "noscript"]):
        script.extract()
        
    # Obtém texto
    text = soup.get_text(separator=" ")
    
    # Normaliza espaços em branco: colapsa múltiplos espaços/novas linhas em espaço único
    # Isso torna a correspondência regex e o armazenamento muito mais limpos
    clean_text = " ".join(text.split())
    
    return clean_text

def normalize_text(text: str) -> str:
    """
    Normaliza o texto para correspondência de pesquisa:
    1. Minúsculas
    2. Remove acentos (decomposição NFD -> filtra marcas sem espaçamento)
    """
    # Normaliza para a forma NFD (decompõe caracteres de acentos)
    nfkd_form = unicodedata.normalize('NFD', text)
    
    # Filtra caracteres de marca sem espaçamento (categoria 'Mn')
    no_accents = "".join([c for c in nfkd_form if unicodedata.category(c) != 'Mn'])
    
    # Retorna em minúsculas (e NFC recomposto principalmente para aparência ascii padrão, embora NFD esteja bem também)
    return no_accents.lower()
