import os
import json
import spacy
import docx
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
import re
import time

# ---------- Configuration ----------
#GENAI_API_KEY = "YOUR_API_KEY"
GENAI_API_KEY = "YOUR_API_KEY"
genai.configure(api_key=GENAI_API_KEY)
nlp = spacy.load("en_core_web_sm")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------- Paths ----------
BASE_DIR = os.path.dirname(__file__)
CONTROL_DIR = os.path.join(BASE_DIR, "..", "controls")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "output")
PROCESSED_DIR = os.path.join(BASE_DIR, "..", "processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ---------- Domain Keywords ----------
DOMAINS = {
    "access_control": ["authentication", "authorization", "login", "password", "access control"],
    "incident_response": ["incident", "breach", "response", "forensics", "security incident"],
    "asset_management": ["inventory", "asset", "device", "hardware", "endpoint"],
    "data_protection": ["encryption", "retention", "disposal", "confidentiality", "sensitive data"],
    "security_governance": ["policy", "risk", "training", "compliance", "audit", "roles"],
}

# Precompute domain embeddings
DOMAIN_EMBEDDINGS = {
    d: embedding_model.encode(" ".join(k), convert_to_tensor=True) for d, k in DOMAINS.items()
}

# ---------- Text Extraction ----------
def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

def clean_and_save(path, text):
    filename = os.path.splitext(os.path.basename(path))[0] + ".txt"
    out_path = os.path.join(PROCESSED_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text.strip().replace("\r", ""))
    return out_path

def parse_policy(path):
    ext = os.path.splitext(path)[-1].lower()
    if ext == ".docx":
        text = extract_text_from_docx(path)
    elif ext == ".pdf":
        text = extract_text_from_pdf(path)
    elif ext == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise ValueError("Unsupported file type.")
    if not text.strip():
        raise ValueError("No content found.")
    return clean_and_save(path, text)

# ---------- Chunk Policy ----------
def extract_chunks(policy_text, window_size=3):
    sentences = [s.text.strip() for s in nlp(policy_text).sents if len(s.text.strip()) > 20]
    return [" ".join(sentences[i:i + window_size]) for i in range(len(sentences))]

# ---------- Domain Detection ----------
def detect_policy_domains(policy_text):
    detected = set()
    lower_text = policy_text.lower()
    for domain, keywords in DOMAINS.items():
        for kw in keywords:
            if kw.lower() in lower_text:
                detected.add(domain)
                break
    return list(detected)

def tag_control_domain(control_text):
    control_emb = embedding_model.encode(control_text, convert_to_tensor=True)
    scores = {d: util.cos_sim(control_emb, emb).item() for d, emb in DOMAIN_EMBEDDINGS.items()}
    return max(scores, key=scores.get)

# ---------- Control Loader ----------
def preprocess_control_text(entry):
    parts = []
    for field in ["title", "description", "summary", "text", "discussion"]:
        if field in entry and entry[field]:
            parts.append(entry[field])
    return ". ".join(parts)

def load_controls(selected_frameworks):
    controls = {}
    if "ISO" in selected_frameworks:
        with open(os.path.join(CONTROL_DIR, "iso27001_custom.json"), encoding="utf-8") as f:
            iso = json.load(f)
            for domain in iso["domains"]:
                for c in domain["controls"]:
                    key = f"ISO::{c['ref']}"
                    text = preprocess_control_text(c)
                    controls[key] = {"text": text, "domain": tag_control_domain(text)}
    if "NIST" in selected_frameworks:
        with open(os.path.join(CONTROL_DIR, "nist80053_custom.json"), encoding="utf-8") as f:
            for c in json.load(f):
                key = f"NIST::{c['id']}"
                text = preprocess_control_text(c)
                controls[key] = {"text": text, "domain": tag_control_domain(text)}
    if "CIS" in selected_frameworks:
        with open(os.path.join(CONTROL_DIR, "cis_custom.json"), encoding="utf-8") as f:
            for c in json.load(f):
                key = f"CIS::{c['id']}"
                text = preprocess_control_text(c)
                controls[key] = {"text": text, "domain": tag_control_domain(text)}


    with open(os.path.join(OUTPUT_DIR, "control_blueprint.json"), "w") as f:
        json.dump(controls, f, indent=2)
    return controls

# ---------- Semantic Matcher ----------
def match_sentences_semantically(policy_text, control_text, threshold=0.55, top_k=3):
    sentences = [s.text.strip() for s in nlp(policy_text).sents if len(s.text.strip()) > 15]
    if not sentences:
        return []

    control_chunks = [c.strip() for c in control_text.split(".") if len(c.strip()) > 20]

    control_embeddings = embedding_model.encode(control_chunks, convert_to_tensor=True)
    sentence_embeddings = embedding_model.encode(sentences, convert_to_tensor=True)

    scores = util.pytorch_cos_sim(control_embeddings, sentence_embeddings)
    scored = [(sentences[j], float(scores[i][j])) for i in range(len(control_chunks)) for j in range(len(sentences))]
    scored = sorted(scored, key=lambda x: x[1], reverse=True)

    filtered = [(s, round(score, 3)) for s, score in scored if score >= threshold]

    seen = set()
    final_matches = []
    for s, score in filtered:
        prefix = s[:60].lower()
        if prefix not in seen:
            final_matches.append((s, score))
            seen.add(prefix)
        if len(final_matches) >= top_k:
            break
    return final_matches

# ---------- Gemini Helpers ----------
def safe_json_parse(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return {"coverage": "unknown", "justification": "Invalid AI response format"}
    return {"coverage": "unknown", "justification": "No valid JSON returned"}

def analyze_gap(control_text, matched_sentences):
    if not matched_sentences:
        return {"coverage": "none", "justification": "No relevant content found."}
    excerpt = "\n".join([s for s, _ in matched_sentences])
    prompt = f"""
You are a cybersecurity auditor. Analyze whether the policy addresses the control.

CONTROL:
\"\"\"{control_text}\"\"\"

POLICY:
\"\"\"{excerpt}\"\"\"

Respond as JSON:
{{"coverage": "full | partial | none", "justification": "..."}}
"""
    try:
        time.sleep(7) 
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        res = model.generate_content(prompt)
        return safe_json_parse(res.text)
    except Exception as e:
        return {"coverage": "unknown", "justification": str(e)}

def generate_remediation(control_text, policy_excerpt):
    prompt = f"""
Suggest a remediation for the gap between the control and policy.

CONTROL:
\"\"\"{control_text}\"\"\"

POLICY:
\"\"\"{policy_excerpt}\"\"\"

Respond as JSON:
{{"suggestion": "..."}}
"""
    try:
        time.sleep(7) 
        model = genai.GenerativeModel("gemini-2.5-flash")
        res = model.generate_content(prompt)
        return safe_json_parse(res.text).get("suggestion", "")
    except:
        return "No suggestion available."

# ---------- Scoring ----------
# ---------- Scoring ----------
SCORE_MAP = {"full": 1.0, "partial": 0.5, "none": 0.0, "unknown": 0.0}

def grade(p):
    return "A+" if p >= 90 else "A" if p >= 80 else "B" if p >= 70 else "C" if p >= 60 else "D" if p >= 50 else "F"

def calculate_score(gaps):
    # Only count controls that have relevant matches
    relevant_gaps = [g for g in gaps if not (g["coverage"] == "none" and g["justification"] == "No relevant content found.")]
    total = len(relevant_gaps)
    score = sum(SCORE_MAP.get(g["coverage"], 0) for g in relevant_gaps)
    pct = round((score / total) * 100, 2) if total > 0 else 100  # if no relevant controls, assume 100%
    return {"score": score, "total": total, "percentage": pct, "grade": grade(pct)}

# ---------- Main Pipeline ----------
def run_policy_pipeline(policy_path, frameworks, status_box=None):
    def update(msg):
        if status_box:
            status_box.info(msg)

    update("📄 Parsing policy...")
    txt_path = parse_policy(policy_path)
    with open(txt_path, encoding="utf-8") as f:
        policy_text = f.read()

    update("🔍 Detecting policy domain...")
    relevant_domains = detect_policy_domains(policy_text)

    update(f"🧩 Loading relevant controls for: {', '.join(frameworks)}")
    controls = load_controls(frameworks)

    update("🔎 Filtering & matching controls...")
    matched_controls = []
    unmatched_controls = []

    for cid, ctrl in controls.items():
        matches = match_sentences_semantically(policy_text, ctrl["text"])
        source, id = cid.split("::")

        if matches:
            matched_controls.append({
                "id": id,
                "source": source,
                "text": ctrl["text"],
                "sentences": [m[0] for m in matches],
                "scores": [m[1] for m in matches],
                "domain": ctrl["domain"]
            })
        else:
            unmatched_controls.append({
                "control_id": id,
                "source": source,
                "coverage": "none",
                "justification": "No relevant content found.",
                "domain": ctrl["domain"]
            })

    update("🧪 Running gap analysis...")
    gaps = []
    for i, m in enumerate(matched_controls):
        analysis = analyze_gap(m["text"], list(zip(m["sentences"], m["scores"])))
        gaps.append({
            "control_id": m["id"],
            "source": m["source"],
            "coverage": analysis["coverage"],
            "justification": analysis["justification"],
            "domain": m["domain"]
        })
        if i % 5 == 0:
            update(f"🔎 Checked {i+1}/{len(matched_controls)} controls...")

    # Do NOT include unmatched controls in gaps for scoring or UI
    all_gaps = gaps  

    summary = calculate_score(all_gaps)

    update("🛠️ Suggesting remediations...")
    remediations = []
    for g in all_gaps:
        if g["coverage"] in ["none", "partial"]:  # Only for matched controls
            ctrl_key = f"{g['source']}::{g['control_id']}"
            ctrl_text = controls.get(ctrl_key, {}).get("text", "")
            excerpt = "\n".join([s for s, _ in match_sentences_semantically(policy_text, ctrl_text)])
            remediation = generate_remediation(ctrl_text, excerpt)
            remediations.append({**g, "remediation": remediation})

    report = {
        "policy": os.path.basename(policy_path),
        "detected_domains": relevant_domains,
        "summary": summary,
        "mappings": matched_controls,
        "gaps": all_gaps,  # unmatched controls removed
        "remediations": remediations
    }

    out_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(os.path.basename(policy_path))[0]}_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    update("✅ Done!")
    return out_path
