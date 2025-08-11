# AI-Powered Policy Compliance Auditor

> An NLP and Large Language Model–powered tool for automated cybersecurity policy compliance auditing against ISO 27001, NIST 800-53, and CIS Controls.

---

## 📌 Overview
The **AI-Powered Policy Compliance Auditor** automates the traditionally manual process of auditing security policies.  
By leveraging **Natural Language Processing (NLP)** and **Large Language Models (LLMs)**, the tool can:
- Parse security policy documents (DOCX, PDF, TXT)
- Map extracted clauses to compliance controls
- Detect gaps and missing coverage
- Score compliance levels
- Suggest AI-generated remediation steps

This solution improves audit speed, accuracy, and scalability — helping organizations stay continuously audit-ready.

---

## ⚡ Features
- **Multi-Framework Compliance** — ISO 27001, NIST 800-53, and CIS Controls.
- **Automated NLP Parsing** — Extracts control-relevant terms from policies.
- **AI Gap Analysis** — Identifies missing or incomplete controls using GPT-4/Gemini.
- **Compliance Scoring** — Provides document-level and control-level compliance percentages.
- **Remediation Suggestions** — Generates actionable text to address gaps.
- **Prototype Dashboard** — Displays scores, gaps and recommendations.
- **Multi-format Support** — Works with DOCX, PDF, and TXT policy documents.

---

## 🛠 Tech Stack
- **Language**: Python  
- **Frameworks/Libraries**: spaCy, Flask, Streamlit, PyPDF2
- **AI Models**: Google Gemini API  


---

## 📂 Repository Structure
```
├── controls/                  # JSON control definitions for compliance frameworks
├── output/                    # JSON reports generated after analysis
├── policies/                  # Source cybersecurity policy documents
├── processed/                 # Preprocessed text versions of policies
├── scripts/                   # Core application scripts
└── dashboard_uploads/         # Documents uploaded via dashboard UI
```

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Aatman1571/AIPoweredPolicyComplianceAuditor.git
cd AIPoweredPolicyComplianceAuditor
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Set API Keys
Create a `.env` file:
```
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
```

### 4️⃣ Launch Dashboard
```bash
streamlit run scripts/dashboard.py
```

---

## 📊 Example Output

### **Upload and Audit Execution**
<img width="1917" height="866" alt="image" src="https://github.com/user-attachments/assets/3ba582fc-21b2-46e2-859b-5dae92699587" />

### **Compliance Overview**
<img width="1919" height="866" alt="image" src="https://github.com/user-attachments/assets/e87d1d85-64fd-4461-9741-e3d1a4cc3d2d" />

### **Matched Controls**
<img width="1919" height="867" alt="image" src="https://github.com/user-attachments/assets/26409b64-8586-450c-87c2-c26687c26a8c" />
<img width="1919" height="870" alt="image" src="https://github.com/user-attachments/assets/a53acfbd-c2d0-4a00-b7a3-d7fd0a367e5a" />

### **Remediation Suggestions**
<img width="1919" height="867" alt="image" src="https://github.com/user-attachments/assets/43d50da8-ba71-4bdf-b25a-4d96b661cd1f" />

### **Gap Analysis**
<img width="1919" height="866" alt="image" src="https://github.com/user-attachments/assets/95cdd95b-6ff1-4158-ab8a-7df81d613589" />

### **Compliance Score**
<img width="1919" height="865" alt="image" src="https://github.com/user-attachments/assets/2789c70e-d8b9-4232-94a6-739e929606a2" />

### **PDF Audit Report**
<img width="1919" height="870" alt="image" src="https://github.com/user-attachments/assets/b354baff-450e-4e7e-8328-9f5974024bd5" />

---

## 📈 Roadmap
- [ ] Add support for HIPAA, PCI-DSS, and GDPR.
- [ ] Real-time regulatory framework updates.
- [ ] Version control for policy changes.
- [ ] Enterprise GRC platform integration.
- [ ] Multi-language policy analysis.

---

## 📜 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Authors
- Aatman Dilipkumar Shah  
- Parth Hareshbhai Kakadiya  
- Pruthvesh Mahendrakumar Prajapati  
- Shivam Satishkumar Patel  
- Tirth Patel  
