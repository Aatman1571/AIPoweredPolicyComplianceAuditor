import json
import os

# Define paths
CONTROL_DIR = os.path.join(os.path.dirname(__file__), '..', 'controls')

ISO_PATH = os.path.join(CONTROL_DIR, 'iso27001.json')
NIST_PATH = os.path.join(CONTROL_DIR, 'nist80053.json')
CIS_PATH = os.path.join(CONTROL_DIR, 'cis.json')

def load_iso_controls():
    with open(ISO_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    flat_controls = []
    for domain in data.get("domains", []):
        for ctrl in domain.get("controls", []):
            flat_controls.append({
                "id": ctrl.get("ref"),
                "title": ctrl.get("title"),
                "description": ctrl.get("summary"),
                "domain": domain.get("title")
            })

    return flat_controls

def load_nist_controls():
    with open(NIST_PATH, 'r') as f:
        return json.load(f)

def load_cis_controls():
    with open(CIS_PATH, 'r') as f:
        return json.load(f)

def load_controls(framework='ISO'):
    framework = framework.upper()
    if framework == 'ISO':
        return load_iso_controls()
    elif framework == 'NIST':
        return load_nist_controls()
    elif framework == 'CIS':
        return load_cis_controls()
    else:
        raise ValueError(f"Unsupported framework: {framework}")

if __name__ == "__main__":
    for fw in ['ISO', 'NIST', 'CIS']:
        controls = load_controls(fw)
        if fw == 'ISO':
            print(f"Loaded {len(controls)} ISO controls (expected ~93)")
        elif fw == 'NIST':
            print(f"Loaded {len(controls)} NIST controls (including enhancements)")
        elif fw == 'CIS':
            safeguard_count = sum(len(c.get("safeguards", [])) for c in controls)
            print(f"Loaded {len(controls)} CIS controls with {safeguard_count} safeguards")
