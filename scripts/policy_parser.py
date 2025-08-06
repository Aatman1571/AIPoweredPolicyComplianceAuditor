import os
import docx
from PyPDF2 import PdfReader

# Folders
RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'policies')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'processed')
os.makedirs(OUT_DIR, exist_ok=True)

def extract_text_from_docx(path):
    doc = docx.Document(path)
    return '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    return '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])

def clean_and_save(input_path, content):
    content = content.strip().replace('\r', '')
    filename = os.path.splitext(os.path.basename(input_path))[0] + '.txt'
    output_path = os.path.join(OUT_DIR, filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return output_path

def process_all():
    for root, _, files in os.walk(RAW_DIR):
        for fname in files:
            in_path = os.path.join(root, fname)
            ext = os.path.splitext(fname)[-1].lower()
            print(f"[~] Processing {fname} ({ext})...")

            if ext == '.docx':
                text = extract_text_from_docx(in_path)
            elif ext == '.pdf':
                text = extract_text_from_pdf(in_path)
            elif ext == '.txt':
                with open(in_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                print(f"[!] Unsupported file type: {fname}")
                continue

            if not text.strip():
                print(f"[!] No text extracted from {fname}")
                continue

            out_path = clean_and_save(in_path, text)
            print(f"[✔] Saved cleaned text → {os.path.basename(out_path)}")


if __name__ == "__main__":
    process_all()
