import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup


def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_text_from_url(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove noise: scripts, styles, nav, footer
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return text


def extract_text(source: str) -> str:
    """Extract text from a PDF, TXT file, or URL."""
    if source.startswith("http://") or source.startswith("https://"):
        return extract_text_from_url(source)
    elif source.endswith('.pdf'):
        return extract_text_from_pdf(source)
    elif source.endswith('.txt'):
        return extract_text_from_txt(source)
    else:
        return ""


def chunk_text(text, chunk_size=500, overlap=100):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks