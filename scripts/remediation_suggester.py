import os
import json
import google.generativeai as genai  # pip install google-generativeai

# CONFIGURATION
GENAI_API_KEY = "AIzaSyAIZZyVBYlggi0tNg5wQe9N7gywKaJnPMA"  # Replace with your actual Gemini Pro API key
genai.configure(api_key=GENAI_API_KEY)

BASE_DIR = os.path.dirname(__file__)
GAP_ANALYSIS_FILE = os.path.join(BASE_DIR, "..", "output", "gap_analysis_results.json")
CONTROL_FILES = {
    "ISO": os.path.join(BASE_DIR, "..", "controls", "iso27001.json"),
    "NIST": os.path.join(BASE_DIR, "..", "controls", "nist80053.json"),
    "CIS": os.path.join(BASE_DIR, "..", "controls", "cis.json"),
}
POLICY_DIR = os.path.join(BASE_DIR, "..", "processed")
OUTPUT_FILE = os.path.join(BASE_DIR, "..", "output", "remediation_recommendations.json")

# LOAD CONTROLS
def load_controls():
    all_controls = {"ISO": {}, "NIST": {}, "CIS": {}}
    # ISO
    with open(CONTROL_FILES["ISO"], encoding="utf-8") as f:
        iso = json.load(f)
        for domain in iso["domains"]:
            for c in domain["controls"]:
                all_controls["ISO"][c["ref"]] = f"{c['title']}: {c['summary']}"
    # NIST
    with open(CONTROL_FILES["NIST"], encoding="utf-8") as f:
        nist = json.load(f)
        for c in nist:
            title = c.get("title", "")
            text = c.get("text", "")
            if c.get("is_enhancement", False):
                title = f"[Enhancement] {title}"
            all_controls["NIST"][c["id"]] = f"{title}: {text}"
    # CIS
    with open(CONTROL_FILES["CIS"], encoding="utf-8") as f:
        cis = json.load(f)
        for c in cis:
            for sg in c.get("safeguards", []):
                full_id = f"{c['control_id']}.{sg['id'].split('.')[-1]}"
                all_controls["CIS"][full_id] = f"{sg['title']}: {sg['description']}"
    return all_controls

# LOAD POLICIES
def load_policies():
    policies = {}
    for fname in os.listdir(POLICY_DIR):
        if fname.endswith(".txt"):
            with open(os.path.join(POLICY_DIR, fname), encoding="utf-8") as f:
                policies[fname] = f.read()
    return policies

# CALL GEMINI FOR REMEDIATION SUGGESTION
def generate_remediation(control_text, policy_text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
You are a cybersecurity expert. A gap was found between a compliance control and a policy document. 

CONTROL:
\"\"\"{control_text}\"\"\"

POLICY EXCERPT:
\"\"\"{policy_text if policy_text else '[No relevant policy found]'}\"\"\"

Please suggest an improved or new policy statement that would meet this control requirement. Keep it concise and clear.

Respond in JSON format:
{{
  "suggestion": "..."
}}
"""
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text)
    except:
        return {"suggestion": "Could not parse response or generate suggestion."}

# MAIN FUNCTION
def suggest_remediations():
    controls = load_controls()
    policies = load_policies()
    with open(GAP_ANALYSIS_FILE, encoding="utf-8") as f:
        gap_data = json.load(f)

    results = {}
    for policy_file, gaps in gap_data.items():
        results[policy_file] = []
        policy_text = policies.get(policy_file, "")

        for gap in gaps:
            if gap["coverage"] in ["none", "partial"]:
                source = gap["source"]
                control_id = gap["control_id"]
                control_text = controls.get(source, {}).get(control_id, "")
                if not control_text:
                    continue
                suggestion = generate_remediation(control_text, policy_text)
                results[policy_file].append({
                    "control_id": control_id,
                    "source": source,
                    "coverage": gap["coverage"],
                    "justification": gap["justification"],
                    "remediation": suggestion["suggestion"]
                })

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("✅ Remediation suggestions saved to:", OUTPUT_FILE)

if __name__ == "__main__":
    suggest_remediations()
