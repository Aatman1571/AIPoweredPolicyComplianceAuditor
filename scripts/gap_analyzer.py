import os
import json
import glob
import google.generativeai as genai  # pip install google-generativeai
import time


# Your Gemini API key (set it securely!)
GENAI_API_KEY = "AIzaSyAIZZyVBYlggi0tNg5wQe9N7gywKaJnPMA"
genai.configure(api_key=GENAI_API_KEY)

BASE_DIR = os.path.dirname(__file__)
PROCESSED_DIR = os.path.join(BASE_DIR, "..", "processed")
MAPPING_FILE = os.path.join(BASE_DIR, "..", "output", "control_mapping_results.json")

# Load all controls
def load_all_controls():
    def load_json(name): return json.load(open(os.path.join(BASE_DIR, "..", "controls", name)))
    controls = {"ISO": {}, "NIST": {}, "CIS": {}}
    iso = load_json("iso27001.json")
    for domain in iso["domains"]:
        for c in domain["controls"]:
            controls["ISO"][c["ref"]] = f"{c['title']}: {c['summary']}"
    nist = load_json("nist80053.json")
    for c in nist:
        controls["NIST"][c["id"]] = f"{c['title']}: {c['text']}"
    cis = load_json("cis.json")
    for c in cis:
        for sg in c.get("safeguards", []):
            full_id = f"{c['control_id']}.{sg['id'].split('.')[-1]}"
            controls["CIS"][full_id] = f"{sg['title']}: {sg['description']}"
    return controls

# Load all cleaned policies
def load_policies():
    policies = {}
    for path in glob.glob(os.path.join(PROCESSED_DIR, "*.txt")):
        with open(path, encoding="utf-8") as f:
            policies[os.path.basename(path)] = f.read()
    return policies

# Query Gemini
def analyze_gap(control_text, policy_text):
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt = f"""
You are a cybersecurity auditor. Analyze how well the following policy content addresses the control.

CONTROL REQUIREMENT:
\"\"\"
{control_text}
\"\"\"

POLICY CONTENT:
\"\"\"
{policy_text if policy_text else '[No relevant content found]'}
\"\"\"

Classify the coverage as one of: full, partial, none.
Then give a short justification.
Reply in JSON format:
{{"coverage": "...", "justification": "..."}}
"""
    response = model.generate_content(prompt)
    time.sleep(5)  # Wait 5 seconds between requests
    try:
        response = model.generate_content(prompt)
        time.sleep(5)  # <-- Add this to avoid quota exhaustion
        return json.loads(response.text)
    except Exception as e:
        return {"coverage": "unknown", "justification": f"Error: {str(e)}"}

# Main logic
def run_gap_analysis():
    control_data = load_all_controls()
    policies = load_policies()
    with open(MAPPING_FILE, encoding="utf-8") as f:
        mapping = json.load(f)

    results = {}

    for policy_file, controls in mapping.items():
        policy_text = policies.get(policy_file, "")
        results[policy_file] = []

        for control in controls:
            control_id = control["id"]
            source = control["source"]
            control_text = control_data.get(source, {}).get(control_id, "")
            if not control_text:
                continue
            result = analyze_gap(control_text, policy_text)
            results[policy_file].append({
                "control_id": control_id,
                "source": source,
                "coverage": result["coverage"],
                "justification": result["justification"]
            })

    os.makedirs(os.path.join(BASE_DIR, "..", "output"), exist_ok=True)
    with open(os.path.join(BASE_DIR, "..", "output", "gap_analysis_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("✅ Gap analysis complete! Results saved to output/gap_analysis_results.json")

if __name__ == "__main__":
    run_gap_analysis()
