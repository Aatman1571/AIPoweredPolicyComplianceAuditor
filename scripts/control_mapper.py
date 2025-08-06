import os
import json
import spacy

# Paths
BASE_DIR = os.path.dirname(__file__)
PROCESSED_DIR = os.path.join(BASE_DIR, '..', 'processed')
CONTROL_PATHS = {
    'ISO': os.path.join(BASE_DIR, '..', 'controls', 'iso27001.json'),
    'NIST': os.path.join(BASE_DIR, '..', 'controls', 'nist80053.json'),
    'CIS': os.path.join(BASE_DIR, '..', 'controls', 'cis.json'),
}

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def load_controls():
    controls = []

    # Load ISO
    with open(CONTROL_PATHS['ISO'], 'r', encoding='utf-8') as f:
        iso = json.load(f)
        for domain in iso['domains']:
            for c in domain['controls']:
                controls.append({
                    "id": c['ref'],
                    "title": c['title'],
                    "desc": c.get('summary', ''),
                    "source": "ISO"
                })

    # Load NIST
    with open(CONTROL_PATHS['NIST'], 'r', encoding='utf-8') as f:
        nist = json.load(f)
        for c in nist:
            controls.append({
                "id": c['id'],
                "title": c['title'],
                "desc": c['text'],
                "source": "NIST"
            })

    # Load CIS
    with open(CONTROL_PATHS['CIS'], 'r', encoding='utf-8') as f:
        cis = json.load(f)
        for control in cis:
            for s in control.get("safeguards", []):
                controls.append({
                    "id": f"{control['control_id']}.{s['id']}",
                    "title": s['title'],
                    "desc": s['description'],
                    "source": "CIS"
                })

    return controls

def extract_keywords(text):
    doc = nlp(text)
    return [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop]

def map_controls():
    controls = load_controls()
    results = {}
    total_matches = 0

    for fname in os.listdir(PROCESSED_DIR):
        path = os.path.join(PROCESSED_DIR, fname)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        keywords = set(extract_keywords(content))
        matched = []

        for c in controls:
            c_keywords = set(extract_keywords(c['title'] + " " + c['desc']))
            overlap = keywords & c_keywords
            if len(overlap) >= 2:  # Less strict threshold
                matched.append({
                    "id": c['id'],
                    "source": c['source'],
                    "title": c['title'],
                    "overlap": list(overlap)
                })
                print(f" - {c['id']} ({c['source']}) matched with overlap: {list(overlap)}")

        results[fname] = matched
        total_matches += len(matched)
        print(f"[✔] {fname}: {len(matched)} controls matched.")

    # Create output directory
    output_dir = os.path.join(BASE_DIR, '..', 'output')
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, 'control_mapping_results.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Mapping complete. {total_matches} total matches across all files.")
    print("📄 Results saved to: output/control_mapping_results.json")

if __name__ == "__main__":
    map_controls()
