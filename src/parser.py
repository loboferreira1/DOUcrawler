import unicodedata
from bs4 import BeautifulSoup

def extract_title(html_content: str) -> str:
    """
    Extracts the title from the HTML content.
    Returns the text of the <title> tag, or empty string if not found.
    """
    soup = BeautifulSoup(html_content, "lxml")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return ""

def extract_text(html_content: str) -> str:
    """
    Extracts clean text from HTML, removing scripts, styles, and tags.
    Preserves original accents and case (storage format).
    """
    soup = BeautifulSoup(html_content, "lxml")
    
    # Remove unwanted tags
    for script in soup(["script", "style", "meta", "noscript"]):
        script.extract()
        
    # Get text
    text = soup.get_text(separator=" ")
    
    # Normalize whitespaces: collapse multiple spaces/newlines into single space
    # This makes regex matching and storage much cleaner
    clean_text = " ".join(text.split())
    
    return clean_text

def normalize_text(text: str) -> str:
    """
    Normalizes text for search matching:
    1. Lowercase
    2. Remove accents (NFD decomposition -> filter non-spacing marks)
    """
    # Normalize to NFD form (decomposes characters from accents)
    nfkd_form = unicodedata.normalize('NFD', text)
    
    # Filter out non-spacing mark characters (category 'Mn')
    no_accents = "".join([c for c in nfkd_form if unicodedata.category(c) != 'Mn'])
    
    # Return lowercased (and NFC re-composed mostly just for standard ascii look, though NFD is fine too)
    return no_accents.lower()
