import os
import json
import spacy

BASE_DIR = os.path.dirname(__file__)
PROCESSED_DIR = os.path.join(BASE_DIR, '..', 'processed')
OUTPUT_PATH = os.path.join(BASE_DIR, '..', 'output', 'policy_keywords.json')

nlp = spacy.load("en_core_web_sm")

def extract_keywords(text):
    doc = nlp(text)
    return sorted(set(token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop))

def main():
    results = {}
    for fname in os.listdir(PROCESSED_DIR):
        if not fname.endswith('.txt'):
            continue
        path = os.path.join(PROCESSED_DIR, fname)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        keywords = extract_keywords(content)
        results[fname] = keywords
        print(f"[✔] Extracted {len(keywords)} keywords from {fname}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Keywords saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
